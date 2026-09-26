#!/usr/bin/env python3
"""Genera manual/reference.docx: el docx de referencia de pandoc con Georgia.

Por qué hace falta: `pandoc -o libro.docx` usa su reference.docx por defecto,
cuyo docDefaults NO declara fuente (delega en el tema, que en las versiones
recientes de Office es Aptos). Eso hacía que el DOCX se viera distinto al PDF
y distinto en cada lector. Este script parte del reference.docx que trae
pandoc y le pone Georgia en el tema y en los estilos, para que el DOCX se lea
igual que el libro.

Uso (desde manual/):  python3 make_reference_docx.py
Luego:                pandoc FUENTE.md -o SALIDA.docx --reference-doc=reference.docx
"""

import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

RAIZ = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(RAIZ, "reference.docx")

# Colores de título del reference.docx por defecto (0F4761 heading, 365F91 TOC).
COLOR_TITULO_POR_DEFECTO = ("0F4761", "365F91", "595959", "272727")
COLOR_LINK = "1A237E"  # el mismo azul de los enlaces en los PDF (css_base.css)
CODIGO = "Consolas"  # el code del DOCX; Fira Code no suele estar en el lector


def parchear_tema(xml: str) -> str:
    """Pone Georgia como fuente mayor y menor del tema (era Aptos)."""
    xml, n1 = re.subn(
        r'(<a:(?:major|minor)Font>\s*<a:latin typeface=")[^"]*("[^/]*/>)',
        r"\1Georgia\2",
        xml,
    )
    return xml, n1


def parchear_estilos(xml: str) -> str:
    """Fija Georgia en docDefaults y en los títulos; pone los títulos en negro."""
    cambios = 0

    # 1. docDefaults: fuente explícita en vez de la del tema.
    nuevo_rfonts = (
        '<w:rFonts w:ascii="Georgia" w:hAnsi="Georgia" '
        'w:eastAsia="Georgia" w:cs="Georgia" />'
    )
    xml, n = re.subn(r"<w:rFonts w:asciiTheme=\"[^\"]*\"[^/]*/>", nuevo_rfonts, xml)
    cambios += n

    # 2. Estilos de título: Georgia explícito (majorHAnsi -> Georgia).
    xml, n = re.subn(
        r'w:asciiTheme="majorHAnsi"[^/]*?w:hAnsiTheme="majorHAnsi"',
        'w:ascii="Georgia" w:hAnsi="Georgia" w:cs="Georgia"',
        xml,
    )
    cambios += n

    # 3. Títulos en negro: el PDF los tiene en negro tras el cambio de 2026-09.
    for color in COLOR_TITULO_POR_DEFECTO:
        xml, n = re.subn(r'<w:color w:val="%s"' % color, '<w:color w:val="auto"', xml)
        cambios += n

    # 4. Enlaces en el azul del libro.
    xml, n = re.subn(
        r'<w:color w:val="4F81BD"', '<w:color w:val="%s"' % COLOR_LINK, xml
    )
    cambios += n

    return xml, cambios


def main() -> int:
    tmp = tempfile.mkdtemp(prefix="refdocx-")
    try:
        crudo = os.path.join(tmp, "default.docx")
        with open(crudo, "wb") as fh:
            subprocess.run(
                ["pandoc", "--print-default-data-file", "reference.docx"],
                stdout=fh,
                check=True,
            )

        with zipfile.ZipFile(crudo) as zin:
            nombres = zin.namelist()
            datos = {n: zin.read(n) for n in nombres}

        # theme1.xml: Georgia como fuente mayor y menor.
        clave = next((n for n in datos if n.endswith("theme1.xml")), None)
        if clave is None:
            print("ERROR: el reference.docx no trae theme1.xml", file=sys.stderr)
            return 1
        tema, n = parchear_tema(datos[clave].decode("utf-8"))
        datos[clave] = tema.encode("utf-8")
        print("theme1.xml: %d fuentes del tema fijadas en Georgia" % n)

        # styles.xml: docDefaults, títulos en Georgia y en negro.
        clave = next((n for n in datos if n.endswith("word/styles.xml")), None)
        estilos, cambios = parchear_estilos(datos[clave].decode("utf-8"))
        datos[clave] = estilos.encode("utf-8")
        print("styles.xml: %d cambios" % cambios)

        # VerbatimChar (código en línea) y SourceCode (bloques) en Consolas.
        texto = datos[clave].decode("utf-8")
        texto, n = re.subn(
            r'(<w:style [^>]*w:styleId="(?:VerbatimChar|SourceCode)".*?)'
            r'w:ascii="[^"]*"',
            r'\1w:ascii="%s"' % CODIGO,
            texto,
            flags=re.S,
        )
        print("código en línea/bloques: %d estilos en %s" % (n, CODIGO))
        datos[clave] = texto.encode("utf-8")

        with zipfile.ZipFile(SALIDA, "w", zipfile.ZIP_DEFLATED) as zout:
            for n in nombres:  # se respeta el orden original
                zout.writestr(n, datos[n])
        print("OK %s (%d bytes)" % (SALIDA, os.path.getsize(SALIDA)))
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
