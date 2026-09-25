"""Ein Buch als PDF sichern und wieder einlesen (#58).

Das PDF zeigt die Seitenbilder wie jeder Scan, darüber liegt der Text unsichtbar (Suchen, Kopieren, Vorlesen in
jedem PDF-Reader), und der ganze Arbeitsstand – Seitentexte, Zeilenlage, Wortliste, Lesezeichen, Protokoll,
Einstellungen – steckt als Anhang »fraktur-korrektor.zip« im PDF. PDF kennt solche Anhänge seit Version 1.4; Acrobat
und Firefox zeigen sie, andere Reader übergehen sie. So wandert ein Buch samt Arbeit als eine Datei auf einen
anderen Rechner, und dort erkennt dieses Programm den Anhang und macht daraus wieder einen Buchordner.

Die Seitenbilder werden unverändert eingepackt (JPEG als DCTDecode-Strom, PNG verlustfrei) und beim Einlesen ebenso
wieder entnommen – ocr.pdf_page tut das schon für Bibliotheks-PDFs. Die Textebene ist zeilengenau: lines.json kennt
keine Wortkästen. Bücher ohne Seitenbilder bekommen Seiten mit sichtbarem Text."""
import os, io, re, json, glob, time, zipfile
import korrlib, pagexml, ocr

ANHANG = 'fraktur-korrektor.zip'
MANIFEST = 'fraktur-korrektor.json'
# Was außer den Seitentexten in den Anhang gehört. Nicht dabei: img/ (das sind die PDF-Seiten selbst), vorher-*.zip
# (ersetzte Fassungen), scantailor/ (Zwischenschritte).
DATEIEN = ('lines.json', 'quellen.json', 'buch.json', 'whitelist.txt', 'lesezeichen.json', 'korrekturen.log', 'qualitaet.json', 'autokorr.log')
DPI = 300          # Seitengröße im PDF: Bildpixel bei 300 dpi – nur Anzeige, der Maßstab der Zeilen kommt vom Bild selbst
A4 = (595.0, 842.0)


def _fitz():
    try:
        import fitz
    except ImportError:
        raise ValueError('kein_pymupdf')
    return fitz


def _text(l):
    """Der Wortlaut einer Zeile ohne Auszeichnung und ohne die Zeichen, die nur dem Programm gelten."""
    if l == '---':
        return ''
    if l.startswith('#'):
        l = l.lstrip('#')
    return ' '.join(korrlib.TAG.sub(' ', l).split())


def _fit(font, text, width, height):
    """Schriftgrad, mit dem der Text in den Zeilenrahmen passt – die Suche im Reader markiert dann die richtige Stelle."""
    w1 = font.text_length(text, fontsize=1) or 1.0
    return max(1.0, min(width / w1, height * 0.85))


def _manifest(folder, title, version, settings):
    pages = pagexml.book_pages(folder)
    seiten = {}
    for pg in pages:
        img = sorted(f for f in glob.glob(os.path.join(folder, 'img', pg + '.*')) if f.lower().endswith(pagexml.IMGEXT))
        seiten[pg] = os.path.basename(img[0]) if img else None
    try:
        with open(os.path.join(folder, 'korrekturen.log'), 'rb') as f:
            corr = sum(1 for _ in f)
    except OSError:
        corr = 0
    return dict(programm='Fraktur-Korrektor', version=version, gesichert=time.strftime('%Y-%m-%d %H:%M:%S'), titel=title,
                kennung=settings.get('kennung'), korrekturen=corr, seiten=seiten)


def _anhang(folder, manifest):
    """Der Arbeitsstand als ZIP im Speicher."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr(MANIFEST, json.dumps(manifest, ensure_ascii=False, indent=1))
        for pg in manifest['seiten']:
            z.write(os.path.join(folder, pg + '.txt'), pg + '.txt')
        for n in DATEIEN:
            p = os.path.join(folder, n)
            if os.path.isfile(p):
                z.write(p, n)
    return buf.getvalue()


def save(book, out, version='', progress=lambda done, total, msg: None, cancelled=lambda: False):
    """Das Buch (ein server.Book) als PDF nach out schreiben; liefert dict(pages, images, corrections, file, size).
    Erst in eine Nachbardatei, dann umbenennen: Ein Abbruch lässt kein halbes PDF unter dem richtigen Namen zurück."""
    fitz = _fitz()
    folder = book.folder
    manifest = _manifest(folder, book.title, version, book.settings)
    if not manifest['seiten']:
        raise ValueError('quelle_fehlt')
    font = fitz.Font('helv')  # eingebettet wird sie einmal je PDF; die Textebene selbst bleibt unsichtbar
    doc = fitz.open()
    pages = list(manifest['seiten'])
    for n, pg in enumerate(pages):
        if cancelled():
            doc.close()
            raise ValueError('abgebrochen')
        lines = korrlib.read_page(os.path.join(folder, pg + '.txt'))
        img = manifest['seiten'][pg]
        if img:
            w, h = book.img_size(pg) or (0, 0)
            if not (w and h):  # unlesbares Bild: die Seite bekommt nur ihren Text
                img = manifest['seiten'][pg] = None
        if img:
            s = 72.0 / DPI
            page = doc.new_page(width=w * s, height=h * s)
            page.insert_image(page.rect, filename=os.path.join(folder, 'img', img))
            geo = book.geo_lines(pg, lines)
            tw, rest = fitz.TextWriter(page.rect), []
            for k, l in enumerate(lines):
                text = _text(l)
                if not text:
                    continue
                g = geo[k] if geo and k < len(geo) else None
                if g and g['x1'] > g['x0'] and g['y1'] > g['y0']:
                    fs = _fit(font, text, (g['x1'] - g['x0']) * s, (g['y1'] - g['y0']) * s)
                    tw.append((g['x0'] * s, g['y1'] * s - 0.2 * fs), text, font=font, fontsize=fs)
                else:
                    rest.append(text)
            # Zeilen ohne bekannte Lage (keine lines.json, Zeilenzahl passt nicht) stehen unsichtbar der Reihe nach
            # über die Seite verteilt – so bleibt der Text wenigstens durchsuchbar
            if rest:
                step = (page.rect.height - 40) / max(len(rest), 1)
                for k, text in enumerate(rest):
                    fs = _fit(font, text, page.rect.width - 40, min(step, 12))
                    tw.append((20, 30 + k * step), text, font=font, fontsize=fs)
            tw.write_text(page, render_mode=3)  # 3 = unsichtbar
        else:
            page = doc.new_page(width=A4[0], height=A4[1])
            texts = [_text(l) for l in lines]
            step = min(15.0, (A4[1] - 100) / max(len(texts), 1))
            tw = fitz.TextWriter(page.rect)
            for k, text in enumerate(texts):
                if text:
                    tw.append((60, 60 + k * step), text, font=font, fontsize=min(11.0, _fit(font, text, A4[0] - 120, step)))
            tw.write_text(page)
        progress(n + 1, len(pages), 'pdf')
    # Die mit H ausgezeichneten Überschriften werden die Lesezeichen des PDFs – das Inhaltsverzeichnis in der Seitenleiste.
    # Ein PDF-Lesezeichen darf keine Ebene überspringen, die Tiefe ergibt sich deshalb aus der Abfolge: Ebene 1 → 3 wird
    # 1 → 2, ein Buch nur mit Ebene 2 hat lauter Einträge der obersten Stufe.
    index, toc, stack = {pg: n + 1 for n, pg in enumerate(pages)}, [], []
    for h in book.headings():
        if h['page'] in index:
            while stack and stack[-1] >= h['level']:
                stack.pop()
            stack.append(h['level'])
            toc.append([len(stack), h['text'], index[h['page']]])
    if toc:
        doc.set_toc(toc)
    doc.embfile_add(ANHANG, _anhang(folder, manifest), filename=ANHANG, ufilename=ANHANG, desc='Fraktur-Korrektor: Arbeitsstand')
    doc.set_metadata(dict(title=book.title, author=book.settings.get('autor') or '', creator='Fraktur-Korrektor ' + version,
                          producer='Fraktur-Korrektor'))
    doc.subset_fonts()
    tmp = out + '.tmp'
    try:
        doc.save(tmp, garbage=3, deflate=True)
    finally:
        doc.close()
    os.replace(tmp, out)
    return dict(pages=len(pages), images=sum(1 for v in manifest['seiten'].values() if v), corrections=manifest['korrekturen'],
                file=out, size=os.path.getsize(out))


def info(pdf):
    """Das Manifest, wenn pdf von diesem Programm gesichert wurde – sonst None. Liest nur den Anhang, nicht die Seiten."""
    try:
        fitz = _fitz()
        with fitz.open(pdf) as d:
            if ANHANG not in d.embfile_names():
                return None
            with zipfile.ZipFile(io.BytesIO(d.embfile_get(ANHANG))) as z:
                m = json.loads(z.read(MANIFEST).decode('utf-8'))
        return m if isinstance(m, dict) and isinstance(m.get('seiten'), dict) else None
    except Exception:
        return None


def member(pdf, name):
    """Eine Datei aus dem Anhang (etwa korrekturen.log) als Bytes – None, wenn es sie dort nicht gibt."""
    try:
        fitz = _fitz()
        with fitz.open(pdf) as d:
            if ANHANG not in d.embfile_names():
                return None
            with zipfile.ZipFile(io.BytesIO(d.embfile_get(ANHANG))) as z:
                return z.read(name) if name in z.namelist() else None
    except Exception:
        return None


def members(pdf):
    """Der ganze Anhang als dict Name -> Bytes (nur Seitentexte und die bekannten Dateien) – leer, wenn es keinen gibt."""
    try:
        fitz = _fitz()
        with fitz.open(pdf) as d:
            if ANHANG not in d.embfile_names():
                return {}
            with zipfile.ZipFile(io.BytesIO(d.embfile_get(ANHANG))) as z:
                return {n: z.read(n) for n in z.namelist() if re.fullmatch(r'\d{3}\.txt', n) or n in DATEIEN}
    except Exception:
        return {}


def images(pdf, out, pages, progress=lambda done, total, msg: None, cancelled=lambda: False):
    """Die Seitenbilder der genannten Seiten aus dem PDF in den Buchordner out holen (beim Zusammenführen, #66: nur
    für Seiten, die hier keines haben). Liefert die Zahl der geholten Bilder."""
    fitz = _fitz()
    m = info(pdf)
    if not m:
        return 0
    order = sorted(m['seiten'])
    os.makedirs(os.path.join(out, 'img'), exist_ok=True)
    n_img = 0
    with fitz.open(pdf) as d:
        for k, pg in enumerate(pages):
            if cancelled():
                raise ValueError('abgebrochen')
            if pg in m['seiten'] and m['seiten'][pg] and order.index(pg) < d.page_count:
                if ocr.pdf_page(d, order.index(pg), ocr.free_slot(out, pg))[0]:
                    n_img += 1
            progress(k + 1, len(pages), 'entpacken')
    return n_img


def load(pdf, out, progress=lambda done, total, msg: None, cancelled=lambda: False):
    """Aus einem gesicherten PDF wieder einen Buchordner machen. Liefert dict(pages, images, corrections, title, saved)."""
    fitz = _fitz()
    m = info(pdf)
    if not m:
        raise ValueError('kein_pdfbuch')
    pages = sorted(m['seiten'])
    os.makedirs(os.path.join(out, 'img'), exist_ok=True)
    with fitz.open(pdf) as d:
        with zipfile.ZipFile(io.BytesIO(d.embfile_get(ANHANG))) as z:
            for name in z.namelist():  # nur bekannte Namen, keine Pfade: der Anhang könnte von irgendwoher kommen
                if re.fullmatch(r'\d{3}\.txt', name) or name in DATEIEN:
                    with open(os.path.join(out, name), 'wb') as f:
                        f.write(z.read(name))
        n_img = 0
        for n, pg in enumerate(pages):
            if cancelled():
                raise ValueError('abgebrochen')
            if m['seiten'][pg] and n < d.page_count:
                if ocr.pdf_page(d, n, ocr.free_slot(out, pg))[0]:  # beim Aktualisieren (#66) weicht das bisherige Bild
                    n_img += 1
            progress(n + 1, len(pages), 'entpacken')
    if not pagexml.book_pages(out):
        raise ValueError('kein_pdfbuch')
    return dict(pages=len(pages), images=n_img, corrections=m.get('korrekturen') or 0, title=m.get('titel') or '',
                saved=m.get('gesichert') or '', kennung=m.get('kennung'))
