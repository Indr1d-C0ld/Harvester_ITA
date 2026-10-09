"""Filmati FST di Harvester (FutureVision): lettura, decodifica, codifica.

Intestazione (32 byte): '2TSF', larghezza, altezza, ?, fotogrammi, fps,
frequenza audio, bit per campione. Poi una tabella di 6 byte per fotogramma
(u32 byte del video, u16 byte dell'audio) e i fotogrammi: video poi audio.

Video: u16 n (bit della mappa), mappa di n bit (letti dal più significativo),
dati. Il primo bit della mappa dice se segue una tavolozza (768 byte, 0-63).
Poi un bit per blocco 4x4, riga per riga: 0 = invariato; 1 = cambiato, e il bit seguente
sceglie fra blocco a due colori (c0, c1, maschera u16: bit 15 = pixel in alto
a sinistra, 1 = c1) e blocco grezzo (16 byte).
"""
import struct
import numpy as np


class FST:
    def __init__(self, path):
        self.d = d = open(path, 'rb').read()
        (self.magia, self.w, self.h, self.ignoto, self.n, self.fps,
         self.freq, self.bit) = struct.unpack_from('<4s7I', d)
        assert self.magia == b'2TSF', path
        self.tab = [struct.unpack_from('<IH', d, 0x20 + i * 6) for i in range(self.n)]
        self.pos = []
        p = 0x20 + self.n * 6
        for v, a in self.tab:
            self.pos.append(p)
            p += v + a

    def video(self, i):
        p = self.pos[i]
        return self.d[p:p + self.tab[i][0]]

    def audio(self, i):
        p = self.pos[i] + self.tab[i][0]
        return self.d[p:p + self.tab[i][1]]


def leggi_fotogramma(v, nblocchi=4000):
    """Analizza un fotogramma: (tavolozza o None, lista di blocchi).
    Ogni blocco è None (invariato), ('2', c0, c1, maschera) o ('g', 16 byte).
    Il numero di blocchi è quello che la mappa descrive."""
    n = struct.unpack_from('<H', v)[0]
    nb = n // 8 + 1
    mappa = v[2:2 + nb]
    dati = 2 + nb
    bit = 0

    def b():
        nonlocal bit
        x = (mappa[bit >> 3] >> (7 - (bit & 7))) & 1
        bit += 1
        return x
    tav = None
    if b():
        tav = v[dati:dati + 768]
        dati += 768
    blocchi = []
    while bit < n and len(blocchi) < nblocchi:
        if not b():
            blocchi.append(None)
        elif b():
            c0, c1, m = v[dati], v[dati + 1], struct.unpack_from('<H', v, dati + 2)[0]
            blocchi.append(('2', c0, c1, m))
            dati += 4
        else:
            blocchi.append(('g', v[dati:dati + 16]))
            dati += 16
    return tav, blocchi, n, dati


MASCHERA_BIT = np.array([1 << (15 - k) for k in range(16)], dtype=np.uint16).reshape(4, 4)


def decodifica(f, schermo=None, tavolozza=None, da=0, a=None):
    """Genera (indice, schermo, tavolozza) per i fotogrammi di f (solo 320x200)."""
    bw, bh = f.w // 4, f.h // 4 - 1   # l'ultima fila di blocchi non si disegna
    if schermo is None:
        schermo = np.zeros((f.h, f.w), np.uint8)
        tavolozza = np.zeros((256, 3), np.uint8)
    for i in range(da, f.n if a is None else a):
        tav, blocchi, _, _ = leggi_fotogramma(f.video(i), bw * bh)
        if tav is not None:
            tavolozza = np.frombuffer(tav, np.uint8).reshape(256, 3).copy()
        for k, bl in enumerate(blocchi[:bw * bh]):
            if bl is None:
                continue
            y, x = (k // bw) * 4, (k % bw) * 4
            if bl[0] == '2':
                _, c0, c1, m = bl
                schermo[y:y + 4, x:x + 4] = np.where((m & MASCHERA_BIT) != 0, c1, c0)
            else:
                schermo[y:y + 4, x:x + 4] = np.frombuffer(bl[1], np.uint8).reshape(4, 4)
        yield i, schermo, tavolozza


def rgb(schermo, tavolozza):
    t = (tavolozza.astype(np.uint16) * 255 // 63).astype(np.uint8)
    return t[schermo]
