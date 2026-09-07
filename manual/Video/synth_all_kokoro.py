#!/usr/bin/env python3
"""Sintetiza la narración de todas las escenas con Kokoro (una sola carga de modelo).
Escribe work/audio/s{i}.wav (24 kHz mono) usando narración de make_video.
"""
import sys
from pathlib import Path

ROOT = Path("/home/carobayo/proyectos/Triqui")
sys.path.insert(0, str(ROOT / "manual" / "Video"))
import numpy as np
import soundfile as sf
from kokoro import KPipeline

from make_video import build_scenes, narrate_text, WORK, prepare_scene

scenes = build_scenes()
pipe = KPipeline(lang_code="e")
speed = 1.0
for i, s in enumerate(scenes):
    out = WORK / "audio" / f"s{i}.wav"
    if out.exists():
        print(f"[{i:02d}] ya existe, salto")
        continue
    text = narrate_text(s, i)
    audio = []
    for r in pipe(text, voice="ef_dora", speed=speed):
        audio.append(r.audio)
    full = np.concatenate(audio) if len(audio) > 1 else audio[0]
    sf.write(out, full, 24000)
    print(f"[{i:02d}] ok dur={len(full) / 24000:.1f}s :: {text[:60]}")
print("FIN")