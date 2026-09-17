"""Qualitätsmaß je Seite aus Transkribus-Text: Anteil der Zeilenend-Wörter, die im ganzen Buch nur einmal vorkommen
(Hapax), verglichen mit Wörtern in der Zeilenmitte. Hohe Zeilenend-Hapax-Quote = am Bund gestauchte Zeilenenden.
Aufruf: py -3.14 ocr_quality.py <txt-ordner> > bericht.csv"""
import sys, glob, os, re, collections
src = sys.argv[1]
W = re.compile(r"[A-Za-zÄÖÜäöüß]+")
pages = {}
for f in sorted(glob.glob(os.path.join(src, '[0-9][0-9][0-9].txt'))):
    n = os.path.basename(f)[:3]
    lines = [l for l in open(f, encoding='utf-8').read().split('\n') if l.strip()]
    pages[n] = lines
freq = collections.Counter()
for lines in pages.values():
    for l in lines:
        freq.update(w.lower() for w in W.findall(l))
print("seite;zeilen;ende_hapax;ende_n;mitte_hapax;mitte_n;ende_quote;mitte_quote")
rows = []
for n, lines in pages.items():
    eh = en = mh = mn = 0
    for l in lines:
        l2 = l.rstrip()
        if l2.endswith('¬'):
            continue  # Trennung, Wortende unbekannt
        ws = W.findall(l2)
        if len(ws) < 4: continue
        en += 1; eh += freq[ws[-1].lower()] == 1
        for w in ws[1:-1]:
            mn += 1; mh += freq[w.lower()] == 1
    eq = eh/en if en else 0; mq = mh/mn if mn else 0
    rows.append((n, len(lines), eh, en, mh, mn, eq, mq))
for r in rows:
    print("%s;%d;%d;%d;%d;%d;%.2f;%.2f" % r)
