#!/usr/bin/env python3
"""Crea patch/dati/ confrontando i dischi originali (cd/DISKn.iso) con la versione tradotta
già costruita (build/HARVEST, da `harvit.py costruisci`).

    python3 tools/crea_patch.py

La patch contiene solo differenze binarie (tools/bindiff.py) e i file di configurazione
nostri: nessun file del gioco."""
import os, sys, json, hashlib, shutil, struct
QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)
sys.path.insert(0, QUI)
import bindiff
from iso9660 import ISO
from xfile import read_index, REC
from harvit import ESCLUSI_CD

BUILD = os.path.join(RADICE, 'build', 'HARVEST')
DATI = os.path.join(RADICE, 'patch', 'dati')
# file dell'installazione presi dal CD 1 (identici a quelli copiati dall'installatore originale)
INSTALLAZIONE = ['HARVEST.EXE', 'HARVEST2.DAT', 'HARVEST.INI', 'HARVEST.ICO', 'MENU.INI', 'DIALOG.RSP',
                 'README.TXT', 'HMIDET.386', 'HMIDRV.386', 'HMIMDRV.386', 'SETSOUND.BAT', 'SETSND.ICO',
                 'UNSTALL.EXE', 'SETSOUND.EXE', 'SETSOUND.INI', 'SMIDET.386', 'SMIDRV.386', 'SMIMDRV.386',
                 'TEST.WAV']
IN_SETSOUND = {'SETSOUND.EXE', 'SETSOUND.INI', 'SMIDET.386', 'SMIDRV.386', 'SMIMDRV.386', 'TEST.WAV'}


def sha1(b):
    return hashlib.sha1(b).hexdigest()


def membri(idx_bytes, dat_bytes):
    out = {}
    for i in range(0, len(idx_bytes) - REC + 1, REC):
        nome = idx_bytes[i + 4:i + 132].split(b'\0')[0].decode('latin-1')
        a, s1, c, s2 = struct.unpack_from('<4I', idx_bytes, i + 132)
        if nome:
            out[nome.split(':\\', 1)[-1].replace('\\', '/').upper()] = (a, s1)
    return out


def main():
    if os.path.exists(DATI):
        shutil.rmtree(DATI)
    os.makedirs(DATI)
    voci = {}          # (tipo, percorso, sha_orig, sha_nuovo) -> voce

    def aggiungi(tipo, percorso, disco, vecchio, nuovo):
        so, sn = sha1(vecchio), sha1(nuovo)
        k = (tipo, percorso, so, sn)
        if k not in voci:
            diff = bindiff.crea(vecchio, nuovo)
            assert bindiff.applica(vecchio, diff) == nuovo
            nome = sha1((so + sn).encode())[:16] + '.hdf'
            open(os.path.join(DATI, nome), 'wb').write(diff)
            voci[k] = dict(tipo=tipo, percorso=percorso, dischi=[], orig=so, nuovo=sn, diff=nome,
                           dimensione=len(nuovo))
        if disco not in voci[k]['dischi']:
            voci[k]['dischi'].append(disco)

    verifica = {}
    for k in (1, 2, 3):
        iso = ISO(os.path.join(RADICE, 'cd', f'DISK{k}.iso'))
        dest = os.path.join(BUILD, f'CD{k}')
        iso.f.seek(16 * 2048 + 40)
        etichetta = iso.f.read(32).decode('latin-1').strip()
        verifica[k] = dict(etichetta=etichetta, file={})
        for p, r in iso.walk():
            if r.isdir or p.split('/')[0].upper() in ESCLUSI_CD:
                continue
            iso.f.seek(r.extent * 2048)
            vecchio = iso.f.read(r.size)
            nuovo = open(os.path.join(dest, p), 'rb').read()
            if p.upper() == 'HARVEST.DAT':
                mv = membri(iso.read('INDEX.001'), None)
                mn = membri(open(os.path.join(dest, 'INDEX.001'), 'rb').read(), None)
                for nome, (a, s) in mv.items():
                    an, sn_ = mn[nome]
                    bv, bn = vecchio[a:a + s], nuovo[an:an + sn_]
                    if bv != bn:
                        aggiungi('membro', nome, k, bv, bn)
                verifica[k]['file'][p] = sha1(vecchio)
                continue
            if p.upper() == 'INDEX.001':
                verifica[k]['file'][p] = sha1(vecchio)
                continue                       # lo riscrive l'applicatore insieme ai membri
            if vecchio != nuovo:
                aggiungi('file', p, k, vecchio, nuovo)
        verifica[k]['nuovi'] = {'INDEX.001': sha1(open(os.path.join(dest, 'INDEX.001'), 'rb').read()),
                                'HARVEST.DAT': sha1(open(os.path.join(dest, 'HARVEST.DAT'), 'rb').read())}
        iso.close()
    # installazione
    iso = ISO(os.path.join(RADICE, 'cd', 'DISK1.iso'))
    for nome in INSTALLAZIONE:
        vecchio = iso.read(nome)
        rel = ('SETSOUND/' + nome) if nome in IN_SETSOUND else nome
        nuovo = open(os.path.join(BUILD, rel), 'rb').read()
        if vecchio != nuovo:
            aggiungi('installazione', rel, 1, vecchio, nuovo)
        verifica[1]['file'].setdefault(nome, sha1(vecchio))
    manifest = dict(formato=1, gioco='Harvester v1.0 (DigiFX Interactive / Merit Studios, 1996), versione inglese su 3 CD',
                    esclusi=list(ESCLUSI_CD), installazione=INSTALLAZIONE, in_setsound=sorted(IN_SETSOUND),
                    dischi=verifica, voci=sorted(voci.values(), key=lambda v: (v['tipo'], v['percorso'])))
    # file nostri: configurazioni e istruzioni
    for f in os.listdir(os.path.join(RADICE, 'pacchetto')):
        shutil.copyfile(os.path.join(RADICE, 'pacchetto', f), os.path.join(DATI, f))
    for f in ('CONFIG.NCD', 'CONFIG.CD', 'SOUND.CFG'):
        shutil.copyfile(os.path.join(BUILD, f), os.path.join(DATI, f))
    json.dump(manifest, open(os.path.join(DATI, 'manifest.json'), 'w'), indent=1, ensure_ascii=False)
    tot = sum(os.path.getsize(os.path.join(DATI, f)) for f in os.listdir(DATI))
    print(f'{len(voci)} differenze, {tot // 1024} KB in {DATI}')


if __name__ == '__main__':
    main()
