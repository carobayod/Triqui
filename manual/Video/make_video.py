#!/usr/bin/env python3
"""Genera el video explicativo v2 del libro (narración Kokoro + slides v2).

Pipeline:
  md + slide_content -> escenas (título + narración + 3 puntos)
     -> TTS Kokoro "Dora" (femenino, local) -> slides v2 (weasyprint)
     -> clips ffmpeg (Ken Burns alternado, o Manim si existe)
     -> xfade 0.5s entre escenas -> pista de narración con offsets visuales
     -> MP4 final 1080p30 (sin música)

Uso:  python make_video.py [--first N] [--voice kokoro|piper] [--rebuild]
"""
import html
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/home/carobayo/proyectos/Triqui")
V = ROOT / "manual" / "Video"
WORK = V / "work"
for d in (V, WORK, WORK / "audio", WORK / "slides", WORK / "clips"):
    d.mkdir(parents=True, exist_ok=True)

import slide_content as CONTENT

SRC = ROOT / "manual" / "Aprendiendo_a_programar_jugando_con_el_Triki.md"
PIPER = ROOT / ".venv" / "bin" / "piper"
VOICE = ROOT / ".venv" / "piper-voices" / "es_ES-sharvard-medium" / "es_ES-sharvard-medium.onnx"
KOKORO_PY = V / "synth_kokoro.py"
KOKORO_PYTHON = ROOT / ".venv312" / "bin" / "python"
SLIDE_CSS = V / "slide_v2.css"
FPS = 30
XFADE = 0.5
NAV_BANNER = "Aprende Java Jugando"
VOICE_ENGINE = "kokoro"

# edge-tts (Microsoft Edge TTS): sin API key y gratis, pero necesita internet.
# Voz elegida tras comparar 27 muestras: es-CL-LorenzoNeural.
# EDGE_RATE ajusta el ritmo; con "+0%" Lorenzo habla algo mas lento que Kokoro,
# asi que el video se alarga un poco. Se mide y se corrige si hace falta.
EDGE_VOICE = "es-CL-LorenzoNeural"
EDGE_RATE = "+0%"


# ---------------------------------------------------------------- parsing
def clean_section(txt):
    """Quita markdown, código, blockquotes, tablas y marcas; devuelve párrafos."""
    lines = txt.splitlines()
    out, cur = [], ""
    in_code = False
    for ln in lines:
        if re.match(r"^\s*```", ln):
            in_code = not in_code
            continue
        if in_code:
            continue
        ln = ln.strip()
        if not ln or ln.startswith((">", "|")) or ln == "---":
            continue
        if re.match(r"^#{1,6} ", ln):
            continue
        if ln in ("[CODEDEL]", "[CODE]"):
            continue
        # marcas en mayúsculas tipo título ("REPASO DEL CAPÍTULO", "PREGUNTA")
        if ln.isupper() and len(ln) <= 45 and not ln.endswith((".", ",")):
            continue
        ln = re.sub(r"[*_`~]", "", ln)
        # Imagenes: se descarta la LINEA COMPLETA, incluidos los atributos que
        # van despues del cierre: "![alt](ruta){ width=42% }".
        #
        # Antes solo se quitaba el "![]()" con regex y el "{ width=42% }"
        # quedaba suelto, con lo que caia como parrafo y la voz leia en voz
        # alta "width igual a cuarenta y dos por ciento" al final de la escena
        # de Tablero.java. No es codigo del juego: es el ancho con el que Pandoc
        # escala la imagen en el PDF.
        if re.match(r"^!\[[^\]]*\]\([^)]*\)", ln):
            continue
        ln = re.sub(r"!\[[^\]]*\]\([^)]*\)\s*\{[^}]*\}", "", ln)
        ln = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", ln)
        ln = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", ln)
        ln = ln.strip()
        if ln:
            out.append(ln)
    return out


def build_scenes():
    raw = SRC.read_text()
    main = raw.split("---", 2)[-1]
    lines = main.splitlines()
    proc = []
    in_code = False
    for ln in lines:
        if re.match(r"^\s*```", ln):
            in_code = not in_code
            proc.append("[CODEDEL]")
            continue
        proc.append("[CODE]" if in_code else ln)
    main = "\n".join(proc)
    scenes = []

    def add(title, parcelas, kind="cap", banner=NAV_BANNER):
        scenes.append(dict(title=title, paras=parcelas, kind=kind, banner=banner))

    for chunk in re.split(r"(^# .+$)", main, flags=re.M):
        chunk = chunk.strip()
        if not chunk:
            continue
        if re.match(r"^# ", chunk):
            t = chunk[2:].strip()
            add(t, ["Apartado del curso."], kind="part", banner=t)
            continue
        block_title = None
        block = ""
        for p in re.split(r"(^## .+$)", chunk, flags=re.M):
            if re.match(r"^## ", p):
                if block.strip() and block_title is not None:
                    add(block_title, clean_section(block))
                block_title = p[3:].strip()
                block = ""
            else:
                block += p + "\n"
        if block.strip() and block_title is not None:
            add(block_title, clean_section(block))
    return scenes


# ---------------------------------------------------------------- narración
# El repaso y el reto viven dentro de scene["paras"] porque asi estan en el
# markdown. Para la narracion hay que filtrarlos: si no, el video intenta leer
# en voz alta "a) Un ciclo. Respuesta correcta: b" y el reto de codigo.
_REPISO = re.compile(
    r"^\s*(\d+[.)]\s|a\\\)|a\)|Respuesta correcta|🏆|> ?[💡⚠🏆]|REPASO|RETO)", re.I)


def _es_narrable(p):
    return not _REPISO.match(p or "")


def first_sentences(paras, max_words=60):
    """Primeras frases con sentido completo.

    Antes cortaba a 40 palabras sin mirar, y si la frase terminaba en dos
    puntos ("que se escribe asi:") se comia lo que venia despues: el oyente
    escuchaba un salto sin saber por que. Ahora, si se pasa del limite pero la
    frase pide continuacion (termina en : o ,), se incluye la siguiente.
    """
    limpio = [p for p in paras if _es_narrable(p)]
    if not limpio:
        limpio = [p for p in paras if p and p.strip()]

    # Se parte POR PARRAFO primero. Un parrafo que acaba en dos puntos suele
    # estar seguido de un bloque de codigo, y los bloques no estan en paras. Si
    # se unieran los parrafos con un espacio, "...que se escribe asi:" y "En el
    # Triki..." quedarian pegados en una sola frase y la voz dira un salto sin
    # aviso. Partiendo por parrafo, la frase que cuelga queda aislada y se puede
    # descartar.
    sentences = []
    for p in limpio:
        p = (p or "").strip()
        if not p:
            continue
        sentences.extend(s for s in re.split(r"(?<=[.!?])\s+", p) if s.strip())

    # Si una frase termina en dos puntos y lo que sigue NO es su continuacion
    # (no empieza en minuscula ni con un conector), se descarta: al oyente le
    # sonaria a que falta algo.
    conectores = ("y ", "o ", "u ", "que ", "porque ", "para ", "como ", "cuando ",
                  "si ", "entonces ", "además ", "también ", "pero ", "por ")
    OKE = []
    for i, s in enumerate(sentences):
        if s.rstrip().endswith(":"):
            nxt = sentences[i + 1] if i + 1 < len(sentences) else ""
            sigue = (not nxt) or nxt[:1].islower() or nxt.lower().startswith(conectores)
            if not sigue:
                continue
        OKE.append(s)
    sentences = OKE or sentences

    words = 0
    picked = []
    for s in sentences:
        w = len(s.split())
        if words + w > max_words and picked:
            if not s.rstrip().endswith((":", ",")):
                break
        picked.append(s)
        words += w
        if len(picked) >= 4:
            break
    return " ".join(picked)


# números -> palabras (para que Dora los lea bien)
_DEC = {0: "cero", 1: "uno", 2: "dos", 3: "tres", 4: "cuatro", 5: "cinco", 6: "seis",
        7: "siete", 8: "ocho", 9: "nueve", 10: "diez", 11: "once", 12: "doce",
        13: "trece", 14: "catorce", 15: "quince", 16: "dieciséis", 17: "diecisiete",
        18: "dieciocho", 19: "diecinueve", 20: "veinte", 21: "veintiuno",
        22: "veintidós", 23: "veintitrés", 24: "veinticuatro", 25: "veinticinco",
        26: "veintiséis", 27: "veintisiete", 28: "veintiocho", 29: "veintinueve"}
_DECENAS = {30: "treinta", 40: "cuarenta", 50: "cincuenta", 60: "sesenta",
            70: "setenta", 80: "ochenta", 90: "noventa"}


def num_words(n):
    if n <= 29:
        return _DEC[n]
    if n in _DECENAS:
        return _DECENAS[n]
    d, u = divmod(n, 10)
    if u:
        return f"{_DECENAS[d * 10]} y {_DEC[u]}"
    return str(n)


def expand_numbers(text):
    text = re.sub(r"(\d)\s*[xX×]\s*(\d)", lambda m: f"{num_words(int(m.group(1)))} por {num_words(int(m.group(2)))}", text)

    def rep(m):
        n = int(m.group(0))
        if n <= 99:
            n = num_words(n)
            return n if n.isdigit() else re.sub(r"^(.)", lambda mm: mm.group(1).upper(), n.lower()) if n.isdigit() else n
        return m.group(0)

    text = re.sub(r"(?<![A-Za-z])\d{1,2}(?![A-Za-z])", rep, text)
    return text


# ---------------------------------------------------------------- normalizacion TTS
# Para espanol, Kokoro no usa un G2P espanol: cae a espeak-ng (kokoro/
# pipeline.py:133, EspeakG2P). Verificado contra el texto real de las escenas:
#
#   "JVM"          -> xˌotaˌuβeˈɛme   "jota-uve-eme", no la sigla
#   "POO"          -> pˈoo            "poo"
#   "if"           -> ˈif             leido en ingles
#   "else"         -> ˈelse           leido en ingles
#   "{ width = x }"-> { wˈidt ... }   las LLAVES se leen
#   "Math.random()"-> mˈat.rˈandom()  los PARENTESIS se leen
#
# Las llaves y los parentesis sobreviven como fonemas literales: eso no suena
# raro, es audio inservible. Y las siglas salen deletreadas con fonema ingles.
#
# Lo que YA funciona solo y por eso NO se toca (verificado con espeak-ng):
#   "=" -> iɣwˈal "igual" | "%" -> poɾθjˈɛnto "por ciento"
#   "+" -> mˈas "mas"      | "-" -> mˈenos "menos"
#   "·" -> pˈunto mˈeðjo "punto medio" | "X" -> ˈɛkis "equis"
#   "LEGO" -> lˈeɣo | "1.5" -> ˈuno kˈoma θˈinko "uno coma cinco"

# Siglas -> como las deberia decir un narrator. Se deletrean cuando la sigla es
# la parte importante (la abreviatura se nombra al lado de su significado), y
# se expanden cuando el significado ya esta dicho y la sigla es de adorno.
_SIGLAS_TXT = [
    (r"\bJVM\b", "Jave Eme Eme"),
    (r"\bPOO\b", "Pe O O"),
    (r"\bGUI\b", "interfaz grafica de usuario"),
]

# Palabras clave de Java: en espanol hay que deletrearlas o glosarlas, porque
# espeak-ng las pronuncia en ingles.
_CLAVES_TXT = [
    (r"\bif\s*/\s*else\b", "i f, barra e l s e"),
    (r"\belse\b", "e l s e"),
    (r"\bif\b", "i f"),
]

# Metodos con parentesis: "Math.random()" -> los parentesis se leen. Se quitan
# los parentesis, pero el punto se convierte en palabra para que no se lea como
# un archivo.
_METODOS_TXT = [
    (r"\bMath\.random\(\)", "Math punto random"),
    (r"\bMath\.random\b", "Math punto random"),
]


def normalize_for_tts(text):
    """Deja el texto legible por espeak-ng antes de mandarlo a Kokoro.

    Se aplica DESPUES de expand_numbers: los numeros ya estan en palabras, asi
    que aca solo hay que arreglar siglas, claves y simbolos que se leen en voz
    alta. No tocar lo que ya funciona (ver la nota de arriba).
    """
    for patron, nuevo in _METODOS_TXT + _SIGLAS_TXT + _CLAVES_TXT:
        text = re.sub(patron, nuevo, text, flags=re.IGNORECASE)

    # Aclaraciones entre parentesis: el parentesis no se puede borrar tal cual,
    # porque a veces es lo unico que separa el termino de su aclaracion
    # ("el molde (la clase) define la forma" -> "el molde la clase define la
    # forma", que ya no se entiende). Se convierte en coma.
    #
    # Se probo "es decir" y sonaba peor: hay escenas con cinco aclaraciones
    # seguidas y el narrator repetia la muletilla en cada una.
    text = re.sub(r"\s*\(([^)]{1,60})\)", r", \1,", text)
    # Parentesis sueltos que el patron anterior no agarro (grupo largo). Se
    # quitan igual.
    text = re.sub(r"[(){}\[\]]", " ", text)
    # Comillas: no suenan, pero sobran al pasar por espeak.
    text = text.replace('"', " ").replace("'", " ")

    # El guion de lista ("- jugada(fila, columna)") se lee como menos. Se
    # convierte en coma.
    text = re.sub(r"(?<![\w-])\-\s+", ", ", text)

    # Limpieza de puntuacion. Sin esto quedan comas colgando, que al leerlas en
    # voz alta suenan como tropezar: ", jugada, fila, columna, turno, marca una
    # casilla." y "es decir interfaz grafica de usuario," seguido de nada.
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    text = re.sub(r"\s*,\s*(?=[.;:])", "", text)
    # Coma justo despues de otra coma.
    text = re.sub(r",\s*(?=,\s)", "", text)
    # Coma con la que arranca una frase tras punto (o al principio del todo).
    text = re.sub(r"(?<=[.;:])\s*,\s*", " ", text)
    text = re.sub(r"^\s*,\s*", "", text)
    # Coma al final: se quita y se deja que la pausa la marque el punto final.
    text = re.sub(r"\s*,\s*$", "", text)
    return text.strip()


def narrate_text(scene, idx):
    _, _, _, narr, _ = CONTENT.get(idx, scene["title"], scene["banner"])
    if narr:
        return expand_numbers(narr)
    t = scene["title"].strip()
    body = first_sentences(scene["paras"])
    num = re.match(r"Capítulo (\d+):\s*(.*)", t)
    # No se anuncia "Capítulo N:" al principio. El slide ya muestra el titulo en
    # grande; repetirlo en la voz hacia que el video sonara a indice ledo, y
    # ademas retardaba la entrada. Se arranca direto con el contenido.
    if num:
        base = body or (num.group(2) or "")
    elif t.startswith("src/"):
        base = f"{CONTENT.get(idx, t, scene['banner'])[0]}. {body}".strip()
    else:
        base = f"{t}. {body}".strip()
    return expand_numbers(base)


# ---------------------------------------------------------------- TTS
def synth_all(escenas):
    """Genera todo el audio de Kokoro en un solo proceso.

    Antes se llamaba a synth() escena por escena, y cada llamada cargaba el
    modelo de 82M: 41 cargas para 41 escenas, casi una hora. Aqui se arma un
    manifiesto y synth_kokoro.py --lote lo resuelve con una sola carga.
    """
    trabajo = []
    for idx, scene in escenas:
        texto = normalize_for_tts(narrate_text(scene, idx))
        trabajo.append({"texto": texto,
                        "salida": str(WORK / "audio" / f"s{idx}.wav")})
    manifiesto = WORK / "kokoro_lote.json"
    manifiesto.write_text(json.dumps(trabajo, ensure_ascii=False), encoding="utf-8")
    p = subprocess.run([str(KOKORO_PYTHON), str(KOKORO_PY), "--lote", str(manifiesto)],
                       capture_output=True, text=True)
    if p.returncode != 0:
        print("KOKORO ERROR:", p.stderr[-400:])
        sys.exit(1)
    print(p.stdout.rstrip())
    manifiesto.unlink(missing_ok=True)


def synth(text, out_wav):
    if VOICE_ENGINE == "kokoro":
        p = subprocess.run([str(KOKORO_PYTHON), str(KOKORO_PY), text, str(out_wav)],
                           capture_output=True, text=True)
        if p.returncode != 0:
            print("KOKORO ERROR:", p.stderr[-300:])
            sys.exit(1)
        return p
    if VOICE_ENGINE == "edge":
        # edge-tts devuelve mp3; el resto del pipeline (sox, ensamblado) espera
        # wav 24 kHz mono, que es lo que produce Kokoro. Convertimos para no
        # tocar nada mas del montaje.
        #
        # Ademas reintenta: el endpoint no es un API oficial y devuelve 403 si
        # se le pide mucho seguido, y con 41 escenas seguidas hace falta.
        tmp = out_wav.with_suffix(".edge.mp3")
        ultimo = ""
        p = None
        for intento in range(4):
            p = subprocess.run(["edge-tts", "--voice", EDGE_VOICE,
                                "--rate", EDGE_RATE, "--text", text,
                                "--write-media", str(tmp)],
                               capture_output=True, text=True)
            if p.returncode == 0 and tmp.exists() and tmp.stat().st_size > 2000:
                break
            ultimo = p.stderr[-200:]
            if intento < 3:
                espera = 20 * (intento + 1)
                print(f"  edge-tts fallo (intento {intento + 1}/4), "
                      f"reintentando en {espera}s", flush=True)
                time.sleep(espera)
        else:
            print("EDGE-TTS ERROR:", ultimo, flush=True)
            sys.exit(1)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp),
                        "-ar", "24000", "-ac", "1", "-c:a", "pcm_s16le", str(out_wav)],
                       check=True, capture_output=True)
        tmp.unlink(missing_ok=True)
        return p
    p = subprocess.run([str(PIPER), "--model", str(VOICE), "--output_file", str(out_wav),
                        "--length_scale", "1.05"],
                       input=text + "\n", capture_output=True, text=True)
    if p.returncode != 0:
        print("PIPER ERROR:", p.stderr[-300:])
        sys.exit(1)
    return p


# ---------------------------------------------------------------- slides
# Ancho util de la diapositiva: 203.2mm menos 16mm de margen a cada lado, y la
# regla @page de build_slide() pone la pagina en mm sobre un PNG de 1920px, o
# sea 9.45 px por mm. 171.2mm * 9.45 = 1618px.
_ANCHO_UTIL_PX = 1618
_FUENTE_TITULO = None


def _ancho_titulo(texto, px):
    """Ancho real del texto en la fuente serif del titulo.

    Se mide con PIL porque el CSS no puede decidirlo: el navegador de WeasyPrint
    parte el titulo donde quiera y despues ya no se puede corregir.
    """
    global _FUENTE_TITULO
    if _FUENTE_TITULO is None:
        from PIL import ImageFont
        base = 90  # 9.5mm * 9.45 px/mm
        for ruta in ("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
                     "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"):
            try:
                _FUENTE_TITULO = ImageFont.truetype(ruta, base)
                break
            except OSError:
                continue
        else:
            _FUENTE_TITULO = False
    if not _FUENTE_TITULO:
        return len(texto) * 45
    return _FUENTE_TITULO.getbbox(texto)[2]


def _clase_titulo(texto):
    """Elige el tamano del h1 segun quepa en una sola linea.

    El umbral es 1450px, no los 1618px teoricos: el titulo lleva text-shadow y
    Georgia renderizada por WeasyPrint es algo mas ancha que la fuente que se
    mide aqui. Con 1450 los cinco titulos del apendice entran en una linea y se
    verificó midiendo el render, no calculando.
    """
    ancho = _ancho_titulo(texto, 90)
    # 7.2mm es 0.758 de 9.5mm: el ancho se reduce en la misma proporcion.
    if ancho * 0.758 > 1450:
        return "t-largo"
    if ancho * 0.863 > 1450:   # 8.2mm
        return "t-medio"
    return ""


def slide_html(scene, idx):
    title, section, points, _, extra = CONTENT.get(idx, scene["title"], scene["banner"])
    # títulos de capítulo: quitar número ("Capítulo 14") -> muestra el enunciado
    if scene["kind"] != "part":
        title = re.sub(r"^Capítulo \d+:\s*", "", title)
    items = [html.escape(p) for p in (points or [])[:4]]
    bullets = "".join(f"<li>{i}</li>" for i in items)
    n = CONTENT.SECTIONS_N
    progress = f"{idx + 1:02d} / {n}"

    # El tamaño del titulo depende de lo que ocupe: con codigo o diagrama
    # debajo, un titulo de dos lineas se come el alto y recorta el contenido
    # (medido: en s40 el flujo se cortaba a media imagen).
    #
    # Se mide el ancho REAL con la fuente, no se estima por numero de
    # caracteres: Georgia y DejaVu miden distinto y un promedio salen mal.
    clase_t = _clase_titulo(title)
    tag_h1 = f' class="{clase_t}"' if clase_t else ""
    cabeza = (f"<h1{tag_h1}>{html.escape(title)}</h1>\n  <div class=\"rule\"></div>")

    # Las escenas del apendice (36-40) son distintas a las demas: en vez de tres
    # palabras, muestran un diagrama o un bloque de codigo real tomado del
    # libro. Antes estas escenas decian "Une todo el juego" y no se entendia
    # nada; el contenido existe en el markdown, solo no llegaba a la pantalla.
    clase = "contenido"
    if extra and extra.get("codigo"):
        clase += " con-codigo"
        cuerpo = cabeza + (f"\n  <pre class=\"code\">{html.escape(extra['codigo'])}</pre>")
        if extra.get("glosa"):
            cuerpo += f"\n  <p class=\"glosa\">{html.escape(extra['glosa'])}</p>"
    elif extra and extra.get("diagrama"):
        # La variante depende de la proporcion del PNG: uno vertical al lado de
        # un texto en 16:9 queda ilegible.
        lado = extra.get("lado")
        if lado is None:
            try:
                from PIL import Image
                with Image.open(extra["diagrama"]) as im:
                    lado = "lado" if im.size[0] / im.size[1] > 1.3 else "abajo"
            except Exception:
                lado = "abajo"
        clase += f" con-img-{lado}"
        img = (f"<img src=\"file://{extra['diagrama']}\" "
               f"alt=\"{html.escape(extra.get('alt', 'diagrama'))}\">")
        cuerpo = (f"\n  <div class=\"texto\">{cabeza}\n  <ul>{bullets}</ul></div>"
                  f"\n  <div class=\"diagrama\">{img}</div>")
    else:
        cuerpo = cabeza + f"\n  <ul>{bullets}</ul>"

    return f"""<div class="slide">
  <div class="orb o1"></div><div class="orb o2"></div>
  <div class="top"><span class="section">{html.escape(section)}</span>
    <span class="progress">{progress}</span></div>
  <div class="{clase}">{cuerpo}
  </div>
  <div class="foot"><span class="course">Aprende Java Jugando</span>
    <span class="tag">Triki con IA</span></div>
</div>"""


def build_slide(scene, idx, out_png):
    css = SLIDE_CSS.read_text()
    htmldoc = f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<style>
@page {{ size: 203.2mm 114.3mm; margin: 0; }}
html,body {{ margin:0; padding:0; }}
{css}
</style></head><body>{slide_html(scene, idx)}</body></html>"""
    tmp = WORK / f"slide_{idx}.html"
    tmp.write_text(htmldoc)
    p = subprocess.run(["weasyprint", str(tmp), str(tmp.with_suffix(".pdf"))],
                       capture_output=True, text=True)
    if p.returncode != 0:
        print("WEASY ERROR:", p.stderr[-400:])
        sys.exit(1)
    subprocess.run(["pdftoppm", "-f", "1", "-l", "1", "-r", "240", "-png",
                    str(tmp.with_suffix(".pdf")), str(out_png.with_suffix(""))],
                   check=True)
    gen = out_png.parent / (out_png.stem + "-1.png")
    if gen.exists():
        gen.rename(out_png)
    return out_png


# ---------------------------------------------------------------- vídeo
def wav_dur(path):
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return float(p.stdout.strip())


def prepare_scene(idx, scene, rebuild=False):
    text = normalize_for_tts(narrate_text(scene, idx))
    awav = WORK / "audio" / f"s{idx}.wav"
    apng = WORK / "slides" / f"s{idx}.png"
    if rebuild or not awav.exists():
        synth(text, awav)
    if rebuild or not apng.exists():
        build_slide(scene, idx, apng)
    adur = wav_dur(awav)
    return 0.5 + adur + 0.9


def kenburns(src_png, dur, out_mp4, idx):
    """Movimiento suave pero VARIADO.

    Antes todas las escenas hacian el mismo zoom hacia adentro con un drift
    lateral alterno. Repetido 38 veces se vuelve pesado: el ojo aprende el
    gesto y deja de mirarlo. Aqui se rota entre seis modos y uno de cada
    cinco deja la imagen quieta, para que el descanso tambien sea parte del
    ritmo.

    Los modos se eligen por indice (no al azar) para que el resultado sea
    reproducible: reejecutar el script da el mismo video.
    """
    frames = max(int(round(dur * FPS)), int(2 * FPS))
    modo = idx % 6
    amp = 0.055                      # recorrido lateral maximo
    vel = 0.0013                     # velocidad de zoom

    if modo == 0:                    # zoom in lento, centrado
        z, x, y = (f"min(zoom+{vel},1.12)",
                   "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)")
    elif modo == 1:                  # zoom out: arranca cerca y se aleja
        z = f"max(1.12-{vel}*on,1.0)"
        x, y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif modo == 2:                  # paneo lateral, sin zoom
        d = amp if idx % 2 == 0 else -amp
        z = "1.04"
        x = f"iw/2-(iw/zoom/2)+({d}*iw*on/{frames})"
        y = "ih/2-(ih/zoom/2)"
    elif modo == 3:                  # paneo vertical, sin zoom
        d = amp if idx % 2 == 0 else -amp
        z = "1.06"
        x = "iw/2-(iw/zoom/2)"
        y = f"ih/2-(ih/zoom/2)+({d}*ih*on/{frames})"
    elif modo == 4:                  # zoom in desplazandose en diagonal
        d = amp * 0.7
        z = f"min(zoom+{vel},1.10)"
        x = f"iw/2-(iw/zoom/2)+({d}*iw*on/{frames})"
        y = f"ih/2-(ih/zoom/2)+({d*0.5}*ih*on/{frames})"
    else:                            # imagen quieta: el ojo descansa
        z, x, y = "1.03", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"

    # El upscale de entrada es lo que mas cuesta: con scale=6000 cada clip de
    # 20 s tardaba 112 s. Con 3500 baja a 43 s (2.6x) sin diferencia visible:
    # 3500 px sobre 203 mm siguen siendo ~440 ppi, de sobra para pantalla e
    # impresion. Solo habria que subirlo si un paneo notase tembleque.
    vf = (f"scale=3500:-2,"
          f"zoompan=z='{z}':d={frames}:"
          f"x='{x}':y='{y}':fps={FPS}:s=1920x1080,"
          "format=yuv420p")
    subprocess.run(["ffmpeg", "-y", "-i", str(src_png), "-vf", vf,
                    "-frames:v", str(frames), "-r", str(FPS),
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                    "-an", str(out_mp4)], check=True, capture_output=True)


# Footage real del juego. Capturar la pantalla no funciona en WSLg (sale
# negro con x11grab y con Robot), asi que el juego se renderiza pidiendo al
# componente Swing que se pinte sobre un BufferedImage: una partida real,
# nitida y reproducible. Va en las escenas donde se explica el juego o los
# clics, que es donde ver la interfaz moviendose explica mas que una foto.
GAMEPLAY = {
    1:  "game_a.mp4",   # Parte Cero - el juego para todos
    3:  "game_c.mp4",   # Cap 2 - una partida bajo el microscopio (la larga)
    6:  "game_b.mp4",   # Cap 4 - compilar y ejecutar
    22: "game_a.mp4",   # Cap 18 - los eventos (los clics)
}


def scene_clip(idx, dur, rebuild=False):
    manim = WORK / "clips" / f"manim_s{idx}.mp4"
    clip = WORK / "clips" / f"s{idx}.mp4"

    if idx in GAMEPLAY:
        src = WORK / "clips" / GAMEPLAY[idx]
        if src.exists():
            vlen = wav_dur(src)
            pad = max(dur - vlen, 0.0)
            vf = ("scale=1080:1080:flags=lanczos,"
                  "pad=1920:1080:(ow-iw)/2:0:color=0x0B1020,"
                  "fps=30,format=yuv420p"
                  + (f",tpad=stop_mode=clone:stop_duration={pad:.2f}" if pad > 0.2 else ""))
            subprocess.run(["ffmpeg", "-y", "-i", str(src), "-vf", vf,
                            "-r", str(FPS), "-t", f"{dur:.2f}",
                            "-c:v", "libx264", "-preset", "veryfast",
                            "-crf", "19", "-an", str(clip)],
                           check=True, capture_output=True)
            return clip

    if manim.exists() and (rebuild or not clip.exists()):
        vlen = wav_dur(manim)
        pad = max(dur - vlen, 0.0)
        vf = "fps=30,format=yuv420p" + (f",tpad=stop_mode=clone:stop_duration={pad:.2f}" if pad > 0.2 else "")
        subprocess.run(["ffmpeg", "-y", "-i", str(manim), "-vf", vf,
                        "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast",
                        "-crf", "19", "-an", str(clip)], check=True, capture_output=True)
        return clip
    if rebuild or not clip.exists():
        kenburns(WORK / "slides" / f"s{idx}.png", dur, clip, idx)
    return clip


# ---------------------------------------------------------------- asamblea
FADE = 0.5  # fade in/out por escena (segundos)


def assemble(durs, out_mp4):
    n = len(durs)
    total = sum(durs)
    # --- pista de narración con offsets visuales
    mix = WORK / "audio" / f"narracion_v2_{n}.wav"
    placed = []
    for i, d in enumerate(durs):
        start = sum(durs[:i]) + 0.5
        adur = wav_dur(WORK / "audio" / f"s{i}.wav")
        rest = max(total - start - adur, 0.0)
        awe = WORK / "audio" / f"s{i}.wav"
        seg = WORK / "audio" / f"placed{i}.wav"
        subprocess.run(["sox", str(awe), str(seg), "pad", f"{start:.3f}", f"{rest:.3f}"],
                       check=True, capture_output=True)
        placed.append(str(seg))
    subprocess.run(["sox", "-m"] + placed + ["-c", "1", "-r", "24000", str(mix), "norm"],
                   check=True, capture_output=True)

    # --- video: fade in/out por escena + concat por lotes (memoria acotada)
    BATCH = 8
    full = WORK / "clips" / "video_full_v2.mp4"
    parts, listf = [], WORK / "clips" / "concat_list.txt"
    for g in range((n + BATCH - 1) // BATCH):
        idx = list(range(g * BATCH, min((g + 1) * BATCH, n)))
        fade_parts = []
        for j, i in enumerate(idx):
            st_out = max(durs[i] - FADE, 0.0)
            fade_parts.append(
                f"[{j}:v]setsar=1,fade=t=in:d={FADE},fade=t=out:st={st_out:.3f}:d={FADE}[v{j}]")
        concat_in = "".join(f"[v{j}]" for j in range(len(idx)))
        fade_parts.append(f"{concat_in}concat=n={len(idx)}:v=1:a=0[out]")
        cmd = ["ffmpeg", "-y"]
        for i in idx:
            cmd += ["-i", str(WORK / "clips" / f"s{i}.mp4")]
        part = WORK / "clips" / f"video_part_{g}.mp4"
        cmd += ["-filter_complex", ";".join(fade_parts), "-map", "[out]",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                "-r", str(FPS), "-an", str(part)]
        subprocess.run(cmd, check=True, capture_output=True)
        parts.append(part)
    listf.write_text("\n".join(f"file '{p.name}'" for p in parts) + "\n")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listf),
                    "-c", "copy", str(full)], check=True, capture_output=True)

    subprocess.run(["ffmpeg", "-y", "-i", str(full),
                    "-i", str(mix), "-filter_complex",
                    "[0:v]fade=t=in:st=0:d=0.6,fade=t=out:st={0:.3f}:d=1.5,format=yuv420p[v];"
                    "[1:a]afade=t=in:st=0:d=0.4,afade=t=out:st={0:.3f}:d=1.5[a]".format(total - 1.6,
                                                                                        total - 1.6),
                    "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                    "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out_mp4)],
                   check=True, capture_output=True)
    return out_mp4


def build_all(first_n=None, rebuild=False):
    scenes = build_scenes()
    if first_n:
        scenes = scenes[:first_n]
    print(f"Escenas: {len(scenes)}  voz={VOICE_ENGINE}  fundidos={XFADE}s")

    # Kokoro carga un modelo de 82M por proceso. Si se sintetiza escena por
    # escena eso son 41 cargas (casi una hora), asi que se pasa todo el lote de
    # una vez. Las escenas que ya tienen wav (rebuild parcial) se respetan.
    if VOICE_ENGINE == "kokoro":
        faltan = [(i, s) for i, s in enumerate(scenes)
                  if rebuild or not (WORK / "audio" / f"s{i}.wav").exists()]
        if faltan:
            print(f"Kokoro: {len(faltan)} escenas por sintetizar (una sola carga)")
            synth_all(faltan)

    durs = [prepare_scene(i, s, rebuild) for i, s in enumerate(scenes)]
    print("Audio + slides listos:")
    print(" ", [round(d, 1) for d in durs])
    for i, s in enumerate(scenes):
        scene_clip(i, durs[i], rebuild)
    print("Clips listos.")
    out = V / "Video_Explicativo_Triki_v2.mp4"
    assemble(durs, out)
    print("OK ->", out)


if __name__ == "__main__":
    # OJO: este bloque NO es un ambito de funcion, es el propio modulo. Por eso
    # la asignacion de abajo ya cambia la global, y por eso poner "global" aqui
    # da SyntaxError (el nombre ya fue asignado en la linea 37).
    args = sys.argv[1:]
    first_n = None
    rebuild = False
    rest = []
    for a in args:
        if a == "--rebuild":
            rebuild = True
        elif a.startswith("--voice"):
            i = args.index(a)
            VOICE_ENGINE = args[i + 1] if i + 1 < len(args) else "kokoro"
        elif a.isdigit():
            first_n = int(a)
        else:
            rest.append(a)
    build_all(first_n, rebuild)