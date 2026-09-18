"""Testumgebung: ein Wegwerf-Buch im Temp-Ordner und ein eigener Server auf einem freien Port.
Berührt weder echte Buchordner noch ~/.fraktur-korrektor (FRAKTUR_HOME zeigt in den Temp-Ordner)."""
import os, sys, json, zlib, struct, socket, subprocess, tempfile, time, urllib.request, urllib.error
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_home = tempfile.mkdtemp(prefix='fraktur-home-')
os.environ['FRAKTUR_HOME'] = _home  # vor dem Import von korrlib
os.environ.pop('FRAKTUR_DIC', None)

PAGES = {
    '001': ['# 5',
            'Die Kolonisten zogen nach Rußland und',
            'ber Weg war weit. Die Zu¬',
            'kunft lag vor ihnen, baß sie',
            'ber Heimat gedachten.',
            '---',
            '1) Vgl. die Quellen.'],
    '002': ['# 6',
            'Der Vater und ber Sohn.'],
}


def png(w, h):
    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d))
    raw = b''.join(b'\0' + b'\xff' * w for _ in range(h))
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 0, 0, 0, 0)) + \
        chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b'')


def make_book(folder):
    os.makedirs(os.path.join(folder, 'img'))
    geo = {}
    for pg, lines in PAGES.items():
        with open(os.path.join(folder, pg + '.txt'), 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(lines) + '\n')
        gl, y, kind = [], 100, 'body'
        for n, l in enumerate(lines):
            if l == '---':
                kind = 'fn'
                continue
            gl.append(dict(text=l[2:] if n == 0 else l, x0=100, x1=900, y0=y, y1=y + 40, kind='head' if n == 0 else kind))
            y += 60
        geo[pg] = dict(w=1000, h=1500, lines=gl)
        with open(os.path.join(folder, 'img', pg + '.png'), 'wb') as f:
            f.write(png(500, 750))  # halbe Transkribus-Größe -> Maßstab 0.5
    with open(os.path.join(folder, 'lines.json'), 'w', encoding='utf-8') as f:
        json.dump(geo, f, ensure_ascii=False)


class Client:
    """get/post sprechen das Buch an (/buch/<id>/api/…), lget/lpost die Bibliothek (/api/…)."""

    def __init__(self, port, folder):
        self.base, self.folder, self.book = 'http://127.0.0.1:%d' % port, folder, ''

    def _req(self, path, body=None, timeout=30):
        data = None if body is None else json.dumps(body).encode('utf-8')
        try:
            with urllib.request.urlopen(urllib.request.Request(self.base + path, data=data), timeout=timeout) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()

    def get(self, path):
        return self.lget(self.book + path)

    def post(self, path, body):
        return self.lpost(self.book + path, body)

    def lget(self, path, timeout=30):
        code, b = self._req(path, timeout=timeout)
        return code, json.loads(b)

    def lpost(self, path, body):
        code, b = self._req(path, body)
        return code, json.loads(b)

    def raw(self, path):
        return self._req(path)

    def text(self, pg):
        return open(os.path.join(self.folder, pg + '.txt'), encoding='utf-8').read().split('\n')[:-1]

    def log(self):
        p = os.path.join(self.folder, 'korrekturen.log')
        return [l.rstrip('\n').split('\t') for l in open(p, encoding='utf-8')] if os.path.exists(p) else []


def start(tmp_path, folder=None):
    """Startet einen Server auf freiem Port; mit folder wie bisher von der Kommandozeile, sonst mit leerer Bibliothek."""
    with socket.socket() as so:
        so.bind(('127.0.0.1', 0))
        port = so.getsockname()[1]
    home = str(tmp_path / 'home')  # eigene Bibliothek je Test
    env = dict(os.environ, PYTHONIOENCODING='utf-8', FRAKTUR_HOME=home)
    p = subprocess.Popen([sys.executable, os.path.join(ROOT, 'server.py')] + ([folder] if folder else []) + ['--port', str(port), '--no-browser'],
                         env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    c = Client(port, folder)
    deadline = time.time() + 120
    while True:
        if p.poll() is not None:
            raise RuntimeError('Server beendet: ' + p.stdout.read().decode('utf-8', 'replace'))
        try:
            books = c.lget('/api/library', timeout=5)[1]['books']
            break
        except OSError as e:
            if time.time() > deadline:
                p.kill()
                raise RuntimeError('Server antwortet nicht (%r): %s' % (e, p.stdout.read().decode('utf-8', 'replace')))
            time.sleep(0.1)
    if folder:
        c.book = '/buch/' + books[0]['id']
    return p, c


@pytest.fixture
def app(tmp_path):
    folder = str(tmp_path / 'buch')
    make_book(folder)
    p, c = start(tmp_path, folder)
    try:
        yield c
    finally:
        p.kill()
        p.wait()


@pytest.fixture
def lib(tmp_path):
    """Server ohne Buchordner: Bibliothek."""
    p, c = start(tmp_path)
    try:
        yield c
    finally:
        p.kill()
        p.wait()
