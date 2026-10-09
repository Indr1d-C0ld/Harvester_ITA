# Harvester in italiano

Traduzione italiana **non ufficiale** di *Harvester* (DigiFX Interactive / Merit
Studios, 1996), l'avventura horror per DOS ambientata nella cittadina di Harvest.

Questo repository **non contiene il gioco** né file presi dal gioco. Contiene
una patch: un programma che, partendo dai tre CD originali che possiedi, crea
una cartella con il gioco in italiano pronta per DOSBox.

> Lavoro amatoriale, senza scopo di lucro, non affiliato né approvato da DigiFX
> Interactive, Merit Studios o dagli attuali titolari dei diritti di Harvester.
> Se sei titolare dei diritti e vuoi che venga rimosso, apri una segnalazione:
> sarà tolto.

## Che cosa è tradotto

- Tutti i sottotitoli dei dialoghi: 2.531 battute. Le voci degli attori restano
  in inglese.
- Le scelte di risposta e gli argomenti di conversazione, compresi quelli che si
  scrivono a mano nel campo «Altro».
- Le descrizioni degli oggetti, i nomi sotto il cursore e la mappa della città.
- I menu, le opzioni, i suggerimenti, le schermate di salvataggio, caricamento e
  aiuto, l'inventario, la richiesta del CD e la schermata di attesa.
- I documenti che si trovano nel gioco: la domanda di ammissione alla Loggia,
  l'invito, il permesso per la carne, l'atto di proprietà della stazione TV, il
  libretto della cassaforte, i turni di pattuglia, il biglietto di Boyle,
  l'indizio degli scacchi, la rivista, il registro dei conti e lo striscione
  della scuola.
- Ai font del gioco sono state aggiunte le lettere accentate che mancavano.

In più, l'eseguibile del 1996 conteneva una modalità usata dagli sviluppatori
per leggere i tre dischi da cartelle: la patch la attiva, così **non serve
cambiare CD**. Chi preferisce l'esperienza originale può creare anche le
immagini dei CD tradotte e giocare cambiandole come nel 1996.

## Che cosa serve

- I **tre CD della versione inglese** di Harvester (versione 1.0 su 3 CD) come
  immagini: `.iso`, `.bin`/`.cue`, o immagini grezze a 2352 byte. La patch
  riconosce i dischi dall'etichetta (`DISK1`, `DISK2`, `DISK3`) e controlla
  che siano proprio quelli giusti prima di toccare qualunque cosa.
- **Python 3.8** o successivo (basta la libreria standard).
- **DOSBox** (provato con DOSBox 0.74).
- Circa 1,2 GB liberi; 2,8 GB con l'opzione `--iso`.

## Come si usa

```bash
python3 applica_patch.py /percorso/delle/immagini/dei/CD /percorso/di/destinazione
cd /percorso/di/destinazione
dosbox -conf dosbox-harvester-ita.conf
```

Aggiungendo `--iso` crea anche le tre immagini dei CD tradotte, per giocare
con `dosbox-harvester-ita-cd.conf` (si cambia disco con Ctrl+F4).

Nella cartella creata trovi un `LEGGIMI.txt` con i dettagli.

## Contenuto del repository

| Percorso | Cosa contiene |
|---|---|
| `applica_patch.py` | l'applicatore: solo libreria standard di Python |
| `dati/` | le differenze binarie fra i file originali e quelli tradotti (`.hdf`), l'elenco con le impronte SHA-1 attese (`manifest.json`), le configurazioni di DOSBox e del gioco |
| `docs/FORMATI.md` | i formati dei file di Harvester e le note sul motore scoperte durante il lavoro |
| `docs/GLOSSARIO.md` | le scelte di traduzione: registro, nomi, termini fissati |
| `strumenti/` | gli strumenti usati per estrarre, tradurre, ridisegnare e ricostruire (servono una copia del gioco e i cataloghi di traduzione, che non sono qui perché contengono il testo originale) |

Le differenze (`.hdf`) dicono come trasformare un file originale in quello
tradotto: senza il file originale non servono a niente. Il formato è descritto
in `strumenti/bindiff.py`.

## Licenza

Il codice e i dati della patch sono distribuiti con licenza GNU GPL v3 (vedi
`LICENSE`). Harvester e tutti i suoi contenuti restano dei rispettivi titolari.
