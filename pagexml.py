"""PAGE-XML (Transkribus) -> Buchordner: NNN.txt (Kopfzeile, Haupttext, Zeile '---', Fußnoten), lines.json
(je Seite Zeilen mit Bildkoordinaten in Transkribus-Pixeln, Bildgröße, Art) und – falls vorhanden – img/NNN.png|jpg."""
import os, re, json, glob, shutil, zipfile, tempfile, statistics
import xml.etree.ElementTree as ET
FN = re.compile(r'^\s*[\d*]{1,2}\)')          # Fußnotenbeginn: "1)" "12)" "*)"
IMGEXT = ('.png', '.jpg', '.jpeg')


def parse_page(f):
    """Liefert (Breite, Höhe, Bilddateiname, Zeilen) einer PAGE-XML-Datei; Zeilen in Lesereihenfolge mit kind head|body|fn."""
    root = ET.parse(f).getroot()
    ns = re.match(r'\{(.*)\}', root.tag).group(1); N = {'p': ns}
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
    # Zeilen mit nahezu gleicher Grundlinie (Fußnoten in zwei Spalten) nach x ordnen
    lines.sort(key=lambda d: d['bl'])
    row = 0; last = -999
    for d in lines:
        if d['bl'] - last > 15: row += 1
        d['row'] = row; last = d['bl']
    lines.sort(key=lambda d: (d['row'], d['x0']))
    for d in lines: d['kind'] = 'body'
    # Kopfzeile (Seitenzahl): erste Zeile, kurz, nur Ziffern/Striche
    if lines and re.fullmatch(r'[\s\d—\-–]+', lines[0]['text']) and len(lines[0]['text']) <= 8:
        lines[0]['kind'] = 'head'
    body = [d for d in lines if d['kind'] == 'body']
    # Fußnoten: ab der ersten Zeile, die wie "N)" beginnt und deren Zeilenabstand danach klein ist
    gaps = [b2['bl'] - b1['bl'] for b1, b2 in zip(body, body[1:]) if 20 < b2['bl'] - b1['bl'] < 120]
    main_gap = statistics.median(gaps) if gaps else 52
    for i, d in enumerate(body):
        if FN.match(d['text']) and i > 0:
            # Abstand der folgenden Zeilen deutlich kleiner als im Haupttext?
            nxt = [b2['bl'] - b1['bl'] for b1, b2 in zip(body[i:], body[i+1:]) if 20 < b2['bl'] - b1['bl'] < 120]
            if not nxt or statistics.median(nxt) < main_gap * 0.9:
                for x in body[i:]: x['kind'] = 'fn'
                break
    return W, H, page.get('imageFilename') or '', lines


def page_text(lines):
    head = [d for d in lines if d['kind'] == 'head']
    txt = ['# ' + (head[0]['text'].strip() if head else '')]
    txt += [d['text'] for d in lines if d['kind'] == 'body']
    fn = [d['text'] for d in lines if d['kind'] == 'fn']
    if fn: txt += ['---'] + fn
    return txt


def numbering(files):
    """Seitennummer je Datei: führende Zahl (Transkribus: 0035_name.xml), sonst pNNN im Namen, sonst die Reihenfolge."""
    for rx in (r'^(\d+)', r'p(\d+)'):
        ms = [re.search(rx, os.path.basename(f)) for f in files]
        if all(ms) and len({int(m.group(1)) for m in ms}) == len(files):
            return {f: int(m.group(1)) for f, m in zip(files, ms)}
    return {f: n for n, f in enumerate(sorted(files), 1)}


def build(xml_files, out, images=None):
    """Schreibt den Buchordner. images: Ordner mit Seitenbildern (nach Dateiname bzw. Reihenfolge zugeordnet).
    Vorhandene NNN.txt werden nicht überschrieben (dort stecken Korrekturen). Liefert dict(pages, fn, images, warnings)."""
    xml_files = sorted(xml_files)
    if not xml_files:
        raise ValueError('keine PAGE-XML-Dateien gefunden')
    if glob.glob(os.path.join(out, '[0-9][0-9][0-9].txt')):
        raise FileExistsError(out)
    os.makedirs(os.path.join(out, 'img'), exist_ok=True)
    num = numbering(xml_files)
    pool = sorted(f for f in glob.glob(os.path.join(images, '**', '*'), recursive=True) if f.lower().endswith(IMGEXT)) if images else []
    byname = {os.path.basename(f).lower(): f for f in pool}
    allpages, nimg, warn = {}, 0, []
    for k, f in enumerate(xml_files):
        W, H, imgname, lines = parse_page(f)
        pg = '%03d' % num[f]
        with open(os.path.join(out, pg + '.txt'), 'w', encoding='utf-8') as o:
            o.write('\n'.join(page_text(lines)) + '\n')
        allpages[pg] = dict(w=W, h=H, lines=lines)
        stem = os.path.splitext(os.path.basename(f))[0].lower()
        src = byname.get(imgname.lower()) or next((byname[stem + e] for e in IMGEXT if stem + e in byname), None) \
            or (pool[k] if len(pool) == len(xml_files) else None)
        if src:
            shutil.copyfile(src, os.path.join(out, 'img', pg + os.path.splitext(src)[1].lower()))
            nimg += 1
    if nimg < len(xml_files):
        warn.append('bilder_fehlen')
    with open(os.path.join(out, 'lines.json'), 'w', encoding='utf-8') as o:
        json.dump(allpages, o, ensure_ascii=False)
    nfn = sum(1 for p in allpages.values() if any(d['kind'] == 'fn' for d in p['lines']))
    return dict(pages=len(allpages), fn=nfn, images=nimg, warnings=warn)


def find_export(src):
    """Sucht in einem Transkribus-Export (Ordner) die PAGE-XML-Dateien: Unterordner 'page', sonst alle XML mit <PcGts>.
    Liefert (xml-dateien, titel laut metadata.xml oder None)."""
    pages = [d for d, _, fs in os.walk(src) if os.path.basename(d).lower() == 'page' and any(f.lower().endswith('.xml') for f in fs)]
    if pages:
        d = sorted(pages)[0]
        files = glob.glob(os.path.join(d, '*.xml'))
        meta = os.path.join(os.path.dirname(d), 'metadata.xml')
    else:
        files = [f for f in glob.glob(os.path.join(src, '**', '*.xml'), recursive=True) if b'PcGts' in open(f, 'rb').read(600)]
        meta = os.path.join(src, 'metadata.xml')
    title = None
    try:
        t = ET.parse(meta).getroot().find('.//title')
        title = (t.text or '').strip() or None if t is not None else None
    except (OSError, ET.ParseError):
        pass
    return files, title


def import_export(src, out, images=None):
    """src: Transkribus-Export als ZIP-Datei oder Ordner. Bilder aus dem Export selbst, wenn images fehlt."""
    tmp = None
    try:
        if os.path.isfile(src):
            if not zipfile.is_zipfile(src):
                raise ValueError('weder Ordner noch ZIP-Datei')
            tmp = tempfile.mkdtemp(prefix='fraktur-import-')
            with zipfile.ZipFile(src) as z:
                for m in z.namelist():  # nur sichere Pfade entpacken
                    if m.strip('/') and not os.path.isabs(m) and '..' not in m.replace('\\', '/').split('/'):
                        z.extract(m, tmp)
            src = tmp
        files, title = find_export(src)
        r = build(files, out, images or src)
        r['title'] = title
        return r
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)
