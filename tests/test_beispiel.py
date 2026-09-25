"""Das mitgelieferte Beispielbuch (#4, beispiel/README.md): gemeinfrei, so wie das Programm es selbst einliest."""
import os, shutil
from conftest import ROOT


def test_beispielbuch_vollstaendig(tmp_path):
    """Acht Seiten, jede Textzeile hat ihre Bildzeile – geprüft an einer Kopie, damit der Test nichts ins Repository schreibt."""
    import server
    folder = tmp_path / 'beispiel'
    shutil.copytree(os.path.join(ROOT, 'beispiel'), folder)
    b = server.Book(str(folder))
    b.refresh()
    assert list(b.pages) == ['%03d' % n for n in range(1, 9)]
    for pg in b.pages:
        d = b.page_data(pg)
        assert d['img'].endswith(pg + '.jpg') and d['geo'] and len(d['geo']) == len(d['lines']), pg
        assert all(g for g, l in zip(d['geo'], d['lines']) if l != '---' and not l.startswith('#')), pg
    assert '1862.' in b.pages['001'] and 'Habe nun, ach! Philosophie,' in b.pages['002']
    assert sum(l.endswith('¬') for pg in ('006', '007', '008') for l in b.pages[pg]) >= 5  # Prosa mit Trennungen
    assert not os.path.exists(os.path.join(ROOT, 'beispiel', 'buch.json'))
