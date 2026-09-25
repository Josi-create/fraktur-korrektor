"""Zwei Arbeitsstände desselben Buchs zusammenführen (#66).

Ein Buch wird als PDF gesichert, am Laptop eingelesen und dort weiterkorrigiert, wieder gesichert – und zurück am
PC wurde inzwischen auch korrigiert. Dann reicht Ersetzen nicht mehr. Aber korrekturen.log hält jede Änderung fest
(Zeit, Art, Seite, Zeile, alt, neu), und so lassen sich die Einträge, die nur im PDF stehen, auf das hiesige Buch
nachspielen – wie ein Rebase: Zeile für Zeile, wenn die Zeile hier noch so aussieht wie dort vor der Änderung.

Was sich nicht sicher nachspielen lässt (die Zeile wurde hier anders geändert, eine geteilte Zeile gibt es so nicht
mehr), wird nie halb angewendet, sondern als Konflikt in konflikte.json vermerkt; die Leseansicht zeigt die Zeile
mit beiden Fassungen, und der Nutzer entscheidet. Nachgespielte Einträge kommen wortgleich (mit ihrer Zeit vom
anderen Rechner) ins hiesige Protokoll: So enthält es danach alles, was das PDF enthält, und beim nächsten Wechsel in
die andere Richtung genügt wieder das einfache Ersetzen.

Das Modul kennt kein PDF und keinen Server: Es bekommt den anderen Stand als Texte und arbeitet über ein
server.Book, dessen edit/split_line/join_lines/fnsep/delete_lines Seiten und lines.json wie gewohnt zusammenhalten."""
import os, json, collections

KONFLIKTE = 'konflikte.json'
TRENNER = ' ⏎ '   # so schreibt Book.klog die zwei Hälften einer geteilten bzw. verbundenen Zeile


def rows(text):
    """Die Zeilen eines Protokolls, wie sie dastehen (ohne Zeilenende)."""
    return [l for l in (text or '').splitlines() if l.strip()]


def compare(mine, theirs):
    """Was steht nur hier, was nur dort? Die Einträge werden als Mengen verglichen, nicht als Folge: Nach einem
    Zusammenführen stehen die fremden Einträge hier hinter den eigenen, und trotzdem fehlt dann nichts.
    Liefert dict(safe, here, there, only_here, only_there); safe = alles Hiesige steht auch dort, das PDF darf
    das Buch ersetzen."""
    a, b = rows(mine), rows(theirs)
    ca, cb = collections.Counter(a), collections.Counter(b)
    only_here = [r for r in a if _take(cb, r)]
    ca2 = collections.Counter(a)
    only_there = [r for r in b if _take(ca2, r)]
    return dict(safe=not only_here, here=len(only_here), there=len(only_there), only_here=only_here, only_there=only_there)


def _take(counter, r):
    """True, wenn r im anderen Protokoll nicht (mehr) vorkommt; sonst dort einmal abgebucht."""
    if counter[r] > 0:
        counter[r] -= 1
        return False
    return True


def parse(row):
    """Ein Protokolleintrag als (zeit, art, seite, zeile 0-basiert, alt, neu) – None, wenn er nicht so aussieht."""
    f = row.split('\t')
    if len(f) != 6:
        return None
    try:
        line = int(f[3]) - 1
    except ValueError:
        return None
    return f[0], f[1], f[2], line, f[4], f[5]


def load_conflicts(folder):
    try:
        with open(os.path.join(folder, KONFLIKTE), encoding='utf-8') as f:
            k = json.load(f)
        return k if isinstance(k, list) else []
    except (OSError, ValueError):
        return []


def save_conflicts(folder, items):
    p = os.path.join(folder, KONFLIKTE)
    if not items:
        try:
            os.remove(p)
        except OSError:
            pass
        return
    tmp = p + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def resolve(folder, done):
    """Konflikte austragen (der Nutzer hat entschieden): alle, die einem der Einträge in done gleichen – an der
    Zeilennummer nicht gemessen, die kann sich seit dem Zusammenführen verschoben haben."""
    key = lambda k: (k.get('page'), k.get('art'), k.get('alt'), k.get('dort'), k.get('zeit'))
    gone = {key(k) for k in done}
    items = load_conflicts(folder)
    rest = [k for k in items if key(k) not in gone]
    save_conflicts(folder, rest)
    return len(items) - len(rest)


class Merge:
    """Ein Zusammenführen: theirs = dict(log, whitelist, bookmark, pages, geo, image) – die Texte aus dem PDF-Anhang
    (pages: Seite -> Zeilen, geo: lines.json) und image(pg): holt das Seitenbild des anderen Stands in den Buchordner."""

    def __init__(self, book, theirs):
        self.book, self.theirs = book, theirs
        self.applied = self.already = 0
        self.conflicts, self.pages = [], set()

    def run(self):
        book = self.book
        with book.lock:
            book.refresh()
            cmp = compare(_read(book.klogpath), self.theirs.get('log', ''))
            touched_here = {parse(r)[2] for r in cmp['only_here'] if parse(r)}
            for r in cmp['only_there']:
                self._replay(r, touched_here)
            wl = self._whitelist(cmp)
            bm = self._bookmark()
            if self.conflicts:
                items = load_conflicts(book.folder)
                for k in self.conflicts:
                    if k not in items:
                        items.append(k)
                save_conflicts(book.folder, items)
            book.refresh()
        return dict(applied=self.applied, already=self.already, conflicts=len(self.conflicts), whitelist=wl, bookmark=bm,
                    pages=sorted(self.pages), only_here=cmp['here'], only_there=cmp['there'])

    # ---- ein Eintrag

    def _replay(self, row, touched_here):
        p = parse(row)
        if not p:
            return
        when, kind, pg, n, old, new = p
        book = self.book
        if kind.startswith('whitelist'):
            return  # kommt gesammelt, siehe _whitelist
        if pg == '-' or pg not in book.pages:
            if pg == '-':
                book.klog(kind, '-', -1, old, new, when=when)  # undo:ID ohne Wirkung – dazu gehört kein Text
            return
        lines = book.pages[pg]
        if kind == 'edit' or kind.startswith('serie:') or kind.startswith('undo:'):
            if 0 <= n < len(lines) and lines[n] == old:
                if book.edit(pg, [dict(line=n, old=old, new=new)], kind=kind, when=when):
                    return self._done(pg)
            elif 0 <= n < len(lines) and lines[n] == new:
                return self._same(row, when, kind, pg, n, old, new)
            return self._conflict(pg, n, 'edit', old, new, when)
        if kind == 'teilen':
            left, _, right = new.partition(TRENNER)
            if 0 <= n < len(lines) - 1 and lines[n] == left and lines[n + 1] == right:
                return self._same(row, when, kind, pg, n, old, new)
            if 0 <= n < len(lines) and lines[n] == old and right:
                pos = next((k for k in range(len(old) + 1) if old[:k].rstrip() == left and old[k:].lstrip() == right), None)
                if pos is not None and book.split_line(pg, n, old, old, pos, when=when)[0]:
                    return self._done(pg)
            return self._conflict(pg, n, 'teilen', old, new, when)
        if kind == 'verbinden':
            a, _, b = old.partition(TRENNER)
            if 0 <= n < len(lines) and lines[n] == new:
                return self._same(row, when, kind, pg, n, old, new)
            if 0 <= n < len(lines) - 1 and lines[n] == a and lines[n + 1] == b:
                r = book.join_lines(pg, n, [a, b], when=when)[0]
                if r:
                    if r['lines'][n] != new:  # dieselben Hälften, anders verbunden (andere Programmversion): der Nutzer sieht es sich an
                        self._conflict(pg, n, 'edit', r['lines'][n], new, when)
                    return self._done(pg)
            return self._conflict(pg, n, 'verbinden', old, new, when)
        if kind.startswith('loeschen:'):
            # Gelöscht wird nur die Zeile mit genau diesem Wortlaut – an n oder, wenn sich die Seite hier verschoben hat,
            # der nächstgelegenen. Fehlt sie und wurde sie hier selbst gelöscht, ist nichts zu tun; wurde sie hier
            # geändert, entscheidet der Nutzer
            k = n if 0 <= n < len(lines) and lines[n] == old else \
                min((i for i, l in enumerate(lines) if l == old), key=lambda i: abs(i - n), default=None)
            if k is not None and book.delete_lines(pg, k, [old], when=when, kind=kind)[0]:
                return self._done(pg)
            if k is None and self._deleted_here(pg, old):
                return self._same(row, when, kind, pg, n, old, new)
            return self._conflict(pg, min(max(0, n), len(lines) - 1), 'loeschen', old, new, when)
        if kind.startswith('zurueck:'):
            if 0 <= n < len(lines) and lines[n] == new:
                return self._same(row, when, kind, pg, n, old, new)
            if book.replay_undelete(pg, n, new, when, kind):
                return self._done(pg)
            return self._conflict(pg, min(max(0, n), len(lines) - 1), 'zurueck', old, new, when)
        if kind == 'fnsep':
            return self._fnsep(row, when, pg, n, old, new)
        if kind == 'seite':
            # Die Seite wurde dort neu erkannt (anderes Bild, anderer Text): Ganz übernehmen geht nur, wenn hier an ihr
            # seit dem Sichern nichts geschah – sonst bleibt sie hier, wie sie ist, und wird angezeigt
            if pg not in touched_here and pg in self.theirs.get('pages', {}):
                book.write_page(pg, self.theirs['pages'][pg])
                book.refresh()
                if pg in self.theirs.get('geo', {}):
                    book.geo[pg] = self.theirs['geo'][pg]
                    book.save_geo()
                if self.theirs.get('image'):
                    self.theirs['image'](pg)
                book.klog(kind, pg, n, old, new, when=when)
                return self._done(pg)
            return self._conflict(pg, 0, 'seite', old, new, when)
        return self._conflict(pg, max(0, n), 'sonst', old, new, when)

    def _fnsep(self, row, when, pg, n, old, new):
        """Fußnotentrenner. Book.fnsep protokolliert die Zeile NACH dem Strich: 'gesetzt' – der Strich steht jetzt an n-1,
        new ist die Zeile n dahinter; 'entfernt' – der Strich stand an n, new ist die Zeile, die dort jetzt steht."""
        book, lines = self.book, self.book.pages[pg]
        has = '---' in lines
        if old == 'gesetzt':
            if 0 < n < len(lines) and lines[n - 1] == '---' and lines[n] == new:
                return self._same(row, when, 'fnsep', pg, n, old, new)
            # Ohne Strich hier steht die Zeile dahinter noch an n-1; der Strich kommt vor sie – nur, wenn sie noch so lautet,
            # sonst hat sich die Seite hier verschoben, und der Nutzer setzt ihn selbst
            if not has and 0 < n <= len(lines) and lines[n - 1] == new and book.fnsep(pg, n - 1, new, when=when):
                return self._done(pg)
        elif old == 'entfernt':
            if not has:
                return self._same(row, when, 'fnsep', pg, n, old, new)
            # die Zeile danach darf hier inzwischen anders lauten – entscheidend ist, dass der Strich an n stand
            if 0 <= n < len(lines) - 1 and lines[n] == '---' and book.fnsep(pg, n + 1, lines[n + 1], when=when):
                return self._done(pg)
        return self._conflict(pg, min(max(0, n), len(lines) - 1), 'fnsep', old, new, when)

    def _done(self, pg):
        self.applied += 1
        self.pages.add(pg)

    def _deleted_here(self, pg, text):
        """Wurde diese Zeile auch hier gelöscht? Dann steht es im hiesigen Protokoll."""
        return any(p and p[1].startswith('loeschen:') and p[2] == pg and p[4] == text for p in map(parse, rows(_read(self.book.klogpath))))

    def _same(self, row, when, kind, pg, n, old, new):
        """Die Änderung ist hier schon so geschehen (beide haben dasselbe berichtigt): nur ins Protokoll, damit es
        alles enthält, was das PDF enthält."""
        self.book.klog(kind, pg, n, old, new, when=when)
        self.already += 1

    def _conflict(self, pg, n, art, alt, dort, when):
        lines = self.book.pages[pg]
        self.conflicts.append(dict(page=pg, line=n, art=art, hier=lines[n] if 0 <= n < len(lines) else '', alt=alt, dort=dort, zeit=when))

    # ---- Wortliste und Lesezeichen

    def _whitelist(self, cmp):
        """Erst die dortigen Einträge (+/−) nachspielen, dann alles aufnehmen, was dort in der Liste steht und hier
        nicht absichtlich herausgenommen wurde. Liefert die Zahl der neu aufgenommenen Wörter."""
        book = self.book
        words = list(dict.fromkeys(book.whitelist()))
        removed_here = {parse(r)[4] for r in cmp['only_here'] if parse(r) and parse(r)[1] == 'whitelist-'}
        added = 0
        for r in cmp['only_there']:
            p = parse(r)
            if not p or not p[1].startswith('whitelist'):
                continue
            when, kind, w = p[0], p[1], p[4]
            if kind == 'whitelist+' and w not in words:
                words.append(w)
                added += 1
            elif kind == 'whitelist-' and w in words:
                words = [x for x in words if x != w]
            book.klog(kind, '-', -1, w, '', when=when)
        for w in (self.theirs.get('whitelist') or '').split():
            if w not in words and w not in removed_here:
                words.append(w)
                added += 1
                book.klog('whitelist+', '-', -1, w, '')
        if words != list(dict.fromkeys(book.whitelist())):
            _write(book.wlpath, ''.join(w + '\n' for w in words))
        return added

    def _bookmark(self):
        """Es gilt das Lesezeichen, das weiter hinten im Buch liegt – dort wurde zuletzt gelesen."""
        book, theirs = self.book, self.theirs.get('bookmark') or {}
        if not theirs.get('page'):
            return None
        try:
            mine = json.load(open(book.bmpath, encoding='utf-8'))
        except (OSError, ValueError):
            mine = {}
        key = lambda b: (str(b.get('page') or ''), int(b.get('line') or 0))
        if key(theirs) > key(mine):
            _write(book.bmpath, json.dumps(dict(page=theirs.get('page'), line=theirs.get('line'))))
            return theirs.get('page')
        return mine.get('page')


def _read(path):
    try:
        return open(path, encoding='utf-8').read()
    except OSError:
        return ''


def _write(path, text):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(text)
    os.replace(tmp, path)
