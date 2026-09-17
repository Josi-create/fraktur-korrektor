"""Fraktur-Korrektor: Lesen und Korrigieren von OCR-Text neben dem Seitenbild.
py -3.14 server.py <buchordner> [--port 8765] [--dic <hunspell-pfad>] [--no-browser]

Buchordner: NNN.txt (eine Datei je Seite), lines.json (Zeilengeometrie), img/NNN.png,
optional autokorr.log, whitelist.txt; lesezeichen.json wird angelegt."""
import sys, os, json, re, glob, time, threading, urllib.parse, webbrowser, argparse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import korrlib
from korrlib import read_page, corpus_freq, joined_tokens, in_dict

ap = argparse.ArgumentParser()
ap.add_argument('folder')
ap.add_argument('--port', type=int, default=8765)
ap.add_argument('--dic')
ap.add_argument('--title')
ap.add_argument('--no-browser', action='store_true')
A = ap.parse_args()
if A.dic:
    korrlib.set_dic(A.dic)
FOLDER = A.folder
IMG = os.path.join(FOLDER, 'img')
WL = os.path.join(FOLDER, 'whitelist.txt')
BM = os.path.join(FOLDER, 'lesezeichen.json')
KLOG = os.path.join(FOLDER, 'korrekturen.log')
_t = os.path.abspath(FOLDER)
while os.path.basename(_t).lower() in ('korr', 'ocr'):
    _t = os.path.dirname(_t)
TITLE = A.title or os.path.basename(_t)
HERE = os.path.dirname(os.path.abspath(__file__))
LOCK = threading.RLock()
GEO = json.load(open(os.path.join(FOLDER, 'lines.json'), encoding='utf-8'))


def autokorr_unsicher():
    out = {}
    p = os.path.join(FOLDER, 'autokorr.log')
    if os.path.exists(p):
        for l in open(p, encoding='utf-8'):
            f = l.rstrip('\n').split('\t')
            if len(f) == 5 and f[4] == 'unsicher':
                out.setdefault(f[0], []).append((int(f[1]) - 1, f[3].replace('¬', '')))
    return out


UNSICHER = autokorr_unsicher()


def known(w, freq):
    """Wörterbuch, oder häufig im Buch (Namen) – kurze Wörter schützt die Häufigkeit nicht (ber, bie, baß …)."""
    return in_dict(w) or (len(w) > 4 and freq.get(w, 0) >= 3)


def klog(kind, pg, line, old, new):
    """Korrekturprotokoll: Zeit, Art (edit | serie:ID | undo:ID), Seite, Zeile (1-basiert), alte Zeile, neue Zeile."""
    with open(KLOG, 'a', encoding='utf-8') as f:
        f.write('\t'.join([time.strftime('%Y-%m-%d %H:%M:%S'), kind, pg, str(line + 1), old, new]) + '\n')


def write_page(pg, lines):
    write_atomic(os.path.join(FOLDER, pg + '.txt'), '\n'.join(lines) + '\n')


def write_atomic(path, text):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(text)
    os.replace(tmp, path)


class Book:
    """Seiten im Speicher; Dateien werden bei geänderter mtime neu gelesen (paralleles Editieren erlaubt)."""

    def __init__(self):
        self.pages, self.mt, self.freq, self.wl, self.wlmt, self.fcache = {}, {}, {}, set(), None, {}

    def refresh(self):
        changed = False
        seen = set()
        for f in sorted(glob.glob(os.path.join(FOLDER, '[0-9][0-9][0-9].txt'))):
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
        wlmt = os.path.getmtime(WL) if os.path.exists(WL) else None
        if wlmt != self.wlmt:
            self.wl = set(open(WL, encoding='utf-8').read().split()) if wlmt else set()
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
        for i, cand in UNSICHER.get(pg, []):
            if i < len(toks) and cand not in wl:
                for s, w in toks[i]:
                    if w == cand and (i, s) not in have:
                        out.append(dict(line=i, start=s, len=len(w), word=w, kind='auto'))
        out.sort(key=lambda f: (f['line'], f['start']))
        self.fcache[pg] = (key, out)
        return out


BOOK = Book()
SIZE = {}


def img_size(pg):
    """PNG-Breite/Höhe aus dem IHDR lesen."""
    if pg not in SIZE:
        try:
            with open(os.path.join(IMG, pg + '.png'), 'rb') as f:
                b = f.read(24)
            SIZE[pg] = (int.from_bytes(b[16:20], 'big'), int.from_bytes(b[20:24], 'big'))
        except OSError:
            SIZE[pg] = None
    return SIZE[pg]


def geo_lines(pg, lines):
    """Ordnet den Textzeilen die XML-Zeilen zu; None wenn die Anzahl nicht passt.
    Transkribus legt die Seite höhenfüllend und horizontal zentriert auf sein Format (g['w'] x g['h'])."""
    g = GEO.get(pg)
    sz = img_size(pg)
    if not g or not sz or not g['lines']:
        return None
    L = g['lines']
    head = [l for l in L if l['kind'] == 'head']
    body = [l for l in L if l['kind'] == 'body']
    fn = [l for l in L if l['kind'] == 'fn']
    seq = ([head[0] if head else None] if lines and lines[0].startswith('#') else []) + body + ([None] if '---' in lines else []) + fn
    while len(seq) > len(lines) and seq[-1] is not None and seq[-1]['text'].strip() == '':
        seq.pop()
    if len(seq) != len(lines):
        return None
    w, h = sz
    s = h / g['h']
    ox = (w - g['w'] * s) / 2
    return [None if l is None else dict(x0=l['x0'] * s + ox, x1=l['x1'] * s + ox, y0=l['y0'] * s, y1=l['y1'] * s) for l in seq]


def page_data(pg):
    with LOCK:
        BOOK.refresh()
        lines = BOOK.pages[pg]
        return dict(page=pg, lines=lines, geo=geo_lines(pg, lines), flags=BOOK.flags(pg), img='/img/%s.png' % pg)


def overview():
    with LOCK:
        BOOK.refresh()
        return [dict(page=pg, n=len(BOOK.flags(pg))) for pg in BOOK.pages]


def occurrences(word, limit=500):
    """Alle Vorkommen eines Wortes im Buch (auch über Zeilentrennung ¬ hinweg), mit Zeilengeometrie."""
    out = []
    with LOCK:
        BOOK.refresh()
        for pg, lines in BOOK.pages.items():
            toks, joined = joined_tokens(lines)
            frag = {(i, s1) for i, s1, w1, j, w2 in joined} | {(j, 0) for i, s1, w1, j, w2 in joined}
            hits = [(i, s1, len(w1), True) for i, s1, w1, j, w2 in joined if w1 + w2 == word]
            hits += [(i, s, len(w), False) for i, tl in enumerate(toks) if not lines[i].startswith('#')
                     for s, w in tl if w == word and (i, s) not in frag]
            if not hits:
                continue
            geo = geo_lines(pg, lines)
            for i, s, n, join in sorted(hits):
                out.append(dict(page=pg, line=i, start=s, len=n, join=join, text=lines[i],
                                text2=lines[i + 1] if join else None, geo=geo[i] if geo else None,
                                geo2=geo[i + 1] if geo and join else None, img='/img/%s.png' % pg))
                if len(out) >= limit:
                    return out
    return out


def series_replace(word, new, items):
    """Ersetzt word durch new an den angegebenen Stellen; nur wenn die Zeilen noch unverändert sind."""
    sid = time.strftime('%Y%m%d-%H%M%S')
    done = skipped = 0
    with LOCK:
        BOOK.refresh()
        bypage = {}
        for it in items:
            bypage.setdefault(it['page'], []).append(it)
        for pg, its in bypage.items():
            if pg not in BOOK.pages:
                skipped += len(its)
                continue
            old = BOOK.pages[pg]
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
                write_page(pg, lines)
                for i, (a, b) in enumerate(zip(old, lines)):
                    if a != b:
                        klog('serie:' + sid, pg, i, a, b)
        BOOK.refresh()
    return dict(id=sid, done=done, skipped=skipped)


def series_undo():
    """Macht die letzte noch nicht zurückgenommene Serie rückgängig (nur Zeilen, die seither unverändert sind)."""
    if not os.path.exists(KLOG):
        return dict(id=None)
    rows = [l.rstrip('\n').split('\t') for l in open(KLOG, encoding='utf-8')]
    rows = [r for r in rows if len(r) == 6]
    undone = {r[1][5:] for r in rows if r[1].startswith('undo:')}
    ids = [r[1][6:] for r in rows if r[1].startswith('serie:') and r[1][6:] not in undone]
    if not ids:
        return dict(id=None)
    sid = ids[-1]
    done = skipped = 0
    with LOCK:
        BOOK.refresh()
        bypage = {}
        for r in rows:
            if r[1] == 'serie:' + sid:
                bypage.setdefault(r[2], []).append((int(r[3]) - 1, r[4], r[5]))
        for pg, ch in bypage.items():
            lines = list(BOOK.pages.get(pg, []))
            for i, a, b in ch:
                if i < len(lines) and lines[i] == b:
                    lines[i] = a
                    klog('undo:' + sid, pg, i, b, a)
                    done += 1
                else:
                    skipped += 1
            if pg in BOOK.pages and lines != BOOK.pages[pg]:
                write_page(pg, lines)
        if not done:
            klog('undo:' + sid, '-', -1, '', '')
        BOOK.refresh()
    return dict(id=sid, done=done, skipped=skipped)


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, body, ctype='application/json'):
        if isinstance(body, str):
            body = body.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', ctype + ('; charset=utf-8' if ctype != 'image/png' else ''))
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'max-age=3600' if ctype == 'image/png' else 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        if u.path == '/':
            return self.send(200, open(os.path.join(HERE, 'reader.html'), encoding='utf-8').read(), 'text/html')
        if u.path.startswith('/img/'):
            p = os.path.join(IMG, os.path.basename(u.path))
            if os.path.exists(p):
                return self.send(200, open(p, 'rb').read(), 'image/png')
            return self.send(404, '{}')
        if u.path == '/api/overview':
            return self.send(200, json.dumps(dict(title=TITLE, pages=overview())))
        if u.path == '/api/bookmark':
            return self.send(200, open(BM, encoding='utf-8').read() if os.path.exists(BM) else '{}')
        if u.path == '/api/occurrences':
            w = q.get('word', [''])[0]
            occ = occurrences(w) if w else []
            if q.get('count'):
                return self.send(200, json.dumps(dict(n=len(occ))))
            return self.send(200, json.dumps(dict(word=w, items=occ, sizes={o['page']: img_size(o['page']) for o in occ}), ensure_ascii=False))
        if u.path == '/api/nextflag':
            after = q.get('after', ['000'])[0]
            for o in overview():
                if o['page'] > after and o['n'] > 0:
                    return self.send(200, json.dumps(dict(page=o['page'])))
            return self.send(200, json.dumps(dict(page=None)))
        m = re.fullmatch(r'/api/page/(\d{3})', u.path)
        if m:
            try:
                return self.send(200, json.dumps(page_data(m.group(1)), ensure_ascii=False))
            except KeyError:
                return self.send(404, '{}')
        self.send(404, '{}')

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        body = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))) or b'{}')
        m = re.fullmatch(r'/api/edit/(\d{3})', u.path)
        if m:
            pg = m.group(1)
            with LOCK:
                BOOK.refresh()
                lines = list(BOOK.pages[pg])
                for e in body['edits']:
                    # nur ändern, wenn die Zeile noch so aussieht wie im Browser (sonst wurde extern editiert)
                    if not (0 <= e['line'] < len(lines)) or lines[e['line']] != e['old'] or '\n' in e['new']:
                        return self.send(409, '{}')
                for e in body['edits']:
                    lines[e['line']] = e['new']
                write_page(pg, lines)
                for e in body['edits']:
                    klog('edit', pg, e['line'], e['old'], e['new'])
                return self.send(200, json.dumps(page_data(pg), ensure_ascii=False))
        if u.path == '/api/series':
            if not body.get('word') or not body.get('new') or re.search(r'\s', body['new']):
                return self.send(400, '{}')
            return self.send(200, json.dumps(series_replace(body['word'], body['new'], body.get('items', []))))
        if u.path == '/api/series_undo':
            return self.send(200, json.dumps(series_undo()))
        if u.path == '/api/whitelist':
            with LOCK:
                with open(WL, 'a', encoding='utf-8') as f:
                    f.write(body['word'] + '\n')
            return self.send(200, '{}')
        if u.path == '/api/bookmark':
            with LOCK:
                write_atomic(BM, json.dumps(dict(page=body.get('page'), line=body.get('line'))))
            return self.send(200, '{}')
        self.send(404, '{}')


if __name__ == '__main__':
    print('Lade Wörterbuch und Seiten …')
    overview()
    url = 'http://localhost:%d' % A.port
    print('Fraktur-Korrektor: %s  (Strg+C beendet)' % url)
    if not A.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    ThreadingHTTPServer(('127.0.0.1', A.port), H).serve_forever()
