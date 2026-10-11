#!/usr/bin/env bash
# Regenera los 6 diagramas del libro desde sus fuentes .dot
#
#   cd manual && ./assets/build_diagramas.sh
#
# Por que existe: hasta ahora los .png se generaban a mano con "dot -Tpng" y se
# commitearon. Eso hacia imposible cambiar un color o corregir una etiqueta sin
# rehacer las 6 imagenes una por una, y no dejaba registro de con que ajustes
# se generaron (los .png salian sin metadato de dpi).
#
# Salidas, por cada .dot:
#   <nombre>.png  600 dpi, para el DOCX, el EPUB y el PDF Premium (LaTeX)
#   <nombre>.svg  vector, para los PDF HTML/Chromium y para el futuro
#   <nombre>.pdf  vector, para LaTeX (\includegraphics no acepta .svg)
#
# NOTA sobre formatos: el Markdown canonico solo puede apuntar a una extension.
# hoy sigue apuntando a .png porque el PDF Premium va por xelatex y LaTeX no
# acepta SVG en \includegraphics. Los .svg y .pdf quedan como material listo
# para cuando el libro tenga una edicion web.
set -euo pipefail
cd "$(dirname "$0")"

DPI="${DPI:-600}"

echo "== diagramas (dot -Tpng -Gdpi=$DPI, dot -Tsvg, dot -Tpdf) =="
for src in *.dot; do
  base="${src%.dot}"
  dot -Tpng -Gdpi="$DPI" "$src" -o "$base.png"
  dot -Tsvg            "$src" -o "$base.svg"
  dot -Tpdf            "$src" -o "$base.pdf"
  printf "   %-24s png %-20s |  svg %s KB  |  pdf %s KB\n" \
    "$base" \
    "$(python3 -c "from PIL import Image;im=Image.open('$base.png');print('%dx%d px'%(im.size[0],im.size[1]))")" \
    "$(( $(stat -c%s "$base.svg") / 1024 ))" \
    "$(( $(stat -c%s "$base.pdf") / 1024 ))"
done

echo ""
echo "Regenerados: $(ls -1 *.dot | wc -l) diagramas."
echo "Verificacion: el .png debe dar ~${DPI} ppi en el PDF; comprueba con"
echo "  pdfimages -list ../Libro_Aprende_Java_Triqui_Premium.pdf | grep -i $base"