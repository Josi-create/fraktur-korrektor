"""Gemeinsames: Wörterbuch (Hunspell via spylls), Korpusfrequenz, Tokenisierung.
Wörterbuch (Pfad mit oder ohne Endung .dic/.aff), in dieser Reihenfolge: set_dic(pfad) bzw. --dic,
Umgebungsvariable FRAKTUR_DIC, "dic" in ~/.fraktur-korrektor/config.json, mitgeliefertes dict/de_DE_OLDSPELL.
dict/zusatz.txt: zusätzlich gültige Wörter (Abkürzungen); dict/fallen.txt: nie gültig, weil fast immer OCR-Fehler (baß)."""
import os, re, glob, json, atexit, hashlib, collections, functools
from spylls.hunspell import Dictionary
HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.environ.get('FRAKTUR_HOME') or os.path.join(os.path.expanduser('~'), '.fraktur-korrektor')
WORD = re.compile(r"[A-Za-zÄÖÜäöüß]+")
DIC = None
_d = None
_cache, _cache_path, _cache_n = {}, None, 0
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
    """Erster Kandidat, zu dem .dic und .aff existieren; sonst Abbruch mit verständlicher Meldung."""
    cand = [DIC, os.environ.get('FRAKTUR_DIC'), config().get('dic'), os.path.join(HERE, 'dict', 'de_DE_OLDSPELL', 'de_DE_OLDSPELL')]
    cand = [_base(c) for c in cand if c]
    for c in cand:
        if os.path.exists(c + '.dic') and os.path.exists(c + '.aff'):
            return c
    raise SystemExit('Kein Wörterbuch gefunden. Gesucht wurde (jeweils .dic und .aff):\n  ' + '\n  '.join(cand) +
                     '\nAbhilfe: den Ordner dict/ des Programms wiederherstellen oder ein Hunspell-Wörterbuch mit --dic <pfad> angeben.')
def set_dic(path):
    global DIC, _d
    DIC = _base(path)
    _d = None; _cache.clear(); in_dict.cache_clear()
def dic():
    """Lädt das Wörterbuch und den Zwischenspeicher der Prüfergebnisse (das freie Wörterbuch prüft langsam)."""
    global _d, _cache_path, _cache_n
    if _d is None:
        p = find_dic()
        _d = Dictionary.from_files(p)
        key = '|'.join([p] + [str(os.path.getmtime(p + e)) for e in ('.dic', '.aff')])
        _cache_path = os.path.join(HOME, 'cache', hashlib.md5(key.encode('utf-8')).hexdigest() + '.json')
        try: _cache.update(json.load(open(_cache_path, encoding='utf-8')))
        except (OSError, ValueError): pass
        _cache_n = len(_cache)
    return _d
def save_cache():
    global _cache_n
    if _cache_path and len(_cache) > _cache_n:
        os.makedirs(os.path.dirname(_cache_path), exist_ok=True)
        with open(_cache_path + '.tmp', 'w', encoding='utf-8') as f:
            json.dump(_cache, f, ensure_ascii=False)
        os.replace(_cache_path + '.tmp', _cache_path)
        _cache_n = len(_cache)
atexit.register(save_cache)
def _wordlist(name):
    p = os.path.join(HERE, 'dict', name)
    return {w for l in open(p, encoding='utf-8') if not l.startswith('#') for w in l.split()} if os.path.exists(p) else set()
ZUSATZ, FALLEN = _wordlist('zusatz.txt'), _wordlist('fallen.txt')
@functools.lru_cache(maxsize=None)
def in_dict(w):
    if len(w) <= 1 or w in ZUSATZ: return True
    if w in FALLEN: return False
    d = dic()
    if w not in _cache:
        _cache[w] = bool(d.lookup(w) or d.lookup(w.lower()) or d.lookup(w[0].upper() + w[1:]))
    return _cache[w]
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
