"""Fraktur-Korrektor: Lesen und Korrigieren von OCR-Text neben dem Seitenbild.
py server.py [<buchordner>] [--port 8765] [--dic <hunspell-pfad>] [--title "…"] [--no-browser] [--lan]

Ohne Buchordner erscheint die Bibliothek (Bücher öffnen, Transkribus-Export importieren).
Buchordner: NNN.txt (eine Datei je Seite), lines.json (Zeilengeometrie), img/NNN.png|jpg,
optional autokorr.log, whitelist.txt; lesezeichen.json und korrekturen.log werden angelegt."""
import sys, os, json, re, glob, time, uuid, shutil, hashlib, tempfile, threading, subprocess, socketserver, urllib.parse, webbrowser, argparse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import korrlib, pagexml, ocr, epub, finder, pdfbuch
from korrlib import read_page, corpus_freq, joined_tokens, in_dict

HERE = getattr(sys, '_MEIPASS', None) or os.path.dirname(os.path.abspath(__file__))  # gepackt liegen dict/, docs/ und die HTML-Dateien im Bundle
DONATE_URL = 'https://buymeacoffee.com/josicreate'  # leer = kein Spenden-Link
LIBFILE = os.path.join(korrlib.HOME, 'bibliothek.json')
LIBLOCK = threading.RLock()
BOOKS = {}
DEFAULT = None  # id des Buchs von der Kommandozeile
IMGTYPES = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg'}
# Wörter in den Zetteln für Obsidian (Dateinamen und Quellenzeile) in der Sprache der Oberfläche
NOTE_WORDS = dict(
    de=dict(page='Seite', line='Zeile', note='Anmerkung', src='0 Quellenangabe',
            template='# %s\n\nHerkunft: (z. B. Universitätsbibliothek Münster, Fernleihe)\n\nZitierweise (Zotero):\n'),
    en=dict(page='Page', line='Line', note='Note', src='0 Source',
            template='# %s\n\nProvenance: (e.g. university library, interlibrary loan)\n\nCitation (Zotero):\n'))


def version():
    try:
        return re.search(r'^version\s*=\s*"([^"]+)"', open(os.path.join(HERE, 'pyproject.toml'), encoding='utf-8').read(), re.M).group(1)
    except (OSError, AttributeError):
        return ''


def known(w, freq, dics=korrlib.DEFAULT):
    """Wörterbuch, oder häufig im Buch (Namen) – kurze Wörter schützt die Häufigkeit nicht (ber, bie, baß …).
    Siglen in Großbuchstaben (GHB, BWKG, LKA) gelten, wenn sie mehrfach vorkommen: Lesefehler sehen nicht so aus."""
    n = freq.get(w, 0)
    return in_dict(w, dics) or (len(w) > 4 and n >= 3) or (n >= 2 and 2 <= len(w) <= 6 and w.isupper())


def propose_settings(folder, year=None):
    """Nach dem Einlesen: Erscheinungsjahr raten und die passende Rechtschreibung vorschlagen (buch.json)."""
    year = year or korrlib.guess_year(korrlib.read_pages(folder))
    st = dict(year=year, dics=korrlib.dics_for_year(year))
    write_atomic(os.path.join(folder, 'buch.json'), json.dumps(st, ensure_ascii=False, indent=1))
    return st


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
        self.stpath = os.path.join(self.folder, 'buch.json')
        self.lock = threading.RLock()
        try:
            self.geo = json.load(open(os.path.join(self.folder, 'lines.json'), encoding='utf-8'))
        except OSError:
            self.geo = {}
        self.unsicher = self.autokorr_unsicher()
        self.settings = self.load_settings()
        self.pages, self.mt, self.freq, self.wl, self.wlmt, self.fcache, self.size = {}, {}, {}, set(), None, {}, {}
        self.prog = None  # [geprüfte Seiten, Seiten] während overview() läuft – für den Ladebalken (/api/progress)

    def load_settings(self):
        """buch.json: year (Erscheinungsjahr, geraten oder None), dics (welche Rechtschreibung gilt), notizen (Ordner für
        Zettel in Obsidian oder None). Fehlt die Datei – Bücher von früher –, gilt wie bisher nur 1901."""
        try:
            st = json.load(open(self.stpath, encoding='utf-8'))
        except (OSError, ValueError):
            st = {}
            own = os.path.normcase(os.path.abspath(books_dir())) + os.sep
            if os.path.exists(os.path.join(self.folder, 'qualitaet.json')) or os.path.normcase(self.folder).startswith(own):
                st = propose_settings(self.folder)  # vom Programm eingelesen (auch EPUB-Textbücher), aber vor dieser Funktion: Vorschlag nachholen
        dics = [d for d in st.get('dics') or korrlib.DEFAULT if d in korrlib.DICS]
        # kennung: bleibt dem Buch über das Sichern als PDF hinweg erhalten – daran erkennt ein anderer Rechner dasselbe Buch wieder
        return dict(year=st.get('year'), dics=dics or list(korrlib.DEFAULT), notizen=st.get('notizen') or None, kennung=st.get('kennung') or None)

    def save_settings(self):
        write_atomic(self.stpath, json.dumps(self.settings, ensure_ascii=False, indent=1))

    def set_dics(self, dics):
        with self.lock:
            if not any(d in dics for d in ('1901', 'neu')):  # 'vor1901' sind nur Regeln – ein Wörterbuch muss gelten
                dics = list(dics) + ['1901']
            self.settings['dics'] = [d for d in korrlib.DICS if d in dics]
            self.save_settings()
            self.fcache.clear()
        return self.settings

    def set_notes(self, folder):
        """Ordner, in dem die Zettel dieses Buchs landen (im Obsidian-Vault); leer = keine Notizen."""
        with self.lock:
            self.settings['notizen'] = os.path.abspath(folder) if folder else None
            self.save_settings()
        return self.settings

    def page_number(self, pg):
        """Gedruckte Seitenzahl aus der Kopfzeile als (zahl, position, länge) – oder None."""
        lines = self.pages.get(pg) or []
        m = re.search(r'\d+', lines[0]) if lines and lines[0].startswith('#') else None
        return (int(m.group()), m.start(), len(m.group())) if m else None

    def expected_page(self, pg):
        """Seitenzahl, die nach den Nachbarseiten in der Kopfzeile stehen müsste – oder None, wenn die Nachbarn sich nicht
        einig sind. Die OCR liest in Fraktur gern 1 als 4 (16 → 46), auch auf zwei Seiten hintereinander; die drei Seiten
        davor und danach verraten es, wenn mindestens drei von ihnen mit Zweidrittelmehrheit dieselbe Zahl ergeben. Bei einem
        fehlenden oder doppelten Scan stehen die Nachbarn halb gegen halb, dann bleibt es still."""
        keys = list(self.pages)
        k = keys.index(pg)
        votes = {}
        for d in (-3, -2, -1, 1, 2, 3):
            n = self.page_number(keys[k + d]) if 0 <= k + d < len(keys) else None
            if n:
                votes[n[0] - d] = votes.get(n[0] - d, 0) + 1
        best = max(votes, key=votes.get) if votes else None
        return best if best is not None and votes[best] >= 3 and votes[best] * 3 >= sum(votes.values()) * 2 else None

    def printed_page(self, pg):
        """Seitenzahl für die Quellenangabe: die gedruckte aus der Kopfzeile – bei einem Lesefehler oder ohne Kopfzeile
        (Kapitelanfang) die nach den Nachbarseiten richtige –, sonst die Nummer der Datei."""
        n = self.page_number(pg)
        exp = self.expected_page(pg)
        return str(exp if exp is not None else n[0] if n else int(pg))

    def make_note(self, pg, text, lang='de', lines=None):
        """Ein Zettel nach Luhmanns Art im Notizordner: fortlaufend nummeriert, oben Platz für die eigene Anmerkung, unter dem
        Strich das Zitat und die Quelle – Seite, Zeilen (lines = (von, bis), gezählt wie in der Leiste des Readers) und Verweis auf die
        Quellenangabe des Buchs (Datei „0 Quellenangabe“, wird bei Bedarf als Vorlage angelegt; dort trägt der Nutzer Herkunft und
        Zotero-Zitierweise ein). Liefert (ergebnis, fehler)."""
        W = NOTE_WORDS.get(lang) or NOTE_WORDS['de']
        folder = self.settings.get('notizen')
        if not folder:
            return None, 'kein_notizordner'
        if not os.path.isdir(folder):
            if not os.path.isdir(os.path.dirname(folder)):
                return None, 'notizordner_fehlt'
            os.makedirs(folder)  # der Ordner des Buchs im Vault darf neu sein, sein Elternordner muss stehen (sonst ist der Pfad vertippt)
        text = korrlib.TAG.sub('', text)
        text = re.sub(r'¬\s*\n\s*', '', text)  # getrennte Wörter zusammenziehen, Zeilen zu einem Absatz
        text = ' '.join(text.split()).strip()
        if not text:
            return None, 'kein_text'
        with self.lock:
            self.refresh()
            if pg not in self.pages:
                return None, 'quelle_fehlt'
            page = self.printed_page(pg)
        src = W['src']
        if not os.path.exists(os.path.join(folder, src + '.md')):
            with open(os.path.join(folder, src + '.md'), 'w', encoding='utf-8', newline='\n') as f:
                f.write(W['template'] % self.title)
        nums = [int(m.group(1)) for n in os.listdir(folder) for m in [re.match(r'(\d+)(?:\D|$)', n)] if m]
        n = max(nums, default=0) + 1
        name = '%02d %s %s' % (n, W['page'], page)
        path = os.path.join(folder, name + '.md')
        where = '%s %s' % (W['page'], page)
        if lines:
            a, b = int(lines[0]), int(lines[-1])
            where += ', %s %s' % (W['line'], str(a) if a == b else '%d–%d' % (a, b))
        body = '**%s**\n\n\n\n---\n\n> %s\n\n%s, [[%s|%s]]\n' % (W['note'], text, where, src, self.title)
        with open(path, 'x', encoding='utf-8', newline='\n') as f:  # 'x': nie überschreiben
            f.write(body)
        return dict(file=path, name=name, number=n, page=page, text=text), None

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
        dics = tuple(self.settings['dics'])
        n, exp = self.page_number(pg), self.expected_page(pg)
        key = (self.mt[pg], self.wlmt, dics, exp)  # exp hängt an den Nachbarseiten, nicht an dieser Datei
        c = self.fcache.get(pg)
        if c and c[0] == key:
            return c[1]
        lines, wl, freq = self.pages[pg], self.wl, self.freq
        out = []
        if n and exp is not None and exp != n[0]:  # Seitenzahl, die nicht zu den Nachbarseiten passt
            out.append(dict(line=0, start=n[1], len=n[2], word=str(n[0]), kind='page', expect=exp))
        toks, joined = joined_tokens(lines)
        jstart = {(i, s1) for i, s1, w1, j, w2 in joined}
        jend = {(j, toks[j][0][0]) for i, s1, w1, j, w2 in joined}  # der zweite Teil beginnt hinter etwaiger Auszeichnung (<td>)
        for i, s1, w1, j, w2 in joined:
            if not (known(w1 + w2, freq, dics) or (w1 + w2) in wl):
                out.append(dict(line=i, start=s1, len=len(w1), word=w1 + '¬' + w2, kind='oov', start2=toks[j][0][0]))
        for i, tl in enumerate(toks):
            if lines[i].startswith('#'):
                continue
            for s, w in tl:
                if (i, s) in jstart or (i, s) in jend or len(w) < 2:
                    continue
                if not (known(w, freq, dics) or w in wl):
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

    def geo_seq(self, pg, lines):
        """Ordnet den Textzeilen die Zeilen aus lines.json zu (dieselben dict-Objekte, None für Trenner); None wenn die Anzahl
        nicht passt."""
        g = self.geo.get(pg)
        if not g or not g['lines']:
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
        return seq

    def geo_lines(self, pg, lines):
        """Zeilenrahmen in Bildpixeln je Textzeile; None ohne Zuordnung oder ohne Bild.
        Transkribus legt die Seite höhenfüllend und horizontal zentriert auf sein Format (g['w'] x g['h']). Ist das Bild
        dagegen höher als der Rahmen (die SuUB Bremen hängt unten an jedes PDF-Bild eine DFG-Leiste), gilt die Breite,
        und der Rahmen sitzt oben – sonst läge die Markierung unten auf der Seite eine Zeile zu tief."""
        seq, sz, g = self.geo_seq(pg, lines), self.img_size(pg), self.geo.get(pg)
        if seq is None or not sz:
            return None
        w, h = sz
        s = min(h / g['h'], w / g['w'])
        ox = (w - g['w'] * s) / 2
        return [None if l is None else dict(x0=l['x0'] * s + ox, x1=l['x1'] * s + ox, y0=l['y0'] * s, y1=l['y1'] * s) for l in seq]

    def page_data(self, pg):
        with self.lock:
            self.refresh()
            lines = self.pages[pg]
            # size: damit der Reader die Nachbarseiten schon richtig platziert, bevor ihre Bilder geladen sind
            return dict(page=pg, lines=lines, geo=self.geo_lines(pg, lines), flags=self.flags(pg), img=self.img_url(pg), size=self.img_size(pg))

    def overview(self):
        with self.lock:
            self.refresh()
            self.prog, out = [0, len(self.pages)], []
            try:
                for pg in self.pages:
                    out.append(dict(page=pg, n=len(self.flags(pg))))
                    self.prog[0] += 1
            finally:
                self.prog = None
            return out

    def search(self, q, limit=1000):
        """Alle Stellen im Buch, an denen q vorkommt: ohne Rücksicht auf Groß- und Kleinschreibung und auf ſ/s,
        auch über die Zeilentrennung ¬ hinweg. Liefert [dict(page, line, start, len[, join, start2, len2])]."""
        norm = lambda s: s.lower().replace('ſ', 's')
        qn, out = norm(q.strip()), []
        if not qn:
            return out
        with self.lock:
            self.refresh()
            for pg, lines in self.pages.items():
                for i, l in enumerate(lines):
                    ln = norm(l)
                    s = ln.find(qn)
                    while s >= 0:
                        out.append(dict(page=pg, line=i, start=s, len=len(qn)))
                        s = ln.find(qn, s + 1)
                toks, joined = joined_tokens(lines)
                for i, s1, w1, j, w2 in joined:  # Zu¬ / kunft: das Wort gibt es nur zusammengesetzt
                    if qn in norm(w1 + w2) and qn not in norm(w1) and qn not in norm(w2):
                        out.append(dict(page=pg, line=i, start=s1, len=len(w1), join=True, start2=toks[j][0][0], len2=len(w2)))
                if len(out) >= limit:
                    break
        out.sort(key=lambda o: (o['page'], o['line'], o['start']))
        return out[:limit]

    def occurrences(self, word, limit=500):
        """Alle Vorkommen eines Wortes im Buch (auch über Zeilentrennung ¬ hinweg), mit Zeilengeometrie."""
        out = []
        with self.lock:
            self.refresh()
            for pg, lines in self.pages.items():
                toks, joined = joined_tokens(lines)
                frag = {(i, s1) for i, s1, w1, j, w2 in joined} | {(j, toks[j][0][0]) for i, s1, w1, j, w2 in joined}
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
                        s2 = toks[i + 1][0][0]
                        lines[i + 1] = lines[i + 1][:s2] + new[n1:] + lines[i + 1][s2 + len(w2):]
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

    def save_geo(self):
        write_atomic(os.path.join(self.folder, 'lines.json'), json.dumps(self.geo, ensure_ascii=False))

    def retable(self, lines, n):
        """Liegt Zeile n in einer Tabelle, die Tabelle neu durchzählen: Nach dem Teilen oder Verbinden stimmen die Spalten wieder."""
        blk = korrlib.table_block(lines, n)
        if not blk:  # beim Teilen kann </table> in die neue Zeile gerutscht sein
            blk = korrlib.table_block(lines, n - 1) if n > 0 else None
        if blk:
            a, b = blk
            cols, head = korrlib.table_shape(lines[a:b + 1])
            lines[a:b + 1] = korrlib.make_table(lines[a:b + 1], cols, head)

    def split_line(self, pg, n, old, text, pos):
        """Zeile n an der Stelle pos teilen (text = Inhalt des Eingabefelds, darf gegenüber old schon geändert sein). Der
        Bildausschnitt der Zeile wird anteilig mitgeteilt, damit jede Textzeile weiter ihre Bildzeile hat."""
        with self.lock:
            self.refresh()
            lines = list(self.pages[pg])
            if not (0 <= n < len(lines)) or lines[n] != old or lines[n] == '---' or (n == 0 and lines[n].startswith('#')) or '\n' in text:
                return None, 409
            if any(m.start() < pos < m.end() for m in korrlib.TAG.finditer(text)):
                return None, 400  # mitten in einer Auszeichnung
            left, right = text[:pos].rstrip(), text[pos:].lstrip()
            if not korrlib.TAG.sub('', left).strip() or not korrlib.TAG.sub('', right).strip():  # am sichtbaren Text gemessen
                return None, 400
            seq = self.geo_seq(pg, lines)
            e = seq[n] if seq else None
            if e:
                vl, vr = len(korrlib.TAG.sub('', left)), len(korrlib.TAG.sub('', right))
                xs = round(e['x0'] + (e['x1'] - e['x0']) * vl / max(1, vl + vr))
                G = self.geo[pg]['lines']
                k = next(i for i, x in enumerate(G) if x is e)
                G.insert(k + 1, dict(e, x0=xs, text=right))
                e.update(x1=xs, text=left)
                self.save_geo()
            lines[n:n + 1] = [left, right]
            self.retable(lines, n)
            self.write_page(pg, lines)
            self.klog('teilen', pg, n, old, left + ' ⏎ ' + right)
            return self.page_data(pg), None

    def join_lines(self, pg, n, old):
        """Zeile n mit der folgenden verbinden; die Bildausschnitte werden vereinigt. Ein Trennzeichen ¬ fällt dabei weg."""
        with self.lock:
            self.refresh()
            lines = list(self.pages[pg])
            if not (0 <= n < len(lines) - 1) or lines[n:n + 2] != old or '---' in lines[n:n + 2] or (n == 0 and lines[n].startswith('#')):
                return None, 409
            a, b = lines[n].rstrip(), lines[n + 1].lstrip()
            seq = self.geo_seq(pg, lines)
            if seq and seq[n] and seq[n + 1]:
                e, f = seq[n], seq[n + 1]
                e.update(x0=min(e['x0'], f['x0']), x1=max(e['x1'], f['x1']), y0=min(e['y0'], f['y0']), y1=max(e['y1'], f['y1']),
                         text=(e.get('text') or '') + ' ' + (f.get('text') or ''))
                G = self.geo[pg]['lines']
                del G[next(i for i, x in enumerate(G) if x is f)]
                self.save_geo()
            m = re.search(r'¬((?:</?\w+>)*)$', a)  # Zu¬ + kunft -> Zukunft (Auszeichnung hinter dem ¬ bleibt)
            joined = a[:m.start()] + m.group(1) + b if m and re.match(r'(?:</?\w+>)*[a-zäöüß]', b) else a + ' ' + b
            lines[n:n + 2] = [joined]
            self.retable(lines, n)
            self.write_page(pg, lines)
            self.klog('verbinden', pg, n, old[0] + ' ⏎ ' + old[1], joined)
            return self.page_data(pg), None

    def markup(self, pg, body):
        """Tabelle setzen/entfernen bzw. Überschrift: baut die Änderungen und schickt sie durch edit() – mit derselben Prüfung
        (die Zeilen müssen noch so aussehen wie im Browser) und demselben Protokoll. Liefert (seitendaten, fehler)."""
        with self.lock:
            self.refresh()
            lines = self.pages[pg]
            a, b = body.get('start', body.get('line', 0)), body.get('end', body.get('line', 0))
            if not (0 <= a <= b < len(lines)):
                return None, 409
            if body.get('kind') == 'untable':
                blk = korrlib.table_block(lines, a)
                if not blk:
                    return None, 400
                a, b = blk
                new = [korrlib.TABLETAG.sub('', l) for l in lines[a:b + 1]]
            elif body.get('kind') == 'table':
                if lines[a:b + 1] != body.get('old') or any(l == '---' or (k == 0 and l.startswith('#')) for k, l in enumerate(lines[a:b + 1], a)):
                    return None, 409
                new = korrlib.make_table(lines[a:b + 1], body.get('cols', 2), bool(body.get('head')))
            elif body.get('kind') == 'heading':
                if lines[a] != body.get('old') or lines[a] == '---' or (a == 0 and lines[a].startswith('#')):
                    return None, 409
                if korrlib.table_block(lines, a):  # <h2><td>…</td></h2> wäre falsch verschachtelt
                    return None, 400
                new = [korrlib.heading(lines[a], int(body.get('level') or 0))]
                b = a
            else:
                return None, 400
            edits = [dict(line=a + k, old=lines[a + k], new=n) for k, n in enumerate(new) if n != lines[a + k]]
            return (self.edit(pg, edits) if edits else self.page_data(pg)), None

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


MARKS = {}  # Buchordner -> läuft die Nachberechnung noch? (je Programmlauf einmal)


def guess_source(folder):
    """Woher der Text eines Buchs stammt, das das noch nicht vermerkt hat: Transkribus nummeriert in lines.json
    seine Zeilen (id), die eingebaute Erkennung merkt sich statt dessen, wie sicher sie war (conf)."""
    for pg in pagexml.load_json(folder, 'lines.json', {}).values():
        for l in pg.get('lines') or []:
            return ['transkribus'] if l.get('id') else ['tesseract'] if l.get('conf') is not None else []
    return []


def ensure_marks(folder):
    """Die Kennzeichen eines Buchs: woher sein Text stammt und wie viele Wörter das Wörterbuch nicht kennt.
    Bücher von früher wissen das nicht – die Herkunft steht schnell fest, die Wörterbuchquote muss gerechnet
    werden. Sie läuft darum nebenher: Die Bibliothek erscheint sofort und holt sich die Zahl nach."""
    qj = pagexml.load_json(folder, 'qualitaet.json', {})
    if qj.get('rating'):
        if qj.get('quelle') is None:
            m = qj.get('model')
            qj['quelle'] = ([m] if m in ('textebene', 'transkribus', 'hocr') else ['tesseract']) if m else guess_source(folder)
            write_atomic(os.path.join(folder, 'qualitaet.json'), json.dumps(qj, ensure_ascii=False, indent=1))
        return qj
    quelle = qj.get('quelle') or guess_source(folder)
    if folder not in MARKS:
        MARKS[folder] = True

        def rechnen():
            try:
                ocr.rate_book(folder, quelle, quelle[0] if quelle else 'text')
            except Exception:
                pass
            finally:
                MARKS[folder] = False
        threading.Thread(target=rechnen, daemon=True).start()
    return dict(quelle=quelle, rating=None, pending=MARKS.get(folder, False))


def lib_list():
    out = []
    for e in lib_load():
        n = len(page_files(e['folder']))
        try:
            bm = json.load(open(os.path.join(e['folder'], 'lesezeichen.json'), encoding='utf-8')).get('page')
        except (OSError, ValueError):
            bm = None
        qj = ensure_marks(e['folder']) if n else {}
        q = (qj.get('rating') or {}).get('level')
        quelle = qj.get('quelle') or []
        unbekannt = (qj.get('rating') or {}).get('dict')
        try:
            with open(os.path.join(e['folder'], 'korrekturen.log'), 'rb') as f:
                corr = sum(1 for _ in f)
        except OSError:
            corr = 0
        out.append(dict(id=book_id(e['folder']), title=e.get('title') or default_title(e['folder']), folder=e['folder'],
                        pages=n, bookmark=bm, last=e.get('last', ''), quality=q, corrections=corr, quelle=quelle,
                        pending=bool(qj.get('pending')), backups=pagexml.backups(e['folder']) if n else [],
                        unknown=None if unbekannt is None else round(100 * (1 - unbekannt)),
                        images=len(glob.glob(os.path.join(e['folder'], 'img', '*.*'))), pdfdir=pdf_target(e['folder'])))
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


def new_folder(title, source, target=None):
    """(name, ordner) für ein neues Buch; vorhandene Bücher nie überschreiben."""
    name = re.sub(r'[\\/:*?"<>|]+', ' ', title or os.path.splitext(os.path.basename(source.rstrip('/\\')))[0]).strip() or 'Buch'
    base = target or os.path.join(books_dir(), name[:60].rstrip(' .'))  # kurze Ordnernamen: Windows-Pfade sind auf 260 Zeichen begrenzt
    out, n = base, 1
    while page_files(out):
        n += 1
        out = base + ' (%d)' % n
    return name, out


def import_transkribus(source, title=None, images=None, target=None):
    if not source or not os.path.exists(source):
        raise ValueError('quelle_fehlt')
    name, out = new_folder(title, source, target)
    try:
        r = pagexml.import_export(source, out, images or None)
    except ValueError:
        raise ValueError('keine_xml')
    e = lib_touch(out, title or r.get('title') or name)
    st = propose_settings(out)
    return dict(id=book_id(out), folder=out, title=e['title'], pages=r['pages'], images=r['images'], warnings=r['warnings'],
                quality=ocr.rate_book(out, ['transkribus']), **st)


def book_folder(bid):
    """Der Ordner eines Buchs aus der Bibliothek."""
    e = next((x for x in lib_load() if book_id(x['folder']) == bid), None)
    if not e or not page_files(e['folder']):
        raise ValueError('quelle_fehlt')
    return e['folder']


def copy_book(folder, title=None):
    """Ein Buch daneben anlegen: Seitenbilder, Texte und Einstellungen kommen mit. Das Protokoll und die
    Leseposition bleiben beim Original – sie gehören zu dessen Text, nicht zu dem, der gleich hineinkommt."""
    out = new_folder(title or default_title(folder), folder)[1]
    os.makedirs(out, exist_ok=True)
    for f in page_files(folder) + [os.path.join(folder, n) for n in ('lines.json', 'quellen.json', 'buch.json', 'whitelist.txt')]:
        if os.path.isfile(f):
            shutil.copyfile(f, os.path.join(out, os.path.basename(f)))
    img = os.path.join(folder, 'img')
    if os.path.isdir(img):
        shutil.copytree(img, os.path.join(out, 'img'), dirs_exist_ok=True)
    return out


def add_transkribus(bid, source, mode, progress, cancelled):
    """Den Text eines Transkribus-Exports – oder den erkannten Text einer Bibliothek (hOCR, ALTO) – in ein Buch
    übernehmen, das es schon gibt. Wer sein Buch erst als PDF
    einliest, die Seiten aufbereitet und zu Transkribus schickt, soll danach nicht wieder von vorn anfangen und
    seine Seitenbilder suchen müssen – sie liegen ja längst hier.

    mode='new' legt statt dessen ein zweites Buch daneben an: erst eine Kopie samt Seitenbildern, dann derselbe
    Weg hinein. So bleibt das Original mit seinen Korrekturen unangetastet, und die Bilder sind trotzdem dabei."""
    folder = book_folder(bid)
    if not source or not os.path.exists(source):
        raise ValueError('quelle_fehlt')
    e = next((x for x in lib_load() if book_id(x['folder']) == bid), None)
    alt = [q for q in (pagexml.load_json(folder, 'qualitaet.json', {}).get('quelle') or []) if q not in ('transkribus', 'hocr')]
    ziel = copy_book(folder, e.get('title') if e else None) if mode == 'new' else folder
    try:
        r = pagexml.import_into(source, ziel, progress, save=ziel == folder)
    except Exception:
        if ziel != folder:
            shutil.rmtree(ziel, ignore_errors=True)  # nichts Halbfertiges stehen lassen
        raise
    with LIBLOCK:
        BOOKS.pop(book_id(ziel), None)  # der Text auf der Platte ist ein anderer geworden
    lib_touch(ziel, e.get('title') if e and ziel != folder else None)
    art = 'hocr' if r.get('extern') else 'transkribus'  # hOCR/ALTO einer Bibliothek oder Transkribus
    return dict(id=book_id(ziel), folder=ziel, neu=ziel != folder, quality=ocr.rate_book(ziel, alt + [art], art), **r)


def add_images(bid, source, progress, cancelled):
    """Seitenbilder zu einem Buch legen, das keine hat (Transkribus-Export ohne Bilder)."""
    folder = book_folder(bid)
    if not source or not os.path.exists(source):
        raise ValueError('quelle_fehlt')
    r = ocr.add_images(folder, source, progress)
    with LIBLOCK:
        BOOKS.pop(bid, None)
    lib_touch(folder)
    return dict(id=bid, folder=folder, **r)


def restore(bid, name):
    """Eine frühere Fassung eines Buchs zurückholen – das Gegenstück zum Ersetzen des Textes."""
    folder = book_folder(bid)
    r = pagexml.restore(folder, name)
    with LIBLOCK:
        BOOKS.pop(bid, None)
    lib_touch(folder)
    return dict(id=bid, folder=folder, **r)


def prepare(bid, tool):
    """Sagt, welcher Ordner in ScanTailor bzw. zu Transkribus gehört, und macht ihn greifbar: in der
    Zwischenablage und im Dateimanager geöffnet. Niemand soll sich einen Pfad merken oder abtippen müssen."""
    folder = book_folder(bid)
    img = os.path.join(folder, 'img')
    if not glob.glob(os.path.join(img, '*.*')):
        raise ValueError('keine_bilder')
    exe = out = None
    if tool == 'scantailor':
        exe = ocr.find_scantailor()
        if not exe:
            raise ValueError('kein_scantailor')
        out = os.path.join(folder, 'scantailor', 'out')
        os.makedirs(out, exist_ok=True)
    clip = ocr.to_clipboard(img)
    ocr.reveal(img)
    if exe:
        ocr.launch(exe)
    return dict(folder=img, out=out, clipboard=clip, pages=len(glob.glob(os.path.join(img, '*.*'))))


def import_ocr(source, title, target, script, textlayer, progress, cancelled):
    """PDF oder Bilderordner mit Tesseract einlesen (läuft als Auftrag im Hintergrund)."""
    if not source or not os.path.exists(source):
        raise ValueError('quelle_fehlt')
    src = source.rstrip('/\\')
    if os.path.isdir(src) and os.path.basename(src).lower() == 'out' and not title:
        title = os.path.basename(os.path.dirname(os.path.dirname(src)))  # …/<Titel>/scantailor/out
    name, out = new_folder(title, source, target)
    try:
        r = ocr.build(source, out, progress, cancelled, 'antiqua' if script == 'antiqua' else 'fraktur', bool(textlayer))
    except ValueError:
        raise
    except Exception:
        ocr.cleanup(out)
        raise
    e = lib_touch(out, title or name)
    st = propose_settings(out)
    # images: für den Weg zu Transkribus – dort werden die aufbereiteten Seitenbilder hochgeladen
    return dict(id=book_id(out), folder=out, images=os.path.join(out, 'img'), title=e['title'],
                pages=r['pages'], quality=r['quality'], **st)


def import_epub(source, pdf, title, target, script, textlayer, progress, cancelled):
    """EPUB einlesen. Mit gleichlautendem PDF: Seitenbilder und Zeilen aus dem PDF, Wortlaut aus dem EPUB; sonst Textbuch."""
    if not source or not os.path.isfile(source):
        raise ValueError('quelle_fehlt')
    try:
        etitle = epub.read(source)[0]
    except Exception:
        raise ValueError('kein_epub')
    name, out = new_folder(title or etitle, source, target)
    try:
        if pdf and os.path.isfile(pdf):
            r = ocr.build(pdf, out, progress, cancelled, 'antiqua' if script == 'antiqua' else 'fraktur', bool(textlayer))
            m = epub.transplant(source, out, progress)
            r = dict(pages=r['pages'], quality=r['quality'], matched=m['matched'])
        else:
            r = epub.text_book(source, out)
    except ValueError:
        raise
    except Exception:
        ocr.cleanup(out)
        raise
    e = lib_touch(out, title or etitle or name)
    st = propose_settings(out)
    return dict(id=book_id(out), folder=out, title=e['title'], **{k: r.get(k) for k in ('pages', 'quality', 'matched')}, **st)


def discard(bid):
    """Ein eben eingelesenes Buch wieder entfernen (der Nutzer lässt den Text neu erkennen). Nur Bücher, die das Programm
    selbst eingelesen hat (qualitaet.json) und in denen noch keine Arbeit steckt – sonst bleibt alles, wie es ist."""
    e = next((x for x in lib_load() if book_id(x['folder']) == bid), None)
    if not e:
        raise ValueError('quelle_fehlt')
    f = e['folder']
    if not os.path.exists(os.path.join(f, 'qualitaet.json')) or any(os.path.exists(os.path.join(f, n)) for n in ('korrekturen.log', 'whitelist.txt')):
        raise ValueError('hat_arbeit')
    lib_forget(bid)
    for n in ('lesezeichen.json', 'buch.json'):
        try: os.remove(os.path.join(f, n))
        except OSError: pass
    ocr.cleanup(f)


def pdf_target(folder):
    """Wohin ein gesichertes PDF vorgeschlagen wird: neben den Buchordner – bei …/<Titel>/ocr/korr neben <Titel>."""
    t = os.path.abspath(folder)
    while os.path.basename(t).lower() in ('korr', 'ocr'):
        t = os.path.dirname(t)
    return os.path.dirname(t)


def export_pdf(bid, target, progress, cancelled):
    """Ein Buch als PDF sichern (#58): Seitenbilder, unsichtbare Textebene, Arbeitsstand als Anhang. Läuft als Auftrag.
    Ein PDF, das dieses Programm von demselben Buch geschrieben hat, wird ersetzt – alles andere bekommt »(2)«."""
    folder = book_folder(bid)
    book = get_book(bid)
    with book.lock:
        if not book.settings.get('kennung'):
            book.settings['kennung'] = uuid.uuid4().hex
            book.save_settings()
    target = target or pdf_target(folder)
    if not os.path.isdir(target):
        raise ValueError('kein_ordner')
    name = re.sub(r'[\\/:*?"<>|]+', ' ', book.title).strip()[:80].rstrip(' .') or 'Buch'
    out, n = os.path.join(target, name + '.pdf'), 1
    while os.path.exists(out) and (pdfbuch.info(out) or {}).get('kennung') != book.settings['kennung']:
        n += 1
        out = os.path.join(target, '%s (%d).pdf' % (name, n))
    r = pdfbuch.save(book, out, version(), progress, cancelled)
    lib_touch(folder)
    return dict(id=bid, folder=target, **r)


def import_pdfbuch(source, title, target, progress, cancelled):
    """Ein mit diesem Programm gesichertes PDF wieder als Buch anlegen (läuft als Auftrag im Hintergrund)."""
    if not source or not os.path.isfile(source):
        raise ValueError('quelle_fehlt')
    m = pdfbuch.info(source)
    if not m:
        raise ValueError('kein_pdfbuch')
    name, out = new_folder(title or m.get('titel'), source, target)
    try:
        r = pdfbuch.load(source, out, progress, cancelled)
    except Exception:
        shutil.rmtree(out, ignore_errors=True)  # nichts Halbfertiges stehen lassen
        raise
    e = lib_touch(out, title or r['title'] or name)
    st = Book(out).settings  # buch.json kam mit; fehlt sie (sehr altes Buch), wird sie hier vorgeschlagen
    try:
        bm = json.load(open(os.path.join(out, 'lesezeichen.json'), encoding='utf-8')).get('page')
    except (OSError, ValueError):
        bm = None
    return dict(id=book_id(out), folder=out, title=e['title'], pages=r['pages'], images=r['images'], corrections=r['corrections'],
                saved=r['saved'], bookmark=bm, quality=None, year=st.get('year'), dics=st.get('dics'))


def scan(path):
    """finder.scan, ergänzt um das, was nur der Server weiß: Steht der Fund schon in der Bibliothek?"""
    r = finder.scan(path)
    lib = lib_load()
    known = {book_id(x['folder']) for x in lib}
    kennungen = {pagexml.load_json(x['folder'], 'buch.json', {}).get('kennung') for x in lib} - {None}
    for f in r['found']:
        if f['kind'] == 'book':
            f['id'] = book_id(f['path'])
            f['known'] = f['id'] in known
        elif f['kind'] == 'pdfbuch':  # dasselbe Buch liegt schon in der Bibliothek (von hier gesichert oder schon einmal eingelesen)
            f['known'] = bool(f.get('kennung')) and f['kennung'] in kennungen
    return r


def scantailor(source, title, progress, cancelled):
    """PDF-Seiten als Bilder in <Buchordner>/scantailor ablegen und ScanTailor starten (ohne PDF: nur starten)."""
    exe = ocr.find_scantailor()
    if not exe:
        raise ValueError('kein_scantailor')
    folder = None
    if source:
        if not (os.path.isfile(source) and source.lower().endswith('.pdf')):
            raise ValueError('nur_pdf')
        folder = os.path.join(new_folder(title, source)[1], 'scantailor')
        try:
            ocr.export_pages(source, folder, progress, cancelled)
        except ImportError:
            raise ValueError('kein_pymupdf')
    # Der Hinweis im Browser verschwindet hinter ScanTailor, darum den Ordner greifbar machen:
    # in die Zwischenablage und im Dateimanager geöffnet, von wo er sich hineinziehen lässt.
    clip = bool(folder) and ocr.to_clipboard(folder)
    if folder:
        ocr.reveal(folder)
    ocr.launch(exe)
    return dict(folder=folder, out=os.path.join(folder, 'out') if folder else None, clipboard=clip)


def open_obsidian(path):
    """Die neue Notiz in Obsidian zeigen. Obsidian meldet beim System die Adresse obsidian://…; liegt die Datei in einem
    Vault, den Obsidian kennt, öffnet es sie dort. Ohne Obsidian bleibt die Datei einfach im Ordner."""
    try:
        ok = bool(webbrowser.open('obsidian://open?path=' + urllib.parse.quote(path)))
    except Exception:
        return False
    if ok and sys.platform == 'win32':
        threading.Thread(target=raise_window, args=('obsidian.exe',), daemon=True).start()
    return ok


def raise_window(exe, wait=6.0):
    """Das Fenster eines Programms nach vorn holen (Windows). Der Server läuft im Hintergrund, und Windows lässt ein von dort
    gestartetes Programm sonst nur in der Taskleiste blinken."""
    import ctypes
    from ctypes import wintypes
    u, k = ctypes.windll.user32, ctypes.windll.kernel32
    k.OpenProcess.restype = wintypes.HANDLE
    k.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    k.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
    k.CloseHandle.argtypes = [wintypes.HANDLE]
    found = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def each(hwnd, _):
        if u.IsWindowVisible(hwnd) and u.GetWindowTextLengthW(hwnd):
            pid = wintypes.DWORD()
            u.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            h = k.OpenProcess(0x1000, False, pid.value)  # PROCESS_QUERY_LIMITED_INFORMATION
            if h:
                buf, n = ctypes.create_unicode_buffer(1024), wintypes.DWORD(1024)
                if k.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(n)) and os.path.basename(buf.value).lower() == exe:
                    found.append(hwnd)
                k.CloseHandle(h)
        return True

    end = time.time() + wait
    while time.time() < end:  # Obsidian startet vielleicht erst
        time.sleep(0.3)
        del found[:]
        u.EnumWindows(each, 0)
        if found:
            hwnd = found[0]  # EnumWindows liefert von vorn nach hinten: das zuletzt benutzte Fenster
            if u.IsIconic(hwnd):
                u.ShowWindow(hwnd, 9)  # SW_RESTORE
            fg = u.GetForegroundWindow()
            if fg != hwnd:  # an den Eingabestrang des vorderen Fensters (Browser) hängen: dann gilt der Wechsel als erlaubt
                t1, t2 = u.GetWindowThreadProcessId(fg, None), k.GetCurrentThreadId()
                u.AttachThreadInput(t2, t1, True)
                u.BringWindowToTop(hwnd)
                u.SetForegroundWindow(hwnd)
                u.AttachThreadInput(t2, t1, False)
            if u.GetForegroundWindow() != hwnd:  # Rückfall: ein leerer Alt-Tastendruck hebt die Sperre auf
                u.keybd_event(0x12, 0, 0, 0)
                u.keybd_event(0x12, 0, 2, 0)
                u.SetForegroundWindow(hwnd)
            return u.GetForegroundWindow() == hwnd
    return False


# ---- Aufträge: lange Arbeiten im Hintergrund, der Browser fragt den Fortschritt ab

JOBS = {}


def start_job(fn, *args):
    jid = uuid.uuid4().hex[:8]
    j = JOBS[jid] = dict(state='running', done=0, total=0, msg='', cancel=False, result=None, error=None)

    def progress(done, total, msg):
        j.update(done=done, total=total, msg=msg)

    def run():
        try:
            j['result'] = fn(*args, progress, lambda: j['cancel'])
            j['state'] = 'done'
        except ValueError as e:
            j.update(state='error', error=str(e))
        except Exception as e:
            j.update(state='error', error='unknown', detail=repr(e))
    threading.Thread(target=run, daemon=True).start()
    return jid


# Dateitypen des Mac-Dialogs als UTI; "any" muss alles zeigen, was finder.py erkennt.
UTI = dict(pdf=['com.adobe.pdf'], zip=['public.zip-archive'],
           export=['public.zip-archive', 'public.plain-text', 'public.xml'],
           any=['com.adobe.pdf', 'org.idpf.epub-container', 'public.zip-archive', 'public.xml', 'public.plain-text',
                'public.jpeg', 'public.png', 'public.tiff'])
PROMPT = dict(folder='Ordner wählen', pdf='PDF wählen', exe='Programm wählen', zip='Transkribus-Export (ZIP) wählen',
              export='Transkribus-Export wählen (ZIP, Text oder XML)')


def mac_dialog(kind):
    """Auswahldialog über osascript: eine Mac-App bringt kein Tk mit, und dies ist der gewohnte Finder-Dialog."""
    what = dict(folder='choose folder', exe='choose application as alias').get(kind, 'choose file')
    types = '' if kind in ('folder', 'exe') else ' of type {%s}' % ', '.join('"%s"' % t for t in UTI.get(kind, UTI['any']))
    prompt = ' with prompt "%s"' % PROMPT.get(kind, 'Datei oder Ordner wählen')
    for script in (what + prompt + types, what + prompt):  # ohne Typfilter noch einmal, falls eine UTI unbekannt ist
        r = subprocess.run(['osascript', '-e', 'POSIX path of (%s)' % script], capture_output=True, timeout=900)
        if r.returncode == 0:
            p = r.stdout.decode('utf-8').strip()
            return ocr.app_binary(p) if kind == 'exe' else p  # gewählt wird ein Bündel, gebraucht die Datei darin
        if b'-128' in r.stderr:  # abgebrochen
            return ''
    return ''


def dialog(kind, out=None):
    """Auswahldialog mit tkinter (Windows, Linux); läuft als eigener Prozess, weil tkinter den Hauptthread braucht.
    Das Ergebnis geht in eine Datei, denn die gepackte App hat keine Standardausgabe."""
    import tkinter
    from tkinter import filedialog
    root = tkinter.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    p = filedialog.askdirectory(parent=root) if kind == 'folder' else \
        filedialog.askopenfilename(parent=root, filetypes=dict(pdf=[('PDF', '*.pdf')], exe=[('*', '*.*')], any=[
            ('PDF, EPUB, ZIP, Bilder, Buchseiten', '*.pdf *.epub *.zip *.xml *.txt *.jpg *.jpeg *.png *.tif *.tiff'), ('*', '*.*')],
            export=[('Transkribus-Export, hOCR, ALTO', '*.zip *.txt *.xml *.html *.htm *.hocr *.alto'), ('*', '*.*')]).get(kind, [('ZIP', '*.zip'), ('*', '*.*')]))
    if out:
        with open(out, 'w', encoding='utf-8') as f:
            f.write(p or '')
    else:
        sys.stdout.buffer.write((p or '').encode('utf-8'))


def choose(kind):
    if sys.platform == 'darwin':
        try:
            return mac_dialog(kind)
        except (OSError, subprocess.TimeoutExpired):
            return ''
    out = os.path.join(tempfile.gettempdir(), 'fraktur-dialog-%s.txt' % uuid.uuid4().hex[:8])
    cmd = [sys.executable] + ([] if getattr(sys, 'frozen', False) else [os.path.abspath(__file__)]) + ['--dialog', kind, out]
    try:
        subprocess.run(cmd, capture_output=True, timeout=900)
        with open(out, encoding='utf-8') as f:
            return f.read().strip()
    except (OSError, subprocess.TimeoutExpired):
        return ''
    finally:
        try:
            os.remove(out)
        except OSError:
            pass


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
th{background:#f6f3ea} td:first-child{white-space:nowrap} code,kbd{background:#eee;border:1px solid #ccc;border-radius:3px;padding:0 4px;font-family:Consolas,monospace;font-size:.9em}
pre{background:#f4f4f4;padding:10px;overflow:auto} pre code{border:0;padding:0} h1{margin-top:.6em}
</style></head><body><div id="top"><b>Fraktur-Korrektor</b><a href="/">%(home)s</a><span class="sp"></span>%(langs)s</div>
<div id="wrap"><nav>%(nav)s</nav><main>%(body)s</main></div></body></html>'''


HELP_ORDER = ['index', 'add-book', 'pdf-import', 'transkribus', 'usage', 'pdf-sichern', 'install', 'install-tools']


def help_pages(lang):
    """[(name, titel)] – index zuerst, Titel ist die erste Überschrift."""
    out = []
    for f in sorted(glob.glob(os.path.join(HERE, 'docs', lang, '*.md'))):
        m = re.search(r'^#\s+(.+)$', open(f, encoding='utf-8').read(), re.M)
        out.append((os.path.basename(f)[:-3], m.group(1).strip() if m else os.path.basename(f)[:-3]))
    out.sort(key=lambda x: HELP_ORDER.index(x[0]) if x[0] in HELP_ORDER else len(HELP_ORDER))
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
        if u.path == '/api/ping':
            return self.sendjson(dict(app='fraktur-korrektor', version=version()))  # daran erkennt der Starter eine laufende Instanz
        if u.path == '/api/tools':
            return self.sendjson(ocr.tools())
        m = re.fullmatch(r'/api/job/([0-9a-f]{8})', u.path)
        if m:
            j = JOBS.get(m.group(1))
            return self.sendjson({k: v for k, v in j.items() if k != 'cancel'}) if j else self.send(404, '{}')
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
            # images/local: die Leseansicht bietet an, Seitenbilder oder einen Transkribus-Text nachzulegen
            r = dict(title=book.title, pages=book.overview(), id=book.id, local=self.local(),
                     images=len(glob.glob(os.path.join(book.imgdir, '*.*'))))
            korrlib.save_cache()
            return self.sendjson(r)
        if rest == '/api/progress':  # ohne Sperre: der Ladebalken fragt, während overview() die Sperre hält
            p = book.prog
            return self.sendjson(dict(done=p[0], total=p[1]) if p else dict(done=1, total=1))
        if rest == '/api/settings':
            return self.sendjson(book.settings)
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
        if rest == '/api/search':
            qs = q.get('q', [''])[0]
            items = book.search(qs) if qs.strip() else []
            return self.sendjson(dict(q=qs, n=len(items), items=items))
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
        m = re.fullmatch(r'/api/job/([0-9a-f]{8})/cancel', u.path)
        if m and m.group(1) in JOBS and self.local():
            JOBS[m.group(1)]['cancel'] = True
            return self.sendjson({})
        if u.path in ('/api/choose', '/api/open', '/api/import_transkribus', '/api/import_ocr', '/api/import_epub', '/api/scan', '/api/discard', '/api/pdf_info', '/api/scantailor', '/api/set_tool', '/api/forget', '/api/reveal', '/api/add_transkribus', '/api/add_images', '/api/prepare', '/api/restore', '/api/export_pdf', '/api/import_pdfbuch'):
            if not self.local():
                return self.sendjson(dict(error='nur_lokal'), 403)
            if u.path == '/api/choose':
                return self.sendjson(dict(path=choose(body.get('kind') if body.get('kind') in ('folder', 'pdf', 'exe', 'any') else 'zip')))
            if u.path == '/api/reveal':
                # Ordner im Dateifenster zeigen und den Pfad in die Zwischenablage – zum Hochladen bei Transkribus
                p = body.get('path') or ''
                if not os.path.isdir(p):
                    return self.sendjson(dict(error='quelle_fehlt'), 400)
                return self.sendjson(dict(clipboard=ocr.to_clipboard(p), shown=ocr.reveal(p)))
            if u.path == '/api/set_tool':
                if body.get('tool') not in ('tesseract', 'scantailor') or not os.path.isfile(body.get('path') or ''):
                    return self.sendjson(dict(error='quelle_fehlt'), 400)
                korrlib.set_config(body['tool'], body['path'])
                return self.sendjson(ocr.tools())
            if u.path == '/api/discard':
                try:
                    discard(body.get('id'))
                    return self.sendjson({})
                except ValueError as e:
                    return self.sendjson(dict(error=str(e)), 400)
            if u.path == '/api/scan':
                try:
                    return self.sendjson(scan(body.get('path') or ''))
                except ValueError as e:
                    return self.sendjson(dict(error=str(e)), 400)
            if u.path == '/api/import_epub':
                return self.sendjson(dict(job=start_job(import_epub, body.get('source'), body.get('pdf'), body.get('title'), body.get('target'),
                                                        body.get('script'), body.get('textlayer'))))
            if u.path == '/api/pdf_info':
                src = body.get('source') or ''
                try:
                    ok = os.path.isfile(src) and src.lower().endswith('.pdf')
                    return self.sendjson(dict(pages=ocr.pdf_count(src), text=ocr.pdf_has_text(src)) if ok else dict(pages=0, text=False))
                except Exception:
                    return self.sendjson(dict(pages=0, text=False))
            if u.path == '/api/add_transkribus':
                return self.sendjson(dict(job=start_job(add_transkribus, body.get('id'), body.get('source'), body.get('mode'))))
            if u.path == '/api/add_images':
                return self.sendjson(dict(job=start_job(add_images, body.get('id'), body.get('source'))))
            if u.path == '/api/export_pdf':
                if not get_book(body.get('id') or ''):
                    return self.sendjson(dict(error='quelle_fehlt'), 400)
                return self.sendjson(dict(job=start_job(export_pdf, body['id'], (body.get('target') or '').strip())))
            if u.path == '/api/import_pdfbuch':
                return self.sendjson(dict(job=start_job(import_pdfbuch, body.get('source'), body.get('title'), body.get('target'))))
            if u.path == '/api/restore':
                try:
                    return self.sendjson(restore(body.get('id'), body.get('name')))
                except ValueError as e:
                    return self.sendjson(dict(error=str(e)), 400)
            if u.path == '/api/prepare':
                try:
                    return self.sendjson(prepare(body.get('id'), body.get('tool')))
                except ValueError as e:
                    return self.sendjson(dict(error=str(e)), 400)
            if u.path == '/api/import_ocr':
                return self.sendjson(dict(job=start_job(import_ocr, body.get('source'), body.get('title'), body.get('target'), body.get('script'), body.get('textlayer'))))
            if u.path == '/api/scantailor':
                return self.sendjson(dict(job=start_job(scantailor, body.get('source'), body.get('title'))))
            if u.path == '/api/forget':
                lib_forget(body.get('id'))
                return self.sendjson({})
            if u.path == '/api/open':
                f = find_book_folder(body.get('folder') or '')
                if not f:
                    return self.sendjson(dict(error='kein_buch'), 400)
                lib_touch(f)
                return self.sendjson(dict(id=book_id(f)))
            if body.get('job'):
                return self.sendjson(dict(job=start_job(lambda progress, cancelled: import_transkribus(
                    body.get('source'), body.get('title'), body.get('images'), body.get('target')))))
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
        m = re.fullmatch(r'/api/lines/(\d{3})', rest)
        if m:
            try:
                if body.get('kind') == 'split':
                    r, err = book.split_line(m.group(1), body.get('line', -1), body.get('old'), body.get('text') or '', int(body.get('pos') or 0))
                else:
                    r, err = book.join_lines(m.group(1), body.get('line', -1), body.get('old'))
            except KeyError:
                return self.send(404, '{}')
            return self.sendjson(r) if r else self.send(err or 409, '{}')
        m = re.fullmatch(r'/api/markup/(\d{3})', rest)
        if m:
            try:
                r, err = book.markup(m.group(1), body)
            except KeyError:
                return self.send(404, '{}')
            return self.sendjson(r) if r else self.send(err or 409, '{}')
        m = re.fullmatch(r'/api/fnsep/(\d{3})', rest)
        if m:
            r = book.fnsep(m.group(1), body['line'], body['old'])
            return self.sendjson(r) if r else self.send(409, '{}')
        if rest == '/api/series':
            if not body.get('word') or not body.get('new') or re.search(r'\s', body['new']):
                return self.send(400, '{}')
            return self.sendjson(book.series_replace(body['word'], body['new'], body.get('items', [])))
        if rest == '/api/settings':
            if 'notizen' in body:  # Notizordner festlegen: schreibt später außerhalb des Buchs, darum nur am Rechner selbst
                if not self.local():
                    return self.sendjson(dict(error='nur_lokal'), 403)
                return self.sendjson(book.set_notes((body.get('notizen') or '').strip()))
            st = book.set_dics(body.get('dics') or [])
            total = sum(o['n'] for o in book.overview())
            korrlib.save_cache()
            return self.sendjson(dict(st, total=total))
        if rest == '/api/notiz':
            r, err = book.make_note(str(body.get('page') or ''), body.get('text') or '', body.get('lang') or 'de', body.get('lines'))
            if err:
                return self.sendjson(dict(error=err), 400)
            r['opened'] = bool(body.get('open')) and self.local() and open_obsidian(r['file'])
            return self.sendjson(r)
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


def parse_args(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('folder', nargs='?', help='Buchordner; ohne Angabe erscheint die Bibliothek')
    ap.add_argument('--port', type=int, default=8765)
    ap.add_argument('--dic')
    ap.add_argument('--title')
    ap.add_argument('--no-browser', action='store_true')
    ap.add_argument('--lan', action='store_true', help='auch für andere Rechner im lokalen Netz erreichbar (kein Passwortschutz!)')
    return ap.parse_args(argv)


def setup(A):
    """Wörterbuch wählen, Port belegen, ein Buch von der Kommandozeile laden; liefert (Server, Adresse).
    Ist der Port belegt, kommt OSError durch – der Starter der gepackten App öffnet dann die laufende Instanz."""
    global DEFAULT
    if A.dic:
        korrlib.set_dic(A.dic)
    korrlib.warm()  # bei gefülltem Zwischenspeicher braucht das Öffnen das Wörterbuch nicht – aber ein neues Wort soll nicht warten
    httpd = Server(('0.0.0.0' if A.lan else '127.0.0.1', A.port), H)
    if A.folder:
        f = find_book_folder(A.folder)
        if not f:
            sys.exit('Kein Buchordner: in %s liegen keine Seitendateien (001.txt, 002.txt, …).' % os.path.abspath(A.folder))
        lib_touch(f, A.title)
        DEFAULT = book_id(f)
        print('Lade Wörterbuch und Seiten …')
        get_book(DEFAULT).overview()
        korrlib.save_cache()
    return httpd, 'http://localhost:%d' % A.port


def main(argv=None):
    A = parse_args(argv)
    try:
        httpd, url = setup(A)
    except OSError:
        sys.exit('Port %d ist belegt – läuft der Fraktur-Korrektor schon? Sonst mit --port <nummer> einen anderen Port wählen.' % A.port)
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
    if len(sys.argv) >= 3 and sys.argv[1] == '--dialog':
        dialog(*sys.argv[2:4])
    else:
        main()
