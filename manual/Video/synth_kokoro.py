#!/usr/bin/env python3
"""Sintetiza texto con Kokoro (voz Dora, español) -> wav 24kHz.
Uso: python synth_kokoro.py <texto> <salida.wav> [speed]
"""
import sys
import numpy as np
import soundfile as sf
from kokoro import KPipeline


def main():
    text = sys.argv[1]
    out = sys.argv[2]
    speed = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    pipe = KPipeline(lang_code="e")
    audio = []
    for r in pipe(text, voice="ef_dora", speed=speed):
        audio.append(r.audio)
    if not audio:
        sys.exit("sin audio")
    full = np.concatenate(audio) if len(audio) > 1 else audio[0]
    sf.write(out, full, 24000)


if __name__ == "__main__":
    main()