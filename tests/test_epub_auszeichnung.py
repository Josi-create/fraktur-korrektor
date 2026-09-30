"""EPUB einlesen, ohne die Auszeichnung zu verlieren (#81): Überschriften, Absätze, Tabellen, fett und kursiv."""
import os, zipfile
import epub, korrlib
from test_ocr import wait

CSS = '''/* Stilvorlage */
p.note { font-style: italic; font-size: 0.9em }
span.fett, .kraeftig { font-weight: 700; }
table.gloss td.w { font-style: italic }
h3.sec { font-weight: bold; text-align: center }
span.pn { vertical-align: super }'''


def make_epub(path, bodies, css=CSS, title='Probe'):
    """EPUB mit beliebigem XHTML je Kapitel und einer Stilvorlage."""
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr('mimetype', 'application/epub+zip')
        z.writestr('META-INF/container.xml', '<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles>'
                   '<rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>')
        items = ''.join('<item id="c%d" href="c%d.xhtml" media-type="application/xhtml+xml"/>' % (n, n) for n in range(len(bodies)))
        refs = ''.join('<itemref idref="c%d"/>' % n for n in range(len(bodies)))
        z.writestr('OEBPS/content.opf', '<package xmlns="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/"><metadata>'
                   '<dc:title>%s</dc:title></metadata><manifest><item id="css" href="stil.css" media-type="text/css"/>%s</manifest>'
                   '<spine>%s</spine></package>' % (title, items, refs))
        z.writestr('OEBPS/stil.css', css)
        for n, body in enumerate(bodies):
            z.writestr('OEBPS/c%d.xhtml' % n, '<?xml version="1.0" encoding="utf-8"?>\n<html xmlns="http://www.w3.org/1999/xhtml" '
                       'xmlns:epub="http://www.idpf.org/2007/ops"><head><title>x</title><link rel="stylesheet" href="stil.css"/>'
                       '</head><body>%s</body></html>' % body)


def lines_of(folder, n=1):
    return (folder / ('%03d.txt' % n)).read_text(encoding='utf-8').split('\n')[:-1]


def test_stilvorlage():
    rules = epub.css_rules(CSS)
    assert (None, {'kraeftig'}, {'b'}) in rules and ('span', {'fett'}, {'b'}) in rules and ('p', {'note'}, {'i'}) in rules
    assert ('td', {'w'}, {'i'}) in rules and ('span', {'pn'}, {'sup'}) in rules  # bei »table.gloss td.w« zählt td.w


def test_zeile_schliesst_was_sie_oeffnet():
    ws = epub._words([('Ein ', ()), ('ganz kursiver', ('em',)), (' Satz', ()), ('1', ('sup',)), ('.', ())])
    assert [epub.plain(w) for w in ws] == ['Ein', 'ganz', 'kursiver', 'Satz1.']
    assert epub.render(ws) == 'Ein <em>ganz kursiver</em> Satz<sup>1</sup>.'
    assert epub.render(ws[:2]) == 'Ein <em>ganz</em>' and epub.render(ws[2:]) == '<em>kursiver</em> Satz<sup>1</sup>.'
    assert epub.render([[('fett', ('b',)), ('kursiv', ('b', 'i'))], [('weiter', ('i',))]]) == '<b>fett<i>kursiv</i></b><i> weiter</i>'
    # und zurück: eine Zeile des Buchs als Stücke
    assert epub.line_runs('<p>Ein <em>ganz</em> <b>fettes</b> Wort<sup>1</sup>') == [
        ('Ein ', ()), ('ganz', ('em',)), (' ', ()), ('fettes', ('b',)), (' Wort', ()), ('1', ('sup',))]


BODY = ('<h1>Erster Teil</h1>'
        '<h2>Die Reise<br/><span style="font-size:0.6em">nach Odessa</span></h2>'
        '<p>Die Kolonisten zogen nach <b>Rußland</b>, und der Weg war <em>sehr weit und über alle Maßen beschwerlich</em>, '
        'so schrieb der Chronist<sup>1</sup>.<span epub:type="pagebreak" role="doc-pagebreak" id="s5">[5]</span></p>'
        '<p class="note">Anmerkung des Herausgebers.</p>'
        '<p>Er rief: <span class="fett">Halt!</span> Und <span class="kraeftig">alle</span> blieben stehen.</p>'
        '<h3 class="sec">73.</h3>'
        '<table class="gloss"><tr><th>Wort</th><th>Bedeutung</th></tr>'
        '<tr><td class="w">Kolonie</td><td>Siedlung</td></tr><tr><td colspan="2">Ende der Liste</td></tr></table>'
        '<p>Nachher.</p>')


def test_textbuch_mit_auszeichnung(tmp_path):
    make_epub(str(tmp_path / 'x.epub'), [BODY])
    assert epub.read(str(tmp_path / 'x.epub'))[1][0][:4] == ['Erster Teil', 'Die Reise', 'nach Odessa',
                                                              'Die Kolonisten zogen nach Rußland, und der Weg war sehr weit und über alle Maßen beschwerlich, so schrieb der Chronist1.']
    epub.text_book(str(tmp_path / 'x.epub'), str(tmp_path / 'out'), width=40)
    lines = lines_of(tmp_path / 'out')
    assert lines == [
        '# ',
        '<h1>Erster Teil</h1>', '',
        '<h2>Die Reise</h2>', '<h2>nach Odessa</h2>', '',  # zwei Zeilen derselben Ebene: eine Überschrift
        '<p>Die Kolonisten zogen nach <b>Rußland</b>, und',
        'der Weg war <em>sehr weit und über alle</em>',        # kursiv über den Zeilenumbruch: je Zeile geschlossen
        '<em>Maßen beschwerlich</em>, so schrieb der',
        'Chronist<sup>1</sup>.', '',                           # die Seitenmarke [5] gehört nicht zum Text
        '<p><i>Anmerkung des Herausgebers.</i>', '',           # kursiv über die Stilvorlage
        '<p>Er rief: <b>Halt!</b> Und <b>alle</b> blieben stehen.', '',
        '<h3>73.</h3>', '',                                     # fett ist eine Überschrift ohnehin
        '<table><tr><th>Wort</th>', '<th>Bedeutung</th></tr>',
        '<tr><td><i>Kolonie</i></td>', '<td>Siedlung</td></tr>',
        '<tr><td>Ende der Liste</td>', '<td></td></tr></table>', '',  # verbundene Zellen: das Gitter bleibt gerade
        '<p>Nachher.']
    pages = {'001': lines}
    assert [(lv, tx) for _, _, lv, tx in korrlib.headings(pages)] == [(1, 'Erster Teil'), (2, 'Die Reise nach Odessa'), (3, '73.')]
    assert korrlib.table_block(lines, lines.index('<td>Siedlung</td></tr>')) == (17, 22)


def test_absatz_mitten_im_satz(tmp_path):
    """Manches EPUB trennt Absätze an den Zeilen seiner Vorlage – mitten im Satz. Das wird kein Absatz; Listen bleiben."""
    make_epub(str(tmp_path / 'x.epub'), ['<p>„Sell ischt wohl!“, gaben die anderen zu. „Aber sei Land ischt</p><p>groß und — ‚Dr Zar ischt weit’.“</p>'
                                         '<p>Kindlieb, Karl 34 Jahre</p><p>Tausch, Katharina 54 Jahre</p><p>Auf dem fürstlichen</p><p>Gutshofe in Radewan.</p>'])
    epub.text_book(str(tmp_path / 'x.epub'), str(tmp_path / 'out'), width=80)
    assert lines_of(tmp_path / 'out') == ['# ', '<p>„Sell ischt wohl!“, gaben die anderen zu. „Aber sei Land ischt', 'groß und — ‚Dr Zar ischt weit’.“', '',
                                          '<p>Kindlieb, Karl 34 Jahre', '', '<p>Tausch, Katharina 54 Jahre', '', '<p>Auf dem fürstlichen', 'Gutshofe in Radewan.']


def test_tabelle_ueber_die_seitengrenze(tmp_path):
    rows = ''.join('<tr><td>Ort %d</td><td>%d</td></tr>' % (n, n) for n in range(20))
    make_epub(str(tmp_path / 'x.epub'), ['<p>Vorher.</p><table>%s</table>' % rows])
    r = epub.text_book(str(tmp_path / 'x.epub'), str(tmp_path / 'out'), per_page=30)
    assert r['pages'] == 2
    for n in (1, 2):  # jede Seite trägt eine vollständige Tabelle; eine Reihe wird nicht geteilt
        ls = [l for l in lines_of(tmp_path / 'out', n) if '<t' in l]
        assert ls[0].startswith('<table><tr><td>') and ls[-1].endswith('</td></tr></table>') and len(ls) % 2 == 0


def test_epub_auf_pdf_zeilen_mit_auszeichnung(tmp_path):
    book = tmp_path / 'buch'; book.mkdir()
    (book / '001.txt').write_text('\n'.join([
        '# — 7 —',
        'Erſter Teil',
        'Die Reiſe',
        'nach Odeſſa',
        'Die Koloniſten zogen nach Rußland, und der',
        'Weg war ſehr weit und über alle Maßen be¬',
        'ſchwerlich, ſo ſchrieb der Chroniſt1.',
        'Er rief: Halt! Und alle blieben ſtehen.']) + '\n', encoding='utf-8')
    make_epub(str(tmp_path / 'x.epub'), [BODY.replace('<em>sehr weit und über alle Maßen beschwerlich</em>',
                                                      'sehr weit und über alle Maßen <em>beschwerlich</em>')])
    r = epub.transplant(str(tmp_path / 'x.epub'), str(book))
    assert lines_of(book) == [
        '# — 7 —',
        '<h1>Erster Teil</h1>',
        '<h2>Die Reise</h2>',
        '<h2>nach Odessa</h2>',
        '<p>Die Kolonisten zogen nach <b>Rußland</b>, und der',
        'Weg war sehr weit und über alle Maßen <em>be¬</em>',  # ¬ am Wort, die Auszeichnung dahinter
        '<em>schwerlich</em>, so schrieb der Chronist<sup>1</sup>.',
        '<p>Er rief: <b>Halt!</b> Und <b>alle</b> blieben stehen.']
    assert r['matched'] == 1.0
    # die Wortprüfung sieht das getrennte Wort als eines
    toks, joined = korrlib.joined_tokens(lines_of(book))
    assert [(w1, w2) for _, _, w1, _, w2 in joined] == [('be', 'schwerlich')]


def test_nachtragen_behaelt_den_wortlaut():
    """Für ein schon korrigiertes Buch: nur Auszeichnung dazu, kein Wort anders; was schon ausgezeichnet ist, bleibt."""
    E = epub.Words()
    for w, lv, st in [('Erster', 1, ()), ('Teil', 1, ()), ('Die', 0, ()), ('Kolonisten', 0, ('i',)), ('zogen', 0, ('i',)),
                      ('nach', 0, ()), ('Rußland,', 0, ()), ('und', 0, ()), ('der', 0, ()), ('Weg', 0, ()), ('war', 0, ()),
                      ('weit', 0, ('b',)), ('und', 0, ()), ('lang.', 0, ())]:
        E.start = w == 'Die'
        E.add([(w, st)], lv)
    pages = {'001': ['# 5', 'Erſter Teil', 'Die Koloniſten zogen nach Rußland,', 'und der Weg war weit', 'und lang.<sup>1</sup>']}
    out, st = epub.markup(E, pages)
    assert out['001'] == ['# 5', '<h1>Erſter Teil</h1>',
                          '<p>Die <i>Koloniſten zogen</i> nach Rußland,',  # anders geschrieben, im EPUB ganz kursiv: das ganze Wort
                          'und der Weg war <b>weit</b>', 'und lang.<sup>1</sup>']
    assert st == dict(headings=1, paragraphs=1, words=3, checked=1, matched=1)
    assert all(korrlib.TAG.sub('', a) == korrlib.TAG.sub('', b) for a, b in zip(pages['001'], out['001']))
    assert epub.markup(E, out)[0] == {}  # ein zweites Mal: nichts mehr zu tun


def test_nachtragen_ueber_die_schnittstelle(app, tmp_path):
    bid = app.book.split('/')[-1]
    make_epub(str(tmp_path / 'fremd.epub'), ['<p>Ganz anderer Text über Schiffe und Häfen im hohen Norden des Landes.</p>'])
    j = wait(app, app.lpost('/api/epub_markup', dict(id=bid, source=str(tmp_path / 'fremd.epub')))[1]['job'])
    assert (j['state'], j['error']) == ('error', 'epub_passt_nicht') and not app.log()  # nichts angefasst
    make_epub(str(tmp_path / 'buch.epub'), ['<p>Die Kolonisten zogen nach <em>Rußland</em> und der Weg war weit.</p>'
                                            '<p>Die <b>Zukunft</b> lag vor ihnen, daß sie der Heimat gedachten.</p><p>Der Vater und der Sohn.</p>'])
    j = wait(app, app.lpost('/api/epub_markup', dict(id=bid, source=str(tmp_path / 'buch.epub')))[1]['job'])
    assert j['state'] == 'done', j
    assert j['result'] == dict(headings=0, paragraphs=2, words=2, checked=2, matched=2, pages=2, id=j['result']['id'])
    assert app.text('001')[1:4] == ['<p>Die Kolonisten zogen nach <em>Rußland</em> und', 'ber Weg war weit. Die <b>Zu¬</b>', '<b>kunft</b> lag vor ihnen, baß sie']
    assert app.text('002')[1] == '<p>Der Vater und ber Sohn.'
    assert {r[1] for r in app.log()} == {'serie:' + j['result']['id']} and j['result']['id'].startswith('auszeichnung-')
    # die Wortprüfung sieht »Zukunft« weiter als ein Wort
    assert not any(f['word'].startswith('Zu') for f in app.get('/api/page/001')[1]['flags'])
    # U nimmt alles zurück
    assert app.get('/api/series_last')[1]['id'] == j['result']['id']
    assert app.post('/api/series_undo', {})[1]['done'] == 4
    assert app.text('001')[1] == 'Die Kolonisten zogen nach Rußland und' and app.text('002')[1] == 'Der Vater und ber Sohn.'


def test_als_ebook_getrennt_und_ausgezeichnet():
    """Das E-Book zieht ein getrenntes Wort auch dann zusammen, wenn hinter dem ¬ Auszeichnung schließt."""
    import epubbuch
    pages = {'001': ['# 5', '<h2><em>Über¬</em></h2>', '<h2><em>fahrt</em></h2>', '<p>Der Weg war <em>be¬</em>', '<em>schwerlich</em>, sagte er.'],
             '002': ['# 6', '<b>Zu¬</b>'], '003': ['# 7', '<b>kunft</b> und Heimat.']}
    r = epubbuch.build(dict(pages=pages, labels={'001': '5', '002': '6', '003': '7'}, foot={}, kopf={}, title='Probe'))
    t = '\n'.join(body for _, _, body in r['files'])
    assert '<em>Über</em><em>fahrt</em></h2>' in t and 'Der Weg war <em>be</em><em>schwerlich</em>, sagte er.' in t
    assert '<b>Zu</b><b>kunft</b>' in t and 'aria-label="7">[7]</span> und Heimat.' in t  # Seitenmarke hinter dem ganzen Wort


def test_eigenes_ebook_wieder_einlesen(tmp_path):
    """Ein E-Book dieses Programms als Textbuch: Überschriften, Absätze und Fußnotenzeichen bleiben, Seitenmarken nicht."""
    import epubbuch
    pages = {'001': ['# 5', '<h2>Vorwort</h2>', '<p>Der Text<sup>1</sup> beginnt <em>hier</em>.', '---', '1 Eine Fußnote.'],
             '002': ['# 6', '<h2>Erstes Kapitel</h2>', '<p>Weiter & fort.']}
    epubbuch.write(dict(pages=pages, labels={'001': '5', '002': '6'}, foot={}, kopf={}, title='Probebuch'), str(tmp_path / 'b.epub'))
    epub.text_book(str(tmp_path / 'b.epub'), str(tmp_path / 'out'))
    text = [l for n in range(1, 6) if (tmp_path / 'out' / ('%03d.txt' % n)).exists() for l in lines_of(tmp_path / 'out', n)]
    assert '<h2>Vorwort</h2>' in text and '<h2>Erstes Kapitel</h2>' in text and '<p>Weiter & fort.' in text
    assert '<p>Der Text<sup>1</sup> beginnt <em>hier</em>.' in text and not any('[5]' in l or '[6]' in l for l in text)


def test_textbuch_auf_pdf_zeilen_behaelt_auszeichnung(tmp_path):
    """Ein Textbuch (EPUB ohne PDF) bekommt später den Scan (#40): Die Auszeichnung darin kommt mit."""
    src = tmp_path / 'text'; src.mkdir()
    (src / '001.txt').write_text('\n'.join(['# ', '<h2>Die Reise</h2>', '', '<p>Die Kolonisten zogen nach <b>Ruß¬</b>',
                                           '<b>land</b>, und der Weg war <em>weit</em>. Sie kamen an.']) + '\n', encoding='utf-8')
    E = epub.book_text(str(src))
    assert E.plain == ['Die', 'Reise', 'Die', 'Kolonisten', 'zogen', 'nach', 'Rußland,', 'und', 'der', 'Weg', 'war', 'weit.', 'Sie', 'kamen', 'an.']
    assert E.level[:3] == [2, 2, 0] and E.para == {2}
    assert epub.book_words(str(src)) == E.plain
    book = tmp_path / 'buch'; book.mkdir()
    (book / '001.txt').write_text('\n'.join(['# 7', 'Die Reiſe', 'Die Koloniſten zogen nach Rußland, und', 'der Weg war weit. Sie kamen an.']) + '\n',
                                  encoding='utf-8')
    epub.transplant_book(str(src), str(book))
    assert lines_of(book) == ['# 7', '<h2>Die Reise</h2>', '<p>Die Kolonisten zogen nach <b>Rußland</b>, und', 'der Weg war <em>weit</em>. Sie kamen an.']
