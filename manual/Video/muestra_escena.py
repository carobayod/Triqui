"""Prueba: una escena con dos voces de Kokoro.

  python3 muestra_escena.py <indice_escena> <voz1> [voz2 ...]

Sirve para comparar el texto normalizado (normalize_for_tts) entre voces sin
tener que generar el video entero. Se apoya en que synth_kokoro.py carga el
modelo una vez por invocacion, que aqui se paga una sola vez para todas las
voces pedidas.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
V = Path(__file__).resolve().parent
sys.path.insert(0, str(V))

import make_video as M  # noqa: E402
import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402
from kokoro import KPipeline  # noqa: E402


def main():
    idx = int(sys.argv[1])
    voces = sys.argv[2:] or ["ef_dora", "em_alex"]
    destino = Path(sys.argv[0]).resolve().parent / "muestras_voz_kokoro"
    destino.mkdir(exist_ok=True)

    escenas = M.build_scenes()
    texto = M.normalize_for_tts(M.narrate_text(escenas[idx], idx))
    print(f"Escena {idx}: {escenas[idx]['title']}")
    print(f"Texto ({len(texto)} chars):\n  {texto}\n")

    # Un solo pipeline para todas las voces: KPipeline carga el modelo de 82M
    # una vez y despues solo cambia el vector de voz.
    pipe = KPipeline(lang_code="e")
    for voz in voces:
        try:
            partes = [r.audio for r in pipe(texto, voice=voz)]
        except Exception as exc:  # noqa: BLE001
            print(f"  {voz}: ERROR {type(exc).__name__}: {exc}")
            continue
        if not partes:
            print(f"  {voz}: sin audio")
            continue
        audio = np.concatenate(partes) if len(partes) > 1 else partes[0]
        out = destino / f"escena{idx:02d}_{voz}.wav"
        sf.write(out, audio, 24000)
        print(f"  {voz}: {len(audio) / 24000:.1f}s -> {out}")


if __name__ == "__main__":
    main()
