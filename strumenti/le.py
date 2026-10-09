"""Parser minimo per eseguibili LE (DOS/4G, Watcom): oggetti, pagine, fixup.
Serve a tradurre indirizzi lineari <-> posizioni nel file e a trovare chi
punta a una stringa."""
import struct

class LE:
    def __init__(self, data, le_off, base=0):
        self.d = data
        self.base = base          # posizione dell'MZ che possiede l'header LE
        self.o = o = le_off
        g = lambda fmt, off: struct.unpack_from(fmt, data, o + off)[0]
        self.page_count = g('<I', 0x14)
        self.eip_obj = g('<I', 0x18); self.eip = g('<I', 0x1c)
        self.page_size = g('<I', 0x28)
        self.last_page = g('<I', 0x2c)
        self.fixup_size = g('<I', 0x30)
        self.obj_tab = g('<I', 0x40); self.obj_cnt = g('<I', 0x44)
        self.page_tab = g('<I', 0x48)
        self.fixpage_tab = g('<I', 0x68); self.fixrec_tab = g('<I', 0x6c)
        self.data_pages = g('<I', 0x80)
        self.objs = []
        for i in range(self.obj_cnt):
            vs, base, fl, pti, pc, _ = struct.unpack_from('<6I', data, o + self.obj_tab + 24 * i)
            self.objs.append(dict(n=i + 1, vsize=vs, base=base, flags=fl, page_idx=pti, pages=pc))
        self.pages = []
        for i in range(self.page_count):
            e = data[o + self.page_tab + 4 * i: o + self.page_tab + 4 * i + 4]
            num = (e[0] << 16) | (e[1] << 8) | e[2]
            self.pages.append(num)

    def page_file_off(self, page_no):  # page_no 1-based
        return self.base + self.data_pages + (page_no - 1) * self.page_size

    def lin2file(self, lin):
        for ob in self.objs:
            if ob['base'] <= lin < ob['base'] + ob['vsize']:
                rel = lin - ob['base']
                pi = rel // self.page_size
                if pi >= ob['pages']:
                    return None
                return self.page_file_off(ob['page_idx'] + pi) + rel % self.page_size
        return None

    def file2lin(self, off):
        for ob in self.objs:
            for pi in range(ob['pages']):
                fo = self.page_file_off(ob['page_idx'] + pi)
                if fo <= off < fo + self.page_size:
                    return ob['base'] + pi * self.page_size + (off - fo)
        return None

    def fixups(self):
        """Genera (oggetto_sorgente, lineare_sorgente, oggetto_dest, offset_dest, tipo)."""
        d, o = self.d, self.o
        fpt = [struct.unpack_from('<I', d, o + self.fixpage_tab + 4 * i)[0] for i in range(self.page_count + 1)]
        # pagina logica -> (oggetto, base lineare)
        pmap = {}
        for ob in self.objs:
            for pi in range(ob['pages']):
                pmap[ob['page_idx'] + pi] = (ob['n'], ob['base'] + pi * self.page_size)
        for p in range(self.page_count):
            a = o + self.fixrec_tab + fpt[p]; b = o + self.fixrec_tab + fpt[p + 1]
            sobj, pbase = pmap.get(p + 1, (None, None))
            while a < b:
                src = d[a]; flg = d[a + 1]; a += 2
                if src & 0x20:
                    cnt = d[a]; a += 1; offs = None
                else:
                    so = struct.unpack_from('<h', d, a)[0]; a += 2; offs = [so]
                tt = flg & 3
                if tt != 0:
                    raise ValueError('fixup non interno: %x' % flg)
                if flg & 0x40:
                    tobj = struct.unpack_from('<H', d, a)[0]; a += 2
                else:
                    tobj = d[a]; a += 1
                toff = None
                if (src & 0xf) != 2:  # non selettore
                    if flg & 0x10:
                        toff = struct.unpack_from('<I', d, a)[0]; a += 4
                    else:
                        toff = struct.unpack_from('<H', d, a)[0]; a += 2
                if offs is None:
                    offs = [struct.unpack_from('<h', d, a + 2 * k)[0] for k in range(cnt)]; a += 2 * cnt
                for so in offs:
                    yield sobj, pbase + so, tobj, toff, src & 0xf

def load(path):
    d = open(path, 'rb').read()
    i = d.find(b'LE\0\0')
    while i >= 0:
        base = 0
        j = d.rfind(b'MZ', 0, i)
        while j >= 0:
            if j + struct.unpack_from('<I', d, j + 0x3c)[0] == i:
                base = j
                break
            j = d.rfind(b'MZ', 0, j)
        try:
            le = LE(d, i, base)
            if 0 < le.obj_cnt < 16 and le.page_size == 4096:
                return le
        except Exception:
            pass
        i = d.find(b'LE\0\0', i + 1)
    raise ValueError('LE non trovato')


def fixup_records(le):
    """Come fixups(), ma restituisce le posizioni nel file dei campi da riscrivere:
    dict(pos_obj, w_obj, pos_off, w_off, tobj, toff, sorgenti=[lineari])."""
    d, o = le.d, le.o
    fpt = [struct.unpack_from('<I', d, o + le.fixpage_tab + 4 * i)[0] for i in range(le.page_count + 1)]
    pmap = {}
    for ob in le.objs:
        for pi in range(ob['pages']):
            pmap[ob['page_idx'] + pi] = ob['base'] + pi * le.page_size
    out = []
    for p in range(le.page_count):
        a = o + le.fixrec_tab + fpt[p]; b = o + le.fixrec_tab + fpt[p + 1]
        pbase = pmap.get(p + 1)
        while a < b:
            src = d[a]; flg = d[a + 1]; a += 2
            if src & 0x20:
                cnt = d[a]; a += 1; offs = None
            else:
                offs = [struct.unpack_from('<h', d, a)[0]]; a += 2
            pos_obj = a
            w_obj = 2 if flg & 0x40 else 1
            tobj = struct.unpack_from('<H' if w_obj == 2 else '<B', d, a)[0]; a += w_obj
            pos_off = w_off = toff = None
            if (src & 0xf) != 2:
                w_off = 4 if flg & 0x10 else 2
                pos_off = a
                toff = struct.unpack_from('<I' if w_off == 4 else '<H', d, a)[0]; a += w_off
            if offs is None:
                offs = [struct.unpack_from('<h', d, a + 2 * k)[0] for k in range(cnt)]; a += 2 * cnt
            out.append(dict(pos_obj=pos_obj, w_obj=w_obj, pos_off=pos_off, w_off=w_off, tobj=tobj, toff=toff,
                            sorgenti=[pbase + s for s in offs], tipo=src & 0xf,
                            pos_src=None if src & 0x20 else pos_obj - 2, pagina=pbase))
    return out
