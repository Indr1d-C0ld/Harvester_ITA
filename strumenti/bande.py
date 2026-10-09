"""Stampa le fasce di testo scuro (non blu) di un documento: aiuto per scrivere le ricette."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from documenti import carica
import numpy as np


def bande(nome, disco='d1', x0=0, x1=640, soglia=150, pal=None):
    img = carica(nome, disco, pal)
    rgb = img.pal[img.px].astype(int)
    blu = (rgb[..., 2] > rgb[..., 0] + 25) & (rgb[..., 2] > 90)
    dark = (rgb.mean(2) < soglia) & ~blu
    rows = dark[:, x0:x1].sum(1)
    y = 0
    out = []
    while y < img.px.shape[0]:
        if rows[y] > 1:
            a = y
            while y < img.px.shape[0] and rows[y] > 1:
                y += 1
            xs = np.nonzero(dark[a:y, x0:x1].any(0))[0] + x0
            # parole
            cols = dark[a:y, x0:x1].any(0)
            segs = []
            x = 0
            while x < len(cols):
                if cols[x]:
                    s = x
                    g = 0
                    while x < len(cols) and (cols[x] or g < 6):
                        g = 0 if cols[x] else g + 1
                        x += 1
                    segs.append((x0 + s, x0 + x - g))
                x += 1
            out.append((a, y, int(xs.min()), int(xs.max()), segs))
        y += 1
    return out


if __name__ == '__main__':
    a = sys.argv[1:]
    for b in bande(a[0], *(a[1:2] or ['d1']), *(map(int, a[2:4]) if len(a) > 2 else [])):
        print(b[0], b[1], b[2], b[3], b[4] if len(b[4]) < 12 else str(len(b[4])) + ' parole')
