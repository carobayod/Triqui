"""Renderiza una diapositiva y mide el diagrama con pdfimages.

  python3 medir_s40.py

Se usa pdfimages y no los pixeles del PNG porque contar "pixeles claros" da
falsos: los diagramas tienen fondo blanco y lineas finas, y el resultado
parecia 13.35 de proporcion cuando el diagrama estaba perfecto. pdfimages
informa el ppi real de cada imagen en el PDF, y de ahi sale el tamano en mm:
ancho_mm = px / ppi * 25.4.
"""
import subprocess
import sys
from pathlib import Path

V = Path(__file__).resolve().parent
sys.path.insert(0, str(V))

import make_video as M  # noqa: E402
import slide_content as S  # noqa: E402
from slide_content import DATA  # noqa: E402

VARIANTES = {
    "A_2filas": "flujo_turno_video.png",
    "B_vertical": "f_vert.png",
    "C_3filas": "f3.png",
}


def medir(idx, etiqueta, fichero):
    DATA[idx]["extra"] = dict(diagrama=S.ASSETS / fichero,
                              alt="Flujo de un turno", lado="abajo")
    escenas = M.build_scenes()
    pdf = Path(f"/tmp/opencode/med_{etiqueta}.pdf")
    html = M.SLIDE_CSS.read_text()
    doc = (f"<!DOCTYPE html><html lang=es><head><meta charset=utf-8><style>\n"
           f"@page {{ size: 203.2mm 114.3mm; margin:0 }}\n"
           f"html,body {{ margin:0; padding:0 }}\n{html}\n</style></head>"
           f"<body>{M.slide_html(escenas[idx], idx)}</body></html>")
    tmp = Path(f"/tmp/opencode/med_{etiqueta}.html")
    tmp.write_text(doc, encoding="utf-8")
    subprocess.run(["weasyprint", str(tmp), str(pdf)], capture_output=True)

    r = subprocess.run(["pdfimages", "-list", str(pdf)],
                       capture_output=True, text=True)
    filas = [l for l in r.stdout.splitlines()
             if l.split() and l.split()[2:3] == ["image"]]
    if not filas:
        print(f"  {etiqueta:11s} sin imagen en el PDF")
        return
    c = filas[0].split()
    w = int(c[3]) / int(c[12]) * 25.4
    h = int(c[4]) / int(c[12]) * 25.4
    from PIL import Image
    with Image.open(S.ASSETS / fichero) as im:
        ro = im.size[0] / im.size[1]
    d = abs(w / h - ro) / ro
    print(f"  {etiqueta:11s} {w:5.0f}x{h:4.0f}mm  ratio {w/h:5.2f} "
          f"vs orig {ro:5.2f}  {'OK' if d < 0.05 else 'DEFORMADO'}")


if __name__ == "__main__":
    print("=== como queda el diagrama en la diapositiva 41/41 ===")
    for etiqueta, fichero in VARIANTES.items():
        medir(40, etiqueta, fichero)
    print("\n  la diapositiva util son 63mm de alto desde top:30mm,")
    print("  y 168mm de ancho. Cuanto mas alto, mas grande el texto del diagrama.")
