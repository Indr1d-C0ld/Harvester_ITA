"""Archivi HARVEST.DAT / SOUND.DAT / HARVEST2.DAT e i loro indici INDEX.00n.
Record di indice (148 byte): 'XFLE', nome[128], quattro u32."""
import struct

REC = 148

def read_index(path):
    b = open(path, 'rb').read()
    out = []
    for i in range(0, len(b) - REC + 1, REC):
        r = b[i:i + REC]
        if r[:4] != b'XFLE':
            raise ValueError(f'record {i} senza XFLE')
        name = r[4:132].split(b'\0')[0].decode('latin-1')
        a, s1, c, s2 = struct.unpack_from('<4I', r, 132)
        out.append(dict(name=name, a=a, size=s1, c=c, size2=s2, raw=r))
    return out

if __name__ == '__main__':
    import sys
    for e in read_index(sys.argv[1]):
        print(e['a'], e['size'], e['c'], e['size2'], e['name'])
