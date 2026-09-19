"""Gemeinsames: Wörterbücher (Hunspell via spylls), Korpusfrequenz, Tokenisierung.

Welche Rechtschreibung gilt, ist je Buch wählbar (DICS):
  1901     Rechtschreibung 1901–1996 (daß, Schiffahrt) – mitgeliefert: dict/de_DE_OLDSPELL. Ein anderes Wörterbuch an dieser
           Stelle: set_dic(pfad) bzw. --dic, Umgebungsvariable FRAKTUR_DIC, "dic" in ~/.fraktur-korrektor/config.json
  neu      neue Rechtschreibung ab 1996 (dass, Schifffahrt) – mitgeliefert: dict/de_DE_frami
  vor1901  kein Wörterbuch, sondern Regeln: Thür, seyn, Noth, civilisiren gelten, wenn die heutige Form bekannt ist
dict/zusatz.txt: zusätzlich gültige Wörter (Abkürzungen); dict/fallen.txt: nie gültig, weil fast immer OCR-Fehler (baß)."""
import os, re, glob, json, atexit, hashlib, collections, functools, itertools
from spylls.hunspell import Dictionary
HERE = os.path.dirname(os.path.abspath(__file__))
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
    """Ein Hunspell-Wörterbuch mit Zwischenspeicher der Prüfergebnisse auf der Platte (die freien Wörterbücher prüfen langsam)."""
    def __init__(self, path):
        self.path, self.d, self.cache, self.cache_path, self.n = path, None, {}, None, 0
    def load(self):
        if self.d is None:
            self.d = Dictionary.from_files(self.path)
            key = '|'.join([self.path] + [str(os.path.getmtime(self.path + e)) for e in ('.dic', '.aff')])
            self.cache_path = os.path.join(HOME, 'cache', hashlib.md5(key.encode('utf-8')).hexdigest() + '.json')
            try: self.cache.update(json.load(open(self.cache_path, encoding='utf-8')))
            except (OSError, ValueError): pass
            self.n = len(self.cache)
        return self.d
    def lookup(self, w):
        if w not in self.cache:
            d = self.load() if self.d is None else self.d
            if w not in self.cache:
                # auch klein (Satzanfang) und groß (Substantivierung) – aber jede Schreibweise nur einmal: Fehlversuche sind teuer
                self.cache[w] = any(d.lookup(v) for v in dict.fromkeys((w, w.lower(), w[0].upper() + w[1:])))
        return self.cache[w]
    def save(self):
        if self.cache_path and len(self.cache) > self.n:
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
            with open(self.cache_path + '.tmp', 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False)
            os.replace(self.cache_path + '.tmp', self.cache_path)
            self.n = len(self.cache)
_checkers = {}
def checker(name='1901'):
    if name not in _checkers:
        c = _checkers[name] = Checker(find_dic() if name == '1901' else os.path.join(HERE, 'dict', 'de_DE_frami', 'de_DE_frami'))
        c.load()
    return _checkers[name]
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
def read_page(path):
    t = open(path, encoding='utf-8').read()
    if t.endswith('\n'): t = t[:-1]
    return t.split('\n')
def read_pages(folder):
    """{ 'NNN': [zeilen] } aus NNN.txt"""
    return {os.path.basename(f)[:3]: read_page(f) for f in sorted(glob.glob(os.path.join(folder, '[0-9][0-9][0-9].txt')))}
def corpus_freq(pages):
    c = collections.Counter()
    for lines in pages.values():
        for l in lines: c.update(WORD.findall(l))
    return c
def joined_tokens(lines):
    """Liefert je Zeile Liste (start, wort) und behandelt '¬'-Trennung: das getrennte Wort wird
    als (zeile_i, start_i, teil1, zeile_j, teil2) zusätzlich in joined zurückgegeben."""
    toks = [[(m.start(), m.group()) for m in WORD.finditer(l)] for l in lines]
    joined = []
    for i, l in enumerate(lines):
        if l.rstrip().endswith('¬') and i + 1 < len(lines) and toks[i] and toks[i+1]:
            s1, w1 = toks[i][-1]; s2, w2 = toks[i+1][0]
            if s1 + len(w1) == len(l.rstrip()) - 1 and s2 == 0:
                joined.append((i, s1, w1, i + 1, w2))
    return toks, joined
def known(w, freq, minfreq=3):
    return in_dict(w) or freq.get(w, 0) >= minfreq
