#!/usr/bin/env bash
# Genera footage real del Triki para el video, sin capturar la pantalla.
#
# Por que no x11grab: en WSLg la captura de pantalla sale negra, tanto con
# ffmpeg -f x11grab como con java.awt.Robot.createScreenCapture. Se verificó.
#
# La via que si funciona: se abre el juego dentro de la JVM, se le hacen clic
# a los botones con doClick() (el juego responde por ActionListener, igual que
# con un clic real) y despues se pide al componente que se pinte sobre un
# BufferedImage. El resultado es una partida de verdad, nitida y reproducible.
#
#   ./render_juego.sh 5     genera partida5.mp4 con tablero 5x5
set -euo pipefail
cd "$(dirname "$0")/../.."

T="${1:-5}"
OUT="$PWD/manual/Video/work/clips"
FRAMES="/tmp/opencode/grab/render_$T"
mkdir -p "$OUT" "$FRAMES"

echo "== 1/3 compilando el juego =="
mvn -q -DskipTests package

echo "== 2/3 renderizando la partida ${T}x${T} =="
javac -cp target/classes -d /tmp/opencode manual/Video/RenderTriki.java
java -cp "target/classes:/tmp/opencode" RenderTriki "$T" 2>&1 | tail -3

echo "== 3/3 armando el clip =="
N=$(ls "$FRAMES"/f*.png 2>/dev/null | wc -l)
[ "$N" -lt 2 ] && { echo "ERROR: no se generaron frames"; exit 1; }

LST=$(mktemp)
for f in $(ls "$FRAMES"/f*.png | sort); do
  printf "file '%s'\nduration 1.3\n" "$f" >> "$LST"
done
printf "file '%s'\nduration 1.3\n" "$(ls "$FRAMES"/f*.png | sort | tail -1)" >> "$LST"

ffmpeg -v error -y -f concat -safe 0 -i "$LST" \
  -vf "scale=1000:1000:flags=lanczos,fps=30,format=yuv420p" \
  -c:v libx264 -preset veryfast -crf 19 "$OUT/partida$T.mp4"
rm -f "$LST"

echo "OK -> $OUT/partida$T.mp4  ($(ls "$FRAMES"/f*.png | wc -l) frames)"
echo
echo "Para usarlo en el video, copialo como game_<letra>.mp4 y anadelo"
echo "al diccionario GAMEPLAY de manual/Video/make_video.py."