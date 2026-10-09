#!/bin/bash
# Scarica i font liberi usati per ridisegnare la grafica e impaginare il manuale
# (Google Fonts, licenze OFL e Apache 2.0). I font URW (Nimbus, URW Gothic, Bookman)
# vengono dal pacchetto di sistema fonts-urw-base35.
cd "$(dirname "$0")" && mkdir -p font && cd font || exit 1
G=https://github.com/google/fonts/raw/main
for u in apache/specialelite/SpecialElite-Regular.ttf apache/permanentmarker/PermanentMarker-Regular.ttf \
         apache/homemadeapple/HomemadeApple-Regular.ttf ofl/reeniebeanie/ReenieBeanie.ttf \
         "ofl/caveat/Caveat%5Bwght%5D.ttf" ofl/uncialantiqua/UncialAntiqua-Regular.ttf \
         ofl/sortsmillgoudy/SortsMillGoudy-Regular.ttf ofl/sortsmillgoudy/SortsMillGoudy-Italic.ttf \
         ofl/goudybookletter1911/GoudyBookletter1911.ttf ofl/fondamento/Fondamento-Italic.ttf \
         ofl/cardo/Cardo-Bold.ttf; do
    f=$(basename "$u" | sed 's/%5B/[/;s/%5D/]/')
    [ -f "$f" ] || curl -sfL -o "$f" "$G/$u" && echo "ok $f"
done
