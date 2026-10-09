"""PNG con griglia di coordinate (ogni 20 px, etichette ogni 40) per leggere le posizioni."""
import sys
from PIL import Image, ImageDraw
src, dst = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = map(int, sys.argv[3:7]) if len(sys.argv) > 6 else (0, 0, 640, 480)
sc = int(sys.argv[7]) if len(sys.argv) > 7 else 2
im = Image.open(src).convert('RGB').crop((x0, y0, x1, y1))
im = im.resize((im.width * sc, im.height * sc), Image.NEAREST)
d = ImageDraw.Draw(im)
for x in range((x0 // 20 + 1) * 20, x1, 20):
    X = (x - x0) * sc
    d.line([(X, 0), (X, im.height)], fill=(0, 255, 0) if x % 40 == 0 else (0, 120, 0), width=1)
    if x % 40 == 0:
        d.text((X + 2, 2), str(x), fill=(255, 0, 255))
for y in range((y0 // 20 + 1) * 20, y1, 20):
    Y = (y - y0) * sc
    d.line([(0, Y), (im.width, Y)], fill=(0, 255, 0) if y % 40 == 0 else (0, 120, 0), width=1)
    if y % 40 == 0:
        d.text((2, Y + 2), str(y), fill=(255, 0, 255))
im.save(dst)
