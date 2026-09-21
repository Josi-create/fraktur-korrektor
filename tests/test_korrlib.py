import os
import pytest
import korrlib


def test_joined_tokens_trennung():
    toks, joined = korrlib.joined_tokens(['Die Zu¬', 'kunft lag', 'kein¬ ', ''])
    assert toks[0] == [(0, 'Die'), (4, 'Zu')]
    assert joined == [(0, 4, 'Zu', 1, 'kunft')]


def test_joined_tokens_trennzeichen_nicht_am_wort():
    assert korrlib.joined_tokens(['Seite 5 ¬', 'weiter'])[1] == []


def test_corpus_freq():
    assert korrlib.corpus_freq({'001': ['ber ber', 'der'], '002': ['ber']})['ber'] == 3


def test_woerterbuch_alte_rechtschreibung():
    assert korrlib.in_dict('daß') and korrlib.in_dict('Rußland') and korrlib.in_dict('Schiffahrt')
    assert not korrlib.in_dict('ber') and not korrlib.in_dict('Bolk')


def test_zusatz_und_fallen():
    assert korrlib.in_dict('Vgl') and korrlib.in_dict('usw')
    assert not korrlib.in_dict('baß')


def test_cache_wird_gespeichert():
    korrlib.in_dict('Zwischenspeicherprobe')
    korrlib.save_cache()
    c = korrlib.checker('1901')
    assert os.path.exists(c.cache_path) and c.cache_path.startswith(os.environ['FRAKTUR_HOME'])


def test_woerterbuch_erst_bei_bedarf(tmp_path, monkeypatch):
    """Steht jedes Wort im Zwischenspeicher, wird das Wörterbuch gar nicht eingelesen (das kostet Sekunden bei jedem Start)."""
    c = korrlib.checker('1901')
    assert c.lookup('Haus') is True and c.d is not None  # echtes Nachschlagen lädt das Wörterbuch
    c.save()
    c2 = korrlib.Checker(c.path)  # neuer Prozess: nur der Zwischenspeicher von der Platte
    assert c2.d is None and c2.lookup('Haus') is True and c2.d is None
    assert c2.lookup('Zwischenspeicherprobe2') is False and c2.d is not None  # erst ein unbekanntes Wort holt es


def test_cache_speichern_aus_zwei_threads():
    """Hintergrundauftrag und Browser-Anfrage speichern zugleich: Beide schrieben über dieselbe .tmp-Datei, und wer zuletzt
    umbenannte, fand sie nicht mehr – »Text nachlegen« endete dann mit einem unbekannten Fehler."""
    import threading
    c = korrlib.Checker(korrlib.checker('1901').path)
    fehler = []

    def speichern(k):
        try:
            for n in range(40):
                c.cache['probe-%d-%d' % (k, n)] = False  # wie lookup(): es kommt laufend etwas dazu
                c.save()
        except Exception as e:
            fehler.append(repr(e))
    threads = [threading.Thread(target=speichern, args=(k,)) for k in range(4)]
    for th in threads: th.start()
    for th in threads: th.join()
    assert not fehler
    assert len(korrlib.Checker(c.path).cache) == len(c.cache)  # und die Datei ist heil und vollständig


def test_rechtschreibung_je_epoche():
    alt, neu, alle = ('1901',), ('1901', 'neu'), ('1901', 'neu', 'vor1901')
    assert korrlib.in_dict('daß', alt) and korrlib.in_dict('Schiffahrt', alt)
    assert not korrlib.in_dict('dass', alt) and korrlib.in_dict('dass', neu) and korrlib.in_dict('Schifffahrt', neu)
    for w in ('Thür', 'seyn', 'Noth', 'Brod', 'Freyheit', 'Vermuthungen', 'civilisiren', 'giebt', 'Waare'):
        assert not korrlib.in_dict(w, neu) and korrlib.in_dict(w, alle), w
    for w in ('ber', 'bie', 'Bolk', 'unb', 'baß'):  # Lesefehler bleiben in jeder Epoche Fehler
        assert not korrlib.in_dict(w, alle), w
    assert korrlib.in_dict('Ebd') and korrlib.in_dict('Hg') and korrlib.in_dict('Offb')  # Apparat und Bibelstellen


def test_erscheinungsjahr_und_vorschlag():
    g = korrlib.guess_year
    assert g({'001': ['Sehnsucht nach Jerusalem'], '002': ['Die Auswanderung 1817', '© 2002 Tübinger Vereinigung', 'ISBN 3-932512-17-0']}) == 2002
    assert g({'001': ['Stuttgart 1928', 'Ausland und Heimat'], '002': ['12.345 Einwohner, 1.817 Eimer, S. 1928-1930 nicht']}) == 1928
    assert g({'001': ['ohne Jahr']}) is None
    assert g({'%03d' % n: ['im Jahre 1999'] if n == 50 else ['Text 1818'] for n in range(1, 100)}) == 1818  # nur Titelei und Schluss zählen
    d = korrlib.dics_for_year
    assert (d(1818), d(1928), d(2002), d(None)) == (['1901', 'vor1901'], ['1901'], ['1901', 'neu'], ['1901'])


def test_kein_woerterbuch_verstaendliche_meldung(monkeypatch, tmp_path):
    monkeypatch.setattr(korrlib, 'HERE', str(tmp_path))
    monkeypatch.setattr(korrlib, 'DIC', str(tmp_path / 'gibtsnicht.dic'))
    with pytest.raises(SystemExit) as e:
        korrlib.find_dic()
    assert 'Kein Wörterbuch gefunden' in str(e.value) and 'gibtsnicht' in str(e.value)
