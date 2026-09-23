"""Scans vorbereiten (#42): Doppelseiten teilen und schiefe Seiten geraderichten – vor der Texterkennung, nur mit
PyMuPDF. Abfotografierte Bücher zeigen meist zwei Seiten auf einem Bild, und die Seite liegt schief; bisher verwies das
Programm dafür auf ScanTailor, das es für den Mac nicht fertig gibt.

Gemessen wird auf einem verkleinerten Graustufenbild (rund 320 Pixel breit), gearbeitet auf dem Original:
  Doppelseite   Breite deutlich größer als Höhe, und in der Bundmitte eine helle Lücke zwischen den Textblöcken
                oder ein dunkler Schatten der Falz (Spaltenprofil der dunklen Pixel im mittleren Drittel).
  Schieflage    Projektionsprofil: Für Winkel zwischen -5° und +5° werden die dunklen Pixel zeilenweise gezählt, als
                wäre das Bild um diesen Winkel gedreht; bei geraden Zeilen ist die Streuung der Zeilensummen am größten.
Alle Funktionen sind ohne Server nutzbar; prepare() schreibt einen neuen Bilderordner, der danach wie ein
ScanTailor-Ergebnis als Quelle für die Erkennung dient."""
import os, json, math, shutil, statistics, tempfile

SRCEXT = ('.png', '.jpg', '.jpeg', '.tif', '.tiff')
ANALYSE_W = 320      # Breite des Messbilds: fein genug für Zeilen, grob genug für reines Python
MIN_ANGLE = 0.3      # darunter wird nicht gedreht: unsichtbar, und jedes Drehen kostet Schärfe
MAX_ANGLE = 5.0      # was schiefer liegt, ist kein Scanfehler, sondern falsch fotografiert
LANDSCAPE = 1.15     # Breite/Höhe, ab der ein Bild als Doppelseite in Frage kommt
FOLDER = 'aufbereitet'


def load_gray(path):
    """Bild als Graustufen-Pixmap ohne Alpha."""
    import fitz
    pix = fitz.Pixmap(path)
    if pix.alpha:
        pix = fitz.Pixmap(pix, 0)
    if pix.n != 1:
        pix = fitz.Pixmap(fitz.csGRAY, pix)
    return pix


def small(pix, width=ANALYSE_W):
    """Verkleinerte Kopie fürs Messen. (fitz.Pixmap(pix) allein wäre eine Kopie MIT Alphakanal – dann stimmt keine
    Zeilenbreite mehr; die skalierte Kopie behält n=1.)"""
    import fitz
    if pix.width <= width:
        return fitz.Pixmap(pix, pix.width, pix.height)
    return fitz.Pixmap(pix, width, max(1, round(pix.height * width / pix.width)))


def otsu(samples):
    """Schwelle zwischen Papier und Druckerschwärze aus dem Grauwert-Histogramm (Otsu)."""
    hist = [0] * 256
    for v in samples:
        hist[v] += 1
    total = len(samples)
    sum_all = sum(i * h for i, h in enumerate(hist))
    best, thr, wb, sb = -1.0, 128, 0, 0
    for i in range(256):
        wb += hist[i]
        if not wb:
            continue
        wf = total - wb
        if not wf:
            break
        sb += i * hist[i]
        mb, mf = sb / wb, (sum_all - sb) / wf
        v = wb * wf * (mb - mf) ** 2
        if v > best:
            best, thr = v, i
    return thr


def dark_rows(pix):
    """Zeilen des Messbilds als Bytes 0/1 (1 = dunkel). Liefert (breite, höhe, zeilen)."""
    assert pix.n == 1, 'Graustufen ohne Alpha erwartet'
    w, h, stride = pix.width, pix.height, pix.stride
    data = pix.samples
    thr = otsu(data[::7])  # Stichprobe genügt fürs Histogramm
    table = bytes(1 if v < thr else 0 for v in range(256))
    rows = [data[y * stride:y * stride + w].translate(table) for y in range(h)]
    return w, h, rows


def column_profile(w, h, rows, y0=0.1, y1=0.9):
    """Anteil dunkler Pixel je Spalte, gezählt zwischen y0 und y1 (Rand oben und unten stört nur), leicht geglättet."""
    a, b = int(h * y0), max(int(h * y1), int(h * y0) + 1)
    col = [0] * w
    for row in rows[a:b]:
        for x in range(w):
            col[x] += row[x]
    n = b - a
    prof = [c / n for c in col]
    return [sum(prof[max(0, x - 1):x + 2]) / len(prof[max(0, x - 1):x + 2]) for x in range(w)]


def _runs(flags):
    """Zusammenhängende Abschnitte mit flag=True als (start, ende) – ende ausschließlich."""
    out, start = [], None
    for x, f in enumerate(flags + [False]):
        if f and start is None:
            start = x
        elif not f and start is not None:
            out.append((start, x))
            start = None
    return out


def find_gutter(profile, near=None, tol=0.05):
    """Bundmitte im Spaltenprofil als Anteil der Breite (0–1), oder None. Gesucht im mittleren Drittel: erst ein
    dunkler Streifen (Schatten der Falz), sonst die breiteste helle Lücke – Text muss links und rechts davon stehen.
    Mit near zählt statt der breitesten die Lücke, die dieser Stelle am nächsten liegt (Feinjustierung je Seite:
    bei Fotos wandert die Falz von Bild zu Bild ein wenig), und nur, wenn sie nicht weiter als tol entfernt ist."""
    w = len(profile)
    lo, hi = w // 3, 2 * w // 3
    if near is not None:
        lo, hi = min(lo, int(w * (near - tol))), max(hi, int(w * (near + tol)))
    lo, hi = max(1, lo), min(w - 1, hi)
    if hi <= lo:
        return None
    ink = sorted(profile)[int(w * 0.75)]  # typischer Wert in Textspalten
    if ink <= 0:
        return None
    left, right = profile[:w // 4], profile[3 * w // 4:]
    if sum(left) / len(left) < 0.25 * ink or sum(right) / len(right) < 0.25 * ink:
        return None  # nur auf einer Seite Text: keine Doppelseite
    dark = [(lo <= x < hi and profile[x] > 0.8) for x in range(w)]
    runs = [r for r in _runs(dark) if r[1] - r[0] >= max(2, w * 0.006)]
    if not runs:
        light = [(lo <= x < hi and profile[x] < 0.12 * ink) for x in range(w)]
        runs = [r for r in _runs(light) if r[1] - r[0] >= max(3, w * 0.01)]
    if not runs:
        return None
    if near is None:
        a, b = max(runs, key=lambda r: r[1] - r[0])
        return (a + b) / 2 / w
    dist = lambda r: 0 if r[0] <= near * w < r[1] else min(abs(r[0] - near * w), abs(r[1] - near * w))
    a, b = min(runs, key=dist)
    return (a + b) / 2 / w if dist((a, b)) <= tol * w else None


def detect_double(pix):
    """dict(double, split, aspect) für ein Seitenbild (Original oder Messbild)."""
    aspect = pix.width / pix.height
    if aspect < LANDSCAPE:
        return dict(double=False, split=None, aspect=aspect)
    w, h, rows = dark_rows(small(pix))
    pos = find_gutter(column_profile(w, h, rows))
    return dict(double=pos is not None, split=pos, aspect=aspect)


def skew_angle(pix, max_angle=MAX_ANGLE):
    """Winkel in Grad, um den rotate() das Bild drehen muss, damit die Zeilen gerade liegen (0.0: liegt gerade).
    Gemessen im mittleren Bereich des Bildes, damit Buchkanten und dunkle Ränder nicht mitzählen."""
    w, h, rows = dark_rows(small(pix))
    x0, x1, y0, y1 = int(w * 0.2), int(w * 0.8), int(h * 0.15), int(h * 0.85)
    cx = (x0 + x1) / 2
    pts = [(x - cx, y) for y in range(y0, y1) for x, b in enumerate(rows[y][x0:x1], x0) if b]
    if len(pts) < 50:
        return 0.0
    if len(pts) > 40000:  # Abbildungen, Flächen: eine Stichprobe misst genauso gut
        pts = pts[::len(pts) // 40000 + 1]

    def score(a):
        t = math.tan(math.radians(a))
        bins = [0] * (h + 2 * w)
        for x, y in pts:
            bins[int(y - x * t) + w] += 1
        return sum(b * b for b in bins)

    best = max((score(a), -abs(a), a) for a in [k / 2 for k in range(-int(max_angle * 2), int(max_angle * 2) + 1)])
    a0 = best[2]
    fine = max((score(a), -abs(a), a) for a in [a0 + k / 10 for k in range(-5, 6)])
    return round(-fine[2], 1) or 0.0  # gemessen ist die Neigung der Zeilen; gedreht wird dagegen


def rotate(pix, angle):
    """Um angle Grad drehen (um die Mitte, Größe bleibt, freie Ecken weiß) – PyMuPDF dreht beim Rendern einer Seite."""
    import fitz
    if abs(angle) < 1e-6:
        return pix
    w, h = pix.width, pix.height
    doc = fitz.open()
    page = doc.new_page(width=w, height=h)
    page.insert_image(page.rect, pixmap=pix)
    m = fitz.Matrix(1, 0, 0, 1, -w / 2, -h / 2) * fitz.Matrix(angle) * fitz.Matrix(1, 0, 0, 1, w / 2, h / 2)
    out = page.get_pixmap(matrix=m, clip=page.rect, colorspace=fitz.csGRAY)
    doc.close()
    x0, y0 = -out.irect[0], -out.irect[1]  # das Gerenderte ist etwas größer als die Seite: mittig zurechtschneiden
    cut = fitz.Pixmap(out, out.width, out.height, fitz.IRect(x0, y0, x0 + w, y0 + h))
    cut.set_origin(0, 0)
    return cut


def crop(pix, x0, x1):
    """Spalten x0..x1 (Pixel) als eigenes Bild."""
    import fitz
    cut = fitz.Pixmap(pix, pix.width, pix.height, fitz.IRect(int(x0), 0, int(x1), pix.height))
    cut.set_origin(0, 0)
    return cut


def split_page(pix, frac, refine=True):
    """Doppelseite an frac (Anteil der Breite) in (links, rechts) teilen; refine sucht die Falz je Seite nahe der
    Vorgabe und nimmt sie, wenn sie sich findet."""
    pos = None
    if refine:
        w, h, rows = dark_rows(small(pix))
        pos = find_gutter(column_profile(w, h, rows), near=frac)
    x = round(pix.width * (pos if pos is not None else frac))
    return crop(pix, 0, x), crop(pix, x, pix.width)


# ---- Quellen: Bilderordner oder PDF

def image_files(folder):
    return sorted(f for f in os.listdir(folder) if f.lower().endswith(SRCEXT))


def page_count(source):
    if os.path.isdir(source):
        return len(image_files(source))
    import fitz
    with fitz.open(source) as d:
        return d.page_count


def page_image(source, n, stem):
    """Seite n (ab 0) der Quelle als Datei stem.<ext>; liefert den Pfad. Aus einem PDF wird ein eingebettetes Foto
    unverändert entnommen (ocr.pdf_page), sonst gerendert."""
    if os.path.isdir(source):
        f = os.path.join(source, image_files(source)[n])
        ext = os.path.splitext(f)[1].lower()
        ext = '.jpg' if ext == '.jpeg' else ext
        shutil.copyfile(f, stem + ext)
        return stem + ext
    import fitz, ocr
    with fitz.open(source) as d:
        return ocr.pdf_page(d, n, stem)[0]


def measure(source, n, tmp):
    """Eine Seite ansehen: dict(n, double, split, angle, w, h)."""
    f = page_image(source, n, os.path.join(tmp, 'p%03d' % n))
    try:
        pix = load_gray(f)
        d = detect_double(pix)
        if d['double']:
            halves = split_page(pix, d['split'])
            angle = statistics.median(skew_angle(x) for x in halves)
        else:
            angle = skew_angle(pix)
        return dict(n=n, double=d['double'], split=d['split'], angle=angle, w=pix.width, h=pix.height)
    finally:
        os.remove(f)


def inspect(source, max_pages=6, progress=lambda done, total, msg: None):
    """Stichprobe über das Buch: Sind es Doppelseiten, liegen die Seiten schief? Liefert dict(pages, double, split,
    skew, first, samples, needed). first = erste geprüfte Doppelseite (für die Vorschau), skew = mittlere Neigung."""
    total = page_count(source)
    if not total:
        raise ValueError('keine_seiten')
    # Umschlag und Vorsatz auslassen: die erste und letzte Seite sehen anders aus als das Buch
    ns = sorted({int(round((k + 1) * total / (max_pages + 1))) for k in range(max_pages)} & set(range(total))) or [0]
    samples = []
    with tempfile.TemporaryDirectory(prefix='fk-scans-') as tmp:
        for k, n in enumerate(ns):
            samples.append(measure(source, n, tmp))
            progress(k + 1, len(ns), 'pruefen')
    doubles = [s for s in samples if s['double']]
    double = len(doubles) * 2 >= len(samples)
    split = statistics.median(s['split'] for s in doubles) if doubles else None
    skew = statistics.median(abs(s['angle']) for s in samples)
    first = doubles[0]['n'] if doubles else samples[0]['n']
    return dict(pages=total, double=double, split=split, skew=skew, first=first, samples=samples,
                needed=double or skew >= MIN_ANGLE)


def preview(source, n, width=900):
    """Seite n als JPEG (Bytes), höchstens width Pixel breit – für die Vorschau mit der Trennlinie."""
    import fitz
    with tempfile.TemporaryDirectory(prefix='fk-scans-') as tmp:
        pix = fitz.Pixmap(page_image(source, n, os.path.join(tmp, 'v')))
    if pix.alpha:
        pix = fitz.Pixmap(pix, 0)
    if pix.width > width:
        pix = fitz.Pixmap(pix, width, round(pix.height * width / pix.width))
    return pix.tobytes('jpeg', jpg_quality=80)


def prepare(source, out, split=None, deskew=True, progress=lambda done, total, msg: None, cancelled=lambda: False):
    """Alle Seiten der Quelle aufbereitet nach out schreiben (seite_001.jpg …): split = Trennposition als Anteil der
    Breite (None: nicht teilen; geteilt werden nur querliegende Bilder), deskew = geraderichten ab MIN_ANGLE.
    Unveränderte Seiten werden unverändert kopiert. Schreibt aufbereitung.json; liefert dict(pages, split, rotated)."""
    total = page_count(source)
    if not total:
        raise ValueError('keine_seiten')
    if total > 999:
        raise ValueError('zu_viele_seiten')
    os.makedirs(out, exist_ok=True)
    pages, nsplit, nrot = [], 0, 0
    with tempfile.TemporaryDirectory(prefix='fk-scans-') as tmp:
        for n in range(total):
            if cancelled():
                raise ValueError('abgebrochen')
            src = page_image(source, n, os.path.join(tmp, 'p'))
            pix = load_gray(src)
            parts = [(pix, None)]
            if split is not None and pix.width / pix.height >= LANDSCAPE:
                links, rechts = split_page(pix, split)
                parts = [(links, 'links'), (rechts, 'rechts')]
                nsplit += 1
            for part, side in parts:
                angle = skew_angle(part) if deskew else 0.0
                if abs(angle) >= MIN_ANGLE:
                    part = rotate(part, angle)
                    nrot += 1
                else:
                    angle = 0.0
                name = 'seite_%03d' % (len(pages) + 1)
                if side is None and not angle:
                    ext = os.path.splitext(src)[1].lower()
                    ext = '.png' if ext in ('.tif', '.tiff') else ext
                    if ext == '.png':
                        pix.save(os.path.join(out, name + ext))
                    else:
                        shutil.copyfile(src, os.path.join(out, name + ext))
                else:
                    ext = '.jpg'
                    part.save(os.path.join(out, name + ext), jpg_quality=88)
                pages.append(dict(datei=name + ext, seite=n + 1, teil=side, winkel=angle))
            os.remove(src)
            progress(n + 1, total, 'scans')
    with open(os.path.join(out, 'aufbereitung.json'), 'w', encoding='utf-8') as f:
        json.dump(dict(quelle=os.path.abspath(source), teilen=split, geraderichten=deskew, geteilt=nsplit, gedreht=nrot, seiten=pages),
                  f, ensure_ascii=False, indent=1)
    return dict(pages=len(pages), split=nsplit, rotated=nrot, folder=out)


if __name__ == '__main__':  # py scans.py <pdf-oder-bilderordner> [<zielordner>]
    import sys
    r = inspect(sys.argv[1])
    print(json.dumps(r, indent=1))
    if len(sys.argv) > 2:
        print(prepare(sys.argv[1], sys.argv[2], r['split'] if r['double'] else None,
                      progress=lambda d, t, m: print('\r%s %d/%d' % (m, d, t), end='', flush=True)))
