"""EPUB lesen. Ein EPUB kennt weder Seiten noch Zeilen; deshalb zwei Wege:
- text_book: reines Textbuch ohne Seitenbilder (Absätze umbrochen, feste Zeilenzahl je "Seite")
- transplant: Es gibt ein gleichlautendes PDF. Aus dem PDF kommt der Buchordner mit Seitenbildern und Zeilengeometrie
  (ocr.build); der Wortlaut jeder Zeile wird dann durch den des EPUB ersetzt (Wortfolgen abgleichen). So steht links
  der Scan und rechts der bereits bearbeitete Text des EPUB.

Auf beiden Wegen kommt die Auszeichnung des EPUB mit (#81): Überschriften, Absatzanfänge, Tabellen und die Schrift
(fett, kursiv, hoch- und tiefgestellt – auch wo das EPUB sie über seine Stilvorlage setzt). Sie wird so geschrieben, wie
das Programm sie selbst setzt (korrlib.MARKUP): zeilenweise, jede Zeile schließt, was sie öffnet."""
import os, re, json, glob, zipfile, difflib, posixpath, urllib.parse
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

BLOCK = {'p', 'div', 'li', 'blockquote', 'hr', 'section', 'article', 'aside', 'dt', 'dd', 'pre', 'figcaption', 'ol', 'ul', 'dl', 'figure'}
SKIP = {'script', 'style', 'head', 'svg', 'nav'}
VOID = {'br', 'hr', 'img', 'meta', 'link', 'input', 'wbr', 'col', 'area', 'base', 'source', 'image'}
HEAD = re.compile(r'h([1-6])$')
# Schrift-Auszeichnung, außen nach innen – in dieser Reihenfolge werden die Elemente verschachtelt
INLINE = ('strong', 'b', 'em', 'i', 'sup', 'sub')
OWN = {'strong': 'strong', 'b': 'b', 'em': 'em', 'i': 'i', 'cite': 'i', 'sup': 'sup', 'sub': 'sub'}
BOLD = {'strong', 'b'}  # in Überschriften und Tabellenköpfen ohnehin fett – dort nicht noch einmal
INVISIBLE = re.compile('[\xad​‌‍⁠﻿]')  # weiche Trennstriche, Breite null: im Text nur Stolpersteine
NORM = re.compile(r'[^0-9a-zäöüß]+')
JUNK = re.compile(r'[|\_{}~^]+')  # Reste mitgescannter Seitenränder – nie echter Text
PARA_END = re.compile(r'[.!?:;»«"“”‘’)\]—…]\s*$')  # wie server.Book.PARA_END, dazu die einfachen Anführungszeichen
LOWER = re.compile(r'[a-zäöüßſ]{2}')
# Darunter gehört ein PDF nicht zu diesem Text: Anteil der Vier-Wort-Folgen aus der Stichprobe (pdf_fit) bzw. der Zeilen,
# die nach dem Zuordnen den Wortlaut tragen (transplant). Lieber abbrechen als Scan und fremden Text nebeneinanderlegen.
MINFIT, MINMATCH = 0.1, 0.05


# ---- Stilvorlagen: Viele EPUBs setzen fett und kursiv nicht mit <b>/<i>, sondern über Klassen (<p class="bibhead">,
# <td class="w">). Verstanden werden einfache Regeln – Element, Klasse, beides; bei »table.gloss td.w« zählt td.w.
def _decl(text):
    """Die Schrift-Auszeichnung einer CSS-Deklaration als Menge (b, i, sup, sub)."""
    out = set()
    for prop, val in re.findall(r'([\w-]+)\s*:\s*([^;]+)', text or ''):
        prop, val = prop.lower(), val.lower()
        if prop == 'font-weight' and re.search(r'bold|[6-9]00', val):
            out.add('b')
        elif prop == 'font-style' and re.search(r'italic|oblique', val):
            out.add('i')
        elif prop == 'vertical-align' and val.strip() in ('super', 'sub'):
            out.add(val.strip()[:3])
        elif prop == 'font' and re.search(r'\b(?:bold|[6-9]00)\b', val):
            out.add('b')
    return out


def css_rules(text):
    """[(element oder None, {klassen}, {stile})] aus einer Stilvorlage."""
    rules = []
    for sel, decl in re.findall(r'([^{}@]+)\{([^}]*)\}', re.sub(r'/\*.*?\*/', '', text, flags=re.S)):
        st = _decl(decl)
        if not st:
            continue
        for s in sel.split(','):
            last = re.split(r'[\s>+~]+', s.strip())[-1]
            m = re.fullmatch(r'([a-zA-Z][\w-]*)?((?:\.[\w-]+)*)', last)
            if m and (m.group(1) or m.group(2)):
                rules.append((m.group(1).lower() if m.group(1) else None, set(m.group(2).split('.')[1:]), st))
    return rules


class _Blocks(HTMLParser):
    """Eine XHTML-Datei des EPUB als Blöcke: dict(kind='p'|'h', level, segs) – segs sind die durch <br/> getrennten
    Zeilen, jede eine Folge von Stücken (text, stile) – oder dict(kind='table', rows=[[(td|th, stücke)]])."""

    def __init__(self, css):
        super().__init__(convert_charrefs=True)
        self.css, self.blocks, self.stack = css, [], []  # stack: offene Elemente (tag, eigene stile)
        self.runs, self.segs = [], []                    # der offene Block
        self.skip, self.pb, self.pre = 0, None, 0
        self.table, self.cell, self.nested = None, None, 0

    def styles(self, tag, a):
        st = {OWN[tag]} if tag in OWN else set()
        cls = set((a.get('class') or '').split())
        for t, cs, s in self.css:
            if (t is None or t == tag) and cs <= cls:
                st |= s
        return st | _decl(a.get('style'))

    def current(self):
        st = set().union(*(s for _, s in self.stack))
        if any(HEAD.match(t) or t == 'th' for t, _ in self.stack):
            st -= BOLD
        return tuple(x for x in INLINE if x in st)

    def level(self):
        return next((int(t[1]) for t, _ in reversed(self.stack) if HEAD.match(t)), 0)

    def text(self, s):
        if self.cell is not None:
            self.cell[1].append((s, self.current()))
        elif self.table is None:
            self.runs.append((s, self.current()))

    def newline(self):
        if self.cell is not None or self.table is not None:
            self.text(' ')  # eine Zelle ist eine Zeile
        else:
            self.segs.append(self.runs)
            self.runs = []

    def flush(self):
        segs = [s for s in self.segs + [self.runs] if _words(s)]
        if segs:
            lv = self.level()
            self.blocks.append(dict(kind='h' if lv else 'p', level=lv, segs=segs))
        self.runs, self.segs = [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in VOID:
            if self.skip:
                pass
            elif tag == 'br':
                self.newline()
            elif tag == 'hr' and self.table is None:
                self.flush()
            return
        if self.pb is None and ('pagebreak' in (a.get('epub:type') or '').split() or a.get('role') == 'doc-pagebreak'):
            self.pb = tag  # Seitenmarke der Druckausgabe (»[12]« in einem E-Book dieses Programms, #59): kein Text des Buchs
            self.skip += 1
            return
        if tag in SKIP:
            self.skip += 1
            return
        if self.skip:
            return
        if tag == 'table':
            if self.table is not None:
                self.nested += 1
                self.text(' ')
            else:
                self.flush()
                self.table = []
        elif tag == 'tr' and self.table is not None and not self.nested:
            self.table.append([])
            self.cell = None
        elif tag in ('td', 'th') and self.table is not None and not self.nested:
            if not self.table:
                self.table.append([])
            self.cell = [tag, []]
            self.table[-1].append(self.cell)
            span = a.get('colspan') or ''
            for _ in range(min(20, int(span) - 1) if span.isdigit() else 0):  # verbundene Zellen: das Gitter bleibt gerade
                self.table[-1].append(['td', []])
        elif (tag in BLOCK or HEAD.match(tag)) and self.table is not None:
            self.text(' ')
        elif tag in BLOCK or HEAD.match(tag):
            self.flush()
        if tag == 'pre':
            self.pre += 1
        self.stack.append((tag, self.styles(tag, a)))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == self.pb:
            self.pb = None
            self.skip = max(0, self.skip - 1)
            return
        if tag in SKIP:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip or tag in VOID:
            return
        if tag == 'table' and self.nested:
            self.nested -= 1
        elif tag == 'table' and self.table is not None:
            rows = [r for r in self.table if r]
            if rows:
                n = max(len(r) for r in rows)
                for r in rows:
                    r += [['td', []] for _ in range(n - len(r))]
                self.blocks.append(dict(kind='table', rows=[[(c[0], c[1]) for c in r] for r in rows]))
            self.table = self.cell = None
        elif tag in ('td', 'th') and not self.nested:
            self.cell = None
        elif (tag in BLOCK or HEAD.match(tag)) and self.table is not None:
            self.text(' ')
        elif tag in BLOCK or HEAD.match(tag):
            self.flush()  # vor dem Schließen: die Ebene der Überschrift gilt noch
        if tag == 'pre':
            self.pre = max(0, self.pre - 1)
        for k in range(len(self.stack) - 1, -1, -1):  # auch bei fehlerhaft verschachteltem HTML: bis zum passenden Element
            if self.stack[k][0] == tag:
                del self.stack[k:]
                break

    def handle_data(self, data):
        if self.skip:
            return
        data = INVISIBLE.sub('', data)
        if self.pre:
            for k, part in enumerate(data.split('\n')):
                if k:
                    self.newline()
                self.text(part)
        else:
            self.text(data)


def _words(runs):
    """Stücke (text, stile) → Wörter; ein Wort ist eine Liste von Stücken ohne Leerraum."""
    out, cur = [], []
    for text, st in runs:
        for p in re.split(r'(\s+)', text):
            if not p:
                continue
            if p.isspace():
                if cur:
                    out.append(cur)
                cur = []
            elif cur and cur[-1][1] == st:
                cur[-1] = (cur[-1][0] + p, st)
            else:
                cur.append((p, st))
    if cur:
        out.append(cur)
    return out


def plain(w):
    return ''.join(t for t, _ in w)


def _slice(w, a, b=None):
    """Buchstaben a..b eines Wortes (für ein getrenntes Wort), die Auszeichnung bleibt."""
    out, pos = [], 0
    for text, st in w:
        s, e = max(a, pos), min(pos + len(text), pos + len(text) if b is None else b)
        if s < e:
            out.append((text[s - pos:e - pos], st))
        pos += len(text)
    return out


def render(ws):
    """Wörter als eine Zeile mit Auszeichnung; jedes Element wird in der Zeile geschlossen, in der es geöffnet wurde.
    Der Zwischenraum ist ausgezeichnet, wenn es beide Nachbarn sind (»<em>ganz kursiv</em>«)."""
    runs = []
    for k, w in enumerate(ws):
        if k and runs and w:
            a, b = runs[-1][1], w[0][1]
            runs.append((' ', tuple(x for x in a if x in b)))
        runs += w
    out, open_ = [], []
    for text, st in runs:
        k = 0
        while k < len(open_) and k < len(st) and open_[k] == st[k]:
            k += 1
        out += ['</%s>' % x for x in reversed(open_[k:])] + ['<%s>' % x for x in st[k:]]
        open_ = list(st)
        out.append(text)
    out += ['</%s>' % x for x in reversed(open_)]
    return ''.join(out)


def line_runs(l):
    """Eine Zeile des Buchs als Stücke (text, stile): Schrift-Auszeichnung wird zum Stil, Struktur (Absatz, Überschrift,
    Tabelle) fällt weg. Was die Zeile öffnet und nicht schließt, gilt bis zu ihrem Ende."""
    import korrlib
    out, st, pos = [], [], 0
    for m in korrlib.TAG.finditer(l):
        if m.start() > pos:
            out.append((l[pos:m.start()], tuple(x for x in INLINE if x in st)))
        pos = m.end()
        name = re.match(r'</?\s*(\w+)', m.group()).group(1).lower()
        if name in INLINE and not m.group().endswith('/>'):
            if not m.group().startswith('</'):
                st.append(name)
            elif name in st:
                del st[len(st) - 1 - st[::-1].index(name)]
        elif name in ('br', 'td', 'th'):
            out.append((' ', ()))
    if pos < len(l):
        out.append((l[pos:], tuple(x for x in INLINE if x in st)))
    return out


def _chapters(path):
    """(titel, [kapitel]); kapitel = Liste von Blöcken (_Blocks), in Lesereihenfolge (spine)."""
    with zipfile.ZipFile(path) as z:
        opf = ET.fromstring(z.read('META-INF/container.xml')).find('.//{*}rootfile').get('full-path')
        root = ET.fromstring(z.read(opf))
        t = root.find('.//{http://purl.org/dc/elements/1.1/}title')
        items = {i.get('id'): i.get('href') for i in root.findall('.//{*}item')}
        css = []
        for n in z.namelist():
            if n.lower().endswith('.css'):
                try:
                    css += css_rules(z.read(n).decode('utf-8', 'replace'))
                except Exception:
                    pass  # eine kaputte Stilvorlage kostet nur die Schrift-Auszeichnung
        chapters = []
        for ref in root.findall('.//{*}itemref'):
            href = items.get(ref.get('idref'))
            if not href:
                continue
            name = posixpath.normpath(posixpath.join(posixpath.dirname(opf), urllib.parse.unquote(href.split('#')[0])))
            try:
                src = z.read(name).decode('utf-8', 'replace')
            except KeyError:
                continue
            head = ''.join(re.findall(r'<style[^>]*>(.*?)</style>', src, re.S | re.I))
            p = _Blocks(css + css_rules(head) if head else css)
            p.feed(src)
            p.flush()
            if p.blocks:
                chapters.append(p.blocks)
        return (t.text or '').strip() if t is not None and t.text else None, chapters


def read(path):
    """(titel, [kapitel]); kapitel = Liste von Absätzen ohne Auszeichnung, in Lesereihenfolge (spine). Eine Zeile nach
    <br/> ist ein eigener Absatz, eine Tabellenreihe einer."""
    title, chapters = _chapters(path)
    out = []
    for ch in chapters:
        paras = []
        for b in ch:
            for seg in (b['segs'] if b['kind'] != 'table' else [[x for c in r for x in c[1] + [(' ', ())]] for r in b['rows']]):
                t = ' '.join(plain(w) for w in _words(seg))
                if t:
                    paras.append(t)
        out.append(paras)
    return title, out


def _continues(prev, l):
    """Setzt die Zeile l den Satz der Zeile prev fort, obwohl das EPUB dort einen Absatz beginnt? prev endet ohne
    Satzzeichen, und eine der beiden Zeilen hat dort ein kleingeschriebenes Wort: »… Aber sei Land ischt</p><p>groß
    und …«, »… auf dem fürstlichen</p><p>Gutshofe …« – beim Erstellen des EPUB an den Zeilen der Vorlage getrennt. Ein
    solcher Absatz gilt nicht. Listen, Verzeichnisse und Titel enden auch ohne Satzzeichen, aber auf ein Hauptwort oder
    eine Zahl (»Kindlieb, Karl 34 Jahre« / »Tausch, Katharina …«)."""
    import korrlib
    s = korrlib.TAG.sub('', prev).strip()
    if not s or korrlib.HLINE.match(prev.strip()) or korrlib.TABLETAG.search(prev) or PARA_END.search(s):
        return False
    return s.endswith('¬') or bool(LOWER.match(s.split()[-1]) or LOWER.match(korrlib.TAG.sub('', l).strip()))


def _wrap(ws, width):
    """Wörter zu Zeilen höchstens width Zeichen – gezählt wird, was man sieht, nicht die Auszeichnung."""
    lines, cur, n = [], [], 0
    for w in ws:
        k = len(plain(w))
        if cur and n + 1 + k > width:
            lines.append(cur)
            cur, n = [], 0
        n += k + (1 if cur else 0)
        cur.append(w)
    if cur:
        lines.append(cur)
    return lines


def _cells(page):
    """Die Zellen einer Seite bekommen ihre Tabellen-Auszeichnung erst hier: Eine Tabelle, die über eine Seitengrenze
    geht, wird auf jeder Seite eine eigene, vollständige – eine Tabelle darf nicht über zwei Seitendateien reichen."""
    out = []
    for k, it in enumerate(page):
        if isinstance(it, str):
            out.append(it)
            continue
        tid, first, last, tag, text = it
        before = k and not isinstance(page[k - 1], str) and page[k - 1][0] == tid
        after = k + 1 < len(page) and not isinstance(page[k + 1], str) and page[k + 1][0] == tid
        out.append(('' if before else '<table>') + ('<tr>' if first else '') + '<%s>%s</%s>' % (tag, text, tag)
                   + ('</tr>' if last else '') + ('' if after else '</table>'))
    return out


def text_book(path, out, width=68, per_page=34):
    """EPUB ohne PDF: Textbuch ohne Seitenbilder. Jedes Kapitel beginnt eine neue Seite. Absätze beginnen mit <p> und
    sind durch eine Leerzeile getrennt – außer das EPUB trennt mitten im Satz (_continues); eine Überschrift, die umbricht, ist
    mehrere Zeilen derselben Ebene (so fasst korrlib.headings sie zusammen); jede Tabellenzelle ist eine Zeile.
    Liefert dict(pages, title)."""
    title, chapters = _chapters(path)
    if not chapters:
        raise ValueError('keine_seiten')
    if glob.glob(os.path.join(out, '[0-9][0-9][0-9].txt')):
        raise FileExistsError(out)
    pages, tid = [], 0
    for blocks in chapters:
        groups, last = [], ''  # groups: was zusammen auf eine Seite gehört – eine Zeile, oder die Zellen einer Tabellenreihe
        for b in blocks:
            cont = b['kind'] == 'p' and _continues(last, plain(_words(b['segs'][0])[0]))  # kein neuer Absatz, keine Leerzeile
            if groups and not cont:
                groups.append([''])
            if b['kind'] == 'table':
                tid += 1
                for row in b['rows']:
                    groups.append([(tid, k == 0, k == len(row) - 1, tag, render(_words(runs))) for k, (tag, runs) in enumerate(row)])
                last = '<table>'
                continue
            for s, seg in enumerate(b['segs']):
                for k, ws in enumerate(_wrap(_words(seg), width)):
                    l = render(ws)
                    if b['kind'] == 'h':
                        l = '<h%d>%s</h%d>' % (b['level'], l, b['level'])
                    elif s == 0 and k == 0 and not cont:
                        l = '<p>' + l
                    groups.append([l])
                    last = l
        page = []
        for g in groups:
            if page and len(page) + len(g) > per_page:
                pages.append(page)
                page = []
            if page or g != ['']:
                page += g
        if page:
            pages.append(page)
    if len(pages) > 999:
        raise ValueError('zu_viele_seiten')
    os.makedirs(out, exist_ok=True)
    for n, page in enumerate(pages, 1):
        lines = _cells(page)
        while lines and not lines[-1]:
            lines.pop()
        with open(os.path.join(out, '%03d.txt' % n), 'w', encoding='utf-8') as f:
            f.write('\n'.join(['# '] + lines) + '\n')
    return dict(pages=len(pages), title=title)


def norm(w):
    return NORM.sub('', w.lower().replace('ſ', 's'))


class Words:
    """Der Wortlaut mit Auszeichnung: je Wort der Text (plain), die Stücke mit Stil (runs), die Ebene der Überschrift,
    in der es steht (0: keine), und ob es einen Absatz beginnt (para)."""

    def __init__(self):
        self.plain, self.runs, self.level, self.para = [], [], [], set()
        self.start = False  # das nächste Wort beginnt einen Absatz

    def add(self, w, level=0):
        p = plain(w)
        if JUNK.fullmatch(p):
            return  # ein Absatzanfang geht auf das nächste echte Wort über
        if self.start and not level:
            self.para.add(len(self.plain))
        self.start = False
        self.plain.append(p)
        self.runs.append(w)
        self.level.append(level)


def epub_words(path):
    """(titel, Words) eines EPUB."""
    title, chapters = _chapters(path)
    E = Words()
    for blocks in chapters:
        for b in blocks:
            if b['kind'] == 'table':
                for row in b['rows']:
                    for _, runs in row:
                        for w in _words(runs):
                            E.add(w)
                continue
            E.start = b['kind'] == 'p'
            for seg in b['segs']:
                for w in _words(seg):
                    E.add(w, b['level'])
    return title, E


def words(path):
    """Der Wortlaut eines EPUB als Wortfolge."""
    title, E = epub_words(path)
    return title, E.plain


def book_text(folder):
    """Words eines Textbuchs (aus einem EPUB ohne PDF angelegt, vielleicht schon korrigiert) – ohne Kopfzeilen und
    Fußnotenstriche; ein am Zeilenende getrenntes Wort wird wieder eines, seine Auszeichnung bleibt."""
    import korrlib
    E = Words()
    for f in sorted(glob.glob(os.path.join(folder, '[0-9][0-9][0-9].txt'))):
        for l in open(f, encoding='utf-8').read().split('\n'):
            if l.startswith('#') or l == '---':
                continue
            h = korrlib.HLINE.match(l.strip())
            level = int(h.group(1)) if h else 0
            E.start = E.start or l.startswith('<p>')
            for w in _words(line_runs(l)):
                if E.plain and E.plain[-1].endswith('¬'):  # zweite Hälfte eines getrennten Wortes
                    E.runs[-1] = _slice(E.runs[-1], 0, len(E.plain[-1]) - 1) + w
                    E.plain[-1] = plain(E.runs[-1])
                else:
                    E.add(w, level)
    return E


def book_words(folder):
    """Der Wortlaut eines Textbuchs als Wortfolge, ohne Auszeichnung."""
    return book_text(folder).plain


def pdf_fit(E, pdf, sample=8):
    """Gehört das PDF zu diesem Wortlaut? Stichprobe über die Textebene des PDF: Vier-Wort-Folgen einiger Seiten, wie
    viele davon im Wortlaut vorkommen (0–1). None, wenn das PDF keine brauchbare Textebene hat – dann zeigt es sich
    erst nach der Texterkennung (matched von transplant)."""
    import fitz
    marks = set()
    En = [norm(w) for w in E]
    for i in range(len(En) - 3):
        key = tuple(En[i:i + 4])
        if all(key):
            marks.add(key)
    tot = hit = 0
    with fitz.open(pdf) as d:
        ns = sorted({int(k * (d.page_count - 1) / max(1, sample - 1)) for k in range(sample)}) if d.page_count else []
        for n in ns:
            raw = []
            for w in d[n].get_text('words'):  # am Zeilenende getrennte Wörter (Zu- / kunft) zusammensetzen wie im EPUB
                if raw and raw[-1][-1:] in '-¬' and len(raw[-1]) > 1:
                    raw[-1] = raw[-1][:-1] + w[4]
                else:
                    raw.append(w[4])
            ws = [x for x in map(norm, raw) if x]
            for i in range(len(ws) - 3):
                tot += 1
                hit += tuple(ws[i:i + 4]) in marks
    return round(hit / tot, 3) if tot >= 20 else None


def transplant(path, book, progress=lambda done, total, msg: None):
    """Ersetzt im Buchordner book (aus dem PDF gebaut) den Wortlaut der Zeilen durch den des EPUB.
    Zeilen, zu denen das EPUB nichts Passendes hat (Kopfzeilen, Fußnoten, die im EPUB anderswo stehen), behalten
    ihren Text aus dem PDF. Liefert dict(title, matched = Anteil der Zeilen mit EPUB-Text)."""
    title, E = epub_words(path)
    return _transplant(E, title, os.path.basename(path), book, progress, os.path.abspath(path))


def transplant_book(src, book, progress=lambda done, total, msg: None):
    """Wie transplant, nur kommt der Wortlaut aus einem Textbuch (#40): Wer sein EPUB ohne PDF angelegt und darin schon
    korrigiert hat, bekommt den korrigierten Text auf die Zeilen des nachgereichten Scans gelegt – mit Auszeichnung."""
    return _transplant(book_text(src), None, os.path.basename(src), book, progress)


def _marks(En):
    """Wo steht eine Seite im EPUB? Vier-Wort-Folgen, die im EPUB genau einmal vorkommen, sind verlässliche Wegmarken –
    unabhängig von der Reihenfolge (Vorspann, Anhang und Anmerkungen stehen im EPUB oft woanders als im Buch)."""
    marks = {}
    for i in range(len(En) - 3):
        key = tuple(En[i:i + 4])
        if all(key):
            marks[key] = i if key not in marks else -1
    return marks


def _tokens(l):
    """(anfang, ende, wort) je Wort der Zeile. Auszeichnung zählt nicht und trennt kein Wort (»Wort<sup>1</sup>«);
    anfang und ende sind Stellen in der Zeile, wie sie ist."""
    import korrlib
    idx, k = [], 0
    for m in korrlib.TAG.finditer(l):
        idx += range(k, m.start())
        k = m.end()
    idx += range(k, len(l))
    s = ''.join(l[i] for i in idx)
    return [(idx[m.start()], idx[m.end() - 1] + 1, m.group()) for m in re.finditer(r'\S+', s)]


def _page_words(lines):
    """Die Wörter einer Seite: [normiert, zeile, zeile2 oder None, länge des ersten Teils, (anfang, ende), (anfang2, ende2)].
    Ein über das Zeilenende getrenntes Wort (Zu¬ / kunft) ist EIN Wort, das zu zwei Zeilen gehört."""
    toks = []
    for i, l in enumerate(lines):
        if l.startswith('#') or l == '---':
            continue
        for s, e, w in _tokens(l):
            if toks and toks[-1][2] == -1:       # Fortsetzung eines getrennten Wortes
                toks[-1][0] += norm(w); toks[-1][2] = i; toks[-1][5] = (s, e)
            elif w.endswith('¬') and len(w) > 1:
                toks.append([norm(w[:-1]), i, -1, len(w) - 1, (s, e), None])
            else:
                toks.append([norm(w), i, None, 0, (s, e), None])
    for t in toks:
        if t[2] == -1:
            t[2] = None
    return [t for t in toks if t[0]]


def _align(En, marks, body, pos):
    """Die Wörter einer Seite den Wörtern des EPUB zuordnen: ({seitenwort: epub-wort} oder None, neue Leseposition)."""
    bn = [t[0] for t in body]
    votes = sorted(marks[k] - i for i in range(len(bn) - 3) for k in [tuple(bn[i:i + 4])] if marks.get(k, -1) >= 0)
    if len(votes) >= 3:
        pos = max(0, votes[len(votes) // 2])  # Median: einzelne Irrläufer stören nicht
        lo, hi = max(0, pos - len(body) // 2 - 50), pos + 2 * len(body) + 50
    else:
        lo, hi = max(0, pos - 200), pos + 3 * len(body) + 1500
    sm = difflib.SequenceMatcher(None, bn, En[lo:hi], autojunk=False)
    blocks = [b for b in sm.get_matching_blocks() if b.size]
    if sum(b.size for b in blocks) < 0.4 * len(body):
        return None, pos
    return {b.a + d: lo + b.b + d for b in blocks for d in range(b.size)}, lo + blocks[-1].b + blocks[-1].size


def _lines_of(body):
    """zeile -> Seitenwörter (ein getrenntes Wort zählt in beiden Zeilen)."""
    on = {}
    for a, t in enumerate(body):
        for ln in ([t[1]] if t[2] is None else [t[1], t[2]]):
            on.setdefault(ln, []).append(a)
    return on


def _sure(idx, m):
    """Passt die Zeile (ihre Seitenwörter idx) zum EPUB? Mindestens die Hälfte ihrer Wörter ist zugeordnet, und die
    zugeordneten liegen im EPUB beieinander – sonst ist es ein Zufallstreffer (Rauschen unter der Seitenzahl)."""
    hits = [a for a in idx if a in m]
    return len(hits) * 2 >= len(idx) and bool(hits) and m[hits[-1]] - m[hits[0]] <= 2 * len(idx) + 3


def _transplant(E, title, source, book, progress, path=None):
    En = [norm(w) for w in E.plain]
    if not En:
        raise ValueError('keine_seiten')
    marks = _marks(En)
    files = sorted(glob.glob(os.path.join(book, '[0-9][0-9][0-9].txt')))
    pos, taken, total_lines = 0, 0, 0
    last = ''  # die letzte Zeile mit Text aus dem EPUB – ob danach ein Absatz beginnen darf (_continues)
    for k, f in enumerate(files):
        lines = open(f, encoding='utf-8').read().split('\n')
        if lines and lines[-1] == '':
            lines.pop()
        body = _page_words(lines)
        if len(body) >= 5:
            m, pos = _align(En, marks, body, pos)
            if m:
                # je Zeile: erstes und letztes zugeordnetes EPUB-Wort; dazwischen gilt der EPUB-Wortlaut
                split = {m[a]: (body[a][1], body[a][3]) for a in m if body[a][2] is not None}
                on = _lines_of(body)
                foot = lines.index('---') if '---' in lines else len(lines)
                span = {}
                for ln, idx in on.items():
                    if not _sure(idx, m):
                        continue  # zu wenig Übereinstimmung bzw. Ausreißer: PDF-Text behalten
                    hits = [a for a in idx if a in m]
                    # head/tail: Seitenwörter vor dem ersten bzw. nach dem letzten Treffer – so viele EPUB-Wörter aus der
                    # Lücke zur Nachbarzeile gehören noch hierher (das EPUB schreibt dort etwas anderes als das PDF)
                    span[ln] = [m[hits[0]], m[hits[-1]], idx.index(hits[0]), len(idx) - 1 - idx.index(hits[-1])]
                order = sorted(span)
                for u, v in zip(order, order[1:]):
                    gap = span[v][0] - span[u][1] - 1
                    if v == u + 1 and 0 < gap <= span[u][3] + span[v][2] + 2:  # Nachbarzeilen: Lückenwörter aufteilen, nichts verlieren
                        take = min(gap, max(span[u][3], gap - span[v][2]))
                        span[u][1] += take; span[v][0] -= gap - take
                new, starts = list(lines), set()
                for ln, (e0, e1, _, _) in span.items():
                    ws = []
                    for e in range(e0, e1 + 1):
                        w = E.runs[e]
                        if e in split:  # getrenntes Wort: am Zeilenende der erste Teil mit ¬, in der Folgezeile der Rest
                            sl, n1 = split[e]
                            cut = _cut(E.plain[e], n1)
                            w = _slice(w, 0, cut) if sl == ln else _slice(w, cut)
                            if sl == ln:  # ¬ gleich hinter dem Wort, die Auszeichnung danach – so wie server.join_lines es kennt
                                w[-1] = (w[-1][0] + '¬', w[-1][1])
                        ws.append(w)
                    l = render(ws)
                    lv = set(E.level[e0:e1 + 1])
                    if ln > foot:  # Fußnoten: keine Überschrift, kein Absatz
                        pass
                    elif len(lv) == 1 and min(lv):  # die ganze Zeile steht in einer Überschrift des EPUB
                        l = '<h%d>%s</h%d>' % (min(lv), l, min(lv))
                    elif e0 in E.para and not (e0 in split and split[e0][0] != ln):
                        starts.add(ln)
                    new[ln] = l
                    taken += 1
                for ln in sorted(x for x in span if x < foot):  # Absatzanfänge in Lesereihenfolge
                    if ln in starts and not _continues(last, new[ln]):
                        new[ln] = '<p>' + new[ln]
                    last = new[ln]
                if new != lines:
                    with open(f, 'w', encoding='utf-8') as o:
                        o.write('\n'.join(new) + '\n')
        total_lines += sum(1 for l in lines if l.strip() and not l.startswith('#') and l != '---')
        progress(k + 1, len(files), 'epub')
    matched = round(taken / total_lines, 3) if total_lines else 0.0
    q = os.path.join(book, 'qualitaet.json')
    try:
        d = json.load(open(q, encoding='utf-8'))
        # path: wo das EPUB lag; auszeichnung: Überschriften und Schrift sind mitgekommen – nichts nachzutragen (markup)
        d['epub'] = dict(file=source, matched=matched, auszeichnung=True, **({'path': path} if path else {}))
        json.dump(d, open(q, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    except (OSError, ValueError):
        pass
    return dict(title=title, matched=matched)


INLINE_JOIN = re.compile(r'</(%s)> <\1>' % '|'.join(INLINE))


def _marked(l, s, x):
    """Ist das Wort l[s:x] schon ausgezeichnet – steht Auszeichnung darin, oder ist an seiner Stelle ein Element offen?
    (Ein Platzhalter \\0 an der Stelle des Wortes: sein Stil ist der, der dort gilt.)"""
    return '<' in l[s:x] or bool(line_runs(l[:s] + '\0')[-1][1])


def markup(E, pages, skip=None, progress=lambda done, total, msg: None):
    """Die Auszeichnung des EPUB in einem Buch nachtragen, das schon eingelesen und vielleicht längst korrigiert ist (#81):
    dieselbe Zuordnung der Wörter wie beim Einlesen, doch der Wortlaut bleibt, wie er ist. Dazu kommen nur Überschriften
    (die ganze Zeile steht im EPUB in einer), Absatzanfänge (<p>, wo noch keiner steht) und die Schrift einzelner Wörter –
    die genaue Auszeichnung, wenn das Wort gleich geschrieben ist, sonst die des ganzen Wortes, wenn es im EPUB ganz
    ausgezeichnet ist. Was schon ausgezeichnet ist, bleibt; nichts wird weggenommen. skip: {seite: {zeilen}}, die nicht zum
    Text gehören (Kolumnentitel, Seitenzahl unten). Liefert ({seite: neue zeilen}, dict(headings, paragraphs, words,
    checked = Seiten mit Text, matched = davon die, die zum EPUB passen))."""
    import korrlib
    En = [norm(w) for w in E.plain]
    marks, pos = _marks(En), 0
    out, stats = {}, dict(headings=0, paragraphs=0, words=0, checked=0, matched=0)
    keys = sorted(pages)
    last = ''  # die letzte Textzeile, die zum EPUB passt – ob danach ein Absatz beginnen darf (_continues)
    for n, pg in enumerate(keys):
        progress(n + 1, len(keys), 'epubmark')
        lines = pages[pg]
        body = _page_words(lines)
        if len(body) < 5:
            last = ''
            continue
        stats['checked'] += 1
        m, pos = _align(En, marks, body, pos)
        if not m:
            last = ''
            continue
        stats['matched'] += 1
        new, on = list(lines), _lines_of(body)
        foot = lines.index('---') if '---' in lines else len(lines)
        no = (skip or {}).get(pg, set())
        good = {ln for ln, idx in on.items() if _sure(idx, m)}
        # Schrift je Wort – an den Stellen der unveränderten Zeile, von hinten nach vorn
        edits = {}
        for a, t in enumerate(body):
            e = m.get(a)
            if e is None or not any(st for _, st in E.runs[e]):
                continue
            parts = [(t[1], t[4])] + ([(t[2], t[5])] if t[2] is not None else [])
            if any(ln not in good or ln in no for ln, _ in parts):
                continue
            raws = [lines[ln][s:x] for ln, (s, x) in parts]
            if any(_marked(lines[ln], s, x) for ln, (s, x) in parts):
                continue  # schon ausgezeichnet (etwa ein hochgestelltes Fußnotenzeichen)
            runs = E.runs[e]
            if ''.join(raws).replace('¬', '') == E.plain[e]:
                if len(raws) == 1:
                    pieces = [render([runs])]
                else:
                    cut = len(raws[0]) - 1
                    first = _slice(runs, 0, cut)
                    first[-1] = (first[-1][0] + '¬', first[-1][1])
                    pieces = [render([first]), render([_slice(runs, cut)])]
            elif len({st for _, st in runs}) == 1:  # anders geschrieben, im EPUB aber ganz ausgezeichnet
                pieces = [render([[(r, runs[0][1])]]) for r in raws]
            else:
                continue
            for (ln, (s, x)), piece in zip(parts, pieces):
                edits.setdefault(ln, []).append((s, x, piece))
            stats['words'] += 1
        for ln, ed in edits.items():
            l = new[ln]
            for s, x, piece in sorted(ed, reverse=True):
                l = l[:s] + piece + l[x:]
            new[ln] = INLINE_JOIN.sub(' ', l)  # »<em>sehr</em> <em>weit</em>« → »<em>sehr weit</em>«
        # Überschriften und Absatzanfänge, Zeile für Zeile in Lesereihenfolge
        for ln in sorted(on):
            idx, l = on[ln], new[ln]
            if ln >= foot or ln in no or ln not in good:
                continue
            if korrlib.HLINE.match(l.strip()) or korrlib.TABLETAG.search(l):
                last = l
                continue
            lv = {E.level[m[a]] if a in m else None for a in idx}  # None: ein Wort, das das EPUB nicht hat
            level = lv.pop() if len(lv) == 1 else None
            if level:
                new[ln] = korrlib.heading(l[3:] if l.startswith('<p>') else l, level)
                stats['headings'] += 1
            elif body[idx[0]][1] == ln and m.get(idx[0]) in E.para and not l.startswith('<p>') \
                    and (len(idx) == 1 or m.get(idx[1]) == m[idx[0]] + 1) and not _continues(last, l):
                new[ln] = '<p>' + l  # auch das zweite Wort folgt im EPUB darauf, und die Zeile davor schließt einen Satz ab
                stats['paragraphs'] += 1
            last = new[ln]
        if new != lines:
            out[pg] = new
    return out, stats


def _cut(word, n1):
    """Trennstelle im EPUB-Wort: so viele Buchstaben wie im ersten Teil des PDF-Wortes (Satzzeichen davor zählen nicht)."""
    lead = len(word) - len(word.lstrip('„“"»«(‚\'['))
    return max(1, min(len(word) - 1, lead + n1))
