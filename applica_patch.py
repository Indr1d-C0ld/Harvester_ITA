#!/usr/bin/env python3
"""Harvester - edizione italiana (non ufficiale): applicatore della patch.

Prende le immagini dei tre CD originali di Harvester (versione inglese, 1996) e crea
una cartella pronta per DOSBox con il gioco in italiano.

    python3 applica_patch.py <cartella con le immagini dei CD> <cartella di destinazione> [--iso]

Formati accettati per i CD: .iso a 2048 byte per settore, immagini grezze a 2352
(.bin/.img/.iso) e .cue che rimandano a un .bin. I dischi si riconoscono dall'etichetta
(DISK1, DISK2, DISK3), non dal nome del file.

Con --iso crea anche le tre immagini dei CD tradotte, per giocare cambiando i dischi
come nel 1996 (dosbox-harvester-ita-cd.conf).

Richiede solo Python 3.8 o successivo, senza moduli aggiuntivi. La patch non contiene
file del gioco: solo le differenze fra gli originali e la traduzione.
"""
import os, sys, json, struct, hashlib, zlib, shutil, argparse

DATI = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dati')
SETT = 2048
REC = 148


def msg(*a):
    print(*a, flush=True)


def sha1(b):
    return hashlib.sha1(b).hexdigest()


# ------------------------------------------------------------------ differenze (HDF1)
def _varint(d, i):
    n = s = 0
    while True:
        b = d[i]
        i += 1
        n |= (b & 0x7f) << s
        s += 7
        if not b & 0x80:
            return n, i


def applica_diff(vecchio, diff):
    if diff[:4] != b'HDF1':
        raise ValueError('differenza non valida')
    d = zlib.decompress(diff[4:])
    out = bytearray()
    i = 0
    while i < len(d):
        op = d[i]
        i += 1
        if op == 1:
            p, i = _varint(d, i)
            n, i = _varint(d, i)
            out += vecchio[p:p + n]
        elif op == 2:
            n, i = _varint(d, i)
            out += d[i:i + n]
            i += n
        else:
            raise ValueError('operazione sconosciuta nella differenza')
    return bytes(out)


# ------------------------------------------------------------------ lettura dei CD
class Disco:
    """Immagine di CD-ROM: 2048 byte per settore oppure grezza a 2352 (modo 1 o 2)."""

    def __init__(self, percorso):
        self.percorso = percorso
        self.f = open(percorso, 'rb')
        dim = os.path.getsize(percorso)
        testa = self.f.read(16)
        self.grezzo = dim % 2352 == 0 and testa[:12] == b'\x00' + b'\xff' * 10 + b'\x00'
        self.nsett = dim // (2352 if self.grezzo else SETT)
        pvd = self.settore(16)
        if pvd[1:6] != b'CD001':
            raise ValueError('non è un CD ISO 9660')
        self.etichetta = pvd[40:72].decode('latin-1').strip()
        self.radice = self._record(pvd[156:190])

    def settore(self, lba):
        if not self.grezzo:
            self.f.seek(lba * SETT)
            return self.f.read(SETT)
        self.f.seek(lba * 2352)
        s = self.f.read(2352)
        return s[16:16 + SETT] if s[15] == 1 else s[24:24 + SETT]

    def leggi(self, lba, n):
        if not self.grezzo:
            self.f.seek(lba * SETT)
            return self.f.read(n)
        out = bytearray()
        k = lba
        while len(out) < n:
            out += self.settore(k)
            k += 1
        return bytes(out[:n])

    @staticmethod
    def _record(r):
        nl = r[32]
        return dict(extent=struct.unpack_from('<I', r, 2)[0], size=struct.unpack_from('<I', r, 10)[0],
                    dir=bool(r[25] & 2), nome=r[33:33 + nl])

    def cartella(self, rec):
        dati = self.leggi(rec['extent'], rec['size'])
        out = []
        i = 0
        while i < len(dati):
            l = dati[i]
            if l == 0:
                i = (i // SETT + 1) * SETT
                continue
            r = self._record(dati[i:i + l])
            if r['nome'] not in (b'\0', b'\1'):
                r['nome'] = r['nome'].decode('latin-1').split(';')[0].rstrip('.')
                out.append(r)
            i += l
        return out

    def file(self, rec=None, prefisso=''):
        for r in self.cartella(rec or self.radice):
            p = prefisso + r['nome']
            if r['dir']:
                yield from self.file(r, p + '/')
            else:
                yield p, r

    def indice(self):
        return {p.upper(): r for p, r in self.file()}

    def scrivi_iso(self, dest):
        """Copia l'immagine in formato ISO a 2048 byte per settore."""
        with open(dest, 'wb') as o:
            if not self.grezzo:
                self.f.seek(0)
                shutil.copyfileobj(self.f, o, 8 << 20)
            else:
                for k in range(self.nsett):
                    o.write(self.settore(k))


def trova_dischi(sorgente):
    candidati = []
    for radice, _, files in os.walk(sorgente):
        for f in files:
            p = os.path.join(radice, f)
            est = f.lower().rsplit('.', 1)[-1]
            if est == 'cue':
                for riga in open(p, encoding='latin-1'):
                    if riga.strip().upper().startswith('FILE'):
                        nome = riga.split('"')[1] if '"' in riga else riga.split()[1]
                        candidati.append(os.path.join(radice, nome))
            elif est in ('iso', 'bin', 'img') and os.path.getsize(p) > 50 << 20:
                candidati.append(p)
    dischi = {}
    for p in dict.fromkeys(candidati):
        try:
            d = Disco(p)
        except Exception:
            continue
        if d.etichetta in ('DISK1', 'DISK2', 'DISK3'):
            dischi.setdefault(int(d.etichetta[-1]), d)
    return dischi


# ------------------------------------------------------------------ scrittura ISO (per --iso)
class ISO:
    def __init__(self, percorso):
        self.f = open(percorso, 'r+b')
        self.f.seek(0, 2)
        self.nsett = self.f.tell() // SETT
        self.descr = []
        s = 16
        while True:
            self.f.seek(s * SETT)
            vd = self.f.read(SETT)
            if vd[1:6] != b'CD001' or vd[0] == 255:
                break
            if vd[0] in (1, 2):
                self.descr.append((s, Disco._record(vd[156:190])))
            s += 1

    def _cartella(self, rec):
        self.f.seek(rec['extent'] * SETT)
        dati = self.f.read(rec['size'])
        i = 0
        while i < len(dati):
            l = dati[i]
            if l == 0:
                i = (i // SETT + 1) * SETT
                continue
            r = Disco._record(dati[i:i + l])
            r['pos'] = rec['extent'] * SETT + i
            n = r['nome']
            if n not in (b'\0', b'\1'):
                try:
                    r['nome'] = (n.decode('utf-16-be') if len(n) % 2 == 0 and n[:1] == b'\0' else n.decode('latin-1')
                                 ).split(';')[0].rstrip('.')
                except UnicodeDecodeError:
                    r['nome'] = n.decode('latin-1')
                yield r
            i += l

    def _cerca(self, percorso):
        trovati = []
        for _, radice in self.descr:
            rec = radice
            parti = percorso.upper().split('/')
            for k, parte in enumerate(parti):
                rec = next((r for r in self._cartella(rec) if r['nome'].upper() == parte), None)
                if rec is None:
                    break
            if rec is not None:
                trovati.append(rec)
        return trovati

    def sostituisci(self, percorso, dati):
        recs = self._cerca(percorso)
        if not recs:
            raise KeyError(percorso)
        r = recs[0]
        vecchi = (r['size'] + SETT - 1) // SETT
        nuovi = (len(dati) + SETT - 1) // SETT
        if nuovi <= vecchi:
            ext = r['extent']
        else:
            ext = self.nsett
            self.nsett += nuovi
        self.f.seek(ext * SETT)
        self.f.write(dati + b'\0' * (nuovi * SETT - len(dati)))
        for rr in recs:
            self.f.seek(rr['pos'] + 2)
            self.f.write(struct.pack('<I', ext) + struct.pack('>I', ext) +
                         struct.pack('<I', len(dati)) + struct.pack('>I', len(dati)))
        for s, _ in self.descr:
            self.f.seek(s * SETT + 80)
            self.f.write(struct.pack('<I', self.nsett) + struct.pack('>I', self.nsett))
        self.f.seek(0, 2)
        if self.f.tell() < self.nsett * SETT:
            self.f.seek(self.nsett * SETT - 1)
            self.f.write(b'\0')
        self.f.flush()


# ------------------------------------------------------------------ archivio HARVEST.DAT
def membri(indice):
    out = {}
    for i in range(0, len(indice) - REC + 1, REC):
        nome = indice[i + 4:i + 132].split(b'\0')[0].decode('latin-1')
        if nome:
            out[nome.split(':\\', 1)[-1].replace('\\', '/').upper()] = i
    return out


def patch_archivio(cartella, voci, diff):
    pidx = os.path.join(cartella, 'INDEX.001')
    pdat = os.path.join(cartella, 'HARVEST.DAT')
    idx = bytearray(open(pidx, 'rb').read())
    posizioni = membri(idx)
    with open(pdat, 'r+b') as dat:
        for v in voci:
            i = posizioni[v['percorso']]
            a, s1, c, s2 = struct.unpack_from('<4I', idx, i + 132)
            dat.seek(a)
            vecchio = dat.read(s1)
            if sha1(vecchio) != v['orig']:
                raise SystemExit(f'ERRORE: {v["percorso"]} nell\'archivio non corrisponde alla versione attesa')
            nuovo = applica_diff(vecchio, diff(v))
            if sha1(nuovo) != v['nuovo'] or len(nuovo) > s1:
                raise SystemExit(f'ERRORE: patch di {v["percorso"]} non riuscita')
            struct.pack_into('<4I', idx, i + 132, a, len(nuovo), c, len(nuovo))
            dat.seek(a - REC)
            dat.write(bytes(idx[i:i + REC]))
            dat.seek(a)
            dat.write(nuovo + bytes(s1 - len(nuovo)))
    open(pidx, 'wb').write(idx)


# ------------------------------------------------------------------ programma
def main():
    ap = argparse.ArgumentParser(description='Harvester in italiano: applica la patch ai tre CD originali.')
    ap.add_argument('sorgente', help='cartella che contiene le immagini dei tre CD')
    ap.add_argument('destinazione', help='cartella da creare per il gioco in italiano')
    ap.add_argument('--iso', action='store_true', help='crea anche le immagini dei CD tradotte')
    a = ap.parse_args()

    man = json.load(open(os.path.join(DATI, 'manifest.json'), encoding='utf-8'))
    msg('Harvester - edizione italiana (non ufficiale)')
    dischi = trova_dischi(a.sorgente)
    mancano = [k for k in (1, 2, 3) if k not in dischi]
    if mancano:
        raise SystemExit('ERRORE: non trovo le immagini dei CD ' + ', '.join(map(str, mancano)) +
                         f' in {a.sorgente} (servono tutti e tre i dischi: DISK1, DISK2, DISK3)')
    for k in (1, 2, 3):
        d = dischi[k]
        msg(f'  CD {k}: {d.percorso} ({"grezza 2352" if d.grezzo else "ISO 2048"})')

    # verifica della versione
    msg('Verifica dei file originali...')
    indici = {k: dischi[k].indice() for k in (1, 2, 3)}

    def leggi(k, percorso):
        r = indici[k][percorso.upper()]
        return dischi[k].leggi(r['extent'], r['size'])
    for k, info in man['dischi'].items():
        k = int(k)
        for percorso, atteso in info['file'].items():
            if percorso.upper() not in indici[k] or sha1(leggi(k, percorso)) != atteso:
                raise SystemExit(f'ERRORE: {percorso} sul CD {k} non è quello della versione inglese v1.0 su 3 CD.\n'
                                 'La patch funziona solo con quella versione.')
    for v in man['voci']:
        if v['tipo'] == 'file':
            for k in v['dischi']:
                if sha1(leggi(k, v['percorso'])) != v['orig']:
                    raise SystemExit(f'ERRORE: {v["percorso"]} sul CD {k} non corrisponde alla versione attesa.')

    def diff(v):
        return open(os.path.join(DATI, v['diff']), 'rb').read()

    dest = os.path.abspath(a.destinazione)
    inst = os.path.join(dest, 'HARVEST')
    if os.path.exists(inst):
        raise SystemExit(f'ERRORE: {inst} esiste già; scegli una cartella di destinazione nuova.')
    os.makedirs(inst)
    esclusi = {e.upper() for e in man['esclusi']}

    # contenuto dei CD
    for k in (1, 2, 3):
        msg(f'Copio il CD {k}...')
        base = os.path.join(inst, f'CD{k}')
        for percorso, r in dischi[k].file():
            if percorso.split('/')[0].upper() in esclusi:
                continue
            p = os.path.join(base, *percorso.split('/'))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, 'wb') as o:
                rimasti, lba = r['size'], r['extent']
                while rimasti > 0:
                    blocco = min(rimasti, 4 << 20)
                    o.write(dischi[k].leggi(lba, blocco))
                    lba += blocco // SETT
                    rimasti -= blocco
        msg(f'Traduco il CD {k}...')
        for v in man['voci']:
            if v['tipo'] == 'file' and k in v['dischi']:
                p = os.path.join(base, *v['percorso'].split('/'))
                nuovo = applica_diff(open(p, 'rb').read(), diff(v))
                if sha1(nuovo) != v['nuovo']:
                    raise SystemExit(f'ERRORE: patch di {v["percorso"]} non riuscita')
                open(p, 'wb').write(nuovo)
        patch_archivio(base, [v for v in man['voci'] if v['tipo'] == 'membro' and k in v['dischi']], diff)
        for nome, atteso in man['dischi'][str(k)]['nuovi'].items():
            if sha1(open(os.path.join(base, nome), 'rb').read()) != atteso:
                raise SystemExit(f'ERRORE: {nome} del CD {k} non corrisponde al risultato atteso')

    # installazione (dal CD 1)
    msg('Installo il gioco...')
    os.makedirs(os.path.join(inst, 'SETSOUND'), exist_ok=True)
    in_setsound = set(man['in_setsound'])
    voci_inst = {v['percorso']: v for v in man['voci'] if v['tipo'] == 'installazione'}
    for nome in man['installazione']:
        rel = ('SETSOUND/' + nome) if nome in in_setsound else nome
        dati = leggi(1, nome)
        if rel in voci_inst:
            dati = applica_diff(dati, diff(voci_inst[rel]))
            if sha1(dati) != voci_inst[rel]['nuovo']:
                raise SystemExit(f'ERRORE: patch di {rel} non riuscita')
        open(os.path.join(inst, *rel.split('/')), 'wb').write(dati)
    for nome in ('CONFIG.NCD', 'CONFIG.CD', 'SOUND.CFG', 'SOTTOTIT.ITA'):
        shutil.copyfile(os.path.join(DATI, nome), os.path.join(inst, nome))
    shutil.copyfile(os.path.join(DATI, 'CONFIG.NCD'), os.path.join(inst, 'CONFIG.INI'))
    for nome in ('dosbox-harvester-ita.conf', 'dosbox-harvester-ita-cd.conf', 'LEGGIMI.txt'):
        shutil.copyfile(os.path.join(DATI, nome), os.path.join(dest, nome))
    manuale = os.path.join(os.path.dirname(DATI), 'manuale', 'Harvester_manuale_ITA.pdf')
    if os.path.exists(manuale):
        shutil.copyfile(manuale, os.path.join(dest, 'Harvester_manuale_ITA.pdf'))

    # file identici fra i dischi: collegamenti fisici, per risparmiare spazio
    risparmio = 0
    for k in (2, 3):
        altro = os.path.join(inst, f'CD{k}')
        for radice, _, files in os.walk(altro):
            for f in files:
                p2 = os.path.join(radice, f)
                p1 = os.path.join(inst, 'CD1', os.path.relpath(p2, altro))
                if os.path.exists(p1) and os.path.getsize(p1) == os.path.getsize(p2):
                    with open(p1, 'rb') as x, open(p2, 'rb') as y:
                        uguali = all(bx == by for bx, by in iter(lambda: (x.read(1 << 20), y.read(1 << 20)), (b'', b'')))
                    if uguali:
                        try:
                            os.remove(p2)
                            os.link(p1, p2)
                            risparmio += os.path.getsize(p1)
                        except OSError:
                            shutil.copyfile(p1, p2)

    if a.iso:
        os.makedirs(os.path.join(dest, 'iso'), exist_ok=True)
        for k in (1, 2, 3):
            msg(f'Creo l\'immagine del CD {k}...')
            pi = os.path.join(dest, 'iso', f'DISK{k}.iso')
            dischi[k].scrivi_iso(pi)
            iso = ISO(pi)
            cambiati = {v['percorso'] for v in man['voci'] if v['tipo'] == 'file' and k in v['dischi']}
            cambiati |= {'HARVEST.DAT', 'INDEX.001'}
            for percorso in sorted(cambiati):
                iso.sostituisci(percorso, open(os.path.join(inst, f'CD{k}', *percorso.split('/')), 'rb').read())
            iso.f.close()

    msg('')
    msg(f'Fatto. Il gioco in italiano è in {dest}')
    msg(f'Per giocare:  cd "{dest}"  e poi  dosbox -conf dosbox-harvester-ita.conf')
    if risparmio:
        msg(f'({risparmio >> 20} MB di file identici fra i dischi sono collegati, non copiati)')


if __name__ == '__main__':
    main()
