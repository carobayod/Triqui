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
| `.docx` | `pandoc Aprendiendo_a_programar_jugando_con_el_Triki.md -o Aprendiendo_a_programar_jugando_con_el_Triki.docx` | `unzip -l` (word/document.xml), tamaño |
| `.epub` | `pandoc <canónica> -o Libro_Aprende_Java_Triqui.epub --toc --toc-depth=2 --metadata lang=es` | `unzip -l` (mimetype), epubcheck si existe |
| Canva A/B/C (HTML→PDF) | `python3 templates_canva/build_canva.py` (pandoc html5 embed `--toc-depth=2` + `--lua-filter=strip-emoji.lua`, plantillas `css_*.css` + `portada_*.html`, WeasyPrint) | `pdfinfo` páginas/tamaño |
| Premium (LaTeX/xelatex) | `pandoc <canónica> --pdf-engine=xelatex -H header.tex --include-before-body cover.tex --lua-filter ... -o Libro_Aprende_Java_Triqui_Premium.pdf` | `pdfinfo` + render de páginas (`pdftoppm`) |

Filtros lua disponibles: `boxes-tcolorbox.lua` (callouts 💡⚠️🏆 → tcolorbox), `fix-figure.lua`, `highlight-final.lua`, `strip-newpage.lua`, `strip-emoji.lua` (usado solo en Canva; en LaTeX los emojis pasan por tcolorbox).

Regeneración completa: command `/rebuild-libro` o skill `book-building`.

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

## Convenciones del libro

- Capítulos: `## Capítulo N: título`. Retos `🏆 RETO DE CÓDIGO`, consejos `> 💡 CONSEJO:` o `> 💡 TIP:`, errores `> ⚠️ BUG ALERT`, bloques "> 🧠" (poda alfa-beta).
- Cada capítulo cierra con `**REPASO DEL CAPÍTULO**` (3 preguntas a/b/c + respuesta) y un reto.
- Render en LaTeX vía tcolorbox (`consejocolor`/`bugcolor`); en Canva/HTML se quitan los emojis (`strip-emoji.lua`).
- Imágenes: `![texto](assets/...)`. TOC de pandoc depth 2 → solo H1 (partes) y H2 (capítulos) entran al índice.
- Código en Java con resaltado de listings (LaTeX) / highlight-js (HTML).

## Entorno y trampas operativas

- Java 25, Maven 3.9.12. X server: `DISPLAY=:0` (WSLg, 1920x1080).
- Lanzar apps Swing: `setsid java -jar ... >log 2>&1 </dev/null & disown` con timeout corto. **Nunca** `pkill -f` con patrón que coincida con el propio comando (usar corchetes, p.ej. `'[t]etris-1.0.jar'`).
- venvs del proyecto: `.venv` (manim, piper), `.venv312` (kokoro, python 3.12).
- Herramientas de build en PATH: `ffmpeg`, `ffprobe`, `sox`, `weasyprint`, `pdftoppm`, `pandoc`, `xelatex`.
- `target/` y artefactos están en `.gitignore`; no commitear `manual/Video/work/`, `media/` ni binarios grandes.