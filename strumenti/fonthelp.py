"""Ricava il font bitmap delle schermate di aiuto dalle immagini originali,
segmentando righe di cui si conosce il testo."""
import numpy as np


def segmenta(t, y0, y1, x0=166, x1=640):
    cols = t[y0:y1, x0:x1].any(0)
    runs = []
    x = 0
    n = len(cols)
    while x < n:
        if cols[x]:
            a = x
            while x < n and cols[x]:
                x += 1
            runs.append((x0 + a, x0 + x))
        x += 1
    return runs


def estrai(px, testo_righe, bande, indici=(15, 31), x0=166):
    """Restituisce {carattere: [maschere]} e le misure (spazio fra parole, baseline)."""
    t = np.isin(px, indici)
    glifi = {}
    spazi = []
    for (y0, y1, _), testo in zip(bande, testo_righe):
        runs = segmenta(t, y0 - 1, y1 + 1, x0)
        car = [c for c in testo if c != ' ']
        if len(runs) != len(car):
            print('riga non allineata', y0, len(runs), len(car), testo)
            continue
        k = 0
        for i, c in enumerate(testo):
            if c == ' ':
                continue
            a, b = runs[k]
            if k and testo[i - 1] == ' ':
                spazi.append(a - runs[k - 1][1])
            g = t[y0 - 1:y0 + 11, a:b]
            glifi.setdefault(c, []).append(g.copy())
            k += 1
    return glifi, spazi
