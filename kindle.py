"""Markierungen vom Kindle (#61): die Datei »My Clippings.txt« lesen, je Buch ordnen und doppelte Einträge auflösen.

Der Kindle hängt jede Markierung, Notiz und jedes Lesezeichen als Eintrag an diese eine Datei an, getrennt durch
»==========«. Ein Eintrag besteht aus Titelzeile (»Titel (Autor)«), Kennzeile und Text:

    Moby Dick (Melville, Herman)
    - Ihre Markierung auf Seite 32 | bei Position 433-434 | Hinzugefügt am Samstag, 14. Mai 2016 14:03:23

    They say that men who have seen the world …

Die Kennzeile folgt der Sprache des Geräts (»- Your Highlight on page 32 | Location 433-434 | Added on …«). Erkannt
werden Deutsch und Englisch; was sich nicht zuordnen lässt, aber Text hat, gilt als Markierung."""
import glob, os, re, string, sys
import kfx

SEP = '=========='
FILE = 'My Clippings.txt'  # heißt auch auf deutschen Geräten so
KINDS = [('note', re.compile(r'\b(?:Notiz|Note)\b', re.I)), ('bookmark', re.compile(r'\b(?:Lesezeichen|Bookmark)\b', re.I)),
         ('highlight', re.compile(r'\b(?:Markierung|Highlight)\b', re.I))]
PAGE = re.compile(r'\b(?:Seite|page)\s+([0-9ivxlcdm]+)', re.I)
LOC = re.compile(r'\b(?:Position|Location|Loc\.)\s+(\d+)(?:-(\d+))?', re.I)
ADDED = re.compile(r'\b(?:Hinzugefügt am|Added on)\s+(.+?)\s*$')
# Monate an den ersten drei Buchstaben, deutsch und englisch (»Jänner« aus Österreich inbegriffen)
MONTHS = dict(jan=1, jän=1, feb=2, mär=3, mar=3, apr=4, mai=5, may=5, jun=6, jul=7, aug=8, sep=9, okt=10, oct=10, nov=11,
              dez=12, dec=12)


def _loc(m):
    """(von, bis) – ältere Geräte kürzen das Ende ab: »Loc. 433-34« ist 433–434."""
    a = int(m.group(1))
    if not m.group(2):
        return a, a
    b = m.group(2)
    if int(b) < a:
        b = str(a)[:len(str(a)) - len(b)] + b
    return a, int(b)


def day(added):
    """Das Datum aus »Mittwoch, 30. April 2025 17:03:43«, »Friday, 7 March 2025 10:00:00« oder »Wednesday, April 30, 2025
    5:03:43 PM« als »2025-04-30« – leer, wenn es sich nicht lesen lässt."""
    if re.match(r'^\d{4}-\d\d-\d\d$', added or ''):
        return added
    m = re.search(r'(\d{1,2})\.?\s+([^\W\d]{3,})\.?\s+(\d{4})', added) or re.search(r'([^\W\d]{3,})\.?\s+(\d{1,2}),?\s+(\d{4})', added)
    if not m:
        return ''
    d, mon = (m.group(1), m.group(2)) if m.group(1).isdigit() else (m.group(2), m.group(1))
    mo = MONTHS.get(mon[:3].casefold())
    return '%s-%02d-%02d' % (m.group(3), mo, int(d)) if mo and 1 <= int(d) <= 31 else ''


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
    """Die Bücher der Datei, zuletzt bearbeitetes zuerst: [{key, title, author, highlights, notes, bookmarks, day}], day
    ist der Tag des jüngsten Eintrags. Auch Bücher mit nur Lesezeichen stehen darin – daraus wird zwar kein Zettel, aber
    wer das Buch in der Liste vermisst, soll sehen, warum."""
    seen = {}
    for e in entries:
        b = seen.setdefault(key(e), dict(key=key(e), title=e['book'], author=e['author'], highlights=0, notes=0, bookmarks=0,
                                         day='', last=0))
        b['last'], b['day'] = e['n'], max(b['day'], day(e['added']))
        if e['kind'] in ('highlight', 'note') and e['text']:
            b['highlights' if e['kind'] == 'highlight' else 'notes'] += 1
        elif e['kind'] == 'bookmark':
            b['bookmarks'] += 1
    return [dict((k, v) for k, v in b.items() if k != 'last') for b in sorted(seen.values(), key=lambda b: -b['last'])
            if b['highlights'] or b['notes'] or b['bookmarks']]


def usable(b):
    """Wird aus diesem Buch mindestens ein Zettel?"""
    return bool(b['highlights'] or b['notes'])


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
    """Ein angeschlossener Kindle, der als Laufwerk erscheint (ältere Geräte): die Wurzelordner. Kindles ab 2024 melden
    sich als Mediengerät (MTP) – die holt unter Windows `fetch`."""
    if sys.platform == 'win32':
        import ctypes
        # Nur Wechseldatenträger: ein getrenntes Netzlaufwerk ließe os.path.isfile sonst sekundenlang warten
        roots = [d + ':\\' for d in string.ascii_uppercase[2:] if ctypes.windll.kernel32.GetDriveTypeW(d + ':\\') == 2]
    elif sys.platform == 'darwin':
        roots = glob.glob('/Volumes/*/')
    else:
        roots = glob.glob('/media/*/*/') + glob.glob('/run/media/*/*/') + glob.glob('/media/*/')
    return [r for r in roots if os.path.isfile(os.path.join(r, 'documents', FILE)) or _dbs(r)]


# ---- Neuere Firmware (ab 5.19, Sommer 2026): Markierungen in einer Datenbank statt in »My Clippings.txt«
#
# system/ksdk/.annotations/amzn1.account.<Konto>/ksdk_annotation_v1.db, SQLite. Jede Markierung steht dort als JSON mit
# Anfang und Ende als Position im Buch (»shortPosition«), ohne Text; den liest `kfx` aus dem Buch – nur bei Büchern
# ohne Kopierschutz. Dieselbe Markierung kann in mehreren Tabellen stehen (abgeglichen, unterwegs, noch nicht
# abgeglichen); die spätere gilt. Tabellen und JSON hat K3yg/kindle-highlights-recovery (GPL) beschrieben.
DB = 'ksdk_annotation_v1.db'
TABLES = [('server_view', 'dataset_id'), ('staging_server_view', 'dataset_id'), ('nonsyncable_annotations', 'book_id'),
          ('local_edit', 'dataset_id')]
TYPES = dict(HIGHLIGHT='highlight', NOTE='note', BOOKMARK='bookmark')
DATASETS = {1: 'highlight', 2: 'bookmark', 3: 'note'}  # nur, wenn das JSON keinen Typ nennt
LOCKED = ('EBOK', 'EBSP')  # gekaufte Bücher und Leseproben: verschlüsselt
BOOKS = ('.kfx', '.azw', '.azw3', '.azw8', '.mobi', '.pdf', '.kfx-zip')
SKIP = ('dictionaries', '.cache', 'system')  # Wörterbücher und Zwischenspeicher sind keine Bücher
COPY = 'abzug.json'  # in einer Kopie vom Gerät (`fetch`): Name des Kindle und die Dateinamen aller Bücher darauf


def _dbs(root):
    found = glob.glob(os.path.join(glob.escape(root), 'system', 'ksdk', '.annotations', '*', DB))
    return found or [p for p in (os.path.join(root, DB),) if os.path.isfile(p)]


def annotations(path):
    """Die Einträge der Datenbank: [{ident, ctype, kind, start, end, note, ms}] – ident ist die Kennung des Buchs
    (ASIN, bei eigenen Dokumenten eine lange Hexzahl), ctype die Art (PDOC eigenes Dokument, EBOK gekauft …)."""
    import json, pathlib, sqlite3
    # immutable: nichts schreiben, auch keine Journaldatei – die Datei kann auf dem Kindle selbst liegen
    con = sqlite3.connect(pathlib.Path(os.path.abspath(path)).as_uri() + '?mode=ro&immutable=1', uri=True)
    rows, gone = {}, set()
    try:
        have = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for table, col in TABLES:
            if table not in have:
                continue
            cols = {r[1] for r in con.execute('PRAGMA table_info("%s")' % table)}
            if not {'annotation_id', 'serialized_payload', col} <= cols:
                continue
            q = 'SELECT annotation_id, "%s", serialized_payload, %s, %s FROM "%s"' % (
                col, 'dataset' if 'dataset' in cols else 'NULL', 'action' if 'action' in cols else 'NULL', table)
            for aid, bid, payload, ds, action in con.execute(q):
                if action is not None and 'DEL' in str(action).upper():
                    gone.add((bid, aid))
                    continue
                try:
                    p = json.loads(payload)
                except ValueError:
                    continue
                if isinstance(p, dict):
                    rows[(bid, aid)] = (p, ds)
    finally:
        con.close()
    out = []
    for (bid, aid), (p, ds) in rows.items():
        kind = TYPES.get(str(p['type']).upper()) if p.get('type') else DATASETS.get(ds)
        start = (p.get('start_position') or p.get('position') or {}).get('shortPosition')
        end = (p.get('end_position') or {}).get('shortPosition', start)
        if not kind or (bid, aid) in gone or not isinstance(start, int) or not isinstance(end, int):
            continue
        try:
            note = json.loads(p.get('json_metadata') or '{}').get('note_text') or ''
        except (ValueError, AttributeError):
            note = ''
        parts = str(bid).split('-')
        out.append(dict(ident=parts[0], ctype=parts[1] if len(parts) > 1 else '', kind=kind, start=min(start, end),
                        end=max(start, end), note=note, ms=p.get('created_time') or 0))
    return sorted(out, key=lambda a: (a['ms'], a['start']))


def _ident(name):
    """Kennung und Titel aus dem Dateinamen, den der Kindle vergibt: »Altes Land_ Roman_B00R6UC8WK.kfx«,
    »Fatma - Immanuel Walker_D0A108F4C57D409AB49207AD20EF81EB.kfx«, Leseproben mit »_sample«."""
    m = re.match(r'^(.*?)_([0-9A-Z]{10}|[0-9A-F]{32})(?:_sample)?(?:\.[^.]+)?$', name, re.I)
    if not m:
        return '', os.path.splitext(name)[0]
    return m.group(2).upper(), m.group(1).replace(' _ ', ' | ').replace('_ ', ': ').strip()


def device(root):
    """Was in einem Kindle-Ordner (dem Laufwerk oder einer Kopie davon) für die Zettel liegt:
    (Pfad zu My Clippings.txt oder '', [Datenbanken], {Kennung: Buchdatei}, {Kennung: Titel aus dem Dateinamen})."""
    clip = next((p for p in (os.path.join(root, 'documents', FILE), os.path.join(root, FILE)) if os.path.isfile(p)), '')
    files, titles = {}, {}
    for cur, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if not d.lower().endswith('.sdr') and d.lower() not in SKIP]
        for n in names:
            if n.lower().endswith(BOOKS):
                i, title = _ident(n)
                if i:
                    titles.setdefault(i, title)
                    if n.lower().endswith('.kfx'):
                        files.setdefault(i, os.path.join(cur, n))
    try:
        import json
        with open(os.path.join(root, COPY), encoding='utf-8') as f:
            for n in json.load(f).get('names') or []:
                i, title = _ident(n)
                if i:
                    titles.setdefault(i, title)
    except (OSError, ValueError):
        pass
    return clip, _dbs(root), files, titles


def _root(path):
    """Der Kindle-Ordner zu einem Pfad: der Ordner selbst, oder bei »documents/My Clippings.txt« auf dem Laufwerk
    dessen Wurzel – dann kommen die neuen Markierungen aus der Datenbank gleich mit."""
    if os.path.isdir(path):
        return path
    up = os.path.dirname(os.path.abspath(path))
    if os.path.basename(up).lower() == 'documents' and _dbs(os.path.dirname(up)):
        return os.path.dirname(up)
    return ''


def _iso(ms):
    import datetime
    try:
        return (datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=ms)).strftime('%Y-%m-%d')
    except (OverflowError, TypeError, ValueError):
        return ''


def _alnum(s):
    return ''.join(c for c in (s or '').casefold() if c.isalnum())


def _same(e):
    """Woran derselbe Eintrag in beiden Quellen zu erkennen ist: Buch, Art und Text – bei Lesezeichen die Stelle."""
    return key(e), e['kind'], ' '.join(e['text'].replace('\xad', '').split()) if e['text'] else e['loc'] and e['loc'][0]


def load(path):
    """Alles aus »My Clippings.txt« und – bei einem Kindle-Ordner – der Datenbank, als Einträge wie `parse` sie liefert,
    dazu {locked: [{title, n, why}], device: Datenbank gefunden}. Was in beiden steht, zählt einmal. »locked« sind
    Bücher mit Markierungen, deren Text das Programm nicht lesen kann: gekauft (why='drm') oder ohne Buchdatei auf dem
    Kindle (why='missing') – gezählt nur, was nach dem letzten Eintrag in My Clippings.txt entstand."""
    root = _root(path)
    if not root and not os.path.isfile(path):
        raise OSError(path)
    clip, dbs, files, titles = device(root) if root else (path, [], {}, {})
    clips = read(clip) if clip else []
    last = max((day(e['added']) for e in clips), default='')
    have = {_same(e) for e in clips}
    named = {_alnum(e['book']): (e['book'], e['author']) for e in clips}  # Titel wie in My Clippings.txt: ein Buch, ein Eintrag
    news, locked, books = [], {}, {}
    for a in (a for db in dbs for a in annotations(db)):
        i = a['ident'].upper()
        if i not in books:
            book, why = None, 'drm' if a['ctype'] in LOCKED else 'missing'
            if why == 'missing' and i in files:
                try:
                    book = kfx.read(files[i])
                except kfx.Locked:
                    why = 'drm'
                except Exception:  # eine beschädigte Datei soll nicht das ganze Fenster verderben
                    pass
            books[i] = book, why
        book, why = books[i]
        if not book:
            if a['kind'] != 'bookmark' and _iso(a['ms']) > last:
                k = titles.get(i) or i, why
                locked[k] = locked.get(k, 0) + 1
            continue
        title, author = named.get(_alnum(book.title), (book.title or titles.get(i) or i, book.author))
        loc = book.location(a['start']), book.location(a['end'])
        text = book.quote(a['start'], a['end']) if a['kind'] == 'highlight' else ' '.join(a['note'].split())
        if a['kind'] != 'bookmark' and not text:
            continue
        e = dict(book=title, author=author, kind=a['kind'], page=book.page(a['start']), loc=loc if loc[0] else None,
                 text='' if a['kind'] == 'bookmark' else text, added=_iso(a['ms']), n=0)
        if _same(e) not in have:
            news.append(e)
            have.add(_same(e))
    every = sorted(enumerate(clips + news), key=lambda x: (day(x[1]['added']), x[0] >= len(clips), x[0]))
    for n, (_, e) in enumerate(every):
        e['n'] = n
    return [e for _, e in every], dict(device=bool(dbs), locked=[dict(title=t, n=n, why=w) for (t, w), n in locked.items()])


# ---- Kindles ab 2024 sind unter Windows kein Laufwerk, sondern ein Mediengerät (MTP): Python kommt nicht an die
# Dateien, der Explorer schon. Darum kopiert PowerShell über dessen Shell-Objekt, was gebraucht wird, in einen Ordner
# des Programms; `load` liest den dann wie ein Laufwerk. Auf dem Kindle wird nichts verändert.
MTP = r'''
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$a = $env:FK_KINDLE | ConvertFrom-Json
$sh = New-Object -ComObject Shell.Application
# Amazon hat die USB-Herstellernummer 1949; ein Kindle als Laufwerk (älteres Gerät) liest Python selbst
$dev = @($sh.Namespace(17).Items() | Where-Object { -not $_.IsFileSystem -and ($_.Name -like '*Kindle*' -or $_.Path -like '*vid_1949*') })[0]
if (-not $dev) { '{}'; exit }
function Sub($f, $n) { if ($f) { @($f.GetFolder.Items() | Where-Object { $_.Name -eq $n })[0] } }
$store = @($dev.GetFolder.Items() | Where-Object { Sub $_ 'documents' })[0]
if (-not $store) { @{ device = $dev.Name; locked = $true } | ConvertTo-Json -Compress; exit }
function Fetch($item, $rel) {
  $dir = Join-Path $a.dest (Split-Path $rel)
  New-Item -ItemType Directory -Force $dir | Out-Null
  $target = Join-Path $a.dest $rel
  $size = $item.ExtendedProperty('System.Size')
  $sh.Namespace($dir).CopyHere($item, 4 + 16 + 1024)
  # Das Kopieren läuft im Hintergrund weiter: warten, bis die Datei vollständig da ist
  for ($t = 0; $t -lt 1500; $t++) {
    Start-Sleep -Milliseconds 200
    if ((Test-Path -LiteralPath $target) -and (Get-Item -LiteralPath $target).Length -ge $size) {
      try { [IO.File]::Open($target, 'Open', 'Read', 'None').Close(); return } catch {}
    }
  }
  throw "Zeitüberschreitung: $rel"
}
function Walk($f, $rel) {
  foreach ($i in $f.GetFolder.Items()) {
    $r = "$rel/$($i.Name)"
    if ($i.IsFolder) { if ($i.Name -notlike '*.sdr' -and $i.Name -notin 'dictionaries', '.cache') { Walk $i $r } }
    else { @{ rel = $r.TrimStart('/'); size = [int64]$i.ExtendedProperty('System.Size'); mtime = "$($i.ExtendedProperty('System.DateModified'))" } }
  }
}
$docs = Sub $store 'documents'
if ($a.mode -eq 'list') {
  $c = Sub $docs 'My Clippings.txt'
  if ($c) { Fetch $c 'documents/My Clippings.txt' }
  foreach ($acc in @((Sub (Sub (Sub $store 'system') 'ksdk') '.annotations').GetFolder.Items() | Where-Object { $_.IsFolder })) {
    $db = Sub $acc 'ksdk_annotation_v1.db'
    if ($db) { Fetch $db "system/ksdk/.annotations/$($acc.Name)/ksdk_annotation_v1.db" }
  }
  @{ device = $dev.Name; files = @(Walk $docs 'documents') } | ConvertTo-Json -Compress -Depth 4
} else {
  foreach ($rel in $a.files) {
    $f = $store
    foreach ($part in $rel.Split('/')) { $f = Sub $f $part }
    if ($f) { Fetch $f $rel }
  }
  '{}'
}
'''


def _mtp(**args):
    import base64, json, subprocess
    env = dict(os.environ, FK_KINDLE=json.dumps(args))
    r = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-EncodedCommand',
                        base64.b64encode(MTP.encode('utf-16-le')).decode()], env=env, capture_output=True, timeout=900,
                       creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    out = r.stdout.decode('utf-8', 'replace').strip().splitlines()
    if r.returncode or not out:
        raise OSError(r.stderr.decode('utf-8', 'replace').strip() or 'PowerShell')
    return json.loads(out[-1])


def fetch(dest):
    """Unter Windows einen als Mediengerät angeschlossenen Kindle nach dest holen: My Clippings.txt, die Datenbank der
    Markierungen und die Bücher ohne Kopierschutz, zu denen es Markierungen gibt. Ein Buch, das beim letzten Mal
    schon gleich groß und gleich alt kam, wird nicht noch einmal übers Kabel geholt. Gibt den Namen des Geräts zurück,
    None ohne Kindle; ValueError('kindle_gesperrt'), wenn Windows den Speicher nicht sieht – beim Sperrbildschirm."""
    import json, shutil
    if sys.platform != 'win32':
        return None
    new = dest + '.neu'
    shutil.rmtree(new, ignore_errors=True)
    os.makedirs(new)
    try:
        r = _mtp(mode='list', dest=new)
        if not r.get('device'):
            return None
        if r.get('locked'):
            raise ValueError('kindle_gesperrt')
        want = {a['ident'].upper() for db in _dbs(new) for a in annotations(db) if a['ctype'] not in LOCKED}
        try:
            with open(os.path.join(dest, COPY), encoding='utf-8') as f:
                before = json.load(f).get('files') or {}
        except (OSError, ValueError):
            before = {}
        files, get = {}, []
        for f in r.get('files') or []:
            if f['rel'].lower().endswith('.kfx') and _ident(os.path.basename(f['rel']))[0] in want:
                files[f['rel']] = [f['size'], f['mtime']]
                old = os.path.join(dest, *f['rel'].split('/'))
                if before.get(f['rel']) == files[f['rel']] and os.path.isfile(old):
                    os.makedirs(os.path.dirname(os.path.join(new, *f['rel'].split('/'))), exist_ok=True)
                    shutil.copy2(old, os.path.join(new, *f['rel'].split('/')))
                else:
                    get.append(f['rel'])
        if get:
            _mtp(mode='copy', dest=new, files=get)
        with open(os.path.join(new, COPY), 'w', encoding='utf-8') as f:
            json.dump(dict(device=r['device'], names=[os.path.basename(f['rel']) for f in r.get('files') or []], files=files),
                      f, ensure_ascii=False)
        shutil.rmtree(dest, ignore_errors=True)
        os.replace(new, dest)
        return r['device']
    finally:
        shutil.rmtree(new, ignore_errors=True)
