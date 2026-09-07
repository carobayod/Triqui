#!/usr/bin/env python3
"""Ensambla el HTML final de cada diseño Canva y genera el PDF con WeasyPrint."""
import re
import subprocess
import sys
from pathlib import Path

MANUAL = Path("/home/carobayo/proyectos/Triqui/manual")
TEMPLATES = MANUAL / "templates_canva"
SRC = MANUAL / "Aprendiendo_a_programar_jugando_con_el_Triki.md"
TMP = Path("/tmp/opencode")

def pandoc_body():
    args = [
        "pandoc", str(SRC), "-t", "html5", "-s", "--embed-resources", "--toc", "--toc-depth=2",
        "--lua-filter=strip-emoji.lua",
        "--metadata", "lang=es",
    ]
    out = subprocess.run(args, capture_output=True, text=True)
    if out.returncode != 0:
        print("pandoc error:", out.stderr)
        sys.exit(1)
    # Extrae el <nav id="TOC">…</nav> y el cuerpo de contenido (sin envoltorio -s)
    html = out.stdout
    nav = ""
    rest = html
    m = re.search(r'<nav id="TOC".*?</nav>', html, re.S)
    if m:
        nav = m.group(0)
        rest = html[m.end():]
    content = rest
    m2 = re.search(r'(^.*?)<body[^>]*>(.*)</body>.*', html, re.S)
    if m2:
        content = m2.group(2)
        content = content.replace(nav, "", 1)
    return nav, content

def add_line_numbers(body):
    # Convert <span id="cb1-1"><a ...></a>CONTENT</span> en
    # <span class="codeline" data-line="1">CONTENT</span>
    def repl(m):
        num, content = m.group(1), m.group(2)
        return f'<span class="codeline" data-line="{num}">{content}</span>'
    return re.sub(
        r'<span id="cb\d+-(\d+)"><a href="#cb\d+-\d+" aria-hidden="true" tabindex="-1"></a>(.*?)</span>',
        repl, body, flags=re.S)

def build(style, css_file, cover_file, out_pdf):
    nav, content = pandoc_body()
    body = add_line_numbers(content)
    css = (TEMPLATES / "css_base.css").read_text()
    css += (TEMPLATES / css_file).read_text()
    cover = (TEMPLATES / cover_file).read_text()
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Libro Canva {style}</title>
<style>
{css}
</style>
</head>
<body>
{cover}
{nav}
{body}
</body>
</html>"""
    html_path = TMP / f"libro_{style}.html"
    html_path.write_text(html)
    p = subprocess.run(["weasyprint", str(html_path), str(MANUAL / out_pdf)], capture_output=True, text=True)
    if p.returncode == 0:
        print(f"OK {style}: {out_pdf} ({ (MANUAL / out_pdf).stat().st_size } bytes)")
    else:
        print(f"FALLO {style}: {p.stderr[-2000:]}")

if __name__ == "__main__":
    build("A", "css_A.css", "portada_A.html", "Libro_Aprende_Java_Triqui_Canva_A.pdf")
    build("B", "css_B.css", "portada_B.html", "Libro_Aprende_Java_Triqui_Canva_B.pdf")
    build("C", "css_C.css", "portada_C.html", "Libro_Aprende_Java_Triqui_Canva_C.pdf")