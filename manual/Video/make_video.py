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
import re
import shutil
import subprocess
import sys
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
        ln = re.sub(r"!\[.*?\]\(.*?\)", "", ln)
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
def first_sentences(paras, max_words=40):
    full = " ".join(paras)
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", full) if s]
    words = 0
    picked = []
    for s in sentences:
        w = len(s.split())
        if words + w > max_words:
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


def narrate_text(scene, idx):
    _, _, _, narr = CONTENT.get(idx, scene["title"], scene["banner"])
    if narr:
        return expand_numbers(narr)
    t = scene["title"].strip()
    num = re.match(r"Capítulo (\d+):\s*(.*)", t)
    if num:
        name = num.group(2) or f"número {num.group(1)}"
        base = f"Capítulo {num.group(1)}: {name}. {first_sentences(scene['paras'])}"
    elif t.startswith("src/"):
        ctitle = CONTENT.get(idx, t, scene["banner"])[0]
        base = f"{ctitle}. {first_sentences(scene['paras'])}"
    else:
        base = f"{t}. {first_sentences(scene['paras'])}"
    return expand_numbers(base)


# ---------------------------------------------------------------- TTS
def synth(text, out_wav):
    if VOICE_ENGINE == "kokoro":
        p = subprocess.run([str(KOKORO_PYTHON), str(KOKORO_PY), text, str(out_wav)],
                           capture_output=True, text=True)
        if p.returncode != 0:
            print("KOKORO ERROR:", p.stderr[-300:])
            sys.exit(1)
        return p
    p = subprocess.run([str(PIPER), "--model", str(VOICE), "--output_file", str(out_wav),
                        "--length_scale", "1.05"],
                       input=text + "\n", capture_output=True, text=True)
    if p.returncode != 0:
        print("PIPER ERROR:", p.stderr[-300:])
        sys.exit(1)
    return p


# ---------------------------------------------------------------- slides
def slide_html(scene, idx):
    title, section, points, _ = CONTENT.get(idx, scene["title"], scene["banner"])
    # títulos de capítulo: quitar número ("Capítulo 14") -> muestra el enunciado
    if scene["kind"] != "part":
        title = re.sub(r"^Capítulo \d+:\s*", "", title)
    items = [html.escape(p) for p in (points or [])[:4]]
    bullets = "".join(f"<li>{i}</li>" for i in items)
    n = CONTENT.SECTIONS_N
    progress = f"{idx + 1:02d} / {n}"
    return f"""<div class="slide">
  <div class="orb o1"></div><div class="orb o2"></div>
  <div class="top"><span class="section">{html.escape(section)}</span>
    <span class="progress">{progress}</span></div>
  <h1>{html.escape(title)}</h1>
  <div class="rule"></div>
  <ul>{bullets}</ul>
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
    text = narrate_text(scene, idx)
    awav = WORK / "audio" / f"s{idx}.wav"
    apng = WORK / "slides" / f"s{idx}.png"
    if rebuild or not awav.exists():
        synth(text, awav)
    if rebuild or not apng.exists():
        build_slide(scene, idx, apng)
    adur = wav_dur(awav)
    return 0.5 + adur + 0.9


def kenburns(src_png, dur, out_mp4, idx):
    frames = max(int(round(dur * FPS)), int(2 * FPS))
    # panorámica suave alternando dirección según la escena
    drift = 0.06 if idx % 2 == 0 else -0.06
    x = f"iw/2-(iw/zoom/2)+({drift:.4f}*iw*on/{frames})"
    vf = (f"scale=6000:-2,"
          f"zoompan=z='min(zoom+0.0010,1.14)':d={frames}:"
          f"x='{x}':y='ih/2-(ih/zoom/2)':fps={FPS}:s=1920x1080,"
          "format=yuv420p")
    subprocess.run(["ffmpeg", "-y", "-i", str(src_png), "-vf", vf,
                    "-frames:v", str(frames), "-r", str(FPS),
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                    "-an", str(out_mp4)], check=True, capture_output=True)


def scene_clip(idx, dur, rebuild=False):
    manim = WORK / "clips" / f"manim_s{idx}.mp4"
    clip = WORK / "clips" / f"s{idx}.mp4"
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