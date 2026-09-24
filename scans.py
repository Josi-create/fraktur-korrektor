"""Scans vorbereiten (#42): Doppelseiten teilen und schiefe Seiten geraderichten – vor der Texterkennung, nur mit
PyMuPDF. Abfotografierte Bücher zeigen meist zwei Seiten auf einem Bild, und die Seite liegt schief; bisher verwies das
Programm dafür auf ScanTailor, das es für den Mac nicht fertig gibt.

Gemessen wird auf einem verkleinerten Graustufenbild (rund 320 Pixel breit), gearbeitet auf dem Original:
  Doppelseite   Breite deutlich größer als Höhe, und in der Bundmitte eine helle Lücke zwischen den Textblöcken
                oder ein dunkler Schatten der Falz (Spaltenprofil der dunklen Pixel im mittleren Drittel).
  Schieflage    Projektionsprofil: Für Winkel zwischen -5° und +5° werden die dunklen Pixel zeilenweise gezählt, als
                wäre das Bild um diesen Winkel gedreht; bei geraden Zeilen ist die Streuung der Zeilensummen am größten.
  Ränder/Finger Zusammenhängende dunkle Flächen, die den Bildrand berühren und dick sind (Textzeilen sind dünn):
                Was eine ganze Seite entlangläuft (Tischplatte, Buchkante, Schatten), wird abgeschnitten, ein Fleck
                (Finger, Klammer) weiß übermalt – immer nur außerhalb des Textblocks mit Sicherheitsabstand.
Alle Funktionen sind ohne Server nutzbar; prepare() schreibt einen neuen Bilderordner, der danach wie ein
ScanTailor-Ergebnis als Quelle für die Erkennung dient."""
import os, json, math, shutil, statistics, tempfile

SRCEXT = ('.png', '.jpg', '.jpeg', '.tif', '.tiff')
ANALYSE_W = 320      # Breite des Messbilds: fein genug für Zeilen, grob genug für reines Python
MIN_ANGLE = 0.3      # darunter wird nicht gedreht: unsichtbar, und jedes Drehen kostet Schärfe
MAX_ANGLE = 5.0      # was schiefer liegt, ist kein Scanfehler, sondern falsch fotografiert
LANDSCAPE = 1.15     # Breite/Höhe, ab der ein Bild als Doppelseite in Frage kommt
FOLDER = 'aufbereitet'
# Ränder und Finger (Maße als Anteil der kürzeren Bildseite des Messbilds)
BLOB_MIN = 0.03      # so dick muss eine dunkle Randfläche mindestens sein – Textzeilen sind dünner
BLOB_MAX = 0.5       # Anteil der Bildfläche, ab dem eine »Randfläche« eher der Text selbst ist: dann lieber nichts tun
EDGE_SPAN = 0.6      # läuft eine Fläche über so viel einer Bildkante, ist es ein Rand (schneiden), sonst ein Fleck (übermalen)
TEXT_PAD = 0.025     # Sicherheitsabstand um den Textblock, in den weder Schnitt noch Übermalung hineinreichen
HALO = 0.01          # Saum um eine dunkle Fläche, der mit weggenommen wird (Schatten, unscharfe Kante)
NOT_PAPER = 60       # so viel dunkler als das Papier gilt als »nicht Papier« (Schatten, Haut, unscharfe Schrift)


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


# ---- Ränder und Finger (#42, Punkt 3)

def paper_level(data):
    """Grauwert des Papiers: der häufigste Wert oberhalb der Otsu-Schwelle."""
    thr = otsu(data[::7])
    hist = [0] * 256
    for v in data[::7]:
        if v >= thr:
            hist[v] += 1
    return max(range(thr, 256), key=hist.__getitem__) if any(hist) else 255


def components(w, h, rows):
    """Zusammenhängende dunkle Flächen (4er-Nachbarschaft) über Lauflängen und Union-Find – schnell genug in reinem
    Python. Liefert (flächen, label): je Fläche dict(id, x0, y0, x1, y1, area) mit ausschließlichen Enden, und je
    Bildzeile eine Liste mit der Flächennummer je Pixel (0 = Papier)."""
    parent = []

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    runs_by_row, prev = [], []
    for y in range(h):
        cur = []
        for a, b in _runs(list(rows[y])):
            k = len(parent)
            parent.append(k)
            cur.append((a, b, k))
            for pa, pb, pk in prev:
                if pa < b and a < pb:
                    ra, rb = find(k), find(pk)
                    if ra != rb:
                        parent[ra] = rb
        runs_by_row.append(cur)
        prev = cur
    comps, label = {}, []
    for y, cur in enumerate(runs_by_row):
        line = [0] * w
        for a, b, k in cur:
            r = find(k)
            c = comps.get(r)
            if c is None:
                c = comps[r] = dict(id=len(comps) + 1, x0=a, y0=y, x1=b, y1=y + 1, area=0)
            c['x0'], c['x1'], c['y1'] = min(c['x0'], a), max(c['x1'], b), y + 1
            c['area'] += b - a
            line[a:b] = [c['id']] * (b - a)
        label.append(line)
    return list(comps.values()), label


def edge_contact(label, w, h, cid, side):
    """Wie eine Fläche eine Bildkante berührt: (lo, hi, depth, deepest) – Bereich entlang der Kante (hi
    ausschließlich), die Tiefe von der Kante her, die 90 % der berührenden Zeilen nicht überschreiten, und die größte
    Tiefe; oder None. So zählt eine Ecke aus Tischplatte links und unten je Kante für sich: Die paar Zeilen der
    unteren Kante reichen zwar bis ganz nach rechts, bestimmen aber nicht, wie weit links geschnitten wird."""
    lo, hi, depths = None, None, []
    for i in (range(h) if side in 'lr' else range(w)):
        if side == 'l':
            px = label[i]
        elif side == 'r':
            px = label[i][::-1]
        elif side == 't':
            px = (label[y][i] for y in range(h))
        else:
            px = (label[y][i] for y in range(h - 1, -1, -1))
        d = 0
        for v in px:
            if v != cid:
                break
            d += 1
        if d:
            lo, hi = i if lo is None else lo, i + 1
            depths.append(d)
    if not depths:
        return None
    depths.sort()
    return lo, hi, depths[min(len(depths) - 1, int(len(depths) * 0.9))], depths[-1]


def paper_box(pix):
    """Papierbereich eines (geteilten, geradegerichteten) Seitenbilds: dict(crop=(x0, y0, x1, y1) in Pixeln des
    Originals, fill=[Rechtecke, die weiß werden], margins=Zahl der Ränder, text=(x0, y0, x1, y1)) – oder None,
    wenn nichts zu tun ist (weißer Hintergrund, keine Ränder).

    Gemessen wird auf dem Messbild: »nicht Papier« ist, was deutlich dunkler als der Papierton ist (NOT_PAPER),
    damit auch Schatten und Haut zählen, nicht nur Druckerschwärze. Eine dunkle Fläche, die den Bildrand berührt und
    dick ist (BLOB_MIN – Textzeilen sind dünn), ist Rand oder Fleck; alles andere ist Text, und dessen Kasten samt
    Sicherheitsabstand (TEXT_PAD) bleibt unangetastet. Ein Rand, der eine Kante fast ganz entlangläuft (EDGE_SPAN),
    wird abgeschnitten, bis zu seiner größten Tiefe samt Saum; ein Fleck (Finger) wird nur außerhalb des Textkastens
    weiß übermalt – was in den Text hineinragt, bleibt, wie es ist. Ist eine »Randfläche« größer als die halbe
    Seite (BLOB_MAX), ist sie eher der Text selbst (Schatten über dem Textblock): dann wird nichts getan."""
    sm = small(pix)
    assert sm.n == 1, 'Graustufen ohne Alpha erwartet'
    w, h, stride, data = sm.width, sm.height, sm.stride, sm.samples
    thr = max(otsu(data[::7]), paper_level(data) - NOT_PAPER)
    table = bytes(1 if v < thr else 0 for v in range(256))
    rows = [data[y * stride:y * stride + w].translate(table) for y in range(h)]
    unit = min(w, h)
    thick, pad, halo = max(4, unit * BLOB_MIN), max(2, round(unit * TEXT_PAD)), max(1, round(unit * HALO))
    comps, label = components(w, h, rows)
    blobs = []
    for c in comps:
        edge = c['x0'] == 0 or c['y0'] == 0 or c['x1'] == w or c['y1'] == h
        if edge and min(c['x1'] - c['x0'], c['y1'] - c['y0']) >= thick:
            if c['area'] > BLOB_MAX * w * h:
                return None  # zu groß, um ein Rand zu sein – lieber nichts anfassen
            blobs.append(c)
    if not blobs:
        return None
    # Textkasten: alle dunklen Pixel, die nicht zu einer Randfläche gehören
    ids = {c['id'] for c in blobs}
    keep = [[1 if v and v not in ids else 0 for v in line] for line in label]
    ys = [y for y in range(h) if sum(keep[y]) >= 2]
    if ys:
        cols = [sum(keep[y][x] for y in ys) for x in range(w)]
        xs = [x for x in range(w) if cols[x] >= 2]
        tx0, ty0, tx1, ty1 = max(0, xs[0] - pad), max(0, ys[0] - pad), min(w, xs[-1] + 1 + pad), min(h, ys[-1] + 1 + pad)
    else:  # leere Seite: alles darf weg, was dunkel ist
        tx0, ty0, tx1, ty1 = w // 2, h // 2, w // 2, h // 2
    cx0, cy0, cx1, cy1 = 0, 0, w, h  # Schnittkasten im Messbild
    fills, margins = [], 0
    for c in blobs:
        for side in 'lrtb':
            hit = edge_contact(label, w, h, c['id'], side)
            if not hit:
                continue
            lo, hi, depth, deepest = hit
            along = h if side in 'lr' else w
            if hi - lo >= EDGE_SPAN * along:  # Rand: abschneiden, aber nicht in den Textkasten hinein
                margins += 1
                if side == 'l':
                    cx0 = max(cx0, min(depth + halo, tx0))
                elif side == 'r':
                    cx1 = min(cx1, max(w - depth - halo, tx1))
                elif side == 't':
                    cy0 = max(cy0, min(depth + halo, ty0))
                else:
                    cy1 = min(cy1, max(h - depth - halo, ty1))
            # Fleck (oder der Teil eines Rands, der über die Schnittlinie hinausreicht – schräge Buchkante):
            # außerhalb des Textkastens weißen, der Streifen zwischen Kante und Textkasten, so breit wie die Berührung
            lo, hi = max(0, lo - halo), min(along, hi + halo)
            if side == 'l' and tx0 > 0:
                fills.append((0, lo, min(deepest + halo, tx0), hi))
            elif side == 'r' and tx1 < w:
                fills.append((max(w - deepest - halo, tx1), lo, w, hi))
            elif side == 't' and ty0 > 0:
                fills.append((lo, 0, hi, min(deepest + halo, ty0)))
            elif side == 'b' and ty1 < h:
                fills.append((lo, max(h - deepest - halo, ty1), hi, h))
    if cx1 - cx0 < w * 0.3 or cy1 - cy0 < h * 0.3:
        return None  # da bliebe kaum etwas übrig: eher ein Bild als eine Seite
    s = pix.width / w  # zurück auf das Original; Ränder rund um die Flächen großzügig (ganze Messpixel)
    up = lambda x0, y0, x1, y1: (int(x0 * s), int(y0 * s), min(pix.width, math.ceil(x1 * s)), min(pix.height, math.ceil(y1 * s)))
    crop_box = (math.ceil(cx0 * s), math.ceil(cy0 * s), min(pix.width, int(cx1 * s)), min(pix.height, int(cy1 * s)))
    fills = [f for f in (up(*f) for f in fills) if f[0] < crop_box[2] and f[2] > crop_box[0] and f[1] < crop_box[3] and f[3] > crop_box[1]]
    if crop_box == (0, 0, pix.width, pix.height) and not fills:
        return None
    return dict(crop=crop_box, fill=fills, margins=margins, text=up(tx0, ty0, tx1, ty1))


def trim(pix, box):
    """paper_box-Ergebnis anwenden: Flecken weiß übermalen, dann auf den Schnittkasten beschneiden."""
    import fitz
    if box is None:
        return pix
    if box['fill']:
        pix = fitz.Pixmap(pix, 0) if pix.alpha else fitz.Pixmap(pix, pix.width, pix.height)  # Kopie, das Original bleibt
        for f in box['fill']:
            pix.set_rect(fitz.IRect(*f), (255,))
    x0, y0, x1, y1 = box['crop']
    if (x0, y0, x1, y1) == (0, 0, pix.width, pix.height):
        return pix
    cut = fitz.Pixmap(pix, pix.width, pix.height, fitz.IRect(x0, y0, x1, y1))
    cut.set_origin(0, 0)
    return cut


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
        parts = split_page(pix, d['split']) if d['double'] else [pix]
        angle = statistics.median(skew_angle(x) for x in parts)
        # Ränder je Teil, für die Vorschau als Anteile des ganzen Bildes (ungedreht gemessen – fürs Bild genau genug)
        boxes, margins, x = [], 0, 0
        for part in parts:
            b = paper_box(part)
            if b:
                margins += b['margins']
                boxes.append([round(v, 4) for v in ((x + b['crop'][0]) / pix.width, b['crop'][1] / pix.height,
                                                    (x + b['crop'][2]) / pix.width, b['crop'][3] / pix.height)])
            x += part.width
        return dict(n=n, double=d['double'], split=d['split'], angle=angle, w=pix.width, h=pix.height, margins=margins, boxes=boxes)
    finally:
        os.remove(f)


def inspect(source, max_pages=6, progress=lambda done, total, msg: None):
    """Stichprobe über das Buch: Sind es Doppelseiten, liegen die Seiten schief, haben sie dunkle Ränder? Liefert
    dict(pages, double, split, skew, margins, first, samples, needed). first = erste geprüfte Doppelseite (für die
    Vorschau), skew = mittlere Neigung, margins = auf mindestens der Hälfte der Seiten läuft ein dunkler Rand entlang."""
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
    margins = sum(1 for s in samples if s['margins']) * 2 >= len(samples)
    first = doubles[0]['n'] if doubles else samples[0]['n']
    return dict(pages=total, double=double, split=split, skew=skew, margins=margins, first=first, samples=samples,
                needed=double or skew >= MIN_ANGLE or margins)


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


def prepare(source, out, split=None, deskew=True, progress=lambda done, total, msg: None, cancelled=lambda: False, trim_edges=False):
    """Alle Seiten der Quelle aufbereitet nach out schreiben (seite_001.jpg …): split = Trennposition als Anteil der
    Breite (None: nicht teilen; geteilt werden nur querliegende Bilder), deskew = geraderichten ab MIN_ANGLE,
    trim_edges = dunkle Ränder abschneiden und Finger übermalen (paper_box) – nach dem Teilen und Drehen.
    Unveränderte Seiten werden unverändert kopiert. Schreibt aufbereitung.json; liefert dict(pages, split, rotated, trimmed)."""
    total = page_count(source)
    if not total:
        raise ValueError('keine_seiten')
    if total > 999:
        raise ValueError('zu_viele_seiten')
    os.makedirs(out, exist_ok=True)
    pages, nsplit, nrot, ntrim = [], 0, 0, 0
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
                box = paper_box(part) if trim_edges else None
                if box:
                    part = trim(part, box)
                    ntrim += 1
                name = 'seite_%03d' % (len(pages) + 1)
                if side is None and not angle and not box:
                    ext = os.path.splitext(src)[1].lower()
                    ext = '.png' if ext in ('.tif', '.tiff') else ext
                    if ext == '.png':
                        pix.save(os.path.join(out, name + ext))
                    else:
                        shutil.copyfile(src, os.path.join(out, name + ext))
                else:
                    ext = '.jpg'
                    part.save(os.path.join(out, name + ext), jpg_quality=88)
                pages.append(dict(datei=name + ext, seite=n + 1, teil=side, winkel=angle, schnitt=list(box['crop']) if box else None))
            os.remove(src)
            progress(n + 1, total, 'scans')
    with open(os.path.join(out, 'aufbereitung.json'), 'w', encoding='utf-8') as f:
        json.dump(dict(quelle=os.path.abspath(source), teilen=split, geraderichten=deskew, raender=trim_edges,
                       geteilt=nsplit, gedreht=nrot, beschnitten=ntrim, seiten=pages), f, ensure_ascii=False, indent=1)
    return dict(pages=len(pages), split=nsplit, rotated=nrot, trimmed=ntrim, folder=out)


if __name__ == '__main__':  # py scans.py <pdf-oder-bilderordner> [<zielordner>]
    import sys
    r = inspect(sys.argv[1])
    print(json.dumps(r, indent=1))
    if len(sys.argv) > 2:
        print(prepare(sys.argv[1], sys.argv[2], r['split'] if r['double'] else None, trim_edges=r['margins'],
                      progress=lambda d, t, m: print('\r%s %d/%d' % (m, d, t), end='', flush=True)))
