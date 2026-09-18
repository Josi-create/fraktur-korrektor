"""Fraktur-Korrektor: Lesen und Korrigieren von OCR-Text neben dem Seitenbild.
py server.py [<buchordner>] [--port 8765] [--dic <hunspell-pfad>] [--title "…"] [--no-browser] [--lan]

Ohne Buchordner erscheint die Bibliothek (Bücher öffnen, Transkribus-Export importieren).
Buchordner: NNN.txt (eine Datei je Seite), lines.json (Zeilengeometrie), img/NNN.png|jpg,
optional autokorr.log, whitelist.txt; lesezeichen.json und korrekturen.log werden angelegt."""
import sys, os, json, re, glob, time, hashlib, threading, subprocess, socketserver, urllib.parse, webbrowser, argparse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import korrlib, pagexml
from korrlib import read_page, corpus_freq, joined_tokens, in_dict

HERE = os.path.dirname(os.path.abspath(__file__))
DONATE_URL = ''  # z. B. https://buymeacoffee.com/<name>; leer = kein Spenden-Link
LIBFILE = os.path.join(korrlib.HOME, 'bibliothek.json')
LIBLOCK = threading.RLock()
BOOKS = {}
DEFAULT = None  # id des Buchs von der Kommandozeile
IMGTYPES = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg'}


def version():
    try:
        return re.search(r'^version\s*=\s*"([^"]+)"', open(os.path.join(HERE, 'pyproject.toml'), encoding='utf-8').read(), re.M).group(1)
    except (OSError, AttributeError):
        return ''


def known(w, freq):
    """Wörterbuch, oder häufig im Buch (Namen) – kurze Wörter schützt die Häufigkeit nicht (ber, bie, baß …)."""
    return in_dict(w) or (len(w) > 4 and freq.get(w, 0) >= 3)


def write_atomic(path, text):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(text)
    os.replace(tmp, path)


def image_size(path):
    """Breite/Höhe aus dem PNG-IHDR bzw. dem JPEG-SOF-Segment lesen."""
    try:
        with open(path, 'rb') as f:
            b = f.read(24)
            if b[:8] == b'\x89PNG\r\n\x1a\n':
                return (int.from_bytes(b[16:20], 'big'), int.from_bytes(b[20:24], 'big'))
            if b[:2] != b'\xff\xd8':
                return None
            f.seek(2)
            while True:
                s = f.read(4)
                if len(s) < 4 or s[0] != 0xFF:
                    return None
                if 0xC0 <= s[1] <= 0xCF and s[1] not in (0xC4, 0xC8, 0xCC):
                    d = f.read(5)
                    return (int.from_bytes(d[3:5], 'big'), int.from_bytes(d[1:3], 'big'))
                f.seek(int.from_bytes(s[2:4], 'big') - 2, 1)
    except OSError:
        return None


def book_id(folder):
    return hashlib.md5(os.path.normcase(os.path.abspath(folder)).encode('utf-8')).hexdigest()[:8]


def default_title(folder):
    t = os.path.abspath(folder)
    while os.path.basename(t).lower() in ('korr', 'ocr'):
        t = os.path.dirname(t)
    return os.path.basename(t)


def page_files(folder):
    return sorted(glob.glob(os.path.join(folder, '[0-9][0-9][0-9].txt')))


def find_book_folder(path):
    """Der Ordner selbst oder – wenn jemand den übergeordneten Ordner wählt – korr bzw. ocr/korr darin."""
    for c in (path, os.path.join(path, 'korr'), os.path.join(path, 'ocr', 'korr')):
        if os.path.isdir(c) and page_files(c):
            return os.path.abspath(c)
    return None


class Book:
    """Ein Buchordner. Seiten im Speicher; Dateien werden bei geänderter mtime neu gelesen (paralleles Editieren erlaubt)."""

    def __init__(self, folder, title=None):
        self.folder = os.path.abspath(folder)
        self.id = book_id(self.folder)
        self.title = title or default_title(self.folder)
        self.imgdir = os.path.join(self.folder, 'img')
        self.wlpath = os.path.join(self.folder, 'whitelist.txt')
        self.bmpath = os.path.join(self.folder, 'lesezeichen.json')
        self.klogpath = os.path.join(self.folder, 'korrekturen.log')
        self.lock = threading.RLock()
        try:
            self.geo = json.load(open(os.path.join(self.folder, 'lines.json'), encoding='utf-8'))
        except OSError:
            self.geo = {}
        self.unsicher = self.autokorr_unsicher()
        self.pages, self.mt, self.freq, self.wl, self.wlmt, self.fcache, self.size = {}, {}, {}, set(), None, {}, {}

    def autokorr_unsicher(self):
        out = {}
        p = os.path.join(self.folder, 'autokorr.log')
        if os.path.exists(p):
            for l in open(p, encoding='utf-8'):
                f = l.rstrip('\n').split('\t')
                if len(f) == 5 and f[4] == 'unsicher':
                    out.setdefault(f[0], []).append((int(f[1]) - 1, f[3].replace('¬', '')))
        return out

    def klog(self, kind, pg, line, old, new):
        """Korrekturprotokoll: Zeit, Art (edit | serie:ID | undo:ID), Seite, Zeile (1-basiert), alte Zeile, neue Zeile."""
        with open(self.klogpath, 'a', encoding='utf-8') as f:
            f.write('\t'.join([time.strftime('%Y-%m-%d %H:%M:%S'), kind, pg, str(line + 1), old, new]) + '\n')

    def write_page(self, pg, lines):
        write_atomic(os.path.join(self.folder, pg + '.txt'), '\n'.join(lines) + '\n')

    def refresh(self):
        changed = False
        seen = set()
        for f in page_files(self.folder):
            pg = os.path.basename(f)[:3]
            seen.add(pg)
            mt = os.path.getmtime(f)
            if self.mt.get(pg) != mt:
                self.pages[pg] = read_page(f)
                self.mt[pg] = mt
                changed = True
        for pg in set(self.pages) - seen:
            del self.pages[pg], self.mt[pg]
            changed = True
        if changed:
            self.pages = dict(sorted(self.pages.items()))
            self.freq = corpus_freq(self.pages)
        wlmt = os.path.getmtime(self.wlpath) if os.path.exists(self.wlpath) else None
        if wlmt != self.wlmt:
            self.wl = set(open(self.wlpath, encoding='utf-8').read().split()) if wlmt else set()
            self.wlmt = wlmt
            self.fcache.clear()

    def flags(self, pg):
        key = (self.mt[pg], self.wlmt)
        c = self.fcache.get(pg)
        if c and c[0] == key:
            return c[1]
        lines, wl, freq = self.pages[pg], self.wl, self.freq
        out = []
        toks, joined = joined_tokens(lines)
        jstart = {(i, s1) for i, s1, w1, j, w2 in joined}
        jend = {(j, 0) for i, s1, w1, j, w2 in joined}
        for i, s1, w1, j, w2 in joined:
            if not (known(w1 + w2, freq) or (w1 + w2) in wl):
                out.append(dict(line=i, start=s1, len=len(w1), word=w1 + '¬' + w2, kind='oov'))
        for i, tl in enumerate(toks):
            if lines[i].startswith('#'):
                continue
            for s, w in tl:
                if (i, s) in jstart or (i, s) in jend or len(w) < 2:
                    continue
                if not (known(w, freq) or w in wl):
                    out.append(dict(line=i, start=s, len=len(w), word=w, kind='oov'))
        have = {(f['line'], f['start']) for f in out}
        for i, cand in self.unsicher.get(pg, []):
            if cand in wl:
                continue
            for ii in (i, i - 1, i + 1):
                hit = [(s, w) for s, w in toks[ii] if w == cand and (ii, s) not in have] if 0 <= ii < len(toks) else []
                if hit:
                    out.append(dict(line=ii, start=hit[0][0], len=len(cand), word=cand, kind='auto'))
                    have.add((ii, hit[0][0]))
                    break
        out.sort(key=lambda f: (f['line'], f['start']))
        self.fcache[pg] = (key, out)
        return out

    def img_file(self, pg):
        for e in IMGTYPES:
            p = os.path.join(self.imgdir, pg + e)
            if os.path.exists(p):
                return p
        return None

    def img_url(self, pg):
        p = self.img_file(pg)
        return '/buch/%s/img/%s' % (self.id, os.path.basename(p)) if p else None

    def img_size(self, pg):
        if pg not in self.size:
            p = self.img_file(pg)
            self.size[pg] = image_size(p) if p else None
        return self.size[pg]

    def geo_lines(self, pg, lines):
        """Ordnet den Textzeilen die XML-Zeilen zu; None wenn die Anzahl nicht passt.
        Transkribus legt die Seite höhenfüllend und horizontal zentriert auf sein Format (g['w'] x g['h'])."""
        g = self.geo.get(pg)
        sz = self.img_size(pg)
        if not g or not sz or not g['lines']:
            return None
        L = g['lines']
        head = [l for l in L if l['kind'] == 'head']
        body = [l for l in L if l['kind'] == 'body']
        fn = [l for l in L if l['kind'] == 'fn']
        # Textzeilen der Reihe nach auf die XML-Zeilen legen; '---' (Fußnotentrenner) darf an beliebiger Stelle stehen
        geoms, k, seq = body + fn, 0, []
        for n, l in enumerate(lines):
            if n == 0 and l.startswith('#'):
                seq.append(head[0] if head else None)
            elif l == '---':
                seq.append(None)
            elif k < len(geoms):
                seq.append(geoms[k])
                k += 1
            else:
                return None
        if any(x['text'].strip() for x in geoms[k:]):  # nur leere Zeilen dürfen am Ende im Text fehlen
            return None
        w, h = sz
        s = h / g['h']
        ox = (w - g['w'] * s) / 2
        return [None if l is None else dict(x0=l['x0'] * s + ox, x1=l['x1'] * s + ox, y0=l['y0'] * s, y1=l['y1'] * s) for l in seq]

    def page_data(self, pg):
        with self.lock:
            self.refresh()
            lines = self.pages[pg]
            return dict(page=pg, lines=lines, geo=self.geo_lines(pg, lines), flags=self.flags(pg), img=self.img_url(pg))

    def overview(self):
        with self.lock:
            self.refresh()
            return [dict(page=pg, n=len(self.flags(pg))) for pg in self.pages]

    def occurrences(self, word, limit=500):
        """Alle Vorkommen eines Wortes im Buch (auch über Zeilentrennung ¬ hinweg), mit Zeilengeometrie."""
        out = []
        with self.lock:
            self.refresh()
            for pg, lines in self.pages.items():
                toks, joined = joined_tokens(lines)
                frag = {(i, s1) for i, s1, w1, j, w2 in joined} | {(j, 0) for i, s1, w1, j, w2 in joined}
                hits = [(i, s1, len(w1), True) for i, s1, w1, j, w2 in joined if w1 + w2 == word]
                hits += [(i, s, len(w), False) for i, tl in enumerate(toks) if not lines[i].startswith('#')
                         for s, w in tl if w == word and (i, s) not in frag]
                if not hits:
                    continue
                geo = self.geo_lines(pg, lines)
                for i, s, n, join in sorted(hits):
                    out.append(dict(page=pg, line=i, start=s, len=n, join=join, text=lines[i],
                                    text2=lines[i + 1] if join else None, geo=geo[i] if geo else None,
                                    geo2=geo[i + 1] if geo and join else None, img=self.img_url(pg)))
                    if len(out) >= limit:
                        return out
        return out

    def series_replace(self, word, new, items):
        """Ersetzt word durch new an den angegebenen Stellen; nur wenn die Zeilen noch unverändert sind."""
        sid = time.strftime('%Y%m%d-%H%M%S')
        done = skipped = 0
        with self.lock:
            self.refresh()
            bypage = {}
            for it in items:
                bypage.setdefault(it['page'], []).append(it)
            for pg, its in bypage.items():
                if pg not in self.pages:
                    skipped += len(its)
                    continue
                old = self.pages[pg]
                lines = list(old)
                toks, joined = joined_tokens(old)
                for it in sorted(its, key=lambda x: (x['line'], -x['start'])):  # je Zeile von rechts nach links
                    i, st = it['line'], it['start']
                    if not (0 <= i < len(old)) or old[i] != it['text']:
                        skipped += 1
                        continue
                    if it.get('join'):
                        m = [(w1, w2) for a, s1, w1, b, w2 in joined if a == i and s1 == st and w1 + w2 == word]
                        if not m or old[i + 1] != it.get('text2'):
                            skipped += 1
                            continue
                        w1, w2 = m[0]
                        n1 = len(w1) if len(new) == len(word) else min(max(1, round(len(new) * len(w1) / len(word))), len(new) - 1)
                        lines[i] = lines[i][:st] + new[:n1] + lines[i][st + len(w1):]
                        lines[i + 1] = new[n1:] + lines[i + 1][len(w2):]
                    elif lines[i][st:st + len(word)] == word:
                        lines[i] = lines[i][:st] + new + lines[i][st + len(word):]
                    else:
                        skipped += 1
                        continue
                    done += 1
                if lines != old:
                    self.write_page(pg, lines)
                    for i, (a, b) in enumerate(zip(old, lines)):
                        if a != b:
                            self.klog('serie:' + sid, pg, i, a, b)
            self.refresh()
        return dict(id=sid, done=done, skipped=skipped)

    def series_undo(self):
        """Macht die letzte noch nicht zurückgenommene Serie rückgängig (nur Zeilen, die seither unverändert sind)."""
        if not os.path.exists(self.klogpath):
            return dict(id=None)
        rows = [l.rstrip('\n').split('\t') for l in open(self.klogpath, encoding='utf-8')]
        rows = [r for r in rows if len(r) == 6]
        undone = {r[1][5:] for r in rows if r[1].startswith('undo:')}
        ids = [r[1][6:] for r in rows if r[1].startswith('serie:') and r[1][6:] not in undone]
        if not ids:
            return dict(id=None)
        sid = ids[-1]
        done = skipped = 0
        with self.lock:
            self.refresh()
            bypage = {}
            for r in rows:
                if r[1] == 'serie:' + sid:
                    bypage.setdefault(r[2], []).append((int(r[3]) - 1, r[4], r[5]))
            for pg, ch in bypage.items():
                lines = list(self.pages.get(pg, []))
                for i, a, b in ch:
                    if i < len(lines) and lines[i] == b:
                        lines[i] = a
                        self.klog('undo:' + sid, pg, i, b, a)
                        done += 1
                    else:
                        skipped += 1
                if pg in self.pages and lines != self.pages[pg]:
                    self.write_page(pg, lines)
            if not done:
                self.klog('undo:' + sid, '-', -1, '', '')
            self.refresh()
        return dict(id=sid, done=done, skipped=skipped)

    def fnsep(self, pg, i, oldline):
        """Fußnotentrenner '---' vor die angegebene Zeile setzen/verschieben; steht er schon dort, entfernen."""
        with self.lock:
            self.refresh()
            lines = list(self.pages[pg])
            if not (0 <= i < len(lines)) or lines[i] != oldline or lines[i] == '---':
                return None
            had = lines.index('---') if '---' in lines else None
            if had is not None:
                del lines[had]
                if had < i:
                    i -= 1
            if had is None or had != i:
                lines.insert(i, '---')
                act, i = 'gesetzt', i + 1
            else:
                act = 'entfernt'
            self.write_page(pg, lines)
            self.klog('fnsep', pg, i, act, lines[i])
            return dict(line=i, action=act, data=self.page_data(pg))

    def edit(self, pg, edits):
        with self.lock:
            self.refresh()
            lines = list(self.pages[pg])
            for e in edits:
                # nur ändern, wenn die Zeile noch so aussieht wie im Browser (sonst wurde extern editiert)
                if not (0 <= e['line'] < len(lines)) or lines[e['line']] != e['old'] or '\n' in e['new']:
                    return None
            for e in edits:
                lines[e['line']] = e['new']
            self.write_page(pg, lines)
            for e in edits:
                self.klog('edit', pg, e['line'], e['old'], e['new'])
            return self.page_data(pg)

    def whitelist(self):
        with self.lock:
            return open(self.wlpath, encoding='utf-8').read().split() if os.path.exists(self.wlpath) else []


# ---- Bibliothek: Liste der bekannten Buchordner in ~/.fraktur-korrektor/bibliothek.json

def lib_load():
    try:
        l = json.load(open(LIBFILE, encoding='utf-8'))
        return l if isinstance(l, list) else []
    except (OSError, ValueError):
        return []


def lib_touch(folder, title=None):
    """Buch eintragen bzw. als zuletzt geöffnet vormerken; liefert den Eintrag."""
    folder = os.path.abspath(folder)
    with LIBLOCK:
        lib = lib_load()
        e = next((x for x in lib if book_id(x['folder']) == book_id(folder)), None)
        if e is None:
            e = dict(folder=folder, title=title or default_title(folder))
            lib.append(e)
        elif title:
            e['title'] = title
        e['last'] = time.strftime('%Y-%m-%d %H:%M:%S')
        os.makedirs(korrlib.HOME, exist_ok=True)
        write_atomic(LIBFILE, json.dumps(lib, ensure_ascii=False, indent=1))
        return e


def lib_forget(bid):
    with LIBLOCK:
        write_atomic(LIBFILE, json.dumps([x for x in lib_load() if book_id(x['folder']) != bid], ensure_ascii=False, indent=1))
        BOOKS.pop(bid, None)


def lib_list():
    out = []
    for e in lib_load():
        n = len(page_files(e['folder']))
        try:
            bm = json.load(open(os.path.join(e['folder'], 'lesezeichen.json'), encoding='utf-8')).get('page')
        except (OSError, ValueError):
            bm = None
        out.append(dict(id=book_id(e['folder']), title=e.get('title') or default_title(e['folder']), folder=e['folder'],
                        pages=n, bookmark=bm, last=e.get('last', '')))
    out.sort(key=lambda b: b['last'], reverse=True)
    return out


def get_book(bid):
    with LIBLOCK:
        if bid not in BOOKS:
            e = next((x for x in lib_load() if book_id(x['folder']) == bid), None)
            if not e or not page_files(e['folder']):
                return None
            BOOKS[bid] = Book(e['folder'], e.get('title'))
        return BOOKS[bid]


def books_dir():
    return korrlib.config().get('buecher') or os.path.join(os.path.expanduser('~'), 'Fraktur-Korrektor')


def import_transkribus(source, title=None, images=None, target=None):
    if not source or not os.path.exists(source):
        raise ValueError('quelle_fehlt')
    name = re.sub(r'[\\/:*?"<>|]+', ' ', title or os.path.splitext(os.path.basename(source.rstrip('/\\')))[0]).strip() or 'Buch'
    out = target or os.path.join(books_dir(), name)
    n = 1
    while page_files(out):  # vorhandene Bücher nie überschreiben
        n += 1
        out = (target or os.path.join(books_dir(), name)) + ' (%d)' % n
    try:
        r = pagexml.import_export(source, out, images or None)
    except ValueError:
        raise ValueError('keine_xml')
    e = lib_touch(out, title or r.get('title') or name)
    return dict(id=book_id(out), folder=out, title=e['title'], pages=r['pages'], images=r['images'], warnings=r['warnings'])


def dialog(kind):
    """Auswahldialog des Betriebssystems (läuft als eigener Prozess, weil tkinter den Hauptthread braucht)."""
    import tkinter
    from tkinter import filedialog
    root = tkinter.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    p = filedialog.askdirectory(parent=root) if kind == 'folder' else \
        filedialog.askopenfilename(parent=root, filetypes=[('ZIP', '*.zip'), ('*', '*.*')])
    sys.stdout.buffer.write((p or '').encode('utf-8'))


def choose(kind):
    cmd = [sys.executable] + ([] if getattr(sys, 'frozen', False) else [os.path.abspath(__file__)]) + ['--dialog', kind]
    try:
        return subprocess.run(cmd, capture_output=True, timeout=900).stdout.decode('utf-8').strip()
    except (OSError, subprocess.TimeoutExpired):
        return ''


# ---- Hilfe: docs/<sprache>/*.md als HTML

HELP_PAGE = '''<!DOCTYPE html><html lang="%(lang)s"><head><meta charset="utf-8"><title>%(title)s – Fraktur-Korrektor</title><style>
body{margin:0;font-family:Segoe UI,Arial,sans-serif;background:#e9e6df;color:#222;line-height:1.6}
#top{display:flex;gap:16px;align-items:center;padding:8px 16px;background:#2b2b2b;color:#eee;font-size:14px}
#top a{color:#eee} #top .sp{flex:1}
#wrap{display:flex;gap:24px;max-width:1100px;margin:20px auto;padding:0 16px}
nav{flex:none;width:210px;font-size:15px} nav a{display:block;padding:4px 8px;border-radius:3px;color:#234;text-decoration:none}
nav a.cur{background:#fff;font-weight:bold} nav a:hover{background:#f4f2ec}
main{flex:1;min-width:0;background:#fff;border:1px solid #bbb;border-radius:4px;padding:10px 34px 30px}
main img{max-width:100%%} table{border-collapse:collapse} td,th{border:1px solid #ccc;padding:4px 9px;vertical-align:top;text-align:left}
th{background:#f6f3ea} code,kbd{background:#eee;border:1px solid #ccc;border-radius:3px;padding:0 4px;font-family:Consolas,monospace;font-size:.9em}
pre{background:#f4f4f4;padding:10px;overflow:auto} pre code{border:0;padding:0} h1{margin-top:.6em}
</style></head><body><div id="top"><b>Fraktur-Korrektor</b><a href="/">%(home)s</a><span class="sp"></span>%(langs)s</div>
<div id="wrap"><nav>%(nav)s</nav><main>%(body)s</main></div></body></html>'''


def help_pages(lang):
    """[(name, titel)] – index zuerst, Titel ist die erste Überschrift."""
    out = []
    for f in sorted(glob.glob(os.path.join(HERE, 'docs', lang, '*.md'))):
        m = re.search(r'^#\s+(.+)$', open(f, encoding='utf-8').read(), re.M)
        out.append((os.path.basename(f)[:-3], m.group(1).strip() if m else os.path.basename(f)[:-3]))
    out.sort(key=lambda x: (x[0] != 'index', ))
    return out


def help_html(lang, name):
    p = os.path.join(HERE, 'docs', lang, name + '.md')
    if not os.path.exists(p):
        return None
    src = open(p, encoding='utf-8').read()
    try:
        import markdown
        body = markdown.markdown(src, extensions=['tables', 'fenced_code', 'toc'])
        body = re.sub(r'href="(?![a-z]+:|/|#)([^"#]+)\.md(#[^"]*)?"', lambda m: 'href="%s%s"' % (m.group(1), m.group(2) or ''), body)
    except ImportError:
        body = '<p><i>pip install markdown</i></p><pre>' + src.replace('&', '&amp;').replace('<', '&lt;') + '</pre>'
    pages = help_pages(lang)
    nav = ''.join('<a href="/hilfe/%s/%s"%s>%s</a>' % (lang, n, ' class="cur"' if n == name else '', t) for n, t in pages)
    other = 'en' if lang == 'de' else 'de'
    langs = '<a href="/hilfe/%s/%s">%s</a>' % (other, name if os.path.exists(os.path.join(HERE, 'docs', other, name + '.md')) else 'index',
                                               'English' if other == 'en' else 'Deutsch')
    return HELP_PAGE % dict(lang=lang, title=dict(pages).get(name, name), nav=nav, body=body, langs=langs,
                            home='Bibliothek' if lang == 'de' else 'Library')


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, body, ctype='application/json'):
        if isinstance(body, str):
            body = body.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', ctype + ('' if ctype.startswith('image/') else '; charset=utf-8'))
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'max-age=3600' if ctype.startswith('image/') else 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def sendjson(self, obj, code=200):
        self.send(code, json.dumps(obj, ensure_ascii=False))

    def sendfile(self, name, ctype='text/html'):
        self.send(200, open(os.path.join(HERE, name), encoding='utf-8').read(), ctype)

    def redirect(self, url):
        self.send_response(302)
        self.send_header('Location', url)
        self.send_header('Content-Length', '0')
        self.end_headers()

    def local(self):
        """Bibliothek verändern (Ordner öffnen, importieren) darf nur, wer am Rechner selbst sitzt – nicht das LAN."""
        return self.client_address[0] in ('127.0.0.1', '::1', '::ffff:127.0.0.1')

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        if u.path == '/':
            return self.redirect('/buch/' + DEFAULT) if DEFAULT else self.sendfile('bibliothek.html')
        if u.path == '/bibliothek':
            return self.sendfile('bibliothek.html')
        if u.path == '/i18n.js':
            return self.sendfile('i18n.js', 'text/javascript')
        if u.path == '/api/library':
            return self.sendjson(dict(books=lib_list(), local=self.local(), version=version(), donate=DONATE_URL, booksdir=books_dir()))
        if u.path in ('/hilfe', '/hilfe/', '/help'):
            return self.redirect('/hilfe/de/index')
        m = re.fullmatch(r'/hilfe/(de|en)/([\w-]+)', u.path)
        if m:
            h = help_html(*m.groups())
            return self.send(200, h, 'text/html') if h else self.send(404, '{}')
        m = re.fullmatch(r'/hilfe/(de|en)/(img/[\w.-]+\.(png|jpg|jpeg|gif))', u.path)
        if m:
            p = os.path.join(HERE, 'docs', m.group(1), *m.group(2).split('/'))
            if os.path.exists(p):
                return self.send(200, open(p, 'rb').read(), IMGTYPES.get('.' + m.group(3), 'image/gif'))
            return self.send(404, '{}')
        m = re.fullmatch(r'/buch/([0-9a-f]{8})(/.*)?', u.path)
        if not m:
            return self.send(404, '{}')
        book, rest = get_book(m.group(1)), m.group(2) or '/'
        if rest == '/':
            return self.sendfile('reader.html') if book else self.redirect('/bibliothek')
        if not book:
            return self.send(404, '{}')
        if rest.startswith('/img/'):
            p = os.path.join(book.imgdir, os.path.basename(rest))
            ext = os.path.splitext(p)[1].lower()
            if ext in IMGTYPES and os.path.exists(p):
                return self.send(200, open(p, 'rb').read(), IMGTYPES[ext])
            return self.send(404, '{}')
        if rest == '/api/overview':
            r = dict(title=book.title, pages=book.overview())
            korrlib.save_cache()
            return self.sendjson(r)
        if rest == '/api/whitelist':
            return self.sendjson(dict(words=list(dict.fromkeys(book.whitelist()))))
        if rest == '/api/bookmark':
            return self.send(200, open(book.bmpath, encoding='utf-8').read() if os.path.exists(book.bmpath) else '{}')
        if rest == '/api/occurrences':
            w = q.get('word', [''])[0]
            occ = book.occurrences(w) if w else []
            if q.get('count'):
                return self.sendjson(dict(n=len(occ)))
            return self.sendjson(dict(word=w, items=occ, sizes={o['page']: book.img_size(o['page']) for o in occ}))
        if rest == '/api/nextflag':
            after = q.get('after', ['000'])[0]
            for o in book.overview():
                if o['page'] > after and o['n'] > 0:
                    return self.sendjson(dict(page=o['page']))
            return self.sendjson(dict(page=None))
        m = re.fullmatch(r'/api/page/(\d{3})', rest)
        if m:
            try:
                return self.sendjson(book.page_data(m.group(1)))
            except KeyError:
                return self.send(404, '{}')
        self.send(404, '{}')

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        body = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))) or b'{}')
        if u.path in ('/api/choose', '/api/open', '/api/import_transkribus', '/api/forget'):
            if not self.local():
                return self.sendjson(dict(error='nur_lokal'), 403)
            if u.path == '/api/choose':
                return self.sendjson(dict(path=choose('folder' if body.get('kind') == 'folder' else 'zip')))
            if u.path == '/api/forget':
                lib_forget(body.get('id'))
                return self.sendjson({})
            if u.path == '/api/open':
                f = find_book_folder(body.get('folder') or '')
                if not f:
                    return self.sendjson(dict(error='kein_buch'), 400)
                lib_touch(f)
                return self.sendjson(dict(id=book_id(f)))
            try:
                return self.sendjson(import_transkribus(body.get('source'), body.get('title'), body.get('images'), body.get('target')))
            except ValueError as e:
                return self.sendjson(dict(error=str(e)), 400)
        m = re.fullmatch(r'/buch/([0-9a-f]{8})(/api/.*)', u.path)
        book = get_book(m.group(1)) if m else None
        if not book:
            return self.send(404, '{}')
        rest = m.group(2)
        m = re.fullmatch(r'/api/edit/(\d{3})', rest)
        if m:
            r = book.edit(m.group(1), body['edits'])
            return self.sendjson(r) if r else self.send(409, '{}')
        m = re.fullmatch(r'/api/fnsep/(\d{3})', rest)
        if m:
            r = book.fnsep(m.group(1), body['line'], body['old'])
            return self.sendjson(r) if r else self.send(409, '{}')
        if rest == '/api/series':
            if not body.get('word') or not body.get('new') or re.search(r'\s', body['new']):
                return self.send(400, '{}')
            return self.sendjson(book.series_replace(body['word'], body['new'], body.get('items', [])))
        if rest == '/api/series_undo':
            return self.sendjson(book.series_undo())
        if rest == '/api/whitelist_remove':
            with book.lock:
                write_atomic(book.wlpath, ''.join(w + '\n' for w in book.whitelist() if w != body['word']))
                book.klog('whitelist-', '-', -1, body['word'], '')
            return self.send(200, '{}')
        if rest == '/api/whitelist':
            with book.lock:
                with open(book.wlpath, 'a', encoding='utf-8') as f:
                    f.write(body['word'] + '\n')
                book.klog('whitelist+', '-', -1, body['word'], '')
            return self.send(200, '{}')
        if rest == '/api/bookmark':
            with book.lock:
                write_atomic(book.bmpath, json.dumps(dict(page=body.get('page'), line=body.get('line'))))
            lib_touch(book.folder)
            return self.send(200, '{}')
        self.send(404, '{}')


class Server(ThreadingHTTPServer):
    allow_reuse_address = os.name != 'nt'  # unter Windows ließe SO_REUSEADDR mehrere Server auf demselben Port zu

    def server_bind(self):
        # HTTPServer.server_bind fragt mit socket.getfqdn() den Rechnernamen ab – auf dem Mac dauert das bis zu 30 s
        socketserver.TCPServer.server_bind(self)
        self.server_name, self.server_port = self.server_address[:2]


def main():
    global DEFAULT
    ap = argparse.ArgumentParser()
    ap.add_argument('folder', nargs='?', help='Buchordner; ohne Angabe erscheint die Bibliothek')
    ap.add_argument('--port', type=int, default=8765)
    ap.add_argument('--dic')
    ap.add_argument('--title')
    ap.add_argument('--no-browser', action='store_true')
    ap.add_argument('--lan', action='store_true', help='auch für andere Rechner im lokalen Netz erreichbar (kein Passwortschutz!)')
    A = ap.parse_args()
    if A.dic:
        korrlib.set_dic(A.dic)
    try:
        httpd = Server(('0.0.0.0' if A.lan else '127.0.0.1', A.port), H)
    except OSError:
        sys.exit('Port %d ist belegt – läuft der Fraktur-Korrektor schon? Sonst mit --port <nummer> einen anderen Port wählen.' % A.port)
    if A.folder:
        f = find_book_folder(A.folder)
        if not f:
            sys.exit('Kein Buchordner: in %s liegen keine Seitendateien (001.txt, 002.txt, …).' % os.path.abspath(A.folder))
        lib_touch(f, A.title)
        DEFAULT = book_id(f)
        print('Lade Wörterbuch und Seiten …')
        get_book(DEFAULT).overview()
        korrlib.save_cache()
    url = 'http://localhost:%d' % A.port
    print('Fraktur-Korrektor: %s  (Strg+C beendet)' % url)
    if A.lan:
        import socket
        try:
            so = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); so.connect(('10.255.255.255', 1)); ip = so.getsockname()[0]; so.close()
        except OSError:
            ip = socket.gethostname()
        print('Im lokalen Netz:   http://%s:%d   oder   http://%s:%d' % (ip, A.port, socket.gethostname(), A.port))
        print('Achtung: ohne Passwort - jeder im selben Netz kann lesen und korrigieren. Nur im eigenen Heimnetz verwenden.')
    if not A.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--dialog':
        dialog(sys.argv[2])
    else:
        main()
