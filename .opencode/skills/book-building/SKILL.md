---
name: book-building
description: Regenera y verifica todas las salidas del libro del Triki (docx, epub, PDF Canva A/B/C vía HTML/WeasyPrint, PDF Premium vía LaTeX/xelatex) desde la fuente canónica markdown. Use when the user mentions "libro", "manual", "regenerar docx/epub/pdf", "canva", "premium", "latex", "avanzar el libro", "actualizar el pdf".
---

# Book building — manual del Triki

Escribe/edita SOLO la fuente canónica. Todo lo demás se regenera.

## Fuente única

- `manual/Aprendiendo_a_programar_jugando_con_el_Triki.md` — canónica (front matter YAML, párrafos sin wrap).
- `manual/Libro_Aprende_Java_Triqui.md` — variante reenrollada histórica: respaldo, NO editar.

## Comandos por formato (ejecutar desde `manual/`)

### .docx
```
pandoc Aprendiendo_a_programar_jugando_con_el_Triki.md -o Aprendiendo_a_programar_jugando_con_el_Triki.docx
```
### .epub
```
pandoc Aprendiendo_a_programar_jugando_con_el_Triki.md -o Libro_Aprende_Java_Triqui.epub --toc --toc-depth=2 --metadata lang=es
```
### Canva A/B/C (HTML → PDF, WeasyPrint)
```
python3 templates_canva/build_canva.py
```
Regenera `Libro_Aprende_Java_Triqui_Canva_{A,B,C}.pdf`. Internamente: pandoc `html5 -s --embed-resources --toc --toc-depth=2 --lua-filter=strip-emoji.lua --metadata lang=es`, extrae `<nav id="TOC">` + body, aplica `css_base.css` + `css_{A,B,C}.css` y `portada_{A,B,C}.html`, y llama `weasyprint`. No tocar el orden de filtros.
### Premium (LaTeX → PDF, xelatex)
```
pandoc Aprendiendo_a_programar_jugando_con_el_Triki.md -o Libro_Aprende_Java_Triqui_Premium.pdf \
  --pdf-engine=xelatex --toc \
  -H header.tex \
  -H cover.tex \
  --lua-filter=highlight-final.lua \
  --lua-filter=fix-figure.lua \
  --lua-filter=strip-newpage.lua \
  --lua-filter=boxes-tcolorbox.lua
```
Notas: `cover.tex` redefine `\maketitle` (portada azul) y carga `tcolorbox` (ppio clase). `boxes-tcolorbox.lua` envuelve 💡CONSEJO / ⚠️BUG en tcolorbox; `highlight-final.lua` la recomendación final. Ambos definen `BlockQuote`; ejecútalos como dos filtros separados en el orden indicado.

## Verificación

| Salida | Comprobación |
|---|---|
| docx | `unzip -l Aprendiendo_a_programar_jugando_con_el_Triki.docx` → contiene `word/document.xml`; tamaño razonable |
| epub | `unzip -l Libro_Aprende_Java_Triqui.epub` → `mimetype`; `epubcheck` si existe |
| Canva x3 | `pdfinfo Libro_Aprende_Java_Triqui_Canva_A.pdf` → páginas y tamaño; abrir render de 2-3 páginas (`pdftoppm -png -r 60`) para ver portada y código |
| Premium | `pdfinfo Libro_Aprende_Java_Triqui_Premium.pdf`; render de portada y 2 páginas (`pdftoppm -png -f 1 -l 3`) |

Verifica siempre con `git diff --stat` que la canónica cambió sustancialmente antes de regenerar. Tras reorg, confirmar en el TOC (pandoc: `pandoc -t html --toc --toc-depth=2 <md> | grep -c "<li"` o el índice del propio PDF) que aparecen Parte 0, nuevas numeraciones y apéndice consolidado.

## Gotchas

- Emojis 💡⚠️🏆🧠: se eliminan SOLO en Canva (strip-emoji.lua); en LaTeX entran por tcolorbox. No "limpiar" emojis a mano en la fuente.
- `strip-newpage.lua` quita `\\newpage` solo para LaTeX (lo usan los scripts para separar secciones en HTML).
- La fuente usa párrafos sin wrap: ¿puede, el reglón muy largo por edición, romper diff? Mantener estilo existente al editar.
- Nunca regenerar el PDF Premium/Canva a mano en los DOI; si el resultado sale con páginas en blanco de más, revisar `strip-newpage`/`toc-depth`.
- No editar `.docx`/`.epub`/`.pdf` a mano jamás.