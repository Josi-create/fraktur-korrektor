"""PAGE-XML (Transkribus) -> Text: py -3.14 page2txt.py <page-ordner> <out-ordner>
Schreibt je Seite NNN.txt (Regionen in Lesereihenfolge, Zeilen) und alle.txt mit Seitentrennern."""
import sys, os, glob, re
import xml.etree.ElementTree as ET
src, out = sys.argv[1:3]
os.makedirs(out, exist_ok=True)
NS = {'p': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}
alle = []
for f in sorted(glob.glob(os.path.join(src, '*.xml'))):
    root = ET.parse(f).getroot()
    ns = re.match(r'\{(.*)\}', root.tag).group(1)
    N = {'p': ns}
    n = int(re.search(r'p(\d+)', os.path.basename(f)).group(1))
    page = root.find('p:Page', N)
    # Reihenfolge aus ReadingOrder, sonst Dokumentreihenfolge
    order = [r.get('regionRef') for r in page.iter(f'{{{ns}}}RegionRefIndexed')]
    regs = {r.get('id'): r for r in page.findall('p:TextRegion', N)}
    ids = [i for i in order if i in regs] + [i for i in regs if i not in order]
    parts = []
    for i in ids:
        r = regs[i]
        typ = r.get('type', '')
        lines = []
        for l in r.findall('p:TextLine', N):
            u = l.find('p:TextEquiv/p:Unicode', N)
            lines.append((u.text or '') if u is not None else '')
        parts.append((typ, '\n'.join(lines)))
    txt = '\n\n'.join(('[%s]\n' % t if t and t != 'paragraph' else '') + s for t, s in parts)
    open(os.path.join(out, '%03d.txt' % n), 'w', encoding='utf-8').write(txt + '\n')
    alle.append('==== Seite %03d ====\n%s' % (n, txt))
open(os.path.join(out, 'alle.txt'), 'w', encoding='utf-8').write('\n\n'.join(alle) + '\n')
print(len(alle), 'Seiten ->', out)
