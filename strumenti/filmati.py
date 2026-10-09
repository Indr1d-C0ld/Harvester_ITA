"""Sottotitoli dei filmati: dalla trascrizione al catalogo traduzione/filmati.po.

  filmati.py prepara <trascrizione.json> [--rifai]
  filmati.py fogli <cartella> [FILMATO...]   miniature per riconoscere chi parla

La trascrizione è l'uscita di faster-whisper con i tempi per parola
({filmato: [segmenti con 'parole': [inizio, fine, parola, probabilità]]}).
Il parlato viene diviso in sottotitoli (una frase o un pezzo di frase che
in italiano stia in due righe), i tempi diventano fotogrammi (15 al secondo:
il fotogramma i va in onda quando l'audio è arrivato a i/15 secondi).

Ogni voce del catalogo ha come contesto "FILMATO primo-dopo" (fotogrammi,
il secondo escluso): per spostare un sottotitolo basta cambiare il contesto.
Il catalogo è il testo di riferimento (la trascrizione si corregge lì):
prepara aggiunge solo i filmati che mancano; --rifai riscrive tutto.
Le parole che il riconoscitore ha capito male sono segnalate nei commenti
("dubbio: ...") per la revisione a orecchio. Le traduzioni già fatte si
conservano quando il testo inglese non cambia."""
import json, os, re, struct, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hpo

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOGO = os.path.join(RADICE, 'traduzione', 'filmati.po')
FPS = 15
MAX_CAR = 64          # caratteri inglesi per sottotitolo: l'italiano è più lungo
MIN_FOT = 18          # durata minima (1,2 s)
CODA = 9              # fotogrammi di tenuta dopo l'ultima parola
DISTACCO = 2          # fotogrammi liberi fra due sottotitoli
DUBBIO = 0.5          # parole sotto questa probabilità vanno riascoltate
# frasi che whisper inventa su musica e silenzio
ALLUCINAZIONI = re.compile(r"(?i)^(you|uh|oh|thanks? (you )?for watching!?|.*see you in the next (one|video).*|"
                           r"this is the end of the video.*|.*subscribe.*|🎵.*|\W*)$")


ABBREVIAZIONI = re.compile(r'(?i)^(mr|mrs|ms|dr|st|jr|sr)\.$')


def fotogrammi():
    """{nome FST: numero di fotogrammi} dai filmati della build (il primo trovato)."""
    out = {}
    for p in sorted(glob.glob(os.path.join(RADICE, 'build', 'HARVEST', 'CD*', 'GRAPHIC', 'FST', '*.FST'))):
        n = os.path.basename(p)
        if n not in out:
            with open(p, 'rb') as f:
                out[n] = struct.unpack('<4s7I', f.read(32))[4]
    return out


def parole_buone(segmenti):
    """Le parole dei segmenti veri, scartate le allucinazioni."""
    out = []
    for s in segmenti:
        t = s['testo'].strip()
        if ALLUCINAZIONI.match(t) or (s['nospeech'] > 0.6 and s['logp'] < -0.5) or s['logp'] < -1.0:
            continue
        for a, b, w, p in s['parole']:
            if w.strip():
                out.append([a, b, w.strip(), p])
    return out


def _lung(g):
    return len(' '.join(x[2] for x in g))


def _spezza(g):
    """Divide una frase troppo lunga in parti che stiano sotto MAX_CAR, il più
    possibile uguali, preferendo i tagli dopo una virgola o su una pausa."""
    if _lung(g) <= MAX_CAR or len(g) < 2:
        return [g]
    migliore = None
    for k in range(1, len(g)):
        a, b = g[:k], g[k:]
        costo = abs(_lung(a) - _lung(b))
        if re.search(r'[,;:]$', g[k - 1][2]):
            costo -= 25
        costo -= min(g[k][0] - g[k - 1][1], 1.0) * 40          # pausa fra le due parti
        if re.match(r'(?i)(and|but|or|that|which|who|because|to|of|the|a)$', g[k - 1][2]):
            costo += 30                                         # mai lasciare in coda un legamento
        if min(_lung(a), _lung(b)) < 12:
            costo += 40
        if migliore is None or costo < migliore[0]:
            migliore = (costo, k)
    k = migliore[1]
    return _spezza(g[:k]) + _spezza(g[k:])


def dividi(parole):
    """Raggruppa le parole in sottotitoli: un taglio a ogni fine frase e sulle
    pause lunghe; le frasi troppo lunghe si dividono con _spezza."""
    frasi, cur = [], []
    for w in parole:
        fine = re.search(r'[.?!]["\']?$', cur[-1][2]) and not ABBREVIAZIONI.match(cur[-1][2]) if cur else False
        if cur and (w[0] - cur[-1][1] > 1.0 or fine):
            frasi.append(cur)
            cur = []
        cur.append(w)
    if cur:
        frasi.append(cur)
    # un pezzo che finisce con la virgola va con la frase che segue, se ci sta
    unite = []
    for f in frasi:
        if unite and re.search(r'[,;:]$', unite[-1][-1][2]) and _lung(unite[-1]) < 15 \
                and f[0][0] - unite[-1][-1][1] < 1.5:
            unite[-1] = unite[-1] + f
        else:
            unite.append(f)
    return [p for f in unite for p in _spezza(f)]


def tempi(gruppi, n_fot):
    """[(primo, dopo_l_ultimo)] in fotogrammi, senza sovrapposizioni."""
    out = []
    for g in gruppi:
        da = int(round(g[0][0] * FPS))
        a = int(round(g[-1][1] * FPS)) + CODA
        a = max(a, da + MIN_FOT)
        out.append([da, a])
    for i in range(len(out) - 1):
        if out[i][1] > out[i + 1][0] - DISTACCO:
            out[i][1] = max(out[i][0] + 6, out[i + 1][0] - DISTACCO)
    for t in out:
        t[1] = min(t[1], n_fot)
        t[0] = min(t[0], t[1] - 1)
    return out


def prepara(trascrizione, rifai=False):
    """Aggiunge al catalogo i filmati della trascrizione che non ci sono ancora;
    quelli presenti restano come sono (correzioni e traduzioni comprese).
    Con rifai riscrive tutto, conservando le traduzioni dei testi invariati."""
    tr = json.load(open(trascrizione))
    nf = fotogrammi()
    vecchio = hpo.read(CATALOGO) if os.path.exists(CATALOGO) else {}
    tradotte = {(e.ctxt.split()[0], e.msgid): e for e in vecchio.values()}
    voci = [] if rifai else list(vecchio.values())
    presenti = set() if rifai else {e.ctxt.split()[0] for e in voci}
    nuovi = 0
    for film in sorted(tr):
        nome = film.split('_')[0] + '.FST'          # C119A_cd2: seconda versione dello stesso nome
        if nome not in nf or film in presenti:
            continue
        base = film.split('_')[0]
        if base != film and base in tr and [s['testo'] for s in tr[film]] == [s['testo'] for s in tr[base]]:
            continue                                # stessa battuta della versione principale
        parole = parole_buone(tr[film])
        if not parole:
            continue
        gruppi = dividi(parole)
        for g, (da, a) in zip(gruppi, tempi(gruppi, nf[nome])):
            testo = ' '.join(w[2] for w in g)
            note = [f'{g[0][0]:.2f}-{g[-1][1]:.2f} s']
            if '_' in film:
                note.append(f'versione {film}')
            dubbi = [f'{w[2]} ({w[3]:.2f})' for w in g if w[3] < DUBBIO]
            if dubbi:
                note.append('dubbio: ' + ', '.join(dubbi))
            prima = tradotte.get((film, testo))
            voci.append(hpo.Entry(f'{film} {da:04d}-{a:04d}', testo, prima.msgstr if prima else '', note,
                                  prima.flags if prima else []))
            nuovi += 1
    voci.sort(key=lambda e: (e.ctxt.split()[0], e.ctxt.split()[1]))
    hpo.write(CATALOGO, voci, 'trascrizione dei filmati (faster-whisper large-v3), da rivedere')
    print(f'{nuovi} sottotitoli aggiunti; in tutto {len(voci)} in {len({e.ctxt.split()[0] for e in voci})} filmati, '
          f'{sum(1 for e in voci if any(c.startswith("dubbio") for c in e.comments))} con parole dubbie -> {CATALOGO}')


def da_catalogo():
    """{nome FST: [(primo, dopo, testo italiano)]} per SOTTOTIT.ITA (solo voci tradotte)."""
    out = {}
    if not os.path.exists(CATALOGO):
        return out
    for e in hpo.read(CATALOGO).values():
        if not e.msgstr:
            continue
        film, intervallo = e.ctxt.split()
        da, a = (int(x) for x in intervallo.split('-'))
        out.setdefault(film.split('_')[0] + '.FST', []).append((da, a, e.msgstr))
    return out


def fogli(cartella, scelti=()):
    """Per ogni filmato del catalogo un foglio di miniature: il fotogramma a metà
    di ogni sottotitolo con il testo inglese sotto (per sapere chi parla)."""
    from PIL import Image, ImageDraw
    import fst
    os.makedirs(cartella, exist_ok=True)
    per_film = {}
    for e in hpo.read(CATALOGO).values():
        film, intervallo = e.ctxt.split()
        da, a = (int(x) for x in intervallo.split('-'))
        per_film.setdefault(film, []).append(((da + a) // 2, e.msgid, intervallo))
    percorsi = {}
    for p in sorted(glob.glob(os.path.join(RADICE, 'build', 'HARVEST', 'CD*', 'GRAPHIC', 'FST', '*.FST'))):
        percorsi.setdefault(os.path.basename(p)[:-4], p)
        percorsi.setdefault(os.path.basename(p)[:-4] + '_cd' + p.split(os.sep)[-4][-1], p)
    for film, voci in sorted(per_film.items()):
        if scelti and film not in scelti:
            continue
        f = fst.FST(percorsi[film])
        voci.sort()
        quadri = {}
        for i, s, tav in fst.decodifica(f, a=voci[-1][0] + 1):
            if any(v[0] == i for v in voci):
                quadri[i] = Image.fromarray(fst.rgb(s, tav))
        col = 4
        righe = (len(voci) + col - 1) // col
        foglio = Image.new('RGB', (col * 320, righe * 250), (20, 20, 20))
        d = ImageDraw.Draw(foglio)
        for k, (i, testo, intervallo) in enumerate(voci):
            x, y = (k % col) * 320, (k // col) * 250
            foglio.paste(quadri[i], (x, y))
            d.text((x + 4, y + 202), f'{k + 1}. {intervallo}', fill=(255, 220, 120))
            parole, riga, yy = testo.split(), '', y + 214
            for w in parole:
                if len(riga) + len(w) > 50:
                    d.text((x + 4, yy), riga, fill=(230, 230, 230)); yy += 11; riga = ''
                riga += w + ' '
            d.text((x + 4, yy), riga, fill=(230, 230, 230))
        foglio.save(os.path.join(cartella, film + '.png'))
        print(film, len(voci))


if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[1] == 'fogli':
        fogli(sys.argv[2], sys.argv[3:])
        raise SystemExit
    if len(sys.argv) in (3, 4) and sys.argv[1] == 'prepara':
        prepara(sys.argv[2], '--rifai' in sys.argv)
    else:
        print(__doc__)
