"""Das mitgelieferte Beispielbuch (#4, beispiel/README.md): gemeinfrei, so wie das Programm es selbst einliest."""
import os, shutil
from conftest import ROOT


def test_beispielbuch_vollstaendig(tmp_path):
    """Acht Seiten, jede Textzeile hat ihre Bildzeile – geprüft an einer Kopie, damit der Test nichts ins Repository schreibt."""
    import server
    folder, repo = tmp_path / 'beispiel', os.path.join(ROOT, 'beispiel')
    before = sorted(os.listdir(repo))
    shutil.copytree(repo, folder)
    b = server.Book(str(folder))
    b.refresh()
    assert list(b.pages) == ['%03d' % n for n in range(1, 9)]
    for pg in b.pages:
        d = b.page_data(pg)
        assert d['img'].endswith(pg + '.jpg') and d['geo'] and len(d['geo']) == len(d['lines']), pg
        assert all(g for g, l in zip(d['geo'], d['lines']) if l != '---' and not l.startswith('#')), pg
    assert '1862.' in b.pages['001'] and 'Habe nun, ach! Philosophie,' in b.pages['002']
    assert sum(l.endswith('¬') for pg in ('006', '007', '008') for l in b.pages[pg]) >= 5  # Prosa mit Trennungen
    assert sorted(os.listdir(repo)) == before  # geprüft wurde die Kopie


def test_beispielbuch_aus_der_bibliothek(lib, tmp_path):
    """»Beispielbuch öffnen« legt eine Kopie im Bücherordner an; ein zweiter Klick öffnet dieselbe Kopie, ein fremder
    Ordner gleichen Namens bleibt unberührt."""
    fremd = tmp_path / 'buecher' / 'Beispiel - Goethe, Faust (1862)'
    fremd.mkdir(parents=True)
    (fremd / 'notiz.txt').write_text('meins', encoding='utf-8')
    code, r = lib.lpost('/api/beispiel', {})
    assert code == 200
    kopie = tmp_path / 'buecher' / 'Beispiel - Goethe, Faust (1862) (2)'
    assert (kopie / '003.txt').is_file() and (kopie / 'img' / '003.jpg').is_file()
    assert sorted(os.listdir(fremd)) == ['notiz.txt']
    (kopie / '003.txt').write_text('geübt\n', encoding='utf-8')
    assert lib.lpost('/api/beispiel', {}) == (200, r)
    assert (kopie / '003.txt').read_text(encoding='utf-8') == 'geübt\n'  # die Übung bleibt
    books = lib.lget('/api/library')[1]['books']
    assert [b['title'] for b in books] == ['Goethe: Faust (1862)']
