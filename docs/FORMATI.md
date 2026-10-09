# Harvester (1996): formati dei file e note sul motore

Appunti tecnici raccolti durante la traduzione italiana. Valgono per la versione
inglese su 3 CD, `HARVEST.EXE` v1.0 (1.173.079 byte, eseguibile LE per DOS/4G,
compilato con Watcom C/C++).

## Dischi

Tre CD ISO 9660 con etichette `DISK1`, `DISK2`, `DISK3`. Alcune copie in giro
sono immagini grezze a 2352 byte per settore (modo 2, forma 1) con estensione
`.iso`: i dati stanno dal byte 24 di ogni settore.

| File | Dove | Contenuto |
|---|---|---|
| `HARVEST.SCR` | CD (1 e 2 uguali, 3 diverso) | script del gioco |
| `DIALOGUE.IDX` | CD (uguale sui tre) | testi delle battute parlate (sottotitoli) |
| `DIALOG.RSP` | cartella del gioco | scelte di risposta e argomenti di conversazione |
| `MENU.INI` | cartella del gioco | voci dei menu |
| `ADJHEAD.RCS` | CD | suggerimenti di gioco, una riga ciascuno |
| `HARVEST.DAT` + `INDEX.001` | CD | archivio della grafica (unità `1:\`) |
| `SOUND.DAT` + `INDEX.002` | CD | voci ed effetti (unità `2:\`) |
| `HARVEST2.DAT` + `INDEX.003` | cartella del gioco | animazioni dei mostri (unità `3:\`) |
| `GRAPHIC/FONT/*.CFT` | CD | font |
| `GRAPHIC/FST/*.FST` | CD | filmati |

`CONFIG.INI` dice al gioco dove trovare il CD (`CD_ROM`) e gli archivi
(`DRIVE_1`, `DRIVE_2`, `DRIVE_3`).

## Testi

- `HARVEST.SCR` e `DIALOGUE.IDX` sono testo cifrato con **XOR 0xAA** su ogni
  byte tranne CR e LF.
- `HARVEST.SCR`: un'istruzione per riga (`ROOM`, `OBJECT`, `NPC`, `TEXT`,
  `COMMAND`, `REGION`...). I testi visibili sono il terzo campo di `TEXT`,
  l'ultimo campo di `OBJECT` e `NPC` (il nome sotto il cursore) e il primo di
  `MAP_LOCATION`. Gli spazi sono scritti `_`. `TEXT "ID" "BOXn" "..."` sceglie
  il riquadro (1-8) in base alla lunghezza: il motore va a capo ogni 38
  caratteri circa.
- `DIALOGUE.IDX`: righe alterne, numero della battuta e testo fra virgolette.
  Una riga di testo è lunga al massimo 410 byte. Il numero coincide con quello
  del file della voce in `SOUND.DAT` (`2:\sound\voice\N.cmp`).
- `DIALOG.RSP`: il codice legge le righe per numero (funzione a `0x3a1a0`).
  Ogni riga è di tre tipi: un menu di argomenti separati da `/`, un argomento
  confrontato senza distinguere maiuscole da ciò che il giocatore sceglie o
  scrive nel campo "Other", oppure una scelta `1. testo/2. testo`. Le
  conversazioni stanno nel codice C++ dell'eseguibile, non nello script: per
  tradurre gli argomenti bisogna che menu, confronti e stringhe
  dell'eseguibile restino coerenti. La voce di congedo (`BYE`, riga 13) deve
  essere più corta di 10 caratteri.

## Font (`.CFT`)

Nome (64 byte), altezza (u16), inizio di ogni carattere nella striscia (256 ×
u16), larghezza (256 × u16), 18 byte (spazio, larghezza e altezza della
striscia), poi la striscia: una bitmap a 8 bit con tutti i caratteri affiancati.
Codifica Latin-1: ci sono gli accenti di francese e spagnolo, ma mancano ì e ò,
che si aggiungono allungando la striscia.

## Grafica

- `.BM`: larghezza (u32), altezza (u32), 4 byte, pixel a 8 bit. La tavolozza è
  un `.PAL` a parte (768 byte, valori 0-63).
- `.ABM`: animazione. Intestazione di 16 byte (numero di fotogrammi, dimensione
  massima); ogni fotogramma ha larghezza, altezza, flag di compressione,
  dimensione e puntatore (17 byte), poi i dati e 8 byte di coda. Compressione
  RLE: un byte `c` sotto 0x80 copia `c` byte, da 0x80 in su ripete il byte
  seguente `c - 0x80` volte.
- Archivi `.DAT`: l'indice ha un record di 148 byte per file (`XFLE`, nome di
  128 byte, posizione e dimensione due volte); ogni file nell'archivio è
  preceduto da una copia del suo record.

## Eseguibile

- Le stringhe dell'interfaccia (verbi del cursore, giorni, nomi degli slot di
  salvataggio, alcune scelte di dialogo) stanno nell'oggetto dati dell'LE. Una
  stringa tradotta più lunga si sposta altrove deviando le fixup che la
  puntano. Come spazio libero si usano le stringhe di debug dell'animazione
  (`state = facing_forward` e simili), che il gioco non mostra mai.
- **Modalità senza CD.** Il cambio di disco (funzione a `0x488a0`) ha un ramo per
  la rete interna degli sviluppatori. Se in `CONFIG.INI` c'è la chiave
  `NETWORK`, non controlla il lettore ma riscrive `CD_ROM` e `DRIVE_1..3` con
  `G:\HARVFNL\TOWN1\`, `TOWN2\` o `LODGE\`. L'edizione italiana riscrive quei
  percorsi in `C:\HARVEST\CD1\`, `CD2\` e `CD3\`. Con `NETWORK` impostata
  salta anche la schermata "inserisci il CD": il controllo è spostato
  all'inizio della funzione, nello spazio del vecchio controllo, e le fixup
  sono spostate in place. All'avvio il gioco vuole comunque un lettore CD
  (MSCDEX), anche vuoto.
- **Trucchi degli sviluppatori**: tabella dei codici di scansione a `0xc3cb0`.
  I codici sono NICK, MURDERER, SON OF SAM, BOSTON STRANGLER, HELTER
  SKELTER, CHARLES MANSON, BRUCE e DUSTIN. DUSTIN esegue il comando di
  script `WARP_TO_LODGE` (la Loggia, CD 3).
