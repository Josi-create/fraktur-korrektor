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
    assert os.path.exists(korrlib._cache_path)
    assert korrlib._cache_path.startswith(os.environ['FRAKTUR_HOME'])


def test_kein_woerterbuch_verstaendliche_meldung(monkeypatch, tmp_path):
    monkeypatch.setattr(korrlib, 'HERE', str(tmp_path))
    monkeypatch.setattr(korrlib, 'DIC', str(tmp_path / 'gibtsnicht.dic'))
    with pytest.raises(SystemExit) as e:
        korrlib.find_dic()
    assert 'Kein Wörterbuch gefunden' in str(e.value) and 'gibtsnicht' in str(e.value)
