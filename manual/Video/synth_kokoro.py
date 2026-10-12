#!/usr/bin/env python3
"""Sintetiza texto con Kokoro (voz Dora, español) -> wav 24kHz mono.

Dos modos:

  python synth_kokoro.py <texto> <salida.wav> [speed]     una sola escena
  python synth_kokoro.py --lote <manifiesto.json>          muchas escenas

El modo por lote existe por una razon concreta: KPipeline carga el modelo de
82M parametros cada vez que se construye. Con el modo de una escena, generar
las 41 escenas del video recargaba el modelo 41 veces y tardaba casi una hora;
cargandolo una sola vez, el mismo trabajo baja a unos minutos. La sintesis por
escena es identica: solo se cambia donde se carga el modelo.

El manifiesto es una lista de {"texto": ..., "salida": ..., "speed": ...}.
"""
import json
import sys
import time

import numpy as np
import soundfile as sf
from kokoro import KPipeline

VOZ = "ef_dora"


def sintetizar(pipe, texto, salida, speed=1.0):
    audio = [r.audio for r in pipe(texto, voice=VOZ, speed=speed)]
    if not audio:
        raise SystemExit(f"sin audio para: {texto[:60]}...")
    full = np.concatenate(audio) if len(audio) > 1 else audio[0]
    sf.write(salida, full, 24000)
    return len(full) / 24000


def main():
    if sys.argv[1] == "--lote":
        with open(sys.argv[2], encoding="utf-8") as fh:
            trabajo = json.load(fh)
        t0 = time.time()
        pipe = KPipeline(lang_code="e")
        print(f"  modelo cargado en {time.time() - t0:.1f}s", flush=True)
        for n, item in enumerate(trabajo, 1):
            t = time.time()
            dur = sintetizar(pipe, item["texto"], item["salida"],
                             item.get("speed", 1.0))
            print(f"  [{n}/{len(trabajo)}] {dur:5.1f}s en {time.time() - t:4.1f}s "
                  f"-> {item['salida'].rsplit('/', 1)[-1]}", flush=True)
        return

    texto, salida = sys.argv[1], sys.argv[2]
    speed = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    sintetizar(KPipeline(lang_code="e"), texto, salida, speed)


if __name__ == "__main__":
    main()
