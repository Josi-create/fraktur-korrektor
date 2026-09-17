"""Gemeinsames: Wörterbuch (Hunspell via spylls), Korpusfrequenz, Tokenisierung.
Wörterbuch: Umgebungsvariable FRAKTUR_DIC oder set_dic(pfad) – Pfad ohne Endung (.dic/.aff)."""
import os, re, glob, collections, functools
from spylls.hunspell import Dictionary
DIC = os.environ.get('FRAKTUR_DIC') or r"C:\Program Files\Adobe\Adobe Photoshop 2026\Required\Linguistics\Providers\Plugins2\AdobeHunspellPlugin\Dictionaries\de_DE\1901\de_DE"
WORD = re.compile(r"[A-Za-zÄÖÜäöüß]+")
_d = None
def set_dic(path):
    global DIC, _d
    DIC = path[:-4] if path.lower().endswith(('.dic', '.aff')) else path
    _d = None; in_dict.cache_clear()
def dic():
    global _d
    if _d is None: _d = Dictionary.from_files(DIC)
    return _d
@functools.lru_cache(maxsize=None)
def in_dict(w):
    if len(w) <= 1: return True
    return bool(dic().lookup(w) or dic().lookup(w.lower()) or dic().lookup(w[0].upper() + w[1:]))
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
