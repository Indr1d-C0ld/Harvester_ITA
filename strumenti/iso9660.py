"""Lettura e modifica in place di immagini ISO 9660 a settori da 2048 byte.

Sostituire un file: se il nuovo contenuto sta nei settori gia' occupati lo si
riscrive li', altrimenti lo si accoda in fondo all'immagine; in entrambi i casi
si aggiornano estensione e dimensione nel record di directory (anche nel ramo
Joliet, se esiste) e la dimensione del volume."""
import struct, os

SECT = 2048

class Rec:
    def __init__(self, img, pos, raw, parent):
        self.pos = pos            # posizione assoluta del record nell'immagine
        self.extent = struct.unpack_from('<I', raw, 2)[0]
        self.size = struct.unpack_from('<I', raw, 10)[0]
        self.flags = raw[25]
        nl = raw[32]
        self.raw_name = raw[33:33 + nl]
        self.parent = parent
        self.isdir = bool(self.flags & 2)

    @property
    def name(self):
        n = self.raw_name
        if n in (b'\0', b'\1'):
            return None
        try:
            if len(n) % 2 == 0 and n[:1] == b'\0':
                s = n.decode('utf-16-be')
            else:
                s = n.decode('latin-1')
        except UnicodeDecodeError:
            s = n.decode('latin-1')
        return s.split(';')[0].rstrip('.')

class ISO:
    def __init__(self, path):
        self.path = path
        self.f = open(path, 'r+b')
        self.roots = []   # (tipo, record radice)
        s = 16
        while True:
            self.f.seek(s * SECT)
            vd = self.f.read(SECT)
            t = vd[0]
            if vd[1:6] != b'CD001' or t == 255:
                break
            if t in (1, 2):
                rootraw = vd[156:156 + 34]
                r = Rec(self, s * SECT + 156, rootraw, None)
                self.roots.append((t, s, r))
            s += 1
        self.f.seek(0, 2)
        self.nsect = self.f.tell() // SECT

    def readdir(self, rec):
        out = []
        self.f.seek(rec.extent * SECT)
        data = self.f.read(rec.size)
        i = 0
        while i < len(data):
            l = data[i]
            if l == 0:
                i = (i // SECT + 1) * SECT
                continue
            r = Rec(self, rec.extent * SECT + i, data[i:i + l], rec)
            if r.name is not None:
                out.append(r)
            i += l
        return out

    def walk(self, root=None, prefix=''):
        if root is None:
            root = self.roots[0][2]
        for r in self.readdir(root):
            p = prefix + r.name
            yield p, r
            if r.isdir:
                yield from self.walk(r, p + '/')

    def find_all(self, path):
        """Tutti i record (primario e Joliet) che corrispondono al percorso."""
        want = path.upper().replace('\\', '/')
        res = []
        for t, s, root in self.roots:
            for p, r in self.walk(root):
                if p.upper() == want:
                    res.append(r)
        return res

    def read(self, path):
        r = self.find_all(path)[0]
        self.f.seek(r.extent * SECT)
        return self.f.read(r.size)

    def replace(self, path, data):
        recs = self.find_all(path)
        if not recs:
            raise KeyError(path)
        r = recs[0]
        old_sects = (r.size + SECT - 1) // SECT
        new_sects = (len(data) + SECT - 1) // SECT
        if new_sects <= old_sects:
            extent = r.extent
        else:
            extent = self.nsect
            self.nsect += new_sects
        self.f.seek(extent * SECT)
        self.f.write(data + b'\0' * (new_sects * SECT - len(data)))
        for rr in recs:
            self.f.seek(rr.pos + 2)
            self.f.write(struct.pack('<I', extent) + struct.pack('>I', extent))
            self.f.write(struct.pack('<I', len(data)) + struct.pack('>I', len(data)))
        # dimensione del volume in ogni descrittore
        for t, s, root in self.roots:
            self.f.seek(s * SECT + 80)
            self.f.write(struct.pack('<I', self.nsect) + struct.pack('>I', self.nsect))
        self.f.seek(self.nsect * SECT - 1)
        if self.f.tell() + 1 > os.path.getsize(self.path):
            self.f.write(b'\0')
        self.f.flush()

    def close(self):
        self.f.close()

if __name__ == '__main__':
    import sys
    iso = ISO(sys.argv[1])
    print('descrittori:', [(t, s) for t, s, _ in iso.roots], 'settori:', iso.nsect)
    for p, r in iso.walk():
        if not r.isdir and '/' not in p:
            print(f'{r.extent:8d} {r.size:10d} {p}')
