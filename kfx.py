"""Bücher im Kindle-Format KFX lesen (#61): der Text Zeichen für Zeichen an den Positionen, die der Kindle für
Markierungen speichert.

Seit einer Firmware vom Sommer 2026 (5.19) schreibt der Kindle neue Markierungen nicht mehr in »My Clippings.txt«,
sondern in eine Datenbank – nur Anfang und Ende als Position im Buch, ohne den Text. Der steht nur im Buch selbst, und
lesbar ist er nur bei Büchern ohne Kopierschutz: selbst erstellten, etwa per »Send to Kindle« geschickten. Gekaufte
Bücher sind verschlüsselt; daran ändert das Programm nichts (`Locked`).

Eine KFX-Datei ist ein Behälter (»CONT«) mit Fragmenten in Amazon Ion, binär. Die Positionen zählen jedes Zeichen
eines Textstücks und jedes andere Element (Absatzbehälter, Bild) als eins, in Lesereihenfolge Abschnitt für Abschnitt.
Die Symbolnummern ($145 Text, $259 Storyline, $260 Abschnitt …) sind die der Amazon-Werkzeuge; kfxlib von John Howell
nennt sie genauso."""
import bisect, struct

BVM = b'\xe0\x01\x00\xea'  # Versionsmarke vor jedem Ion-Datenstrom
RAW = ('$417', '$418')     # Bilder und Schriften: Rohdaten, kein Ion


class Locked(Exception):
    """Das Buch ist kopiergeschützt."""


class Sym(str):
    """Ein Ion-Symbol, als Name: »$145« für die Symbole der Amazon-Tabelle, sonst der Name aus dem Buch."""


class Annot:
    def __init__(self, names, value):
        self.names, self.value = names, value


def _varuint(d, i):
    v = 0
    while True:
        b = d[i]
        i += 1
        v = (v << 7) | (b & 0x7f)
        if b & 0x80:
            return v, i


def _varint(d, i):
    b = d[i]
    i += 1
    neg, v = b & 0x40, b & 0x3f
    while not b & 0x80:
        b = d[i]
        i += 1
        v = (v << 7) | (b & 0x7f)
    return -v if neg else v, i


class _Ion:
    """Liest Ion binär – nur so viel, wie KFX braucht; Zeitstempel bleiben Rohbytes."""

    def __init__(self, names=None):
        self.names = names or {}

    def sym(self, sid):
        return Sym(self.names.get(sid, '$%d' % sid))

    def values(self, d, i, end):
        out = []
        while i < end:
            if d[i:i + 4] == BVM:
                i += 4
                continue
            v, i, ok = self.value(d, i)
            if ok:
                out.append(v)
        return out

    def value(self, d, i):
        t, n = d[i] >> 4, d[i] & 15
        i += 1
        if t == 0:  # Füllbytes
            if n == 14:
                n, i = _varuint(d, i)
            return None, i + n, False
        if n == 15:
            return None, i, True
        if t == 1:
            return bool(n), i, True
        if n == 14 or (t == 13 and n == 1):  # Länge folgt; bei Strukturen heißt 1 »sortiert, Länge folgt«
            n, i = _varuint(d, i)
        s, e = i, i + n
        if t in (2, 3):
            v = int.from_bytes(d[s:e], 'big')
            return -v if t == 3 else v, e, True
        if t == 4:
            return (struct.unpack('>f', d[s:e])[0] if n == 4 else struct.unpack('>d', d[s:e])[0] if n == 8 else 0.0), e, True
        if t == 5:
            if not n:
                return 0, e, True
            x, j = _varint(d, s)
            c = d[j:e]
            m = int.from_bytes(bytes([c[0] & 0x7f]) + c[1:], 'big') if c else 0
            return (-m if c and c[0] & 0x80 else m) * 10.0 ** x, e, True
        if t == 6:
            return bytes(d[s:e]), e, True
        if t == 7:
            return self.sym(int.from_bytes(d[s:e], 'big')), e, True
        if t == 8:
            return d[s:e].decode('utf-8', 'replace'), e, True
        if t in (9, 10):
            return bytes(d[s:e]), e, True
        if t in (11, 12):
            return self.values(d, s, e), e, True
        if t == 13:
            out, j = {}, s
            while j < e:
                f, j = _varuint(d, j)
                v, j, ok = self.value(d, j)
                if ok:
                    out[self.sym(f)] = v
            return out, e, True
        if t == 14:
            k, j = _varuint(d, s)
            names, stop = [], j + k
            while j < stop:
                a, j = _varuint(d, j)
                names.append(self.sym(a))
            v, j, ok = self.value(d, j)
            return Annot(names, v), e, True
        raise ValueError('kein Ion')


def _plain(v):
    return v.value if isinstance(v, Annot) else v


def fragments(data):
    """Alle Fragmente eines KFX-Behälters als {Typ: {Name: Wert}}."""
    if data[:4] != b'CONT':
        raise Locked() if b'DRMION' in data[:64] else ValueError('kein KFX')
    head_len, info_at, info_len = struct.unpack_from('<III', data, 6)
    info = _Ion().values(data, info_at, info_at + info_len)[0]
    g = lambda k: info.get('$%d' % k)
    if g(411):  # Verschlüsselungsverfahren
        raise Locked()
    table = _plain(_Ion().values(data, g(415), g(415) + g(416))[0])
    base = 10 + sum(imp.get('$8', 0) for imp in table.get('$6') or [])  # nach den 9 System- und den Amazon-Symbolen
    ion = _Ion({base + n: s for n, s in enumerate(table.get('$7') or [])})
    out = {}
    for k in range(g(414) // 24):
        fid, ftype, off, length = struct.unpack_from('<IIQQ', data, g(413) + 24 * k)
        p = head_len + off
        if data[p:p + 4] != b'ENTY':
            raise ValueError('kein KFX')
        kind = ion.sym(ftype)
        if kind in RAW:
            continue
        body = data[p + struct.unpack_from('<I', data, p + 6)[0]:p + length]
        if b'DRMION' in body[:16]:
            raise Locked()
        vals = ion.values(body, 0, len(body))
        out.setdefault(kind, {})[ion.sym(fid)] = _plain(vals[0]) if vals else None
    return out


class Book:
    """Ein KFX-Buch: title, author, ident (Kennung, unter der der Kindle Markierungen ablegt), text (ein Zeichen je
    Position; Behälter und Bilder als Zeilenumbruch), Positionen der Kindle-Fundstellen (locs) und Seitenzahlen."""

    def __init__(self, data):
        fr = fragments(data)
        one = lambda kind: _plain(next(iter((fr.get(kind) or {None: None}).values())))
        meta = {}
        for cat in (one('$490') or {}).get('$491') or []:
            for kv in cat.get('$258') or []:
                meta.setdefault(kv.get('$492'), kv.get('$307'))
        for kv in (one('$258') or {}).get('$491') or []:  # ältere Bücher: Metadaten als Liste
            meta.setdefault(kv.get('$492'), kv.get('$307'))
        self.title, self.author = str(meta.get('title') or ''), str(meta.get('author') or '')
        self.ident = str(meta.get('content_id') or meta.get('ASIN') or meta.get('asin') or '')
        texts, lines, sections = fr.get('$145') or {}, fr.get('$259') or {}, fr.get('$260') or {}
        chars, starts, breaks = [], {}, []

        def walk(items):
            for it in items or []:
                it = _plain(it)
                if not isinstance(it, dict):
                    continue
                if it.get('$155') is not None:
                    starts.setdefault(it['$155'], len(chars))
                ref = it.get('$145')
                if isinstance(ref, dict) and ref.get('$4') in texts:
                    breaks.append(len(chars))
                    chars.extend(_plain(texts[ref['$4']]).get('$146')[ref.get('$403') or 0])
                elif isinstance(ref, str) and not isinstance(ref, Sym):
                    breaks.append(len(chars))
                    chars.extend(ref)
                else:
                    chars.append('\n')
                walk(it.get('$146'))

        order = []
        for doc in (one('$538'), one('$258')):
            for ro in (doc or {}).get('$169') or []:
                order = order or list(ro.get('$170') or [])
        for name in order:
            for tpl in (sections.get(name) or {}).get('$141') or []:
                tpl = _plain(tpl)
                if tpl.get('$155') is not None:
                    starts.setdefault(tpl['$155'], len(chars))
                chars.append('\n')
                story = lines.get(tpl.get('$176'))
                walk(story.get('$146') if story else tpl.get('$146'))
        self.text, self.breaks = ''.join(chars), breaks
        at = lambda p: starts.get(_plain(p).get('$155'), 0) + (_plain(p).get('$143') or 0)
        # Fundstellen: neuere Bücher führen die Anfangspositionen gleich mit ($621), ältere als Verweise ($550)
        pids, refs = one('$621'), one('$550')
        self.locs = sorted(_plain(pids[0]).get('$182') or []) if isinstance(pids, list) and pids else []
        if not self.locs and isinstance(refs, list) and refs:
            self.locs = sorted(at(p) for p in _plain(refs[0]).get('$182') or [])
        self.pages = []
        nav = fr.get('$391') or {}
        for ro in one('$389') or []:
            for c in ro.get('$392') or []:
                c = nav.get(c) if isinstance(c, Sym) else _plain(c)
                if c and c.get('$235') == '$237':  # die Seitenliste
                    self.pages = sorted((at(e['$246']), (e.get('$241') or {}).get('$244') or '')
                                        for e in map(_plain, c.get('$247') or []) if e.get('$246'))

    def quote(self, start, end):
        """Der markierte Text, Leerraum zusammengezogen; Ende einschließlich wie beim Kindle. Zwei Textstücke stoßen ohne
        Position dazwischen aneinander – etwa die Zeilen eines Scans, die als eigene Absätze ins E-Book kamen –, also
        steht dort ein Leerzeichen, und ein am Zeilenende getrenntes Wort wird wieder eins."""
        cuts = self.breaks[bisect.bisect_right(self.breaks, start):bisect.bisect_right(self.breaks, end)]
        out = ''
        for a, b in zip([start] + cuts, cuts + [end + 1]):
            part = self.text[a:b]
            if out and out[-1] in '-­⸗' and out[-2:-1].isalpha() and part[:1].islower():
                out = out[:-1] + part
            else:
                out += (' ' if out else '') + part
        return ' '.join(out.replace('­', '').split())

    def location(self, pos):
        """Die Fundstelle, die der Kindle als »Position« anzeigt."""
        return (bisect.bisect_right(self.locs, pos) or None) if self.locs else None

    def page(self, pos):
        k = bisect.bisect_right(self.pages, (pos, '￿'))
        return self.pages[k - 1][1] if k else None


def read(path):
    with open(path, 'rb') as f:
        return Book(f.read())
