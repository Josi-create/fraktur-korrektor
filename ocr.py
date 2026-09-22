"""PDF oder Bilderordner -> Buchordner: img/NNN.jpg|png, NNN.txt, lines.json, qualitaet.json – per Tesseract oder,
wenn das PDF schon durchsuchbar ist, aus seiner Textebene.
Tesseract und ScanTailor finden, Fraktur-Modell bei Bedarf laden, Qualität je Seite schätzen."""
import os, re, sys, json, glob, shutil, statistics, subprocess, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
import korrlib, pagexml

FRAKTUR = ['frak2021', 'deu_latf', 'deu_frak', 'frk', 'Fraktur']  # Modelle in der Reihenfolge der Vorliebe
MODELS = dict(fraktur=FRAKTUR, antiqua=['deu'] + FRAKTUR)  # frak2021 ist auch an Antiqua trainiert – Ersatz, wenn deu fehlt
MODEL_URL = 'https://ub-backup.bib.uni-mannheim.de/~stweil/tesstrain/frak2021/tessdata_fast/frak2021_0.905.traineddata'
TESSDATA = os.path.join(korrlib.HOME, 'tessdata')  # eigene Modelle; der Tesseract-Ordner ist oft nicht beschreibbar
BUNDLE = getattr(sys, '_MEIPASS', None)  # in der gepackten App liegen Tesseract und die Modelle bei


def bundled(*parts):
    """Pfad in der gepackten App – None, wenn ungepackt oder nicht vorhanden."""
    p = os.path.join(BUNDLE, *parts) if BUNDLE else None
    return p if p and os.path.exists(p) else None
SRCEXT = ('.png', '.jpg', '.jpeg', '.tif', '.tiff')
NOWIN = dict(creationflags=subprocess.CREATE_NO_WINDOW) if os.name == 'nt' else {}
DPI = 300
NOISE = re.compile(r"[|\\/_{}\[\]~^·.,;:'`´-]{1,3}")  # allein stehende Zeichen, wie sie die OCR aus Rändern und Flecken liest


def app_binary(path):
    """Aus einem Mac-Programmbündel die Datei, die wirklich startet. In Contents/MacOS liegen oft mehrere
    Einträge (ScanTailor bringt dort einen Ordner »config« mit), darum entscheidet die Info.plist."""
    p = path.rstrip('/')
    if not p.endswith('.app'):
        return path
    try:
        import plistlib
        with open(os.path.join(p, 'Contents', 'Info.plist'), 'rb') as f:
            name = plistlib.load(f).get('CFBundleExecutable')
        if name and os.path.isfile(os.path.join(p, 'Contents', 'MacOS', name)):
            return os.path.join(p, 'Contents', 'MacOS', name)
    except (OSError, ValueError):
        pass
    hits = [h for h in sorted(glob.glob(os.path.join(p, 'Contents', 'MacOS', '*'))) if os.path.isfile(h)]
    return hits[0] if hits else path


def _find(conf_key, names, places, first=None):
    c = korrlib.config().get(conf_key)
    if c and os.path.exists(c):
        return c
    if first:  # mitgeliefert: geht vor allem, was auf dem Rechner sonst herumliegt (nur die Wahl von Hand zählt mehr)
        return first
    for n in names:
        w = shutil.which(n)
        if w:
            return w
    for pat in places:
        hits = sorted(glob.glob(os.path.expandvars(os.path.expanduser(pat))))
        if hits:
            return app_binary(hits[-1])
    return None


def find_tesseract():
    return _find('tesseract', ['tesseract'], [
        r'%ProgramFiles%\Tesseract-OCR\tesseract.exe', r'%ProgramFiles(x86)%\Tesseract-OCR\tesseract.exe',
        r'%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe', '/opt/homebrew/bin/tesseract', '/usr/local/bin/tesseract'],
        bundled('tesseract', 'tesseract.exe' if os.name == 'nt' else 'tesseract'))


def find_scantailor():
    return _find('scantailor', ['scantailor', 'scantailor-advanced', 'ScanTailor'], [
        r'%LOCALAPPDATA%\Programs\ScanTailor*\scantailor*.exe', r'%ProgramFiles%\ScanTailor*\scantailor*.exe',
        r'%ProgramFiles%\Scan Tailor*\scantailor*.exe', r'%ProgramFiles(x86)%\Scan Tailor*\scantailor*.exe',
        '/Applications/ScanTailor*.app', '/Applications/Scan Tailor*.app',
        '/opt/homebrew/bin/scantailor', '/usr/local/bin/scantailor'])  # eine Mac-App sieht den PATH des Terminals nicht


def _langs(tess, tessdata=None):
    try:
        r = subprocess.run([tess, '--list-langs'] + (['--tessdata-dir', tessdata] if tessdata else []), capture_output=True, timeout=60, **NOWIN)
        return [l.strip() for l in r.stdout.decode('utf-8', 'replace').splitlines()[1:] if l.strip()]
    except (OSError, subprocess.TimeoutExpired):
        return []


def pick_model(tess, script='fraktur'):
    """(modell, tessdata-ordner oder None) für fraktur | antiqua; bei gleichem Rang gehen die eigenen Modelle vor."""
    dirs = [d for d in (TESSDATA, bundled('tesseract', 'tessdata')) if d and os.path.isdir(d)] + [None]
    have = [(d, _langs(tess, d)) for d in dirs]
    for m in MODELS.get(script, FRAKTUR):
        for d, langs in have:
            if m in langs:
                return m, d
    return None, None


def download_model():
    os.makedirs(TESSDATA, exist_ok=True)
    out = os.path.join(TESSDATA, 'frak2021.traineddata')
    with urllib.request.urlopen(MODEL_URL, timeout=120) as r, open(out + '.tmp', 'wb') as f:
        shutil.copyfileobj(r, f)
    os.replace(out + '.tmp', out)


def tools():
    """Was vorhanden ist – für die Anzeige im Importdialog."""
    tess = find_tesseract()
    try:
        import fitz  # noqa: F401
        pdf = True
    except ImportError:
        pdf = False
    try:
        korrlib.find_dic()
        dic = True
    except SystemExit:
        dic = False
    return dict(tesseract=tess, model=pick_model(tess)[0] if tess else None, antiqua=pick_model(tess, 'antiqua')[0] if tess else None,
                scantailor=find_scantailor(), pdf=pdf, dict=dic)


def clean(text):
    """Langes s, rundes r und überschriebenes e der Frakturmodelle in heutige Zeichen."""
    for a, b in (('ſ', 's'), ('ꝛ', 'r'), ('aͤ', 'ä'), ('oͤ', 'ö'), ('uͤ', 'ü'), ('Aͤ', 'Ä'), ('Oͤ', 'Ö'), ('Uͤ', 'Ü'), ('⸗', '-')):
        text = text.replace(a, b)
    return text


def hyphens(texts):
    """Trennstrich am Zeilenende -> '¬', wenn die nächste Zeile klein weitergeht (Fraktur-Doppelstrich wird oft als '=' gelesen)."""
    out = list(texts)
    for i in range(len(out) - 1):
        m = re.search(r'(?<=[A-Za-zÄÖÜäöüß])[-=]\s*$', out[i])
        if m and re.match(r'[a-zäöüß]', out[i + 1]):
            out[i] = out[i][:m.start()] + '¬'
    return out


def ocr_image(tess, img, model, tessdata=None, dpi=DPI):
    """Eine Seite erkennen. Liefert (zeilen, wörter): Zeilen als dicts text, x0, x1, y0, y1, bl, conf;
    Wörter als (konfidenz, text, steht_am_zeilenende)."""
    cmd = [tess, img, 'stdout', '-l', model, '--psm', '3', '--dpi', str(int(dpi))] + (['--tessdata-dir', tessdata] if tessdata else [])
    cmd += ['-c', 'tessedit_create_tsv=1']  # nicht die Konfigurationsdatei "tsv": die fehlt im eigenen Modellordner
    r = subprocess.run(cmd, capture_output=True, env=dict(os.environ, OMP_THREAD_LIMIT='1'), **NOWIN)
    if r.returncode:
        raise RuntimeError(r.stderr.decode('utf-8', 'replace')[-300:])
    lines = {}
    for row in r.stdout.decode('utf-8', 'replace').splitlines()[1:]:
        f = row.split('\t')
        if len(f) < 12 or f[0] != '5' or not f[11].strip():
            continue
        x, y, w, h, conf, t = int(f[6]), int(f[7]), int(f[8]), int(f[9]), float(f[10]), clean(f[11].strip())
        lines.setdefault((f[2], f[3], f[4]), []).append((x, y, w, h, conf, t))
    out, words = [], []
    for ws in lines.values():
        ws.sort()
        words += [(w[4], w[5], len(ws) >= 4 and w is ws[-1]) for w in ws]
        y0, y1 = min(w[1] for w in ws), max(w[1] + w[3] for w in ws)
        out.append(dict(text=' '.join(w[5] for w in ws), x0=ws[0][0], x1=max(w[0] + w[2] for w in ws), y0=y0, y1=y1,
                        bl=int(statistics.median(w[1] + w[3] for w in ws)), conf=round(sum(w[4] for w in ws) / len(ws), 1)))
    return out, words


def page_quality(words):
    """Mittlere Wortkonfidenz (nach Wortlänge gewichtet), Anteil der Wörter, die das Wörterbuch kennt, und
    ends: um wie viel die Konfidenz der Wörter am Zeilenende unter der der übrigen liegt (am Bund gestauchte Zeilen)."""
    toks = [w for c, t, e in words for w in korrlib.WORD.findall(t) if len(w) > 1]
    ok = lambda w: korrlib.in_dict(w, korrlib.DICS)  # die Ampel misst die Texterkennung, nicht die Rechtschreibung: jede Epoche gilt
    if words and words[0][0] is None:  # Text aus dem PDF übernommen: keine Konfidenz bekannt
        return dict(conf=None, words=len(toks), dict=round(sum(ok(w) for w in toks) / len(toks), 3) if toks else 0.0, ends=0.0)
    n = sum(len(t) for c, t, e in words)
    end, mid = [c for c, t, e in words if e], [c for c, t, e in words if not e]
    return dict(conf=round(sum(c * len(t) for c, t, e in words) / n, 1) if n else 0.0, words=len(toks),
                dict=round(sum(ok(w) for w in toks) / len(toks), 3) if toks else 0.0,
                ends=round(sum(mid) / len(mid) - sum(end) / len(end), 1) if end and mid else 0.0)


def rating(pages):
    """Ampel fürs ganze Buch aus den Seitenwerten: gruen | gelb | rot, dazu die Mediane. Seiten fast ohne Text zählen nicht.
    Geeicht an einem Frakturbuch von 1928: korrigierter Text hat Wörterbuchquote 0,95, Transkribus roh 0,88,
    Tesseract auf einem Handy-Scan 0,83 bei Konfidenz 81. Grün heißt: etwa so gut wie Transkribus.
    ends: Seiten, deren Zeilenenden deutlich schwächer sind als der Rest (Hinweis auf ScanTailor)."""
    ps = [p for p in pages.values() if p['words'] >= 20]
    if not ps:
        return dict(level='rot', conf=0, dict=0, weak=[], ends=[])
    dq = statistics.median(p['dict'] for p in ps)
    if ps[0]['conf'] is None:  # übernommene Textebene: nur die Wörterbuchquote zählt
        weak = sorted(pg for pg, p in pages.items() if p['words'] >= 20 and p['dict'] < 0.78)
        return dict(level='gruen' if dq >= 0.88 else 'rot' if dq < 0.78 else 'gelb', conf=None, dict=round(dq, 3), weak=weak, ends=[])
    conf = statistics.median(p['conf'] for p in ps)
    level = 'gruen' if conf >= 85 and dq >= 0.88 else 'rot' if conf < 75 or dq < 0.78 else 'gelb'
    weak = sorted(pg for pg, p in pages.items() if p['words'] >= 20 and (p['conf'] < 75 or p['dict'] < 0.78))
    ends = sorted(pg for pg, p in pages.items() if p['words'] >= 20 and p['ends'] >= 10)
    return dict(level=level, conf=round(conf, 1), dict=round(dq, 3), weak=weak, ends=ends)


def render_pdf(pdf, n, out):
    """Seite n (ab 0) als Graustufen-JPEG mit 300 dpi."""
    import fitz
    with fitz.open(pdf) as d:
        d[n].get_pixmap(dpi=DPI, colorspace=fitz.csGRAY).save(out, jpg_quality=85)


def pdf_count(pdf):
    import fitz
    with fitz.open(pdf) as d:
        return d.page_count


def pdf_has_text(pdf):
    """Durchsuchbares PDF? Stichprobe über das Buch: mindestens die Hälfte der Seiten trägt Text."""
    import fitz
    with fitz.open(pdf) as d:
        ns = sorted({int(k * (d.page_count - 1) / 11) for k in range(12)}) if d.page_count else []
        return bool(ns) and sum(len(d[n].get_text('words')) >= 10 for n in ns) * 2 >= len(ns)


def pdf_page(d, n, stem, text=False):
    """Seite n (ab 0) des geöffneten PDF als Bild nach stem.jpg|png. Besteht die Seite aus genau einem ungedrehten,
    seitenfüllenden JPEG/PNG (der Normalfall bei Scans), wird es unverändert entnommen – schneller und ohne
    Qualitätsverlust; sonst wird die Seite mit 300 dpi berechnet.
    Liefert (bildpfad, breite, höhe, dpi, wörter); wörter = [(x0, y0, x1, y1, text, grundlinie)] in Bildpixeln, wenn text."""
    import fitz
    page = d[n]
    img = None
    ims = page.get_images(full=True)
    if len(ims) == 1 and page.rotation == 0 and not ims[0][1]:
        xref, _, w, h, *_ = ims[0]
        r = page.get_image_bbox(ims[0])  # ohne das Bild zu dekodieren (get_image_rects täte das: 0,1 s je Seite)
        if not r.is_infinite and abs(r & page.rect) >= 0.9 * abs(page.rect) and abs(w / h / (r.width / r.height) - 1) < 0.03:
            if ims[0][8] == 'DCTDecode':
                img, data = stem + '.jpg', d.xref_stream_raw(xref)  # der Datenstrom ist die JPEG-Datei
            else:
                x = d.extract_image(xref)
                ext = dict(jpeg='.jpg', jpg='.jpg', png='.png').get(x['ext'])
                img, data = (stem + ext, x['image']) if ext else (None, None)
            if img:
                with open(img, 'wb') as f:
                    f.write(data)
    if img is None:
        img, r = stem + '.jpg', page.rect
        pix = page.get_pixmap(dpi=DPI, colorspace=fitz.csGRAY)
        pix.save(img, jpg_quality=85)
        w, h = pix.width, pix.height
    sx, sy = w / r.width, h / r.height
    words = []
    if text:
        tp = page.get_textpage()
        # Grundlinie je PDF-Zeile: verlässlicher als die Wortrahmen, die bei Störzeichen über mehrere Zeilen reichen
        base = {(b['number'], k): l['spans'][0]['origin'][1] for b in page.get_text('dict', textpage=tp)['blocks'] if b['type'] == 0
                for k, l in enumerate(b['lines']) if l['spans'] and abs(l['dir'][0]) > 0.95}
        for x0, y0, x1, y1, t, b, l, _ in page.get_text('words', textpage=tp):
            if t.strip() and (b, l) in base:
                words.append(((x0 - r.x0) * sx, (y0 - r.y0) * sy, (x1 - r.x0) * sx, (y1 - r.y0) * sy, clean(t), (base[b, l] - r.y0) * sy))
    return img, w, h, 72 * sx, words


def group_words(words):
    """Wörter einer Textebene (x0, y0, x1, y1, text, grundlinie) zu Zeilen ordnen: Was auf derselben Grundlinie steht,
    gehört zusammen – das PDF selbst zerlegt Zeilen oft in Bruchstücke. Eine Lücke von mehr als drei Zeilenhöhen
    trennt Spalten (zweispaltige Fußnoten)."""
    if not words:
        return []
    hmed = statistics.median(w[3] - w[1] for w in words)
    rows = []
    for w in sorted(words, key=lambda w: w[5]):
        if rows and abs(w[5] - rows[-1]['bl']) < 0.35 * hmed:
            r = rows[-1]
            r['ws'].append(w); r['bl'] += (w[5] - r['bl']) / len(r['ws'])
        else:
            rows.append(dict(bl=w[5], ws=[w]))
    out = []
    for r in rows:
        part = []
        for w in sorted(r['ws']) + [None]:
            if w is None or (part and w[0] - part[-1][2] > 3 * hmed):
                while part and NOISE.fullmatch(part[0][4]): del part[0]    # mitgescannter Seitenrand: | \_ / } am Zeilenrand
                while part and NOISE.fullmatch(part[-1][4]): del part[-1]
                if not part:
                    continue
                bl = statistics.median(x[5] for x in part)
                out.append(dict(text=' '.join(x[4] for x in part), x0=round(part[0][0]), x1=round(max(x[2] for x in part)),
                                # Rahmen an der Grundlinie ausrichten: Störzeichen blähen die Wortrahmen auf
                                y0=round(max(min(x[1] for x in part), bl - 1.1 * hmed)), y1=round(min(max(x[3] for x in part), bl + 0.4 * hmed)),
                                bl=round(bl)))
                part = []
            if w is not None:
                part.append(w)
    return out


def image_files(folder):
    return sorted(f for f in glob.glob(os.path.join(folder, '*')) if f.lower().endswith(SRCEXT))


def copy_image(src, stem):
    """Seitenbild in den Buchordner; TIFF (kann der Browser nicht) wird PNG. Liefert den Zielpfad."""
    ext = os.path.splitext(src)[1].lower()
    if ext in ('.tif', '.tiff'):
        import fitz
        fitz.Pixmap(src).save(stem + '.png')
        return stem + '.png'
    shutil.copyfile(src, stem + ('.jpg' if ext == '.jpeg' else ext))
    return stem + ('.jpg' if ext == '.jpeg' else ext)


def page_lines(lines, h):
    """Erkannte Zeilen einer Seite in Lesereihenfolge bringen, Kopfzeile und Fußnoten erkennen, Trennungen setzen."""
    pagexml.classify(lines, h / 3508)
    for kind in ('body', 'fn'):  # Trennungen je Textteil, nicht vom Haupttext in die Fußnoten
        part = [d for d in lines if d['kind'] == kind]
        for d, t in zip(part, hyphens([d['text'] for d in part])):
            d['text'] = t
    return lines


def recognize_page(folder, pg, source, n=1, script='fraktur', progress=lambda done, total, msg: None):
    """Eine Seite eines Buchs neu machen (#52): Seitenbild aus einer Bilddatei oder aus Seite n (ab 1) eines PDF, dann
    nur diese Seite erkennen – mit Tesseract; ohne Tesseract mit der Textebene des PDF, wenn es eine hat. Schreibt
    NNN.txt, das Bild und die Seite in lines.json und qualitaet.json. Liefert dict(lines, words, quality)."""
    is_pdf = source.lower().endswith('.pdf')
    tess = find_tesseract()
    stem = free_slot(folder, pg)
    if is_pdf:
        try:
            import fitz
        except ImportError:
            raise ValueError('kein_pymupdf')
        with fitz.open(source) as d:
            if not 1 <= n <= d.page_count:
                raise ValueError('keine_seiten')
            img, w, h, dpi, words = pdf_page(d, n - 1, stem, text=not tess)
    elif source.lower().endswith(SRCEXT):
        img, dpi, words = copy_image(source, stem), DPI, []
        w, h = image_size(img) or (0, 0)
        if not (w and h):
            raise ValueError('quelle_fehlt')
    else:
        raise ValueError('quelle_fehlt')
    progress(1, 2, 'ocr')
    if tess:
        model, tessdata = pick_model(tess, script)
        if not model:
            progress(0, 2, 'modell')
            try:
                download_model()
            except OSError:
                raise ValueError('modell_laden')
            model, tessdata = pick_model(tess, script)
            if not model:
                raise ValueError('modell_laden')
        lines, words = ocr_image(tess, img, model, tessdata, dpi)
    elif words:
        lines, words = group_words(words), [(None, x[4], False) for x in words]
    else:
        raise ValueError('kein_tesseract')
    page_lines(lines, h)
    with open(os.path.join(folder, pg + '.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(pagexml.page_text(lines)) + '\n')
    geo = pagexml.load_json(folder, 'lines.json', {})
    geo[pg] = dict(w=w, h=h, lines=lines)
    with open(os.path.join(folder, 'lines.json'), 'w', encoding='utf-8') as f:
        json.dump(dict(sorted(geo.items())), f, ensure_ascii=False)
    q = pagexml.load_json(folder, 'qualitaet.json', {})
    if q.get('pages'):  # die Ampel des Buchs kennt diese Seite jetzt neu
        q['pages'][pg] = page_quality(words)
        q['rating'] = rating(q['pages'])
        with open(os.path.join(folder, 'qualitaet.json'), 'w', encoding='utf-8') as f:
            json.dump(q, f, ensure_ascii=False, indent=1)
    korrlib.save_cache()
    progress(2, 2, 'ocr')
    return dict(lines=len(lines), words=len(words), quality=page_quality(words))


def build(source, out, progress=lambda done, total, msg: None, cancelled=lambda: False, script='fraktur', textlayer=False):
    """source: PDF-Datei oder Ordner mit Seitenbildern. Schreibt den Buchordner out; liefert dict(pages, quality).
    textlayer: den Text eines durchsuchbaren PDF übernehmen, statt ihn neu zu erkennen (braucht kein Tesseract).
    Fehler als ValueError mit Schlüssel: kein_tesseract, kein_pymupdf, quelle_fehlt, keine_seiten, modell_laden, abgebrochen."""
    is_pdf = os.path.isfile(source) and source.lower().endswith('.pdf')
    textlayer = textlayer and is_pdf
    tess = find_tesseract()
    if not tess and not textlayer:
        raise ValueError('kein_tesseract')
    if is_pdf:
        try:
            total = pdf_count(source)
        except ImportError:
            raise ValueError('kein_pymupdf')
        except Exception:
            raise ValueError('quelle_fehlt')
    elif os.path.isdir(source):
        files = image_files(source)
        total = len(files)
    else:
        raise ValueError('quelle_fehlt')
    if not total:
        raise ValueError('keine_seiten')
    if total > 999:
        raise ValueError('zu_viele_seiten')
    model, tessdata = ('textebene', None) if textlayer else pick_model(tess, script)
    if not model:
        progress(0, total, 'modell')
        try:
            download_model()
        except OSError:
            raise ValueError('modell_laden')
        model, tessdata = pick_model(tess, script)
        if not model:
            raise ValueError('modell_laden')
    os.makedirs(os.path.join(out, 'img'), exist_ok=True)

    def finish(pg, w, h, lines, words):
        page_lines(lines, h)
        with open(os.path.join(out, pg + '.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(pagexml.page_text(lines)) + '\n')
        geo[pg] = dict(w=w, h=h, lines=lines)
        quality[pg] = page_quality(words)

    def one(n):
        if cancelled():
            return None
        pg = '%03d' % (n + 1)
        stem = os.path.join(out, 'img', pg)
        if is_pdf:
            import fitz
            with fitz.open(source) as d:  # je Aufruf öffnen: ein PDF-Objekt verträgt keine mehreren Threads
                img, w, h, dpi, _ = pdf_page(d, n, stem)
        else:
            img, dpi = copy_image(files[n], stem), DPI
            w, h = image_size(img)
        lines, words = ocr_image(tess, img, model, tessdata, dpi)
        return pg, w, h, lines, words

    geo, quality, done = {}, {}, 0
    if textlayer:
        import fitz
        with fitz.open(source) as d:
            for n in range(total):
                if cancelled():
                    break
                pg = '%03d' % (n + 1)
                img, w, h, dpi, words = pdf_page(d, n, os.path.join(out, 'img', pg), text=True)
                finish(pg, w, h, group_words(words), [(None, x[4], False) for x in words])
                progress(n + 1, total, 'text')
    else:
        with ThreadPoolExecutor(max_workers=max(1, (os.cpu_count() or 2) - 1)) as ex:
            # in der Reihenfolge des Fertigwerdens: eine langsame Seite (Abbildung) hält die Anzeige nicht auf
            for fu in as_completed([ex.submit(one, n) for n in range(total)]):
                r = fu.result()
                if r is None:
                    continue
                finish(*r)
                done += 1
                progress(done, total, 'ocr')
    geo, quality = dict(sorted(geo.items())), dict(sorted(quality.items()))
    if cancelled():
        cleanup(out)
        raise ValueError('abgebrochen')
    with open(os.path.join(out, 'lines.json'), 'w', encoding='utf-8') as f:
        json.dump(geo, f, ensure_ascii=False)
    quelle = ['scantailor'] if not is_pdf and os.path.basename(os.path.dirname(source.rstrip('/\\'))).lower() == 'scantailor' else []
    q = dict(model=model, rating=rating(quality), quelle=quelle + ['textebene' if textlayer else 'tesseract'], pages=quality)
    with open(os.path.join(out, 'qualitaet.json'), 'w', encoding='utf-8') as f:
        json.dump(q, f, ensure_ascii=False, indent=1)
    if not is_pdf:  # damit ein Transkribus-Export später wiederfindet, welches Bild welche Seite war
        pagexml.save_origin(out, {'%03d' % (n + 1): os.path.basename(files[n]) for n in range(total)})
    korrlib.save_cache()
    return dict(pages=total, quality=q['rating'])


def rate_book(folder, quelle=(), model='transkribus'):
    """Ampel und Wörterbuchquote für einen Text, dessen Erkennung keine Konfidenz mitliefert – Transkribus etwa
    sagt nichts darüber, wie sicher es sich war. Gemessen wird, wie viele Wörter das Wörterbuch kennt; das ist
    dieselbe Zahl, die der Leser später als rote Wörter sieht. quelle: die Schritte, die zu diesem Text führten."""
    quality = {}
    for f in sorted(glob.glob(os.path.join(folder, '[0-9][0-9][0-9].txt'))):
        with open(f, encoding='utf-8') as fh:
            lines = [korrlib.mask(l.rstrip('\n')) for l in fh]
        quality[os.path.basename(f)[:3]] = page_quality([(None, l, False) for l in lines if l.strip() not in ('', '---')])
    if not quality:
        return None
    q = dict(model=model, rating=rating(quality), quelle=list(quelle), pages=quality)
    with open(os.path.join(folder, 'qualitaet.json'), 'w', encoding='utf-8') as f:
        json.dump(q, f, ensure_ascii=False, indent=1)
    korrlib.save_cache()
    return q['rating']


def cleanup(out):
    """Nur das Erzeugte wieder entfernen – im Buchordner kann schon ein ScanTailor-Projekt liegen."""
    shutil.rmtree(os.path.join(out, 'img'), ignore_errors=True)
    for f in glob.glob(os.path.join(out, '[0-9][0-9][0-9].txt')) + [os.path.join(out, n) for n in ('lines.json', 'qualitaet.json', 'quellen.json')]:
        try: os.remove(f)
        except OSError: pass
    try: os.rmdir(out)
    except OSError: pass


def free_slot(folder, pg):
    """Platz für das Seitenbild einer Seite schaffen: ein vorhandenes weicht dem neuen."""
    for f in glob.glob(os.path.join(folder, 'img', pg + '.*')):
        os.remove(f)
    return os.path.join(folder, 'img', pg)


def images_from_book(folder, other, progress=lambda done, total, msg: None):
    """Die Seitenbilder eines anderen Buchs übernehmen. Welches Bild zu welcher Seite gehört, verrät der Text:
    In beiden Büchern steht dasselbe Werk, nur anders erkannt. Darum wird hier jede Seite dieses Buchs einer
    Seite des anderen zugeordnet – so darf das andere ruhig mehr Seiten haben (eine Deckelhälfte etwa, für die
    im Transkribus-Export kein Text steht)."""
    ziel = pagexml.book_pages(folder)
    mein = pagexml.load_json(folder, 'quellen.json', {})

    def text_of(pg):
        try:
            with open(os.path.join(folder, pg + '.txt'), encoding='utf-8') as f:
                return f.read()
        except OSError:
            return ''

    hit, how = pagexml.match_to_pages(other, ziel, lambda pg: (mein.get(pg, ''),), text_of=text_of)
    fremd, n = pagexml.load_json(other, 'quellen.json', {}), 0
    for k, pg in enumerate(ziel):
        src = sorted(glob.glob(os.path.join(other, 'img', hit[pg] + '.*'))) if pg in hit else []
        if src:
            copy_image(src[0], free_slot(folder, pg))
            mein.setdefault(pg, fremd.get(hit[pg]) or os.path.basename(src[0]))
            n += 1
        progress(k + 1, len(ziel), 'bilder')
    if not n:
        raise ValueError('keine_seiten')
    pagexml.save_origin(folder, mein)
    return dict(added=n, pages=len(ziel), how=how)


def add_images(folder, source, progress=lambda done, total, msg: None):
    """Seitenbilder zu einem Buch legen, das keine hat – etwa nach einem Transkribus-Export ohne Bilder. Quelle ist
    ein Bilderordner oder das PDF, aus dem die Seiten stammen. Zugeordnet wird über die Namen, nicht blind der
    Reihe nach. Liefert dict(added, pages, how)."""
    pages = pagexml.book_pages(folder)
    if not pages:
        raise ValueError('quelle_fehlt')
    os.makedirs(os.path.join(folder, 'img'), exist_ok=True)
    frei = lambda pg: free_slot(folder, pg)

    # Seitenbilder liegen selten allein herum: Meist gehören sie zu einem anderen Buch dieses Programms – und
    # das hat Text. Dann ist die Zuordnung eine Frage des Wortlauts, nicht der Dateinamen.
    nachbar = os.path.dirname(source) if os.path.basename(source).lower() == 'img' else source
    if os.path.isdir(nachbar) and os.path.abspath(nachbar) != os.path.abspath(folder) and pagexml.book_pages(nachbar):
        return images_from_book(folder, nachbar, progress)

    if os.path.isfile(source) and source.lower().endswith('.pdf'):
        try:
            import fitz
        except ImportError:
            raise ValueError('kein_pymupdf')
        if pdf_count(source) != len(pages):  # Seite für Seite, also muss die Zahl stimmen
            raise ValueError('seiten_passen_nicht')
        with fitz.open(source) as d:
            for n, pg in enumerate(pages):
                pdf_page(d, n, frei(pg))
                progress(n + 1, len(pages), 'bilder')
        return dict(added=len(pages), pages=len(pages), how='reihenfolge')

    files = image_files(source) if os.path.isdir(source) else []
    if not files:
        raise ValueError('keine_seiten')
    hit, how = pagexml.match_to_pages(folder, files, lambda f: (f,))
    origin = pagexml.load_json(folder, 'quellen.json', {})
    for n, f in enumerate(sorted(hit)):
        copy_image(f, frei(hit[f]))
        origin.setdefault(hit[f], os.path.basename(f))
        progress(n + 1, len(hit), 'bilder')
    pagexml.save_origin(folder, origin)
    return dict(added=len(hit), pages=len(pages), how=how)


def image_size(path):
    import fitz
    p = fitz.Pixmap(path)
    return p.width, p.height


def export_pages(pdf, folder, progress=lambda done, total, msg: None, cancelled=lambda: False):
    """PDF-Seiten als PNG für ScanTailor (das keine PDFs liest)."""
    import fitz
    os.makedirs(folder, exist_ok=True)
    with fitz.open(pdf) as d:
        for n, page in enumerate(d):
            if cancelled():
                raise ValueError('abgebrochen')
            page.get_pixmap(dpi=DPI).save(os.path.join(folder, 'seite_%03d.png' % (n + 1)))
            progress(n + 1, d.page_count, 'export')
    return n + 1


def launch(exe):
    subprocess.Popen([exe], close_fds=True, **(dict(creationflags=subprocess.DETACHED_PROCESS) if os.name == 'nt' else dict(start_new_session=True)))


def to_clipboard(text):
    """Pfad in die Zwischenablage. Im Dateidialog eines anderen Programms ließe er sich sonst nur abtippen –
    und der Hinweis im Browser ist verdeckt, sobald das andere Programm im Vordergrund ist."""
    cmd = dict(darwin=['pbcopy'], win32=['clip']).get(sys.platform) or ['xclip', '-selection', 'clipboard']
    try:
        return subprocess.run(cmd, input=text.encode('utf-8'), timeout=15, **NOWIN).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def reveal(folder):
    """Ordner im Dateimanager zeigen – von dort lässt er sich in das andere Programm ziehen."""
    cmd = dict(darwin=['open', folder], win32=['explorer', folder]).get(sys.platform) or ['xdg-open', folder]
    try:
        subprocess.Popen(cmd, **NOWIN)
        return True
    except OSError:
        return False


if __name__ == '__main__':  # py ocr.py <pdf-oder-bilderordner> <buchordner>
    print(build(sys.argv[1], sys.argv[2], progress=lambda d, t, m: print('\r%s %d/%d' % (m, d, t), end='', flush=True)))
