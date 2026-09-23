"""#40: EPUB ohne gleichnamiges PDF – das PDF von anderswo dazuholen (Öffnen-Dialog) oder einem Textbuch nachreichen."""
import os, io
import pytest
import epub
from test_open import make_epub, PARAS
from test_ocr import make_searchable_pdf, wait


def make_other_pdf(path, fitz):
    """Ein durchsuchbares PDF mit ganz anderem Inhalt – gehört zu keinem EPUB dieser Tests."""
    d = fitz.open()
    for n in range(3):
        pg = d.new_page(width=420, height=595)
        for k, l in enumerate(['Der Dampfer verliess den Hafen bei Nebel und', 'die Matrosen sangen ein altes Lied vom', 'Meer, das niemand mehr kannte.']):
            pg.insert_text((50, 100 + 22 * k), l, fontsize=13, fontname='tiro')
    d.save(path); d.close()


def test_textbuch_wortlaut_und_stichprobe(tmp_path):
    """Wortlaut eines Textbuchs ohne Kopfzeile, Fußnotenstrich und Auszeichnung, getrennte Wörter wieder eines –
    und die Stichprobe: gehört das PDF zu diesem Wortlaut?"""
    fitz = pytest.importorskip('fitz')
    book = tmp_path / 'tb'; book.mkdir()
    (book / '001.txt').write_text('# 3\nDie <em>Kolonisten</em> zogen nach Ruß¬\nland, | und der Weg war weit.\n---\n1) Fußnote.\n', encoding='utf-8')
    assert epub.book_words(str(book)) == ['Die', 'Kolonisten', 'zogen', 'nach', 'Rußland,', 'und', 'der', 'Weg', 'war', 'weit.', '1)', 'Fußnote.']
    make_searchable_pdf(str(tmp_path / 'p.pdf'), fitz)
    make_other_pdf(str(tmp_path / 'fremd.pdf'), fitz)
    words = [w for p in PARAS for w in p.split()]
    assert epub.pdf_fit(words, str(tmp_path / 'p.pdf')) >= 0.4
    assert epub.pdf_fit(words, str(tmp_path / 'fremd.pdf')) == 0.0
    d = fitz.open(); d.new_page(); d.save(str(tmp_path / 'leer.pdf')); d.close()
    assert epub.pdf_fit(words, str(tmp_path / 'leer.pdf')) is None  # keine Textebene: erst nach der Erkennung zu sagen


def test_epub_mit_pdf_von_anderswo(lib, tmp_path):
    """Kein gleichnamiges PDF daneben – der Nutzer holt es von anderswo; danach läuft es wie EPUB + PDF."""
    fitz = pytest.importorskip('fitz')
    (tmp_path / 'a').mkdir(); (tmp_path / 'b').mkdir()
    make_epub(str(tmp_path / 'a' / 'Probe.epub'), [[p.replace('Rußland', 'RUSSLAND') for p in PARAS]] * 3, title='Probe')
    make_searchable_pdf(str(tmp_path / 'b' / 'Scan 1832.pdf'), fitz)
    f = lib.lpost('/api/scan', dict(path=str(tmp_path / 'a' / 'Probe.epub')))[1]['found'][0]
    assert f['kind'] == 'epub' and f['pdf'] is None
    code, r = lib.lpost('/api/epub_pair', dict(source=f['path'], pdf=str(tmp_path / 'b' / 'Scan 1832.pdf')))
    assert code == 200 and r['text'] and r['pages'] == 3 and r['fit'] >= 0.4 and r['pdf'].endswith('Scan 1832.pdf')
    j = wait(lib, lib.lpost('/api/import_epub', dict(source=f['path'], pdf=r['pdf'], textlayer=True, target=str(tmp_path / 'ziel')))[1]['job'])
    assert j['state'] == 'done', j
    assert j['result']['matched'] > 0.6 and j['result']['pages'] == 3
    page = lib.lget('/buch/%s/api/page/001' % j['result']['id'])[1]
    assert 'RUSSLAND' in page['lines'][1] and page['img'].endswith('.jpg')
    # Fehlfälle: kein PDF, kein EPUB, ein fremdes PDF – verständlich abgelehnt, nichts angelegt
    assert lib.lpost('/api/epub_pair', dict(source=f['path'], pdf=str(tmp_path / 'a' / 'Probe.epub'))) == (400, dict(error='quelle_fehlt'))
    assert lib.lpost('/api/epub_pair', dict(source=str(tmp_path / 'b' / 'Scan 1832.pdf'), pdf=str(tmp_path / 'b' / 'Scan 1832.pdf'))) == (400, dict(error='kein_epub'))
    make_other_pdf(str(tmp_path / 'b' / 'fremd.pdf'), fitz)
    assert lib.lpost('/api/epub_pair', dict(source=f['path'], pdf=str(tmp_path / 'b' / 'fremd.pdf'))) == (400, dict(error='pdf_passt_nicht'))
    j = wait(lib, lib.lpost('/api/import_epub', dict(source=f['path'], pdf=str(tmp_path / 'b' / 'fremd.pdf'), textlayer=True, target=str(tmp_path / 'ziel2')))[1]['job'])
    assert (j['state'], j['error']) == ('error', 'pdf_passt_nicht')
    assert not os.path.exists(tmp_path / 'ziel2') and len(lib.lget('/api/library')[1]['books']) == 1


def test_pdf_zum_textbuch_nachreichen(lib, tmp_path):
    """Ein Textbuch (EPUB ohne PDF), darin schon korrigiert – das PDF kommt später. Es entsteht ein neues Buch mit
    Bildern, Zeilen und dem korrigierten Text; das Textbuch bleibt unangetastet."""
    fitz = pytest.importorskip('fitz')
    make_epub(str(tmp_path / 'Probe.epub'), [[p.replace('Rußland', 'RUSSLAND') for p in PARAS]] * 3, title='Probe')
    (tmp_path / 'anderswo').mkdir()
    make_searchable_pdf(str(tmp_path / 'anderswo' / 'scan.pdf'), fitz)
    r = wait(lib, lib.lpost('/api/import_epub', dict(source=str(tmp_path / 'Probe.epub'), target=str(tmp_path / 'text')))[1]['job'])['result']
    b = lib.lget('/api/library')[1]['books'][0]
    assert b['textbook'] and b['images'] == 0
    bid = r['id']
    old = lib.lget('/buch/%s/api/page/001' % bid)[1]['lines'][1]
    assert 'RUSSLAND' in old
    lib.lpost('/buch/%s/api/edit/001' % bid, dict(edits=[dict(line=1, old=old, new=old.replace('RUSSLAND', 'Rußland'))]))
    lib.lpost('/buch/%s/api/whitelist' % bid, dict(word='Kolonisten'))
    assert lib.lpost('/api/epub_pair', dict(id=bid, pdf=str(tmp_path / 'anderswo' / 'scan.pdf')))[1]['fit'] >= 0.4
    j = wait(lib, lib.lpost('/api/add_pdf', dict(id=bid, source=str(tmp_path / 'anderswo' / 'scan.pdf')))[1]['job'])
    assert j['state'] == 'done', j
    n = j['result']
    assert n['neu'] and n['id'] != bid and n['pages'] == 3 and n['matched'] > 0.6 and n['title'] == 'Probe'
    page = lib.lget('/buch/%s/api/page/001' % n['id'])[1]
    assert 'Rußland' in page['lines'][1] and 'RUSSLAND' not in page['lines'][1] and page['img'].endswith('.jpg') and page['geo'][1]
    assert open(os.path.join(n['folder'], 'whitelist.txt'), encoding='utf-8').read().split() == ['Kolonisten']
    assert not os.path.exists(os.path.join(n['folder'], 'korrekturen.log'))  # das Protokoll gehört zu den Seiten des Textbuchs
    assert lib.lget('/buch/%s/api/page/001' % bid)[1]['img'] is None and os.path.exists(tmp_path / 'text' / 'korrekturen.log')
    books = lib.lget('/api/library')[1]['books']
    assert sorted((x['title'], x['textbook']) for x in books) == [('Probe', False), ('Probe', True)]
    # ein fremdes PDF: nichts angelegt
    make_other_pdf(str(tmp_path / 'fremd.pdf'), fitz)
    assert lib.lpost('/api/epub_pair', dict(id=bid, pdf=str(tmp_path / 'fremd.pdf'))) == (400, dict(error='pdf_passt_nicht'))
    j = wait(lib, lib.lpost('/api/add_pdf', dict(id=bid, source=str(tmp_path / 'fremd.pdf')))[1]['job'])
    assert (j['state'], j['error']) == ('error', 'pdf_passt_nicht') and len(lib.lget('/api/library')[1]['books']) == 2


def test_pdf_dazuholen_nur_lokal():
    """Dateidialog und Einlesen sind aus dem LAN gesperrt – auch die neuen Wege."""
    import server
    for path in ('/api/epub_pair', '/api/add_pdf', '/api/choose'):
        h = server.H.__new__(server.H)
        h.client_address, h.path, h.request_version, h.command, h.requestline = ('192.168.1.20', 4711), path, 'HTTP/1.1', 'POST', ''
        h.headers = {'Content-Length': '2'}
        h.rfile, h.wfile = io.BytesIO(b'{}'), io.BytesIO()
        h.do_POST()
        out = h.wfile.getvalue().decode('utf-8')
        assert ' 403 ' in out.split('\r\n')[0] and 'nur_lokal' in out, path
