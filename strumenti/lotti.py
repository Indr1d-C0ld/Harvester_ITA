#!/usr/bin/env python3
"""Prepara i lotti di traduzione in traduzione/lotti/ (una volta sola) e li
riunisce nei cataloghi principali.

    lotti.py prepara     crea lotto_NN.po (dialoghi+scelte per conversazione),
                         testi_A.po, testi_B.po, nomi.po
    lotti.py unisci      riporta le traduzioni dei lotti in traduzione/*.po
"""
import os, sys, json, glob, collections
QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)
sys.path.insert(0, QUI)
import hpo

TRAD = os.path.join(RADICE, 'traduzione')
LOTTI = os.path.join(TRAD, 'lotti')
MOD = os.path.join(TRAD, 'modelli')
PAROLE_LOTTO = 3400

NOMI_PARL = {
    'PC': 'STEVE (protagonista)', 'MOM': 'la mamma di Steve', 'DAD': 'il papà di Steve',
    'HANK': 'Hank, fratellino di Steve', 'DWAYNE': 'lo sceriffo Dwayne',
    'STEPHANIE': 'Stephanie, fidanzata di Steve', 'MR_POTTS': 'il signor Pottsdam (padre di Stephanie)',
    'MRS_POTTS': 'la signora Pottsdam (madre di Stephanie)', 'BUSTER': 'il colonnello Buster',
    'HERRILL': 'il preside Herrill', 'BOYLE': 'Boyle, direttore delle poste', 'EDNA': 'Edna della tavola calda',
    'WHALEY': 'la signorina Whaley, insegnante', 'SERGEANT': 'il sergente della Loggia',
    'LOOMIS': 'il vicesceriffo Loomis', 'PHELPS': "la signora Phelps dell'emporio",
    'JIMMY': 'Jimmy James, lo strillone', 'KARIN': 'Karin, bambina', 'WASP_WOMAN': 'la Donna Vespa',
    'SPARKY': 'Sparky, pompiere', 'BUTCHER': 'il macellaio', 'MCKNIGHT': 'McKnight della TV',
}


def parlante(p):
    if not p:
        return 'parlante non noto'
    return NOMI_PARL.get(p, p)


def prepara():
    os.makedirs(LOTTI, exist_ok=True)
    if glob.glob(os.path.join(LOTTI, 'lotto_*.po')):
        sys.exit('i lotti esistono già: non li sovrascrivo')
    idx = hpo.read(os.path.join(MOD, 'dialoghi.po'))
    rsp = hpo.read(os.path.join(MOD, 'risposte.po'))
    idx_by = {e.ctxt: e for e in idx.values()}
    rsp_by = {e.ctxt: e for e in rsp.values()}
    conv = json.load(open(os.path.join(RADICE, 'estratti', 'conversazioni.json')))

    def tipo_rsp(e):
        return e.comments[0].split(': ', 1)[1]

    usati = set()
    gruppi = []   # (chiave_ordinamento, [voci], [commenti_per_voce])
    for f in conv:
        voci = []
        nota = []
        for ev in f['eventi']:
            if ev[0] == 'di':
                c = f'IDX:{ev[1]}'
                if c in idx_by and c not in usati:
                    usati.add(c)
                    voci.append((idx_by[c], [f'parla: {parlante(ev[2])}'] + nota))
                    nota = []
            else:
                c = f'RSP:{ev[1]}'
                if c not in rsp_by:
                    continue
                e = rsp_by[c]
                t = tipo_rsp(e)
                if 'scelta' in t or 'altro' in t:
                    if c not in usati:
                        usati.add(c)
                        voci.append((e, ['SCELTA DI RISPOSTA mostrata al giocatore (poi Steve la dice: tienila coerente con la sua battuta)'] + nota))
                        nota = []
                elif 'menu' in t:
                    nota.append(f'[qui il gioco mostra il menu argomenti: {e.msgid}]')
                elif 'confronto' in t:
                    nota.append(f'[ramo: se il giocatore ha scelto/scritto l\'argomento {e.msgid!r}]')
        if voci:
            nums = [int(v[0].ctxt[4:]) for v in voci if v[0].ctxt.startswith('IDX:')]
            gruppi.append((min(nums) if nums else 10 ** 6, voci, f['inizio']))
    # battute non trovate nel codice
    for c, e in idx_by.items():
        if c not in usati:
            usati.add(c)
            gruppi.append((int(c[4:]), [(e, ['battuta non collegata a una conversazione nel codice (ordine numerico)'])], None))
    # scelte non usate dal codice
    resto = [e for c, e in rsp_by.items() if c not in usati and tipo_rsp(e) in ('scelta', 'altro', 'inutilizzata')
             and ('/' in e.msgid and e.msgid.startswith('1.') or tipo_rsp(e) != 'inutilizzata')]
    gruppi.sort(key=lambda g: g[0])
    lotti = []
    cur, parole = [], 0
    for k, voci, fn in gruppi:
        w = sum(len(v[0].msgid.split()) for v in voci)
        if cur and parole + w > PAROLE_LOTTO:
            lotti.append(cur)
            cur, parole = [], 0
        if fn:
            voci[0] = (voci[0][0], [f'=== inizio conversazione (funzione {fn}) ==='] + voci[0][1])
        cur += voci
        parole += w
    if cur:
        lotti.append(cur)
    for i, l in enumerate(lotti, 1):
        ent = []
        for e, com in l:
            ent.append(hpo.Entry(e.ctxt, e.msgid, '', com + [x for x in e.comments if not x.startswith('parla:')]))
        hpo.write(os.path.join(LOTTI, f'lotto_{i:02d}.po'), ent, f'lotto {i}')
        print(f'lotto_{i:02d}: {len(ent)} voci, {sum(len(e.msgid.split()) for e in ent)} parole')
    ent = [hpo.Entry(e.ctxt, e.msgid, '', e.comments) for e in resto]
    hpo.write(os.path.join(LOTTI, 'risposte_resto.po'), ent, 'scelte non collegate')
    print('risposte_resto:', len(ent))
    # testi dello script per disco
    testi = hpo.read(os.path.join(MOD, 'testi.po'))
    a = [e for e in testi.values() if 'A' in ''.join(x.split(':')[0] for x in e.comments[0].split(': ', 1)[1].split(', '))]
    b = [e for e in testi.values() if e not in a]
    hpo.write(os.path.join(LOTTI, 'testi_A.po'), a, 'testi dischi 1-2')
    hpo.write(os.path.join(LOTTI, 'testi_B.po'), b, 'testi disco 3 (la Loggia)')
    print('testi', len(a), len(b))
    nomi = hpo.read(os.path.join(MOD, 'nomi.po'))
    hpo.write(os.path.join(LOTTI, 'nomi.po'), list(nomi.values()), 'nomi')
    print('nomi', len(nomi))


def unisci():
    dest = {
        'IDX:': 'dialoghi.po', 'RSP:': 'risposte.po', 'TEXT:': 'testi.po', 'NOME': 'nomi.po',
    }
    cat = {}
    for pref, f in dest.items():
        p = os.path.join(TRAD, f)
        if not os.path.exists(p):
            shutil_copy(os.path.join(MOD, f), p)
        cat[pref] = hpo.read(p)
    agg = collections.Counter()
    for path in sorted(glob.glob(os.path.join(LOTTI, '*.po'))):
        for (c, m), e in hpo.read(path).items():
            pref = next(p for p in dest if c.startswith(p))
            po = cat[pref]
            if (c, m) not in po:
                print('voce sconosciuta', os.path.basename(path), c)
                continue
            if e.msgstr and po[(c, m)].msgstr != e.msgstr:
                po[(c, m)].msgstr = e.msgstr
                po[(c, m)].flags = e.flags
                agg[pref] += 1
    for pref, f in dest.items():
        hpo.write(os.path.join(TRAD, f), list(cat[pref].values()), f)
        po = cat[pref]
        fatte = sum(1 for e in po.values() if e.msgstr)
        print(f'{f}: {agg[pref]} aggiornate, {fatte}/{len(po)} tradotte')


def shutil_copy(a, b):
    import shutil
    shutil.copy(a, b)


if __name__ == '__main__':
    {'prepara': prepara, 'unisci': unisci}[sys.argv[1]]()
