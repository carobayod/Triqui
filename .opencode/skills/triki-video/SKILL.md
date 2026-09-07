---
name: triki-video
description: Regenera o itera sobre el video explicativo del libro del Triki (narración Kokoro voz Dora o Piper, slides WeasyPrint→PNG, clips Ken Burns o Manim, ensamblado ffmpeg por lotes). Use when the user says "video", "video del triki", "narración", "voz", "kokoro", "piper", "manim", "slides", "escenas", "rehacer/regenerar el video".
---

# Video explicativo del Triki (v2)

## Fuente y flujo

```
manual/Aprendiendo_a_programar_jugando_con_el_Triki.md
   + manual/Video/slide_content.py (38 escenas curadas: DATA[idx] = title/section/points/narr)
   └─> make_video.py  ─>  work/  ─>  Video_Explicativo_Triki_v2.mp4
```

1. `build_scenes()` parsea el .md en SECTIONS_N escenas.
2. `narrate_text()`: usa `narr` de slide_content.py; si no, título + primeras frases; `expand_numbers()` convierte números a palabras (Dora los lee bien).
3. TTS: Kokoro (`.venv312/bin/python synth_kokoro.py <texto> <out.wav>`, voz ef_dora, KPipeline lang_code="e", wav 24 kHz mono). Alternativa: `--voice piper` (`.venv/bin/piper`, modelo es_ES-sharvard-medium).
4. Slides: HTML (título + puntos + progreso NN/38) → WeasyPrint PDF (page 203.2x114.3mm ≈16:9, `slide_v2.css`) → `pdftoppm` PNG 240 dpi.
5. Clips: si existe `work/clips/manim_s<N>.mp4` se usa el clip de Manim; si no, **Ken Burns** (ffmpeg `scale=2000*zoompan` 1920x1080@30, CRF 19) sobre el PNG del slide.
6. Ensamblado: pista de narración con sox (pad + mix 1ch 24k norm); **concat por lotes BATCH=8** con fades 0.5 s de escena, `setsar=1`; último pase mezcla vídeo+audio y fades globales → MP4 1080p30 h264/yuv420p, aac mono, `-movflags +faststart`.

## Comandos

- Regenerar todo (incremental): `python3 manual/Video/make_video.py` (cualquier cwd; rutas absolutas).
- Iterar pocas escenas: `python3 manual/Video/make_video.py --first 3`
- Forzar re-síntesis/rebuild de audio+slides+clips: `--rebuild`
- Voz alternativa: `--voice piper`
- Clips Manim (sustituyen Ken Burns de ciertas escenas, hoy 18/20/21):
  ```
  cd manual/Video && .venv/bin/manim -qh manim_scenes.py <Escena>
  cp media/images/.../<Escena>.mp4 work/clips/manim_s<N>.mp4
  ```

## Curación de contenido (si cambia el libro)

- Editar `manual/Video/slide_content.py` (DATA[idx], SECTIONS_N).
- **Acoplamiento**: el video se genera desde el mismo .md; si reorganizamos capítulos hay que re-mapear índices/títulos para que las escenas sigan correspondiendo.
- Regla del proyecto: tras reorganizar el libro, AJUSTAR slide_content.py pero NO regenerar el video salvo petición explícita.

## Verificación

- `ffprobe Video_Explicativo_Triki_v2.mp4`: 1920x1080, 30 fps, duración ~8:57, codec h264 yuv420p, audio aac mono, tamaño ~98 MB.
- Revisar arranques: `ffplay` o copiar a Windows (`/mnt/c/Users/57350/OneDrive/Desktop/Triqui_Libro/`) para revisión humana.
- Comprobar que los offests de narración vs escenas no se desalinean (una escena de 7.4 s con narración larga es señal de curación pobre).

## Gotchas

- El docstring del script aún dice "xfade", pero el código REAL usa concat por lotes (xfade histórico daba OOM). No "corregir" a xfade.
- `setsar=1` imprescindible (evita SAR 4:3 erróneo en el concat).
- Kokoro por escena es lento: usar `--first N` para probar. `.venv312` es Python 3.12; `.venv` trae manim + piper.
- No usar `pkill -f` con patrón que coincida con el propio comando (corchetes `'[m]ake_video.py'`).
- No commitear `work/`, `media/` ni binarios grandes.