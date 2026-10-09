"""Estrae i file di un archivio HARVEST.DAT da un'immagine ISO usando l'indice."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from iso9660 import ISO
from xfile import read_index

def main(iso_path, idx_path, dat_name, outdir):
    iso = ISO(iso_path)
    rec = iso.find_all(dat_name)[0]
    base = rec.extent * 2048
    f = iso.f
    n = 0
    for e in read_index(idx_path):
        if not e['name']:
            continue
        rel = e['name'].split(':\\', 1)[-1].replace('\\', '/').upper()
        p = os.path.join(outdir, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        f.seek(base + e['a'])
        open(p, 'wb').write(f.read(e['size']))
        n += 1
    print(iso_path, n, 'file')

if __name__ == '__main__':
    main(*sys.argv[1:5])
