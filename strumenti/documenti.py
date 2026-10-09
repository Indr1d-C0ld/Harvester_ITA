"""Documenti di gioco tradotti (primi piani a schermo intero).

Ogni documento: si cancellano le righe di testo (conservando le linee del modulo e
i segni a penna che non sono parole), poi si ribatte l'italiano con un font da
macchina da scrivere o manoscritto, mescolato sulla carta e riportato alla
tavolozza originale."""
import os, sys
import numpy as np
import cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grafica import BM, riempi_trama, testo_aa

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'font')
MACCHINA = os.path.join(FONT, 'SpecialElite-Regular.ttf')
PENNA = os.path.join(FONT, 'Caveat[wght].ttf')
PENNA2 = os.path.join(FONT, 'ReenieBeanie.ttf')


def dat(disco, *p):
    return os.path.join(RADICE, 'estratti', 'dat', disco, 'GRAPHIC', *p)


def carica(nome, disco='d1', pal=None):
    return BM.load(dat(disco, 'ROOMS', nome + '.BM'), dat(disco, 'PAL', (pal or nome) + '.PAL'))


class Doc:
    def __init__(self, img):
        self.img = img
        self.rgb = img.pal[img.px].astype(int)
        self.amm = set(np.unique(img.px).tolist())

    def lum(self):
        return self.img.pal[self.img.px].astype(int).mean(2)

    def cancella_scritte(self, box, soglia=200, linee=30, colore=None, dil=1, raggio=3, carta=None):
        """Cancella i pixel scuri (o del colore dato) nel box, salvo le linee orizzontali
        lunghe almeno `linee` pixel."""
        x0, y0, x1, y1 = box
        rgb = self.img.pal[self.img.px[y0:y1, x0:x1]].astype(int)
        if colore == 'blu':
            m = (rgb[..., 2] > rgb[..., 0] + 25) & (rgb[..., 2] > 90)
        else:
            blu = (rgb[..., 2] > rgb[..., 0] + 25) & (rgb[..., 2] > 90)
            m = (rgb.mean(2) < soglia) & ~blu
        if linee:
            keep = np.zeros_like(m)
            for y in range(m.shape[0]):
                riga = m[y]
                x = 0
                while x < len(riga):
                    if riga[x]:
                        a = x
                        while x < len(riga) and riga[x]:
                            x += 1
                        if x - a >= linee:
                            keep[y, a:x] = True
                    x += 1
            m &= ~keep
        mask = np.zeros(self.img.px.shape, bool)
        mask[y0:y1, x0:x1] = m
        if dil:
            mask = cv2.dilate(mask.astype(np.uint8), np.ones((2 * dil + 1, 2 * dil + 1), np.uint8)).astype(bool)
            lim = np.zeros_like(mask)
            lim[y0:y1, x0:x1] = True
            if linee:
                lim[y0:y1, x0:x1] &= ~keep
            mask &= lim
        carta = carta or getattr(self, 'carta', None)
        if carta:
            cx0, cy0, cx1, cy1 = carta
            campione = self.img.px[cy0:cy1, cx0:cx1].flatten()
            rng = np.random.default_rng(int(mask.sum()))
            self.img.px[mask] = rng.choice(campione, int(mask.sum()))
        else:
            riempi_trama(self.img, mask, raggio=raggio)

    def scrivi(self, x, y, testo, ttf=MACCHINA, size=11, rgb=(55, 55, 55), ancora='ls', larg=None, sp=0, usura=None):
        k = 1.0
        if larg:
            from PIL import ImageFont, ImageDraw, Image
            f = ImageFont.truetype(ttf, size)
            w = ImageDraw.Draw(Image.new('L', (1, 1))).textlength(testo, font=f) + sp * (len(testo) - 1)
            k = min(1.0, larg / w)
        if usura is None:
            usura = 0.45 if ttf == MACCHINA else 0.15
        self.seme = getattr(self, 'seme', 0) + 1
        return testo_aa(self.img, x, y, testo, ttf, size, rgb, self.amm, ancora=ancora, scala_x=k, spaziatura=sp,
                        usura=usura, seme=self.seme)


# ------------------------------------------------------------------ domanda di ammissione
LODG_TESTI = [
    # (y base, x, testo, ancora, larghezza massima)
    (52, 322, "La Sala dell'Ordine della Luna del Raccolto", 'ms', 200),
    (70, 298, 'DOMANDA DI AMMISSIONE', 'ms', 110),
    (96, 171, 'Quante volte mangi carne? *', 'ls', 110),
    (112, 171, 'Nome', 'ls', None),
    (130, 171, 'Secondo nome', 'ls', 74),
    (148, 171, 'Cognome', 'ls', 36),
    (165, 171, 'Via', 'ls', None),
    (183, 171, 'Città', 'ls', None),
    (190, 171, 'Stato', 'ls', None),
    (202, 268, 'CAP', 'ls', None),
    (217, 169, 'Hai disabilità fisiche che ti impediscano di', 'ls', 296),
    (227, 169, 'mangiare carne?', 'ls', 78),
    (245, 172, 'Hai un triciclo?', 'ls', 98),
    (263, 169, "Ti piace l'arte del 'guardare la gente'?", 'ls', 188),
    (280, 169, 'Sai salire sulla fune?', 'ls', 100),
    (298, 168, 'Sei allergico a una di queste cose (cerchiare):', 'ls', 240),
    (366, 168, 'Hai mai avuto la pneumoultramicroscopicosilicovulcanoconiosi?', 'ls', 290),
    (393, 168, 'In 50 parole o meno, spiega perché saresti utile al nostro Ordine:', 'ls', 290),
    (463, 170, 'AVVISO: ogni candidato sarà informato subito della sua sorte', 'ls', 296),
]
# Sì / No / (cerchiare) nelle stesse posizioni di Yes / No / (circle one): i cerchi a penna restano giusti
LODG_SINO = [(227, 253, 275, 294), (245, 276, 301, 321), (263, 364, 390, 413), (280, 276, 301, 325), (375, 208, 233, 252)]
LODG_ELENCO = [
    (212, 84, ['cuoio', 'CARNE', 'semi', 'violette', 'seni']),
    (301, 100, ['polvere da sparo', 'armadilli', 'miscela per motosega', 'carne', 'indiani Hopi']),
    (406, 76, ['estrogeni', 'mutande di cotone', 'plasma', 'Nuovo Ordine Mond.', 'lattice']),
]
LODG_Y_ELENCO = [315, 324, 333, 341, 350]


def domanda(compilata=False):
    nome = 'LODGAPP2' if compilata else 'LODGAPP1'
    d = Doc(carica(nome))
    if compilata:
        # parole a penna (non i cerchi né i punti di domanda)
        for box in ((248, 82, 420, 100), (205, 100, 290, 112), (330, 117, 480, 133), (205, 168, 290, 182),
                    (300, 368, 498, 385), (170, 400, 470, 460)):
            d.cancella_scritte(box, colore='blu', linee=40, dil=1)
    # testo battuto a macchina: tutte le fasce
    for box in ((225, 44, 420, 56), (245, 62, 352, 72), (168, 87, 284, 99), (168, 105, 216, 113), (168, 122, 248, 131),
                (168, 140, 209, 149), (168, 157, 196, 166), (168, 174, 196, 192), (255, 195, 305, 204),
                (166, 209, 470, 229), (168, 236, 375, 247), (166, 253, 466, 265), (166, 271, 378, 282),
                (166, 288, 408, 300), (210, 306, 475, 352), (166, 358, 443, 377), (166, 384, 460, 395),
                (166, 453, 470, 466)):
        d.cancella_scritte(box, linee=30)
    for y, x, t, a, larg in LODG_TESTI:
        d.scrivi(x, y, t, size=10, ancora=a, larg=larg)
    for y, xs, xn, xc in LODG_SINO:
        d.scrivi(xs, y, 'Sì', size=10)
        d.scrivi(xn, y, 'No', size=10)
        d.scrivi(xc, y, '(cerchiare)', size=10, larg=52)
    for x, larg, voci in LODG_ELENCO:
        for y, v in zip(LODG_Y_ELENCO, voci):
            d.scrivi(x, y - (1 if v.startswith('Nuovo') else 0), v, size=10 if larg > 80 else 9, larg=larg)
    if compilata:
        blu = (60, 90, 170)
        d.scrivi(288, 95, '3 volte al giorno', ttf=PENNA, size=18, rgb=blu, larg=130)
        d.scrivi(222, 110, 'Steve', ttf=PENNA, size=17, rgb=blu)
        d.scrivi(330, 130, 'Nessuno me lo dice', ttf=PENNA, size=17, rgb=blu, larg=150)
        d.scrivi(206, 179, 'HARVEST', ttf=PENNA, size=15, rgb=blu)
        d.scrivi(304, 381, 'Non so nemmeno cosa sia!', ttf=PENNA, size=16, rgb=blu, larg=190)
        for y, t in ((409, 'Credo di poter essere utile lavorando sodo e'), (418, 'tutti pensano che sarei perfetto per'),
                     (427, 'la Loggia.'), (446, 'P.S. Sono molto bravo con le mani.')):
            d.scrivi(173, y, t, ttf=PENNA, size=14, rgb=blu, larg=285)
    return d.img


def ricetta(nome, cancella, scritte, disco='d1', pal=None, size=12, rgb=(45, 45, 45), ttf=MACCHINA, carta=None, linee=80):
    """cancella: lista di box (o (box, opzioni)); scritte: (x, y_base, testo, ancora, larghezza_max[, opzioni]).
    carta: box di carta pulita da cui campionare il riempimento (None = trama dei vicini)."""
    d = Doc(carica(nome, disco, pal))
    d.carta = carta
    for c in cancella:
        if isinstance(c[0], tuple):
            d.cancella_scritte(c[0], **c[1])
        else:
            d.cancella_scritte(c, linee=linee)
    for w in scritte:
        x, y, t, a, larg = w[:5]
        op = dict(size=size, rgb=rgb, ttf=ttf)
        if len(w) > 5:
            op.update(w[5])
        d.scrivi(x, y, t, ancora=a, larg=larg, **op)
    return d.img


PERMESSO_CANC = [(100, 142, 530, 159), (44, 172, 620, 222), (40, 236, 396, 254), (390, 236, 580, 254),
                 (100, 255, 320, 271), (38, 284, 152, 303), (436, 284, 548, 303), (210, 303, 310, 321), (38, 332, 392, 350)]
PERMESSO_SCR = [
    (313, 155, '*Modulo ufficiale di cessione carne - MR-8231-b, Sezione A*', 'ms', 500),
    (50, 187, 'Avviso: in nessun caso i soggetti NON MENZIONATI in questo', 'ls', 560),
    (115, 203, "modulo come 'destinatari' possono ricevere prodotti", 'ls', 495),
    (115, 218, 'della HARVEST MEATS, Inc.', 'ls', None),
    (42, 251, 'Io,', 'ls', None),
    (397, 251, 'concedo il mio pieno', 'ls', 178),
    (210, 268, '(firma del dipendente HMI)', 'ms', 200),
    (42, 300, 'permetto a', 'ls', 108),
    (469, 300, 'di ricevere un', 'ls', 76),
    (261, 317, '(destinatario)', 'ms', None),
    (43, 346, 'prodotto di III CATEGORIA della HARVEST MEATS, Inc.', 'ls', 440),
]


SERIF = '/usr/share/fonts/opentype/urw-base35/NimbusRoman-Bold.otf'
SERIF_R = '/usr/share/fonts/opentype/urw-base35/NimbusRoman-Regular.otf'
CORSIVO = os.path.join(FONT, 'HomemadeApple-Regular.ttf')


def cassaforte():
    d = Doc(carica('SAFEBOOK'))
    d.carta = (200, 300, 430, 340)
    # 'Your Safe Combination is:' e 'User Manual' (la marca e il modello restano)
    for box in ((240, 240, 410, 258), (280, 388, 380, 405), (255, 116, 345, 129)):
        d.cancella_scritte(box, linee=0, soglia=150, dil=1)
    d.scrivi(320, 254, 'La combinazione della cassaforte è:', ttf=SERIF, size=12, rgb=(40, 30, 35), ancora='ms', larg=190, usura=0)
    d.scrivi(330, 402, "Manuale d'uso", ttf=SERIF_R, size=14, rgb=(40, 30, 35), ancora='ms', usura=0)
    d.scrivi(306, 127, 'MODELLO:', ttf=SERIF, size=12, rgb=(40, 30, 35), ancora='ms', usura=0)
    return d.img


def turni():
    from grafica import testo_ruotato
    d = Doc(carica('SCHEDULE'))
    x0, y0, x1, y1 = 205, 94, 476, 286
    rgb = d.img.pal[d.img.px[y0:y1, x0:x1]].astype(int)
    sat = rgb.max(2) - rgb.min(2)
    blu = (rgb[..., 2] > rgb[..., 0] + 20)
    m = (rgb.mean(2) < 178) & (sat < 45) & ~blu
    mask = np.zeros(d.img.px.shape, bool)
    mask[y0:y1, x0:x1] = m
    mask = cv2.dilate(mask.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    lim = np.zeros_like(mask)
    lim[y0:y1, x0:x1] = True
    # inizio del titolo accanto al fermaglio
    sub = d.img.pal[d.img.px[84:100, 205:250]].astype(int)
    mask[84:100, 205:250] |= (sub.mean(2) < 178) & ((sub.max(2) - sub.min(2)) < 45)
    lim[84:100, 205:250] = True
    riempi_trama(d.img, mask & lim, raggio=5)
    inch = (40, 35, 45)
    testo_ruotato(d.img, 336, 117, 'POLIZIA DI HARVEST', SERIF, 18, inch, d.amm, angolo=-5.8, ancora='ms')
    testo_ruotato(d.img, 336, 131, 'Turni di pattuglia notturni', SERIF_R, 15, inch, d.amm, angolo=-5.8, ancora='ms')
    righe = [('00:00 - 00:59 : Caserma dei pompieri', 222, 144), ('01:00 - 01:59 : Tavola calda di Edna', 219, 168),
             ('02:00 - 02:59 : Casa Johnson', 216, 192), ('03:00 - 03:59 : Ufficio postale / Barbiere Pastorelli', 213, 216),
             ('04:00 - 04:59 : Emporio Phelps', 211, 240), ('05:00 - 05:59 : Posto di comando', 208, 264)]
    for t, x, y in righe:
        k = min(1.0, 250 / (len(t) * 5.3))
        testo_ruotato(d.img, x, y, t, SERIF_R, 11, inch, d.amm, angolo=-5.5, scala_x=k)
    return d.img


def biglietto_boyle(copia=False):
    nome = 'BOYLCOPY' if copia else 'BOYLNOTE'
    d = Doc(carica(nome))
    d.carta = None
    ox, oy = (55, -5) if copia else (0, 0)
    x0, y0, x1, y1 = (138 + ox, 112 + oy, 458 + ox, 334 + oy)
    rgb = d.img.pal[d.img.px[y0:y1, x0:x1]].astype(int)
    m = (rgb.mean(2) < (92 if copia else 150)) & ((rgb.max(2) - rgb.min(2)) < 60)
    if copia:
        # nella fotocopia la macchia di caffè è grigia: si risparmia l'anello salvo l'inchiostro più nero
        yy, xx = np.mgrid[y0:y1, x0:x1]
        r = np.hypot(xx - 397, yy - 333)
        anello = (r > 50) & (r < 80)
        m &= ~anello | (rgb.mean(2) < 52)
    mask = np.zeros(d.img.px.shape, bool)
    mask[y0:y1, x0:x1] = m
    mask = cv2.dilate(mask.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    lim = np.zeros_like(mask)
    lim[y0:y1, x0:x1] = True
    riempi_trama(d.img, mask & lim, raggio=5)
    inchiostro = (35, 35, 45)
    for x, y, t, sz in ((144, 150, 'Sceriffo,', 17), (168, 190, 'se credi che continuerò', 16),
                        (140, 230, 'a pagarti per sempre,', 16), (176, 270, 'sei PAZZO.', 16),
                        (146, 310, "C'è un", 16)):
        d.scrivi(x + ox, y + oy, t, ttf=CORSIVO, size=sz, rgb=inchiostro, usura=0.1, larg=295)
    x0, y0, x1, y1 = d.scrivi(238 + ox, 311 + oy, 'LIMITE!', ttf=PENNA, size=24, rgb=inchiostro, usura=0.05)
    from grafica import testo_aa
    testo_aa(d.img, 240 + ox, 316 + oy, '_' * 6, PENNA, 24, inchiostro, d.amm, ancora='ls', scala_x=0.95)
    return d.img


def indizio():
    d = Doc(carica('CLUE', 'd3'))
    rgb = d.img.pal[d.img.px].astype(int)
    # inchiostro blu scuro (le righe del quaderno sono più chiare: R >= 120)
    mask = (rgb[..., 2] > rgb[..., 0] + 30) & (rgb[..., 0] < 115)
    mask[:138] = False
    mask[342:] = False
    mask = cv2.dilate(mask.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    riempi_trama(d.img, mask, raggio=5)
    blu = (45, 55, 135)
    for y, t in ((170, 'Insieme alle posizioni dei'), (220, 'suoi pezzi, il Maestro di Scacchi tiene'),
                 (270, 'la chiave del terzo livello sempre'), (320, 'nei suoi pensieri.')):
        d.scrivi(58, y, t, ttf=PENNA, size=34, rgb=blu, usura=0.05, larg=545)
    return d.img


UNCIALE = os.path.join(FONT, 'UncialAntiqua-Regular.ttf')


def invito():
    img = BM.load(dat('d1', 'ROOMS', 'INVITE.BM'), dat('d1', 'ROOMS', 'INVITE.PAL'))
    d = Doc(img)
    x0, y0, x1, y1 = 62, 84, 600, 472
    rgb = img.pal[img.px[y0:y1, x0:x1]].astype(int)
    m = rgb.mean(2) < 150
    mask = np.zeros(img.px.shape, bool)
    mask[y0:y1, x0:x1] = m
    mask = cv2.dilate(mask.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    lim = np.zeros_like(mask)
    lim[y0:y1, x0:x1] = True
    # non toccare la mano in basso a destra
    lim[370:480, 560:640] = False
    riempi_trama(img, mask & lim, raggio=6)
    nero = (20, 20, 15)
    righe = [(108, "'Sia noto che il", 19), (143, 'Sacro Ordine della', 27), (163, 'Luna del Raccolto', 27),
             (199, "con la presente dichiara l'idoneità di", 19), (229, 'Steve Mason', 27),
             (252, "all'iniziazione ai", 19), (284, 'Sacri Misteri del', 27), (314, 'Raccolto.', 27),
             (350, 'Si presenti con tutta la', 19), (377, 'sollecitudine possibile al', 19),
             (413, "Sergente d'Armi", 27), (455, "per l'inizio dei riti.'", 19)]
    for y, t, sz in righe:
        d.scrivi(328, y, t, ttf=UNCIALE, size=sz, rgb=nero, ancora='ms', larg=500, usura=0)
    return img


def atto(copia=False):
    """Atto di proprietà della WHAR (TVDEED1 originale, TVDEED2 fotocopia): pagina inclinata."""
    from grafica import testo_ruotato
    nome = 'TVDEED2' if copia else 'TVDEED1'
    d = Doc(carica(nome))
    img = d.img
    lum = img.pal[img.px].astype(int).mean(2)
    # zone di testo da ripulire (tutto tranne le linee lunghe del modulo e i nomi battuti a macchina)
    mask = np.zeros(img.px.shape, bool)
    def poligono(punti, soglia=175):
        z = np.zeros(img.px.shape, np.uint8)
        cv2.fillPoly(z, [np.array(punti, np.int32)], 1)
        mask[(z == 1) & (lum < soglia)] = True
    dy = 0 if copia else -120 if False else 0
    # OWNERSHIP
    poligono([(0, 0), (640, 0), (640, 45), (0, 165)])
    # This certifies that:
    poligono([(10, 190), (170, 165), (175, 200), (12, 228)])
    # are the official bearers ... as th
    poligono([(40, 395), (640, 285), (640, 320), (40, 428)])
    # W.H.A.R. Television Studio, Harvest Co (macchina da scrivere)
    poligono([(165, 445), (640, 360), (640, 395), (170, 470)])
    # righe in fondo
    poligono([(50, 470), (640, 400), (640, 480), (50, 480)])
    mask = cv2.dilate(mask.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    # le linee lunghe del modulo restano: si tolgono dalla maschera i pixel scuri in fila lunga
    riempi_trama(img, mask, raggio=5)
    nero = (25, 25, 30)
    serif = SERIF_R
    testo_ruotato(img, 310, 130, 'PROPRIETÀ', serif, 104, nero, d.amm, angolo=9.5, ancora='ms', scala_x=0.85)
    testo_ruotato(img, 18, 220, 'Si certifica che:', serif, 15, nero, d.amm, angolo=8.5)
    testo_ruotato(img, 52, 413, 'sono i titolari ufficiali di questo atto e vanno pienamente riconosciuti come', serif, 15, nero, d.amm, angolo=10.2, scala_x=0.92)
    testo_ruotato(img, 178, 445, 'Studio televisivo W.H.A.R., Contea di Harvest', MACCHINA, 15, (35, 35, 60), d.amm, angolo=10.0, usura=0.35)
    testo_ruotato(img, 62, 479, "(1) ...altri vincoli, e sono preposti alla gestione e al controllo", serif, 15, nero, d.amm, angolo=10.0, scala_x=0.9)
    return img


SANS = '/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf'
SANS_N = '/usr/share/fonts/opentype/urw-base35/NimbusSansNarrow-Regular.otf'
SANS_BI = '/usr/share/fonts/opentype/urw-base35/NimbusSans-BoldItalic.otf'
SERIF_I = '/usr/share/fonts/opentype/urw-base35/NimbusRoman-Italic.otf'


def rivista():
    d = Doc(carica('DRTYMAG'))
    img = d.img
    rgb = img.pal[img.px].astype(int)
    lum = rgb.mean(2)
    sat = rgb.max(2) - rgb.min(2)
    nero = lum < 75
    bianco = (lum > 185) & (sat < 60)
    rosso = (rgb[..., 0] > 140) & (rgb[..., 1] < 90) & (rgb[..., 2] < 110)
    mask = np.zeros(img.px.shape, bool)
    def zona(box, sel):
        x0, y0, x1, y1 = box
        mask[y0:y1, x0:x1] |= sel[y0:y1, x0:x1]
    zona((378, 0, 534, 16), nero)          # This Issue $.25
    zona((398, 18, 534, 36), nero)         # NOVEMBER 1953
    zona((112, 172, 240, 202), nero)       # Uncensored
    zona((362, 138, 534, 218), bianco)     # A Midget and...
    zona((112, 250, 220, 324), nero)       # Mrs. Phelps ...
    zona((430, 296, 534, 348), rosso)      # DADDY'S Day Off!
    zona((112, 342, 188, 424), nero)       # HOW MEAT CHANGED MY LIFE!
    zona((188, 342, 232, 398), nero)
    zona((112, 440, 240, 468), nero)       # SPECIAL ISSUE!
    mask = cv2.dilate(mask.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    riempi_trama(img, mask, raggio=5)
    N, B, R = (15, 15, 20), (245, 245, 250), (215, 25, 25)
    d.scrivi(524, 13, 'PREZZO $.25', ttf=SANS, size=12, rgb=N, ancora='rs', usura=0)
    d.scrivi(522, 32, 'NOVEMBRE 1953', ttf=SERIF_I, size=13, rgb=N, ancora='rs', usura=0)
    d.scrivi(114, 197, 'Senza censure', ttf=SERIF_I, size=21, rgb=N, larg=125, usura=0)
    for y, t in ((158, 'UN NANO E'), (176, 'UN PACCHETTO DI'), (194, "'NECO WAFERS'"), (212, 'DI: MR. SWELLS')):
        d.scrivi(448, y, t, ttf=SERIF, size=15, rgb=B, ancora='ms', larg=165, usura=0)
    for y, t in ((271, 'La signora Phelps:'), (293, "'L'Emporio dei"), (315, "PIACERI..'")):
        d.scrivi(114, y, t, ttf=SANS_N, size=14, rgb=N, larg=104, usura=0)
    d.scrivi(483, 318, 'PAPÀ', ttf=SANS_BI, size=19, rgb=R, ancora='ms', usura=0)
    d.scrivi(483, 341, 'in ferie!', ttf=SANS_BI, size=18, rgb=R, ancora='ms', larg=98, usura=0)
    for y, t in ((362, 'COME LA CARNE'), (386, 'MI HA CAMBIATO'), (410, 'LA VITA!')):
        d.scrivi(114, y, t, ttf=SANS_N, size=19, rgb=N, larg=112, usura=0)
    d.scrivi(114, 463, 'NUMERO SPECIALE!', ttf=SANS_N, size=17, rgb=N, larg=124, usura=0)
    return img


def registro():
    """Registro dei conti dello sceriffo (REGISTER): intestazioni stampate minuscole e voci a mano."""
    d = Doc(carica('REGISTER'))
    img = d.img
    rgb = img.pal[img.px].astype(int)
    lum = rgb.mean(2)
    blu = (rgb[..., 2] > rgb[..., 0] + 25)
    def linee_lunghe(m, minimo=25):
        keep = np.zeros_like(m)
        for y in range(m.shape[0]):
            r = m[y]; x = 0
            while x < len(r):
                if r[x]:
                    a = x
                    while x < len(r) and r[x]: x += 1
                    if x - a >= minimo: keep[y, a:x] = True
                x += 1
        for x in range(m.shape[1]):
            c = m[:, x]; y = 0
            while y < len(c):
                if c[y]:
                    a = y
                    while y < len(c) and c[y]: y += 1
                    if y - a >= 12: keep[a:y, x] = True
                y += 1
        return keep
    def cancella(box, soglia=110, solo_blu=False, minimo=25):
        x0, y0, x1, y1 = box
        m = (blu if solo_blu else ((lum < soglia) | blu))[y0:y1, x0:x1].copy()
        m &= ~linee_lunghe(m, minimo)
        mask = np.zeros(img.px.shape, bool)
        mask[y0:y1, x0:x1] = m
        mask = cv2.dilate(mask.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        lim = np.zeros_like(mask); lim[y0:y1, x0:x1] = True
        riempi_trama(img, mask & lim, raggio=3)
    # colori d'inchiostro delle voci (campionati prima di cancellare)
    righe = [65, 78, 95, 109, 126, 140, 155, 170, 185, 201, 214]
    inchiostri = []
    for y in righe:
        z = rgb[y - 5:y + 4, 152:300]
        scuri = (z.mean(2) < 120)
        zb = blu[y - 5:y + 4, 152:300] & (z.mean(2) < 190)
        inchiostri.append((60, 85, 160) if zb.sum() > scuri.sum() else (35, 35, 35))
    cancella((80, 21, 330, 32))                       # avviso in testa
    for box in ((84, 38, 122, 57), (124, 38, 142, 57), (200, 38, 290, 57), (338, 34, 398, 57),
                (406, 34, 428, 57), (430, 34, 484, 57), (500, 34, 540, 46)):
        cancella(box, soglia=165)
    cancella((140, 58, 337, 222), minimo=120)          # descrizioni
    cancella((340, 179, 392, 190))                     # TAX DEDUCT.
    N = (25, 25, 25)
    SN = '/usr/share/fonts/opentype/urw-base35/NimbusSansNarrow-Bold.otf'
    def stampa(x, y, t, sz=6, larg=None, a='ls'):
        d.scrivi(x, y, t, ttf=SN, size=sz, rgb=N, ancora=a, larg=larg, usura=0)
    stampa(205, 30, 'RICORDATE DI DETRARRE GLI ADDEBITI CHE RIGUARDANO IL VOSTRO CONTO', 7, 236, 'ms')
    stampa(103, 47, 'NUMERO O', 5, 34, 'ms'); stampa(103, 53, 'CODICE', 5, 34, 'ms')
    stampa(133, 50, 'DATA', 5, 16, 'ms')
    stampa(245, 50, "DESCRIZIONE DELL'OPERAZIONE", 6, 86, 'ms')
    stampa(368, 41, 'ADDEBITI', 6, 50, 'ms'); stampa(368, 48, 'IMPORTO PAGATO', 6, 56, 'ms'); stampa(368, 55, 'O PRELEVATO (-)', 6, 56, 'ms')
    stampa(417, 41, '(-)', 6, 18, 'ms'); stampa(417, 48, 'SPESE', 6, 20, 'ms')
    stampa(457, 41, 'ACCREDITI', 6, 50, 'ms'); stampa(457, 48, 'IMPORTO VERSATO', 6, 52, 'ms'); stampa(457, 55, 'O INTERESSI (+)', 6, 52, 'ms')
    stampa(520, 42, 'SALDO', 6, 30, 'ms')
    voci = ['Versamento - Boyle', 'Versamento - Boyle', 'Versamento - Boyle', 'Versamento - Boyle',
            "Assegno n. 716 - DNA's", 'Versamento - Boyle', 'Versamento - Boyle', 'Versamento - WHAR',
            'Versamento - Boyle', "ARMERIA TULIP - 1 cassa di cartucce", 'Versamento - Boyle']
    for y, t, ink in zip(righe, voci, inchiostri):
        d.scrivi(154, y + 3, t, ttf=PENNA, size=16, rgb=ink, larg=176, usura=0.05)
    d.scrivi(343, 189, 'DETRAIBILE', ttf=PENNA, size=12, rgb=(35, 35, 35), larg=48, usura=0.05)
    return img


PENNARELLO = os.path.join(FONT, 'PermanentMarker-Regular.ttf')


def striscione():
    """Striscione della vendita di dolci nella palestra della scuola (BAKESALE, sfondo di stanza)."""
    d = Doc(carica('BAKESALE'))
    img = d.img
    rgb = img.pal[img.px].astype(int)
    rosso = (rgb[..., 0] > rgb[..., 1] + 45) & (rgb[..., 0] > 120)
    colore = tuple(int(v) for v in np.percentile(rgb[110:185, 152:472][rosso[110:185, 152:472]], 40, axis=0))
    rosato = (rgb[..., 0] - rgb[..., 1] > 26)
    mask = np.zeros(img.px.shape, bool)
    mask[106:188, 150:474] = rosato[106:188, 150:474]
    mask = cv2.dilate(mask.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    from grafica_ui import ritocca
    ritocca(img, mask, raggio=3)
    from grafica import testo_ruotato
    testo_ruotato(img, 312, 163, 'Vendita di dolci oggi!', PENNARELLO, 36, colore, d.amm, angolo=-1.5, ancora='ms', scala_x=0.74)
    return img


DOCUMENTI = {
    'LODGAPP1': lambda: domanda(False),
    'LODGAPP2': lambda: domanda(True),
    'PERMIT1': lambda: ricetta('PERMIT1', PERMESSO_CANC, PERMESSO_SCR, size=13, carta=(60, 360, 600, 380)),
    'PERMIT2': lambda: ricetta('PERMIT2', PERMESSO_CANC, PERMESSO_SCR, size=13, carta=(60, 360, 600, 380)),
    'SAFEBOOK': cassaforte,
    'SCHEDULE': turni,
    'BOYLNOTE': lambda: biglietto_boyle(False),
    'BOYLCOPY': lambda: biglietto_boyle(True),
    'CLUE': indizio,
    'INVITE': invito,
    'TVDEED1': lambda: atto(False),
    'TVDEED2': lambda: atto(True),
    'DRTYMAG': rivista,
    'REGISTER': registro,
    'BAKESALE': striscione,
}

if __name__ == '__main__':
    out = os.path.join(RADICE, 'grafica', 'documenti')
    os.makedirs(out, exist_ok=True)
    scelti = sys.argv[1:] or list(DOCUMENTI)
    for n in scelti:
        img = DOCUMENTI[n]()
        open(os.path.join(out, n + '.BM'), 'wb').write(img.dump())
        img.png(os.path.join(out, n + '.png'))
        print('scritto', n)
