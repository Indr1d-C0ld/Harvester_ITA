"""Schermate di aiuto in italiano (MOUSHELP, KEYSHELP, INVHELP: file sciolti sul CD).

Il testo minuto usa il font bitmap ricavato dalle schermate originali
(estratti/font_aiuto.pkl, vedi fonthelp.py) più alcune lettere disegnate qui."""
import os, sys, pickle
import numpy as np
import cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grafica import BM

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIANCO, VERDE, NERO = 15, 31, 0


def _g(righe):
    """Glifo da stringhe ('#' acceso) in una maschera 12 righe (riga 1 = cima maiuscole, 8 = base)."""
    m = np.array([[c == '#' for c in r] for r in righe], dtype=bool)
    out = np.zeros((12, m.shape[1]), dtype=bool)
    out[:m.shape[0]] = m
    return out


def _accenta(base, grave=True, cols=None):
    g = base.copy()
    w = g.shape[1]
    if cols is None:
        c0 = max(0, w // 2 - 1)
        cols = (c0, c0 + 1)
    a, b = cols
    if grave:
        g[1, a] = True
        g[2, b] = True
    else:
        g[1, b] = True
        g[2, a] = True
    return g


def carica_font():
    f = pickle.load(open(os.path.join(RADICE, 'estratti', 'font_aiuto.pkl'), 'rb'))
    f = {c: g.astype(bool) for c, g in f.items()}
    f['q'] = f['p'][:, ::-1].copy()
    f['z'] = _g(['.....', '.....', '.....', '#####', '...#.', '..#..', '.#...', '#####'])
    f['à'] = _accenta(f['a'])
    f['è'] = _accenta(f['e'])
    f['é'] = _accenta(f['e'], grave=False)
    f['ò'] = _accenta(f['o'])
    f['ù'] = _accenta(f['u'])
    i = f['i'].copy()
    i[1, :] = False
    i[1, 0] = True
    i[2, 1] = True
    f['ì'] = i
    f.setdefault('V', _g(['.....', '#...#', '#...#', '#...#', '.#.#.', '.#.#.', '..#..', '..#..']))
    f.setdefault(':', _g(['.', '.', '.', '#', '.', '.', '.', '#']))
    return f


def larghezza(f, testo):
    w = 0
    for k, c in enumerate(testo):
        if c == ' ':
            w += 6
        else:
            w += f[c].shape[1] + 1
    return w - 1 if testo else 0


def scrivi(px, f, x, y, testo, colore=BIANCO, contorno=None):
    """y = cima delle maiuscole. Restituisce la x finale."""
    for c in testo:
        if c == ' ':
            x += 6
            continue
        g = f[c]
        h, w = g.shape
        if contorno is not None:
            d = cv2.dilate(g.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
            zona = px[y - 2:y - 2 + h + 2, x - 1:x - 1 + w + 2]
            dd = np.zeros((h + 2, w + 2), bool)
            dd[1:-1, 1:-1] = g
            dd = cv2.dilate(dd.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
            zona[dd[:zona.shape[0], :zona.shape[1]]] = contorno
        zona = px[y - 1:y - 1 + h, x:x + w]
        zona[g[:zona.shape[0], :zona.shape[1]]] = colore
        x += w + 1
    return x - 1


def riga(px, f, x, y, testo, termine=None, **kw):
    """Riga con eventuale 'Termine - ' iniziale in verde."""
    if termine:
        x = scrivi(px, f, x, y, termine, VERDE, **kw) + 1
        testo = ' - ' + testo
    return scrivi(px, f, x, y, testo, BIANCO, **kw)


def centra(px, f, y, testo, **kw):
    w = larghezza(f, testo)
    scrivi(px, f, (640 - w) // 2, y, testo, **kw)


URW_GOTHIC = '/usr/share/fonts/opentype/urw-base35/URWGothic-Book.otf'


def pulisci_testo(img, sfondo, zone=((168, 140, 640, 425), (0, 425, 640, 480))):
    """Nelle zone del testo riporta lo sfondo ricostruito dove l'immagine ne differisce."""
    for x0, y0, x1, y1 in zone:
        z = img.px[y0:y1, x0:x1]
        s = sfondo[y0:y1, x0:x1]
        d = z != s
        z[d] = s[d]


def targa(img, testo, box=(214, 101, 424, 127), size=13, spaziatura=1.0):
    """Ridisegna il titolo sulla targhetta beige: ripulisce replicando una colonna senza testo."""
    from PIL import Image, ImageDraw, ImageFont
    x0, y0, x1, y1 = box
    col = img.px[y0:y1, x0 + 6:x0 + 7].copy()
    img.px[y0:y1, x0 + 10:x1 - 10] = np.repeat(col, x1 - x0 - 20, axis=1)
    fnt = ImageFont.truetype(URW_GOTHIC, size)
    W, H = x1 - x0, y1 - y0
    # misura con spaziatura tra lettere
    lar = [fnt.getbbox(c)[2] if c != ' ' else fnt.getbbox('n')[2] for c in testo]
    tot = sum(lar) + spaziatura * (len(testo) - 1)
    pil = Image.new('L', (W * 4, H * 4), 0)
    d = ImageDraw.Draw(pil)
    f4 = ImageFont.truetype(URW_GOTHIC, size * 4)
    x = (W - tot) / 2 * 4
    asc = fnt.getbbox('M')
    yy = ((H - (asc[3] - asc[1])) / 2 - asc[1]) * 4
    for c, l in zip(testo, lar):
        d.text((x, yy), c, font=f4, fill=255)
        x += (l + spaziatura) * 4
    a = np.array(pil.resize((W, H), Image.LANCZOS)).astype(float) / 255
    zona = img.px[y0:y1, x0:x1]
    rgb = img.pal[zona].astype(float)
    nero = np.array([30, 30, 30], float)
    nuovo = rgb * (1 - a[..., None]) + nero * a[..., None]
    usati = np.unique(zona)
    pal = img.pal
    for yy2, xx in zip(*np.nonzero(a > 0.08)):
        dd = ((pal - nuovo[yy2, xx]) ** 2).sum(1)
        zona[yy2, xx] = int(dd.argmin())
    return tot


# ------------------------------------------------------------------ generatori
CD1 = os.path.join(RADICE, 'cd', 'd1', 'GRAPHIC')
DAT1 = os.path.join(RADICE, 'estratti', 'dat', 'd1', 'GRAPHIC')
LEGENDA = [(427, 'LEGENDA'), (439, 'TS - Tasto sinistro del mouse'), (450, 'TD - Tasto destro del mouse'),
           (466, "TS PER CAMBIARE SCHERMATA - ESC PER USCIRE DALL'AIUTO")]


def _sfondo():
    return np.load(os.path.join(RADICE, 'estratti', 'help_sfondo.npy'))


def genera_mouse():
    f = carica_font()
    bg = _sfondo()
    m = BM.load(os.path.join(CD1, 'OTHER', 'MOUSHELP.BM'), os.path.join(DAT1, 'PAL', 'MOUSHELP.PAL'))
    pulisci_testo(m, bg)
    Y = [151, 164, 183, 194, 214, 225, 243, 255, 268, 285, 297, 309, 326, 337, 348, 367, 378, 396, 409]
    X = [171, 171, 170, 171, 169, 169, 171, 171, 171, 171, 171, 171, 169, 169, 170, 171, 170, 171, 171]
    righe = [('Movimento', 'Fai clic col TS quando compare questo cursore'), (None, 'e Steve camminerà fino al punto indicato.'),
             ('Usa', 'Fai clic col TS mentre il cursore è'), (None, 'su un oggetto e Steve lo userà.'),
             ('Bersaglio', 'Fai clic col TD su un personaggio quando compare'), (None, 'questo cursore e Steve lo attaccherà.'),
             ('Prendi', 'Tieni premuto il TS mentre questo cursore'), (None, "è su un oggetto, trascina l'oggetto su Steve e poi"),
             (None, "rilascia il TS per metterlo nell'inventario di Steve."),
             ('Primo piano', 'Fai clic col TS mentre il cursore è'), (None, "sull'oggetto: l'oggetto verrà aggiunto automaticamente"),
             (None, "all'inventario di Steve."),
             ('Conversazione', 'Fai clic col TS mentre il cursore è su un personaggio'),
             (None, 'e Steve comincerà a parlare. Fai clic col TS sulle'),
             (None, 'risposte o sugli argomenti che compaiono nella conversazione.'),
             ('Esamina', 'Fai clic col TS quando compare questo cursore'), (None, 'su un oggetto e Steve lo osserverà.'),
             ('Esci', 'Fai clic col TS quando compare questo cursore'), (None, 'e Steve uscirà dalla stanza.')]
    for (term, txt), y, x in zip(righe, Y, X):
        riga(m.px, f, x, y, txt, term)
    for y, txt in LEGENDA:
        centra(m.px, f, y, txt)
    targa(m, 'COMANDI DEL MOUSE')
    return m


def font_titoli(k):
    """Glifi grandi di 'MOVEMENT' e 'COMBAT' (più una I disegnata)."""
    import fonthelp
    t = np.isin(k.px, (BIANCO, VERDE))
    g = {}
    for (a, b, x0, x1), testo in (((141, 152, 50, 140), 'MOVEMENT'), ((223, 234, 50, 120), 'COMBAT')):
        runs = fonthelp.segmenta(t, a, b, x0, x1)
        for (r0, r1), c in zip(runs, testo):
            g[c] = t[a:b, r0:r1].copy()
    h = g['M'].shape[0]
    g['I'] = np.ones((h, 1), bool)
    return g


def scrivi_titolo(px, g, x, y, testo):
    for c in testo:
        m = g[c]
        px[y:y + m.shape[0], x:x + m.shape[1]][m] = BIANCO
        x += m.shape[1] + 2
    return x


def genera_tastiera():
    f = carica_font()
    bg = _sfondo()
    pal = os.path.join(DAT1, 'PAL', 'KEYSHELP.PAL')
    orig = BM.load(os.path.join(CD1, 'OTHER', 'KEYSHELP.BM'), pal)
    k = BM.load(os.path.join(CD1, 'OTHER', 'KEYSHELP.BM'), pal)
    gt = font_titoli(orig)
    # via testo e tasti: si riparte dallo sfondo pulito
    k.px[135:425, 40:640] = bg[135:425, 40:640]
    k.px[425:480] = bg[425:480]
    diff = orig.px != bg

    def tasto(box, x, y):
        x0, y0, x1, y1 = box
        x0 -= 4; y0 -= 4; x1 += 4; y1 += 4
        sp = orig.px[y0:y1, x0:x1]
        mk = diff[y0:y1, x0:x1] & ~np.isin(sp, (BIANCO, VERDE))
        dx, dy = x - (box[0]), y - (box[1])
        z = k.px[y0 + dy:y1 + dy, x0 + dx:x1 + dx]
        z[mk] = sp[mk]
        return box[2] + dx

    DESTRA, SINISTRA, GIU, SU = (89, 155, 116, 179), (89, 185, 116, 209), (241, 155, 268, 179), (241, 185, 268, 209)
    CTRL = [(89, 237, 130, 261), (89, 267, 130, 291), (89, 297, 130, 321)]
    FRECCE_C = [(144, 237, 171, 261), (144, 267, 171, 291), (144, 297, 171, 321)]
    FR_O = (189, 297, 216, 321)
    ALT, SHIFT = (89, 327, 130, 351), (89, 357, 130, 381)
    scrivi_titolo(k.px, gt, 56, 141, 'MOVIMENTO')
    scrivi_titolo(k.px, gt, 56, 223, 'COMBATTIMENTO')
    # movimento: due colonne
    t1 = ('per andare a destra.', 'per andare a sinistra.')
    t2 = ('per andare avanti.', 'per andare indietro.')
    for (y, ky), a in zip(((163, 155), (193, 185)), t1):
        scrivi(k.px, f, 56, y, 'Premi')
        scrivi(k.px, f, 121, y, a)
    fine = max(121 + larghezza(f, a) for a in t1)
    c2 = max(208, fine + 22)
    tasto(DESTRA, 89, 155)
    tasto(SINISTRA, 89, 185)
    kx = c2 + larghezza(f, 'Premi') + 5
    for (y, box), b in zip(((163, GIU), (193, SU)), t2):
        scrivi(k.px, f, c2, y, 'Premi')
        e = tasto(box, kx, box[1])
        scrivi(k.px, f, e + 6, y, b)
    # combattimento
    testi = ['per un attacco alto.', 'per un attacco basso.']
    for i, y in enumerate((245, 275, 305)):
        scrivi(k.px, f, 57, y, 'Premi')
        tasto(CTRL[i], 89, CTRL[i][1])
        scrivi(k.px, f, 134, y, '+')
        tasto(FRECCE_C[i], 144, FRECCE_C[i][1])
        if i < 2:
            scrivi(k.px, f, 175, y, testi[i])
    scrivi(k.px, f, 177, 305, 'o')
    tasto(FR_O, 189, 297)
    scrivi(k.px, f, 220, 305, "(dove è rivolto Steve) per un attacco medio.")
    scrivi(k.px, f, 57, 335, 'Premi')
    tasto(ALT, 89, 327)
    scrivi(k.px, f, 134, 335, 'per abbassarti.')
    scrivi(k.px, f, 57, 365, 'Premi')
    tasto(SHIFT, 89, 357)
    scrivi(k.px, f, 134, 365, 'per far correre Steve.')
    for y, txt in LEGENDA:
        centra(k.px, f, y, txt)
    targa(k, 'COMANDI DA TASTIERA')
    return k


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RADICE, 'build', 'grafica')
    os.makedirs(out, exist_ok=True)
    for nome, fn in (('MOUSHELP', genera_mouse), ('KEYSHELP', genera_tastiera)):
        img = fn()
        open(os.path.join(out, nome + '.BM'), 'wb').write(img.dump())
        img.png(os.path.join(out, nome + '.png'))
        print('scritto', nome)
