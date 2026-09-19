"""Was steckt in dem, was der Nutzer öffnen will? scan(pfad) untersucht eine Datei oder einen Ordner und liefert die
Funde – der Nutzer soll nicht wissen müssen, was ein "Transkribus-Export" oder ein "Buchordner" ist.

Fund = dict(kind, path, name, pages, mtime, …):
  book         Buchordner des Fraktur-Korrektors (NNN.txt) – corrections = Zeilen in korrekturen.log
  transkribus  Export als ZIP oder Ordner (PAGE-XML) – images = Seitenbilder liegen bei; images_dir = passender Bilderordner
  epub         EPUB – pdf = gleichlautendes PDF (dann: links das PDF, rechts der EPUB-Text)
  pdf          PDF – text = durchsuchbar
  images       Ordner mit Seitenbildern
Der erste Fund ist die Empfehlung: Wo schon Korrekturen stecken, geht nichts verloren; sonst der fertigste Text."""
import os, re, glob, time, zipfile
import xml.etree.ElementTree as ET

IMG = ('.png', '.jpg', '.jpeg', '.tif', '.tiff')
PRUNE = {'venv', '.venv', 'node_modules', '__pycache__', 'build', 'dist', 'site-packages', '$recycle.bin', 'system volume information',
         'cache'}  # ScanTailor legt in out/cache Miniaturbilder und Zwischenschritte ab – die sind keine Buchseiten
RANK = dict(book=0, transkribus=1, epub=2, pdf=3, images=4)
MAXDEPTH, MAXFILES, MAXTIME = 4, 40000, 6.0


def stem_key(name):
    """'Fatma - Immanuel Walker (durchsuchbar).pdf' und 'Fatma - Immanuel Walker.epub' lauten gleich."""
    s = os.path.splitext(name)[0].lower()
    s = re.sub(r'\([^)]*\)|\[[^\]]*\]', ' ', s)
    s = re.sub(r'[_\s-]+(ocr|durchsuchbar|kompakt|kompatibel|searchable|scan|roh|v\d+)\b', ' ', s)
    return re.sub(r'[^0-9a-zäöüß]+', '', s)


def _mtime(path):
    try:
        return time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getmtime(path)))
    except OSError:
        return ''


def book_info(folder):
    pages = glob.glob(os.path.join(folder, '[0-9][0-9][0-9].txt'))
    if not pages:
        return None
    log = os.path.join(folder, 'korrekturen.log')
    try:
        with open(log, 'rb') as f:
            corr = sum(1 for _ in f)
    except OSError:
        corr = 0
    newest = max(pages + ([log] if corr else []), key=os.path.getmtime)
    base, top = os.path.basename(folder), folder
    while os.path.basename(top).lower() in ('korr', 'ocr'):  # Arbeitsordner heißen oft so; der Buchtitel steht darüber
        top = os.path.dirname(top)
    name = base if top == folder else '%s – %s' % (os.path.basename(top), base)
    return dict(kind='book', path=folder, name=name, pages=len(pages), corrections=corr,
                images=os.path.isdir(os.path.join(folder, 'img')), mtime=_mtime(newest))


def _is_page_xml(path):
    try:
        with open(path, 'rb') as f:
            return b'PcGts' in f.read(800)
    except OSError:
        return False


def transkribus_dir(page_dir):
    """page_dir: Ordner 'page' eines Exports; der Export selbst ist der Ordner darüber."""
    xml = [f for f in glob.glob(os.path.join(page_dir, '*.xml'))]
    if not xml or not _is_page_xml(xml[0]):
        return None
    root = os.path.dirname(page_dir)
    title = None
    try:
        t = ET.parse(os.path.join(root, 'metadata.xml')).getroot().find('.//title')
        title = (t.text or '').strip() or None if t is not None else None
    except (OSError, ET.ParseError):
        pass
    imgs = sum(1 for f in os.listdir(root) if f.lower().endswith(IMG))
    return dict(kind='transkribus', path=root, name=title or os.path.basename(root), pages=len(xml), images=imgs >= len(xml) * 0.9,
                mtime=_mtime(max(xml, key=os.path.getmtime)))


def transkribus_zip(path):
    try:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            xml = [n for n in names if re.search(r'(^|/)page/[^/]+\.xml$', n, re.I)]
            if not xml:
                return None
            title = None
            meta = [n for n in names if n.lower().endswith('metadata.xml')]
            if meta:
                try:
                    t = ET.fromstring(z.read(meta[0])).find('.//title')
                    title = (t.text or '').strip() or None if t is not None else None
                except ET.ParseError:
                    pass
            imgs = sum(1 for n in names if n.lower().endswith(IMG))
            return dict(kind='transkribus', path=path, name=title or os.path.splitext(os.path.basename(path))[0], pages=len(xml),
                        images=imgs >= len(xml) * 0.9, mtime=_mtime(path))
    except (OSError, zipfile.BadZipFile):
        return None


def pdf_info(path, deep=True):
    d = dict(kind='pdf', path=path, name=os.path.splitext(os.path.basename(path))[0], pages=0, text=False, mtime=_mtime(path),
             size=os.path.getsize(path))
    if deep:
        try:
            import ocr
            d['pages'], d['text'] = ocr.pdf_count(path), ocr.pdf_has_text(path)
        except Exception:
            pass
    return d


def epub_info(path):
    d = dict(kind='epub', path=path, name=os.path.splitext(os.path.basename(path))[0], pages=0, pdf=None, mtime=_mtime(path))
    try:
        with zipfile.ZipFile(path) as z:
            opf = ET.fromstring(z.read('META-INF/container.xml')).find('.//{*}rootfile').get('full-path')
            t = ET.fromstring(z.read(opf)).find('.//{http://purl.org/dc/elements/1.1/}title')
            if t is not None and t.text:
                d['name'] = t.text.strip()
    except Exception:
        return None
    return d


def _pair(found):
    """EPUB und gleichlautendes PDF gehören zusammen: bevorzugt das durchsuchbare, dann das größere (bessere Bilder).
    Das gepaarte PDF bleibt in der Liste, rückt aber hinter das EPUB."""
    pdfs = [f for f in found if f['kind'] == 'pdf']
    for e in (f for f in found if f['kind'] == 'epub'):
        key = stem_key(os.path.basename(e['path']))
        same = [p for p in pdfs if key and stem_key(os.path.basename(p['path'])) == key
                and os.path.dirname(p['path']) == os.path.dirname(e['path'])]
        if same:
            best = max(same, key=lambda p: (p['text'], p['size']))
            e['pdf'], e['pdf_text'], e['pages'] = best['path'], best['text'], best['pages']


def _images_for(found):
    """Transkribus-Export ohne Bilder: ein Bilderordner mit genau so vielen Bildern wie Seiten passt dazu."""
    for t in (f for f in found if f['kind'] == 'transkribus' and not f['images']):
        fit = [i for i in found if i['kind'] == 'images' and i['pages'] == t['pages']]
        if fit:
            t['images_dir'] = max(fit, key=lambda i: i['mtime'])['path']


def scan_file(path):
    ext = os.path.splitext(path)[1].lower()
    name = os.path.basename(path).lower()
    folder = os.path.dirname(path)
    if ext == '.pdf':
        found = [pdf_info(path)] + [e for e in (epub_info(f) for f in glob.glob(os.path.join(folder, '*.epub'))) if e]
        _pair(found)
        keep = [f for f in found if f['kind'] == 'epub' and f.get('pdf') == path]
        return keep + [found[0]]  # gibt es ein gleichlautendes EPUB, wird es mit angeboten
    if ext == '.epub':
        e = epub_info(path)
        found = ([e] if e else []) + [pdf_info(f) for f in glob.glob(os.path.join(folder, '*.pdf'))[:12]]
        _pair(found)
        return found[:1] if e else []
    if ext == '.zip':
        t = transkribus_zip(path)
        return [t] if t else []
    if ext == '.xml' and _is_page_xml(path):
        t = transkribus_dir(folder)
        return [t] if t else []
    if re.fullmatch(r'\d{3}\.txt', name) or name in ('lines.json', 'korrekturen.log', 'whitelist.txt', 'lesezeichen.json'):
        b = book_info(folder)
        return [b] if b else []
    if ext in IMG:
        n = sum(1 for f in os.listdir(folder) if f.lower().endswith(IMG))
        return [dict(kind='images', path=folder, name=os.path.basename(folder), pages=n, mtime=_mtime(path))]
    return []


def scan_dir(root):
    found, nfiles, t0, npdf = [], 0, time.time(), 0
    for cur, dirs, files in os.walk(root):
        depth = cur[len(root):].count(os.sep)
        dirs[:] = [] if depth >= MAXDEPTH else sorted(d for d in dirs if not d.startswith('.') and d.lower() not in PRUNE)
        nfiles += len(files)
        if nfiles > MAXFILES or time.time() - t0 > MAXTIME:
            break
        b = book_info(cur)
        if b:
            found.append(b)
            dirs[:] = [d for d in dirs if d.lower() == 'scantailor']  # img/ gehört zum Buch; ein ScanTailor-Ergebnis ist ein eigener Fund
            continue
        if os.path.basename(cur).lower() == 'page':
            t = transkribus_dir(cur)
            if t:
                found.append(t)
                dirs[:] = []
                continue
        nimg = 0
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            p = os.path.join(cur, f)
            if ext == '.pdf':
                npdf += 1
                found.append(pdf_info(p, deep=npdf <= 12))
            elif ext == '.epub':
                e = epub_info(p)
                if e:
                    found.append(e)
            elif ext == '.zip':
                t = transkribus_zip(p)
                if t:
                    found.append(t)
            elif ext in IMG:
                nimg += 1
        parent = os.path.basename(os.path.dirname(cur)).lower()
        if nimg >= 2 and not any(f['kind'] == 'transkribus' and f['path'] == cur for f in found):
            found.append(dict(kind='images', path=cur, name=os.path.relpath(cur, root) if cur != root else os.path.basename(cur), pages=nimg,
                              mtime=_mtime(cur), scantailor=os.path.basename(cur).lower() == 'out' and parent == 'scantailor'))
    # derselbe Export als ZIP und entpackt: einmal genügt (der entpackte Ordner)
    dirs_t = {(f['name'], f['pages']) for f in found if f['kind'] == 'transkribus' and os.path.isdir(f['path'])}
    found = [f for f in found if not (f['kind'] == 'transkribus' and os.path.isfile(f['path']) and (f['name'], f['pages']) in dirs_t)]
    # Seitenbilder, die zu einem Transkribus-Export gehören (liegen im Exportordner), sind kein eigener Fund
    troots = [f['path'] for f in found if f['kind'] == 'transkribus' and f['images']]
    found = [f for f in found if not (f['kind'] == 'images' and f['path'] in troots)]
    # Liegt das Ergebnis von ScanTailor vor, ist sein Eingabeordner (die unbearbeiteten Seiten) keine Wahl mehr
    outs = [f['path'] for f in found if f.get('scantailor')]
    found = [f for f in found if not (f['kind'] == 'images' and any(o.startswith(f['path'] + os.sep) for o in outs))]
    _pair(found)
    _images_for(found)
    return found


def scan(path):
    """Liefert dict(path, found=[…]); der erste Fund ist die Empfehlung, 'newer' markiert Funde, die jünger sind als sie."""
    path = os.path.abspath(path)
    if not os.path.exists(path):
        raise ValueError('quelle_fehlt')
    found = scan_file(path) if os.path.isfile(path) else scan_dir(path)
    # Empfehlung: Bücher mit Korrekturen zuerst (dort steckt Arbeit), dann nach Art, innerhalb der Art das Jüngste
    found.sort(key=lambda f: f['mtime'], reverse=True)
    found.sort(key=lambda f: (0 if f.get('corrections') else 1, RANK[f['kind']], 0 if f.get('pdf') or f.get('text') else 1))
    # Wer eben ScanTailor hat laufen lassen, will dessen Ergebnis einlesen – die aufbereiteten Seiten sind der
    # ganze Zweck der Übung. Ein schon vorhandenes Buch geht nur dann vor, wenn darin Arbeit steckt.
    st = next((f for f in found if f.get('scantailor')), None)
    if st and found[0] is not st and not found[0].get('corrections') and st['mtime'] > found[0]['mtime']:
        found.remove(st)
        found.insert(0, st)
    for f in found[1:]:
        f['newer'] = bool(found[0]['mtime']) and f['mtime'] > found[0]['mtime']
    return dict(path=path, found=found[:40])
