"""Die Hilfe als Website (tools/build_site.py): jede Seite aus docs/ kommt heraus, alle Links lösen sich auf,
nichts zeigt mehr auf /hilfe oder die Bibliothek, beide Sprachen verweisen aufeinander."""
import os, re, sys
from conftest import ROOT
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import build_site


def links(html):
    return re.findall(r'href="([^"]+)"', html)


def test_website(tmp_path):
    out = str(tmp_path / 'site')
    build_site.build(out)
    assert os.path.exists(os.path.join(out, 'index.html'))
    for lang in ('de', 'en'):
        md = {f[:-3] for f in os.listdir(os.path.join(ROOT, 'docs', lang)) if f.endswith('.md')}
        html = {f[:-5] for f in os.listdir(os.path.join(out, lang)) if f.endswith('.html')}
        assert html == md, lang
    for d, _, files in os.walk(out):
        for f in files:
            if not f.endswith('.html'):
                continue
            p = os.path.join(d, f)
            html = open(p, encoding='utf-8').read()
            assert '/hilfe/' not in html, p
            assert 'href="/' not in html, p  # keine Adresse des Programms (/, /bibliothek, /buch/…) bleibt übrig
            for h in links(html):
                if re.match(r'[a-z]+:', h) or h.startswith('#'):
                    continue
                ziel = os.path.normpath(os.path.join(d, h.split('#')[0]))
                assert os.path.exists(ziel), '%s -> %s' % (p, h)
    for name in ('index', 'usage'):
        de = open(os.path.join(out, 'de', name + '.html'), encoding='utf-8').read()
        en = open(os.path.join(out, 'en', name + '.html'), encoding='utf-8').read()
        assert '<a href="../en/%s.html">English</a>' % name in de
        assert '<a href="../de/%s.html">Deutsch</a>' % name in en
        assert 'href="usage.html"' in de and 'href="usage.html"' in en  # Navigation bleibt relativ
    start = open(os.path.join(out, 'index.html'), encoding='utf-8').read()
    assert 'href="de/index.html"' in start and 'href="en/index.html"' in start
    assert 'Fraktur' in start and '<h1>' in start


def test_programmlinks_werden_text():
    html = 'Öffnen Sie die <a href="/bibliothek">Bibliothek</a> oder <a href="/buch/0123abcd/">das Buch</a>, ' \
           'nicht aber <a href="https://example.org/buch">diesen Link</a>.'
    out = build_site.app_links(html, 'de')
    assert out.startswith('Öffnen Sie die Bibliothek (im Programm) oder das Buch (im Programm), ')
    assert '<a href="https://example.org/buch">' in out
    assert 'in the program' in build_site.app_links('<a href="/bibliothek">Library</a>', 'en')


def test_programm_rendert_unveraendert(lib):
    """Im Programm zeigen die Links weiter auf /hilfe/<sprache>/<seite> und oben links auf die Bibliothek."""
    html = lib.raw('/hilfe/de/usage')[1].decode('utf-8')
    assert '<a href="/hilfe/de/index"' in html and '<a href="/hilfe/en/usage">English</a>' in html
    assert '<a href="/">Bibliothek</a>' in html
