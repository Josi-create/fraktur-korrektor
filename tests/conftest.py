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
    def __init__(self, port, folder):
        self.base, self.folder = 'http://127.0.0.1:%d' % port, folder

    def _req(self, path, body=None):
        data = None if body is None else json.dumps(body).encode('utf-8')
        try:
            with urllib.request.urlopen(urllib.request.Request(self.base + path, data=data), timeout=30) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()

    def get(self, path):
        code, b = self._req(path)
        return code, json.loads(b)

    def post(self, path, body):
        code, b = self._req(path, body)
        return code, json.loads(b)

    def raw(self, path):
        return self._req(path)

    def text(self, pg):
        return open(os.path.join(self.folder, pg + '.txt'), encoding='utf-8').read().split('\n')[:-1]

    def log(self):
        p = os.path.join(self.folder, 'korrekturen.log')
        return [l.rstrip('\n').split('\t') for l in open(p, encoding='utf-8')] if os.path.exists(p) else []


@pytest.fixture
def app(tmp_path):
    folder = str(tmp_path / 'buch')
    make_book(folder)
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    p = subprocess.Popen([sys.executable, os.path.join(ROOT, 'server.py'), folder, '--port', str(port), '--no-browser'],
                         env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    c = Client(port, folder)
    try:
        for _ in range(600):
            if p.poll() is not None:
                raise RuntimeError('Server beendet: ' + p.stdout.read().decode('utf-8', 'replace'))
            try:
                c.raw('/api/bookmark')
                break
            except OSError:
                time.sleep(0.1)
        else:
            raise RuntimeError('Server startet nicht')
        yield c
    finally:
        p.kill()
        p.wait()
