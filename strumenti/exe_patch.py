"""Applica traduzioni di stringhe a HARVEST.EXE (LE, DOS/4G).

Una stringa tradotta che entra nello spazio dell'originale viene scritta lì.
Se è più lunga viene messa in un'area 'donatrice' (stringhe di debug che il
gioco non mostra mai, i cui riferimenti vengono deviati su una stringa vuota) e
tutte le fixup che puntavano all'originale vengono deviate sulla copia nuova.
Le aree donatrici stanno nell'oggetto dati sotto i 64 KB, perché molte fixup
hanno il campo di destinazione a 16 bit."""
import struct, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import le as L

# Stringhe di debug dell'animazione ('state = facing_forward' ...): file offset
# [inizio, fine) nell'eseguibile originale v1.0.
DONATRICI = [(0xfca6e, 0xfcf24)]


class Patch:
    def __init__(self, data):
        self.d = bytearray(data)
        self.le = L.LE(bytes(data), *self._trova())
        self.recs = L.fixup_records(self.le)
        self.per_dest = {}
        for r in self.recs:
            if r['toff'] is None:
                continue
            lin = self.le.objs[r['tobj'] - 1]['base'] + r['toff']
            self.per_dest.setdefault(lin, []).append(r)
        self.liberi = []          # (file_off, fine)
        self.vuota = None
        self.log = []

    def _trova(self):
        d = bytes(self.d)
        i = d.find(b'LE\0\0')
        while i >= 0:
            j = d.rfind(b'MZ', 0, i)
            while j >= 0:
                if j + struct.unpack_from('<I', d, j + 0x3c)[0] == i:
                    return i, j
                j = d.rfind(b'MZ', 0, j)
            i = d.find(b'LE\0\0', i + 1)
        raise ValueError('LE non trovato')

    def lin(self, fo):
        return self.le.file2lin(fo)

    def stringa(self, fo):
        return bytes(self.d[fo:self.d.index(0, fo)])

    def devia(self, da_lin, a_lin):
        """Sposta tutte le fixup che puntano a da_lin su a_lin (stesso oggetto dati)."""
        ob = self.le.objs[2]
        n = 0
        for r in self.per_dest.get(da_lin, []):
            nuovo = a_lin - self.le.objs[r['tobj'] - 1]['base']
            if r['tobj'] != 3:
                raise ValueError('fixup verso oggetto inatteso')
            if r['w_off'] == 2 and nuovo > 0xffff:
                raise ValueError(f'destinazione {a_lin:#x} fuori dai 16 bit')
            struct.pack_into('<H' if r['w_off'] == 2 else '<I', self.d, r['pos_off'], nuovo)
            r['toff'] = nuovo
            n += 1
        self.per_dest.setdefault(a_lin, []).extend(self.per_dest.pop(da_lin, []))
        return n

    def prepara_donatrici(self):
        # stringa vuota: il primo byte 0 preceduto da 0 nell'area dati bassa
        for a, b in DONATRICI:
            p = a
            while p < b:
                s = self.stringa(p)
                lp = self.lin(p)
                if self.vuota is None:
                    self.vuota = self.lin(b - 1) if self.d[b - 1] == 0 else None
                p += len(s) + 1
        # cerca una stringa vuota referenziata fuori dalle donatrici
        for lin, rs in self.per_dest.items():
            fo = self.le.lin2file(lin)
            if fo and self.d[fo] == 0 and not any(a <= fo < b for a, b in DONATRICI) and lin - self.le.objs[2]['base'] < 0x10000:
                self.vuota = lin
                break
        for a, b in DONATRICI:
            p = a
            while p < b:
                s = self.stringa(p)
                n = self.devia(self.lin(p), self.vuota)
                # niente fixup deve puntare dentro la stringa
                for k in range(1, len(s) + 1):
                    if self.lin(p + k) in self.per_dest:
                        raise ValueError(f'fixup dentro una stringa donatrice a {p + k:#x}')
                p += len(s) + 1
            self.d[a:b] = bytes(b - a)
            self.liberi.append([a, b])

    def alloca(self, n):
        for z in self.liberi:
            if z[1] - z[0] >= n:
                fo = z[0]
                z[0] += n
                return fo
        raise ValueError(f'spazio donatore esaurito ({n} byte richiesti)')

    def sostituisci(self, fo, nuova):
        """fo: offset nel file dell'inizio della stringa originale."""
        vecchia = self.stringa(fo)
        for k in range(1, len(vecchia) + 1):
            if self.lin(fo + k) in self.per_dest:
                raise ValueError(f'fixup dentro la stringa a {fo:#x}+{k}: non si può accorciare/spostare')
        if len(nuova) <= len(vecchia):
            self.d[fo:fo + len(vecchia)] = nuova + bytes(len(vecchia) - len(nuova))
            self.log.append(f'{fo:#x} in place')
        else:
            dove = self.alloca(len(nuova) + 1)
            self.d[dove:dove + len(nuova) + 1] = nuova + b'\0'
            n = self.devia(self.lin(fo), self.lin(dove))
            if n == 0:
                raise ValueError(f'nessun riferimento alla stringa {fo:#x}')
            self.log.append(f'{fo:#x} -> {dove:#x} ({n} rif.)')

    def patch_byte(self, fo, vecchi, nuovi):
        if bytes(self.d[fo:fo + len(vecchi)]) != vecchi:
            raise ValueError(f'byte inattesi a {fo:#x}')
        self.d[fo:fo + len(nuovi)] = nuovi


# ------------------------------------------------------------------ gioco senza CD
# HARVEST.EXE v1.0 contiene una modalità di sviluppo: con la chiave NETWORK nel
# CONFIG.INI il cambio di disco non controlla il lettore ma riscrive CD_ROM e
# DRIVE_1..3 con i percorsi G:\HARVFNL\{TOWN1,TOWN2,LODGE}\ (funzione 0x488a0).
# Qui: i percorsi diventano C:\HARVEST\CD1..3\ e, se NETWORK è impostata, la
# schermata "inserisci il CD" viene saltata del tutto. Senza NETWORK nel
# CONFIG.INI il gioco si comporta come l'originale.
PERCORSI_RETE = [('G:\\HARVFNL\\TOWN1\\', 'C:\\HARVEST\\CD1\\'), ('G:\\HARVFNL\\TOWN2\\', 'C:\\HARVEST\\CD2\\'),
                 ('G:\\HARVFNL\\LODGE\\', 'C:\\HARVEST\\CD3\\')]


def _rel32(da, a):
    return struct.pack('<i', a - da)


def patch_senza_cd(p):
    d = p.d
    lin2 = lambda lin: p.le.lin2file(lin)
    def atteso(lin, b):
        fo = lin2(lin)
        if bytes(d[fo:fo + len(b)]) != b:
            raise ValueError(f'byte inattesi a {lin:#x}: {bytes(d[fo:fo+len(b)]).hex()}')
    # 1. percorsi
    n = 0
    for vecchio, nuovo in PERCORSI_RETE:
        for coda in ('HARVEST.DAT', 'SOUND.DAT', 'HARVEST2.DAT', ''):
            v = (vecchio + coda).encode()
            i = d.find(b'\0' + v + b'\0')
            while i >= 0:
                p.sostituisci(i + 1, (nuovo + coda).encode())
                n += 1
                i = d.find(b'\0' + v + b'\0', i + 1)
    # 2. salto della schermata del CD
    atteso(0x488ad, bytes.fromhex('8945f48855fc'))
    atteso(0x48bac, bytes.fromhex('ba'))
    atteso(0x48bb1, bytes.fromhex('b8'))
    atteso(0x48bb6, b'\xe8' + _rel32(0x48bbb, 0x7d7d0))
    atteso(0x48bbb, bytes.fromhex('85c07429'))
    cave = bytearray()
    cave += b'\xeb' + bytes([0x48be8 - 0x48bae])                 # 48bac: jmp 48be8 (ramo originale)
    cave += bytes.fromhex('8945f4') + bytes.fromhex('8855fc')     # 48bae: istruzioni spostate
    cave += b'\xba' + struct.pack('<I', 0x9443)                   # 48bb4: mov edx, "NETWORK"
    cave += b'\xb8' + struct.pack('<I', 0x32438)                  # 48bb9: mov eax, config
    cave += b'\xe8' + _rel32(0x48bc3, 0x7d7d0)                    # 48bbe: call leggi_config
    cave += bytes.fromhex('85c0')                                 # 48bc3: test eax, eax
    cave += b'\x0f\x85' + _rel32(0x48bcb, 0x48ce3)                # 48bc5: jne cambio percorsi
    cave += b'\xe9' + _rel32(0x48bd0, 0x488b3)                    # 48bcb: jmp corpo originale
    cave += b'\xcc' * (0x48be8 - 0x48bac - len(cave))
    fo = lin2(0x48bac)
    d[fo:fo + len(cave)] = cave
    fo = lin2(0x488ad)
    d[fo:fo + 6] = b'\xe9' + _rel32(0x488b2, 0x48bae) + b'\x90'
    # fixup: le due che servono seguono le istruzioni, le altre finiscono su un byte morto
    nuove = {0x48bad: 0x48bb5, 0x48bb2: 0x48bba}
    for r in p.recs:
        for s in r['sorgenti']:
            if 0x48bac <= s < 0x48be8:
                if r['pos_src'] is None:
                    raise ValueError('fixup a sorgenti multiple nella grotta')
                dest = nuove.get(s, 0x48bd8)
                struct.pack_into('<h', d, r['pos_src'], dest - r['pagina'])
    p.log.append(f'senza CD: {n} percorsi, salto schermata del CD')


# ------------------------------------------------------------------ sottotitoli ai filmati
# Il codice (tools/sottotitoli_fmv.S) va al posto di compress_fst, il compressore
# dei filmati degli sviluppatori, mai chiamato dal gioco. Le fixup di quel tratto
# sono riusate per i riferimenti alle globali del codice nuovo (etichette fx_*),
# le altre scrivono su una parola morta (zavorra).
ORIGINE_SOTTOTITOLI = 0x12010
FINE_GROTTA_SOTTOTITOLI = 0x12b00          # inizio di decompress_fst
GLOBALI_SOTTOTITOLI = {'fx_bl': 0xc7e70, 'fx_td': 0xc7e58, 'fx_tf': 0xd5bc4}   # block_list, text_dialog, textfont
AGGANCI_SOTTOTITOLI = [
    # (indirizzo, byte originali, istruzione nuova, simbolo di destinazione)
    (0x12b06, '81ec48010000', 'jmp', 'inizio'),
    (0x1311c, '8b42388984 24d4000000', 'call', 'destinazione'),
    (0x131f8, 'b800000a00', 'call', 'schermo'),
    (0x13275, '0f856cfdffff', 'jne', 'fotogramma_censurato'),
    (0x136a2, '0f8d3ff9ffff', 'jge', 'fine_fotogramma'),
]


def assembla_sottotitoli(origine=ORIGINE_SOTTOTITOLI):
    """Assembla sottotitoli_fmv.S con GNU as/ld: (byte, {simbolo: indirizzo})."""
    import subprocess, tempfile
    sorgente = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sottotitoli_fmv.S')
    with tempfile.TemporaryDirectory() as t:
        o, elf, binf = (os.path.join(t, n) for n in ('s.o', 's.elf', 's.bin'))
        subprocess.run(['as', '--32', '-o', o, sorgente], check=True)
        subprocess.run(['ld', '-m', 'elf_i386', f'-Ttext={origine:#x}', '-e', 'inizio', '-o', elf, o], check=True)
        subprocess.run(['objcopy', '-O', 'binary', elf, binf], check=True)
        codice = open(binf, 'rb').read()
        simboli = {}
        for r in subprocess.run(['nm', elf], check=True, capture_output=True, text=True).stdout.split('\n'):
            parti = r.split()
            if len(parti) == 3 and parti[1] in 'tT':
                simboli[parti[2]] = int(parti[0], 16)
    return codice, simboli


def patch_sottotitoli(p):
    d = p.d
    lin2 = p.le.lin2file
    codice, sim = assembla_sottotitoli()
    if ORIGINE_SOTTOTITOLI + len(codice) > FINE_GROTTA_SOTTOTITOLI:
        raise ValueError(f'codice dei sottotitoli troppo lungo ({len(codice)} byte)')
    pagina = ORIGINE_SOTTOTITOLI & ~0xfff
    if (FINE_GROTTA_SOTTOTITOLI - 1) & ~0xfff != pagina:
        raise ValueError('la grotta dei sottotitoli deve stare in una sola pagina')
    # agganci: controlla i byte originali e che nessuna fixup li tocchi
    for a, orig, _, _ in AGGANCI_SOTTOTITOLI:
        b = bytes.fromhex(orig.replace(' ', ''))
        fo = lin2(a)
        if bytes(d[fo:fo + len(b)]) != b:
            raise ValueError(f'byte inattesi a {a:#x}: {bytes(d[fo:fo + len(b)]).hex()}')
        for r in p.recs:
            if any(a - 3 <= s < a + len(b) for s in r['sorgenti']):
                raise ValueError(f'fixup sull\'aggancio {a:#x}')
    # fixup del tratto sostituito
    tratto = [r for r in p.recs if any(ORIGINE_SOTTOTITOLI - 3 <= s < FINE_GROTTA_SOTTOTITOLI for s in r['sorgenti'])]
    for r in tratto:
        if r['pos_src'] is None or r['pagina'] != pagina or r['sorgenti'][0] < ORIGINE_SOTTOTITOLI:
            raise ValueError(f'fixup inattesa nella grotta dei sottotitoli: {r["sorgenti"]}')
    servono = sorted((n, sim[n] - 4) for n in sim if n.startswith('fx_'))
    libere = [r for r in tratto if r['w_off'] == 4 and r['tobj'] == 3]
    if len(libere) < len(servono):
        raise ValueError('fixup riusabili insufficienti')
    usate = set()
    for (nome, pos), r in zip(servono, libere):
        dest = next(v for k, v in GLOBALI_SOTTOTITOLI.items() if nome.startswith(k))
        struct.pack_into('<I', d, r['pos_off'], dest - p.le.objs[2]['base'])
        struct.pack_into('<h', d, r['pos_src'], pos - r['pagina'])
        r['toff'] = dest - p.le.objs[2]['base']
        r['sorgenti'] = [pos]
        usate.add(id(r))
    for r in tratto:
        if id(r) not in usate:
            struct.pack_into('<h', d, r['pos_src'], sim['zavorra'] - r['pagina'])
            r['sorgenti'] = [sim['zavorra']]
    # codice, poi riempitivo fino a decompress_fst
    fo = lin2(ORIGINE_SOTTOTITOLI)
    d[fo:fo + len(codice)] = codice
    resto = FINE_GROTTA_SOTTOTITOLI - ORIGINE_SOTTOTITOLI - len(codice)
    d[fo + len(codice):fo + len(codice) + resto] = b'\xcc' * resto
    for a, orig, istr, dest in AGGANCI_SOTTOTITOLI:
        n = len(bytes.fromhex(orig.replace(' ', '')))
        if istr in ('jge', 'jne'):
            nuovo = (b'\x0f\x8d' if istr == 'jge' else b'\x0f\x85') + _rel32(a + 6, sim[dest])
        else:
            nuovo = (b'\xe9' if istr == 'jmp' else b'\xe8') + _rel32(a + 5, sim[dest])
        nuovo += b'\x90' * (n - len(nuovo))
        d[lin2(a):lin2(a) + n] = nuovo
    p.log.append(f'sottotitoli dei filmati: {len(codice)} byte di codice, {len(servono)} fixup riusate, '
                 f'{len(tratto) - len(servono)} neutralizzate')
