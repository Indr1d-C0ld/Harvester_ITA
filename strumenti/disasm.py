"""Disassembla una regione del codice di HARVEST.EXE annotando le stringhe puntate."""
import sys, re
sys.path.insert(0, __import__('os').path.dirname(__file__))
import le as L
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

def main(exe, start, length):
    le = L.load(exe)
    d = le.d
    fx = {}   # indirizzo sorgente -> testo annotazione
    for so, sl, to, toff, t in le.fixups():
        if toff is None:
            continue
        tl = le.objs[to - 1]['base'] + toff
        fo = le.lin2file(tl)
        ann = f'{tl:#x}'
        if to == 3 and fo is not None:
            s = d[fo:fo + 70].split(b'\0')[0]
            if len(s) >= 1 and all(32 <= c < 127 for c in s):
                ann += ' "' + s.decode() + '"'
        fx[sl] = ann
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    fo = le.lin2file(start)
    code = d[fo:fo + length]
    for ins in md.disasm(code, start):
        ann = ''
        for a in range(ins.address, ins.address + ins.size):
            if a in fx:
                ann += '   ; ' + fx[a]
        print(f'{ins.address:08x}  {ins.mnemonic:6s} {ins.op_str}{ann}')

if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3], 0))
