"""Costruisce SOTTOTIT.ITA, il file dei sottotitoli dei filmati letto dal codice
aggiunto a HARVEST.EXE (tools/sottotitoli_fmv.S, dove è descritto il formato).

Le righe vanno a capo e si centrano qui, misurate con TEXTFONT.CFT, il font
dei testi del gioco: il codice nell'eseguibile si limita a disegnarle."""
import struct, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cft

SPAZIO = 4            # avanzamento dello spazio, in pixel
LARGHEZZA = 308       # righe al massimo così larghe (schermo di 320)
Y_UNA = 178           # fascia libera: righe 168-199
Y_DUE = (171, 185)


def larghezza(font, s):
    w = 0
    for c in s.encode('latin-1'):
        if c in (32, 95):
            w += SPAZIO
        elif not font.width[c]:
            raise ValueError(f'carattere {chr(c)!r} assente dal font in: {s}')
        else:
            w += font.width[c]
    return w


def a_capo(font, testo):
    """Una o due righe; con due, il taglio che le rende più simili."""
    testo = ' '.join(testo.split())
    if '|' in testo:                      # a capo deciso a mano
        righe = [r.strip() for r in testo.split('|')]
    elif larghezza(font, testo) <= LARGHEZZA:
        righe = [testo]
    else:
        parole = testo.split(' ')
        migliori = []
        for k in range(1, len(parole)):
            a, b = ' '.join(parole[:k]), ' '.join(parole[k:])
            la, lb = larghezza(font, a), larghezza(font, b)
            if la <= LARGHEZZA and lb <= LARGHEZZA:
                migliori.append((abs(la - lb), a, b))
        if not migliori:
            raise ValueError(f'sottotitolo troppo lungo per due righe: {testo}')
        righe = list(min(migliori)[1:])
    if len(righe) > 2:
        raise ValueError(f'più di due righe: {testo}')
    for r in righe:
        if larghezza(font, r) > LARGHEZZA:
            raise ValueError(f'riga troppo larga: {r}')
    return righe


def costruisci(filmati, font):
    """filmati: {nome FST: [(primo fotogramma, fotogramma dopo l'ultimo, testo)]}."""
    nomi = sorted(filmati)
    for n in nomi:
        if len(n) > 12 or n != n.upper():
            raise ValueError(f'nome di filmato non valido: {n}')
    testa = 16 + 20 * len(nomi)
    cue = bytearray()
    testi = bytearray()
    indice = bytearray()
    voci_cue = []
    for n in nomi:
        voci = sorted(filmati[n])
        for (a, b, _), (c, _, _) in zip(voci, voci[1:]):
            if b > c:
                raise ValueError(f'{n}: sottotitoli sovrapposti ai fotogrammi {c}-{b}')
        voci_cue.append((n, len(cue), len(voci)))
        for da, a, testo in voci:
            if not 0 <= da < a <= 0xffff:
                raise ValueError(f'{n}: fotogrammi non validi {da}-{a}')
            righe = a_capo(font, testo)
            ys = [Y_UNA] if len(righe) == 1 else list(Y_DUE)
            pos = len(testi)
            for r, y in zip(righe, ys):
                x = (320 - larghezza(font, r)) // 2
                testi += struct.pack('<HH', x, y) + r.encode('latin-1') + b'\0'
            testi += b'\xff\xff'
            cue += struct.pack('<HHI', da, a, pos)    # posizione del testo corretta sotto
    base_cue = testa
    base_testi = testa + len(cue)
    for i in range(0, len(cue), 8):
        da, a, pos = struct.unpack_from('<HHI', cue, i)
        struct.pack_into('<HHI', cue, i, da, a, base_testi + pos)
    for n, off, k in voci_cue:
        indice += n.encode('ascii').ljust(12, b'\0') + struct.pack('<II', base_cue + off, k)
    dim = testa + len(cue) + len(testi)
    return b'SOTT' + struct.pack('<IIHH', dim, len(nomi), SPAZIO, 0) + bytes(indice) + bytes(cue) + bytes(testi)


if __name__ == '__main__':
    font = cft.CFT.load(sys.argv[1])
    for t in sys.argv[2:]:
        print(a_capo(font, t), [larghezza(font, r) for r in a_capo(font, t)])
