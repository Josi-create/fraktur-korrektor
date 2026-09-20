"""PAGE-XML (Transkribus) -> Buchordner: NNN.txt (Kopfzeile, Haupttext, Zeile '---', Fußnoten), lines.json
(je Seite Zeilen mit Bildkoordinaten in Transkribus-Pixeln, Bildgröße, Art) und – falls vorhanden – img/NNN.png|jpg."""
import os, re, json, glob, time, shutil, zipfile, tempfile, statistics
import xml.etree.ElementTree as ET
FN = re.compile(r'^\s*[\d*]{1,2}\)')          # Fußnotenbeginn: "1)" "12)" "*)"
IMGEXT = ('.png', '.jpg', '.jpeg')


def classify(lines, scale=1.0):
    """Ordnet die Zeilen (dicts mit text, x0, bl = Grundlinie) in Lesereihenfolge und setzt kind = head | body | fn.
    Die Pixelschwellen gelten für Seiten von 3508 px Höhe (Transkribus-Format); scale = Seitenhöhe / 3508."""
    # Zeilen mit nahezu gleicher Grundlinie (Fußnoten in zwei Spalten) nach x ordnen
    lines.sort(key=lambda d: d['bl'])
    row = 0; last = -999
    for d in lines:
        if d['bl'] - last > 15 * scale: row += 1
        d['row'] = row; last = d['bl']
    lines.sort(key=lambda d: (d['row'], d['x0']))
    for d in lines: d['kind'] = 'body'
    # Kopfzeile (Seitenzahl): erste Zeile, kurz, nur Ziffern/Striche
    if lines and re.fullmatch(r'[\s\d—\-–]+', lines[0]['text']) and len(lines[0]['text']) <= 8:
        lines[0]['kind'] = 'head'
    body = [d for d in lines if d['kind'] == 'body']
    # Fußnoten: ab der ersten Zeile, die wie "N)" beginnt und deren Zeilenabstand danach klein ist
    lo, hi = 20 * scale, 120 * scale
    gaps = [b2['bl'] - b1['bl'] for b1, b2 in zip(body, body[1:]) if lo < b2['bl'] - b1['bl'] < hi]
    main_gap = statistics.median(gaps) if gaps else 52 * scale
    for i, d in enumerate(body):
        if FN.match(d['text']) and i > 0:
            # Abstand der folgenden Zeilen deutlich kleiner als im Haupttext?
            nxt = [b2['bl'] - b1['bl'] for b1, b2 in zip(body[i:], body[i+1:]) if lo < b2['bl'] - b1['bl'] < hi]
            if not nxt or statistics.median(nxt) < main_gap * 0.9:
                for x in body[i:]: x['kind'] = 'fn'
                break
    return lines


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
    classify(lines, H / 3508)
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


def write_page(out, pg, lines):
    with open(os.path.join(out, pg + '.txt'), 'w', encoding='utf-8') as o:
        o.write('\n'.join(page_text(lines)) + '\n')


def save_origin(out, origin):
    """Hält fest, wie das Bild jeder Seite ursprünglich hieß. Ohne das lässt sich ein Transkribus-Export, der
    später zurückkommt, den Seiten nicht mehr sicher zuordnen: aus »seite_016_1L.tif« wurde hier »030.png«."""
    origin = {k: v for k, v in origin.items() if v}
    if not origin:
        return
    try:
        with open(os.path.join(out, 'quellen.json'), 'w', encoding='utf-8') as o:
            json.dump(dict(sorted(origin.items())), o, ensure_ascii=False, indent=1)
    except OSError:
        pass


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
    allpages, origin, nimg, warn = {}, {}, 0, []
    for k, f in enumerate(xml_files):
        W, H, imgname, lines = parse_page(f)
        pg = '%03d' % num[f]
        write_page(out, pg, lines)
        allpages[pg] = dict(w=W, h=H, lines=lines)
        origin[pg] = imgname or os.path.basename(f)
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
    save_origin(out, origin)
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


def unpack(src):
    """Export als ZIP in einen Temp-Ordner auspacken. Liefert (Ordner, aufzuräumender Temp-Ordner oder None)."""
    if os.path.isdir(src):
        return src, None
    if os.path.isfile(src) and not zipfile.is_zipfile(src):
        if os.path.splitext(src)[1].lower() in ('.txt', '.xml'):
            return src, None  # eine einzelne Datei: Textexport oder PAGE-XML
        raise ValueError('weder Ordner noch ZIP-Datei')
    if not os.path.isfile(src):
        raise ValueError('weder Ordner noch ZIP-Datei')
    tmp = tempfile.mkdtemp(prefix='fraktur-import-')
    with zipfile.ZipFile(src) as z:
        for m in z.namelist():  # nur sichere Pfade entpacken
            if m.strip('/') and not os.path.isabs(m) and '..' not in m.replace('\\', '/').split('/'):
                z.extract(m, tmp)
    return tmp, tmp


def image_of(f):
    """Der Bilddateiname, der in einer PAGE-XML steht – ohne die Datei ganz zu lesen."""
    try:
        with open(f, 'rb') as fh:
            m = re.search(rb'imageFilename="([^"]*)"', fh.read(8000))
    except OSError:
        return ''
    return m.group(1).decode('utf-8', 'replace') if m else ''


def name_keys(name):
    """Schlüssel, unter denen ein Datei- oder Bildname wiederzuerkennen ist: klein und ohne Endung. Transkribus
    stellt jeder Datei die laufende Nummer voran (0030_seite_016_1L.xml) – darum auch der Name ohne sie."""
    s = os.path.splitext(os.path.basename(name or ''))[0].lower()
    m = re.match(r'\d{1,4}[_-](.+)', s)
    return [s, m.group(1)] if m else [s]


def book_pages(folder):
    """Die Seitennummern eines Buchordners als '001', '002', …"""
    return sorted(os.path.basename(f)[:3] for f in glob.glob(os.path.join(folder, '[0-9][0-9][0-9].txt')))


def words(text):
    """Die Wörter einer Seite als Menge – Grundlage, um dieselbe Buchseite in zwei Texterkennungen wiederzufinden.
    Kurze Wörter bleiben weg: »und«, »der«, »die« stehen auf jeder Seite und sagen nichts."""
    return set(re.findall(r'[^\W\d_]{4,}', text.lower()))


def similarity(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0


def match_by_text(folder, items, text_of):
    """Die Seiten am Wortlaut wiedererkennen. Das braucht es für Bücher, die noch nicht wissen, wie ihre Bilder
    ursprünglich hießen: Derselbe Buchtext steht in beiden Fassungen, auch wenn die eine schlechter erkannt ist.

    Sicher erkannte Seiten sind die Anker; dazwischen zählt der Versatz. Stimmt er links und rechts einer Lücke
    überein, liegen die Seiten dort so, wie es die Reihenfolge verlangt. Stimmt er nicht, fehlt irgendwo eine
    Seite, und niemand kann sagen, wo – dann lieber abbrechen als danebenlegen."""
    pages, items = book_pages(folder), list(items)
    have = {}
    for pg in pages:
        try:
            with open(os.path.join(folder, pg + '.txt'), encoding='utf-8') as f:
                have[pg] = words(f.read())
        except OSError:
            have[pg] = set()
    anchor = {}
    for i, it in enumerate(items):
        w = words(text_of(it))
        if len(w) < 8:  # ein paar Wörter treffen zufällig überall
            continue
        best = sorted(((similarity(w, have[pg]), pg) for pg in pages), reverse=True)
        if best[0][0] >= 0.25 and (len(best) < 2 or best[0][0] >= 1.6 * best[1][0]):
            anchor[i] = pages.index(best[0][1])
    idx = sorted(anchor)
    if not idx or [anchor[i] for i in idx] != sorted({anchor[i] for i in idx}):
        raise ValueError('seiten_passen_nicht')
    hit = {}
    for i, it in enumerate(items):
        near = [j for j in (max((j for j in idx if j <= i), default=None), min((j for j in idx if j >= i), default=None)) if j is not None]
        off = {anchor[j] - j for j in near}
        k = i + off.pop() if len(off) == 1 else -1
        if 0 <= k < len(pages):
            hit[it] = pages[k]
    # Wo links und rechts verschiedene Versätze gelten, fehlt dazwischen etwas und niemand kann sagen, wo. Diese
    # Seiten bleiben offen – lieber ein paar auslassen als das Ganze verwerfen oder danebenlegen.
    if len(hit) < max(1, len(items) // 2) or len(set(hit.values())) != len(hit):
        raise ValueError('seiten_passen_nicht')
    return hit


def match_to_pages(folder, items, names, text_of=None):
    """Ordnet Dateien den Seiten eines vorhandenen Buchs zu. names(datei) liefert die Namen, unter denen die Datei
    zu erkennen ist; der erste, der auf eine Seite passt, entscheidet.

    Der Reihe nach zuzuordnen wäre bequem und geht schief, sobald im Export eine Seite fehlt: dann stünde jeder
    weitere Text neben dem falschen Bild. Darum zuerst über die Namen – wozu das Buch sich beim Einlesen gemerkt
    hat, wie seine Bilder ursprünglich hießen (quellen.json). Die Reihenfolge bleibt der Notnagel, und nur, wenn
    die Seitenzahl auf beiden Seiten gleich ist. Liefert (dict datei -> 'NNN', 'namen'|'reihenfolge')."""
    pages, items = book_pages(folder), list(items)
    known = {pg: pg for pg in pages}
    try:
        with open(os.path.join(folder, 'quellen.json'), encoding='utf-8') as f:
            for pg, name in json.load(f).items():
                for k in name_keys(name):
                    known[k] = pg if known.get(k, pg) == pg else None  # zwei Seiten unter einem Namen: unbrauchbar
    except (OSError, ValueError, AttributeError):
        pass
    hit, used = {}, set()
    for it in items:
        pg = next((known[k] for n in names(it) for k in name_keys(n) if known.get(k)), None)
        if pg and pg not in used:
            hit[it] = pg
            used.add(pg)
    if items and len(hit) == len(items):
        return hit, 'namen'
    if items and text_of:
        try:
            return match_by_text(folder, items, text_of), 'text'
        except ValueError:
            pass
    if items and len(items) == len(pages):
        return dict(zip(sorted(items), pages)), 'reihenfolge'
    raise ValueError('seiten_passen_nicht')


def backup(folder, pages):
    """Die Seiten, die gleich überschrieben werden, vorher in eine ZIP-Datei sichern (samt Protokoll und Ampel):
    hier steckt womöglich die Arbeit von Stunden. Liefert den Dateinamen der Sicherung oder None."""
    names = [pg + '.txt' for pg in pages] + ['lines.json', 'quellen.json', 'qualitaet.json', 'korrekturen.log']
    have = [n for n in names if os.path.isfile(os.path.join(folder, n))]
    if not have:
        return None
    stamp, n = time.strftime('%Y-%m-%d-%H%M%S'), 1
    name = 'vorher-%s.zip' % stamp
    while os.path.exists(os.path.join(folder, name)):  # zwei Sicherungen in derselben Sekunde
        n += 1
        name = 'vorher-%s-%d.zip' % (stamp, n)
    with zipfile.ZipFile(os.path.join(folder, name), 'w', zipfile.ZIP_DEFLATED) as z:
        for n in have:
            z.write(os.path.join(folder, n), n)
    return name


def backups(folder):
    """Die gesicherten Fassungen eines Buchs, jüngste zuerst: dict(name, zeit, pages)."""
    out = []
    # nach Alter, nicht nach Namen: bei zwei Sicherungen derselben Sekunde täuscht der Name
    for f in sorted(glob.glob(os.path.join(folder, 'vorher-*.zip')), key=os.path.getmtime, reverse=True):
        name = os.path.basename(f)
        m = re.fullmatch(r'vorher-(\d{4})-(\d\d)-(\d\d)-(\d\d)(\d\d)\d*(?:-\d+)?\.zip', name)
        zeit = '%s-%s-%s %s:%s' % m.groups() if m else time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getmtime(f)))
        try:
            with zipfile.ZipFile(f) as z:
                n = sum(1 for x in z.namelist() if re.fullmatch(r'\d{3}\.txt', x))
        except (OSError, zipfile.BadZipFile):
            continue
        out.append(dict(name=name, zeit=zeit, pages=n))
    return out


SICHERBAR = re.compile(r'\d{3}\.txt|lines\.json|quellen\.json|qualitaet\.json|korrekturen\.log')


def restore(folder, name):
    """Eine frühere Fassung zurückholen. Was jetzt dasteht, wird vorher gesichert – auch ein Zurückholen soll
    sich zurückholen lassen. Seiten, die in der Sicherung fehlen, bleiben, wie sie sind: Sie waren damals nicht
    betroffen und sind es jetzt auch nicht."""
    p = os.path.join(folder, os.path.basename(name or ''))
    if not (os.path.isfile(p) and os.path.basename(p).startswith('vorher-')):
        raise ValueError('quelle_fehlt')
    saved = backup(folder, book_pages(folder))
    zurueck = 0
    with zipfile.ZipFile(p) as z:
        for n in z.namelist():
            if SICHERBAR.fullmatch(n):
                with open(os.path.join(folder, n), 'wb') as f:
                    f.write(z.read(n))
                zurueck += n.endswith('.txt')
    return dict(restored=os.path.basename(p), backup=saved, pages=len(book_pages(folder)), back=zurueck)


def load_json(folder, name, default):
    try:
        with open(os.path.join(folder, name), encoding='utf-8') as f:
            d = json.load(f)
        return d if isinstance(d, dict) else default
    except (OSError, ValueError):
        return default


def text_pages(src):
    """Transkribus gibt auf Wunsch reinen Text statt PAGE-XML aus. Das ist eine Datei für das ganze Buch, in der
    zwei Leerzeilen die Seiten trennen – oder, seltener, eine Datei je Seite. Liefert [(name, [zeilen])].
    Ohne Zeilenlage im Bild, die steht nur im XML."""
    if os.path.isfile(src):
        files = [src]
    else:
        files = sorted(f for f in glob.glob(os.path.join(src, '**', '*.txt'), recursive=True)
                       if os.path.basename(f).lower() not in ('log.txt', 'metadata.txt') and os.path.getsize(f) > 0)
    if not files:
        return []
    if len(files) > 1:  # eine Datei je Seite
        out = []
        for f in files:
            with open(f, encoding='utf-8', errors='replace') as fh:
                zeilen = [l.rstrip() for l in fh.read().splitlines()]
            out.append((os.path.basename(f), [l for l in zeilen if l.strip()] or ['']))
        return out
    with open(files[0], encoding='utf-8', errors='replace') as fh:
        ganz = fh.read()
    bloecke = [b for b in re.split(r'\n\s*\n\s*\n', ganz) if b.strip()]
    name = os.path.splitext(os.path.basename(files[0]))[0]
    return [('%s_%03d' % (name, n), [l.rstrip() for l in b.strip('\n').splitlines() if l.strip()])
            for n, b in enumerate(bloecke, 1)]


def plain_lines(texte):
    """Zeilen ohne Lage im Bild. Die Seitenzahl oben erkennt man auch so; Fußnoten nicht – dafür braucht es die
    Abstände, die nur im PAGE-XML stehen."""
    lines = [dict(text=t, kind='body') for t in texte]
    if lines and re.fullmatch(r'[\s\d—\-–]+', lines[0]['text']) and len(lines[0]['text']) <= 8:
        lines[0]['kind'] = 'head'
    return lines


def read_book_page(path):
    """Eine Seite aus einem Buchordner: optional »# Kopfzeile«, Haupttext, Zeile »---«, Fußnoten."""
    with open(path, encoding='utf-8') as f:
        zeilen = [l.rstrip('\n') for l in f.read().splitlines()]
    lines, kind = [], 'body'
    for n, z in enumerate(zeilen):
        if n == 0 and z.startswith('#'):
            t = z[1:].strip()
            if t:
                lines.append(dict(text=t, kind='head'))
            continue
        if z.strip() == '---':
            kind = 'fn'
            continue
        lines.append(dict(text=z, kind=kind))
    return lines


def read_export(src):
    """Die Seiten einer Quelle, gleich welcher Art: {schlüssel: dict(w, h, img, lines)}. Bei PAGE-XML haben die
    Zeilen ihre Lage im Bild, bei Text oder einem fremden Buchordner nicht (w = 0). Dazu der Titel, wenn er
    dabeisteht."""
    files, title = ([src], None) if os.path.isfile(src) and src.lower().endswith('.xml') else find_export(src)
    if files:
        out = {}
        for f in sorted(files):
            W, H, img, lines = parse_page(f)
            out[f] = dict(w=W, h=H, img=img, lines=lines)
        return out, title
    if os.path.isdir(src) and book_pages(src):
        # Die Quelle ist selbst ein Buch des Programms. Seine Seitennummern sagen nichts darüber, wohin sein
        # Text hier gehört – »001« dort ist nicht »001« hier. Zugeordnet wird darum am Wortlaut.
        return {pg: dict(w=0, h=0, img='', lines=read_book_page(os.path.join(src, pg + '.txt')), book=True)
                for pg in book_pages(src)}, None
    return {k: dict(w=0, h=0, img='', lines=plain_lines(zeilen)) for k, zeilen in text_pages(src)}, None


def import_into(src, folder, progress=lambda done, total, msg: None, save=True):
    """Den Text eines Transkribus-Exports in ein Buch übernehmen, das es schon gibt: Seitenbilder, Lesezeichen,
    Wortliste und Einstellungen bleiben, wo sie sind. Ersetzt werden nur die Seiten, für die der Export Text
    liefert; wofür er keinen hat, bleibt stehen. Liefert dict(pages, replaced, kept, how, backup, title)."""
    src, tmp = unpack(src)
    try:
        if not book_pages(folder):
            raise ValueError('quelle_fehlt')
        progress(0, 1, 'lesen')
        read, title = read_export(src)
        if not read:
            raise ValueError('keine_xml')
        keys = sorted(read)
        # Kommt der Text aus einem anderen Buch, taugen dessen Seitennummern nicht als Namen; was dort über die
        # Herkunft der Bilder steht, dagegen schon.
        fremd = load_json(src, 'quellen.json', {}) if any(v.get('book') for v in read.values()) else None
        namen = (lambda k: (fremd.get(k, ''),)) if fremd is not None else (lambda k: (read[k]['img'], k))
        hit, how = match_to_pages(folder, keys, namen,
                                  text_of=lambda k: '\n'.join(d['text'] for d in read[k]['lines']))
        offen = [k for k in keys if k not in hit]
        keys = [k for k in keys if k in hit]
        saved = backup(folder, sorted(hit.values())) if save else None
        geo, origin = load_json(folder, 'lines.json', {}), load_json(folder, 'quellen.json', {})
        ohne_lage = []
        for n, k in enumerate(keys):
            pg, seite = hit[k], read[k]
            lines, alt = seite['lines'], geo.get(pg)
            if seite['w']:
                geo[pg] = dict(w=seite['w'], h=seite['h'], lines=lines)
            elif alt and len(alt['lines']) == len(lines):
                # Derselbe Text, nur ohne Koordinaten: die vorhandenen Zeilen behalten ihre Lage im Bild
                for l, neu in zip(alt['lines'], lines):
                    l['text'] = neu['text']
                    l.setdefault('bl', l.get('y1', 0))  # Bücher von außen kennen die Grundlinie nicht
                    l.setdefault('x0', 0)
                lines = classify(alt['lines'], (alt.get('h') or 3508) / 3508)
                geo[pg] = dict(w=alt.get('w'), h=alt.get('h'), lines=lines)
            else:
                geo.pop(pg, None)  # andere Zeilenzahl: die alte Lage gehörte zu anderem Text
                ohne_lage.append(pg)
            write_page(folder, pg, lines)
            origin.setdefault(pg, seite['img'] or os.path.basename(k))
            progress(n + 1, len(keys), 'seiten')
        with open(os.path.join(folder, 'lines.json'), 'w', encoding='utf-8') as o:
            json.dump(dict(sorted(geo.items())), o, ensure_ascii=False)
        save_origin(folder, origin)
        # Die Ampel stammte von der alten Texterkennung und sagt über den neuen Text nichts mehr; sie steckt in
        # der Sicherung, falls doch jemand nachsehen will.
        try:
            os.remove(os.path.join(folder, 'qualitaet.json'))
        except OSError:
            pass
        kept = [pg for pg in book_pages(folder) if pg not in set(hit.values())]
        return dict(pages=len(book_pages(folder)), replaced=len(hit), kept=kept, how=how, backup=saved, title=title,
                    nogeo=ohne_lage, unclear=len(offen))
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)


def import_export(src, out, images=None):
    """src: Transkribus-Export als ZIP-Datei oder Ordner. Bilder aus dem Export selbst, wenn images fehlt."""
    src, tmp = unpack(src)
    try:
        files, title = find_export(src)
        r = build(files, out, images or src)
        r['title'] = title
        return r
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)
