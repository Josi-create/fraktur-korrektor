"""Veröffentlichen (scripts/release.py): Versionsnummer an allen Stellen, CHANGELOG-Abschnitt, Text des Releases,
und dass README und Release dieselben festen Dateinamen benutzen wie die Builds."""
import os, re, shutil, sys
import pytest
from conftest import ROOT
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import release


@pytest.fixture
def repo(tmp_path):
    for name in ('pyproject.toml', 'CITATION.cff'):
        shutil.copy(os.path.join(ROOT, name), tmp_path / name)
    (tmp_path / 'CHANGELOG.md').write_text(
        '# Änderungen\n\n## [Unveröffentlicht]\n\n### Neu\n- Etwas Neues, siehe [Hilfe](docs/de/usage.md) und '
        '[Keep a Changelog](https://keepachangelog.com/de/) (#12).\n\n## [0.5.0] – 2026-09-18\n\nAlter Stand.\n',
        encoding='utf-8')
    return str(tmp_path)


def test_bump_und_notes(repo):
    release.bump(repo, '1.2.3', '2026-10-01')
    assert release.current_version(repo) == '1.2.3'
    cff = release.read(repo, 'CITATION.cff')
    assert 'version: 1.2.3\n' in cff and 'date-released: 2026-10-01\n' in cff
    log = release.read(repo, 'CHANGELOG.md')
    assert '## [Unveröffentlicht]\n\n## [1.2.3] – 2026-10-01\n\n### Neu' in log
    assert release.section(repo, 'Unveröffentlicht') == ''
    assert release.section(repo, '0.5.0') == 'Alter Stand.'

    text = release.notes(repo, 'v1.2.3')
    assert 'Etwas Neues' in text and 'Alter Stand' not in text
    # relative Links werden absolut, fremde bleiben, wie sie sind
    assert f'[Hilfe]({release.REPO}/blob/v1.2.3/docs/de/usage.md)' in text
    assert '(https://keepachangelog.com/de/)' in text
    for _, name in release.DOWNLOADS:
        assert f'{release.REPO}/releases/download/v1.2.3/{name}' in text


def test_bump_verweigert(repo):
    with pytest.raises(SystemExit):
        release.bump(repo, '1.2', '2026-10-01')        # keine Versionsnummer
    with pytest.raises(SystemExit):
        release.bump(repo, '0.5.0', '2026-10-01')      # gibt es schon
    release.bump(repo, '1.2.3', '2026-10-01')
    with pytest.raises(SystemExit):
        release.bump(repo, '1.2.4', '2026-10-02')      # nichts Unveröffentlichtes mehr


def test_notes_verweigert(repo):
    with pytest.raises(SystemExit):
        release.notes(repo, 'v9.9.9')                  # passt nicht zu pyproject.toml
    with pytest.raises(SystemExit):
        release.notes(repo, 'v' + release.current_version(repo))  # kein CHANGELOG-Abschnitt


def test_crlf_bleibt(repo):
    p = os.path.join(repo, 'CHANGELOG.md')
    text = release.read(repo, 'CHANGELOG.md').replace('\n', '\r\n')
    release.write(repo, 'CHANGELOG.md', text)
    release.bump(repo, '1.2.3', '2026-10-01')
    raw = open(p, 'rb').read()
    assert b'\n' not in raw.replace(b'\r\n', b'')
    assert b'## [1.2.3] \xe2\x80\x93 2026-10-01\r\n' in raw


def test_feste_dateinamen():
    """Was README, Hilfe und Release verlinken, muss der Workflow auch bauen und nach dem Veröffentlichen prüfen."""
    workflow = open(os.path.join(ROOT, '.github', 'workflows', 'release.yml'), encoding='utf-8').read()
    for _, name in release.DOWNLOADS:
        assert name in workflow, name
    for doc in ('README.md', 'README.en.md', 'docs/de/install.md', 'docs/en/install.md'):
        text = open(os.path.join(ROOT, doc), encoding='utf-8').read()
        for name in re.findall(r'releases/latest/download/([^)\s]+)', text):
            assert name in dict((n, l) for l, n in release.DOWNLOADS), (doc, name)


def test_readme_beginnt_mit_download():
    """Ganz oben im README steht der Weg zur neuesten Version – vor der ersten Zwischenüberschrift."""
    for doc in ('README.md', 'README.en.md'):
        head = open(os.path.join(ROOT, doc), encoding='utf-8').read().split('\n## ')[0]
        assert f'{release.REPO}/releases/latest' in head, doc
        for _, name in release.DOWNLOADS:
            assert f'releases/latest/download/{name}' in head, (doc, name)
