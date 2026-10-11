# AGENTS.md — Triqui (juego + libro + video)

## Qué es este repo

- **Juego**: Triki en Java Swing + IA minimax. Repo `carobayod/Triqui` (remoto SSH).
- **`manual/`**: libro "Aprende Java Jugando" (fuente markdown + salidas docx/epub/PDF) y video explicativo.

## Fuente canónica del libro

- **`manual/Aprendiendo_a_programar_jugando_con_el_Triki.md`** — ÚNICA fuente editable (front matter YAML, párrafos sin wrap).
- `manual/Libro_Aprende_Java_Triqui.md` — variante reenrollada histórica. **Respaldo, no editar**; el `.epub` se regenera desde la canónica.
- Todos los `.docx`, `.epub`, PDF Canva (HTML) y PDF Premium (LaTeX) son **salidas generadas** — nunca editar a mano; se regeneran desde la canónica.

## Pipeline del libro (formato → comando)

Desde `manual/`:

| Formato | Comando | Verificación |
|---|---|---|
| `.docx` | `pandoc Aprendiendo_a_programar_jugando_con_el_Triki.md -o Aprendiendo_a_programar_jugando_con_el_Triki.docx --reference-doc=reference.docx` | `unzip -l` (word/document.xml), tamaño, `word/theme/theme1.xml` → Georgia |
| `.epub` | `pandoc <canónica> -o Libro_Aprende_Java_Triqui.epub --toc --toc-depth=2 --metadata lang=es` | `unzip -l` (mimetype), epubcheck si existe |
| Canva A/B/C (HTML→PDF) | `python3 templates_canva/build_canva.py` (pandoc html5 embed `--toc-depth=2` + `--lua-filter=strip-emoji.lua`, plantillas `css_*.css` + `portada_*.html`, WeasyPrint) | `pdfinfo` páginas/tamaño |
| Premium (LaTeX/xelatex) | `pandoc <canónica> --pdf-engine=xelatex -V papersize=a4 -H header.tex -H cover.tex --listings --lua-filter ... -o Libro_Aprende_Java_Triqui_Premium.pdf` | `pdfinfo` + render de páginas (`pdftoppm`) |

Filtros lua disponibles: `boxes-tcolorbox.lua` (callouts 💡⚠️🏆 → tcolorbox), `fix-figure.lua`, `highlight-final.lua`, `strip-newpage.lua`, `strip-emoji.lua` (usado solo en Canva; en LaTeX los emojis pasan por tcolorbox).

Regeneración completa: command `/rebuild-libro` o skill `book-building`.

### Diagramas

Los 6 diagramas del libro se generan desde sus fuentes `.dot` en `manual/assets/`:
`tablero_reglas`, `partida_secuencia`, `mapa_clases`, `minimax_basic`, `minimax_tree`,
`flujo_turno`. (`mockup_juego.png` NO tiene .dot: es una captura real.)

```
cd manual/assets && ./build_diagramas.sh          # png 600dpi + svg + pdf
cd manual/assets && DPI=300 ./build_diagramas.sh  # si el peso molesta
```

El Markdown canónico apunta a los `.png` (no a los `.svg`): el PDF Premium va por
xelatex y **LaTeX no acepta SVG** en `\includegraphics`. Los `.svg` y `.pdf` quedan
generados como material vectorial listo para una futura edición web. Los PNG a 600dpi
dan 641–1114 ppi en el PDF final (por encima del estándar de impresión de 300).

### Motor PDF del libro: Chromium (decidido 2026-10-11)

El libro se genera con **Chromium** (Playwright), no con WeasyPrint. Motivo: Chromium
implementa el CSS de paged media (`@page`, margin boxes, `counter(page)`, páginas
con nombre) igual que WeasyPrint, y además numera portada e índice.

| | |
|---|---|
| **Herramienta canónica** | `~/herramientas/pdf-chromium/build_pdf.mjs` — genérica, por flags, con README. **Es la que se usa.** |
| Script acoplado (solo procedencia) | `manual/build_playwright.mjs` — generaba los `Chromium_{A,B,C}.pdf` de la comparación |

```
cd manual && node ~/herramientas/pdf-chromium/build_pdf.mjs \
  --fuente Aprendiendo_a_programar_jugando_con_el_Triki.md \
  --plantilla templates_canva --tema C --lua-filter strip-emoji.lua \
  --salida Libro_Aprende_Java_Triqui_Chromium_C.pdf --verificar
```

**Lo que NO cambia**: WeasyPrint sigue usándose para los PDF Canva A/B/C (salidas ya
entregadas) y para los slides del video (`make_video.py`). La decisión aplica solo al
motor del **libro** cuando se regenere.

Chromium no soporta `target-counter`, así que el índice paginado se resuelve con
**dos pasadas** (la herramienta lo hace). `--verificar` avisa si el paginado o el
índice no cuadran: si dice `DESAJUSTE`, no publicar.

Diferencias medidas Chromium vs WeasyPrint (por si hay que comparar):
Chromium da ~1 página menos, numera portada e índice, y sustituye FiraCode-SemiBold
por Regular. El texto es idéntico salvo los números de página corridos una.

## Skill externo: archify (auditoría de diagramas, no pipeline)

Instalado global en `~/.agents/skills/archify` (82k estrellas, MIT). Es un skill de
opencode que genera diagramas **interactivos HTML** leyendo el código. No se usa para
generar los diagramas del libro (su tipografía es JetBrains Mono y rompe Georgia+Fira
Code). Se puede usar para **auditar el contenido** de los `.dot` contra el código real.
Su salida vive en el Desktop: `Triqui_Libro/Mapa_clases_Archify/`.

## Pipeline del video (v2)

Fuente: la canónica + `manual/Video/slide_content.py` (38 escenas curadas) → `make_video.py`:

1. `build_scenes()`: parsea el `.md` en 38 escenas.
2. `narrate_text()`: narración de `slide_content.py`, si no, título + primeras frases; `expand_numbers()` convierte números a palabras.
3. TTS **Kokoro** voz `ef_dora` (`.venv312/bin/python manual/Video/synth_kokoro.py <texto> <out.wav>`) → wav 24 kHz mono. Alternativa Piper (`--voice piper`).
4. Slides: HTML (título + puntos + progreso) → WeasyPrint PDF 16:9 → `pdftoppm` PNG 240 dpi.
5. Clips: Manim (`manim -qh manim_scenes.py`, `.venv`) si existe `work/clips/manim_s<N>.mp4`; si no **Ken Burns** ffmpeg zoompan 1920x1080@30.
6. Ensamblado: narración con `sox` (pad+mix 1ch 24k norm); **concat por lotes (BATCH=8)** con fades 0.5 s y `setsar=1` — el docstring del script aún dice xfade pero el código real NO usa xfade (OOM histórico).

Uso: `python3 manual/Video/make_video.py [--first N] [--voice kokoro|piper] [--rebuild]`.
Verificación: `ffprobe` → 1920x1080p30, h264 yuv420p, aac mono, duración ~8:57. Command `/rebuild-video` / skill `triki-video`.

## Estado del plan (relevante para futuras sesiones)

- **Reorganización del libro HECHA**: nueva estructura ya en la canónica — Parte Cero "El juego, para todos" (2 caps nuevos: reglas + partida bajo el microscopio), Parte I "Prepara el taller" (entorno + ejecutar temprano), Parte II fundamentos, Parte III "Cómo está construido" (mapa del código primero, Cap 14), Parte IV herramientas (CLI absorbida como Cap 23), glosario + apéndice de "Referencia rápida" (sin duplicar la Parte III). 29 capítulos, todos renumerados y con referencias cruzadas actualizadas.
- **Formatos regenerados** (docx, epub, Canva A/B/C, Premium LaTeX) desde la canónica y verificados. Copias nuevas en `/mnt/c/Users/57350/OneDrive/Desktop/Triqui_Libro/` (los archivos antiguos con sufijo `_` son entregas previas, se pueden borrar).
- **Acoplamiento video**: el video v2 NO se regeneró (decisión). `slide_content.py` ya está re-mapeado al nuevo libro = **41 escenas futuras** (SECTIONS_N=41); si se redescribe el video se obtendrá esa cantidad, no 38.
- Skills/commands de opencode en `.opencode/` (ver arriba). Recordar: al modificar `.opencode/` hay que **reiniciar opencode** para que cargue.
- **Curso Hotmart "Documentos PRO con IA" (paralelo, 2026-10-11)**: en `~/proyectos/hotmart_proyecto.md` (fuera de este repo). NO es el libro del Triki: es un curso nuevo sobre crear PDF/Word/EPUB profesionales. El libro solo se cita, **no se toca**. Índice v3 aprobado (9 módulos · 48 lecciones) pero el texto de las lecciones vive solo en el chat: recuperar de ahí antes de escribir.

## Pendientes conocidos (2026-10-11)

1. **Revocar el PAT de GitHub** que se expuso al inicio de una sesión de octubre.
2. **Curso Hotmart**: recuperar el índice v3 y el Módulo 1 del chat.

Resueltos el 2026-10-11: motor PDF elegido (Chromium), garantía de 30 días definida
en `ventas/copy_hotmart_para_quien_no.md`, `.md` del Desktop sincronizado con la
canónica, diagramas regenerados a 600 dpi.

## Convenciones del libro

- Capítulos: `## Capítulo N: título`. Retos `🏆 RETO DE CÓDIGO`, consejos `> 💡 CONSEJO:` o `> 💡 TIP:`, errores `> ⚠️ BUG ALERT`, bloques "> 🧠" (poda alfa-beta).
- Cada capítulo cierra con `**REPASO DEL CAPÍTULO**` (3 preguntas a/b/c + respuesta) y un reto.
- Render en LaTeX vía tcolorbox (`consejocolor`/`bugcolor`); en Canva/HTML se quitan los emojis (`strip-emoji.lua`).
- Imágenes: `![texto](assets/...)`. TOC de pandoc depth 2 → solo H1 (partes) y H2 (capítulos) entran al índice.
- Código en Java con resaltado de listings (LaTeX) / highlight-js (HTML).
- **Tipografía (unificada 2026-09-26)**: Georgia para todo el texto (cuerpo, títulos, portada, paginación) y Fira Code para el código, en los 4 PDF, el EPUB y el DOCX. En LaTeX: nada de `\sffamily` ni de color en los `titlesec` de `header.tex`. En CSS: la regla `code { font-family }` debe existir (si no, el código en línea cae al `monospace` genérico) y `@bottom-center` no debe usar Liberation Sans. `pdffonts` debe dar solo Georgia (3) + Fira Code (2).
- **Diagramas (2026-10-11)**: los 6 `.dot` se regeneran con `build_diagramas.sh` a 600 dpi (641–1114 ppi en el PDF). `mapa_clases.dot` ahora muestra los **dos** caminos de la máquina (fácil=aleatoria, difícil=inteligente→IA) mediante el nodo `nivel`; antes solo mostraba el camino de la IA, lo que hacía pensar que siempre usaba minimax.

## Entorno y trampas operativas

- Java 25, Maven 3.9.12. X server: `DISPLAY=:0` (WSLg, 1920x1080).
- Lanzar apps Swing: `setsid java -jar ... >log 2>&1 </dev/null & disown` con timeout corto. **Nunca** `pkill -f` con patrón que coincida con el propio comando (usar corchetes, p.ej. `'[t]etris-1.0.jar'`).
- venvs del proyecto: `.venv` (manim, piper), `.venv312` (kokoro, python 3.12).
- Herramientas de build en PATH: `ffmpeg`, `ffprobe`, `sox`, `weasyprint`, `pdftoppm`, `pandoc`, `xelatex`.
- `target/` y artefactos están en `.gitignore`; no commitear `manual/Video/work/`, `media/` ni binarios grandes.