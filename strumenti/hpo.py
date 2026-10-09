"""Lettura/scrittura minimale di cataloghi gettext .po (UTF-8)."""
import re


class Entry:
    __slots__ = ('ctxt', 'msgid', 'msgstr', 'comments', 'flags')

    def __init__(self, ctxt, msgid, msgstr='', comments=(), flags=()):
        self.ctxt, self.msgid, self.msgstr = ctxt, msgid, msgstr
        self.comments, self.flags = list(comments), list(flags)


def _q(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t') + '"'


_UNQ = {'n': '\n', 't': '\t', '"': '"', '\\': '\\'}


def _uq(s):
    s = s.strip()
    if not (s.startswith('"') and s.endswith('"')):
        raise ValueError('stringa .po non valida: %r' % s)
    return re.sub(r'\\(.)', lambda m: _UNQ[m.group(1)], s[1:-1])


def write(path, entries, header=''):
    with open(path, 'w', encoding='utf-8') as f:
        f.write('msgid ""\nmsgstr ""\n"Content-Type: text/plain; charset=UTF-8\\n"\n')
        if header:
            f.write('"X-Harv-Source: %s\\n"\n' % header)
        f.write('\n')
        for e in entries:
            for c in e.comments:
                f.write('#. %s\n' % c)
            if e.flags:
                f.write('#, %s\n' % ', '.join(e.flags))
            f.write('msgctxt %s\nmsgid %s\nmsgstr %s\n\n' % (_q(e.ctxt), _q(e.msgid), _q(e.msgstr)))


def read(path):
    """Restituisce {(ctxt, msgid): Entry}, esclusa l'intestazione."""
    out = {}
    cur = {}
    field = None
    comments, flags = [], []

    def flush():
        nonlocal cur, comments, flags
        if 'msgid' in cur and cur['msgid']:
            e = Entry(cur.get('msgctxt', ''), cur['msgid'], cur.get('msgstr', ''), comments, flags)
            out[(e.ctxt, e.msgid)] = e
        cur, comments, flags = {}, [], []

    with open(path, encoding='utf-8') as f:
        for ln, line in enumerate(f, 1):
            line = line.rstrip('\n')
            try:
                if not line.strip():
                    flush()
                    field = None
                elif line.startswith('#.'):
                    comments.append(line[2:].strip())
                elif line.startswith('#,'):
                    flags += [x.strip() for x in line[2:].split(',')]
                elif line.startswith('#'):
                    pass
                elif line.startswith('"'):
                    cur[field] += _uq(line)
                else:
                    field, _, rest = line.partition(' ')
                    if field == 'msgid' and 'msgid' in cur:
                        flush()
                    cur[field] = _uq(rest)
            except (ValueError, KeyError) as e:
                raise ValueError('%s:%d: %s' % (path, ln, e))
    flush()
    return out
