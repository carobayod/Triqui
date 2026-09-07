---
description: Regenera el video explicativo del Triki (voz Kokoro Dora, 38 escenas) desde la fuente del libro.
agent: build
---

Regenera el video siguiendo la skill `triki-video`:

1. Carga la skill `triki-video`.
2. Si el .md cambió de estructura, re-mapear antes `manual/Video/slide_content.py` (no regenerar con escenas desalineadas).
3. Ejecuta: `python3 /home/carobayo/proyectos/Triqui/manual/Video/make_video.py [--rebuild]`
   - Sin `--rebuild` = incremental (solo lo que falte); con `--rebuild` re-sintetiza audio/slides/clips.
4. Verifica con `ffprobe` (1920x1080p30, h264 yuv420p, aac mono, ~8:57) y tamaño.
5. Opcional: copiar a `/mnt/c/Users/57350/OneDrive/Desktop/Triqui_Libro/`.