"""Gemeinsames: Wörterbücher (Hunspell via spylls), Korpusfrequenz, Tokenisierung.

Welche Rechtschreibung gilt, ist je Buch wählbar (DICS):
  1901     Rechtschreibung 1901–1996 (daß, Schiffahrt) – mitgeliefert: dict/de_DE_OLDSPELL. Ein anderes Wörterbuch an dieser
           Stelle: set_dic(pfad) bzw. --dic, Umgebungsvariable FRAKTUR_DIC, "dic" in ~/.fraktur-korrektor/config.json
  neu      neue Rechtschreibung ab 1996 (dass, Schifffahrt) – mitgeliefert: dict/de_DE_frami
  vor1901  kein Wörterbuch, sondern Regeln: Thür, seyn, Noth, civilisiren gelten, wenn die heutige Form bekannt ist
dict/zusatz.txt: zusätzlich gültige Wörter (Abkürzungen); dict/fallen.txt: nie gültig, weil fast immer OCR-Fehler (baß)."""
import os, re, sys, glob, json, time, atexit, hashlib, collections, functools, itertools, threading
from spylls.hunspell import Dictionary
HERE = getattr(sys, '_MEIPASS', None) or os.path.dirname(os.path.abspath(__file__))  # gepackt liegt dict/ im Bundle
HOME = os.environ.get('FRAKTUR_HOME') or os.path.join(os.path.expanduser('~'), '.fraktur-korrektor')
WORD = re.compile(r"[A-Za-zÄÖÜäöüß]+")
DICS = ('1901', 'neu', 'vor1901')
DEFAULT = ('1901',)
DIC = None
def config():
    p = os.path.join(HOME, 'config.json')
    try: return json.load(open(p, encoding='utf-8'))
    except OSError: return {}
    except ValueError as e:
        print('Warnung: %s ist kein gültiges JSON und wird ignoriert (%s)' % (p, e))
        return {}
def set_config(key, value):
    c = config(); c[key] = value
    os.makedirs(HOME, exist_ok=True)
    with open(os.path.join(HOME, 'config.json'), 'w', encoding='utf-8') as f:
        json.dump(c, f, ensure_ascii=False, indent=2)
def _base(path):
    return path[:-4] if path.lower().endswith(('.dic', '.aff')) else path
def find_dic():
    """Wörterbuch für '1901': erster Kandidat, zu dem .dic und .aff existieren; sonst Abbruch mit verständlicher Meldung."""
    cand = [DIC, os.environ.get('FRAKTUR_DIC'), config().get('dic'), os.path.join(HERE, 'dict', 'de_DE_OLDSPELL', 'de_DE_OLDSPELL')]
    cand = [_base(c) for c in cand if c]
    for c in cand:
        if os.path.exists(c + '.dic') and os.path.exists(c + '.aff'):
            return c
    raise SystemExit('Kein Wörterbuch gefunden. Gesucht wurde (jeweils .dic und .aff):\n  ' + '\n  '.join(cand) +
                     '\nAbhilfe: den Ordner dict/ des Programms wiederherstellen oder ein Hunspell-Wörterbuch mit --dic <pfad> angeben.')
class Checker:
    """Ein Hunspell-Wörterbuch mit Zwischenspeicher der Prüfergebnisse auf der Platte (die freien Wörterbücher prüfen langsam).
    Das Wörterbuch selbst wird erst eingelesen, wenn ein Wort nicht im Zwischenspeicher steht: spylls braucht dafür mehrere
    Sekunden, und bei einem Buch, das schon einmal offen war, kommt es meist gar nicht dazu (warm() holt es im Hintergrund)."""
    def __init__(self, path):
        self.path, self.d, self.cache, self.lock = path, None, {}, threading.Lock()
        key = '|'.join([self.path] + [str(os.path.getmtime(self.path + e)) for e in ('.dic', '.aff')])
        self.cache_path = os.path.join(HOME, 'cache', hashlib.md5(key.encode('utf-8')).hexdigest() + '.json')
        try: self.cache.update(json.load(open(self.cache_path, encoding='utf-8')))
        except (OSError, ValueError): pass
        self.n = len(self.cache)
    def load(self):
        with self.lock:  # zwei Anfragen zugleich sollen das Wörterbuch nicht zweimal einlesen
            if self.d is None:
                self.d = Dictionary.from_files(self.path)
        return self.d
    def lookup(self, w):
        if w not in self.cache:
            d = self.d or self.load()
            if w not in self.cache:
                # auch klein (Satzanfang) und groß (Substantivierung) – aber jede Schreibweise nur einmal: Fehlversuche sind teuer
                self.cache[w] = any(d.lookup(v) for v in dict.fromkeys((w, w.lower(), w[0].upper() + w[1:])))
        return self.cache[w]
    def save(self):
        # Ein Hintergrundauftrag und eine Anfrage des Browsers speichern sonst zugleich über dieselbe .tmp-Datei, und wer
        # zuletzt umbenennt, findet sie nicht mehr. Eigene Sperre: self.lock hält load() sekundenlang.
        with _savelock:
            if self.cache_path and len(self.cache) > self.n:
                os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
                stand = dict(self.cache)  # lookup() trägt währenddessen weiter ein
                tmp = self.cache_path + '.tmp'
                with open(tmp, 'w', encoding='utf-8') as f:
                    json.dump(stand, f, ensure_ascii=False)
                # Unter Windows schlägt das Umbenennen fehl, solange ein anderer die Datei gerade offen hat – der Virenscanner
                # oder die Suche sehen sich jede frisch geschriebene Datei kurz an. Darum ein paar Anläufe; klappt es dann
                # immer noch nicht, bleibt der alte Stand auf der Platte (nur ein Zwischenspeicher, nichts geht verloren).
                for versuch in range(20):
                    try:
                        os.replace(tmp, self.cache_path)
                        self.n = len(stand)
                        break
                    except PermissionError:
                        time.sleep(0.05)
                else:
                    try: os.remove(tmp)
                    except OSError: pass
_checkers, _savelock, _newlock = {}, threading.Lock(), threading.Lock()
def checker(name='1901'):
    if name not in _checkers:
        with _newlock:  # zwei Threads zugleich sollen nicht zwei Wörterbücher anlegen (und beide einlesen)
            if name not in _checkers:
                _checkers[name] = Checker(find_dic() if name == '1901' else os.path.join(HERE, 'dict', 'de_DE_frami', 'de_DE_frami'))
    return _checkers[name]
def warm(name='1901'):
    """Das Wörterbuch im Hintergrund einlesen, damit das erste unbekannte Wort später nicht darauf warten muss."""
    threading.Thread(target=lambda: checker(name).load(), daemon=True).start()
def set_dic(path):
    global DIC
    DIC = _base(path)
    _checkers.pop('1901', None); in_dict.cache_clear()
def save_cache():
    for c in list(_checkers.values()): c.save()
atexit.register(save_cache)
def _wordlist(name):
    p = os.path.join(HERE, 'dict', name)
    return {w for l in open(p, encoding='utf-8') if not l.startswith('#') for w in l.split()} if os.path.exists(p) else set()
ZUSATZ, FALLEN = _wordlist('zusatz.txt'), _wordlist('fallen.txt')
# Schreibungen vor 1901 -> heutige Form; jede Regel einzeln und alle zusammen werden versucht
OLD = [(r'th', 't'), (r'Th', 'T'), (r'(?<=[ae])y', 'i'), (r'ir(?=en$|t$|te$|ten$|ung$|ungen$)', 'ier'), (r'c(?=[aou])', 'k'), (r'C(?=[aou])', 'K'),
       (r'c(?=[eiä])', 'z'), (r'C(?=[eiä])', 'Z'), (r'ct', 'kt'), (r'aa', 'a'), (r'oo', 'o'), (r'dt$', 't'), (r'(?<=[a-zäöü])d$', 't'),
       (r'ie(?=bt|ng)', 'i'), (r'ß$', 's'), (r'et$', 't'), (r'eten$', 'ten')]
OLD = [(re.compile(a), b) for a, b in OLD]
def modern(w):
    """Mögliche heutige Formen einer alten Schreibung: Thür -> Tür, seyn -> sein, Noth -> Not, civilisiren -> zivilisieren."""
    one = {r.sub(b, w) for r, b in OLD} - {w}
    allr = w
    for r, b in OLD[:10]: allr = r.sub(b, allr)
    two = {r.sub(b, v) for v in one for r, b in OLD[:10]}
    return (one | two | {allr}) - {w}
@functools.lru_cache(maxsize=None)
def in_dict(w, dics=DEFAULT):
    if len(w) <= 1 or w in ZUSATZ: return True
    if w in FALLEN: return False
    real = [d for d in dics if d != 'vor1901'] or ['1901']
    if any(checker(d).lookup(w) for d in real): return True
    return 'vor1901' in dics and len(w) > 2 and any(checker(d).lookup(v) for v in modern(w) for d in real)
# ---- Korrekturvorschläge (#41). Erst das Billige: Was die Fraktur-OCR typischerweise verwechselt (b/d, f/s, n/u, r/t,
# ll/tt, fehlende Umlautpunkte), an jeder Stelle des Wortes einmal getauscht und nachgesehen, ob das ein Wort ergibt.
# Hunspell selbst erst danach: spylls braucht dafür Sekunden, darum mit Zeitbudget.
CONFUSIONS = [('b', 'd'), ('d', 'b'), ('f', 's'), ('s', 'f'), ('n', 'u'), ('u', 'n'), ('r', 't'), ('t', 'r'), ('t', 'k'), ('k', 't'),
              ('l', 'i'), ('i', 'l'), ('c', 'e'), ('e', 'c'), ('o', 'v'), ('v', 'o'), ('h', 'b'), ('b', 'h'), ('ll', 'tt'), ('tt', 'll'),
              ('rn', 'm'), ('m', 'rn'), ('in', 'm'), ('ii', 'n'), ('ck', 'd'), ('a', 'ä'), ('o', 'ö'), ('u', 'ü'), ('ä', 'a'), ('ö', 'o'),
              ('ü', 'u'), ('ß', 'ss'), ('ss', 'ß'), ('B', 'V'), ('V', 'B'), ('R', 'N'), ('N', 'R'), ('S', 'G'), ('G', 'S'), ('J', 'I'),
              ('I', 'J'), ('C', 'E'), ('E', 'C'), ('D', 'O'), ('O', 'D'), ('K', 'R'), ('R', 'K'), ('Z', 'B'), ('B', 'Z'), ('T', 'X'),
              ('A', 'U'), ('U', 'A'), ('M', 'N'), ('W', 'B')]
def ocr_candidates(w, ok):
    """Wörter, die sich von w um eine typische Verwechslung unterscheiden und die ok() für gültig hält."""
    out = []
    for a, b in CONFUSIONS:
        i = w.find(a)
        while i >= 0:
            c = w[:i] + b + w[i + len(a):]
            if c != w and c not in out and c not in FALLEN and ok(c): out.append(c)
            i = w.find(a, i + 1)
    return out
_haken = threading.local()  # .f: wird im rechnenden Thread bei jedem Wörterbuchzugriff der Vorschlagssuche aufgerufen
def _hake():
    f = getattr(_haken, 'f', None)
    if f: f()
class _Nachsehen:
    """Steht in spylls an Stelle des Nachschlagens, das die Vorschlagssuche für jeden Kandidaten aufruft – so kommt der
    Haken alle paar Millisekunden dran, auch mitten in einem Schritt, der Sekunden dauert."""
    def __init__(self, orig): self.orig = orig
    def __call__(self, *a, **k): _hake(); return self.orig(*a, **k)
    def good_forms(self, *a, **k): _hake(); return self.orig.good_forms(*a, **k)
    def __getattr__(self, n): return getattr(self.orig, n)
class _Woerter(list):
    """Die Wortliste, die spylls für die n-Gramm-Vorschläge ganz durchgeht (170 000 Wörter, eine Sekunde): Haken je 1000."""
    def __iter__(self):
        it = list.__iter__(self)
        while True:
            _hake()
            teil = list(itertools.islice(it, 1000))
            if not teil: return
            yield from teil
def _suggester(d):
    sg = checker(d).load().suggester
    if not isinstance(sg.lookup, _Nachsehen):
        sg.lookup, sg.words_for_ngram = _Nachsehen(sg.lookup), _Woerter(sg.words_for_ngram)
    return sg
class _Genug(Exception): pass
def suggest(w, dics=DEFAULT, budget=1.5, limit=5, haken=None, uhr=time.monotonic):
    """Hunspell-Vorschläge zu w. spylls liefert sie nacheinander, die naheliegenden zuerst. Nach dem Budget (Sekunden auf
    der uhr) ist Schluss, sobald es einen gibt – geprüft bei jedem Wörterbuchzugriff, denn ein einzelner Schritt von
    spylls dauert bei langen Zusammensetzungen auch 20 s; ohne jeden Vorschlag wird bis zum Fünffachen gesucht.
    haken: wird dabei jedes Mal aufgerufen (siehe Vorschlaege)."""
    sgs = [_suggester(d) for d in dics if d != 'vor1901'] or [_suggester('1901')]  # das Einlesen zählt nicht zum Budget
    out, t0 = [], uhr()
    def pruefe():
        if haken: haken()
        if uhr() - t0 > (budget if out else 5 * budget): raise _Genug
    _haken.f = pruefe
    try:
        for sg in sgs:
            for s in sg(w):
                s = s.strip('-')  # spylls schlägt auch Zusammensetzungen mit Bindestrich vor (-kolonisten)
                if s and s != w and s not in out and s not in FALLEN: out.append(s)
                if len(out) >= limit or uhr() - t0 > budget: return out
        return out
    except _Genug:
        return out
    finally:
        _haken.f = None
# ---- Hunspell-Vorschläge im Hintergrund (#68). spylls rechnet sekundenlang in reinem Python. Lief das im Thread der
# Anfrage, teilte sich jede andere Anfrage den Interpreter mit ihm und wartete nach jedem Dateizugriff bis zu 5 ms, bis
# sie wieder dran war – das Speichern mit Return brauchte so 3 s statt 0,07 s. Jetzt rechnet ein einziger Thread, und der
# hält an, solange eine andere Anfrage läuft (vorrang). Nebenbei rechnet er die nächsten roten Wörter voraus, die der
# Reader meldet, während der Nutzer noch liest – das Wort, auf dem er steht, geht immer vor.
class _Abbruch(Exception): pass
class Vorschlaege:
    def __init__(self, budget=1.5):
        self.budget, self.cache, self.cond = budget, {}, threading.Condition()
        self.eilig, self.voraus, self.jetzt = None, [], None  # Schlüssel (wort, dics): der Nutzer steht darauf | vorausrechnen | in Arbeit
        self.warten = {}                                      # Schlüssel -> [Event] der Anfragen, die auf ihn warten
        self.vorn, self.frei, self.pause, self.thread, self.tl = 0, threading.Event(), 0.0, None, threading.local()
        self.frei.set()

    @staticmethod
    def key(word, dics):
        return word, tuple(d for d in dics if d != 'vor1901') or ('1901',)

    def hole(self, word, dics, timeout=30):
        """Die Vorschläge für das Wort, auf dem der Nutzer gerade steht – wartet, bis sie gerechnet sind. None, wenn
        inzwischen nach einem anderen Wort gefragt wurde (der Reader will sie dann nicht mehr)."""
        k = self.key(word, dics)
        with self.cond:
            if k in self.cache: return self.cache[k]
            mein = getattr(self.tl, 'n', 0)  # die Anfrage selbst hat Vortritt – den gibt sie ab, solange sie auf den Rechner wartet
            self.vorn -= mein
            if not self.vorn: self.frei.set()
            if self.eilig and self.eilig != k: self._freigeben(self.eilig)  # überholt: nicht warten lassen, der Browser hat nur wenige Verbindungen
            self.eilig, ev = k, threading.Event()
            self.warten.setdefault(k, []).append(ev)
            self._starten()
        ev.wait(timeout)
        with self.cond:
            self.vorn += mein
            if self.vorn: self.frei.clear()
            if ev in self.warten.get(k, []): self.warten[k].remove(ev)
            return self.cache.get(k)

    def vorausrechnen(self, words, dics):
        """Die nächsten roten Wörter der Reihe nach vorab rechnen; ersetzt die bisherige Liste."""
        with self.cond:
            self.voraus = [k for k in dict.fromkeys(self.key(w, dics) for w in words) if k not in self.cache]
            if self.voraus: self._starten()

    def vorrang(self):
        """Solange eine Anfrage darin läuft, rechnet der Hintergrund nicht (with vorschlaege.vorrang(): …)."""
        return _Vorrang(self)

    def _freigeben(self, k):
        for ev in self.warten.pop(k, []): ev.set()

    def _starten(self):
        if not self.thread:
            self.thread = threading.Thread(target=self._lauf, daemon=True, name='vorschlaege')
            self.thread.start()
        self.cond.notify()

    def _haken(self):
        """Im Rechen-Thread bei jedem Wörterbuchzugriff: warten, solange eine Anfrage läuft (die Pause zählt nicht zum
        Budget); aufhören, wenn die Arbeit überholt ist – der Nutzer ist weitergegangen oder steht jetzt auf einem Wort."""
        if self.vorn:
            t0 = time.monotonic()
            while self.vorn: self.frei.wait(0.1)
            self.pause += time.monotonic() - t0
        k = self.jetzt
        if k != self.eilig and (self.eilig or k not in self.voraus): raise _Abbruch

    def _lauf(self):
        while True:
            with self.cond:
                while not (self.eilig or self.voraus): self.cond.wait()
                k = self.jetzt = self.eilig or self.voraus[0]
            self.pause = 0.0
            try:
                r = suggest(k[0], k[1], budget=self.budget, haken=self._haken, uhr=lambda: time.monotonic() - self.pause)
                save_cache()  # was die Suche nebenbei nachgeschlagen hat
            except _Abbruch:
                r = None
            except Exception:  # ein Fehler in spylls darf den Thread nicht beenden: ohne Vorschläge weiter
                r = []
            with self.cond:
                self.jetzt = None
                if r is not None:
                    self.cache[k] = r
                    self._freigeben(k)
                    if k in self.voraus: self.voraus.remove(k)
                if self.eilig == k: self.eilig = None
class _Vorrang:
    def __init__(self, v): self.v = v
    def __enter__(self):
        with self.v.cond:
            self.v.vorn += 1; self.v.frei.clear()
            self.v.tl.n = getattr(self.v.tl, 'n', 0) + 1  # je Thread: wie oft er gerade Vortritt hat
    def __exit__(self, *a):
        with self.v.cond:
            self.v.vorn -= 1; self.v.tl.n -= 1
            if not self.v.vorn: self.v.frei.set()
VORSCHLAEGE = Vorschlaege()
def dics_for_year(year):
    """Vorschlag nach dem Erscheinungsjahr. Ab 1998 beide Rechtschreibungen: Die Umstellung zog sich hin, und neuere
    Arbeiten zitieren ältere Texte."""
    if not year: return list(DEFAULT)
    return ['1901', 'vor1901'] if year < 1902 else ['1901'] if year < 1998 else ['1901', 'neu']
YEAR = re.compile(r'(?<![\d.,/-])(1[5-9]\d\d|20[0-2]\d)(?![\d,/-]|\.\d)')
def guess_year(pages, now=2100):
    """Erscheinungsjahr raten: die späteste Jahreszahl auf den ersten und letzten Seiten (Titelei, Impressum) – eine
    Arbeit von 2002 nennt 1817, ein Buch von 1928 aber nicht 2002. Bevorzugt, was hinter © oder 'Copyright' steht."""
    keys = sorted(pages)
    text = '\n'.join('\n'.join(pages[k]) for k in keys[:8] + keys[-3:])
    m = re.search(r'(?:©|\(c\)|Copyright)\D{0,40}?(1[5-9]\d\d|20[0-2]\d)', text, re.I)
    if m: return int(m.group(1))
    ys = [int(y) for y in YEAR.findall(text) if int(y) <= now]
    return max(ys) if ys else None
def page_lines(t):
    """Der Inhalt einer Seitendatei als Zeilen: Die Datei endet normalerweise mit einem Zeilenumbruch (so schreibt das
    Programm sie), doch ein Editor lässt ihn manchmal weg – die letzte Zeile darf dabei nicht verloren gehen."""
    t = t.replace('\r\n', '\n')
    if t.endswith('\n'): t = t[:-1]
    return t.split('\n')
def read_page(path):
    return page_lines(open(path, encoding='utf-8').read())
def read_pages(folder):
    """{ 'NNN': [zeilen] } aus NNN.txt"""
    return {os.path.basename(f)[:3]: read_page(f) for f in sorted(glob.glob(os.path.join(folder, '[0-9][0-9][0-9].txt')))}
# ---- Gedruckte Seitenzahl: in der Kopfzeile (# 23) oder unten auf der Seite – so in neueren Büchern, in älteren oft auf
# Kapitelanfängen. Unten ist es eine kurze Zeile unter den letzten drei, die fast nur aus einer Zahl besteht; Rauschen vom
# Seitenrand darf danebenstehen (»i 20«, »44ä«, »— 137 —«), eine Bogensignatur (»4 *«) ist keine Seitenzahl.
NUM = re.compile(r'\d+')
def head_number(lines):
    """(zahl, zeile, position, länge) aus der Kopfzeile oder None."""
    m = NUM.search(lines[0]) if lines and lines[0].startswith('#') else None
    return (int(m.group()), 0, m.start(), len(m.group())) if m else None
def foot_number(lines):
    """(zahl, zeile, position, länge) einer Zahl am Seitenende oder None. Von zwei Zahlen gilt die hintere (»8 | 4«)."""
    top, seen = (1 if lines and lines[0].startswith('#') else 0), 0
    for i in range(len(lines) - 1, top - 1, -1):
        s = lines[i].strip()
        if not s or s == '---':
            continue
        seen += 1
        if seen > 3:
            return None
        ms = list(NUM.finditer(lines[i]))
        if len(s) <= 8 and 1 <= len(ms) <= 2 and max(len(m.group()) for m in ms) <= 4 and '*' not in s and '<' not in s \
                and sum(c.isalpha() for c in s) <= 1:
            m = ms[-1]
            return int(m.group()), i, m.start(), len(m.group())
    return None
def head_lines(pages):
    """{seite: (seitenzahl oder None, [zeilen])}: der lebende Kolumnentitel, den die Erkennung als gewöhnliche Zeile oben
    auf der Seite gelesen hat – »Stalins Bauernopfer am Schwarzen Meer 9«, auch als zwei Zeilen Titel und Zahl, oder links
    der Buchtitel, rechts der Kapiteltitel. Erkannt am Wortlaut ohne Ziffern: Er steht in einer der beiden obersten
    Textzeilen von mindestens drei Seiten – aber nur, wenn das Buch wirklich Kolumnentitel trägt: Mindestens ein Drittel
    der Seiten hat einen, und ihre Seitenzahlen passen zu den Nachbarseiten. Sonst ist es Zufall (»Faust.« als erste
    Zeile einiger Seiten eines Dramas). Eine Zahl vorn oder hinten – oder als eigene Zeile daneben – ist die Seitenzahl:
    (zahl, zeile, position, länge). Kolumnentitel ohne Zahl (sie steht dann unten) bleiben Text."""
    key = lambda l: ' '.join(re.sub(r'[\d\W_]+', ' ', TAG.sub('', l)).lower().split())
    tops = {}
    for pg, lines in pages.items():
        start, end = (1 if lines and lines[0].startswith('#') else 0), (lines.index('---') if '---' in lines else len(lines))
        text = [i for i in range(start, end) if lines[i].strip()]
        tops[pg] = text[:3] if len(text) >= 4 else []  # fast leere Seite: oben und unten nicht zu unterscheiden
    count = collections.Counter(k for pg, c in tops.items() for k in {key(pages[pg][i]) for i in c[:2]
                                                                     if len(pages[pg][i]) <= 80} if len(k) >= 4)
    out = {}
    for pg, c in tops.items():
        lines = pages[pg]
        hit = next((i for i in c[:2] if len(lines[i]) <= 80 and len(key(lines[i])) >= 4 and count[key(lines[i])] >= 3), None)
        if hit is None:
            continue
        idx = [hit] + [j for j in (hit - 1, hit + 1) if j in c and len(lines[j].strip()) <= 8 and NUM.search(lines[j])
                                                        and re.fullmatch(r'[\s\d—\-–.|]+', lines[j])]
        num = None
        for j in sorted(idx):
            m = re.match(r'\s*[—\-–]?\s*(\d{1,4})\b', lines[j]) or re.search(r'\b(\d{1,4})\s*[—\-–]?\s*$', lines[j])
            if m:
                num = (int(m.group(1)), j, m.start(1), len(m.group(1)))
                break
        out[pg] = (num, sorted(idx))
    # Wie bei der Seitenzahl unten: Nur ein Buch, dessen Kolumnentitel wirklich Seitenzahlen tragen, die zu den
    # Nachbarseiten passen – sonst ist es eine Textzeile, die sich wiederholt (Tabellenköpfe, gleichlautende Anfänge)
    keys = sorted(pages)
    nums = {pg: v[0][0] for pg, v in out.items() if v[0]}
    ok = sum(1 for k, pg in enumerate(keys) if pg in nums and
             any(0 <= k + d < len(keys) and nums.get(keys[k + d]) == nums[pg] + d for d in (-2, -1, 1, 2)))
    return out if len(out) * 3 >= len(pages) and ok >= 3 and ok * 3 >= len(out) else {}
def foot_numbers(pages, heads=None):
    """{seite: foot_number} für die Seiten ohne Zahl in der Kopfzeile – aber nur, wenn das Buch seine Seitenzahlen wirklich
    unten trägt: Mindestens ein Drittel dieser Seiten (und wenigstens drei) hat unten eine Zahl, die zu einer Nachbarseite
    passt. Sonst sind es Jahreszahlen, Fußnotennummern oder Rauschen, und eine Notiz nennte »S. 1985«. heads: die
    Kolumnentitel (head_lines) – deren Seitenzahl zählt wie eine in der Kopfzeile."""
    keys, feet, num = sorted(pages), {}, {}
    for pg in keys:
        h = head_number(pages[pg]) or ((heads or {}).get(pg) or (None,))[0]
        f = None if h else foot_number(pages[pg])
        if f:
            feet[pg] = f
        num[pg] = (h or f or (None,))[0]
    ok = sum(1 for k, pg in enumerate(keys) if pg in feet and
             any(0 <= k + d < len(keys) and num[keys[k + d]] == feet[pg][0] + d for d in (-2, -1, 1, 2)))
    without = sum(1 for pg in keys if num[pg] is None or pg in feet)
    return feet if ok >= 3 and ok * 3 >= without else {}
# ---- Auszeichnung im Text: dieselben Elemente wie im EPUB (XHTML), nichts Eigenes. Die Zeilenzahl einer Seite bleibt dabei
# gleich (sonst ginge die Bildzuordnung verloren): Jede Zeile bleibt eine Zeile, eine Tabellenzelle ist eine Zeile.
MARKUP = 'table|tr|td|th|h[1-6]|em|strong|i|b|sup|sub|p|blockquote|br'
TAG = re.compile(r'</?(?:%s)\s*/?>' % MARKUP)
TABLETAG = re.compile(r'</?(?:table|tr|td|th)>')
HEADTAG = re.compile(r'</?h[1-6]>')
def mask(l):
    """Auszeichnung durch Leerzeichen ersetzen – die Zeichenpositionen bleiben, die Wortprüfung sieht kein 'td'."""
    return TAG.sub(lambda m: ' ' * len(m.group()), l)
def make_table(lines, cols, head=False):
    """Aus aufeinanderfolgenden Zeilen eine Tabelle: Die Zeilen füllen die Zellen der Reihe nach, von links nach rechts.
    Leere Zeilen bleiben leer. head: die erste Reihe sind Spaltenköpfe (<th>). Liefert die neuen Zeilen (gleich viele)."""
    cols = max(1, int(cols))
    out = [TABLETAG.sub('', l) for l in lines]
    cells = [i for i, l in enumerate(out) if l.strip()]
    for k, i in enumerate(cells):
        c, last, tag = k % cols, k == len(cells) - 1, 'th' if head and k < cols else 'td'
        pre = ('<table>' if k == 0 else '') + ('<tr>' if c == 0 else '') + '<%s>' % tag
        post = '</%s>' % tag
        if last:
            post += '<td></td>' * (cols - 1 - c) + '</tr></table>'  # unvollständige letzte Reihe auffüllen
        elif c == cols - 1:
            post += '</tr>'
        out[i] = pre + out[i] + post
    return out
def table_block(lines, i):
    """(erste, letzte Zeile) der Tabelle, in der Zeile i liegt, sonst None."""
    a = next((k for k in range(i, -1, -1) if '<table>' in lines[k]), None)
    if a is None or any('</table>' in lines[k] for k in range(a, i)):
        return None
    b = next((k for k in range(a, len(lines)) if '</table>' in lines[k]), None)
    return (a, b) if b is not None and b >= i else None
def table_shape(lines):
    """(spalten, kopfzeile) einer ausgezeichneten Tabelle: Zellen bis zum ersten </tr>."""
    first = ''.join(lines).split('</tr>')[0]
    return max(1, len(re.findall(r'<t[dh]>', first))), '<th>' in first
def heading(line, level):
    """Zeile als Überschrift der Ebene 1–6 auszeichnen; level 0 nimmt die Auszeichnung weg."""
    t = HEADTAG.sub('', line)
    return '<h%d>%s</h%d>' % (level, t, level) if level and t.strip() else t
HLINE = re.compile(r'<h([1-6])>(.*)</h\1>$')
def headings(pages):
    """Die Überschriften in Lesereihenfolge: [(seite, zeile, ebene, text)] – für die Übersicht im Reader und das
    Inhaltsverzeichnis. Zeilen derselben Ebene unmittelbar untereinander (»Drittes Kapitel.« / »Die Reise nach Odessa.«)
    sind eine Überschrift; eine Trennung ¬ am Zeilenende wird zusammengezogen, Schrift-Auszeichnung fällt weg."""
    out = []
    for pg in sorted(pages):
        prev = None  # (ebene, zeile) der letzten Überschriftszeile dieser Seite
        for i, l in enumerate(pages[pg]):
            m = HLINE.match(l.strip())
            text = ' '.join(TAG.sub('', m.group(2)).split()) if m else ''
            if not text:
                prev = None
                continue
            level = int(m.group(1))
            if prev == (level, i - 1):
                p = out[-1]
                out[-1] = (p[0], p[1], level, p[3][:-1] + text if p[3].endswith('¬') else p[3] + ' ' + text)
            else:
                out.append((pg, i, level, text))
            prev = (level, i)
    return out
def corpus_freq(pages):
    c = collections.Counter()
    for lines in pages.values():
        for l in lines: c.update(WORD.findall(mask(l)))
    return c
def joined_tokens(lines):
    """Liefert je Zeile Liste (start, wort) und behandelt '¬'-Trennung: das getrennte Wort wird
    als (zeile_i, start_i, teil1, zeile_j, teil2) zusätzlich in joined zurückgegeben."""
    lines = [mask(l) for l in lines]
    toks = [[(m.start(), m.group()) for m in WORD.finditer(l)] for l in lines]
    joined = []
    for i, l in enumerate(lines):
        if l.rstrip().endswith('¬') and i + 1 < len(lines) and toks[i] and toks[i+1]:
            s1, w1 = toks[i][-1]; s2, w2 = toks[i+1][0]
            if s1 + len(w1) == len(l.rstrip()) - 1 and not lines[i + 1][:s2].strip():  # vor dem zweiten Teil steht höchstens Auszeichnung
                joined.append((i, s1, w1, i + 1, w2))
    return toks, joined
def known(w, freq, minfreq=3):
    return in_dict(w) or freq.get(w, 0) >= minfreq
