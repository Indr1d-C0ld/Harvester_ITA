"""Strumenti per tradurre la grafica: immagini .BM con la loro tavolozza,
scritte ridisegnate con i font del gioco (.CFT) o con font TrueType."""
import os, sys, struct
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cft as _cft
from bm import read_pal

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(RADICE, 'cd', 'd1', 'GRAPHIC', 'FONT')


class BM:
    def __init__(self, data, pal):
        self.hdr = data[:12]
        w, h = struct.unpack_from('<II', data, 0)
        self.px = np.frombuffer(data[12:12 + w * h], dtype=np.uint8).reshape(h, w).copy()
        self.coda = data[12 + w * h:]
        self.pal = np.array(pal, dtype=np.int32).reshape(256, 3)

    @classmethod
    def load(cls, path, pal_path):
        return cls(open(path, 'rb').read(), read_pal(open(pal_path, 'rb').read()))

    def dump(self):
        h, w = self.px.shape
        hdr = bytearray(self.hdr)
        struct.pack_into('<II', hdr, 0, w, h)
        return bytes(hdr) + self.px.tobytes() + self.coda

    def png(self, path, scala=1):
        im = Image.fromarray(self.px, 'P')
        im.putpalette(self.pal.astype(np.uint8).flatten().tolist())
        if scala != 1:
            im = im.resize((im.width * scala, im.height * scala), Image.NEAREST)
        im.convert('RGB').save(path)

    def riempi(self, x0, y0, x1, y1, indice):
        self.px[y0:y1, x0:x1] = indice

    def vicino(self, rgb, ammessi=None):
        """Indice di tavolozza più vicino a un colore RGB (eventualmente tra gli ammessi)."""
        idx = np.arange(256) if ammessi is None else np.array(sorted(ammessi))
        d = ((self.pal[idx] - np.array(rgb)) ** 2).sum(1)
        return int(idx[d.argmin()])


def font(nome):
    return _cft.CFT.load(os.path.join(FONT_DIR, nome))


def rendi_cft(f, testo, spazio=1):
    """Matrice di indici (0 = trasparente) del testo nel font del gioco."""
    glifi = []
    for ch in testo:
        c = ord(ch)
        if ch == ' ':
            glifi.append(np.zeros((f.bh, f.space), dtype=np.uint8))
            continue
        if not f.width[c]:
            raise ValueError(f'carattere {ch!r} assente nel font')
        g = np.array([list(r) for r in f.glyph(c)], dtype=np.uint8)
        glifi.append(g)
    parti = []
    for k, g in enumerate(glifi):
        parti.append(g)
        if k < len(glifi) - 1 and spazio:
            parti.append(np.zeros((f.bh, spazio), dtype=np.uint8))
    return np.hstack(parti) if parti else np.zeros((f.bh, 0), dtype=np.uint8)


def incolla(img, m, x, y, mappa=None):
    """Copia i pixel non trasparenti di m in img a (x, y); mappa: dict indice->indice."""
    h, w = m.shape
    zona = img.px[y:y + h, x:x + w]
    mm = m[:zona.shape[0], :zona.shape[1]]
    if mappa:
        mm = np.vectorize(lambda v: mappa.get(int(v), int(v)))(mm).astype(np.uint8)
    zona[mm != 0] = mm[mm != 0]


def trova_testo(img, m, zona):
    """Cerca la posizione esatta di m dentro zona=(x0,y0,x1,y1) di img; None se non c'è."""
    x0, y0, x1, y1 = zona
    h, w = m.shape
    maschera = m != 0
    for y in range(y0, y1 - h + 1):
        for x in range(x0, x1 - w + 1):
            if np.array_equal(img.px[y:y + h, x:x + w][maschera], m[maschera]):
                return x, y
    return None


def testo_ttf(img, box, testo, ttf, size, rgb, allinea='centro', ammessi=None, ombra=None, dy=0):
    """Disegna testo TrueType antialiasato dentro box, riportando i colori alla tavolozza.
    I pixel di sfondo restano quelli dell'immagine."""
    x0, y0, x1, y1 = box
    sub = img.px[y0:y1, x0:x1]
    rgbimg = img.pal[sub].astype(np.uint8)
    pil = Image.fromarray(rgbimg, 'RGB')
    d = ImageDraw.Draw(pil)
    fnt = ImageFont.truetype(ttf, size)
    bb = d.textbbox((0, 0), testo, font=fnt)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    W, H = x1 - x0, y1 - y0
    if allinea == 'centro':
        tx = (W - tw) // 2 - bb[0]
    elif allinea == 'sinistra':
        tx = -bb[0]
    else:
        tx = W - tw - bb[0]
    ty = (H - th) // 2 - bb[1] + dy
    if ombra:
        d.text((tx + 1, ty + 1), testo, font=fnt, fill=tuple(ombra))
    d.text((tx, ty), testo, font=fnt, fill=tuple(rgb))
    nuovo = np.array(pil).astype(np.int32)
    cambiati = (nuovo != rgbimg).any(2)
    idx = np.arange(256) if ammessi is None else np.array(sorted(ammessi))
    palx = img.pal[idx]
    for (yy, xx) in zip(*np.nonzero(cambiati)):
        dd = ((palx - nuovo[yy, xx]) ** 2).sum(1)
        sub[yy, xx] = idx[dd.argmin()]
    return tw, th


MONO = '/usr/share/fonts/opentype/urw-base35/NimbusMonoPS-Regular.otf'


def testo_1bit(img, box, testo, indice, ttf=MONO, size=15, allinea='centro', sfondo=None, dy=0, dx=0):
    """Testo senza antialias in un solo indice di colore (come le etichette originali).
    sfondo: indice con cui ripulire prima il box (None = non ripulire)."""
    x0, y0, x1, y1 = box
    if sfondo is not None:
        img.px[y0:y1, x0:x1] = sfondo
    fnt = ImageFont.truetype(ttf, size)
    W, H = x1 - x0, y1 - y0
    im = Image.new('1', (W, H), 0)
    d = ImageDraw.Draw(im)
    d.fontmode = '1'
    bb = d.textbbox((0, 0), testo, font=fnt)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    tx = {'centro': (W - tw) // 2, 'sinistra': 0, 'destra': W - tw}[allinea] - bb[0] + dx
    ty = (H - th) // 2 - bb[1] + dy
    d.text((tx, ty), testo, font=fnt, fill=1)
    a = np.array(im)
    img.px[y0:y1, x0:x1][a] = indice
    return tw


def riempi_trama(img, maschera, raggio=4, seme=1):
    """Riempie i pixel della maschera dall'esterno verso l'interno, copiando pixel noti
    vicini scelti a caso: conserva la grana della carta meglio di un ritocco liscio."""
    rng = np.random.default_rng(seme)
    da_fare = maschera.copy()
    h, w = da_fare.shape
    while da_fare.any():
        noto = ~da_fare
        # pixel da fare con almeno un vicino noto (bordo)
        k = np.ones((3, 3), np.uint8)
        bordo = da_fare & (cv2.dilate(noto.astype(np.uint8), k).astype(bool))
        ys, xs = np.nonzero(bordo)
        if len(ys) == 0:
            break
        for y, x in zip(ys, xs):
            for _ in range(60):
                dy, dx = rng.integers(-raggio, raggio + 1, 2)
                yy, xx = y + dy, x + dx
                if 0 <= yy < h and 0 <= xx < w and noto[yy, xx]:
                    img.px[y, x] = img.px[yy, xx]
                    break
        da_fare[ys, xs] = False
    return img


def testo_aa(img, x, y, testo, ttf, size, rgb, ammessi, ancora='la', spaziatura=0, scala_x=1.0, usura=0.0, seme=7):
    """Testo TrueType antialiasato (supercampionato) mescolato sullo sfondo e riportato
    agli indici ammessi. (x, y) secondo 'ancora' di PIL. Restituisce il riquadro (x0,y0,x1,y1)."""
    S = 4
    fnt = ImageFont.truetype(ttf, size * S)
    tmp = Image.new('L', (1, 1))
    d = ImageDraw.Draw(tmp)
    # larghezza con spaziatura
    lw = [d.textlength(c, font=fnt) for c in testo]
    tot = sum(lw) + spaziatura * S * (len(testo) - 1)
    bb = d.textbbox((0, 0), testo, font=fnt, anchor='ls')
    H = (bb[3] - bb[1]) + 8 * S
    W = int(tot + 8 * S)
    lay = Image.new('L', (W, H), 0)
    dl = ImageDraw.Draw(lay)
    cx = 4 * S
    base = -bb[1] + 4 * S
    for c, l in zip(testo, lw):
        dl.text((cx, base), c, font=fnt, fill=255, anchor='ls')
        cx += l + spaziatura * S
    if scala_x != 1.0:
        lay = lay.resize((int(W * scala_x), H), Image.LANCZOS)
        W = lay.width
    lay = lay.resize((max(1, W // S), max(1, H // S)), Image.LANCZOS)
    a = np.array(lay).astype(float) / 255
    if usura:
        rng = np.random.default_rng(seme)
        a = a * (1 - usura * rng.random(a.shape))
    hh, ww = a.shape
    tw = (tot * scala_x) / S
    if ancora[0] == 'm':
        x0 = int(round(x - tw / 2)) - 4
    elif ancora[0] == 'r':
        x0 = int(round(x - tw)) - 4
    else:
        x0 = int(x) - 4
    y0 = int(y) - (base // S)
    idx = np.array(sorted(ammessi))
    palx = img.pal[idx].astype(float)
    for yy in range(hh):
        for xx in range(ww):
            al = a[yy, xx]
            if al < 0.06:
                continue
            Y, X = y0 + yy, x0 + xx
            if not (0 <= Y < img.px.shape[0] and 0 <= X < img.px.shape[1]):
                continue
            src = img.pal[img.px[Y, X]].astype(float)
            col = src * (1 - al) + np.array(rgb, float) * al
            img.px[Y, X] = idx[((palx - col) ** 2).sum(1).argmin()]
    return x0, y0, x0 + ww, y0 + hh


def testo_ruotato(img, x, y, testo, ttf, size, rgb, ammessi, angolo=0.0, scala_x=1.0, usura=0.0, seme=7, ancora='ls'):
    """Come testo_aa ma ruotato di `angolo` gradi (positivo = antiorario) attorno al punto
    (x, y), che è l'inizio della linea di base ('ls') o il suo centro ('ms')."""
    S = 4
    fnt = ImageFont.truetype(ttf, size * S)
    d = ImageDraw.Draw(Image.new('L', (1, 1)))
    w = d.textlength(testo, font=fnt)
    asc, desc = fnt.getmetrics()
    R = int(w * scala_x + asc + desc) + 8 * S
    extra = int(size * S * 0.35)          # spazio per gli accenti sulle maiuscole
    R += extra
    lay = Image.new('L', (2 * R, 2 * R), 0)
    tmp = Image.new('L', (int(w) + 4 * S, asc + desc + 4 * S + extra), 0)
    ImageDraw.Draw(tmp).text((2 * S, 2 * S + asc + extra), testo, font=fnt, fill=255, anchor='ls')
    if scala_x != 1.0:
        tmp = tmp.resize((max(1, int(tmp.width * scala_x)), tmp.height), Image.LANCZOS)
    ox = R - 2 * S if ancora[0] == 'l' else R - tmp.width // 2
    lay.paste(tmp, (ox, R - (2 * S + asc + extra)))
    lay = lay.rotate(angolo, resample=Image.BICUBIC, center=(R, R))
    lay = lay.resize((2 * R // S, 2 * R // S), Image.LANCZOS)
    a = np.array(lay).astype(float) / 255
    if usura:
        a = a * (1 - usura * np.random.default_rng(seme).random(a.shape))
    x0, y0 = int(round(x - R / S)), int(round(y - R / S))
    idx = np.array(sorted(ammessi))
    palx = img.pal[idx].astype(float)
    for yy, xx in zip(*np.nonzero(a >= 0.06)):
        Y, X = y0 + yy, x0 + xx
        if 0 <= Y < img.px.shape[0] and 0 <= X < img.px.shape[1]:
            al = a[yy, xx]
            col = img.pal[img.px[Y, X]].astype(float) * (1 - al) + np.array(rgb, float) * al
            img.px[Y, X] = idx[((palx - col) ** 2).sum(1).argmin()]
