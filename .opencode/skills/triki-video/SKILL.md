---
name: triki-video
description: Regenera o itera sobre el video explicativo del libro del Triki (narración Kokoro voz Dora, slides WeasyPrint a PNG con sistema de imágenes, clips Ken Burns o Manim, ensamblado ffmpeg por lotes). Use when the user says "video", "video del triki", "narración", "voz", "kokoro", "manim", "slides", "escenas", "diapositiva", "rehacer/regenerar el video".
---

# Video explicativo del Triki (v3)

## Fuente y flujo

```
manual/Aprendiendo_a_programar_jugando_con_el_Triki.md
   + manual/Video/slide_content.py (41 escenas curadas)
   └─> make_video.py ─> work/ ─> Video_Explicativo_Triki_v2.mp4
```

1. `build_scenes()` parsea el .md en 41 escenas (`SECTIONS_N = 41`).
2. `narrate_text()`: usa `narr` de `slide_content.py` si existe; si no, título +
   primeras frases del markdown. Filtra el repaso y el reto de código (viven dentro
   de `paras` porque así están en el markdown) y **no** anuncia "Capítulo N:" al
   principio.
3. `normalize_for_tts()`: deja el texto legible por espeak-ng antes del TTS.
4. `expand_numbers()`: números a palabras (Kokoro en español no los lee bien).
5. TTS: **Kokoro** voz `ef_dora`, wav 24 kHz mono, vía `.venv312/bin/python
   synth_kokoro.py`. El script tiene modo `--lote` (manifiesto JSON) que carga el
   modelo de 82M **una sola vez** para las 41 escenas.
6. Slides: HTML → WeasyPrint PDF (página 203.2×114.3 mm ≈ 16:9, `slide_v2.css`) →
   `pdftoppm` PNG 240 dpi.
7. Clips: si existe `work/clips/manim_s<N>.mp4` se usa; si no, **Ken Burns**.
8. Ensamblado: concat por lotes con fades de 0.5 s.

## Comandos

```bash
cd manual/Video
python3 make_video.py --voice kokoro          # completo
python3 make_video.py --voice kokoro --first 5   # probar sin esperar 40 min
python3 check_slides.py 36 37 38 39 40        # verificar slides por píxeles
python3 muestra_escena.py 40 ef_dora em_alex  # comparar dos voces
```

Motores de voz: `--voice kokoro` (por defecto), `--voice edge`, `--voice piper`.

## Verificación

- `ffprobe Video_Explicativo_Triki_v2.mp4` → 1920×1080, 30 fps, ~9:58, h264
  yuv420p, aac mono 24 kHz, ~52 MB.
- **Decodificación completa antes de publicar**:
  ```
  ffmpeg -v error -i Video_Explicativo_Triki_v2.mp4 -f null -
  ```
  Log vacío = íntegro. (ffmpeg SÍ abre mp4; solo falla con PDF.)
- Audio presente al inicio, medio y final: `volumedetect` a los 30 s, 300 s y 570 s.
- **md5 del origen y la copia deben coincidir.** Una copia hecha antes de que
  termine el ensamblado deja un archivo truncado que `ffprobe` reporta como
  completo si tiene `-movflags +faststart` (el moov va al principio). Ese fue el
  corte de audio que reportó el usuario.

## Entregables

Copiar **a la raíz** de `/mnt/c/Users/57350/OneDrive/Desktop/Triqui_Libro/`
(nombre en español, con la voz incluida). Ese Desktop es solo una copia de
entrega: **el usuario no tiene acceso gráfico a WSL**, así que nunca hay que
intentar leer o comparar desde ahí. Comparar siempre dentro de
`~/proyectos/Triqui`.

## Animaciones (Manim)

Clases en `manual/Video/manim_scenes.py`: `TableroScene`, `MinimaxScene`,
`CapasScene`, `SwingScene`, `LayoutScene`.

| Clip | Escena | Contenido |
|---|---|---|
| `manim_s03` | 3 | una jugada en el tablero |
| `manim_s18` | 18 | el mapa del código, tres capas |
| `manim_s20` | 20 | componentes Swing: JFrame, botonera, JButton |
| `manim_s21` | 21 | GridLayout |
| `manim_s25` | 25 | **el árbol de minimax** (va en el capítulo de la IA, no en Swing) |

Renderizar: `.venv/bin/python -m manim -qh --format mp4 -r 1920,1080 -o <salida>
manim_scenes.py <Clase>`.

## Curación de contenido

- Editar `manual/Video/slide_content.py` (`DATA[idx]`, `SECTIONS_N`).
- **Acoplamiento**: el video se genera desde el mismo .md; si se reorganizan
  capítulos hay que re-mapear índices y títulos.
- Cada entrada puede traer un `extra` con `diagrama` (ruta PNG) o `codigo`
  (bloque de texto) + `glosa`. Es lo que usan las escenas 36-40 del apéndice.

## Gotchas

- **Lotes de Kokoro**: sin `synth_kokoro.py --lote` son 41 cargas del modelo de
  82M (una por escena) y el build tarda casi una hora. El modo por lote lo baja a
  unos minutos.
- **edge-tts usa el endpoint interno de Edge** (`speech.platform.bing.com`), con
  un token antifraude `Sec-MS-GEC`. Microsoft puede romperlo: devuelve 403 a todo
  el mundo a la vez. Verificado 2026-10-11 con la 7.2.8 (la última). Si vuelve a
  fallar, no reintentar: usar Kokoro. Es la razón por la que el video usa Kokoro.
- **Kokoro en español cae a espeak-ng**, que lee mal las siglas (`JVM` → "jota-uve-
  eme") y **lee las llaves y paréntesis en voz alta**. Por eso `normalize_for_tts()`.
- `all()` con un generador cortaba el chequeo en el primer `False` y solo revisaba
  una escena. Evaluar la lista entera y resumir después.
- El docstring de `make_video.py` aún dice "xfade", pero el código REAL usa concat
  por lotes (xfade histórico daba OOM). No "corregir" a xfade.
- `setsar=1` imprescindible (evita SAR 4:3 erróneo en el concat).
- No usar `pkill -f` con patrón que coincida con el propio comando (usar `'[m]ake_video.py'`).
- **No copiar el video al Desktop hasta que el ensamblado termine.** Verificar con
  md5.
