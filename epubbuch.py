"""Ein Buch als E-Book sichern (#59): EPUB 3, lesbar in jeder Lese-App.

Das Inhaltsverzeichnis entsteht aus den mit H ausgezeichneten Überschriften – dieselbe Liste wie die Übersicht (I) und die
Lesezeichen des PDFs (korrlib.headings), damit die drei nie auseinanderlaufen. An jedem Seitenwechsel steht die gedruckte
Seitenzahl (sichtbar klein im Text und als Seitenliste der Lese-App): So lässt sich auch aus dem E-Book nach der
Druckausgabe zitieren. Fußnoten werden EPUB-Fußnoten, der Verweis im Text ein Link; eine Fußnote, deren Verweis das
Programm nicht findet, steht sichtbar unter dem Absatz – verloren geht nichts. Absätze kommen aus dem <p> am Zeilenanfang
(#67). Nicht in den Text gehören Kopfzeile, Kolumnentitel und die Seitenzahl unten samt dem Rauschen darunter.

Aufbau nach EPUB 3.3: mimetype unkomprimiert vorn, Paketdokument, Navigationsdokument (außerhalb der Lesereihenfolge), vorn
eine Titelseite und eine sichtbare Seite »Inhalt«, jede Überschrift der obersten Stufe beginnt eine neue Datei. toc.ncx
nur für ältere Lesegeräte. Die Kennung des Buchs steht als dc:identifier darin – daran erkennt das Programm sein EPUB wieder
(ersetzen statt »(2)«, das gesicherte PDF daneben empfehlen)."""
import os, re, html, time, zipfile
import xml.etree.ElementTree as ET
import korrlib

MIME = 'application/epub+zip'
OPF = 'OEBPS/content.opf'
GROSS = 150000   # Zeichen je Textdatei: Ein Buch ohne Überschriften wird so geteilt – sehr große Dateien machen Lese-Apps träge
UMSCHLAG = 1600  # Höhe des Umschlagbilds in Pixeln
INLINE = {'em', 'strong', 'i', 'b', 'sup', 'sub', 'br'}
# Ein Fußnotenzeichen im Text: hochgestellt (<sup>36</sup>, <sup>*</sup>), »wurde 1)« wie in älteren Büchern, ein Stern am Wort
# (»Wort*«, »Wort*)«) oder Ziffern, die am Wort kleben (»beziffert.36« – noch nicht hochgestellt)
REF = re.compile(r'<sup>\s*(\d{1,3}|\*+)(\)?)\s*</sup>'
                 r'|(?<=[^\s\d(])( ?)(\d{1,3})\)'
                 r'|(?<=[A-Za-zÄÖÜäöüßſ.,;:!?“”"»«\'’)\]])(\*+)(\)?)(?![\d*])'
                 r'|(?<=[A-Za-zÄÖÜäöüßſ.,;:!?“”"»«\'’\]])(\d{1,3})(?=[\s,.;:!?)“”"»«]|$)')
# Anfang einer Fußnote unten: »1) …«, »1 …«, »* …«, »*) …«, »<sup>1</sup> …« – eine bloße Zahl nur mit Leerzeichen dahinter
NOTE = re.compile(r'\s*(?:<sup>\s*)?(?:(\d{1,3})|(\*+))(\)?)(\s*</sup>)?')
ENDE = re.compile(r'[.!?:“”"»«)]$')  # ein Absatz endet mit einem Satzzeichen
MARK = '%d'               # Platzhalter für fertiges XHTML (Seitenmarke, Fußnotenlink) im Text eines Absatzes
PLATZ = re.compile('(\\d+)')
W = dict(inhalt='Inhalt', seiten='Seiten', orientierung='Orientierung', titelseite='Titelseite', text='Text',
         seitenzahlen='Die kleinen Zahlen in eckigen Klammern sind die Seitenzahlen der gedruckten Ausgabe.',
         erstellt='Text korrigiert mit dem Fraktur-Korrektor.')
CSS = '''body { margin: 0 4%; line-height: 1.45; }
p { margin: 0; text-indent: 1.2em; text-align: justify; hyphens: auto; -webkit-hyphens: auto; }
p.erst { text-indent: 0; }
p.vers { text-indent: 0; text-align: left; hyphens: none; -webkit-hyphens: none; margin: 0.4em 0; }
h1, h2, h3, h4, h5, h6 { text-align: center; line-height: 1.25; margin: 1.5em 0 0.8em; font-weight: bold; hyphens: none; }
h1 { font-size: 1.5em; } h2 { font-size: 1.3em; } h3 { font-size: 1.12em; } h4, h5, h6 { font-size: 1em; }
span.seite { font-size: 0.7em; color: #888; font-weight: normal; font-style: normal; }
div.seite { text-align: right; text-indent: 0; margin: 0; }
sup { font-size: 0.7em; line-height: 0; vertical-align: super; }
a.nr { text-decoration: none; }
.fn { font-size: 0.85em; margin: 0.3em 0 0.3em 1.2em; }
.fn p { text-indent: 0; text-align: left; }
table { border-collapse: collapse; margin: 0.8em auto; }
td, th { padding: 0.1em 0.5em; vertical-align: top; text-align: left; }
.titel { text-align: center; margin-top: 20%; }
.titel h1 { font-size: 1.8em; margin-bottom: 1em; }
.titel p { text-indent: 0; text-align: center; margin: 0.4em 0; }
.titel .hinweis { font-size: 0.8em; color: #666; margin-top: 4em; }
.inhalt ol { list-style: none; margin: 0; padding-left: 1.2em; }
.inhalt > ol { padding-left: 0; }
.inhalt li { margin: 0.3em 0; }
.inhalt .s { color: #888; font-size: 0.85em; }
'''


def esc(s):
    return html.escape(s, quote=True)


def xhtml(s, keep=INLINE):
    """Text mit Auszeichnung als wohlgeformtes XHTML: Elemente aus keep bleiben – ausgeglichen, denn ein <em> ohne Ende (in
    einem Editor bearbeitet) machte in manchen Lese-Apps das ganze Kapitel unlesbar –, anderes fällt weg; < und & werden
    Entitäten. Die Platzhalter für Seitenmarken und Fußnotenlinks bleiben stehen."""
    out, stack, pos = [], [], 0
    for m in korrlib.TAG.finditer(s):
        out.append(html.escape(s[pos:m.start()], quote=False))
        pos = m.end()
        name = re.match(r'</?\s*(\w+)', m.group()).group(1).lower()
        if name not in keep:
            continue
        if name == 'br':
            out.append('<br/>')
        elif m.group().endswith('/>'):
            continue
        elif not m.group().startswith('</'):
            stack.append(name)
            out.append('<%s>' % name)
        elif name in stack:
            while stack:
                n = stack.pop()
                out.append('</%s>' % n)
                if n == name:
                    break
    out.append(html.escape(s[pos:], quote=False))
    out += ['</%s>' % n for n in reversed(stack)]
    return ''.join(out)


def plain(s):
    return korrlib.TAG.sub('', s).strip()


def join(a, b, br=False):
    """Zwei Zeilen desselben Absatzes: ¬ am Ende zieht das Wort zusammen. Ein Bindestrich bleibt; vor einem großen
    Anfangsbuchstaben gehört er zum Wort (»Staats-|Archiv«), sonst folgt ein Leerzeichen (»Umwelt-|und«). br: Die
    gedruckte Zeile bleibt eine Zeile (Verse, Listen – lined)."""
    if not a:
        return b
    if a.endswith('¬'):
        return a[:-1] + b
    if br:
        return a + '<br/>' + b
    if a[-1] in '-=' and plain(b)[:1].isupper():
        return a + b
    return a + ' ' + b


class _Flow:
    """Aus den Seiten wird fortlaufender Text: Blöcke (Absatz, Überschrift, Tabelle, Fußnoten, Seitenmarke) in
    Lesereihenfolge. Seitenmarken stehen, wo die Seite beginnt – mitten im Absatz, bei einem getrennten Wort erst hinter
    dessen zweiter Hälfte. Die Fußnoten einer Seite folgen dem Absatz, in dem die Seite endet."""

    def __init__(self, pages, labels, foot, kopf):
        self.pages, self.labels, self.foot, self.kopf = pages, labels, foot, kopf
        self.blocks, self.snips = [], []
        self.para = None      # Text des offenen Absatzes (mit Platzhaltern)
        self.marks = []       # Seitenmarken, die vor den nächsten Text gehören
        self.due = []         # Fußnoten, deren Seite schon durch ist
        self.first = True     # der nächste Absatz folgt einer Überschrift oder Tabelle: ohne Einzug
        self.fallback = not any(pages[pg][k].startswith('<p>') for pg in pages for k in self.main(pg))
        lens = sorted(len(plain(pages[pg][k])) for pg in pages for k in self.main(pg) if plain(pages[pg][k]))
        self.full = lens[int(len(lens) * 0.95)] if lens else 0
        self.lined = {pg for pg in pages if self.is_lined(pg)}
        self.verse = False    # der offene Absatz hat Zeilen, die Zeilen bleiben
        self.notes = self.footnotes()
        self.names = {(pg, i): (lv, tx) for pg, i, lv, tx in korrlib.headings(pages)}
        self.stats = dict(paragraphs=0, headings=0)

    # ---- Bereiche einer Seite
    def main(self, pg):
        """Zeilennummern des Haupttexts: ohne Kopfzeile, Kolumnentitel, Fußnoten und ohne die Seitenzahl unten samt dem
        Rauschen vom Seitenrand darunter."""
        lines = self.pages[pg]
        end = lines.index('---') if '---' in lines else len(lines)
        if pg in self.foot:
            end = min(end, self.foot[pg])
        start = 1 if lines and lines[0].startswith('#') else 0
        kopf = self.kopf.get(pg) or ()
        return [k for k in range(start, end) if k not in kopf]

    def is_lined(self, pg):
        """Eine Seite, deren gedruckte Zeilen Zeilen bleiben müssen: Verse, Dialoge, Namenslisten, Register. Fast jede Zeile
        beginnt groß, und kaum eine reicht bis zum Rand – im Fließtext endet eine Zeile mitten im Satz und reicht bis zum
        Rand (in vier Büchern mit 1400 Seiten Prosa traf es nur solche Seiten, im Faust jede Versseite)."""
        raw = [self.pages[pg][k] for k in self.main(pg)]
        ls = [plain(l) for l in raw if plain(l) and not korrlib.HLINE.match(l.strip()) and not korrlib.TABLETAG.search(l)]
        if len(ls) < 6 or not self.full:
            return False
        up = sum(1 for l in ls if re.match(r'[\W\d_]*[A-ZÄÖÜ]', l)) / len(ls)
        full = sum(1 for l in ls if len(l) >= 0.85 * self.full) / len(ls)
        return up >= 0.85 and full <= 0.3

    def note_lines(self, pg):
        lines = self.pages[pg]
        if '---' not in lines:
            return []
        a = lines.index('---') + 1
        end = self.foot[pg] if pg in self.foot and self.foot[pg] >= a else len(lines)
        return [k for k in range(a, end)]

    def footnotes(self):
        """{seite: [fußnote]} – vorab für das ganze Buch, weil eine Fußnote auf der nächsten Seite weiterlaufen kann (die
        Zeilen oben im Fußnotenblock ohne eigene Nummer). Eine Nummer beginnt nur dann eine neue Fußnote, wenn sie zur
        Zählung passt; sonst ist sie der Anfang einer Folgezeile (»12 Pferde …«)."""
        out, last, prev, steady = {}, None, None, False  # steady: fortlaufend gezählt (eine Seite beginnt mit 4 oder mehr)
        for pg in self.pages:
            idx = self.note_lines(pg)
            if not idx:
                last = None
                continue
            cur, num = [], None
            for k in idx:
                l = korrlib.sup_markup(self.pages[pg][k].strip())
                if not l:
                    continue
                m = NOTE.match(l)
                if m and m.group(1) and not (m.group(3) or m.group(4)) and not re.match(r'\s|$', l[m.end():]):
                    m = None  # »12Pferde«, »1816 zogen«
                new = False
                if m and m.group(2):
                    new = True
                elif m:
                    n = int(m.group(1))
                    if num is not None:
                        new = num < n <= num + 3
                    elif steady:  # fortlaufend gezählt: an die Seite davor anschließen, 1 bei neuer Zählung je Kapitel
                        new = n == 1 or (prev is not None and prev < n <= prev + 10)
                    else:
                        new = n <= 3 or (prev is not None and prev < n <= prev + 10)
                if new:
                    n = int(m.group(1)) if m.group(1) else None
                    if n is not None and num is None and n > 3:
                        steady = True
                    cur.append(dict(id='fn-%s-%d' % (pg, len(cur) + 1), page=pg, num=n, star=m.group(2), paren=bool(m.group(3)),
                                    mark=(m.group(1) or m.group(2)) + m.group(3), text=l[m.end():].strip(), ref=None))
                    if n is not None:
                        num = n
                elif cur:
                    cur[-1]['text'] = join(cur[-1]['text'], l)
                elif last:  # läuft von der Seite davor weiter
                    last['text'] = join(last['text'], l)
                else:
                    cur.append(dict(id='fn-%s-%d' % (pg, len(cur) + 1), page=pg, num=None, star=None, paren=False, mark='', text=l, ref=None))
            out[pg] = cur
            last = cur[-1] if cur else last
            prev = num if num is not None else prev
        return out

    # ---- Bausteine
    def snip(self, h):
        self.snips.append(h)
        return MARK % (len(self.snips) - 1)

    def link(self, pg, line):
        """Fußnotenzeichen der Zeile, zu denen es auf der Seite eine Fußnote gibt, werden Links (als Platzhalter)."""
        notes = self.notes.get(pg)
        if not notes:
            return line
        line = korrlib.sup_markup(line)

        def free(num=None, star=None):
            return next((x for x in notes if not x['ref'] and ((num is not None and x['num'] == num) or (star and x['star'] == star))), None)

        def sub(m):
            before = line[:m.start()]
            if m.group(1):
                x = free(num=int(m.group(1))) if m.group(1).isdigit() else free(star=m.group(1))
                shown = m.group(1) + m.group(2)
            elif m.group(4):
                b = re.sub(r'\d{1,3}\)', '', before)  # schon gezählte Fußnotenzeichen schließen keine Klammer
                if not before.strip() or b.count('(') > b.count(')'):
                    return m.group()  # Aufzählung am Zeilenanfang, »(vgl. S. 12)«
                x = next((x for x in notes if not x['ref'] and x['num'] == int(m.group(4)) and x['paren']), None)
                shown = m.group(4) + ')'
            elif m.group(5):
                # Ein Stern, aber unten nummerierte Fußnoten: Die Erkennung liest »1)« gern als »*)« – dann die nächste
                # Fußnote nach der zuletzt verknüpften (so zählt auch der Vorschlag für Fußnotenzeichen weiter)
                x = free(star=m.group(5))
                if not x and not any(n['star'] for n in notes):
                    done = [k for k, n in enumerate(notes) if n['ref']]
                    x = next((n for n in notes[done[-1] + 1 if done else 0:] if not n['ref'] and n['num'] is not None), None)
                shown = m.group(5) + m.group(6)
            else:
                if (before[-1:] in '.,;:' and before[-2:-1].isdigit()) or korrlib.REFABBR.search(before):
                    return m.group()  # »10.000«, »S.12«
                x, shown = free(num=int(m.group(7))), m.group(7)
            if not x:
                return m.group()
            x['ref'] = 'ref-' + x['id'][3:]
            return self.snip('<sup><a class="nr" epub:type="noteref" role="doc-noteref" id="%s" href="#%s">%s</a></sup>'
                                    % (x['ref'], x['id'], esc(shown)))
        return REF.sub(sub, line)

    def mark(self, pg):
        label = self.labels.get(pg)
        return self.snip('<span class="seite" epub:type="pagebreak" role="doc-pagebreak" id="seite-%s" aria-label="%s">[%s]</span>'
                         % (pg, esc(label), esc(label))) if label else None

    def emit(self, kind, h, **kw):
        self.blocks.append(dict(kind=kind, html=h, **kw))

    def close(self):
        """Den offenen Absatz abschließen; danach die Fußnoten der Seiten, die in ihm enden."""
        if self.para is not None:
            text = self.para[:-1] if self.para.endswith('¬') else self.para
            if plain(PLATZ.sub('', text)) or PLATZ.search(text):
                cls = 'vers' if self.verse else 'erst' if self.first else ''
                self.emit('p', '<p%s>%s</p>' % (' class="%s"' % cls if cls else '', self.fill(xhtml(text))))
                self.stats['paragraphs'] += 1
                self.first = False
            self.para, self.verse = None, False
        for x in self.due:
            body = self.fill(xhtml(x['text']))
            if x['ref']:
                self.emit('fn', '<aside class="fn" epub:type="footnote" role="doc-footnote" id="%s"><p><a class="nr" href="#%s">%s</a> %s</p></aside>'
                          % (x['id'], x['ref'], esc(x['mark'] or '↑'), body))
            else:
                self.emit('fn', '<div class="fn" id="%s"><p>%s%s</p></div>' % (x['id'], esc(x['mark']) + ' ' if x['mark'] else '', body))
        self.due = []

    def block(self):
        """Vor einem neuen Block: Absatz schließen, dann die Seitenmarken, die noch keinen Text vor sich hatten."""
        self.close()
        for m in self.marks:
            self.emit('mark', '<div class="seite">%s</div>' % self.fill(m))
        self.marks = []

    def fill(self, h):
        return PLATZ.sub(lambda m: self.snips[int(m.group(1))], h)

    def add(self, raw, br=False):
        """Eine Zeile an den offenen Absatz hängen (oder einen beginnen); br: als eigene Zeile (lined)."""
        if self.para is None:
            self.block()
            self.para = ''
        self.verse = self.verse or br
        if self.marks:
            ms = ''.join(self.marks)
            self.marks = []
            if self.para.endswith('¬'):  # getrenntes Wort über die Seitengrenze: die Marke hinter seine zweite Hälfte
                w = re.match(r'\S*', raw).end()
                raw = raw[:w] + ms + raw[w:]
            else:
                raw = ms + ' ' + raw
        self.para = join(self.para, raw, br)

    # ---- der Durchlauf
    def run(self, progress=lambda done, total, msg: None, cancelled=lambda: False):
        keys = list(self.pages)
        for n, pg in enumerate(keys):
            if cancelled():
                raise ValueError('abgebrochen')
            lines, main = self.pages[pg], self.main(pg)
            m0 = self.mark(pg)
            if m0:
                self.marks.append(m0)
            i = 0
            while i < len(main):
                k = main[i]
                l = lines[k].rstrip()
                s = l.strip()
                if not s:
                    if self.fallback:  # Textbuch aus einem EPUB: Leerzeilen trennen die Absätze
                        self.close()
                    i += 1
                    continue
                if '<table>' in s:
                    j = i
                    while j + 1 < len(main) and '</table>' not in lines[main[j]]:
                        j += 1
                    self.block()
                    t = table([self.link(pg, lines[main[x]]) for x in range(i, j + 1)])
                    if t:
                        self.emit('table', self.fill(t))
                        self.first = True
                    i = j + 1
                    continue
                h = korrlib.HLINE.match(s)
                if h and plain(h.group(2)):
                    level, parts = int(h.group(1)), [self.link(pg, h.group(2))]
                    # Zeilen derselben Ebene unmittelbar untereinander sind eine Überschrift (wie korrlib.headings)
                    while i + 1 < len(main) and main[i + 1] == main[i] + 1:
                        h2 = korrlib.HLINE.match(lines[main[i + 1]].strip())
                        if not (h2 and int(h2.group(1)) == level and plain(h2.group(2))):
                            break
                        parts.append(self.link(pg, h2.group(2)))
                        i += 1
                    self.block()
                    inner = ''
                    for p in parts:
                        inner = inner[:-1] + p if inner.endswith('¬') else inner + ('<br/>' if inner else '') + p
                    name = self.names.get((pg, k), (level, plain(PLATZ.sub('', inner.replace('<br/>', ' ')))))[1]
                    self.emit('h', '<h%d id="h-%s-%d">%s</h%d>' % (level, pg, k, self.fill(xhtml(inner)), level),
                              level=level, id='h-%s-%d' % (pg, k), text=name, page=pg)
                    self.stats['headings'] += 1
                    self.first = True
                    i += 1
                    continue
                raw = self.link(pg, l)
                if raw.startswith('<p>'):
                    self.close()
                    raw = raw[3:]
                self.add(raw, pg in self.lined)
                if self.fallback and pg not in self.lined and ENDE.search(plain(l)) and len(plain(l)) < 0.8 * self.full:
                    self.close()  # ohne Absatzmarken: eine kurze Zeile mit Satzzeichen am Ende schließt den Absatz
                i += 1
            self.due += self.notes.get(pg, [])
            if self.para is None:
                self.block()
            progress(n + 1, len(keys), 'epub')
        self.block()
        return self.blocks


def table(lines):
    """Die Zeilen einer ausgezeichneten Tabelle als wohlgeformte XHTML-Tabelle – neu aufgebaut aus Reihen und Zellen,
    damit auch eine von Hand verdorbene Auszeichnung (ein <td> ohne <tr>) eine gültige Tabelle ergibt."""
    text = re.sub(r'¬\n', '', '\n'.join(lines)).replace('\n', ' ')
    text = re.sub(r'</?(?:p|h[1-6]|blockquote)>', '', text)
    rows, row, cell, pos = [], None, None, 0

    def put(chunk):
        nonlocal row, cell
        if not chunk.strip():
            return
        if cell is None:
            if row is None:
                row = []
                rows.append(row)
            cell = ['td', []]
            row.append(cell)
        cell[1].append(chunk)
    for m in re.finditer(r'<(/?)(table|tr|td|th)\s*>', text):
        put(text[pos:m.start()])
        pos = m.end()
        closing, name = m.group(1), m.group(2)
        if name == 'tr':
            row = None if closing else []
            if not closing:
                rows.append(row)
            cell = None
        elif name in ('td', 'th'):
            if closing:
                cell = None
            else:
                if row is None:
                    row = []
                    rows.append(row)
                cell = [name, []]
                row.append(cell)
        else:
            row = cell = None
    put(text[pos:])
    rows = [r for r in rows if r]
    if not rows:
        return ''
    return '<table>%s</table>' % ''.join('<tr>%s</tr>' % ''.join('<%s>%s</%s>' % (c[0], xhtml(''.join(c[1]).strip()), c[0]) for c in r) for r in rows)


def _doc(title, body):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE html>\n'
            '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="de" lang="de">\n'
            '<head>\n<meta charset="UTF-8"/>\n<title>%s</title>\n<link rel="stylesheet" type="text/css" href="stil.css"/>\n</head>\n'
            '<body>\n%s\n</body>\n</html>\n') % (esc(title), body)


def _tree(entries):
    """[(tiefe, eintrag)] → verschachtelte Liste [(eintrag, [kinder])] – die Tiefe steigt höchstens um eins (depths())."""
    root = []
    stack = [(0, root)]
    for d, e in entries:
        while stack[-1][0] >= d:
            stack.pop()
        node = (e, [])
        stack[-1][1].append(node)
        stack.append((d, node[1]))
    return root


def depths(levels):
    """Tiefe im Inhaltsverzeichnis aus der Abfolge der Ebenen, wie bei den Lesezeichen des PDFs: Keine Ebene wird
    übersprungen (1 → 3 wird 1 → 2), ein Buch nur mit Ebene 2 hat lauter Einträge der obersten Stufe."""
    out, stack = [], []
    for lv in levels:
        while stack and stack[-1] >= lv:
            stack.pop()
        stack.append(lv)
        out.append(len(stack))
    return out


def build(data, progress=lambda done, total, msg: None, cancelled=lambda: False):
    """Aus den Seiten (gather) die Dateien des EPUB: dict(files=[(name, titel, xhtml)], toc, pages, stats)."""
    pages, labels = data['pages'], data['labels']
    flow = _Flow(pages, labels, data.get('foot') or {}, data.get('kopf') or {})
    blocks = flow.run(progress, cancelled)
    heads = [b for b in blocks if b['kind'] == 'h']
    for b, d in zip(heads, depths([b['level'] for b in heads])):
        b['depth'] = d
    # Dateien: jede Überschrift der obersten Stufe beginnt eine neue; ein Buch ohne sie wird nach Größe geteilt.
    # Seitenmarken unmittelbar davor wandern mit – sie gehören zur Seite, auf der das Kapitel beginnt
    parts, cur, size = [], [], 0
    for b in blocks:
        split = cur and any(x['kind'] != 'mark' for x in cur) and (
            (b['kind'] == 'h' and b['depth'] == 1) or (b['kind'] in ('p', 'h') and size > GROSS))
        if split:
            tail = []
            while cur and cur[-1]['kind'] == 'mark':
                tail.insert(0, cur.pop())
            parts.append(cur)
            cur, size = tail, sum(len(x['html']) for x in tail)
        cur.append(b)
        size += len(b['html'])
    if cur or not parts:
        parts.append(cur)
    files, where = [], {}
    for n, part in enumerate(parts, 1):
        name = 'text-%03d.xhtml' % n
        body = '\n'.join(b['html'] for b in part)
        for m in re.finditer(r' id="([^"]+)"', body):
            where[m.group(1)] = name
        title = next((b['text'] for b in part if b['kind'] == 'h'), data['title'])
        files.append([name, title, body])

    def href(i, here=None):
        f = where.get(i, files[0][0])
        return '#' + i if f == here else f + '#' + i
    for f in files:  # Links über Dateigrenzen: Fußnote und Verweis können in verschiedenen Dateien liegen
        f[2] = re.sub(r'href="#([^"]+)"', lambda m, here=f[0]: 'href="%s"' % href(m.group(1), here), f[2])
    toc = [(b['depth'], dict(text=b['text'], href=href(b['id']), page=labels.get(b['page']))) for b in heads]
    plist = [(labels[pg], href('seite-' + pg)) for pg in pages if labels.get(pg) and 'seite-' + pg in where]
    notes = [x for v in flow.notes.values() for x in v]
    stats = dict(flow.stats, pages=len(pages), files=len(files), notes=len(notes), linked=sum(1 for x in notes if x['ref']),
                 marked=len(plist), fallback=flow.fallback)
    return dict(files=[tuple(f) for f in files], toc=toc, pagelist=plist, stats=stats)


def _nav(title, toc, plist, first, inhalt):
    def ol(nodes):
        return '<ol>%s</ol>' % ''.join('<li><a href="%s">%s</a>%s</li>' % (esc(e['href']), esc(e['text']), ol(k) if k else '') for e, k in nodes)
    toc = toc or [(1, dict(text=title, href=first))]
    body = '<nav epub:type="toc" role="doc-toc" id="toc"><h1>%s</h1>%s</nav>' % (W['inhalt'], ol(_tree(toc)))
    if plist:
        body += '\n<nav epub:type="page-list" id="seiten" hidden="hidden"><h1>%s</h1><ol>%s</ol></nav>' % (
            W['seiten'], ''.join('<li><a href="%s">%s</a></li>' % (esc(h), esc(l)) for l, h in plist))
    marks = [('titlepage', 'titel.xhtml', W['titelseite'])] + ([('toc', 'inhalt.xhtml', W['inhalt'])] if inhalt else []) + [('bodymatter', first, W['text'])]
    body += '\n<nav epub:type="landmarks" id="orientierung" hidden="hidden"><h1>%s</h1><ol>%s</ol></nav>' % (
        W['orientierung'], ''.join('<li><a epub:type="%s" href="%s">%s</a></li>' % (t, esc(h), esc(x)) for t, h, x in marks))
    return _doc(title, body)


def _inhalt(title, toc):
    """Die sichtbare Seite »Inhalt« gleich nach der Titelseite: Lese-Apps öffnen vorn. Jeder Eintrag ein Link mit der
    gedruckten Seitenzahl."""
    def ol(nodes):
        return '<ol>%s</ol>' % ''.join('<li><a href="%s">%s</a>%s%s</li>' % (
            esc(e['href']), esc(e['text']), ' <span class="s">%s</span>' % esc(e['page']) if e['page'] else '', ol(k) if k else '') for e, k in nodes)
    return _doc(W['inhalt'], '<section class="inhalt"><h1>%s</h1>%s</section>' % (W['inhalt'], ol(_tree(toc))))


def _titel(data, marked):
    rows = ['<h1>%s</h1>' % esc(data['title'])]
    if data.get('author'):
        rows.append('<p class="autor">%s</p>' % esc(data['author']))
    if data.get('year'):
        rows.append('<p class="jahr">%s</p>' % esc(str(data['year'])))
    if marked:
        rows.append('<p class="hinweis">%s</p>' % W['seitenzahlen'])
    rows.append('<p class="hinweis">%s</p>' % W['erstellt'])
    return _doc(data['title'], '<section class="titel" epub:type="titlepage">%s</section>' % '\n'.join(rows))


def _ncx(uid, title, toc, first):
    toc = toc or [(1, dict(text=title, href=first))]
    count = [0]

    def points(nodes):
        out = ''
        for e, kids in nodes:
            count[0] += 1
            out += '<navPoint id="np%d" playOrder="%d"><navLabel><text>%s</text></navLabel><content src="%s"/>%s</navPoint>' % (
                count[0], count[0], esc(e['text']), esc(e['href']), points(kids))
        return out
    nav = points(_tree(toc))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="de">\n'
            '<head><meta name="dtb:uid" content="%s"/><meta name="dtb:depth" content="%d"/><meta name="dtb:totalPageCount" content="0"/>'
            '<meta name="dtb:maxPageNumber" content="0"/></head>\n<docTitle><text>%s</text></docTitle>\n<navMap>%s</navMap>\n</ncx>\n') % (
        esc(uid), max([d for d, e in toc] or [1]), esc(title), nav)


def _opf(data, uid, files, inhalt, cover, stats):
    meta = ['<dc:identifier id="uid">%s</dc:identifier>' % esc(uid), '<dc:title>%s</dc:title>' % esc(data['title']),
            '<dc:language>de</dc:language>']
    if data.get('author'):
        meta.append('<dc:creator>%s</dc:creator>' % esc(data['author']))
    meta.append('<meta property="dcterms:modified">%s</meta>' % time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    # das Programm als »book producer« (MARC-Rolle bkp), wie es auch Calibre einträgt
    meta += ['<dc:contributor id="prog">%s</dc:contributor>' % esc(('Fraktur-Korrektor ' + (data.get('version') or '')).strip()),
             '<meta refines="#prog" property="role" scheme="marc:relators">bkp</meta>']
    # Barrierefreiheit (EPUB Accessibility 1.1): was das Buch bietet – Lese-Apps und Kataloge zeigen es an
    feats = ['structuralNavigation' if stats['headings'] else None, 'tableOfContents', 'printPageNumbers' if stats['marked'] else None]
    meta += ['<meta property="schema:accessMode">textual</meta>', '<meta property="schema:accessModeSufficient">textual</meta>']
    meta += ['<meta property="schema:accessibilityFeature">%s</meta>' % f for f in feats if f]
    meta += ['<meta property="schema:accessibilityHazard">none</meta>',
             '<meta property="schema:accessibilitySummary">Text einer gescannten Druckausgabe, von Hand korrigiert; Inhaltsverzeichnis aus den '
             'Überschriften, Seitenzahlen der Druckausgabe, Fußnoten als Links.</meta>']
    if stats['marked']:
        meta.append('<meta property="pageBreakSource">%s</meta>' % esc(
            'Druckausgabe' + (' %s' % data['year'] if data.get('year') else '')))
    items = ['<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
             '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
             '<item id="stil" href="stil.css" media-type="text/css"/>',
             '<item id="titel" href="titel.xhtml" media-type="application/xhtml+xml"/>']
    spine = ['<itemref idref="titel"/>']
    if inhalt:
        items.append('<item id="inhalt" href="inhalt.xhtml" media-type="application/xhtml+xml"/>')
        spine.append('<itemref idref="inhalt"/>')
    for name, title, body in files:
        i = name[:-6]
        items.append('<item id="%s" href="%s" media-type="application/xhtml+xml"/>' % (i, name))
        spine.append('<itemref idref="%s"/>' % i)
    if cover:
        items.append('<item id="umschlag" href="umschlag.jpg" media-type="image/jpeg" properties="cover-image"/>')
        meta.append('<meta name="cover" content="umschlag"/>')  # für ältere Lesegeräte (EPUB 2)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid" xml:lang="de">\n'
            '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n%s\n</metadata>\n<manifest>\n%s\n</manifest>\n'
            '<spine toc="ncx">\n%s\n</spine>\n</package>\n') % ('\n'.join(meta), '\n'.join(items), '\n'.join(spine))


def uid_of(kennung):
    """dc:identifier aus der Kennung des Buchs (32 Hexziffern) als urn:uuid."""
    k = (kennung or '').lower()
    if not re.fullmatch(r'[0-9a-f]{32}', k):
        return None
    return 'urn:uuid:%s-%s-%s-%s-%s' % (k[:8], k[8:12], k[12:16], k[16:20], k[20:])


def kennung(path):
    """Die Kennung des Buchs, wenn path ein EPUB ist, das dieses Programm geschrieben hat (urn:uuid im dc:identifier) –
    sonst None. Auch für fremde EPUBs mit urn:uuid: Die Kennung trifft dann einfach kein Buch."""
    try:
        with zipfile.ZipFile(path) as z:
            opf = ET.fromstring(z.read('META-INF/container.xml')).find('.//{*}rootfile').get('full-path')
            root = ET.fromstring(z.read(opf))
        uid = root.get('unique-identifier')
        for e in root.iter('{http://purl.org/dc/elements/1.1/}identifier'):
            if e.get('id') == uid and e.text:
                m = re.fullmatch(r'urn:uuid:([0-9a-f]{8})-([0-9a-f]{4})-([0-9a-f]{4})-([0-9a-f]{4})-([0-9a-f]{12})', e.text.strip().lower())
                return ''.join(m.groups()) if m else None
    except Exception:
        return None
    return None


def _umschlag(path):
    """Die erste Scanseite als Umschlagbild: JPEG, höchstens UMSCHLAG Pixel hoch – Lese-Apps zeigen es in der Bücherliste."""
    if not path:
        return None
    try:
        import fitz
        pix = fitz.Pixmap(path)
        if pix.alpha:
            pix = fitz.Pixmap(pix, 0)
        if pix.colorspace is None or pix.colorspace.n not in (1, 3):
            pix = fitz.Pixmap(fitz.csRGB, pix)
        if pix.height > UMSCHLAG:
            pix = fitz.Pixmap(pix, max(1, round(pix.width * UMSCHLAG / pix.height)), UMSCHLAG)
        return pix.tobytes('jpeg', jpg_quality=80)
    except Exception:  # ohne PyMuPDF oder bei einem unlesbaren Bild: ohne Umschlag
        return None


def gather(book):
    """Was der Export vom Buch (server.Book) braucht – einmal unter der Sperre gelesen, danach arbeitet er auf einer Kopie.
    labels: die gedruckte Seitenzahl je Seite oder None; anders als printed_page ohne Rückfall auf die Dateinummer – eine
    erfundene Seitenzahl wäre im E-Book schlimmer als keine."""
    with book.lock:
        book.refresh()
        pages = {pg: list(v) for pg, v in book.pages.items()}
        labels = {}
        for pg in pages:
            n, exp = book.page_number(pg), book.expected_page(pg)
            labels[pg] = str(exp) if exp is not None else str(n[0]) if n else None
        foot = {pg: v[1] for pg, v in book.feet.items()}
        kopf = {pg: book.kopf(pg) for pg in pages}
        st = dict(book.settings)
    cover = next((p for p in (book.img_file(pg) for pg in pages) if p), None)
    return dict(pages=pages, labels=labels, foot=foot, kopf=kopf, title=book.title, author=st.get('autor'), year=st.get('year'),
                kennung=st.get('kennung'), cover=cover)


def preview(book):
    """Was das E-Book enthalten wird – für den Dialog vor dem Sichern: Überschriften, Absätze, Fußnoten, Seitenzahlen."""
    return build(gather(book))['stats']


def write(data, out, version='', progress=lambda done, total, msg: None, cancelled=lambda: False):
    """Das EPUB nach out schreiben; erst in eine Nachbardatei, dann umbenennen. Liefert die Kennzahlen samt file und size."""
    if not data['pages']:
        raise ValueError('quelle_fehlt')
    data = dict(data, version=version)
    r = build(data, progress, cancelled)
    uid = uid_of(data.get('kennung')) or 'urn:fraktur-korrektor:%s' % re.sub(r'\W+', '-', data['title']).strip('-').lower()
    first, inhalt = r['files'][0][0], bool(r['toc'])
    cover = _umschlag(data.get('cover'))
    tmp = out + '.tmp'
    try:
        with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr(zipfile.ZipInfo('mimetype'), MIME, compress_type=zipfile.ZIP_STORED)  # vorn und unkomprimiert
            z.writestr('META-INF/container.xml', '<?xml version="1.0" encoding="UTF-8"?>\n'
                       '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles>'
                       '<rootfile full-path="%s" media-type="application/oebps-package+xml"/></rootfiles></container>\n' % OPF)
            z.writestr(OPF, _opf(data, uid, r['files'], inhalt, cover, r['stats']))
            z.writestr('OEBPS/nav.xhtml', _nav(data['title'], r['toc'], r['pagelist'], first, inhalt))
            z.writestr('OEBPS/toc.ncx', _ncx(uid, data['title'], r['toc'], first))
            z.writestr('OEBPS/stil.css', CSS)
            z.writestr('OEBPS/titel.xhtml', _titel(data, r['stats']['marked']))
            if inhalt:
                z.writestr('OEBPS/inhalt.xhtml', _inhalt(data['title'], r['toc']))
            for name, title, body in r['files']:
                z.writestr('OEBPS/' + name, _doc(title, body))
            if cover:
                z.writestr('OEBPS/umschlag.jpg', cover, compress_type=zipfile.ZIP_STORED)
        os.replace(tmp, out)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    return dict(r['stats'], file=out, size=os.path.getsize(out), cover=bool(cover))


def save(book, out, version='', progress=lambda done, total, msg: None, cancelled=lambda: False):
    """Das Buch (ein server.Book) als EPUB nach out schreiben."""
    return write(gather(book), out, version, progress, cancelled)
