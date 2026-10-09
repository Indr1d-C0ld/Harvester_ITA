"""Lettura/scrittura dei font .CFT di Harvester (colorfnt.cpp).
Formato: nome[64], altezza u16, start[256] u16, larghezza[256] u16,
poi 18 byte: spazio u16, 4 byte, larghezza bitmap u32, altezza bitmap u32, 4 byte;
poi bitmap 8 bit per pixel, riga per riga."""
import struct, sys

class CFT:
    def __init__(self, data):
        self.name = data[:64]
        self.height = struct.unpack_from('<H', data, 64)[0]
        self.start = list(struct.unpack_from('<256H', data, 66))
        self.width = list(struct.unpack_from('<256H', data, 66 + 512))
        o = 66 + 1024
        self.tail = data[o:o + 18]
        self.space, = struct.unpack_from('<H', data, o)
        self.bw, self.bh = struct.unpack_from('<II', data, o + 6)
        self.bmp = bytearray(data[o + 18:o + 18 + self.bw * self.bh])
        self.extra = data[o + 18 + self.bw * self.bh:]

    @classmethod
    def load(cls, path):
        return cls(open(path, 'rb').read())

    def pixel_rows(self):
        return [self.bmp[y * self.bw:(y + 1) * self.bw] for y in range(self.bh)]

    def glyph(self, c):
        s, w = self.start[c], self.width[c]
        return [bytes(r[s:s + w]) for r in self.pixel_rows()]

    def add_glyph(self, c, rows):
        """Accoda un glifo (lista di righe di byte, altezza bh) e lo assegna al codice c."""
        w = len(rows[0])
        newbw = self.bw + w
        nb = bytearray()
        for y in range(self.bh):
            nb += self.bmp[y * self.bw:(y + 1) * self.bw] + bytes(rows[y])
        self.start[c] = self.bw
        self.width[c] = w
        self.bw = newbw
        self.bmp = nb

    def dump(self):
        out = bytearray(self.name)
        out += struct.pack('<H', self.height)
        out += struct.pack('<256H', *self.start)
        out += struct.pack('<256H', *self.width)
        t = bytearray(self.tail)
        struct.pack_into('<H', t, 0, self.space)
        struct.pack_into('<II', t, 6, self.bw, self.bh)
        out += t + self.bmp + self.extra
        return bytes(out)


def accento_grave(font, base_acuta, base_nuda):
    """Ricava il glifo con accento grave da quello con l'acuto: le righe che
    differiscono dalla lettera senza accento vengono specchiate orizzontalmente."""
    g = font.glyph(base_acuta)
    n = font.glyph(base_nuda) if font.width[base_nuda] else None
    out = []
    for y, riga in enumerate(g):
        diversa = n is None or len(n[y]) != len(riga) or n[y] != riga
        # l'accento sta sopra la lettera: specchia solo le righe alte che differiscono
        if diversa and y < font.bh * 0.55:
            out.append(bytes(reversed(riga)))
        else:
            out.append(riga)
    return out


def aggiungi_grave(font):
    """Aggiunge ì ò Ì Ò (Latin-1 0xEC 0xF2 0xCC 0xD2) dove mancano."""
    fatti = []
    for nuovo, acuta, nuda in ((0xEC, 0xED, 0x131), (0xF2, 0xF3, ord('o')), (0xCC, 0xCD, ord('I')), (0xD2, 0xD3, ord('O'))):
        if font.width[nuovo]:
            continue
        if not font.width[acuta]:
            continue
        nuda_eff = nuda if nuda < 256 else None
        if nuda_eff is None:
            # per la i: confronta con 'i' solo sotto il puntino -> usa l'acuta e specchia le righe alte
            g = font.glyph(acuta)
            i = font.glyph(ord('i'))
            righe = []
            for y, r in enumerate(g):
                if y < font.bh * 0.55 and (len(i[y]) != len(r) or i[y] != r or True) and any(r) and not any(i[y]) :
                    righe.append(bytes(reversed(r)))
                else:
                    righe.append(r)
            font.add_glyph(nuovo, righe)
        else:
            font.add_glyph(nuovo, accento_grave(font, acuta, nuda_eff))
        fatti.append(nuovo)
    return fatti
