"""Animazioni .ABM di Harvester (WAIT.ABM, POINTERS.ABM, personaggi...).
Header: u32 numero fotogrammi, u32 dimensione massima, 8 byte.
Fotogramma: u32 larghezza, u32 altezza, u8 compresso, u32 dimensione dati,
u32 (puntatore, ignorato), dati, 8 byte finali (di solito zero). RLE: c<0x80 copia c byte; c>=0x80 ripete
(c-0x80) volte il byte seguente."""
import struct


def rle_dec(data, n):
    out = bytearray()
    i = 0
    while len(out) < n and i < len(data):
        c = data[i]; i += 1
        if c < 0x80:
            out += data[i:i + c]; i += c
        else:
            out += bytes([data[i]]) * (c - 0x80); i += 1
    return bytes(out[:n]), i


def rle_enc(px):
    out = bytearray()
    i = 0
    n = len(px)
    while i < n:
        j = i
        while j < n and j - i < 127 and px[j] == px[i]:
            j += 1
        if j - i >= 3:
            out += bytes([0x80 + (j - i), px[i]])
            i = j
            continue
        j = i
        while j < n and j - i < 127:
            if j + 2 < n and px[j] == px[j + 1] == px[j + 2]:
                break
            j += 1
        out += bytes([j - i]) + px[i:j]
        i = j
    return bytes(out)


class ABM:
    def __init__(self, data):
        self.n, self.maxsz = struct.unpack_from('<II', data, 0)
        self.hdr = data[:16]
        self.frames = []
        o = 16
        for k in range(self.n):
            w, h, comp, size, ptr = struct.unpack_from('<IIBII', data, o)
            raw = data[o + 17:o + 17 + size]
            if comp:
                px, used = rle_dec(raw, w * h)
            else:
                px = raw[:w * h]
            fine = data[o + 17 + size:o + 25 + size]
            self.frames.append(dict(w=w, h=h, comp=comp, ptr=ptr, px=px, px0=px, raw=raw, fine=fine))
            o += 25 + size
        self.coda = data[o:]

    @classmethod
    def load(cls, p):
        return cls(open(p, 'rb').read())

    def dump(self):
        out = bytearray()
        body = bytearray()
        mx = 0
        for f in self.frames:
            if f['px'] == f.get('px0'):
                raw = f['raw']
            else:
                raw = rle_enc(f['px']) if f['comp'] else f['px']
            body += struct.pack('<IIBII', f['w'], f['h'], f['comp'], len(raw), f['ptr']) + raw + f['fine']
            mx = max(mx, len(raw))
        hdr = bytearray(self.hdr)
        struct.pack_into('<II', hdr, 0, len(self.frames), max(mx, self.maxsz))
        return bytes(hdr) + bytes(body) + self.coda
