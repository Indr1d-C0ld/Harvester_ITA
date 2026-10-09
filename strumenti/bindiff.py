"""Differenze binarie compatte (formato HDF1) fra un file originale e la sua versione tradotta.

Operazioni, in sequenza:
    0x01 varint(pos) varint(lun)   copia lun byte dall'originale a partire da pos
    0x02 varint(lun) byte...        inserisce byte nuovi
Il tutto compresso con zlib e preceduto da b'HDF1'.
La creazione indicizza l'originale a blocchi allineati e scorre il nuovo a ogni posizione
(come rsync), quindi trova anche il contenuto spostato."""
import zlib

MAGIA = b'HDF1'
BLOCCO = 16


def _varint(n):
    out = bytearray()
    while True:
        b = n & 0x7f
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def _leggi_varint(d, i):
    n = s = 0
    while True:
        b = d[i]
        i += 1
        n |= (b & 0x7f) << s
        s += 7
        if not b & 0x80:
            return n, i


def crea(vecchio, nuovo):
    vecchio, nuovo = bytes(vecchio), bytes(nuovo)
    indice = {}
    for p in range(0, len(vecchio) - BLOCCO + 1, BLOCCO):
        indice.setdefault(vecchio[p:p + BLOCCO], p)
    ops = bytearray()
    lett = bytearray()

    def scarica():
        if lett:
            ops.extend(b'\x02' + _varint(len(lett)) + lett)
            lett.clear()
    j = 0
    n = len(nuovo)
    while j < n:
        p = indice.get(nuovo[j:j + BLOCCO]) if j + BLOCCO <= n else None
        if p is None:
            # prova la stessa posizione nell'originale (modifiche in place)
            if j < len(vecchio) and j + 8 <= n and vecchio[j:j + 8] == nuovo[j:j + 8]:
                p = j
            else:
                lett.append(nuovo[j])
                j += 1
                continue
        # estendi all'indietro dentro i letterali accumulati
        indietro = 0
        while indietro < len(lett) and p - indietro - 1 >= 0 and vecchio[p - indietro - 1] == lett[-1 - indietro]:
            indietro += 1
        if indietro:
            del lett[len(lett) - indietro:]
            p -= indietro
            j -= indietro
        lun = 0
        while j + lun < n and p + lun < len(vecchio) and nuovo[j + lun] == vecchio[p + lun]:
            lun += 1
        scarica()
        ops.extend(b'\x01' + _varint(p) + _varint(lun))
        j += lun
    scarica()
    return MAGIA + zlib.compress(bytes(ops), 9)


def applica(vecchio, diff):
    if diff[:4] != MAGIA:
        raise ValueError('differenza non valida')
    d = zlib.decompress(diff[4:])
    out = bytearray()
    i = 0
    while i < len(d):
        op = d[i]
        i += 1
        if op == 1:
            p, i = _leggi_varint(d, i)
            lun, i = _leggi_varint(d, i)
            out += vecchio[p:p + lun]
        elif op == 2:
            lun, i = _leggi_varint(d, i)
            out += d[i:i + lun]
            i += lun
        else:
            raise ValueError('operazione sconosciuta')
    return bytes(out)
