<!-- pagina 0 -->

[IMMAGINE: copertina - logo «Harvester» in lettere rosse grondanti; una figura incappucciata con la falce davanti all'insegna del DNA's Diner («Open 24 Hours») e alla Loggia, di notte]

[IMMAGINE: quarta di copertina - cielo nuvoloso solcato da crepe, con i loghi degli editori]

Pubblicato da\
[IMMAGINE: logo Merit Studios]

Sviluppato da\
[IMMAGINE: logo DigiFX Interactive Inc.]

© 1996 DigiFX Interactive, Inc. Harvester™ è un marchio registrato di DigiFX Interactive, Inc. Tutti i diritti riservati.\
Pubblicato da Merit Studios, Inc. Stampato negli U.S.A.

<!-- pagina 1 -->

# Guida all'installazione e riferimento tecnico

## INTRODUZIONE

Benvenuto in Harvester. Se è la prima volta che installi il gioco, vorremmo dedicare qualche istante ad aiutarti a prendere confidenza con le istruzioni di installazione. Durante l'installazione saranno le schermate stesse a guidarti passo passo nella procedura.

Nota: se sul tuo sistema è in uso un programma di compressione del disco come DoubleSpace o DriveSpace, probabilmente i tempi di caricamento del programma si allungheranno. Harvester funziona sui computer su cui sono installati programmi di compressione di questo tipo; tuttavia non possiamo garantire che non si verifichino problemi se usi un altro software di compressione. Per avere prestazioni migliori, ti consigliamo di usare un'unità non compressa via software.

***IMPORTANTE! Harvester ha bisogno di un file di swap di 20 MB sul disco rigido locale. Se, mentre giochi a Harvester, non hai almeno 20 MB di spazio libero su disco, il programma potrebbe interrompersi o mandare in crash il computer. Se il tuo sistema ha 16 MB di RAM o più, il file di swap non serve.***

<!-- pagina 2 -->

## PRIMA DELL'INSTALLAZIONE

Prima di installare il gioco, è bene verificare l'integrità dei dati sul disco rigido. Per farlo, basta eseguire SCANDISK o DEFRAG dal prompt del DOS o da Windows. Dati danneggiati sul disco rigido possono peggiorare le prestazioni del sistema.

## INSTALLARE HARVESTER DA DOS

Per installare Harvester da DOS:

1. Inserisci il CD n. 1 nell'unità CD-ROM.
2. Digita la lettera dell'unità CD-ROM seguita dai due punti (esempio: `D:`), poi premi INVIO. Il prompt dovrebbe mostrare `D:\` o qualcosa di simile.
3. Digita `INSTALL` e premi INVIO.
4. Segui le istruzioni sullo schermo per installare Harvester sul computer.
5. Al termine dell'installazione, digita `HARVEST` per avviare il gioco.

## NOTE AGGIUNTIVE SULL'INSTALLAZIONE PER GLI UTENTI DOS

Se usi l'opzione (o parametro) per la memoria EMS, assicurati che nell'istruzione `device=` del CONFIG.SYS siano indicati almeno 8 MB (8192K). In alternativa puoi usare il parametro `AUTO` o il parametro `NOEMS`, oppure eliminare del tutto la riga dal file CONFIG.SYS.

<!-- pagina 3 -->

Righe di esempio per il file CONFIG.SYS:

```
device=emm386.exe 8192
device=emm386.exe noems
device=emm386.exe auto
```

Assicurati che il file CONFIG.SYS contenga l'istruzione `FILES=20` o un valore superiore.

Per funzionare correttamente, Harvester richiede 500K di memoria convenzionale (bassa) LIBERA. Se il tuo sistema ha meno di 500K di memoria convenzionale (bassa) LIBERA, potrebbe essere necessario eseguire l'utilità MEMMAKER per aumentare la RAM LIBERA.

Se il tuo sistema ha solo 8 MB di RAM, dovrai disattivare SMARTDRV o qualsiasi altro programma di cache del disco. Harvester usa circa 7 MB della memoria disponibile: con SMARTDRV o altri programmi di cache del disco caricati, la memoria a disposizione del gioco non basta.

<!-- pagina 4 -->

## INSTALLARE HARVESTER DA WINDOWS 3.1

Per installare Harvester da Windows 3.1:

1. Inserisci il CD n. 1 nell'unità CD-ROM.
2. Con il mouse, fai clic sul menu *File* e scegli *Esegui*.
3. Digita `D:\SETUP` e premi INVIO per avviare l'installazione (dove `D:\` è l'unità CD-ROM).

Al termine dell'installazione troverai un gruppo di programmi *Harvester* con diverse icone che puoi selezionare. Per avviare Harvester, basta fare clic sull'icona *Harvester*.

## NOTE AGGIUNTIVE SULL'INSTALLAZIONE PER GLI UTENTI DI WINDOWS 3.1

Se il tuo sistema ha solo 8 MB di RAM, dovrai disattivare il programma di cache del disco SMARTDRV. Harvester usa circa 7 MB della memoria disponibile: con SMARTDRV caricato, la memoria a disposizione del gioco non basta.

Se in Windows all'evento *Apertura programma* è associato un suono piuttosto lungo, quando avvii il programma Harvester potrebbe non rilevare la scheda audio del computer e quindi non riuscire ad avviarsi. Windows infatti non permette di usare più di una periferica audio alla volta. Per risolvere il problema, basta impostare su *(Nessuno)* il suono di *Apertura programma*.

<!-- pagina 5 -->

## INSTALLARE HARVESTER DA WINDOWS 95

Per installare Harvester da Windows 95:

1. Inserisci il CD n. 1 nell'unità.
2. Con il mouse, fai clic sul pulsante *Avvio* e scegli *Esegui...*.
3. Digita `D:\SETUP` e premi INVIO per avviare l'installazione (dove `D:\` è l'unità CD-ROM).

Al termine dell'installazione troverai un gruppo di programmi *Harvester* con diverse icone che puoi selezionare. Per avviare Harvester, basta fare clic sull'icona *Harvester*.

## NOTE AGGIUNTIVE SULL'INSTALLAZIONE PER GLI UTENTI DI WINDOWS 95

Quando giochi a Harvester sotto Windows 95, ti consigliamo di non tenere altri programmi in esecuzione in background. Se provi a tornare a Windows mentre giochi, Harvester potrebbe smettere di funzionare correttamente. In questo caso, riavvia il computer e non eseguire altri programmi mentre giochi a Harvester.

Se il tuo sistema ha meno di 16 MB di RAM, potrebbe essere necessario impostare a 16 MB l'opzione *Memoria DOS in modalità protetta (DPMI)* nelle *Proprietà*. Fai clic col tasto destro sulla barra delle applicazioni, nella parte bassa dello schermo, e scegli *Proprietà*. Poi apri la scheda *Programmi del menu Avvio* e fai clic sul pulsante *Avanzate* per aprire la finestra dei collegamenti. Trova il collegamento di Harvester, fai clic col tasto destro sull'icona di Harvester e scegli *Proprietà*. Seleziona la scheda *Memoria*.

<!-- pagina 6 -->

Individua la sezione *Memoria DOS in modalità protetta (DPMI)*, scegli il valore 16384 e fai clic su OK. Chiudi tutte le finestre.

Se mentre giochi a Harvester si attiva lo screen saver di Windows, potresti non riuscire più a tornare al programma, oppure il gioco potrebbe bloccarsi o chiudersi. Per risolvere il problema, disattiva lo screen saver.

Se in Windows all'evento *Apertura programma* è associato un suono piuttosto lungo, quando avvii il programma Harvester potrebbe non rilevare la scheda audio del computer e quindi non riuscire ad avviarsi. Windows infatti non permette di usare più di una periferica audio alla volta. Per risolvere il problema, basta impostare su *(Nessuno)* il suono di *Apertura programma*.

Nota: a causa dei limiti della prima versione dei driver video di Windows 95, alcune schede video potrebbero avere difficoltà con i giochi DOS in SVGA. Rivolgiti al produttore della scheda video per avere la versione più recente dei driver video per Windows 95.

Se usi Windows 95 e giochi a Harvester da una sessione DOS, potrebbe essere necessario caricare il driver VESA nel file AUTOEXEC.BAT.

## INFORMAZIONI SULLA SCHEDA AUDIO

Di solito, all'avvio del gioco, Harvester rileva la maggior parte delle schede audio e le relative impostazioni.

<!-- pagina 7 -->

Se però il gioco non parte, puoi eseguire il programma SETSOUND dalla directory in cui hai installato i file del gioco. SETSOUND ti guiderà nel rilevamento o nella scelta dei parametri corretti per la tua scheda audio.

Puoi eseguire SETSOUND anche da Windows 3.1 o da Windows 95: basta fare clic sull'icona *Sound Setup*.

Inoltre, assicurati che siano installati i driver audio appropriati. Insieme alla scheda audio dovrebbe esserti stato fornito un programma di installazione che la configura per funzionare correttamente con i giochi DOS. Se questi driver non sono installati o non sono configurati bene, il gioco potrebbe non funzionare correttamente o bloccare il computer.

## INFORMAZIONI SULLA SCHEDA VIDEO (VESA)

Harvester usa grafica ad alta risoluzione e richiede che il computer sia compatibile VESA. Di solito la compatibilità VESA è data da un driver software fornito dal produttore della scheda video.

All'avvio, il gioco cerca di rilevare se il driver VESA è caricato. Alcuni computer più recenti, però, hanno il supporto VESA integrato nella scheda madre: in questi casi il driver VESA viene attivato automaticamente all'avvio del gioco.

Nota: se, dopo aver lasciato che sia Harvester ad attivare il driver VESA, il computer si blocca o non risponde più, dovrai caricare manualmente il driver VESA nel file AUTOEXEC.BAT perché funzioni correttamente.

<!-- pagina 8 -->

Se non hai un driver VESA per la tua scheda video, nella directory VESA del CD n. 1 trovi i driver VESA più recenti disponibili. Consulta anche il file VESA.TXT, che si trova nella stessa directory VESA. Basta copiare sul disco rigido il driver VESA adatto e aggiungere il nome del driver (di solito VESA.EXE o VESA.COM) al file AUTOEXEC.BAT. Poi riavvia il sistema con il nuovo driver VESA e riprova.

<!-- pagina 9 -->

## AVVIARE HARVESTER DA DOS

Per giocare a Harvester dopo averlo installato:

1. Assicurati che il CD-ROM sia inserito correttamente nell'unità CD-ROM.
2. Spostati nell'unità e nella directory in cui hai installato Harvester.
3. Digita `HARVEST` e premi INVIO per avviare il gioco.

## AVVIARE HARVESTER DA WINDOWS 3.1 O 95

Per giocare a Harvester dopo averlo installato:

1. Assicurati che il CD-ROM sia inserito correttamente nell'unità CD-ROM.
2. Seleziona il gruppo di programmi *Harvester*.
3. Seleziona l'icona *Harvester* e fai clic col tasto sinistro del mouse per avviare il gioco.

## DISINSTALLARE HARVESTER

Per rimuovere Harvester da DOS, esegui il programma UNINSTALL che si trova nella directory in cui avevi installato il programma. In alternativa, seleziona l'icona *Uninstall Harvester* nel gruppo di programmi di Windows.

## NOTE SULLA RIPRODUZIONE DEL FILE .AVI *MAKING OF HARVESTER*

Il file .AVI che si trova sul CD n. 1 usa un programma di compressione/decompressione di nuova generazione, Intel Indeo Interactive™ di Intel. Se il video non viene riprodotto correttamente, seleziona l'icona *Install Intel Indeo* per configurare il computer. Puoi riprodurre il file .AVI selezionando l'icona *The Making of Harvester* oppure con il Lettore multimediale incluso in Windows 95.

<!-- pagina 10 -->

# Giocare a Harvester

L'ambiente di gioco di Harvester è formato da una serie di luoghi in cui puoi fare clic sulle cose, visitarle e conversare con le persone che popolano la cittadina di Harvest. Nel corso del gioco dovrai risolvere enigmi e usare oggetti per portare a termine diversi compiti.

## L'interfaccia di gioco

L'interfaccia del gioco è un semplice sistema punta e clicca: muovi il cursore sullo schermo e selezioni i «punti attivi» con il tasto sinistro del mouse. Quando il cursore passa sopra un punto attivo, assume la forma corrispondente:

[IMMAGINE: cursore Movimento - un uomo che cammina]

**Movimento**\
Cammina fino al punto indicato.

[IMMAGINE: cursore Conversazione - una bocca]

**Conversazione**\
Parla con il personaggio indicato.

[IMMAGINE: cursore Esamina - una lente d'ingrandimento]

**Esamina**\
Esamina l'oggetto indicato.

[IMMAGINE: cursore Usa - un ingranaggio]

**Usa**\
Apri, sposta o aziona il punto o l'oggetto indicato.

[IMMAGINE: cursore Esci - un cartello EXIT]

**Esci**\
Lascia la stanza o il luogo in cui ti trovi.

<!-- pagina 11 -->

## La mappa della città

[IMMAGINE: mappa della città - veduta dall'alto di isolati, strade ed edifici]

Nella parte del gioco ambientata in città ti sposti selezionando uno dei luoghi sulla mappa. La mappa della città compare automaticamente ogni volta che esci dal luogo in cui ti trovi.

## Muovere il personaggio

Muovere Steve (il personaggio che controlli) è semplicissimo: porta il mouse sul punto in cui vuoi andare e fai clic col tasto sinistro quando compare l'icona di *movimento*. Se preferisci, puoi muovere il personaggio anche con i tasti freccia. Il personaggio non si muove se il cursore si trova sopra un oggetto o un punto attivo.

## Parlare con i personaggi

Per parlare con un personaggio, basta portare il cursore del mouse su di lui e premere il tasto sinistro. Quando entri nella modalità dialogo, hai a disposizione più risposte tra cui scegliere. Tieni presente che le risposte che puoi dare a un certo personaggio cambiano dinamicamente a seconda di *quando* gli parli.

I dialoghi di Harvester cambiano dinamicamente anche in base agli altri eventi che si sono verificati nel mondo di Harvest.

<!-- pagina 12 -->

Le risposte di un personaggio possono cambiare *completamente* a seconda di quello che hai fatto e degli eventi che si sono verificati nel mondo di gioco. Parla spesso con i personaggi: ti daranno molti indizi e spunti per risolvere gli enigmi.

## Raccogliere e usare gli oggetti

[IMMAGINE: quattro fotogrammi in sequenza - la lente sopra un oggetto, il cursore che diventa una mano, la mano che afferra l'oggetto, Steve con l'oggetto in mano]

Raccogliere e usare gli oggetti, in Harvester, è facilissimo. Dopo che hai *esaminato* un oggetto, il cursore del mouse si trasforma automaticamente in una *mano* (il cursore Prendi). Per raccogliere un oggetto che hai *esaminato*, basta fare clic col tasto sinistro del mouse quando la *mano* compare sopra quel punto. Il cursore prenderà la forma dell'oggetto appena raccolto. Quando il cursore è un oggetto, puoi metterlo nell'inventario portandolo sopra il tuo personaggio e premendo il tasto sinistro del mouse, oppure semplicemente facendo clic col tasto destro.

[IMMAGINE: riquadro dell'inventario - il catalogo «Harvest Land - Magazzino di mobili» con il pulsante ESCI e la foto di Steve in basso a sinistra]

Se vuoi usare un oggetto su un punto del mondo di gioco, fai clic col tasto sinistro del mouse sul tuo personaggio oppure premi [TASTO: I] per aprire il riquadro dell'inventario. Seleziona l'oggetto che vuoi usare facendo clic col tasto sinistro. Il riquadro dell'inventario scompare automaticamente se sposti il cursore del mouse fuori dai suoi bordi. Per rinunciare a usare un oggetto, fai clic col tasto destro del mouse: l'oggetto tornerà nell'inventario.

<!-- pagina 13 -->

**Puoi anche fare clic col tasto sinistro su un oggetto dell'inventario e «trascinarlo» sopra un altro oggetto dell'inventario. In certi casi si ottiene un nuovo oggetto, che viene messo nell'inventario.**

## Esaminare gli oggetti

Dopo che hai ottenuto certi oggetti, puoi osservarli più da vicino nell'inventario: porta il puntatore sopra l'oggetto e fai clic col tasto destro del mouse. Comparirà un «primo piano» dell'oggetto, con una descrizione più dettagliata. Nota: non tutti gli oggetti si possono vedere da vicino.

## Azionare, aprire e spostare le cose nel mondo di gioco

Nel mondo di Harvester ti capiterà di tanto in tanto di dover *azionare, aprire o spostare* certe zone dello schermo. Facendo clic col tasto sinistro del mouse su questi punti attivi (con il cursore *Usa*), il personaggio può azionarli, aprirli o spostarli.

## Inventario

L'inventario è il posto in cui vengono conservati tutti gli oggetti che raccogli o ottieni durante il gioco. Non c'è limite al numero di oggetti che puoi portare nell'inventario. Per risolvere gli enigmi dovrai aprire spesso l'inventario e fare clic col tasto sinistro sull'oggetto che vuoi usare. Per aprire l'inventario, basta fare clic col tasto sinistro del mouse sul tuo personaggio oppure premere il tasto [TASTO: I] sulla tastiera.

<!-- pagina 14 -->

## Risolvere gli enigmi

Come in ogni avventura, anche in Harvester lo scopo principale è svelare i misteri della cittadina risolvendo enigmi. Gli enigmi cambiano a seconda della situazione in cui ti trovi.

Tra gli enigmi più comuni ci sono quelli che ti chiedono di usare degli oggetti su certi punti del mondo di gioco o su altri oggetti dell'inventario. In questo modo fai accadere degli eventi: per esempio sblocchi porte, apri bauli o consegni oggetti alle persone. Parte del divertimento sta proprio nel provare a usare gli oggetti su luoghi e persone, provocando reazioni interessanti.

**Inoltre, a volte gli enigmi si risolvono azionando certe zone dello schermo che fanno accadere azioni ed eventi.**

## Metodi alternativi per risolvere gli enigmi

In Harvester ci sono molte situazioni in cui esiste *più di un modo corretto per risolvere un enigma*. Alcuni giocatori risolveranno un enigma ragionando sulla soluzione, altri potranno scegliere un approccio più violento.

## Combattimento

Durante il gioco puoi scegliere di uccidere o affrontare un altro personaggio in qualsiasi momento. Ci sono due situazioni in cui puoi decidere di uccidere un mostro o un personaggio nella cittadina di Harvest.

<!-- pagina 15 -->

La prima consiste semplicemente nell'uccidere un personaggio non giocante attaccandolo con il tasto destro del mouse oppure con i tasti [TASTO: CTRL] + [TASTO: frecce]. Basta fare clic col tasto destro del mouse e il tuo personaggio menerà un colpo o farà fuoco con l'arma nella direzione in cui è rivolto.

La seconda è una semplice forma di combattimento che ti costringe a «uccidere o essere ucciso», usando una qualsiasi delle ventuno armi diverse che puoi trovare nel corso del gioco.

[IMMAGINE: cursore Bersaglio - un mirino]

Se combatti il nemico con il mouse, puoi anche concentrare o «dirigere» l'attacco su una parte precisa del corpo dell'avversario, posizionando sopra il nemico il cursore *Bersaglio*. Le zone che puoi colpire sono tre: la parte alta del corpo, il ventre e le gambe. Per attaccare il nemico in una di queste zone, basta portare sopra di lui il cursore Bersaglio e fare clic col tasto destro del mouse.

## Salute

[IMMAGINE: foto Polaroid di Steve con il volto insanguinato]

Durante i combattimenti il tuo personaggio può rimanere ferito. Per sapere quanto sei ferito, fai clic col tasto sinistro del mouse sul tuo personaggio oppure premi [TASTO: I] per aprire l'inventario. Nella parte in basso a sinistra dello schermo c'è una foto del tuo personaggio. Più vieni ferito, più la foto appare insanguinata.

<!-- pagina 16 -->

Se non hai a disposizione oggetti curativi, prima o poi morirai.

**In tutto Harvester troverai oggetti che ti permetteranno di curare il personaggio semplicemente raccogliendoli.**

Nota: usa con giudizio gli oggetti curativi. Per riuscire a uccidere certi nemici dovrai prima curarti.

## Armi

[IMMAGINE: inventario con alcune armi (pistola calibro 9, fucile, forcone, pala) e i messaggi di stato sull'arma impugnata, «clic destro per impugnare o riporre»]

In Harvester ci sono ventuno (21) armi diverse, ognuna con le sue capacità d'attacco. Per esempio, un coltello o i pugni fanno molti meno danni di una motosega o di un fucile da caccia. Fai attenzione a quando attacchi un nemico e all'arma che usi. Alcuni personaggi sono piuttosto potenti e, senza un'arma più forte, potresti subirne le conseguenze... la morte.

Per impugnare o riporre un'arma che hai ottenuto, basta portare il cursore del mouse sull'arma nell'inventario e fare clic col tasto destro. Nota: poiché ogni arma ha capacità d'attacco diverse, impugnarla e riporla richiede qualche istante.

<!-- pagina 17 -->

## Configurare le opzioni di gioco

[IMMAGINE: menu principale - NUOVA PARTITA, SALVA PARTITA, CARICA PARTITA, OPZIONI, AIUTO, ESCI DAL GIOCO sotto il logo di Harvester, davanti al cimitero]

Puoi accedere alle opzioni di gioco premendo il tasto ESC. Dopo aver premuto ESC compariranno le seguenti voci:

### NUOVA PARTITA

Scegli questa voce per cominciare una nuova partita dall'inizio.

### SALVA PARTITA

Questa voce ti permette di salvare la situazione in cui ti trovi. Per salvare la partita, usa il mouse o la tastiera per evidenziare la casella in cui vuoi salvare. Fai clic col tasto sinistro del mouse o premi INVIO per selezionare la casella. Scrivi il nome che vuoi dare alla partita da salvare. Premi INVIO o fai clic sul pulsante SALVA in fondo allo schermo. Ora la partita è salvata in quella posizione.

### CARICA PARTITA

Questa voce ti permette di caricare in memoria una partita salvata in precedenza, così da riprendere a giocare dal punto in cui eri rimasto. Per caricare una partita salvata, evidenzia la casella in cui è salvata e premi INVIO, oppure fai clic col tasto sinistro del mouse per caricarla.

<!-- pagina 18 -->

### OPZIONI

Il menu delle opzioni ti permette di configurare diversi elementi del gioco. Le opzioni disponibili sono le seguenti:

#### EFFETTI

Questa opzione ti permette di regolare il volume degli effetti sonori, con il mouse o con i tasti freccia della tastiera.

#### MUSICA

Questa opzione ti permette di regolare il volume della musica, con il mouse o con i tasti freccia della tastiera.

#### GAMMA

Questa opzione ti permette di regolare il contrasto e la luminosità del gioco (correzione gamma). Alcuni monitor sono più scuri o più chiari di altri: così puoi adattare l'intensità ai tuoi gusti.

#### SOTTOTITOLI

Questa opzione ti permette di scegliere come mostrare il testo dei dialoghi: *NO*, *CLIC* o *SÌ*.

- **NO**\
  Con i sottotitoli su **NO** senti soltanto le voci dei personaggi. Sullo schermo non compare alcun testo.

<!-- pagina 19 -->

- **CLIC**\
  Con i sottotitoli su **CLIC** vedi il testo e senti anche le voci dei personaggi. Con questa impostazione devi fare clic col tasto sinistro del mouse per passare alla battuta successiva, o per saltare quella in corso prima del tempo.
- **SÌ**\
  Con i sottotitoli su **SÌ** vedi il testo e senti anche le voci dei personaggi. Con questa impostazione il gioco passa da solo alla battuta successiva. Puoi comunque fare clic col tasto sinistro del mouse per andare avanti o per saltare la battuta in corso prima del tempo.

#### SANGUE (SÌ/NO)

Questa opzione ti permette di attivare o disattivare le scene di violenza esplicita del gioco.

#### SUGGERIMENTI

Questa opzione ti permette di attivare una serie di suggerimenti di gioco.

#### PASSWORD (SÌ/NO)

Questa opzione ti permette di impostare una password che, una volta attivata, dovrà essere inserita per poter giocare.

<!-- pagina 20 -->

### AIUTO

Questa voce ti permette di vedere la schermata di aiuto.

### ESCI DAL GIOCO

Questa voce ti permette di uscire dal gioco.

<!-- pagina 21 -->

# Riconoscimenti

- **Ideazione e testi**
  - G.P. Austin
- **Produttore**
  - M. Lee Jacobson
- **Programmatore capo**
- **Sviluppo del motore**
  - Nick Shaffner
- **Programmazione**
  - Bruce Mack
  - Dustin Nulf
  - Steve Goodman
- **Progettazione tecnica**
  - Tom Lima
  - M. Lee Jacobson
  - David Mitchell
- **Grafico capo**
  - Chad Woyewodzic
- **Grafici**
  - Michael Napadano
  - Scott Hansen
  - Tim Higgins
  - Jason Lickliter
  - R. Kevin Obregon
  - Craig Rundels
- **Collaudo**
  - Dennis Gyor
  - Steve Woyewodzic
  - Jeff Scott
  - Glen Hansen
  - Libby Smithwick

## Riprese prima unità

- **Regia**
  - G.P. Austin
- **Aiuto regista**
  - Michael Brooks
- **Fotografia/Riprese**
  - John Johns
  - Ultimatte System 7 fornito da In-Sync, Dallas, TX
- **Luci**
  - Allied Lighting
- **Post-produzione audio**
  - Byron Parks
  - Chris Erlon
  - Digital Domain, Austin, TX
- **Capo macchinista**
  - Michael Brooks

<!-- pagina 22 -->

- **Trucco**
  - Barbera Kramer
- **Casting**
  - Peggy Taylor Talent, Inc. - Dallas, TX
- **Produzione scenica**
  - Jim Brovont
  - Jess Brovont

## Riprese seconda unità

- **Regia**
  - G.P. Austin
- **Aiuto regista**
  - Michael Brooks
- **Riprese**
  - Eric Jewel
  - John Cermin
- **Ingegnere Betacam**
  - Pat Gough
- **Gobbo**
  - Becky Hamill
- **Luci e post-produzione audio**
  - David Jewel
  - David Hughes
- **Coordinamento di produzione**
  - Natalie Corey
- **Trucco**
  - Jodi Callahan
- **Girato presso**
  - AMS Productions, Dallas, TX

## Interpreti

- **Sorellina (del protagonista)**
  - Michael Napadano, Jr.
- **Mendicante**
  - Pieter Van Der Vliet
- **Cain**
  - M R Eudy
- **Maestro di Scacchi**
  - Tim Higgins
- **Addetto al guardaroba**
  - Bill Nelson
- **Colonnello Buster Monroe**
  - Graham Teschke
- **Curatore**
  - Charlie Latch
- **Addetto ai cartelli**
  - Mike Napadano
- **Donna bruna esotica**
  - Tracy Napadano
- **Vicesceriffo Loomis**
  - Pieter Van Der Vliet

<!-- pagina 23 -->

- **Edna Fitzpatrick**
  - Roxanne Lovseth
- **Pompiere Sparky**
  - Nick Shaffner
- **Seguace n. 1**
  - Simon
- **Seguace n. 2**
  - Danny Hansard
- **Mamme dell'associazione genitori**
  - Mary Allen
- **Alunno in classe n. 1**
  - Rheagan Wallace
- **Alunno in classe n. 2**
  - Ben Morgan
- **Poliziotto**
  - Pieter Van Der Vliet
- **Gladiatori**
  - John Kaufman
- **Gran Mogol**
  - Jack Irons
- **Hank**
  - Ben Morgan
- **Indiano n. 1**
  - Matt Bentele
- **Indiano n. 2 (in città)**
  - Dennis Gyor
- **Inquisitore**
  - W.D. Hollon
- **Jimmy James**
  - Christopher Ammons
- **Signor Johnson**
  - Bob Cawley
- **Karin**
  - Rheagan Wallace
- **Bambola Kewpie**
  - Tom Lima
- **Signor McKnight**
  - Lee Jacobson
- **Bibliotecaria**
  - Doris McLellan
- **Cuoco della Loggia**
  - Zeb Cash Lane
- **Tenutaria**
  - Karen Sexton
- **Manutentore**
  - Colonel Mason
- **Direttore delle ammissioni**
  - Charlie Beecham
- **Mamma**
  - Mary Allen
- **Moynahan**
  - G.P. Austin
- **Uomo nudo**
  - Michael Brooks

<!-- pagina 24 -->

- **Signor Parsons**
  - Bill Nelson
- **Signor Pastorelli**
  - Colonel Mason
- **Pat O'Reilly**
  - Zeb Cash Lane
- **Signora Phelps**
  - Doris McLellan
- **Direttore delle poste Boyle**
  - Charlie Beecham
- **Signor Pottsdam**
  - Travis Miller
- **Signora Pottsdam**
  - Mary Allen
- **Prete**
  - Jack Brovont
- **Prostituta**
  - Dawn Wells
- **Range Ryder**
  - Charlie Latch
- **Sergente d'armi**
  - R. Kevin Obregon
- **Sceriffo Dwayne**
  - Nelson Knight
- **Stephanie**
  - Lisa Cangelosi
- **Steve (protagonista)**
  - Kurt Kistler
- **Signor Swell**
  - Richard Raski
- **Tecnico n. 1**
  - R. Kevin Obregon
- **Tecnico n. 2**
  - Mike Napadano
- **Uomo torturato**
  - Dean Preston
- **Valletto**
  - Richard Raski
- **Spettatore**
  - Joel Guadarama
- **Signorina Whaley**
  - Karen Sexton
- **Bambina vietnamita**
  - Christine Tran
- **Bambino vietnamita**
  - Michael Tran
- **Mamma vietnamita**
  - Ann Tran
- **Reduce di guerra**
  - John Brook
- **Donna Vespa**
  - Persis Forster
- **Elettricista zombi**
  - Ed Woyewodzic
- **Dalmata**
  - il cane di Matt

<!-- pagina 25 -->

# Assistenza clienti

Se hai problemi con Harvester e sei un utente registrato, puoi chiamare il nostro reparto di assistenza tecnica al numero (214) 385-2957. Un tecnico sarà a tua disposizione dalle 10:00 alle 17:00, ora centrale degli Stati Uniti, dal lunedì al venerdì.

Domande, commenti e osservazioni di ogni genere su Harvester o su qualsiasi altro nostro prodotto sono sempre graditi. Puoi scriverci a questo indirizzo:

Merit Studios\
13707 Gamma Road\
Dallas, Texas 75244

Per le ultime informazioni di assistenza tecnica su Harvester e gli annunci dei nuovi prodotti, visita questi siti sul World Wide Web:

Merit Studios - www.softdisk.com/comp/merit\
DigiFX Interactive - www.digifx.net

## Assistenza in linea tramite CompuServe

Per l'assistenza in linea su Harvester tramite CompuServe, chiama il numero 800-848-8199 e chiedi del Rappresentante 321: avrai l'iscrizione introduttiva GRATUITA e 15 dollari di credito d'uso. Se sei già iscritto a CompuServe, digita il comando GO GAMAPUB a un qualsiasi prompt «!» per accedere alla sezione di assistenza di Merit Studios, oppure contatta il nostro reparto di assistenza tecnica all'ID 76711,247.

*Informazioni dell'edizione originale del 1996: numeri, indirizzi e servizi non sono più attivi.*

<!-- pagina 26 -->

# CONTRATTO DI LICENZA DEL PROGRAMMA E GARANZIA LIMITATA DI MERIT STUDIOS

*Traduzione di cortesia. Fa fede il testo inglese originale.*

LEGGI ATTENTAMENTE TUTTI I TERMINI E LE CONDIZIONI DEL PRESENTE CONTRATTO PRIMA DI USARE IL PROGRAMMA REGISTRATO SUI DISCHETTI O SUI CD. L'USO DI QUESTO PROGRAMMA COMPORTA L'ACCETTAZIONE DI TALI TERMINI E CONDIZIONI.

**COPYRIGHT:** QUESTI PROGRAMMI E LA RELATIVA DOCUMENTAZIONE SONO PROTETTI DA COPYRIGHT. NON PUOI USARE, COPIARE, MODIFICARE O TRASFERIRE I PROGRAMMI O LA DOCUMENTAZIONE, NÉ ALCUNA LORO COPIA, SALVO QUANTO ESPRESSAMENTE PREVISTO DAL PRESENTE CONTRATTO.

**LICENZA:** Hai il diritto non esclusivo di usare ciascun programma accluso su un solo computer. Puoi caricare il programma nella memoria temporanea (RAM) del computer. Puoi trasferire fisicamente il programma da un computer a un altro, a condizione che il programma sia usato su un solo computer alla volta. Puoi modificare o tradurre il programma, a condizione che la modifica o la traduzione sia per tuo uso personale e che non esista più di una copia modificata o tradotta alla volta. Non puoi trasferire elettronicamente il programma né accedervi da un altro computer attraverso una rete. Non puoi distribuire ad altri copie del programma o della documentazione che lo accompagna. Non puoi decompilare, disassemblare o in altro modo decodificare il programma (reverse engineering). Non puoi tentare di sbloccare o aggirare le protezioni contro la copia usate dal programma. La titolarità dei programmi e tutti gli altri diritti e usi non espressamente concessi dalla presente licenza sono riservati a MERIT STUDIOS.

**COPIA DI RISERVA E TRASFERIMENTO:** Puoi fare una (1) copia del programma esclusivamente a scopo di riserva (backup). Devi riprodurre e includere l'avviso di copyright sulla copia di riserva. Puoi trasferire il prodotto e cederne la licenza a terzi solo se questi accettano i termini e le condizioni del presente Contratto e compilano e rispediscono una cartolina di registrazione a MERIT STUDIOS. Se trasferisci il programma, devi contemporaneamente trasferire la documentazione e la copia di riserva, oppure trasferire la documentazione e distruggere la copia di riserva.

**DURATA:** La presente licenza è valida fino alla sua risoluzione. Puoi risolverla distruggendo il programma, la documentazione e tutte le loro copie. La licenza si risolve inoltre se non rispetti uno qualsiasi dei termini o delle condizioni del presente Contratto. In caso di risoluzione, ti impegni a distruggere tutte le copie del programma e della documentazione.

**ESCLUSIONI DI GARANZIA SUL PROGRAMMA: I programmi sono forniti «COSÌ COME SONO», senza garanzie di alcun tipo, esplicite o implicite, comprese, a titolo esemplificativo, le garanzie implicite di commerciabilità e di idoneità a uno scopo particolare. Tutti i rischi relativi ai risultati e alle prestazioni di qualsiasi programma sono a tuo carico.** Se il programma dovesse rivelarsi difettoso, sarai tu (e non MERIT STUDIOS o i suoi rivenditori) a sostenere l'intero costo di tutti gli interventi di assistenza, riparazione o correzione necessari. Inoltre MERIT STUDIOS non garantisce né assicura alcunché e non rilascia alcuna dichiarazione riguardo all'uso del programma o ai risultati del suo uso, in termini di idoneità, precisione, affidabilità, aggiornamento o altro; ti affidi al programma e ai suoi risultati esclusivamente a tuo rischio.

<!-- pagina 27 -->

**GARANZIA LIMITATA SUI SUPPORTI:** MERIT STUDIOS garantisce al licenziatario originale che i supporti su cui è registrato il programma sono esenti da difetti di materiale e di fabbricazione, solo per un periodo di novanta (90) giorni dalla data dell'acquisto originale. Se durante questo periodo di garanzia di 90 giorni si manifesta un difetto coperto dalla garanzia, e il prodotto viene restituito a MERIT STUDIOS entro cinque (5) giorni dalla fine di tale periodo di 90 giorni, MERIT STUDIOS provvederà a sostituire o riparare il prodotto. Alla scadenza della garanzia, MERIT STUDIOS sostituirà o riparerà il prodotto acquistato al prezzo di 5 dollari.

La garanzia di cui sopra è esclusiva e sostituisce tutte le altre condizioni e garanzie, esplicite o implicite, comprese, a titolo esemplificativo, le condizioni o garanzie implicite di commerciabilità o di idoneità a uno scopo particolare e quelle derivanti dalla legge o altrimenti dal diritto o dalle consuetudini commerciali. Nella misura in cui tali leggi o norme vietino l'esclusione di dette garanzie implicite, queste saranno limitate a un periodo di 90 giorni dalla data dell'acquisto originale. Trascorso tale periodo non si applicherà alcuna condizione o garanzia, né esplicita né implicita.

**LIMITAZIONE DI RESPONSABILITÀ: La responsabilità di MERIT Studios è limitata esclusivamente alla riparazione o alla sostituzione del prodotto difettoso, a sua discrezione, e non comprenderà in alcun caso danni per mancato uso o per perdita di profitti o benefici attesi, né altri costi, spese o danni incidentali o consequenziali, compresi, senza limitazione, dati o informazioni eventualmente andati perduti o resi inesatti, anche qualora MERIT STUDIOS sia stata avvertita della possibilità di tali danni.**

Alcuni stati non consentono l'esclusione delle garanzie implicite o la limitazione dei danni incidentali o consequenziali, quindi le limitazioni o esclusioni di cui sopra potrebbero non applicarsi nel tuo caso. La presente garanzia ti conferisce specifici diritti legali; potresti avere anche altri diritti, che variano da stato a stato.

**DISPOSIZIONI VARIE:** Il presente contratto costituisce l'intero accordo relativo ai programmi e alla relativa documentazione e sostituisce qualsiasi precedente ordine d'acquisto, comunicazione o dichiarazione. Il presente contratto può essere modificato solo con un emendamento scritto firmato da un dirigente di MERIT STUDIOS. Se una qualsiasi disposizione del contratto dovesse essere ritenuta illecita, nulla o, per qualsiasi motivo, inapplicabile, sarà considerata separabile dal contratto e non pregiudicherà in alcun modo la validità e l'applicabilità delle restanti disposizioni.

Il presente contratto di licenza è regolato dalle leggi degli Stati Uniti d'America, Stato del Texas. Se questo prodotto viene acquistato dagli Stati Uniti d'America, dalle loro agenzie e/o dai loro enti, o per loro conto, viene fornito con DIRITTI LIMITATI (RESTRICTED RIGHTS), e ogni uso, riproduzione o divulgazione del software e della documentazione acclusi è soggetto alle restrizioni stabilite dalla clausola «Rights in Technical Data and Computer Software» al punto 252.227-7013 del DOD FAR e dalla clausola «Rights in Data-General» al punto 52.227-14 del FAR. Salvo diversa indicazione, il produttore/integratore è Merit Studios, 13707 Gamma Road, Dallas, TX 75244.

**Il Contratto di licenza del programma** va a beneficio di Merit Studios, della sua società controllante e di tutte le società a essa affiliate.

Merit Studios e i loghi Merit sono marchi di Merit Software, Inc.
