"""Ricava dal codice di HARVEST.EXE chi pronuncia ogni battuta di DIALOGUE.IDX:
cerca le chiamate alla funzione 'di' (numero battuta in eax, personaggio in edx)
e, per contesto, la funzione di dialogo che le contiene (talk_to)."""
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(__file__))
import le as L
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

def analizza(exe):
    le = L.load(exe)
    d = le.d
    fx = {}
    for so, sl, to, toff, t in le.fixups():
        if toff is None:
            continue
        tl = le.objs[to - 1]['base'] + toff
        fo = le.lin2file(tl)
        if to == 3 and fo is not None:
            fx[sl] = d[fo:fo + 64].split(b'\0')[0].decode('latin-1')
    o1 = le.objs[0]
    code = b''.join(d[le.page_file_off(o1['page_idx'] + i):le.page_file_off(o1['page_idx'] + i) + 4096] for i in range(o1['pages']))
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    md.skipdata = True
    regs = {}
    calls = collections.Counter()
    out = []
    for ins in md.disasm(code, o1['base']):
        if ins.mnemonic == 'mov' and ins.op_str.startswith(('eax, 0x', 'edx, 0x', 'eax, ', 'edx, ')):
            r, v = ins.op_str.split(', ', 1)
            s = None
            for a in range(ins.address, ins.address + ins.size):
                if a in fx:
                    s = fx[a]
            try:
                regs[r] = (int(v, 0), s)
            except ValueError:
                regs.pop(r, None)
        elif ins.mnemonic == 'call':
            calls[ins.op_str] += 1
            out.append((ins.address, ins.op_str, regs.get('eax'), regs.get('edx')))
            regs = {}
        elif ins.mnemonic in ('ret', 'jmp'):
            regs = {}
    return out, calls

if __name__ == '__main__':
    out, calls = analizza(sys.argv[1])
    say = {}
    for addr, tgt, eax, edx in out:
        if tgt in ('0x7a690',) and eax and edx and edx[1] and eax[1] is None:
            say.setdefault(eax[0], set()).add(edx[1])
    print(len(say), 'battute con parlante dal codice')
    json.dump({k: sorted(v) for k, v in sorted(say.items())}, open(sys.argv[2], 'w'), indent=0)
    # altre funzioni chiamate con un numero di battuta plausibile + stringa
    cand = collections.Counter()
    for addr, tgt, eax, edx in out:
        if eax and edx and edx[1] and eax[1] is None and 1 <= eax[0] <= 20000 and tgt != '0x7a690':
            cand[tgt] += 1
    print(cand.most_common(10))
