"""Grafica d'interfaccia tradotta: inventario, salvataggio/caricamento, riquadri,
richiesta dei CD, attesa. Ogni funzione restituisce l'oggetto BM/ABM modificato."""
import os, sys
import numpy as np
import cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grafica import BM, riempi_trama, testo_aa, testo_1bit

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = '/usr/share/fonts/opentype/urw-base35/'
BOOKMAN = FONTS + 'URWBookman-Demi.otf'
VERDE_SCURO = (38, 62, 30)


def dat(disco, *p):
    return os.path.join(RADICE, 'estratti', 'dat', disco, 'GRAPHIC', *p)


def cancella(img, boxes, soglia=195, dil=2, raggio=7):
    """Cancella il testo scuro dentro i box riempiendo con la trama vicina."""
    rgb = img.pal[img.px]
    mask = np.zeros(img.px.shape, bool)
    for x0, y0, x1, y1 in boxes:
        sub = rgb[y0:y1, x0:x1]
        mask[y0:y1, x0:x1] |= sub[..., 0] < soglia
    mask = cv2.dilate(mask.astype(np.uint8), np.ones((dil * 2 + 1, dil * 2 + 1), np.uint8)).astype(bool)
    lim = np.zeros_like(mask)
    for x0, y0, x1, y1 in boxes:
        lim[y0 - dil:y1 + dil, x0 - dil:x1 + dil] = True
    riempi_trama(img, mask & lim, raggio=raggio)


def adatta(testo, ttf, size, larg_max):
    """Fattore di compressione orizzontale perché il testo stia in larg_max pixel."""
    from PIL import ImageFont, ImageDraw, Image
    f = ImageFont.truetype(ttf, size)
    w = ImageDraw.Draw(Image.new('L', (1, 1))).textlength(testo, font=f)
    return min(1.0, larg_max / w)


def intestazione_catalogo(img, scala=1.0, ox=0, oy=0):
    """Traduce l'intestazione 'Harvest Land' (inventario, 512x384; scala per INVHELP)."""
    s = scala
    B = lambda x0, y0, x1, y1: (int(ox + x0 * s), int(oy + y0 * s), int(ox + x1 * s) + 1, int(oy + y1 * s) + 1)
    cancella(img, [B(30, 5, 93, 17), B(414, 5, 499, 17), B(432, 25, 485, 43), B(163, 46, 361, 62)],
             raggio=max(3, int(7 * s)), dil=max(1, int(2 * s)))
    amm = set(np.unique(img.px).tolist())
    sz = max(7, int(round(12 * s)))
    for testo, x, y, lmax, size in (('25 CENT', 61, 15, 62, sz), ('PRIMAVERA 1953', 456, 15, 88, sz),
                                     ('ESCI', 458, 40, 60, int(round(16 * s))), ('MAGAZZINO DI MOBILI', 262, 60, 200, int(round(16 * s)))):
        k = adatta(testo, BOOKMAN, size, lmax * s)
        testo_aa(img, ox + x * s, oy + y * s, testo, BOOKMAN, size, VERDE_SCURO, amm, ancora='ms', scala_x=k)
    return img


def inventario(disco='d1'):
    img = BM.load(dat(disco, 'OTHER', 'INVENTRY.BM'), dat('d1', 'PAL', 'PCROOM.PAL'))
    return intestazione_catalogo(img)




# ------------------------------------------------------------------ etichette Courier
from grafica import font as font_cft, rendi_cft, incolla

COURIER_BOX = {'titolo': (4, 3, 636, 18), 'sx': (4, 461, 318, 477), 'dx': (322, 461, 636, 477)}


def salva(disco='d1'):
    img = BM.load(dat(disco, 'OTHER', 'SAVEGAME.BM'), dat(disco, 'PAL', 'SAVEGAME.PAL'))
    for k, t in (('titolo', 'SALVA PARTITA'), ('sx', 'SALVA'), ('dx', 'ANNULLA')):
        testo_1bit(img, COURIER_BOX[k], t, 15, sfondo=1)
    return img


def carica(disco='d1'):
    img = BM.load(dat(disco, 'OTHER', 'LOADGAME.BM'), dat(disco, 'PAL', 'LOADGAME.PAL'))
    sx = 'Scegli la partita da caricare' if disco == 'd1' else 'CARICA'
    for k, t in (('titolo', 'CARICA PARTITA'), ('sx', sx), ('dx', 'ANNULLA')):
        testo_1bit(img, COURIER_BOX[k], t, 15, sfondo=1)
    return img


def titolo_riquadro(nome, testo, disco='d1'):
    """TIPS.BM e KEYWORD.BM: titolo nel font del gioco (TEXTFONT) su fondo indice 3."""
    img = BM.load(dat(disco, 'OTHER', nome + '.BM'), dat('d1', 'PAL', 'PCROOM.PAL'))
    img.px[3:15, 4:302] = 3
    m = rendi_cft(font_cft('TEXTFONT.CFT'), testo, 1)
    x = (306 - m.shape[1]) // 2
    incolla(img, m, x, 4)
    return img


# ------------------------------------------------------------------ richiesta del CD
TIMES = FONTS + 'NimbusRoman-Regular.otf'


def maschera_rossa(img, box):
    x0, y0, x1, y1 = box
    rgb = img.pal[img.px[y0:y1, x0:x1]].astype(int)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    m = (r > 60) & (r > g + 45) & (r > b + 45) & (g < 90)
    out = np.zeros(img.px.shape, bool)
    out[y0:y1, x0:x1] = m
    return out


def ritocca(img, mask, raggio=4):
    """Ritocco liscio (OpenCV) riportato alla tavolozza dell'immagine."""
    rgb = img.pal[img.px].astype(np.uint8)
    m = cv2.dilate(mask.astype(np.uint8), np.ones((3, 3), np.uint8))
    out = cv2.inpaint(rgb, m, raggio, cv2.INPAINT_TELEA)
    usati = np.unique(img.px[m == 0])
    palu = img.pal[usati]
    ys, xs = np.nonzero(m)
    for y, x in zip(ys, xs):
        img.px[y, x] = usati[((palu - out[y, x].astype(int)) ** 2).sum(1).argmin()]


def richiesta_cd(n, disco='d1'):
    img = BM.load(dat(disco, 'OTHER', f'CD{n}.BM'), dat(disco, 'PAL', f'CD{n}.PAL'))
    mask = maschera_rossa(img, (10, 160, 230, 320)) | maschera_rossa(img, (10, 445, 640, 480))
    rgb = img.pal[img.px]
    colore = tuple(int(v) for v in np.median(rgb[mask], 0))
    ritocca(img, mask)
    amm = set(np.unique(img.px).tolist())
    for testo, y in (('Inserisci', 200), ('il CD', 248), (f'n. {n}', 296)):
        testo_aa(img, 112, y, testo, TIMES, 36, colore, amm, ancora='ms')
    t = 'FAI CLIC COL TASTO SINISTRO QUANDO SEI PRONTO'
    k = adatta(t, TIMES, 22, 600)
    testo_aa(img, 325, 471, t, TIMES, 22, colore, amm, ancora='ms', scala_x=k)
    return img


# ------------------------------------------------------------------ attesa (WAIT.ABM)
def attesa(disco='d1'):
    from abm import ABM
    from bm import read_pal
    a = ABM.load(dat(disco, 'OTHER', 'WAIT.ABM'))
    pal = np.array(read_pal(open(dat(disco, 'PAL', 'WAIT.PAL'), 'rb').read())).reshape(256, 3)
    f0 = a.frames[0]
    px0 = np.frombuffer(f0['px'], np.uint8).reshape(f0['h'], f0['w'])
    rgb = pal[px0]
    lum = rgb.max(2)
    righe = np.nonzero((lum[60:] > 60).any(1))[0] + 60
    # la scritta è l'ultima fascia di righe accese
    y1 = righe.max() + 1
    y0 = y1
    while y0 > 60 and (lum[y0 - 1] > 60).any():
        y0 -= 1
    testo_px = (lum[y0:y1] > 60)
    colore = tuple(int(v) for v in np.percentile(rgb[y0:y1][testo_px], 75, axis=0))
    fondo = int(np.bincount(px0[y0:y1].flatten()).argmax())
    import struct
    tmp = BM(struct.pack('<III', f0['w'], f0['h'], 0) + bytes(f0['w'] * f0['h']), pal.flatten().tolist())
    tmp.px[:] = px0
    tmp.px[y0 - 1:y1 + 1] = fondo
    amm = set(np.unique(px0).tolist())
    testo_aa(tmp, f0['w'] / 2, y1 - 4, 'Attendere...', FONTS + 'NimbusRoman-Bold.otf', 17, colore, amm, ancora='ms')
    nuova = tmp.px[y0 - 3:y1 + 3].copy()
    for f in a.frames:
        px = np.frombuffer(f['px'], np.uint8).reshape(f['h'], f['w']).copy()
        px[y0 - 3:y1 + 3] = nuova
        f['px'] = px.tobytes()
    return a, (y0, y1)


# ------------------------------------------------------------------ censura (PCX)
def pcx_rle(px):
    out = bytearray()
    for riga in px:
        i = 0
        n = len(riga)
        while i < n:
            v = riga[i]
            j = i
            while j < n and riga[j] == v and j - i < 63:
                j += 1
            c = j - i
            if c > 1 or v >= 0xC0:
                out += bytes([0xC0 | c, v])
            else:
                out.append(v)
            i = j
    return bytes(out)


def censura(disco='d1'):
    from PIL import Image, ImageDraw, ImageFont
    p = dat(disco, 'OTHER', 'CENSORED.PCX')
    raw = open(p, 'rb').read()
    a = np.array(Image.open(p)).copy()
    a[60:130, 10:310] = 0
    for testo, y, size in (('Filmato censurato', 92, 17), ('Attiva il sangue nelle opzioni per vederlo', 113, 13)):
        S = 4
        fnt = ImageFont.truetype(FONTS + 'NimbusRoman-Bold.otf', size * S)
        lay = Image.new('L', (320 * S, 200 * S), 0)
        d = ImageDraw.Draw(lay)
        d.text((160 * S, y * S), testo, font=fnt, fill=255, anchor='ms')
        al = np.array(lay.resize((320, 200), Image.LANCZOS)).astype(float) / 255
        for soglia, val in ((0.75, 75), (0.5, 154), (0.3, 132), (0.12, 73)):
            sel = (al >= soglia) & (a == 0)
            a[sel] = val
    # La tavolozza in coda (0x0C + 768 byte) serve: il gioco carica il file sciolto
    # del CD, che ce l'ha, mentre la copia in HARVEST.DAT da cui partiamo no.
    sciolto = open(os.path.join(RADICE, 'cd', disco, 'GRAPHIC', 'OTHER', 'CENSORED.PCX'), 'rb').read()
    if sciolto[-769] != 0x0C:
        raise ValueError('CENSORED.PCX del CD senza tavolozza in coda')
    return raw[:128] + pcx_rle(a) + sciolto[-769:]


def genera_tutto(out):
    os.makedirs(out, exist_ok=True)
    risultati = {}
    for nome, fn in (('INVENTRY', inventario), ('SAVEGAME', salva), ('LOADGAME', carica),
                     ('TIPS', lambda: titolo_riquadro('TIPS', 'SUGGERIMENTI DI GIOCO')),
                     ('KEYWORD', lambda: titolo_riquadro('KEYWORD', 'Argomenti')),
                     ('CD1', lambda: richiesta_cd(1)), ('CD2', lambda: richiesta_cd(2)), ('CD3', lambda: richiesta_cd(3))):
        img = fn()
        img.png(os.path.join(out, nome + '.png'))
        open(os.path.join(out, nome + '.BM'), 'wb').write(img.dump())
        risultati[nome] = img.dump()
    img = carica('d3')
    img.png(os.path.join(out, 'LOADGAME_d3.png'))
    open(os.path.join(out, 'LOADGAME_d3.BM'), 'wb').write(img.dump())
    a, _ = attesa()
    open(os.path.join(out, 'WAIT.ABM'), 'wb').write(a.dump())
    open(os.path.join(out, 'CENSORED.PCX'), 'wb').write(censura())
    print('grafica d\'interfaccia scritta in', out)


if __name__ == '__main__':
    genera_tutto(os.path.join(RADICE, 'build', 'grafica'))
