"""Ricostruisce dal codice di HARVEST.EXE le conversazioni: per ogni funzione,
nell'ordine degli indirizzi, le battute dette (DIALOGUE.IDX, con il parlante)
e le righe di DIALOG.RSP usate (menu, scelte, confronti)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
import le as L
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

SAY, RSP = '0x7a690', '0x3a1a0'

def main(exe, out):
    le = L.load(exe); d = le.d
    fx = {}
    for so, sl, to, toff, t in le.fixups():
        if toff is None: continue
        tl = le.objs[to - 1]['base'] + toff
        fo = le.lin2file(tl)
        if to == 3 and fo is not None:
            fx[sl] = d[fo:fo + 64].split(b'\0')[0].decode('latin-1')
    o1 = le.objs[0]
    code = b''.join(d[le.page_file_off(o1['page_idx'] + i):le.page_file_off(o1['page_idx'] + i) + 4096] for i in range(o1['pages']))
    md = Cs(CS_ARCH_X86, CS_MODE_32); md.skipdata = True
    ins = list(md.disasm(code, o1['base']))
    funcs = []
    cur = None
    regs = {}
    talk = None
    for k, i in enumerate(ins):
        if cur is None:
            cur = dict(inizio=hex(i.address), eventi=[])
        if i.mnemonic == 'mov' and i.op_str.split(', ')[0] in ('eax', 'edx'):
            r, v = i.op_str.split(', ', 1)
            s = next((fx[a] for a in range(i.address, i.address + i.size) if a in fx), None)
            try: regs[r] = (int(v, 0), s)
            except ValueError: regs.pop(r, None)
        elif i.mnemonic == 'xor' and i.op_str == 'eax, eax':
            regs['eax'] = (0, None)
        elif i.mnemonic == 'call':
            e, dd = regs.get('eax'), regs.get('edx')
            if i.op_str == SAY and e and e[1] is None:
                cur['eventi'].append(['di', e[0], dd[1] if dd else None])
            elif i.op_str == RSP and e and e[1] is None:
                cur['eventi'].append(['rsp', e[0]])
            regs = {}
        elif i.mnemonic == 'ret':
            if cur['eventi']:
                funcs.append(cur)
            cur = None; regs = {}
    json.dump(funcs, open(out, 'w'), indent=0)
    print(len(funcs), 'funzioni con dialoghi')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
