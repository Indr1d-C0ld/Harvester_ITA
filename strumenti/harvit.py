#!/usr/bin/env python3
"""Traduzione italiana di Harvester (DigiFX/Merit, 1996).

    harvit.py estrai   -> crea/aggiorna i cataloghi in traduzione/modelli/
    harvit.py costruisci [--solo-dati]  -> build/ (ISO patchate + cartella C:\\HARVEST con CD1..CD3)
    python3 tools/manuale.py            -> build/Harvester_manuale_ITA.pdf

I file originali stanno in cd/ (ISO a 2048 byte ricavate dalle immagini grezze) e in
orig/HARVEST (installazione). Non vengono mai modificati.
"""
import os, re, sys, json, shutil, argparse, collections

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)
sys.path.insert(0, QUI)
import hpo

CD = os.path.join(RADICE, 'cd')
TRAD = os.path.join(RADICE, 'traduzione')
MODELLI = os.path.join(TRAD, 'modelli')
ESTR = os.path.join(RADICE, 'estratti')


# ---------------------------------------------------------------- codifiche
def xor(b):
    """HARVEST.SCR e DIALOGUE.IDX: ogni byte XOR 0xAA tranne CR e LF."""
    return bytes(x if x in (10, 13) else x ^ 0xAA for x in b)


def leggi_scr(disco):
    return xor(open(os.path.join(CD, disco, 'HARVEST.SCR'), 'rb').read()).decode('latin-1')


def leggi_idx():
    return xor(open(os.path.join(CD, 'd1', 'DIALOGUE.IDX'), 'rb').read()).decode('latin-1')


def leggi_rsp():
    return open(os.path.join(CD, 'd1', 'DIALOG.RSP'), 'rb').read().decode('latin-1').split('\r\n')


# ---------------------------------------------------------------- DIALOGUE.IDX
RE_VOCE = re.compile(r'^(?P<pre>[^"]*)"(?P<testo>.*?)(?P<chiusa>"?)$')


def voci_idx(testo):
    """Il gioco legge righe alterne: numero, testo (una sola riga, max 410 byte).
    Restituisce [(numero, prefisso, testo, chiusa)] e lo scheletro per ricostruire."""
    righe = testo.split('\r\n')
    out = []
    i = 0
    while i < len(righe):
        r = righe[i]
        if r.strip() == '':
            i += 1
            continue
        if not r.isdigit():
            raise ValueError(f'riga {i}: atteso numero, trovato {r!r}')
        n = int(r)
        t = righe[i + 1]
        m = RE_VOCE.match(t)
        if not m:
            raise ValueError(f'riga {i + 1}: testo senza virgolette {t!r}')
        out.append((n, m.group('pre'), m.group('testo'), m.group('chiusa')))
        i += 2
    return out


# ---------------------------------------------------------------- HARVEST.SCR
RE_Q = re.compile(r'"([^"]*)"')


def campi(riga):
    return [(m.start(1), m.end(1), m.group(1)) for m in RE_Q.finditer(riga)]


def tipo_riga(riga):
    s = riga.strip()
    if not s or s.startswith('{') or s.startswith('//'):
        return None
    m = re.match(r'^[-\d\s.]*([A-Z_0-9]+)\s', s + ' ')
    return m.group(1) if m else None


def testi_scr(testo):
    """Genera (n_riga, tipo, chiave, campo_idx, valore) per ogni stringa visibile."""
    for n, riga in enumerate(testo.split('\r\n')):
        t = tipo_riga(riga)
        if t is None:
            continue
        c = campi(riga)
        if t == 'TEXT' and len(c) >= 3:
            yield n, 'TEXT', c[0][2], 2, c[2][2], c[1][2]
        elif t in ('OBJECT', 'NPC') and c:
            v = c[-1][2]
            if v and v != 'NULL_ID':
                chiave = c[1][2] if t == 'OBJECT' else c[2][2]
                yield n, t, chiave, len(c) - 1, v, c[0][2]
        elif t == 'MAP_LOCATION' and c:
            yield n, t, c[1][2] if len(c) > 1 else '', 0, c[0][2], ''


def sp(s):
    return s.replace('_', ' ')


# ---------------------------------------------------------------- estrazione
def estrai():
    os.makedirs(MODELLI, exist_ok=True)
    parl = {}
    p = os.path.join(ESTR, 'parlanti_exe.json')
    if os.path.exists(p):
        parl = {int(k): v for k, v in json.load(open(p)).items()}

    # dialoghi
    voci = voci_idx(leggi_idx())
    ent = []
    for n, pre, t, chiusa in voci:
        com = []
        if n in parl:
            com.append('parla: ' + ', '.join(parl[n]))
        if pre:
            com.append(f'prefisso originale da conservare: {pre!r}')
        com.append(f'lunghezza inglese {len(t)} (massimo assoluto 405)')
        ent.append(hpo.Entry(f'IDX:{n}', t, '', com))
    hpo.write(os.path.join(MODELLI, 'dialoghi.po'), ent, 'DIALOGUE.IDX')

    # script: testi descrittivi e nomi
    testi = collections.OrderedDict()
    nomi = collections.OrderedDict()
    for disco, sigla in (('d1', 'A'), ('d3', 'B')):
        for n, tipo, chiave, ci, val, extra in testi_scr(leggi_scr(disco)):
            if tipo == 'TEXT':
                k = (chiave, val)
                testi.setdefault(k, []).append(f'{sigla}{n + 1}:{extra}')
            else:
                nomi.setdefault(val, []).append(f'{tipo} {chiave} [{sigla}:{extra}]')
    ent = []
    visti = collections.Counter()
    for (chiave, val), dove in testi.items():
        visti[chiave] += 1
        ctx = f'TEXT:{chiave}' if visti[chiave] == 1 else f'TEXT:{chiave}#{visti[chiave]}'
        ent.append(hpo.Entry(ctx, sp(val), '', [f'riquadro e righe: {", ".join(dove)}']))
    hpo.write(os.path.join(MODELLI, 'testi.po'), ent, 'HARVEST.SCR TEXT')
    ent = []
    for val, dove in nomi.items():
        ent.append(hpo.Entry('NOME', sp(val), '', ['usato da: ' + '; '.join(dove[:6]) + (' ...' if len(dove) > 6 else '')]))
    hpo.write(os.path.join(MODELLI, 'nomi.po'), ent, 'HARVEST.SCR nomi')

    # DIALOG.RSP
    usi = json.load(open(os.path.join(ESTR, 'rsp_usi.json')))
    T = {'0x8145a': 'confronto', '0x7af10': 'scelta', None: 'menu', '0x3a1a0': 'altro', '0x80be1': 'altro'}
    rsp = leggi_rsp()
    ent = []
    for i, r in enumerate(rsp):
        if not r:
            continue
        u = usi.get(str(i))
        tipo = ','.join(sorted(set(T.get(t, 'altro') for a, t in u))) if u else 'inutilizzata'
        ent.append(hpo.Entry(f'RSP:{i}', r, '', [f'tipo: {tipo}']))
    hpo.write(os.path.join(MODELLI, 'risposte.po'), ent, 'DIALOG.RSP')

    # suggerimenti
    tips = open(os.path.join(CD, 'd1', 'ADJHEAD.RCS'), 'rb').read().decode('latin-1').split('\r\n')
    ent = [hpo.Entry(f'TIP:{i}', t, '', []) for i, t in enumerate(tips) if t]
    hpo.write(os.path.join(MODELLI, 'suggerimenti.po'), ent, 'ADJHEAD.RCS')

    # MENU.INI
    ent = []
    for r in open(os.path.join(CD, 'd1', 'MENU.INI'), 'rb').read().decode('latin-1').split('\r\n'):
        if '=' in r:
            k, v = r.split('=', 1)
            ent.append(hpo.Entry(f'MENU:{k}', v, '', ['spazi finali originali conservati se presenti']))
    hpo.write(os.path.join(MODELLI, 'menu.po'), ent, 'MENU.INI')
    print('modelli scritti in', MODELLI)


# ---------------------------------------------------------------- costruzione
BUILD = os.path.join(RADICE, 'build')
CHAR_RIGA = 38          # il motore va a capo a numero di caratteri (verificato sui riquadri originali)


def righe_testo(t, n=CHAR_RIGA):
    k = 0
    while len(t) > n:
        p = n
        while p > 0 and t[p] != ' ':
            p -= 1
        if p == 0:
            p = n
        t = t[p + 1:]
        k += 1
    return k + 1


def riquadro(righe):
    for lim, b in ((1, 1), (2, 2), (3, 3), (5, 4), (6, 5), (8, 6), (10, 7)):
        if righe <= lim:
            return b
    return 8


def carica(nome):
    p = os.path.join(TRAD, nome + '.po')
    return hpo.read(p) if os.path.exists(p) else {}


def tr_dict(nome):
    """{(ctxt, msgid): msgstr} solo per le voci tradotte."""
    return {k: e.msgstr for k, e in carica(nome).items() if e.msgstr}


def enc(s):
    return s.encode('latin-1')


def parole_chiave():
    kw = {e.msgid: e.msgstr for e in carica('parole_chiave').values() if e.msgstr}
    kw[''] = ''          # menu che cominciano con '/' (voce vuota)
    return kw


def costruisci_rsp(stat):
    rsp = leggi_rsp()
    tr = {c: s for (c, m), s in tr_dict('risposte').items()}
    usi = json.load(open(os.path.join(ESTR, 'rsp_usi.json')))
    kw = parole_chiave()
    # la riga di confronto identica a una scelta segue la traduzione della scelta
    for i, r in enumerate(rsp):
        if r in kw and f'RSP:{i}' in tr and r.startswith('1.'):
            kw[r] = tr[f'RSP:{i}']
    out = []
    for i, r in enumerate(rsp):
        parti = r.split('/')
        tipo = set(t for a, t in usi.get(str(i), []))
        if r and (('0x8145a' in tipo or None in tipo) or all(p in kw for p in parti)) and all(p in kw for p in parti):
            out.append('/'.join(kw[p] for p in parti))
            stat['rsp_chiavi'] += 1
        elif f'RSP:{i}' in tr:
            out.append(tr[f'RSP:{i}'])
            stat['rsp_tradotte'] += 1
        else:
            out.append(r)
            if r:
                stat['rsp_inglesi'] += 1
    return enc('\r\n'.join(out))


def costruisci_idx(stat):
    tr = {c: s for (c, m), s in tr_dict('dialoghi').items()}
    out = []
    for n, pre, t, chiusa in voci_idx(leggi_idx()):
        it = tr.get(f'IDX:{n}', t)
        if f'IDX:{n}' in tr:
            stat['idx_tradotte'] += 1
        riga = f'{pre}"{it}{chiusa}'
        if len(enc(riga)) > 410:
            raise ValueError(f'IDX:{n} troppo lunga ({len(riga)})')
        out.append(f'{n}\r\n{riga}\r\n')
    return xor(enc(''.join(out)))


def costruisci_scr(disco, stat):
    testo = leggi_scr(disco)
    testi = {}
    for (c, m), s in tr_dict('testi').items():
        testi.setdefault((c.split(':', 1)[1].split('#')[0], m), s)
    nomi = {m: s for (c, m), s in tr_dict('nomi').items()}
    righe = testo.split('\r\n')
    voci = {}
    for n, tipo, chiave, ci, val, extra in testi_scr(testo):
        voci.setdefault(n, []).append((tipo, chiave, ci, val, extra))
    for n, lista in voci.items():
        riga = righe[n]
        c = campi(riga)
        sost = {}
        for tipo, chiave, ci, val, extra in lista:
            if tipo == 'TEXT':
                it = testi.get((chiave, sp(val)))
                if it is None:
                    continue
                sost[ci] = it.replace(' ', '_')
                b0 = int(extra[3:]) if extra.startswith('BOX') and extra[3:].isdigit() else None
                if b0:
                    nb = max(b0, riquadro(righe_testo(it)))
                    if nb != b0:
                        sost[1] = f'BOX{nb}'
                        stat['riquadri_ingranditi'] += 1
                stat['scr_testi'] += 1
            else:
                it = nomi.get(sp(val))
                if it is None:
                    continue
                sost[ci] = it.replace(' ', '_')
                stat['scr_nomi'] += 1
        for ci in sorted(sost, reverse=True):
            a, b, _ = c[ci]
            riga = riga[:a] + sost[ci] + riga[b:]
        righe[n] = riga
    return xor(enc('\r\n'.join(righe)))


def costruisci_menu(stat):
    import cft
    tr = {c: s for (c, m), s in tr_dict('menu').items()}
    font = cft.CFT.load(os.path.join(CD, 'd1', 'GRAPHIC', 'FONT', 'HARVFONT.CFT'))

    def larg(s):
        return sum(font.space if ch == ' ' else font.width[ord(ch.lower()) if not font.width[ord(ch)] else ord(ch)] for ch in s)
    out = []
    for r in open(os.path.join(CD, 'd1', 'MENU.INI'), 'rb').read().decode('latin-1').split('\r\n'):
        if '=' not in r:
            out.append(r)
            continue
        k, v = r.split('=', 1)
        if f'MENU:{k}' not in tr:
            out.append(r)
            continue
        it = tr[f'MENU:{k}'].strip(' ')
        lab = v.rstrip(' ')
        if k in ('options_menu_1', 'options_menu_2', 'options_menu_3') and v != lab:
            # il cursore del volume sta a destra: l'etichetta (centrata insieme agli
            # spazi) deve finire non più a destra dell'originale
            wo = larg(v)
            need = wo - 2 * larg(lab) + larg(it)
            n = max(1, -(-need // font.space))
            it = it + ' ' * n
        elif k in ('newgame', 'quitgame'):
            it = ' ' * (len(v) - len(v.lstrip(' '))) + it
        out.append(f'{k}={it}')
        stat['menu'] += 1
    return enc('\r\n'.join(out))


def costruisci_suggerimenti(stat):
    tr = {c: s for (c, m), s in tr_dict('suggerimenti').items()}
    righe = open(os.path.join(CD, 'd1', 'ADJHEAD.RCS'), 'rb').read().decode('latin-1').split('\r\n')
    out = []
    for i, t in enumerate(righe):
        out.append(tr.get(f'TIP:{i}', t))
        stat['suggerimenti'] += f'TIP:{i}' in tr
    return enc('\r\n'.join(out))


def costruisci_font(nome):
    import cft
    f = cft.CFT.load(os.path.join(CD, 'd1', 'GRAPHIC', 'FONT', nome))
    cft.aggiungi_grave(f)
    return f.dump()


def costruisci_exe(stat):
    import exe_patch
    p = exe_patch.Patch(open(os.path.join(RADICE, 'orig', 'HARVEST', 'HARVEST.EXE'), 'rb').read())
    p.prepara_donatrici()
    kw = parole_chiave()
    for e in carica('eseguibile').values():
        it = e.msgstr
        if e.msgid in kw and kw[e.msgid]:
            it = kw[e.msgid]
        if not it:
            continue
        for fo in e.ctxt[4:].split(','):
            p.sostituisci(int(fo, 16), enc(it))
            stat['exe_stringhe'] += 1
    exe_patch.patch_senza_cd(p)
    return bytes(p.d)


def sostituisci_dat(iso, nome, dati):
    """Sostituisce un file dentro HARVEST.DAT (stesso posto, dimensione non maggiore)
    e aggiorna il record in INDEX.001 e la sua copia nel .DAT."""
    import struct
    from xfile import REC
    idx = bytearray(iso.read('INDEX.001'))
    dat = iso.find_all('HARVEST.DAT')[0]
    chiave = nome.upper().replace('/', '\\')
    for i in range(0, len(idx) - REC + 1, REC):
        n = idx[i + 4:i + 132].split(b'\0')[0].decode('latin-1').upper()
        if n.split(':', 1)[-1].lstrip('\\') == chiave:
            a, s1, c, s2 = struct.unpack_from('<4I', idx, i + 132)
            if len(dati) > s1:
                raise ValueError(f'{nome}: {len(dati)} byte > {s1} originali')
            struct.pack_into('<4I', idx, i + 132, a, len(dati), c, len(dati))
            base = dat.extent * 2048
            iso.f.seek(base + a - REC)
            iso.f.write(bytes(idx[i:i + REC]))
            iso.f.seek(base + a)
            iso.f.write(dati + bytes(s1 - len(dati)))
            iso.replace('INDEX.001', bytes(idx))
            return
    raise KeyError(nome)


def grafica_tradotta():
    """Genera (se mancano) le immagini tradotte in grafica/ e le restituisce per disco."""
    G = os.path.join(RADICE, 'grafica')
    attesi = ['INVENTRY.BM', 'SAVEGAME.BM', 'LOADGAME.BM', 'LOADGAME_d3.BM', 'TIPS.BM', 'KEYWORD.BM',
              'CD1.BM', 'CD2.BM', 'CD3.BM', 'WAIT.ABM', 'CENSORED.PCX', 'MOUSHELP.BM', 'KEYSHELP.BM']
    if not all(os.path.exists(os.path.join(G, n)) for n in attesi):
        import grafica_ui, grafica_aiuto
        grafica_ui.genera_tutto(G)
        for nome, fn in (('MOUSHELP', grafica_aiuto.genera_mouse), ('KEYSHELP', grafica_aiuto.genera_tastiera)):
            img = fn()
            open(os.path.join(G, nome + '.BM'), 'wb').write(img.dump())
            img.png(os.path.join(G, nome + '.png'))
    leggi = lambda n: open(os.path.join(G, n), 'rb').read()
    comuni = {f'GRAPHIC/OTHER/{n}': leggi(n) for n in ('INVENTRY.BM', 'SAVEGAME.BM', 'TIPS.BM', 'KEYWORD.BM',
                                                      'CD1.BM', 'CD2.BM', 'CD3.BM', 'WAIT.ABM')}
    # documenti (primi piani): grafica/documenti/, generati da tools/documenti.py
    DOC = os.path.join(G, 'documenti')
    citta = ['LODGAPP1', 'LODGAPP2', 'PERMIT1', 'PERMIT2', 'SAFEBOOK', 'SCHEDULE', 'BOYLNOTE', 'BOYLCOPY',
             'INVITE', 'TVDEED1', 'TVDEED2', 'DRTYMAG', 'REGISTER', 'BAKESALE']
    loggia = ['CLUE']
    if not all(os.path.exists(os.path.join(DOC, n + '.BM')) for n in citta + loggia):
        import documenti
        os.makedirs(DOC, exist_ok=True)
        for n in citta + loggia:
            img = documenti.DOCUMENTI[n]()
            open(os.path.join(DOC, n + '.BM'), 'wb').write(img.dump())
    doc = lambda n: open(os.path.join(DOC, n + '.BM'), 'rb').read()
    per_disco = {}
    for k in (1, 2, 3):
        d = dict(comuni)
        d['GRAPHIC/OTHER/LOADGAME.BM'] = leggi('LOADGAME_d3.BM' if k == 3 else 'LOADGAME.BM')
        for n in (loggia if k == 3 else citta):
            d[f'GRAPHIC/ROOMS/{n}.BM'] = doc(n)
        per_disco[k] = d
    sciolti = {'GRAPHIC/OTHER/MOUSHELP.BM': leggi('MOUSHELP.BM'), 'GRAPHIC/OTHER/KEYSHELP.BM': leggi('KEYSHELP.BM'),
               'GRAPHIC/OTHER/CENSORED.PCX': leggi('CENSORED.PCX')}
    return per_disco, sciolti


def costruisci(solo_dati=False):
    import iso9660
    stat = collections.Counter()
    os.makedirs(BUILD, exist_ok=True)
    rsp = costruisci_rsp(stat)
    idx = costruisci_idx(stat)
    scr = {'d1': costruisci_scr('d1', stat), 'd3': costruisci_scr('d3', stat)}
    menu = costruisci_menu(stat)
    tips = costruisci_suggerimenti(stat)
    exe = costruisci_exe(stat)
    fonts = {n: costruisci_font(n) for n in os.listdir(os.path.join(CD, 'd1', 'GRAPHIC', 'FONT'))}
    dati = os.path.join(BUILD, 'dati')
    os.makedirs(dati, exist_ok=True)
    for nome, b in (('DIALOG.RSP', rsp), ('DIALOGUE.IDX', idx), ('HARVEST1.SCR', scr['d1']), ('HARVEST3.SCR', scr['d3']),
                    ('MENU.INI', menu), ('ADJHEAD.RCS', tips), ('HARVEST.EXE', exe)):
        open(os.path.join(dati, nome), 'wb').write(b)
    for n, b in fonts.items():
        open(os.path.join(dati, n), 'wb').write(b)
    print(dict(stat))
    if solo_dati:
        return
    # cartella di installazione
    inst = os.path.join(BUILD, 'HARVEST')
    if os.path.exists(inst):
        shutil.rmtree(inst)
    shutil.copytree(os.path.join(RADICE, 'orig', 'HARVEST'), inst, ignore=shutil.ignore_patterns('iso', 'dosbox.conf'))
    for nome, b in (('HARVEST.EXE', exe), ('DIALOG.RSP', rsp), ('MENU.INI', menu)):
        open(os.path.join(inst, nome), 'wb').write(b)
    # immagini dei CD
    grafica, sciolti = grafica_tradotta()
    os.makedirs(os.path.join(BUILD, 'iso'), exist_ok=True)
    for k in (1, 2, 3):
        dst = os.path.join(BUILD, 'iso', f'DISK{k}.iso')
        shutil.copyfile(os.path.join(CD, f'DISK{k}.iso'), dst)
        iso = iso9660.ISO(dst)
        iso.replace('HARVEST.SCR', scr['d3' if k == 3 else 'd1'])
        iso.replace('DIALOGUE.IDX', idx)
        iso.replace('ADJHEAD.RCS', tips)
        if iso.find_all('DIALOG.RSP'):
            iso.replace('DIALOG.RSP', rsp)
        if iso.find_all('MENU.INI'):
            iso.replace('MENU.INI', menu)
        if iso.find_all('HARVEST.EXE'):
            iso.replace('HARVEST.EXE', exe)
        for n, b in fonts.items():
            iso.replace(f'GRAPHIC/FONT/{n}', b)
        for n, b in grafica[k].items():
            sostituisci_dat(iso, n, b)
        for n, b in sciolti.items():
            iso.replace(n, b)
        iso.close()
        print('scritto', dst)
    installa_senza_cd(inst)


ESCLUSI_CD = ('16BIT', '32BIT', 'VESA', 'MAKINGOF.AVI', 'SETUP.EXE', 'SETUP.CFG', 'INSTALL.EXE', 'INSTALL.CFG',
              'ISETUP.EXE', 'UNINSTAL.EXE', 'README.BAK')
CONFIG_SENZA_CD = '''FX_VOLUME=9
MUSIC_VOLUME=3
TEXT=YES
GORE=YES
QUICK_TIPS=ON
SAVE=.\\
VOICE=SOUND\\VOICE\\
GAMMA=0
TOWN=HARVEST.SCR
NETWORK=ITA
CD_ROM=C:\\HARVEST\\CD1\\
DRIVE_1=C:\\HARVEST\\CD1\\HARVEST.DAT
DRIVE_2=C:\\HARVEST\\CD1\\SOUND.DAT
DRIVE_3=C:\\HARVEST\\CD1\\HARVEST2.DAT
'''


def installa_senza_cd(inst):
    """Copia il contenuto dei tre CD tradotti in HARVEST/CD1..CD3 e configura il gioco
    nella modalità NETWORK (vedi exe_patch.patch_senza_cd): niente cambi di disco."""
    import subprocess, filecmp
    for k in (1, 2, 3):
        dst = os.path.join(inst, f'CD{k}')
        if os.path.exists(dst):
            shutil.rmtree(dst)
        esc = sum((['-x!' + e] for e in ESCLUSI_CD), [])
        subprocess.run(['7z', 'x', '-y', '-o' + dst, os.path.join(BUILD, 'iso', f'DISK{k}.iso')] + esc,
                       check=True, stdout=subprocess.DEVNULL)
    # file identici fra i dischi: collegamenti fisici (risparmia spazio)
    risparmio = 0
    base = os.path.join(inst, 'CD1')
    for k in (2, 3):
        altro = os.path.join(inst, f'CD{k}')
        for radice, _, files in os.walk(altro):
            for f in files:
                p2 = os.path.join(radice, f)
                p1 = os.path.join(base, os.path.relpath(p2, altro))
                if os.path.exists(p1) and os.path.getsize(p1) == os.path.getsize(p2) and filecmp.cmp(p1, p2, shallow=False):
                    risparmio += os.path.getsize(p2)
                    os.remove(p2)
                    os.link(p1, p2)
    for nome in ('CONFIG.INI', 'CONFIG.NCD'):
        open(os.path.join(inst, nome), 'wb').write(CONFIG_SENZA_CD.replace('\n', '\r\n').encode())
    # configurazione originale per chi preferisce le immagini dei CD (dosbox-harvester-ita-cd.conf)
    shutil.copyfile(os.path.join(RADICE, 'orig', 'HARVEST', 'CONFIG.INI'), os.path.join(inst, 'CONFIG.CD'))
    for f in os.listdir(os.path.join(RADICE, 'pacchetto')):
        shutil.copyfile(os.path.join(RADICE, 'pacchetto', f), os.path.join(BUILD, f))
    print(f'installazione senza CD in {inst} (collegati {risparmio // 2**20} MB di file identici)')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('azione', choices=['estrai', 'costruisci', 'prova'])
    ap.add_argument('--solo-dati', action='store_true')
    a = ap.parse_args()
    if a.azione == 'estrai':
        estrai()
    elif a.azione == 'costruisci':
        costruisci(a.solo_dati)
