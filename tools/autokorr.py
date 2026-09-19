"""Automatische Korrektur typischer Fraktur-Verwechslungen in ocr/korr/*.txt (in place).
py -3.14 autokorr.py <ordner> [--dry]   Protokoll: <ordner>/autokorr.log"""
import sys, os, itertools
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from korrlib import *
folder = sys.argv[1]; dry = '--dry' in sys.argv
pages = read_pages(folder); freq = corpus_freq(pages)
wlp = os.path.join(folder, 'whitelist.txt')
WLIST = set(open(wlp, encoding='utf-8').read().split()) if os.path.exists(wlp) else set()
SUBS = [('l','t'),('l','k'),('l','f'),('b','d'),('B','W'),('B','V'),('s','f'),('u','n'),('n','u'),('ii','n'),('rn','m'),('ck','d'),('Th','Tr'),('c','e'),('i','l'),('J','I'),('I','J'),('D','O'),('O','D'),('P','B'),('R','K'),('K','R'),('S','G'),('G','S'),('h','k'),('j','f'),('ö','o'),('a','ä')]
def candidates(w):
    """Ein- und Zweifach-Ersetzungen, nur gleiche Länge außer ß/ss; Ergebnis muss bekannt sein."""
    seen = set(); out = []
    def one(x):
        for a, b in SUBS:
            i = x.find(a)
            while i >= 0:
                y = x[:i] + b + x[i+len(a):]
                if y not in seen: seen.add(y); yield y
                i = x.find(a, i + 1)
    lvl1 = list(one(w))
    # kurze Wörter: Kandidat muss im Buch belegt sein; lange: Wörterbuch genügt
    fw = freq.get(w, 0)
    # Ein Wort, das im Buch haeufiger ist als sein Kandidat, ist wahrscheinlich ein Name oder eine alte Schreibung
    good = [c for c in lvl1 if ((in_dict(c) and (len(c) >= 6 or freq.get(c, 0) >= 1) and (freq.get(c, 0) >= fw or fw < 3))
                                or (freq.get(c, 0) >= 3 and freq.get(c, 0) > fw))]
    if good: return good
    lvl2 = [c for x in lvl1 for c in one(x)]
    return [c for c in lvl2 if in_dict(c) and freq.get(c, 0) >= 1 and freq.get(c, 0) >= fw]  # Zweifach nur wenn im Buch belegt
def best(w):
    # Nur Wörterbuch und Whitelist schützen ein Wort; Häufigkeit im Buch nicht (häufige OCR-Fehler!)
    if len(w) < 4 or in_dict(w) or w in WLIST: return None
    cs = candidates(w)
    if not cs: return None
    cs.sort(key=lambda c: -freq.get(c, 0))
    if len(cs) == 1 or freq.get(cs[0], 0) >= 3 * max(1, freq.get(cs[1], 0)):
        return cs[0]
    return None
def sicher(b): return 'sicher' if freq.get(b, 0) >= 3 else 'unsicher'
log = []; n = 0
for pg, lines in pages.items():
    toks, joined = joined_tokens(lines)
    new = list(lines)
    # getrennte Wörter
    for i, s1, w1, j, w2 in joined:
        b = best(w1 + w2)
        if b and len(b) == len(w1 + w2):
            nb1, nb2 = b[:len(w1)], b[len(w1):]
            new[i] = new[i][:s1] + nb1 + new[i][s1+len(w1):]
            s2 = toks[j][0][0]  # hinter etwaiger Auszeichnung (<td>)
            new[j] = new[j][:s2] + nb2 + new[j][s2+len(w2):]
            log.append(f'{pg}	{i+1}	{w1}¬{w2}	{nb1}¬{nb2}	' + sicher(b)); n += 1
            toks[i] = toks[i][:-1]; toks[j] = toks[j][1:]
    frag = {(i, s1) for i, s1, w1, j, w2 in joined} | {(j, toks[j][0][0]) for i, s1, w1, j, w2 in joined}
    for i, tl in enumerate(toks):
        for s, w in reversed(tl):
            if (i, s) in frag: continue
            b = best(w)
            if b:
                new[i] = new[i][:s] + b + new[i][s+len(w):]
                log.append(f'{pg}	{i+1}	{w}	{b}	' + sicher(b)); n += 1
    if not dry and new != lines:
        open(os.path.join(folder, pg + '.txt'), 'w', encoding='utf-8').write('\n'.join(new) + '\n')
open(os.path.join(folder, 'autokorr.log'), 'w', encoding='utf-8').write('\n'.join(log) + '\n')
print(n, 'Ersetzungen', '(Probelauf)' if dry else '')
