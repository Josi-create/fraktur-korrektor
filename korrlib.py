"""Gemeinsames: Wörterbücher (Hunspell via spylls), Korpusfrequenz, Tokenisierung.

Welche Rechtschreibung gilt, ist je Buch wählbar (DICS):
  1901     Rechtschreibung 1901–1996 (daß, Schiffahrt) – mitgeliefert: dict/de_DE_OLDSPELL. Ein anderes Wörterbuch an dieser
           Stelle: set_dic(pfad) bzw. --dic, Umgebungsvariable FRAKTUR_DIC, "dic" in ~/.fraktur-korrektor/config.json
  neu      neue Rechtschreibung ab 1996 (dass, Schifffahrt) – mitgeliefert: dict/de_DE_frami
  vor1901  kein Wörterbuch, sondern Regeln: Thür, seyn, Noth, civilisiren gelten, wenn die heutige Form bekannt ist
dict/zusatz.txt: zusätzlich gültige Wörter (Abkürzungen); dict/fallen.txt: nie gültig, weil fast immer OCR-Fehler (baß)."""
import os, re, sys, glob, json, atexit, hashlib, collections, functools, itertools, threading
from spylls.hunspell import Dictionary
HERE = getattr(sys, '_MEIPASS', None) or os.path.dirname(os.path.abspath(__file__))  # gepackt liegt dict/ im Bundle
HOME = os.environ.get('FRAKTUR_HOME') or os.path.join(os.path.expanduser('~'), '.fraktur-korrektor')
WORD = re.compile(r"[A-Za-zÄÖÜäöüß]+")
DICS = ('1901', 'neu', 'vor1901')
DEFAULT = ('1901',)
DIC = None
def config():
    p = os.path.join(HOME, 'config.json')
    try: return json.load(open(p, encoding='utf-8'))
    except OSError: return {}
    except ValueError as e:
        print('Warnung: %s ist kein gültiges JSON und wird ignoriert (%s)' % (p, e))
        return {}
def set_config(key, value):
    c = config(); c[key] = value
    os.makedirs(HOME, exist_ok=True)
    with open(os.path.join(HOME, 'config.json'), 'w', encoding='utf-8') as f:
        json.dump(c, f, ensure_ascii=False, indent=2)
def _base(path):
    return path[:-4] if path.lower().endswith(('.dic', '.aff')) else path
def find_dic():
    """Wörterbuch für '1901': erster Kandidat, zu dem .dic und .aff existieren; sonst Abbruch mit verständlicher Meldung."""
    cand = [DIC, os.environ.get('FRAKTUR_DIC'), config().get('dic'), os.path.join(HERE, 'dict', 'de_DE_OLDSPELL', 'de_DE_OLDSPELL')]
    cand = [_base(c) for c in cand if c]
    for c in cand:
        if os.path.exists(c + '.dic') and os.path.exists(c + '.aff'):
            return c
    raise SystemExit('Kein Wörterbuch gefunden. Gesucht wurde (jeweils .dic und .aff):\n  ' + '\n  '.join(cand) +
                     '\nAbhilfe: den Ordner dict/ des Programms wiederherstellen oder ein Hunspell-Wörterbuch mit --dic <pfad> angeben.')
class Checker:
    """Ein Hunspell-Wörterbuch mit Zwischenspeicher der Prüfergebnisse auf der Platte (die freien Wörterbücher prüfen langsam).
    Das Wörterbuch selbst wird erst eingelesen, wenn ein Wort nicht im Zwischenspeicher steht: spylls braucht dafür mehrere
    Sekunden, und bei einem Buch, das schon einmal offen war, kommt es meist gar nicht dazu (warm() holt es im Hintergrund)."""
    def __init__(self, path):
        self.path, self.d, self.cache, self.lock = path, None, {}, threading.Lock()
        key = '|'.join([self.path] + [str(os.path.getmtime(self.path + e)) for e in ('.dic', '.aff')])
        self.cache_path = os.path.join(HOME, 'cache', hashlib.md5(key.encode('utf-8')).hexdigest() + '.json')
        try: self.cache.update(json.load(open(self.cache_path, encoding='utf-8')))
        except (OSError, ValueError): pass
        self.n = len(self.cache)
    def load(self):
        with self.lock:  # zwei Anfragen zugleich sollen das Wörterbuch nicht zweimal einlesen
            if self.d is None:
                self.d = Dictionary.from_files(self.path)
        return self.d
    def lookup(self, w):
        if w not in self.cache:
            d = self.d or self.load()
            if w not in self.cache:
                # auch klein (Satzanfang) und groß (Substantivierung) – aber jede Schreibweise nur einmal: Fehlversuche sind teuer
                self.cache[w] = any(d.lookup(v) for v in dict.fromkeys((w, w.lower(), w[0].upper() + w[1:])))
        return self.cache[w]
    def save(self):
        # Ein Hintergrundauftrag und eine Anfrage des Browsers speichern sonst zugleich über dieselbe .tmp-Datei, und wer
        # zuletzt umbenennt, findet sie nicht mehr. Eigene Sperre: self.lock hält load() sekundenlang.
        with _savelock:
            if self.cache_path and len(self.cache) > self.n:
                os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
                stand = dict(self.cache)  # lookup() trägt währenddessen weiter ein
                with open(self.cache_path + '.tmp', 'w', encoding='utf-8') as f:
                    json.dump(stand, f, ensure_ascii=False)
                os.replace(self.cache_path + '.tmp', self.cache_path)
                self.n = len(stand)
_checkers, _savelock, _newlock = {}, threading.Lock(), threading.Lock()
def checker(name='1901'):
    if name not in _checkers:
        with _newlock:  # zwei Threads zugleich sollen nicht zwei Wörterbücher anlegen (und beide einlesen)
            if name not in _checkers:
                _checkers[name] = Checker(find_dic() if name == '1901' else os.path.join(HERE, 'dict', 'de_DE_frami', 'de_DE_frami'))
    return _checkers[name]
def warm(name='1901'):
    """Das Wörterbuch im Hintergrund einlesen, damit das erste unbekannte Wort später nicht darauf warten muss."""
    threading.Thread(target=lambda: checker(name).load(), daemon=True).start()
def set_dic(path):
    global DIC
    DIC = _base(path)
    _checkers.pop('1901', None); in_dict.cache_clear()
def save_cache():
    for c in list(_checkers.values()): c.save()
atexit.register(save_cache)
def _wordlist(name):
    p = os.path.join(HERE, 'dict', name)
    return {w for l in open(p, encoding='utf-8') if not l.startswith('#') for w in l.split()} if os.path.exists(p) else set()
ZUSATZ, FALLEN = _wordlist('zusatz.txt'), _wordlist('fallen.txt')
# Schreibungen vor 1901 -> heutige Form; jede Regel einzeln und alle zusammen werden versucht
OLD = [(r'th', 't'), (r'Th', 'T'), (r'(?<=[ae])y', 'i'), (r'ir(?=en$|t$|te$|ten$|ung$|ungen$)', 'ier'), (r'c(?=[aou])', 'k'), (r'C(?=[aou])', 'K'),
       (r'c(?=[eiä])', 'z'), (r'C(?=[eiä])', 'Z'), (r'ct', 'kt'), (r'aa', 'a'), (r'oo', 'o'), (r'dt$', 't'), (r'(?<=[a-zäöü])d$', 't'),
       (r'ie(?=bt|ng)', 'i'), (r'ß$', 's'), (r'et$', 't'), (r'eten$', 'ten')]
OLD = [(re.compile(a), b) for a, b in OLD]
def modern(w):
    """Mögliche heutige Formen einer alten Schreibung: Thür -> Tür, seyn -> sein, Noth -> Not, civilisiren -> zivilisieren."""
    one = {r.sub(b, w) for r, b in OLD} - {w}
    allr = w
    for r, b in OLD[:10]: allr = r.sub(b, allr)
    two = {r.sub(b, v) for v in one for r, b in OLD[:10]}
    return (one | two | {allr}) - {w}
@functools.lru_cache(maxsize=None)
def in_dict(w, dics=DEFAULT):
    if len(w) <= 1 or w in ZUSATZ: return True
    if w in FALLEN: return False
    real = [d for d in dics if d != 'vor1901'] or ['1901']
    if any(checker(d).lookup(w) for d in real): return True
    return 'vor1901' in dics and len(w) > 2 and any(checker(d).lookup(v) for v in modern(w) for d in real)
# ---- Korrekturvorschläge (#41). Erst das Billige: Was die Fraktur-OCR typischerweise verwechselt (b/d, f/s, n/u, r/t,
# ll/tt, fehlende Umlautpunkte), an jeder Stelle des Wortes einmal getauscht und nachgesehen, ob das ein Wort ergibt.
# Hunspell selbst erst danach: spylls braucht dafür Sekunden, darum mit Zeitbudget.
CONFUSIONS = [('b', 'd'), ('d', 'b'), ('f', 's'), ('s', 'f'), ('n', 'u'), ('u', 'n'), ('r', 't'), ('t', 'r'), ('t', 'k'), ('k', 't'),
              ('l', 'i'), ('i', 'l'), ('c', 'e'), ('e', 'c'), ('o', 'v'), ('v', 'o'), ('h', 'b'), ('b', 'h'), ('ll', 'tt'), ('tt', 'll'),
              ('rn', 'm'), ('m', 'rn'), ('in', 'm'), ('ii', 'n'), ('ck', 'd'), ('a', 'ä'), ('o', 'ö'), ('u', 'ü'), ('ä', 'a'), ('ö', 'o'),
              ('ü', 'u'), ('ß', 'ss'), ('ss', 'ß'), ('B', 'V'), ('V', 'B'), ('R', 'N'), ('N', 'R'), ('S', 'G'), ('G', 'S'), ('J', 'I'),
              ('I', 'J'), ('C', 'E'), ('E', 'C'), ('D', 'O'), ('O', 'D'), ('K', 'R'), ('R', 'K'), ('Z', 'B'), ('B', 'Z'), ('T', 'X'),
              ('A', 'U'), ('U', 'A'), ('M', 'N'), ('W', 'B')]
def ocr_candidates(w, ok):
    """Wörter, die sich von w um eine typische Verwechslung unterscheiden und die ok() für gültig hält."""
    out = []
    for a, b in CONFUSIONS:
        i = w.find(a)
        while i >= 0:
            c = w[:i] + b + w[i + len(a):]
            if c != w and c not in out and c not in FALLEN and ok(c): out.append(c)
            i = w.find(a, i + 1)
    return out
def suggest(w, dics=DEFAULT, budget=1.5, limit=5):
    """Hunspell-Vorschläge zu w. spylls liefert sie nacheinander, die naheliegenden zuerst – nach dem Budget (Sekunden)
    wird nicht weiter gewartet; ein einzelner Schritt kann es trotzdem überziehen."""
    import time
    real = [d for d in dics if d != 'vor1901'] or ['1901']
    out, t0 = [], time.monotonic()
    for d in real:
        for s in checker(d).load().suggest(w):
            s = s.strip('-')  # spylls schlägt auch Zusammensetzungen mit Bindestrich vor (-kolonisten)
            if s and s != w and s not in out and s not in FALLEN: out.append(s)
            if len(out) >= limit or time.monotonic() - t0 > budget: return out
    return out
def dics_for_year(year):
    """Vorschlag nach dem Erscheinungsjahr. Ab 1998 beide Rechtschreibungen: Die Umstellung zog sich hin, und neuere
    Arbeiten zitieren ältere Texte."""
    if not year: return list(DEFAULT)
    return ['1901', 'vor1901'] if year < 1902 else ['1901'] if year < 1998 else ['1901', 'neu']
YEAR = re.compile(r'(?<![\d.,/-])(1[5-9]\d\d|20[0-2]\d)(?![\d,/-]|\.\d)')
def guess_year(pages, now=2100):
    """Erscheinungsjahr raten: die späteste Jahreszahl auf den ersten und letzten Seiten (Titelei, Impressum) – eine
    Arbeit von 2002 nennt 1817, ein Buch von 1928 aber nicht 2002. Bevorzugt, was hinter © oder 'Copyright' steht."""
    keys = sorted(pages)
    text = '\n'.join('\n'.join(pages[k]) for k in keys[:8] + keys[-3:])
    m = re.search(r'(?:©|\(c\)|Copyright)\D{0,40}?(1[5-9]\d\d|20[0-2]\d)', text, re.I)
    if m: return int(m.group(1))
    ys = [int(y) for y in YEAR.findall(text) if int(y) <= now]
    return max(ys) if ys else None
def page_lines(t):
    """Der Inhalt einer Seitendatei als Zeilen: Die Datei endet normalerweise mit einem Zeilenumbruch (so schreibt das
    Programm sie), doch ein Editor lässt ihn manchmal weg – die letzte Zeile darf dabei nicht verloren gehen."""
    t = t.replace('\r\n', '\n')
    if t.endswith('\n'): t = t[:-1]
    return t.split('\n')
def read_page(path):
    return page_lines(open(path, encoding='utf-8').read())
def read_pages(folder):
    """{ 'NNN': [zeilen] } aus NNN.txt"""
    return {os.path.basename(f)[:3]: read_page(f) for f in sorted(glob.glob(os.path.join(folder, '[0-9][0-9][0-9].txt')))}
# ---- Auszeichnung im Text: dieselben Elemente wie im EPUB (XHTML), nichts Eigenes. Die Zeilenzahl einer Seite bleibt dabei
# gleich (sonst ginge die Bildzuordnung verloren): Jede Zeile bleibt eine Zeile, eine Tabellenzelle ist eine Zeile.
MARKUP = 'table|tr|td|th|h[1-6]|em|strong|i|b|sup|sub|p|blockquote|br'
TAG = re.compile(r'</?(?:%s)\s*/?>' % MARKUP)
TABLETAG = re.compile(r'</?(?:table|tr|td|th)>')
HEADTAG = re.compile(r'</?h[1-6]>')
def mask(l):
    """Auszeichnung durch Leerzeichen ersetzen – die Zeichenpositionen bleiben, die Wortprüfung sieht kein 'td'."""
    return TAG.sub(lambda m: ' ' * len(m.group()), l)
def make_table(lines, cols, head=False):
    """Aus aufeinanderfolgenden Zeilen eine Tabelle: Die Zeilen füllen die Zellen der Reihe nach, von links nach rechts.
    Leere Zeilen bleiben leer. head: die erste Reihe sind Spaltenköpfe (<th>). Liefert die neuen Zeilen (gleich viele)."""
    cols = max(1, int(cols))
    out = [TABLETAG.sub('', l) for l in lines]
    cells = [i for i, l in enumerate(out) if l.strip()]
    for k, i in enumerate(cells):
        c, last, tag = k % cols, k == len(cells) - 1, 'th' if head and k < cols else 'td'
        pre = ('<table>' if k == 0 else '') + ('<tr>' if c == 0 else '') + '<%s>' % tag
        post = '</%s>' % tag
        if last:
            post += '<td></td>' * (cols - 1 - c) + '</tr></table>'  # unvollständige letzte Reihe auffüllen
        elif c == cols - 1:
            post += '</tr>'
        out[i] = pre + out[i] + post
    return out
def table_block(lines, i):
    """(erste, letzte Zeile) der Tabelle, in der Zeile i liegt, sonst None."""
    a = next((k for k in range(i, -1, -1) if '<table>' in lines[k]), None)
    if a is None or any('</table>' in lines[k] for k in range(a, i)):
        return None
    b = next((k for k in range(a, len(lines)) if '</table>' in lines[k]), None)
    return (a, b) if b is not None and b >= i else None
def table_shape(lines):
    """(spalten, kopfzeile) einer ausgezeichneten Tabelle: Zellen bis zum ersten </tr>."""
    first = ''.join(lines).split('</tr>')[0]
    return max(1, len(re.findall(r'<t[dh]>', first))), '<th>' in first
def heading(line, level):
    """Zeile als Überschrift der Ebene 1–6 auszeichnen; level 0 nimmt die Auszeichnung weg."""
    t = HEADTAG.sub('', line)
    return '<h%d>%s</h%d>' % (level, t, level) if level and t.strip() else t
def corpus_freq(pages):
    c = collections.Counter()
    for lines in pages.values():
        for l in lines: c.update(WORD.findall(mask(l)))
    return c
def joined_tokens(lines):
    """Liefert je Zeile Liste (start, wort) und behandelt '¬'-Trennung: das getrennte Wort wird
    als (zeile_i, start_i, teil1, zeile_j, teil2) zusätzlich in joined zurückgegeben."""
    lines = [mask(l) for l in lines]
    toks = [[(m.start(), m.group()) for m in WORD.finditer(l)] for l in lines]
    joined = []
    for i, l in enumerate(lines):
        if l.rstrip().endswith('¬') and i + 1 < len(lines) and toks[i] and toks[i+1]:
            s1, w1 = toks[i][-1]; s2, w2 = toks[i+1][0]
            if s1 + len(w1) == len(l.rstrip()) - 1 and not lines[i + 1][:s2].strip():  # vor dem zweiten Teil steht höchstens Auszeichnung
                joined.append((i, s1, w1, i + 1, w2))
    return toks, joined
def known(w, freq, minfreq=3):
    return in_dict(w) or freq.get(w, 0) >= minfreq
