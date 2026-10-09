# Sottotitoli ai filmati di Harvester: codice aggiunto a HARVEST.EXE.
#
# Sta al posto di compress_fst (il compressore dei filmati usato dagli
# sviluppatori, mai chiamato dal gioco) e si aggancia a decompress_fst:
#   0x12b06  jmp inizio          (al posto di sub esp,0x148)
#   0x1311c  call destinazione   (al posto di mov eax,[edx+0x38] / mov [esp+0xd4],eax)
#   0x131f8  call schermo        (al posto di mov eax,0xa0000 a fine censura)
#   0x13275  jne fotogramma_censurato (al posto di jne 0x12fe7: GORE=NO)
#   0x136a2  jge fine_fotogramma (al posto di jge 0x12fe7)
# Se il filmato ha sottotitoli in SOTTOTIT.ITA (cartella del gioco), l'opzione
# TEXT non è NO e il filmato è a 320x200, il decodificatore scrive in un buffer;
# a fine fotogramma il buffer va sullo schermo spostato in su di 16 righe e
# nella fascia 168-199 si disegna il sottotitolo col font dei testi del gioco
# (bianco con contorno nero, scelti nella tavolozza del filmato). Nei tratti
# censurati (GORE=NO) sul cartello CENSORED resta solo la fascia.
# Negli altri casi il gioco fa esattamente quello che faceva.
#
# Lo stato sta in un blocco allocato una volta, il cui indirizzo è nella
# globale block_list (usata solo da compress_fst). I riferimenti alle globali
# hanno l'indirizzo come ultimi 4 byte dell'istruzione, seguiti da un'etichetta
# fx_*: exe_patch vi sposta le fixup del codice sostituito.
#
# SOTTOTIT.ITA: 'SOTT', u32 dimensione, u32 numero di filmati, u16 avanzamento
# dello spazio, u16 0; per ogni filmato 20 byte: nome[12] in maiuscolo, u32
# posizione dei sottotitoli, u32 quanti; per ogni sottotitolo 8 byte: u16 primo
# fotogramma, u16 fotogramma dopo l'ultimo, u32 posizione del testo; il testo è
# una serie di righe u16 x, u16 y, caratteri, 0, chiusa da x = 0xffff.

.intel_syntax noprefix
.code32
.text

.set RITORNO_INIZIO, 0x12b0c
.set PROSSIMO_FOTOGRAMMA, 0x12fe7
.set NMALLOC, 0x81493
.set OPEN, 0x81576
.set READ, 0x81f63
.set CLOSE, 0x81f10
# offset nell'oggetto dati: il caricatore li sostituisce con l'indirizzo vero
.set BLOCK_LIST, 0x17e70
.set TEXT_DIALOG, 0x17e58
.set TEXTFONT, 0x25bc4

# stato
.set S_BUF, 0          # buffer dei fotogrammi (64000 byte)
.set S_FILE, 4         # SOTTOTIT.ITA in memoria, -1 se manca
.set S_CUE, 8          # sottotitoli del filmato corrente (0 = nessuno)
.set S_NCUE, 12
.set S_ATTIVO, 16
.set S_VRAM, 20        # memoria video vera
.set S_SPAZIO, 24
.set S_FONT, 28
.set S_X, 32
.set S_Y, 36
.set S_GW, 40
.set S_GH, 44
.set S_PASSO, 48
.set S_BIANCO, 52
.set S_NERO, 53
.set S_SFONDO, 54
.set S_PASSATA, 55
.set S_ULTIMO, 56      # testo disegnato nella fascia (per non ridisegnarlo)
.set S_COLORI, 60      # bianco, nero, sfondo con cui è stato disegnato
.set S_CENS, 64        # 1 se il fotogramma precedente era censurato
.set S_DIM, 68

.globl inizio
inizio:
        sub     esp, 0x148
        pushad
        mov     esi, eax                        # nome del filmato
        mov     eax, DWORD PTR ds:BLOCK_LIST
fx_bl_1:
        test    eax, eax
        jnz     1f
        mov     eax, S_DIM
        call    NMALLOC
        test    eax, eax
        jz      .Lfine_inizio
        mov     edi, eax
        mov     edx, eax
        xor     eax, eax
        mov     ecx, S_DIM / 4
        rep     stosd
        mov     eax, edx
        mov     DWORD PTR ds:BLOCK_LIST, eax
fx_bl_2:
1:      mov     ebx, eax
        mov     DWORD PTR [ebx + S_CUE], 0
        mov     DWORD PTR [ebx + S_ATTIVO], 0
        mov     DWORD PTR [ebx + S_ULTIMO], -1
        movzx   eax, BYTE PTR ds:TEXT_DIALOG
fx_td:
        test    eax, eax
        jz      .Lfine_inizio
        cmp     DWORD PTR [ebx + S_FILE], 0
        jne     2f
        call    carica
2:      mov     edi, [ebx + S_FILE]
        cmp     edi, -1
        je      .Lfine_inizio
        # edx = nome senza percorso
        mov     edx, esi
3:      mov     al, [esi]
        inc     esi
        test    al, al
        jz      4f
        cmp     al, '\\'
        je      5f
        cmp     al, '/'
        je      5f
        cmp     al, ':'
        jne     3b
5:      mov     edx, esi
        jmp     3b
4:      mov     ecx, [edi + 8]
        lea     ebp, [edi + 16]
6:      test    ecx, ecx
        jz      .Lfine_inizio
        xor     esi, esi
7:      mov     al, [edx + esi]
        cmp     al, 'a'
        jb      8f
        cmp     al, 'z'
        ja      8f
        sub     al, 0x20
8:      cmp     al, [ebp + esi]
        jne     9f
        test    al, al
        jz      10f
        inc     esi
        cmp     esi, 12
        jb      7b
        cmp     BYTE PTR [edx + esi], 0
        je      10f
9:      add     ebp, 20
        dec     ecx
        jmp     6b
10:     mov     eax, [ebp + 12]
        add     eax, edi
        mov     [ebx + S_CUE], eax
        mov     eax, [ebp + 16]
        mov     [ebx + S_NCUE], eax
        movzx   eax, WORD PTR [edi + 12]
        mov     [ebx + S_SPAZIO], eax
        # buffer dei fotogrammi: allocato la prima volta, azzerato a ogni filmato
        mov     eax, [ebx + S_BUF]
        test    eax, eax
        jnz     11f
        mov     eax, 64000
        call    NMALLOC
        mov     [ebx + S_BUF], eax
        test    eax, eax
        jnz     11f
        mov     DWORD PTR [ebx + S_CUE], 0
        jmp     .Lfine_inizio
11:     mov     edi, eax
        xor     eax, eax
        mov     ecx, 16000
        rep     stosd
.Lfine_inizio:
        popad
        jmp     RITORNO_INIZIO

# Carica SOTTOTIT.ITA. ebx = stato; imposta S_FILE (-1 se non c'è o è guasto).
carica:
        pushad
        mov     DWORD PTR [ebx + S_FILE], -1
        call    1f
1:      pop     eax
        add     eax, OFFSET nome_file - 1b
        push    0x200                           # O_RDONLY | O_BINARY
        push    eax
        call    OPEN
        add     esp, 8
        cmp     eax, -1
        je      .Lc_fine
        mov     esi, eax                        # descrittore
        sub     esp, 8
        mov     edx, esp
        mov     ebx, 8
        call    READ                            # intestazione: 'SOTT', dimensione
        cmp     eax, 8
        jne     .Lc_chiudi8
        cmp     DWORD PTR [esp], 0x54544f53     # 'SOTT'
        jne     .Lc_chiudi8
        mov     eax, [esp + 4]
        cmp     eax, 16
        jb      .Lc_chiudi8
        cmp     eax, 0x100000
        ja      .Lc_chiudi8
        mov     edi, eax                        # dimensione
        call    NMALLOC
        test    eax, eax
        jz      .Lc_chiudi8
        mov     ebp, eax
        mov     ecx, [esp]
        mov     [ebp], ecx
        mov     [ebp + 4], edi
        lea     edx, [ebp + 8]
        lea     ebx, [edi - 8]
        mov     eax, esi
        call    READ
        lea     ecx, [edi - 8]
        cmp     eax, ecx
        jne     .Lc_chiudi8
        mov     ebx, [esp + 8 + 16]             # stato (ebx salvato da pushad)
        mov     [ebx + S_FILE], ebp
.Lc_chiudi8:
        add     esp, 8
        mov     eax, esi
        call    CLOSE
.Lc_fine:
        popad
        ret

# Chiamata a 0x1311c: eax = destinazione dei blocchi (memoria video o buffer).
.globl destinazione
destinazione:
        mov     eax, [edx + 0x38]
        push    ebx
        mov     ebx, DWORD PTR ds:BLOCK_LIST
fx_bl_3:
        test    ebx, ebx
        jz      1f
        mov     DWORD PTR [ebx + S_ATTIVO], 0
        cmp     DWORD PTR [ebx + S_CUE], 0
        je      1f
        cmp     DWORD PTR [esp + 8 + 0x8c], 0x140
        jne     1f
        mov     [ebx + S_VRAM], eax
        mov     eax, [ebx + S_BUF]
        mov     DWORD PTR [ebx + S_ATTIVO], 1
1:      pop     ebx
        mov     [esp + 4 + 0xd4], eax
        ret

# Chiamata a 0x131f8 (fine di un tratto censurato): eax = cosa azzerare.
.globl schermo
schermo:
        mov     eax, 0xa0000
        push    ebx
        mov     ebx, DWORD PTR ds:BLOCK_LIST
fx_bl_4:
        test    ebx, ebx
        jz      1f
        cmp     DWORD PTR [ebx + S_ATTIVO], 0
        je      1f
        mov     eax, [ebx + S_BUF]
        mov     DWORD PTR [ebx + S_ULTIMO], -1  # il cartello ha coperto la fascia
1:      pop     ebx
        ret

# Destinazione del salto di fine fotogramma (0x136a2).
.globl fine_fotogramma
fine_fotogramma:
        pushad
        mov     ebx, DWORD PTR ds:BLOCK_LIST
fx_bl_5:
        test    ebx, ebx
        jz      1f
        cmp     DWORD PTR [ebx + S_ATTIVO], 0
        je      1f
        mov     BYTE PTR [ebx + S_CENS], 0
        mov     ecx, [esp + 32 + 0xdc]          # fotogramma corrente
        mov     eax, DWORD PTR ds:TEXTFONT
fx_tf:
        mov     [ebx + S_FONT], eax
        call    presenta
1:      popad
        jmp     PROSSIMO_FOTOGRAMMA

# Destinazione del salto dei fotogrammi censurati (0x13275).
.globl fotogramma_censurato
fotogramma_censurato:
        pushad
        mov     ebx, DWORD PTR ds:BLOCK_LIST
fx_bl_6:
        test    ebx, ebx
        jz      1f
        cmp     DWORD PTR [ebx + S_ATTIVO], 0
        je      1f
        cmp     BYTE PTR [ebx + S_CENS], 0
        jne     2f
        mov     BYTE PTR [ebx + S_CENS], 1
        mov     DWORD PTR [ebx + S_ULTIMO], -1  # il cartello ha coperto la fascia
2:      mov     ecx, [esp + 32 + 0xdc]
        mov     eax, DWORD PTR ds:TEXTFONT
fx_tf_2:
        mov     [ebx + S_FONT], eax
        push    ecx
        call    colori
        mov     al, [ebx + S_NERO]
        mov     [ebx + S_SFONDO], al
        pop     ecx
        call    fascia
1:      popad
        jmp     PROSSIMO_FOTOGRAMMA

# Bianco e nero: luminanza massima e minima nella tavolozza attuale (DAC).
# ebx = stato; sporca eax, ecx, edx, esi, edi, ebp.
colori:
        mov     dx, 0x3c7
        xor     eax, eax
        out     dx, al
        mov     dx, 0x3c9
        xor     ecx, ecx
        mov     edi, -1
        mov     ebp, 0x7fffffff
1:      in      al, dx
        movzx   esi, al
        lea     esi, [esi + esi * 2]
        in      al, dx
        movzx   eax, al
        lea     eax, [eax + eax * 2]
        lea     esi, [esi + eax * 2]
        in      al, dx
        movzx   eax, al
        add     esi, eax
        cmp     esi, edi
        jle     2f
        mov     edi, esi
        mov     [ebx + S_BIANCO], cl
2:      cmp     esi, ebp
        jge     3f
        mov     ebp, esi
        mov     [ebx + S_NERO], cl
3:      inc     ecx
        cmp     ecx, 256
        jb      1b
        ret

# Fotogramma normale. ebx = stato, ecx = fotogramma.
presenta:
        push    ecx
        call    colori
        # colore della fascia: quello del bordo sinistro del filmato
        mov     esi, [ebx + S_BUF]
        mov     al, [esi + 100 * 320]
        mov     [ebx + S_SFONDO], al
        # immagine spostata in su di 16 righe
        add     esi, 16 * 320
        mov     edi, [ebx + S_VRAM]
        mov     ecx, 168 * 320 / 4
        rep     movsd
        pop     ecx

# La fascia 168-199 col sottotitolo del fotogramma ecx (S_SFONDO già scelto).
fascia:
        xor     ebp, ebp
        mov     esi, [ebx + S_CUE]
        mov     edx, [ebx + S_NCUE]
4:      test    edx, edx
        jz      6f
        movzx   eax, WORD PTR [esi]
        cmp     ecx, eax
        jb      5f
        movzx   eax, WORD PTR [esi + 2]
        cmp     ecx, eax
        jae     5f
        mov     ebp, [esi + 4]
        add     ebp, [ebx + S_FILE]
        jmp     6f
5:      add     esi, 8
        dec     edx
        jmp     4b
        # la fascia si ridisegna solo se cambiano testo o colori
6:      mov     eax, [ebx + S_BIANCO]
        and     eax, 0xffffff
        cmp     ebp, [ebx + S_ULTIMO]
        jne     7f
        cmp     eax, [ebx + S_COLORI]
        je      .Lp_fine
7:      mov     [ebx + S_ULTIMO], ebp
        mov     [ebx + S_COLORI], eax
        movzx   eax, BYTE PTR [ebx + S_SFONDO]
        imul    eax, eax, 0x01010101
        mov     edi, [ebx + S_VRAM]
        add     edi, 168 * 320
        mov     ecx, 32 * 320 / 4
        rep     stosd
        test    ebp, ebp
        jz      .Lp_fine
        cmp     DWORD PTR [ebx + S_FONT], 0
        je      .Lp_fine
        mov     BYTE PTR [ebx + S_PASSATA], 0   # prima il contorno, poi il corpo
8:      mov     esi, ebp
9:      movzx   eax, WORD PTR [esi]
        cmp     eax, 0xffff
        je      10f
        movzx   edx, WORD PTR [esi + 2]
        add     esi, 4
        call    riga
        jmp     9b
10:     inc     BYTE PTR [ebx + S_PASSATA]
        cmp     BYTE PTR [ebx + S_PASSATA], 2
        jb      8b
.Lp_fine:
        ret

# Disegna una riga: eax = x, edx = y, esi = testo (avanza oltre lo 0). Preserva ebp.
riga:
        push    ebp
        mov     [ebx + S_X], eax
        mov     [ebx + S_Y], edx
1:      movzx   ecx, BYTE PTR [esi]
        inc     esi
        test    ecx, ecx
        jz      .Lr_fine
        cmp     ecx, ' '
        je      5f
        cmp     ecx, '_'
        je      5f
        mov     ebp, [ebx + S_FONT]
        movzx   edi, WORD PTR [ebp + 0x242 + ecx * 2]
        mov     [ebx + S_GW], edi
        movzx   eax, WORD PTR [ebp + 0x42 + ecx * 2]
        movzx   ecx, WORD PTR [ebp + 0x40]
        mov     [ebx + S_GH], ecx
        mov     edx, [ebp + 0x444]              # striscia dei caratteri
        mov     ecx, [edx]
        mov     [ebx + S_PASSO], ecx
        push    esi
        mov     esi, [edx + 8]
        add     esi, eax
        xor     edx, edx                        # riga del carattere
2:      xor     ecx, ecx                        # colonna
3:      movzx   eax, BYTE PTR [esi + ecx]
        test    eax, eax
        jz      4f
        call    pixel
4:      inc     ecx
        cmp     ecx, [ebx + S_GW]
        jb      3b
        add     esi, [ebx + S_PASSO]
        inc     edx
        cmp     edx, [ebx + S_GH]
        jb      2b
        pop     esi
        mov     eax, [ebx + S_GW]
        add     [ebx + S_X], eax
        jmp     1b
5:      mov     eax, [ebx + S_SPAZIO]
        add     [ebx + S_X], eax
        jmp     1b
.Lr_fine:
        pop     ebp
        ret

# eax = valore del pixel nel font, ecx = colonna, edx = riga. Preserva tutto.
# Valori 1 e 32 sono l'ombra del font: nel contorno sì, nel corpo no.
pixel:
        pushad
        add     ecx, [ebx + S_X]
        add     edx, [ebx + S_Y]
        cmp     BYTE PTR [ebx + S_PASSATA], 0
        jne     5f
        mov     al, [ebx + S_NERO]
        lea     esi, [edx - 1]
        lea     ebp, [edx + 2]
1:      cmp     esi, 200
        jae     3f
        imul    edi, esi, 320
        add     edi, [ebx + S_VRAM]
        lea     edx, [ecx - 1]
        mov     ah, 3
2:      cmp     edx, 320
        jae     4f
        mov     [edi + edx], al
4:      inc     edx
        dec     ah
        jnz     2b
3:      inc     esi
        cmp     esi, ebp
        jne     1b
        jmp     9f
5:      cmp     eax, 1
        je      9f
        cmp     eax, 32
        je      9f
        cmp     edx, 200
        jae     9f
        cmp     ecx, 320
        jae     9f
        imul    edi, edx, 320
        add     edi, [ebx + S_VRAM]
        mov     al, [ebx + S_BIANCO]
        mov     [edi + ecx], al
9:      popad
        ret

nome_file:
        .asciz  "SOTTOTIT.ITA"
        .balign 4
.globl zavorra
zavorra:                # le fixup del codice sostituito che non servono scrivono qui
        .long   0
.globl fine_codice
fine_codice:
