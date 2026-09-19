"""EPUB lesen. Ein EPUB kennt weder Seiten noch Zeilen; deshalb zwei Wege:
- text_book: reines Textbuch ohne Seitenbilder (Absätze umbrochen, feste Zeilenzahl je "Seite")
- transplant: Es gibt ein gleichlautendes PDF. Aus dem PDF kommt der Buchordner mit Seitenbildern und Zeilengeometrie
  (ocr.build); der Wortlaut jeder Zeile wird dann durch den des EPUB ersetzt (Wortfolgen abgleichen). So steht links
  der Scan und rechts der bereits bearbeitete Text des EPUB."""
import os, re, json, glob, zipfile, difflib, posixpath, textwrap, urllib.parse
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

BLOCK = {'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'blockquote', 'tr', 'br', 'hr', 'section', 'dt', 'dd', 'pre', 'figcaption'}
SKIP = {'script', 'style', 'head', 'svg', 'nav'}
NORM = re.compile(r'[^0-9a-zäöüß]+')
JUNK = re.compile(r'[|\_{}~^]+')  # Reste mitgescannter Seitenränder – nie echter Text


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.paras, self.buf, self.skip = [], [], 0

    def flush(self):
        t = re.sub(r'\s+', ' ', ''.join(self.buf)).strip()
        if t:
            self.paras.append(t)
        self.buf = []

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip += 1
        elif tag in BLOCK:
            self.flush()

    def handle_endtag(self, tag):
        if tag in SKIP:
            self.skip = max(0, self.skip - 1)
        elif tag in BLOCK:
            self.flush()

    def handle_data(self, data):
        if not self.skip:
            self.buf.append(data)


def read(path):
    """(titel, [kapitel]); kapitel = Liste von Absätzen, in Lesereihenfolge (spine)."""
    with zipfile.ZipFile(path) as z:
        opf = ET.fromstring(z.read('META-INF/container.xml')).find('.//{*}rootfile').get('full-path')
        root = ET.fromstring(z.read(opf))
        t = root.find('.//{http://purl.org/dc/elements/1.1/}title')
        items = {i.get('id'): i.get('href') for i in root.findall('.//{*}item')}
        chapters = []
        for ref in root.findall('.//{*}itemref'):
            href = items.get(ref.get('idref'))
            if not href:
                continue
            name = posixpath.normpath(posixpath.join(posixpath.dirname(opf), urllib.parse.unquote(href.split('#')[0])))
            try:
                p = _Text()
                p.feed(z.read(name).decode('utf-8', 'replace'))
                p.flush()
            except KeyError:
                continue
            if p.paras:
                chapters.append(p.paras)
        return (t.text or '').strip() if t is not None and t.text else None, chapters


def text_book(path, out, width=68, per_page=34):
    """EPUB ohne PDF: Textbuch ohne Seitenbilder. Jedes Kapitel beginnt eine neue Seite. Liefert dict(pages, title)."""
    title, chapters = read(path)
    if not chapters:
        raise ValueError('keine_seiten')
    if glob.glob(os.path.join(out, '[0-9][0-9][0-9].txt')):
        raise FileExistsError(out)
    pages = []
    for paras in chapters:
        lines = []
        for p in paras:
            lines += textwrap.wrap(p, width) + ['']
        for k in range(0, len(lines), per_page):
            pages.append(lines[k:k + per_page])
    if len(pages) > 999:
        raise ValueError('zu_viele_seiten')
    os.makedirs(out, exist_ok=True)
    for n, lines in enumerate(pages, 1):
        while lines and not lines[-1]:
            lines.pop()
        with open(os.path.join(out, '%03d.txt' % n), 'w', encoding='utf-8') as f:
            f.write('\n'.join(['# '] + lines) + '\n')
    return dict(pages=len(pages), title=title)


def norm(w):
    return NORM.sub('', w.lower().replace('ſ', 's'))


def transplant(path, book, progress=lambda done, total, msg: None):
    """Ersetzt im Buchordner book (aus dem PDF gebaut) den Wortlaut der Zeilen durch den des EPUB.
    Zeilen, zu denen das EPUB nichts Passendes hat (Kopfzeilen, Fußnoten, die im EPUB anderswo stehen), behalten
    ihren Text aus dem PDF. Liefert dict(title, matched = Anteil der Zeilen mit EPUB-Text)."""
    title, chapters = read(path)
    E = [w for paras in chapters for p in paras for w in p.split() if not JUNK.fullmatch(w)]
    En = [norm(w) for w in E]
    if not E:
        raise ValueError('keine_seiten')
    # Wo steht eine Seite im EPUB? Vier-Wort-Folgen, die im EPUB genau einmal vorkommen, sind verlässliche Wegmarken –
    # unabhängig von der Reihenfolge (Vorspann, Anhang und Anmerkungen stehen im EPUB oft woanders als im Buch).
    marks = {}
    for i in range(len(En) - 3):
        key = tuple(En[i:i + 4])
        if all(key):
            marks[key] = i if key not in marks else -1
    files = sorted(glob.glob(os.path.join(book, '[0-9][0-9][0-9].txt')))
    pos, taken, total_lines = 0, 0, 0
    for k, f in enumerate(files):
        lines = open(f, encoding='utf-8').read().split('\n')
        if lines and lines[-1] == '':
            lines.pop()
        # Wörter der Seite; ein über das Zeilenende getrenntes Wort (Zu¬ / kunft) ist EIN Wort, das zu zwei Zeilen gehört
        toks = []  # [normiert, zeile, zeile2 oder None, länge des ersten Teils]
        for i, l in enumerate(lines):
            if l.startswith('#') or l == '---':
                continue
            for w in l.split():
                if toks and toks[-1][2] == -1:       # Fortsetzung eines getrennten Wortes
                    toks[-1][0] += norm(w); toks[-1][2] = i
                elif w.endswith('¬') and len(w) > 1:
                    toks.append([norm(w[:-1]), i, -1, len(w) - 1])
                else:
                    toks.append([norm(w), i, None, 0])
        for t in toks:
            if t[2] == -1:
                t[2] = None
        body = [t for t in toks if t[0]]
        if len(body) >= 5:
            bn = [t[0] for t in body]
            votes = sorted(marks[k] - i for i in range(len(bn) - 3) for k in [tuple(bn[i:i + 4])] if marks.get(k, -1) >= 0)
            if len(votes) >= 3:
                pos = max(0, votes[len(votes) // 2])  # Median: einzelne Irrläufer stören nicht
                lo, hi = max(0, pos - len(body) // 2 - 50), pos + 2 * len(body) + 50
            else:
                lo, hi = max(0, pos - 200), pos + 3 * len(body) + 1500
            win = En[lo:hi]
            sm = difflib.SequenceMatcher(None, bn, win, autojunk=False)
            blocks = [b for b in sm.get_matching_blocks() if b.size]
            hit = sum(b.size for b in blocks)
            if hit >= 0.4 * len(body):
                # je Zeile: erstes und letztes zugeordnetes EPUB-Wort; dazwischen gilt der EPUB-Wortlaut
                m = {b.a + d: lo + b.b + d for b in blocks for d in range(b.size)}  # Seitenwort -> EPUB-Wort
                split = {m[a]: (body[a][1], body[a][3]) for a in m if body[a][2] is not None}
                on = {}  # zeile -> Seitenwörter (ein getrenntes Wort zählt in beiden Zeilen)
                for a, t in enumerate(body):
                    for ln in ([t[1]] if t[2] is None else [t[1], t[2]]):
                        on.setdefault(ln, []).append(a)
                span = {}
                for ln, idx in on.items():
                    hits = [a for a in idx if a in m]
                    if len(hits) * 2 < len(idx) or m[hits[-1]] - m[hits[0]] > 2 * len(idx) + 3:
                        continue  # zu wenig Übereinstimmung bzw. Ausreißer: PDF-Text behalten
                    # head/tail: Seitenwörter vor dem ersten bzw. nach dem letzten Treffer – so viele EPUB-Wörter aus der
                    # Lücke zur Nachbarzeile gehören noch hierher (das EPUB schreibt dort etwas anderes als das PDF)
                    span[ln] = [m[hits[0]], m[hits[-1]], idx.index(hits[0]), len(idx) - 1 - idx.index(hits[-1])]
                order = sorted(span)
                for u, v in zip(order, order[1:]):
                    gap = span[v][0] - span[u][1] - 1
                    if v == u + 1 and 0 < gap <= span[u][3] + span[v][2] + 2:  # Nachbarzeilen: Lückenwörter aufteilen, nichts verlieren
                        take = min(gap, max(span[u][3], gap - span[v][2]))
                        span[u][1] += take; span[v][0] -= gap - take
                new = list(lines)
                for ln, (e0, e1, _, _) in span.items():
                    ws = []
                    for e in range(e0, e1 + 1):
                        w = E[e]
                        if e in split:  # getrenntes Wort: am Zeilenende der erste Teil mit ¬, in der Folgezeile der Rest
                            sl, n1 = split[e]
                            cut = _cut(w, n1)
                            w = w[:cut] + '¬' if sl == ln else w[cut:]
                        ws.append(w)
                    new[ln] = ' '.join(ws)
                    taken += 1
                if new != lines:
                    with open(f, 'w', encoding='utf-8') as o:
                        o.write('\n'.join(new) + '\n')
                pos = lo + blocks[-1].b + blocks[-1].size
        total_lines += sum(1 for l in lines if l.strip() and not l.startswith('#') and l != '---')
        progress(k + 1, len(files), 'epub')
    matched = round(taken / total_lines, 3) if total_lines else 0.0
    q = os.path.join(book, 'qualitaet.json')
    try:
        d = json.load(open(q, encoding='utf-8'))
        d['epub'] = dict(file=os.path.basename(path), matched=matched)
        json.dump(d, open(q, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    except (OSError, ValueError):
        pass
    return dict(title=title, matched=matched)


def _cut(word, n1):
    """Trennstelle im EPUB-Wort: so viele Buchstaben wie im ersten Teil des PDF-Wortes (Satzzeichen davor zählen nicht)."""
    lead = len(word) - len(word.lstrip('„“"»«(‚\'['))
    return max(1, min(len(word) - 1, lead + n1))
