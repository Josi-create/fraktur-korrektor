"""PAGE-XML -> Korrekturtexte mit Fußnotentrennung.
py -3.14 build_text.py <page-ordner> <out-ordner>
Schreibt out/NNN.txt (Kopfzeile, Haupttext, Zeile '---' , Fußnoten) und out/lines.json
(je Seite Zeilen mit Bildkoordinaten in Transkribus-Pixeln, Bildgröße, Art)."""
import sys, os, glob, re, json, statistics
import xml.etree.ElementTree as ET
src, out = sys.argv[1:3]
os.makedirs(out, exist_ok=True)
FN = re.compile(r'^\s*[\d*]{1,2}\)')          # Fußnotenbeginn: "1)" "12)" "*)"
allpages = {}
for f in sorted(glob.glob(os.path.join(src, '*.xml'))):
    root = ET.parse(f).getroot()
    ns = re.match(r'\{(.*)\}', root.tag).group(1); N = {'p': ns}
    n = int(re.search(r'p(\d+)', os.path.basename(f)).group(1))
    page = root.find('p:Page', N)
    W, H = int(page.get('imageWidth')), int(page.get('imageHeight'))
    lines = []
    for l in page.iter(f'{{{ns}}}TextLine'):
        pts = [tuple(map(int, p.split(','))) for p in l.find('p:Coords', N).get('points').split()]
        b = l.find('p:Baseline', N)
        bpts = [tuple(map(int, p.split(','))) for p in b.get('points').split()] if b is not None and b.get('points') else pts
        u = l.find('p:TextEquiv/p:Unicode', N)
        t = (u.text or '') if u is not None else ''
        xs = [x for x, y in pts]; ys = [y for x, y in pts]
        lines.append(dict(id=l.get('id'), text=t, x0=min(xs), x1=max(xs), y0=min(ys), y1=max(ys),
                          bl=int(statistics.median(y for x, y in bpts))))
    # Kopfzeile (Seitenzahl): erste Zeile, kurz, nur Ziffern/Striche
    # Zeilen mit nahezu gleicher Grundlinie (Fußnoten in zwei Spalten) nach x ordnen
    lines.sort(key=lambda d: d['bl'])
    row = 0; last = -999
    for d in lines:
        if d['bl'] - last > 15: row += 1
        d['row'] = row; last = d['bl']
    lines.sort(key=lambda d: (d['row'], d['x0']))
    for d in lines: d['kind'] = 'body'
    if lines and re.fullmatch(r'[\s\d—\-–]+', lines[0]['text']) and len(lines[0]['text']) <= 8:
        lines[0]['kind'] = 'head'
    body = [d for d in lines if d['kind'] == 'body']
    # Fußnoten: ab der ersten Zeile, die wie "N)" beginnt und deren Zeilenabstand danach klein ist
    gaps = [b2['bl'] - b1['bl'] for b1, b2 in zip(body, body[1:]) if 20 < b2['bl'] - b1['bl'] < 120]
    main_gap = statistics.median(gaps) if gaps else 52
    start = None
    for i, d in enumerate(body):
        if FN.match(d['text']) and i > 0:
            # Abstand der folgenden Zeilen deutlich kleiner als im Haupttext?
            nxt = [b2['bl'] - b1['bl'] for b1, b2 in zip(body[i:], body[i+1:]) if 20 < b2['bl'] - b1['bl'] < 120]
            if not nxt or statistics.median(nxt) < main_gap * 0.9:
                start = i; break
    if start is not None:
        for d in body[start:]: d['kind'] = 'fn'
    # Fußnoten in zwei Spalten (gleiche Zeile) nach x sortieren – Reihenfolge bleibt bl,x0
    txt = []
    head = [d for d in lines if d['kind'] == 'head']
    txt.append('# ' + (head[0]['text'].strip() if head else '') )
    txt += [d['text'] for d in lines if d['kind'] == 'body']
    fn = [d['text'] for d in lines if d['kind'] == 'fn']
    if fn: txt += ['---'] + fn
    open(os.path.join(out, '%03d.txt' % n), 'w', encoding='utf-8').write('\n'.join(txt) + '\n')
    allpages['%03d' % n] = dict(w=W, h=H, lines=lines)
json.dump(allpages, open(os.path.join(out, 'lines.json'), 'w', encoding='utf-8'), ensure_ascii=False)
nfn = sum(1 for p in allpages.values() if any(d['kind'] == 'fn' for d in p['lines']))
print(len(allpages), 'Seiten,', nfn, 'mit Fußnoten ->', out)
