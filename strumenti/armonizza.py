#!/usr/bin/env python3
"""Correzioni puntuali di armonizzazione fra i lotti (decise dal coordinatore).
Ogni voce: (catalogo, msgctxt, msgid o None, vecchio, nuovo). Idempotente."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hpo
T = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'traduzione')

CORR = [
    ('dialoghi', 'IDX:695', None, 'direttore delle iscrizioni', 'direttore delle ammissioni'),
    ('dialoghi', 'IDX:725', None, 'al terzo piano', 'al terzo livello'),
    ('dialoghi', 'IDX:3914', None, 'Il secondo piano', 'Il secondo livello'),
    ('dialoghi', 'IDX:3914', None, 'chiave del secondo piano', 'chiave del secondo livello'),
    ('dialoghi', 'IDX:6937', None, 'questo piano', 'questo livello'),
    ('dialoghi', 'IDX:6961', None, 'secondo piano', 'secondo livello'),
    ('dialoghi', 'IDX:7567', None, 'al terzo piano', 'al terzo livello'),
    ('dialoghi', 'IDX:7576', None, 'al terzo piano', 'al terzo livello'),
    ('dialoghi', 'IDX:7607', None, 'al terzo piano', 'al terzo livello'),
    ('dialoghi', 'IDX:7611', None, 'chiave del terzo piano', 'chiave del terzo livello'),
    ('dialoghi', 'IDX:14160', None, 'Per mille rospi in calore!', 'Rospi in fregola!'),
    ('dialoghi', 'IDX:14984', None, "Sergente d'Armi", "sergente d'armi"),
    ('dialoghi', 'IDX:1580', None, 'la pezza di stoffa', 'il rotolo di stoffa'),
    ('dialoghi', 'IDX:9238', None, 'una pezza di stoffa costosa', 'un rotolo di stoffa costosa'),
    ('dialoghi', 'IDX:16978', None, 'la sua preziosa insegna da barbiere', 'il suo prezioso palo da barbiere'),
    ('dialoghi', 'IDX:16990', None, "ruba l'insegna del barbiere", 'ruba il palo da barbiere'),
    ('testi', 'TEXT:MBLMGLUE_STEXT', None, 'Astro-Glue', 'Astro Glue'),
    ('testi', 'TEXT:MBLMGLUE_LTEXT', None, 'Astro-Glue', 'Astro Glue'),
    ('nomi', 'NOME', 'barber pole', 'insegna da barbiere', 'palo da barbiere'),
    ('nomi', 'NOME', "barber's pole", 'insegna da barbiere', 'palo da barbiere'),
    ('nomi', 'NOME', 'evidence', 'stanza delle prove', 'stanza dei reperti'),
    ('nomi', 'NOME', 'Grand Muckey Muck', 'Gran Mogol', 'Gran Papavero'),
]


def main():
    cats = {}
    n = 0
    for cat, ctx, mid, a, b in CORR:
        if cat not in cats:
            cats[cat] = hpo.read(os.path.join(T, cat + '.po'))
        trov = [e for (c, m), e in cats[cat].items() if c == ctx and (mid is None or m == mid)]
        if not trov:
            print('voce non trovata', cat, ctx, mid)
            continue
        for e in trov:
            if a in e.msgstr:
                e.msgstr = e.msgstr.replace(a, b)
                n += 1
            elif b not in e.msgstr:
                print('testo non trovato', cat, ctx, mid, repr(a))
    for cat, po in cats.items():
        hpo.write(os.path.join(T, cat + '.po'), list(po.values()), cat + '.po')
    print(n, 'correzioni applicate')


if __name__ == '__main__':
    main()
