#!/usr/bin/env python3
"""Controlli di qualità sui cataloghi .po di Harvester.

    qa.py file.po [altri.po ...]

Errori = rompono il gioco o violano una regola fissa; avvisi = da guardare."""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hpo

ACCENTATE = 'àèéìòùÀÈÉÌÒÙ'
AMMESSI = set(chr(c) for c in range(32, 127)) | set(ACCENTATE)
VIETATI = {'"': 'virgolette doppie (usa gli apici \')', '_': 'trattino basso',
           '\n': 'a capo', '\t': 'tabulazione', '{': 'graffa', '}': 'graffa', '\\': 'barra rovescia'}
MAX_IDX = 405      # il motore tronca le righe di DIALOGUE.IDX a 410 byte, virgolette comprese
MAX_TESTO = 400    # oltre, il riquadro più grande (BOX8) trabocca
MAX_NOME = 32
RE_SCELTE = re.compile(r'^(\d)\. ')


def scelte(s):
    """'1. aaa/2. bbb' -> ['1', '2'] (numeri delle opzioni in ordine)."""
    return re.findall(r'(?:^|/)(\d)\. ', s)


def controlla(ctxt, msgid, msgstr, tipo_rsp=''):
    err, avv = [], []
    if not msgstr:
        return err, avv
    for c in msgstr:
        if c in VIETATI:
            err.append(f'carattere vietato: {VIETATI[c]}')
        elif c not in AMMESSI:
            err.append(f'carattere non disponibile nei font: {c!r}')
    if msgstr != msgstr.strip():
        avv.append('spazi all\'inizio o alla fine')
    if '  ' in msgstr.strip().replace('.  ', '. ').replace('?  ', '? ').replace('!  ', '! ').replace(':  ', ': '):
        avv.append('doppio spazio in mezzo alla frase')
    if re.search(r"\bE'", msgstr):
        avv.append("E' al posto di È")
    if re.search(r'\b(perchè|poichè|benchè|nè|sè|affinchè|finchè)\b', msgstr):
        err.append('accento sbagliato (perché, poiché, né, sé...)')
    if re.search(r"\b(qual'è|po')\b", msgstr):
        err.append("qual'è/po' scritti male (qual è, po')")
    le, li = len(msgid), len(msgstr)
    if ctxt.startswith('IDX:'):
        if li > MAX_IDX:
            err.append(f'troppo lunga: {li} > {MAX_IDX} caratteri (il gioco la tronca)')
        elif li > 1.45 * le + 20:
            avv.append(f'molto più lunga dell\'inglese ({li} contro {le})')
    elif ctxt.startswith('TEXT:'):
        if li > MAX_TESTO:
            err.append(f'troppo lunga: {li} > {MAX_TESTO}')
        elif li > 1.5 * le + 20:
            avv.append(f'molto più lunga dell\'inglese ({li} contro {le})')
    elif ctxt == 'NOME':
        if li > MAX_NOME:
            err.append(f'nome troppo lungo: {li} > {MAX_NOME}')
        if '/' in msgstr:
            err.append('barra / in un nome')
    elif ctxt.startswith('RSP:'):
        se, si = scelte(msgid), scelte(msgstr)
        if se and se != si:
            err.append(f'formato scelte diverso: inglese {se}, italiano {si} (serve "1. .../2. ...")')
        if msgstr.count('/') != msgid.count('/'):
            err.append(f'numero di / diverso ({msgid.count("/")} contro {msgstr.count("/")})')
        if '%' in msgid and re.findall(r'%[sd]', msgid) != re.findall(r'%[sd]', msgstr):
            err.append('segnaposto %s/%d diversi')
    # punteggiatura finale
    for p in ('?', '!', '...'):
        if msgid.rstrip().endswith(p) and not msgstr.rstrip().endswith(p) and p != '!':
            avv.append(f'l\'inglese finisce con {p!r}, l\'italiano no')
    if msgid.startswith('...') and not msgstr.startswith('...'):
        avv.append("l'inglese comincia con '...', l'italiano no")
    return err, avv


def controlla_po(path):
    po = hpo.read(path)
    tot_e = tot_a = 0
    vuote = 0
    for (ctxt, msgid), e in po.items():
        if not e.msgstr:
            vuote += 1
            continue
        err, avv = controlla(ctxt, msgid, e.msgstr)
        for x in err:
            print(f'ERRORE {ctxt}: {x}\n   EN: {msgid}\n   IT: {e.msgstr}')
        for x in avv:
            print(f'avviso {ctxt}: {x}\n   EN: {msgid}\n   IT: {e.msgstr}')
        tot_e += len(err)
        tot_a += len(avv)
    print(f'{os.path.basename(path)}: {len(po)} voci, {vuote} vuote, {tot_e} errori, {tot_a} avvisi')
    return tot_e


if __name__ == '__main__':
    n = 0
    for p in sys.argv[1:]:
        n += controlla_po(p)
    sys.exit(1 if n else 0)
