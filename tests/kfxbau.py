"""Ausgedachte Kindle-Daten für die Tests (#61): ein winziges KFX-Buch und die Datenbank der Markierungen, wie neuere
Kindles sie führen. Nur so viel Ion und KFX, wie `kfx` liest."""
import json, os, sqlite3, struct

YJ = 859  # so viele Symbole hat die Amazon-Tabelle, auf die sich ein Buch beruft


def _varuint(n):
    out = [0x80 | (n & 0x7f)]
    n >>= 7
    while n:
        out.insert(0, n & 0x7f)
        n >>= 7
    return bytes(out)


def _td(t, body):
    n = len(body)
    if n < 14 and not (t == 13 and n == 1):  # Strukturen mit Länge 1 hießen »sortiert«
        return bytes([t << 4 | n]) + body
    return bytes([t << 4 | 14]) + _varuint(n) + body


class Ion:
    """Schreibt Ion binär. Symbole sind Strings mit »$«: »$145« ist das Amazon-Symbol 145, »$name« ein eigenes."""

    def __init__(self):
        self.local = []

    def sid(self, name):
        name = name[1:]
        if name.isdigit():
            return int(name)
        if name not in self.local:
            self.local.append(name)
        return 10 + YJ + self.local.index(name)

    def enc(self, v):
        if isinstance(v, bool):
            return bytes([0x11 if v else 0x10])
        if isinstance(v, int):
            mag = abs(v).to_bytes((abs(v).bit_length() + 7) // 8, 'big')
            return _td(3 if v < 0 else 2, mag)
        if isinstance(v, str) and v.startswith('$'):
            s = self.sid(v)
            return _td(7, s.to_bytes((s.bit_length() + 7) // 8, 'big'))
        if isinstance(v, str):
            return _td(8, v.encode('utf-8'))
        if isinstance(v, list):
            return _td(11, b''.join(self.enc(x) for x in v))
        if isinstance(v, dict):
            return _td(13, b''.join(_varuint(self.sid(k)) + self.enc(x) for k, x in v.items()))
        if isinstance(v, tuple):  # (Annotation, Wert)
            a = _varuint(self.sid(v[0]))
            return _td(14, _varuint(len(a)) + a + self.enc(v[1]))
        raise TypeError(v)


BVM = b'\xe0\x01\x00\xea'


def container(frags, drm=0):
    """frags: [(Name, Typ, Wert)] → Bytes einer KFX-Datei."""
    ion = Ion()
    ents, index = b'', b''
    for name, kind, value in frags:
        head = BVM + ion.enc({'$410': 0, '$411': 0})
        e = b'ENTY' + struct.pack('<HI', 1, 10 + len(head)) + head + BVM + ion.enc(value)
        index += struct.pack('<IIQQ', ion.sid(name), ion.sid(kind), len(ents), len(e))
        ents += e
    # erst nach den Fragmenten: dann kennt die Symboltabelle alle eigenen Namen
    syms = BVM + Ion().enc(('$3', {'$6': [{'$4': 'YJ_symbols', '$5': 10, '$8': YJ}], '$7': ion.local}))
    at_index = 18
    at_syms = at_index + len(index)
    at_info = at_syms + len(syms)
    info = BVM + Ion().enc({'$409': 'CR!TEST', '$410': 0, '$411': drm, '$413': at_index, '$414': len(index),
                            '$415': at_syms, '$416': len(syms), '$412': 4096})
    head_len = at_info + len(info)
    return b'CONT' + struct.pack('<HIII', 2, head_len, at_info, len(info)) + index + syms + info + ents


def book(title, author, ident, paras, pages=(), drm=0):
    """Ein Buch aus Absätzen, ein Abschnitt; Positionen wie beim Kindle: der Abschnitt 1, je Absatz der Behälter 1
    und jedes Zeichen 1. pages: [(Absatz, Versatz, Seitenzahl)]. Fundstellen alle 10 Positionen."""
    items, eid = [], 100
    for n in range(len(paras)):
        items.append({'$155': eid + n, '$159': '$269', '$145': {'$4': '$text1', '$403': n}})
    story = {'$176': '$story1', '$146': [{'$155': 99, '$159': '$269', '$146': items}]}
    total = 2 + sum(len(p) for p in paras)
    frags = [('$text1', '$145', {'$4': '$text1', '$146': list(paras)}),
             ('$story1', '$259', story),
             ('$sec1', '$260', {'$174': '$sec1', '$141': [{'$155': 98, '$176': '$story1', '$159': '$269'}]}),
             ('$348', '$538', {'$169': [{'$178': '$351', '$170': ['$sec1']}]}),
             ('$348', '$490', {'$491': [{'$495': 'kindle_title_metadata', '$258': [
                 {'$492': 'title', '$307': title}, {'$492': 'author', '$307': author},
                 {'$492': 'content_id', '$307': ident}]}]}),
             ('$348', '$621', [{'$182': list(range(0, total, 10))}])]
    if pages:
        frags += [('$nav1', '$391', {'$235': '$237', '$247': [
                      {'$241': {'$244': label}, '$246': {'$155': eid + p, '$143': off}} for p, off, label in pages]}),
                  ('$348', '$389', [{'$178': '$351', '$392': ['$nav1']}])]
    return container(frags, drm)


def pos(paras, n, off=0):
    """Die Kindle-Position des Zeichens off in Absatz n (zum Prüfen und für Markierungen)."""
    return 2 + sum(len(p) for p in paras[:n]) + off


TABLES = {
    'server_view': "dataset INTEGER, dataset_id TEXT, annotation_id TEXT, serialized_payload TEXT, created_time INTEGER, modified_time INTEGER",
    'staging_server_view': "dataset INTEGER, dataset_id TEXT, annotation_id TEXT, serialized_payload TEXT, created_time INTEGER, modified_time INTEGER",
    'nonsyncable_annotations': "annotation_id TEXT, book_id TEXT, dataset INTEGER, start_position TEXT, end_position TEXT, created_time INTEGER, modified_time INTEGER, serialized_payload TEXT",
    'local_edit': "annotation_id TEXT, action TEXT, dataset INTEGER, dataset_id TEXT, serialized_payload TEXT, dirty_flag INTEGER, created_time INTEGER, modified_time INTEGER, retry_count INTEGER, expiration_timestamp TEXT",
}


def note(kind, start, end, ms, text=''):
    """Das JSON eines Eintrags, wie der Kindle es ablegt."""
    return json.dumps(dict(type=kind, created_time=ms, last_modified=ms, json_metadata=json.dumps(dict(note_text=text) if text else {}),
                           start_position=dict(longPosition='', shortPosition=start), end_position=dict(longPosition='', shortPosition=end)))


def database(path, rows):
    """rows: [(Tabelle, Buchkennung, Eintragskennung, JSON, Aktion)] → SQLite-Datei wie auf dem Kindle."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    con = sqlite3.connect(path)
    for t, cols in TABLES.items():
        con.execute('CREATE TABLE %s (%s)' % (t, cols))
    for table, bid, aid, payload, action in rows:
        if table == 'local_edit':
            con.execute('INSERT INTO local_edit (annotation_id, action, dataset, dataset_id, serialized_payload) VALUES (?, ?, 1, ?, ?)',
                        (aid, action, bid, payload))
        else:
            con.execute('INSERT INTO %s (dataset, dataset_id, annotation_id, serialized_payload) VALUES (1, ?, ?, ?)' % table,
                        (bid, aid, payload))
    con.commit()
    con.close()
