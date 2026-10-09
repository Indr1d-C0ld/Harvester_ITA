#!/bin/bash
# Collaudo automatico di Harvester in DOSBox su un display virtuale (Xvfb).
#   collaudo.sh avvia <cartella_prova> <iso1> <iso2> <iso3>
#   collaudo.sh foto <file.png>
#   collaudo.sh tasto <tasti xdotool...>
#   collaudo.sh clic <x> <y> [1|3]      (coordinate del gioco 640x480)
#   collaudo.sh ferma
DISP=${DISP:-:99}
STATO=${STATO:-${TMPDIR:-/tmp}/harv_collaudo}
mkdir -p "$STATO"
export DISPLAY=$DISP
finestra() { xdotool search --class dosbox 2>/dev/null | tail -1; }
case "$1" in
  avvia)
    if ! [ -f "$STATO/xvfb.pid" ] || ! kill -0 "$(cat "$STATO/xvfb.pid")" 2>/dev/null; then
      Xvfb "$DISP" -screen 0 1024x768x24 >/dev/null 2>&1 & echo $! > "$STATO/xvfb.pid"; sleep 1
    fi
    sed -e "s#PROVA_DIR#$2#" -e "s#ISO1#$3#" -e "s#ISO2#$4#" -e "s#ISO3#$5#" \
        "$(dirname "$0")/../prova/dosbox-prova.conf" > "$STATO/dosbox.conf"
    # senza CD: "collaudo.sh avvia <cartella> -" non monta nessuna immagine
    [ "$3" = "-" ] && sed -i '/^imgmount/d' "$STATO/dosbox.conf"
    SDL_AUDIODRIVER=${SDL_AUDIODRIVER:-dummy} dosbox -conf "$STATO/dosbox.conf" >"$STATO/dosbox.log" 2>&1 &
    echo $! > "$STATO/dosbox.pid"
    sleep 2; w=$(finestra); [ -n "$w" ] && xdotool windowmove "$w" 0 0
    echo "dosbox pid $(cat "$STATO/dosbox.pid") finestra $w" ;;
  foto)
    w=$(finestra); import -window "${w:-root}" "$2" 2>/dev/null; echo "$2" ;;
  tasto)
    shift; w=$(finestra); xdotool windowfocus --sync "$w" 2>/dev/null; xdotool key --delay 120 "$@" ;;
  clic)
    w=$(finestra); xdotool mousemove --window "$w" "$2" "$3"; sleep 0.2; xdotool mousedown "${4:-1}"; sleep ${PRESS:-0.3}; xdotool mouseup "${4:-1}" ;;
  muovi)
    w=$(finestra); xdotool mousemove --window "$w" "$2" "$3" ;;
  ferma)
    [ -f "$STATO/dosbox.pid" ] && kill "$(cat "$STATO/dosbox.pid")" 2>/dev/null; rm -f "$STATO/dosbox.pid"; echo fermato ;;
esac
