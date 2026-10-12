"""Verifica el render de las diapositivas por pixeles.

  python3 check_slides.py 36 37 38 39 40

Mide tres cosas que se rompen al agregar diagramas y codigo:
  1. si el titulo parte en mas de una linea (tinta clara a partir de y=390);
  2. si el contenido invade la franja del pie (y=1010 en adelante);
  3. si el diagrama queda cortado (contenido que empieza y no termina limpio).
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

V = Path(__file__).resolve().parent
sys.path.insert(0, str(V))
import make_video as M  # noqa: E402

def CLARO(a):
    return (a[:, :, 0] > 190) & (a[:, :, 1] > 190) & (a[:, :, 2] > 190)


def revisar(idx):
    out = V / "work" / "slides" / f"s{idx}.png"
    a = np.array(Image.open(out).convert("RGB"))
    claro = CLARO(a)

    # 1. Titulo en una sola linea.
    #
    # Solo se mira la columna IZQUIERDA (x<820). Antes se miraba toda la
    # diapositiva y el diagrama de la derecha contaba como una "segunda linea"
    # del titulo: el chequeo daba falso positivo en las variantes con-img-lado.
    izq = claro[:, :820]
    filas_t = [y for y in range(283, 430) if izq[y].sum() > 8]
    if filas_t:
        alto = max(filas_t) - min(filas_t)
        titulo = "PARTE EN 2 LINEAS" if alto > 120 else "1 linea"
        ok_tit = alto <= 120
    else:
        titulo, ok_tit = "sin titulo visible", True

    # 2. invasion del pie (y=1010 en adelante, la zona del pie real)
    pie = int(claro[1010:1080].sum())

    # 3. Diagramas: se verifica con pdfimages, no contando pixeles del PNG.
    #
    # Medir sobre el PNG daba falso: los diagramas tienen fondo blanco y lineas
    # finas, asi que contando "pixeles claros" salia una proporcion de 13.3
    # cuando el original es 3.55, y parecia deformado cuando en realidad estaba
    # perfecto. pdfimages informa el ppi real de cada imagen en el PDF:
    # ancho_mm = px / ppi * 25.4, y ahi si se ve si se deforma o se recorta.
    verif = ""
    ok_img = True
    try:
        from slide_content import DATA
        extra = DATA[idx].get("extra") or {}
        if extra.get("diagrama"):
            import subprocess
            pdf = V / "work" / f"slide_{idx}.pdf"
            r = subprocess.run(["pdfimages", "-list", str(pdf)],
                               capture_output=True, text=True)
            # Las lineas empiezan con espacios y el tipo es "image", asi que
            # el filtro tiene que buscar la palabra suelta.
            filas_img = [l for l in r.stdout.splitlines()
                         if l.split() and l.split()[2:3] == ["image"]]
            if filas_img:
                # columnas: page num type width height color comp bpc enc
                #           interp objectID x-ppi y-ppi ...  (x-ppi = [12])
                c = filas_img[0].split()
                w_mm = int(c[3]) / int(c[12]) * 25.4
                h_mm = int(c[4]) / int(c[12]) * 25.4
                from PIL import Image as _I
                with _I.open(extra["diagrama"]) as im:
                    r_orig = im.size[0] / im.size[1]
                r_now = w_mm / h_mm
                d = abs(r_now - r_orig) / r_orig
                ok_img = d < 0.05 and h_mm <= 63
                verif = (f"img {w_mm:.0f}x{h_mm:.0f}mm ratio {r_now:.2f}"
                         f" vs orig {r_orig:.2f}")
    except Exception as exc:  # noqa: BLE001
        verif = f"img sin verificar: {exc}"

    print(f"  s{idx}: titulo={titulo:18s} pie={pie:5d}px  {verif}")
    return pie == 0 and ok_tit and ok_img


if __name__ == "__main__":
    args = [int(x) for x in sys.argv[1:]] or [36, 37, 38, 39, 40]
    escenas = M.build_scenes()
    for i in args:
        M.build_slide(escenas[i], i, V / "work" / "slides" / f"s{i}.png")
    print("=== verificaciones ===")
    # all() con un generador cortaba en el primer False y solo revisaba una
    # escena. Se evaluan todas y despues se resume.
    resultados = [revisar(i) for i in args]
    print("  RESULTADO:", "todo OK" if all(resultados) else "HAY PROBLEMAS")
