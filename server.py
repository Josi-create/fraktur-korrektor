"""Fraktur-Korrektor: Lesen und Korrigieren von OCR-Text neben dem Seitenbild.
py -3.14 server.py <buchordner> [--port 8765] [--dic <hunspell-pfad>] [--no-browser]

Buchordner: NNN.txt (eine Datei je Seite), lines.json (Zeilengeometrie), img/NNN.png,
optional autokorr.log, whitelist.txt; lesezeichen.json wird angelegt."""
import sys, os, json, re, glob, threading, urllib.parse, webbrowser, argparse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import korrlib
from korrlib import read_page, corpus_freq, joined_tokens, known

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
                write_atomic(os.path.join(FOLDER, pg + '.txt'), '\n'.join(lines) + '\n')
                return self.send(200, json.dumps(page_data(pg), ensure_ascii=False))
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
