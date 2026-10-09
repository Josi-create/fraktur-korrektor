"""Bildschirmfotos für Hilfe und README neu aufnehmen – aus dem gemeinfreien Beispielbuch, in einer eigenen Instanz.

    python scripts/screenshots.py                    # alle Szenen, deutsch und englisch, nach docs/<sprache>/img/
    python scripts/screenshots.py korrektur lesen    # nur diese Szenen
    python scripts/screenshots.py --sprache en       # nur englisch
    python scripts/screenshots.py --laufwerk S:      # Windows: Arbeitsordner als Laufwerk S: – kurze Pfade im Bild

Je Sprache ein frischer Arbeitsordner mit eigenem FRAKTUR_HOME und eigenem Server auf einem freien Port: echte Bücher
und Einstellungen bleiben unberührt. Das Beispielbuch kommt über den Knopf der Bibliothek hinein, wie beim Nutzer.
Die Texterkennung (Szene »ampel«) braucht Tesseract.

Braucht Google Chrome, Chromium oder Edge (sonst CHROME=<pfad>) und Pillow (Bilder verkleinern, GIF). Chrome wird
über das DevTools-Protokoll gesteuert – der Websocket ist von Hand geschrieben, damit nichts nachzuinstallieren ist.
"""
import argparse, base64, io, json, os, shutil, socket, struct, subprocess, sys, tempfile, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGS = ('de', 'en')


def chrome_exe():
    cands = [os.environ.get('CHROME', '')]
    for base in (os.environ.get('PROGRAMFILES', ''), os.environ.get('PROGRAMFILES(X86)', ''), os.environ.get('LOCALAPPDATA', '')):
        cands += [os.path.join(base, 'Google', 'Chrome', 'Application', 'chrome.exe'),
                  os.path.join(base, 'Microsoft', 'Edge', 'Application', 'msedge.exe')]
    cands += ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Chromium.app/Contents/MacOS/Chromium']
    cands += [shutil.which(n) or '' for n in ('google-chrome', 'chromium', 'chromium-browser', 'chrome')]
    exe = next((c for c in cands if c and os.path.isfile(c)), None)
    if not exe:
        sys.exit('Chrome nicht gefunden – CHROME=<pfad zu chrome> setzen.')
    return exe


class Browser:
    """Ein Chrome ohne Fenster, eine Seite, gesteuert über das DevTools-Protokoll."""

    def __init__(self, lang):
        self.prof = tempfile.mkdtemp(prefix='fk-chrome-')  # je Lauf ein frisches Profil: localStorage (Sprache) leer
        self.proc = subprocess.Popen([chrome_exe(), '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run',
                                      '--no-default-browser-check', '--remote-debugging-port=0', '--user-data-dir=' + self.prof,
                                      '--lang=' + lang, 'about:blank'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        portfile, deadline = os.path.join(self.prof, 'DevToolsActivePort'), time.time() + 30
        while not (os.path.isfile(portfile) and open(portfile).read().strip()):
            if time.time() > deadline:
                raise RuntimeError('Chrome startet nicht')
            time.sleep(0.1)
        port = int(open(portfile).read().split()[0])
        pages = json.load(urllib.request.urlopen('http://127.0.0.1:%d/json/list' % port))
        u = urllib.parse.urlparse(next(p for p in pages if p['type'] == 'page')['webSocketDebuggerUrl'])
        self.sock = socket.create_connection((u.hostname, u.port), timeout=180)
        key = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall(('GET %s HTTP/1.1\r\nHost: %s:%d\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n'
                           'Sec-WebSocket-Key: %s\r\nSec-WebSocket-Version: 13\r\n\r\n' % (u.path, u.hostname, u.port, key)).encode())
        head = b''
        while not head.endswith(b'\r\n\r\n'):
            head += self.sock.recv(1)
        if b' 101 ' not in head.split(b'\r\n')[0]:
            raise RuntimeError('DevTools: ' + head.decode('latin-1'))
        self.n = 0
        self.call('Page.enable')

    def _send(self, text):
        data, mask = text.encode('utf-8'), os.urandom(4)
        n = len(data)
        head = bytes([0x81]) + (bytes([0x80 | n]) if n < 126 else bytes([0x80 | 126]) + struct.pack('>H', n) if n < 65536
                                else bytes([0x80 | 127]) + struct.pack('>Q', n))
        self.sock.sendall(head + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))

    def _read(self, n):
        buf = b''
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                raise RuntimeError('DevTools-Verbindung beendet')
            buf += chunk
        return buf

    def _recv(self):
        msg = b''
        while True:
            b0, b1 = self._read(2)
            n = b1 & 0x7f
            if n == 126:
                n = struct.unpack('>H', self._read(2))[0]
            elif n == 127:
                n = struct.unpack('>Q', self._read(8))[0]
            data, op = self._read(n), b0 & 0x0f
            if op in (0, 1, 2):
                msg += data
                if b0 & 0x80:
                    return json.loads(msg)

    def call(self, method, **params):
        self.n += 1
        self._send(json.dumps(dict(id=self.n, method=method, params=params)))
        while True:
            m = self._recv()
            if m.get('id') == self.n:
                if 'error' in m:
                    raise RuntimeError('%s: %s' % (method, m['error']))
                return m.get('result', {})
            # Ein alert() blockiert die Seite – dann stimmt die Szene nicht (etwa »keine roten Wörter mehr«)
            if m.get('method') == 'Page.javascriptDialogOpening':
                raise RuntimeError('Meldung im Browser: ' + m['params']['message'])

    def js(self, expr):
        r = self.call('Runtime.evaluate', expression=expr, awaitPromise=True, returnByValue=True)
        if 'exceptionDetails' in r:
            raise RuntimeError('JavaScript: %s' % r['exceptionDetails'])
        return r['result'].get('value')

    def size(self, w, h, touch=False):
        self.call('Emulation.setDeviceMetricsOverride', width=w, height=h, deviceScaleFactor=1, mobile=touch)
        self.call('Emulation.setTouchEmulationEnabled', enabled=touch, maxTouchPoints=5 if touch else 1)

    def wait(self, cond, timeout=60):
        """Warten, bis der Ausdruck wahr ist, die Bilder geladen sind und die Seite still steht."""
        deadline = time.time() + timeout
        while not self.js('!!(%s) && [...document.images].every(i => i.complete)' % cond):
            if time.time() > deadline:
                with open(os.path.join(tempfile.gettempdir(), 'fk-screenshot-fehler.png'), 'wb') as f:
                    f.write(self.png())  # so stand es, als das Warten aufgab
                raise RuntimeError('Zeitüberschreitung beim Warten auf: %s – Bild: %s' % (cond, f.name))
            time.sleep(0.25)
        time.sleep(0.6)

    def go(self, url, cond='document.readyState == "complete"', timeout=60):
        self.call('Page.navigate', url='about:blank')  # sonst lädt eine Adresse, die sich nur nach dem # unterscheidet, nicht neu
        self.call('Page.navigate', url=url)
        time.sleep(0.3)
        self.wait(cond, timeout)

    def keys(self, *keys):
        """Tasten wie im Selbsttest des Readers (?keys=…): als keydown an das Element mit dem Fokus."""
        for k in keys:
            mod = dict(shiftKey=True) if k.startswith('Shift+') else {}
            k = k.split('+')[-1] if mod else k
            self.js('(document.activeElement || document).dispatchEvent(new KeyboardEvent("keydown", %s))'
                    % json.dumps(dict(key=' ' if k == 'Space' else k, bubbles=True, **mod)))
            time.sleep(0.45)

    def type(self, text, frames=None):
        """Buchstaben einzeln eintippen wie ein Mensch; mit frames= nach jedem ein Bild fürs GIF."""
        for ch in text:
            self.call('Input.insertText', text=ch)
            time.sleep(0.08)
            if frames is not None:
                frames.append((self.png(), 120))

    def png(self):
        return base64.b64decode(self.call('Page.captureScreenshot', format='png')['data'])

    def close(self):
        try:
            self.sock.close()
        finally:
            self.proc.kill()
            self.proc.wait()
            shutil.rmtree(self.prof, ignore_errors=True)


def save(png, path):
    """PNG mit höchstens 256 Farben: Seitenbilder und Oberfläche vertragen das, die Dateien werden ein Drittel so groß."""
    from PIL import Image
    im = Image.open(io.BytesIO(png)).convert('RGB').quantize(256, method=Image.Quantize.MEDIANCUT)
    im.save(path, optimize=True)
    print('  ', os.path.relpath(path, ROOT), '%d KB' % (os.path.getsize(path) // 1024))


def save_gif(frames, path, width=960):
    """frames: [(png, Dauer in ms)]. Eine gemeinsame Palette für alle Bilder – sonst flackert der Hintergrund."""
    from PIL import Image
    ims = [Image.open(io.BytesIO(p)).convert('RGB') for p, _ in frames]
    ims = [im.resize((width, round(im.height * width / im.width)), Image.LANCZOS) for im in ims]
    pal = ims[len(ims) // 2].quantize(255, method=Image.Quantize.MEDIANCUT)
    ims = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in ims]
    ims[0].save(path, save_all=True, append_images=ims[1:], duration=[d for _, d in frames], loop=0, optimize=True)
    print('  ', os.path.relpath(path, ROOT), '%d KB' % (os.path.getsize(path) // 1024))


class Instance:
    """Ein eigener Server mit eigener Bibliothek im Arbeitsordner."""

    def __init__(self, work):
        self.work, home = work, os.path.join(work, 'Einstellungen')
        self.books = os.path.join(work, 'Fraktur-Korrektor')
        os.makedirs(home)
        with open(os.path.join(home, 'config.json'), 'w', encoding='utf-8') as f:
            json.dump(dict(buecher=os.path.normpath(self.books)), f)
        with socket.socket() as s:
            s.bind(('127.0.0.1', 0))
            self.port = s.getsockname()[1]
        self.base = 'http://127.0.0.1:%d' % self.port
        self.proc = subprocess.Popen([sys.executable, os.path.join(ROOT, 'server.py'), '--port', str(self.port), '--no-browser'],
                                     env=dict(os.environ, FRAKTUR_HOME=home, PYTHONIOENCODING='utf-8'),
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.time() + 60
        while True:
            try:
                urllib.request.urlopen(self.base + '/api/library', timeout=5)
                break
            except OSError:
                if time.time() > deadline or self.proc.poll() is not None:
                    raise RuntimeError('Server startet nicht')
                time.sleep(0.2)

    def close(self):
        self.proc.kill()
        self.proc.wait()


def post(inst, path, **body):
    return json.load(urllib.request.urlopen(urllib.request.Request(inst.base + path, json.dumps(body).encode())))


def make_pdf(path):
    """Ein PDF nur aus Seitenbildern, wie aus einem Scanner: die ersten fünf Seiten des Beispielbuchs."""
    import fitz
    doc = fitz.open()
    for n in range(1, 6):
        img = os.path.join(ROOT, 'beispiel', 'img', '%03d.jpg' % n)
        w, h = fitz.Pixmap(img).width, fitz.Pixmap(img).height
        page = doc.new_page(width=w * 72 / 300, height=h * 72 / 300)
        page.insert_image(page.rect, filename=img)
    doc.save(path)


# ---- Die Szenen, in dieser Reihenfolge: Jede baut auf dem Stand der vorigen auf (leere Bibliothek → Beispielbuch → PDF).
# Jede bekommt (Browser, Instanz, Sprache, Zielordner, Ergebnisse) und legt ihre Bilder selbst ab.

def s_bibliothek_start(b, inst, lang, out, st):
    b.size(1200, 700)
    b.go(inst.base + '/bibliothek', 'document.querySelector("#empty .example")')
    save(b.png(), os.path.join(out, 'bibliothek-start.png'))


def s_beispiel(b, inst, lang, out, st):
    """Kein Bild: das Beispielbuch über den Knopf anlegen, wie es der Nutzer tut."""
    if 'book' in st:
        return
    b.go(inst.base + '/bibliothek', 'document.querySelector("#foot .example")')
    b.js('document.querySelector("#foot .example").click()')
    b.wait('location.pathname.startsWith("/buch/") && document.querySelector("#lines .flag")')
    st['book'] = b.js('location.pathname')


def reader(b, inst, st, page, *keys, cond='document.querySelector("#lines .flag")'):
    b.size(1440, 860)
    b.go(inst.base + st['book'] + '?notrans&seite=' + page, cond)
    b.keys(*keys)
    time.sleep(0.5)


def s_lesen(b, inst, lang, out, st):
    # »Habe nun, ach! Philosophie« als Lesezeile: Bild und Text stehen auf gleicher Höhe
    reader(b, inst, st, '002', *['ArrowDown'] * 5)
    save(b.png(), os.path.join(out, 'lesen.png'))


def s_korrektur(b, inst, lang, out, st):
    # Erstes rotes Wort der Seite 3: »Ehr'« – im Bild rot umrahmt, darunter die Vorschläge des Wörterbuchs
    reader(b, inst, st, '003', 'Space')
    b.wait('document.querySelector("#sugbox") && document.querySelector("#sugbox").offsetParent && document.querySelector("#sugbox").children.length')
    save(b.png(), os.path.join(out, 'korrektur.png'))


def s_korrigieren_gif(b, inst, lang, out, st):
    """Kurzfilm für die README: ein Fehler der Texterkennung wird berichtigt, ein altes Wort bestätigt."""
    work = os.path.join(inst.books, 'gif-' + lang)  # eine eigene Kopie: die Korrekturen sollen in keinem anderen Bild stehen
    shutil.copytree(os.path.join(ROOT, 'beispiel'), work)
    bid = post(inst, '/api/open', folder=work)['id']
    b.size(1440, 860)
    b.go(inst.base + '/buch/%s?notrans&seite=002' % bid, 'document.querySelector("#lines .flag")')
    frames = [(b.png(), 1600)]
    b.keys('Space')                      # zum ersten roten Wort: »Ge« statt »gothischen«
    frames.append((b.png(), 1800))
    b.type('gothischen', frames)
    frames[-1] = (frames[-1][0], 1200)
    b.keys('Enter')                      # übernommen; weiter zum nächsten roten Wort: »Bemühn« ist richtig
    frames.append((b.png(), 2000))
    b.keys('F8')                         # also merken, weiter
    frames.append((b.png(), 2600))
    save_gif(frames, os.path.join(out, 'korrigieren.gif'))
    post(inst, '/api/forget', id=bid)  # die Übungskopie gehört nicht in das Bild der Bibliothek


def s_oeffnen_pdf(b, inst, lang, out, st):
    pdf = os.path.join(inst.work, 'Faust 1862.pdf')
    if not os.path.exists(pdf):
        make_pdf(pdf)
    st['pdf'] = pdf
    b.size(1200, 800)
    b.go(inst.base + '/bibliothek#open=' + urllib.parse.quote(pdf), 'document.querySelector("#dlg.on") && document.querySelector("#target").textContent')
    save(b.png(), os.path.join(out, 'oeffnen-pdf.png'))


def s_ampel(b, inst, lang, out, st):
    if 'pdf' not in st:
        st['pdf'] = os.path.join(inst.work, 'Faust 1862.pdf')
        make_pdf(st['pdf'])
    b.size(1200, 800)
    b.go(inst.base + '/bibliothek#auto=' + urllib.parse.quote(st['pdf']), 'document.querySelector(".verdict .amp")', timeout=300)
    save(b.png(), os.path.join(out, 'ampel.png'))


def s_bibliothek(b, inst, lang, out, st):
    b.size(1200, 640)
    b.go(inst.base + '/bibliothek', 'document.querySelectorAll(".book").length')
    save(b.png(), os.path.join(out, 'bibliothek.png'))


SCENES = [('bibliothek-start', s_bibliothek_start), ('beispiel', s_beispiel), ('lesen', s_lesen), ('korrektur', s_korrektur),
          ('korrigieren', s_korrigieren_gif), ('oeffnen-pdf', s_oeffnen_pdf), ('ampel', s_ampel), ('bibliothek', s_bibliothek)]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('szenen', nargs='*', help='Namen der Szenen (ohne Angabe: alle): ' + ', '.join(n for n, _ in SCENES if n != 'beispiel'))
    ap.add_argument('--sprache', choices=LANGS, action='append')
    ap.add_argument('--laufwerk', help='Windows: Arbeitsordner per subst als dieses Laufwerk (z. B. S:), damit Pfade im Bild kurz sind')
    a = ap.parse_args()
    want = set(a.szenen) or {n for n, _ in SCENES}
    unknown = want - {n for n, _ in SCENES}
    if unknown:
        sys.exit('Unbekannte Szene: ' + ', '.join(sorted(unknown)))
    if want & {'lesen', 'korrektur'}:
        want.add('beispiel')
    for lang in a.sprache or LANGS:
        tmp = tempfile.mkdtemp(prefix='fk-shots-')
        work = tmp
        if a.laufwerk:
            subprocess.run(['subst', a.laufwerk, tmp], check=True)
            work = a.laufwerk + os.sep
        inst = b = None
        try:
            inst, b = Instance(work), Browser(lang)
            out = os.path.join(ROOT, 'docs', lang, 'img')
            os.makedirs(out, exist_ok=True)
            print(lang)
            st = {}
            for name, fn in SCENES:
                if name in want:
                    fn(b, inst, lang, out, st)
        finally:
            if b:
                b.close()
            if inst:
                inst.close()
            if a.laufwerk:
                subprocess.run(['subst', a.laufwerk, '/D'])
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
