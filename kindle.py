"""Markierungen vom Kindle (#61): die Datei »My Clippings.txt« lesen, je Buch ordnen und doppelte Einträge auflösen.

Der Kindle hängt jede Markierung, Notiz und jedes Lesezeichen als Eintrag an diese eine Datei an, getrennt durch
»==========«. Ein Eintrag besteht aus Titelzeile (»Titel (Autor)«), Kennzeile und Text:

    Moby Dick (Melville, Herman)
    - Ihre Markierung auf Seite 32 | bei Position 433-434 | Hinzugefügt am Samstag, 14. Mai 2016 14:03:23

    They say that men who have seen the world …

Die Kennzeile folgt der Sprache des Geräts (»- Your Highlight on page 32 | Location 433-434 | Added on …«). Erkannt
werden Deutsch und Englisch; was sich nicht zuordnen lässt, aber Text hat, gilt als Markierung."""
import glob, os, re, string, sys

SEP = '=========='
FILE = 'My Clippings.txt'  # heißt auch auf deutschen Geräten so
KINDS = [('note', re.compile(r'\b(?:Notiz|Note)\b', re.I)), ('bookmark', re.compile(r'\b(?:Lesezeichen|Bookmark)\b', re.I)),
         ('highlight', re.compile(r'\b(?:Markierung|Highlight)\b', re.I))]
PAGE = re.compile(r'\b(?:Seite|page)\s+([0-9ivxlcdm]+)', re.I)
LOC = re.compile(r'\b(?:Position|Location|Loc\.)\s+(\d+)(?:-(\d+))?', re.I)
ADDED = re.compile(r'\b(?:Hinzugefügt am|Added on)\s+(.+?)\s*$')


def _loc(m):
    """(von, bis) – ältere Geräte kürzen das Ende ab: »Loc. 433-34« ist 433–434."""
    a = int(m.group(1))
    if not m.group(2):
        return a, a
    b = m.group(2)
    if int(b) < a:
        b = str(a)[:len(str(a)) - len(b)] + b
    return a, int(b)


def parse(raw):
    """Alle Einträge der Datei als [{book, author, kind, page, loc, text, added, n}] in der Reihenfolge der Datei."""
    out = []
    for n, chunk in enumerate(raw.replace('﻿', '').replace('\r\n', '\n').replace('\r', '\n').split(SEP)):
        lines = chunk.split('\n')
        while lines and not lines[0].strip():
            lines.pop(0)
        if len(lines) < 2 or not lines[1].lstrip().startswith('-'):
            continue
        head, meta, text = lines[0].strip(), lines[1], '\n'.join(lines[2:]).strip()
        if not (LOC.search(meta) or ADDED.search(meta) or any(rx.search(meta) for _, rx in KINDS)):
            continue  # eine unterstrichene Überschrift oder ein Spiegelstrich ist keine Kennzeile – sonst wäre jede Textdatei ein Kindle
        m = re.match(r'^(.*\S)\s*\(([^()]*)\)$', head)  # der Autor steht in der letzten Klammer; Titel dürfen eigene Klammern haben
        book, author = (m.group(1), m.group(2).strip()) if m else (head, '')
        kind = next((k for k, rx in KINDS if rx.search(meta)), 'highlight' if text else 'bookmark')
        pm, lm, am = PAGE.search(meta), LOC.search(meta), ADDED.search(meta)
        out.append(dict(book=book, author=author, kind=kind, page=pm.group(1) if pm else None, loc=_loc(lm) if lm else None,
                        text=text, added=am.group(1) if am else '', n=n))
    return out


def key(e):
    return e['book'] + '\x00' + e['author']


def books(entries):
    """Die Bücher der Datei, zuletzt bearbeitetes zuerst: [{key, title, author, highlights, notes}]."""
    seen = {}
    for e in entries:
        b = seen.setdefault(key(e), dict(key=key(e), title=e['book'], author=e['author'], highlights=0, notes=0, last=0))
        b['last'] = e['n']
        if e['kind'] in ('highlight', 'note') and e['text']:
            b['highlights' if e['kind'] == 'highlight' else 'notes'] += 1
    return [dict((k, v) for k, v in b.items() if k != 'last') for b in sorted(seen.values(), key=lambda b: -b['last'])
            if b['highlights'] or b['notes']]


def limited(text):
    """Hat der Verlag das Kopieren begrenzt, steht statt des Texts eine Meldung in spitzen Klammern
    (»<You have reached the clipping limit for this item>«)."""
    return text.startswith('<') and text.endswith('>')


def _overlap(a, b):
    if a['loc'] and b['loc']:
        return a['loc'][0] <= b['loc'][1] + 1 and b['loc'][0] <= a['loc'][1] + 1
    if a['page'] and b['page']:
        return a['page'] == b['page']
    return True


def _order(e):
    return (e['loc'][0] if e['loc'] else float('inf'), e['n'])


def items(entries, k):
    """Was aus einem Buch zu Zetteln wird, in der Reihenfolge des Buchs: [{text, note, page, loc}] und die Zahl der
    Markierungen, die der Kopierschutz des Verlags verschluckt hat.

    Erweitert man eine Markierung, legt der Kindle einen neuen Eintrag an und lässt den alten stehen; ein Text, der in
    einer späteren oder längeren Markierung an derselben Stelle vollständig enthalten ist, fällt darum weg. Eine eigene
    Notiz gehört zu der Markierung, an deren Ende sie steht – sie wird deren Anmerkung. Notizen ohne Markierung
    werden eigene Zettel."""
    mine = [e for e in entries if key(e) == k and e['text']]
    hs = [e for e in mine if e['kind'] == 'highlight' and not limited(e['text'])]
    cut = sum(1 for e in mine if e['kind'] == 'highlight' and limited(e['text']))
    norm = lambda s: ' '.join(s.split())
    keep = [h for i, h in enumerate(hs) if not any(
        j != i and norm(h['text']) in norm(o['text']) and (len(norm(o['text'])) > len(norm(h['text'])) or j > i) and _overlap(h, o)
        for j, o in enumerate(hs))]
    out = [dict(text=norm(h['text']), note='', page=h['page'], loc=h['loc'], n=h['n']) for h in sorted(keep, key=_order)]
    for e in (e for e in mine if e['kind'] == 'note'):
        at = e['loc'][0] if e['loc'] else None
        home = [o for o in out if o['text'] and at is not None and o['loc'] and o['loc'][0] <= at <= o['loc'][1]]
        home.sort(key=lambda o: (o['loc'][1] != at, -o['n']))  # am liebsten die Markierung, die genau dort endet
        if home:
            home[0]['note'] = (home[0]['note'] + '\n\n' if home[0]['note'] else '') + e['text'].strip()
        else:
            out.append(dict(text='', note=e['text'].strip(), page=e['page'], loc=e['loc'], n=e['n']))
    out.sort(key=_order)
    return [dict((x, v) for x, v in o.items() if x != 'n') for o in out], cut


def read(path):
    with open(path, encoding='utf-8-sig', errors='replace') as f:
        return parse(f.read())


def find():
    """Ein angeschlossener Kindle, der als Laufwerk erscheint (ältere Geräte): Pfade zu »My Clippings.txt«. Kindles ab
    2024 melden sich als Mediengerät (MTP) – dort muss der Nutzer die Datei erst auf den Rechner kopieren."""
    if sys.platform == 'win32':
        import ctypes
        # Nur Wechseldatenträger: ein getrenntes Netzlaufwerk ließe os.path.isfile sonst sekundenlang warten
        drives = [d + ':\\' for d in string.ascii_uppercase[2:] if ctypes.windll.kernel32.GetDriveTypeW(d + ':\\') == 2]
        cands = [os.path.join(d, 'documents', FILE) for d in drives]
    elif sys.platform == 'darwin':
        cands = glob.glob('/Volumes/*/documents/' + FILE)
    else:
        cands = glob.glob('/media/*/*/documents/' + FILE) + glob.glob('/run/media/*/*/documents/' + FILE) + glob.glob('/media/*/documents/' + FILE)
    return [p for p in cands if os.path.isfile(p)]
