---
description: Regenera todas las salidas del libro del Triki (docx, epub, Canva A/B/C y Premium LaTeX) desde la fuente canónica.
agent: build
---

Regenera el libro completo siguiendo la skill `book-building`:

1. Carga la skill `book-building`.
2. Verifica que `manual/Aprendiendo_a_programar_jugando_con_el_Triki.md` es la fuente y está actualizado (git diff).
3. Ejecuta los comandos en orden (desde `manual/`):
   - docx → `pandoc Aprendiendo_a_programar_jugando_con_el_Triki.md -o Aprendiendo_a_programar_jugando_con_el_Triki.docx`
   - epub → `pandoc Aprendiendo_a_programar_jugando_con_el_Triki.md -o Libro_Aprende_Java_Triqui.epub --toc --toc-depth=2 --metadata lang=es`
   - Canva → `python3 templates_canva/build_canva.py`
   - Premium → comando xelatex de la skill
4. Verifica cada salida (pdfinfo/unzip/render).
5. Nota en el reporte final: NO regenerar el video salvo petición explícita (acoplamiento en AGENTS.md).