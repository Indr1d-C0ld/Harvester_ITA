#!/usr/bin/env python3
"""Manuale di Harvester in italiano: manuale/testo_it.md -> build/Harvester_manuale_ITA.pdf

Usa pandoc (Markdown -> HTML) e WeasyPrint (HTML -> PDF) di sistema.
    python3 tools/manuale.py [--html]"""
import os, re, subprocess, sys, html

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)
MAN = os.path.join(RADICE, 'manuale')
IMG = os.path.join(MAN, 'img')
FONT = os.path.join(QUI, 'font')

EDIZIONE = r"""
# L'edizione italiana

Questo libretto traduce il manuale originale del 1996. Le istruzioni per installare il gioco su DOS, Windows 3.1 e Windows 95 sono rimaste per completezza: oggi Harvester si gioca con DOSBox, e per l'edizione italiana è già tutto pronto.

## AVVIARE IL GIOCO

1. Apri un terminale nella cartella dell'edizione italiana, quella che contiene la cartella `HARVEST` e il file `dosbox-harvester-ita.conf`.
2. Avvia DOSBox con la configurazione inclusa: `dosbox -conf dosbox-harvester-ita.conf`
3. Il contenuto dei tre CD è già copiato nelle cartelle `HARVEST\CD1`, `CD2` e `CD3`: il gioco passa da un disco all'altro da solo, senza chiederti nulla.

Se preferisci giocare come nel 1996, con i tre dischi, usa invece `dosbox-harvester-ita-cd.conf`. Quando il gioco ti chiede un altro CD premi [TASTO: CTRL] + [TASTO: F4] (anche più volte, finché non compare il disco giusto) e poi fai clic.

## CHE COSA È TRADOTTO

Le voci degli attori sono rimaste quelle originali, in inglese. Tutto quello che si legge è in italiano: i sottotitoli dei dialoghi (tienili attivi: menu *OPZIONI*, voce *SOTTOTITOLI*), le risposte e gli argomenti di conversazione, le descrizioni degli oggetti, i nomi che compaiono sotto il cursore, la mappa, i menu, le schermate di aiuto, l'inventario e i documenti che troverai nel corso del gioco.

## GLI ARGOMENTI DI CONVERSAZIONE

Durante un dialogo compare l'elenco degli argomenti di cui puoi parlare. Il pulsante *Altro* ti permette di scriverne uno a mano: scrivilo in italiano, per esempio «Loggia», «sorella» o «incendio del giornale». Per chiudere una conversazione scegli *SALUTA*.

## COMANDI IN BREVE

| Comando | Effetto |
|---|---|
| Tasto sinistro del mouse | cammina, esamina, usa, parla, prende |
| Tasto destro del mouse | attacca; nell'inventario: primo piano, impugna o ripone un'arma |
| [TASTO: I] | apre l'inventario |
| [TASTO: ESC] | menu principale |
| [TASTO: frecce] | muovono Steve |
| [TASTO: CTRL] + [TASTO: frecce] | attacco alto, basso o medio |
| [TASTO: ALT] | Steve si abbassa |
| [TASTO: SHIFT] | Steve corre |
"""

COLOFONE = """
<section class="colofone">
<table class="loghi"><tr><td>Pubblicato da</td><td>Sviluppato da</td></tr>
<tr><td><img src="{img}/logo_merit.png"></td><td><img src="{img}/logo_digifx.png"></td></tr></table>
<p>© 1996 DigiFX Interactive, Inc. Harvester™ è un marchio registrato di DigiFX Interactive, Inc. Tutti i diritti riservati. Pubblicato da Merit Studios, Inc.</p>
<p class="ita"><strong>Edizione italiana non ufficiale</strong> (2026): traduzione dei testi, dei sottotitoli, della grafica e di questo manuale; adattamento per DOSBox. Lavoro amatoriale senza scopo di lucro: richiede una copia originale del gioco.</p>
</section>
"""

CSS = """
@font-face {{ font-family: 'Goudy'; src: url('{font}/SortsMillGoudy-Regular.ttf'); }}
@font-face {{ font-family: 'Goudy'; font-style: italic; src: url('{font}/SortsMillGoudy-Italic.ttf'); }}
@font-face {{ font-family: 'GoudyB'; src: url('{font}/GoudyBookletter1911.ttf'); }}
@font-face {{ font-family: 'Goudy'; font-weight: bold; src: url('{font}/Cardo-Bold.ttf'); }}
@font-face {{ font-family: 'Fondamento'; font-style: italic; src: url('{font}/Fondamento-Italic.ttf'); }}
@font-face {{ font-family: 'Mano'; src: url('{font}/ReenieBeanie.ttf'); }}
@page {{
  size: 150mm 150mm;
  margin: 12mm 13mm 15mm 13mm;
}}
@page :left {{ @bottom-left {{ content: counter(page); font-family: 'Mano'; font-size: 17pt; color: #222; }} }}
@page :right {{ @bottom-right {{ content: counter(page); font-family: 'Mano'; font-size: 17pt; color: #222; }} }}
@page copertina {{ margin: 0; @bottom-left {{ content: none; }} @bottom-right {{ content: none; }} }}
@page muta {{ @bottom-left {{ content: none; }} @bottom-right {{ content: none; }} }}
html {{ font-family: 'Goudy', serif; font-size: 9.6pt; line-height: 1.32; color: #111; }}
body {{ margin: 0; }}
.copertina {{ page: copertina; width: 150mm; height: 150mm; position: relative; break-after: page;
  background: #000 url('{img}/copertina.png') center / cover no-repeat; }}
.copertina .fascia {{ position: absolute; bottom: 9mm; left: 0; right: 0; text-align: center;
  font-family: 'Fondamento'; font-style: italic; color: #f2e9d8; font-size: 15pt;
  background: rgba(0,0,0,.72); padding: 2.2mm 0; }}
.quarta {{ page: copertina; width: 150mm; height: 150mm; break-before: page;
  background: #ddd url('{img}/quarta.png') center / cover no-repeat; }}
.colofone {{ page: muta; break-after: page; padding-top: 28mm; font-size: 8.4pt; text-align: center; }}
.colofone .loghi {{ width: 100%; margin-bottom: 10mm; }}
.colofone .loghi td {{ border: none; text-align: center; width: 50%; font-weight: bold; padding: 1mm; }}
.colofone .loghi img {{ height: 18mm; }}
.colofone .ita {{ margin-top: 8mm; border-top: .3pt solid #555; padding-top: 4mm; }}
h1 {{ break-before: page; font-family: 'Fondamento'; font-style: italic; font-weight: normal;
  background: #0d0d0d; color: #f4f1ea; text-align: center; font-size: 15pt; letter-spacing: .3pt;
  padding: 1.6mm 4mm 2mm; margin: 0 0 5mm; }}
h2 {{ font-family: 'GoudyB'; font-weight: normal; font-size: 10.6pt; letter-spacing: .25pt;
  margin: 4.2mm 0 1.2mm; break-after: avoid; }}
h3 {{ font-style: italic; font-weight: normal; font-size: 10.4pt; margin: 3.5mm 0 1mm; break-after: avoid; }}
h4 {{ font-weight: normal; text-decoration: underline; font-size: 10pt; margin: 2.8mm 0 .6mm; break-after: avoid; }}
p {{ margin: 0 0 2.3mm; orphans: 2; widows: 2; }}
ol, ul {{ margin: 0 0 2.3mm; padding-left: 5mm; }}
li {{ margin-bottom: .8mm; }}
code {{ font-family: 'DejaVu Sans Mono', monospace; font-size: 8.2pt; }}
pre {{ margin: 0 0 2.3mm 6mm; }}
strong {{ font-weight: bold; font-size: .94em; }}
kbd {{ font-family: 'DejaVu Sans', sans-serif; font-size: 7pt; border: .5pt solid #333; border-radius: .5mm;
  padding: 0 1.2mm; box-shadow: .4pt .6pt 0 #333; background: #f7f7f7; white-space: nowrap; }}
table {{ border-collapse: collapse; width: 100%; font-size: 8.8pt; margin-bottom: 3mm; }}
th, td {{ text-align: left; vertical-align: top; padding: .9mm 1.5mm; border-bottom: .3pt solid #999; }}
th {{ font-family: 'GoudyB'; font-weight: normal; }}
.cursori {{ width: 100%; border-collapse: separate; border-spacing: 0 2mm; margin: 1mm 0 2mm; }}
.cursori td {{ border: none; padding: 0; vertical-align: top; font-size: 9pt; }}
.cursori td.ic {{ width: 12.5mm; }}
.cursori td.ic img {{ width: 11mm; height: 11mm; image-rendering: pixelated; border: .4pt solid #222; }}
.cursori td.tx {{ width: 37%; padding-right: 3mm; }}
figure {{ margin: 1.5mm 0 3mm; text-align: center; break-inside: avoid; }}
figure img {{ max-width: 100%; border: .4pt solid #444; }}
figure.destra {{ float: right; width: 44%; margin: .5mm 0 2mm 4mm; }}
figure.sinistra {{ float: left; width: 30%; margin: .5mm 4mm 2mm 0; }}
figure.icona {{ float: left; margin: .5mm 3mm 1mm 0; }}
figure.icona img {{ width: 11mm; image-rendering: pixelated; }}
.riga-img {{ text-align: center; }}
.riga-img img {{ border: none; margin: 0 1mm; vertical-align: middle; }}
figcaption {{ font-size: 7.6pt; font-style: italic; margin-top: .8mm; }}
.nota {{ font-style: italic; }}
.licenza {{ font-size: 7.2pt; line-height: 1.22; }}
.licenza h1 {{ font-size: 10.5pt; font-family: 'GoudyB'; font-style: normal; }}
.riconoscimenti ul {{ list-style: none; padding: 0; columns: 2; column-gap: 6mm; font-size: 8.4pt; }}
.riconoscimenti li {{ break-inside: avoid; margin: 0 0 1.3mm; }}
.riconoscimenti li strong {{ text-decoration: underline; -weasy-text-stroke: 0; font-family: 'Goudy'; font-variant: small-caps; }}
.riconoscimenti li ul {{ columns: 1; padding-left: 3.5mm; font-size: 8.4pt; margin: 0; }}
.riconoscimenti li ul li {{ margin: 0; }}
.riconoscimenti h2 {{ font-family: 'Fondamento'; font-style: italic; background: #0d0d0d; color: #f4f1ea;
  text-align: center; font-size: 10pt; padding: .8mm; margin: 3mm 0 2mm; column-span: all; }}
"""

CURSORI = {'Movimento': 'movimento', 'Conversazione': 'conversazione', 'Esamina': 'esamina', 'Usa': 'usa', 'Esci': 'esci'}
TASTI = {'frecce': '<kbd>↑</kbd> <kbd>↓</kbd> <kbd>←</kbd> <kbd>→</kbd>'}


def immagine(desc):
    d = desc.lower()
    i = f'file://{IMG}'
    if d.startswith('copertina') or d.startswith('quarta') or d.startswith('logo'):
        return ''
    if d.startswith('cursore bersaglio'):
        return f'<figure class="icona"><img src="{i}/cursore_bersaglio.png"></figure>'
    if d.startswith('cursore'):
        return ''   # gestiti insieme alla definizione che segue
    if 'mappa' in d:
        return f'<figure class="destra"><img src="{i}/mappa.png"><figcaption>La mappa di Harvest</figcaption></figure>'
    if 'fotogrammi' in d:
        return f'<figure><img src="{i}/raccogliere.png" style="width:70%; border:none"></figure>'
    if 'inventario' in d and 'armi' not in d:
        return f'<figure class="destra" style="width:50%"><img src="{i}/inventario_crop.png"><figcaption>L\'inventario</figcaption></figure>'
    if 'polaroid' in d:
        return (f'<figure class="riga-img">' + ''.join(f'<img src="{i}/salute_HEAD-{k}.png" style="width:20mm">'
                                                      for k in ('A1', 'A3', 'B1', 'C1')) + '</figure>')
    if 'armi' in d:
        return (f'<figure class="riga-img">' + ''.join(f'<img src="{i}/arma_{k}.png" style="height:12mm">'
                for k in ('NINEMM', 'SHOTGUN', 'CHAINSAW', 'PITCHFK', 'SHOVEL')) + '</figure>')
    if 'menu principale' in d:
        return f'<figure class="destra"><img src="{i}/menu.png"></figure>'
    print('immagine non gestita:', desc, file=sys.stderr)
    return ''


def tasti(s):
    def r(m):
        k = m.group(1).strip()
        return TASTI.get(k, f'<kbd>{html.escape(k)}</kbd>')
    return re.sub(r'\[TASTO:\s*([^\]]+)\]', r, s)


def md2html(md):
    md = tasti(md)
    out = subprocess.run(['pandoc', '-f', 'markdown+raw_html', '-t', 'html5', '--wrap=none'],
                         input=md.encode(), capture_output=True, check=True).stdout.decode()
    return out


def costruisci(solo_html=False):
    testo = open(os.path.join(MAN, 'testo_it.md'), encoding='utf-8').read()
    testo = re.sub(r'<!-- pagina \d+ -->\n?', '', testo)
    # parti del libretto che hanno una veste propria
    i_rico = testo.index('# Riconoscimenti')
    i_assi = testo.index('# Assistenza clienti')
    i_lic = testo.index('# CONTRATTO DI LICENZA')
    i_guida = testo.index('# Guida all')
    corpo = md2html(testo[i_guida:i_rico])
    rico = md2html(testo[i_rico:i_assi])
    assi = md2html(testo[i_assi:i_lic])
    lic = md2html(testo[i_lic:])
    ediz = md2html(EDIZIONE)

    # segnaposto immagine
    def sost(h):
        return re.sub(r'<p>\[IMMAGINE:\s*([^\]]+)\]</p>', lambda m: immagine(m.group(1)), h)
    # cursori: icona + paragrafo successivo
    def cursori(h):
        voci = []
        def r(m):
            nome = m.group(2)
            chiave = next((v for k, v in CURSORI.items() if nome.startswith(k)), None)
            voci.append((chiave, nome, m.group(3)))
            return '\x00CURSORE\x00'
        h = re.sub(r'<p>\[IMMAGINE:\s*cursore (?!Bersaglio)([^\]]+)\]</p>\s*<p><strong>([^<]+)</strong><br />\s*([^<]+)</p>\s*', r, h)
        celle = [f'<td class="ic"><img src="file://{IMG}/cursore_{c}.png"></td><td class="tx"><strong>{n}</strong><br />{t}</td>'
                 for c, n, t in voci]
        righe = ''.join('<tr>' + ''.join(celle[i:i + 2]) + '</tr>' for i in range(0, len(celle), 2))
        h = h.replace('\x00CURSORE\x00', f'<table class="cursori">{righe}</table>', 1).replace('\x00CURSORE\x00', '')
        return h
    corpo = sost(cursori(corpo))
    # la sequenza "raccogliere" va dopo il titoletto, la mappa e il menu prima del testo: già nell'ordine del .md
    rico = sost(rico)
    assi = sost(assi).replace('<p><em>Informazioni dell', '<p class="nota"><em>Informazioni dell')

    pagina = f"""<!DOCTYPE html><html lang="it"><head><meta charset="utf-8"><title>Harvester - Manuale</title>
<style>{CSS.format(font='file://' + FONT, img='file://' + IMG)}</style></head><body>
<section class="copertina"><div class="fascia">Manuale di gioco &middot; edizione italiana</div></section>
{COLOFONE.format(img='file://' + IMG)}
{ediz}
{corpo}
<section class="riconoscimenti">{rico}</section>
{assi}
<section class="licenza">{lic}</section>
<section class="quarta"></section>
</body></html>"""
    os.makedirs(os.path.join(RADICE, 'build'), exist_ok=True)
    p_html = os.path.join(MAN, 'manuale.html')
    open(p_html, 'w', encoding='utf-8').write(pagina)
    if solo_html:
        print(p_html)
        return
    import weasyprint
    out = os.path.join(RADICE, 'build', 'Harvester_manuale_ITA.pdf')
    weasyprint.HTML(p_html).write_pdf(out)
    print(out)


if __name__ == '__main__':
    costruisci('--html' in sys.argv)
