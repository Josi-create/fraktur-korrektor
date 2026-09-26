"""Eine Version veröffentlichen – ein Befehl, den Rest erledigt GitHub.

    python scripts/release.py 0.12.0        # auf main, ohne offene Änderungen

setzt die Versionsnummer (pyproject.toml, CITATION.cff), macht aus »[Unveröffentlicht]« im CHANGELOG den Abschnitt
dieser Version, legt Commit und Tag v0.12.0 an und schiebt beides nach Rückfrage hoch (»--ja« ohne Rückfrage). Der
Tag startet .github/workflows/release.yml: Tests, Installer bauen und prüfen, Release veröffentlichen.

    python scripts/release.py --notes v0.12.0

gibt den Text des Releases aus (Download-Tabelle und der Abschnitt aus dem CHANGELOG) – so ruft ihn der Workflow
auf. Bricht ab, wenn Tag, pyproject.toml und CHANGELOG nicht zusammenpassen: Dann wird gar nicht erst gebaut.

Nur Standardbibliothek, damit es im Workflow ohne Installation läuft.
"""
import argparse, datetime, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = 'https://github.com/Josi-create/fraktur-korrektor'
UNRELEASED = '## [Unveröffentlicht]'
VERSION_RE = re.compile(r'^\d+\.\d+\.\d+(-[0-9A-Za-z.]+)?$')

# Feste Dateinamen, auf die README und Hilfe mit releases/latest/download/… verweisen. Der Workflow prüft nach dem
# Veröffentlichen, dass jeder davon auf die neue Version zeigt.
DOWNLOADS = [
    ('Windows', 'Fraktur-Korrektor_Setup.exe'),
    ('Mac mit Apple-Chip (M1 und neuer) · Apple Silicon', 'Fraktur-Korrektor-macos-arm64.dmg'),
    ('Mac mit Intel-Chip · Intel', 'Fraktur-Korrektor-macos-x86_64.dmg'),
    ('Linux (x86_64)', 'Fraktur-Korrektor-linux-x86_64.AppImage'),
]


def read(root, name):
    # newline='' behält die Zeilenenden der Datei bei
    with open(os.path.join(root, name), encoding='utf-8', newline='') as f:
        return f.read()


def write(root, name, text):
    with open(os.path.join(root, name), 'w', encoding='utf-8', newline='') as f:
        f.write(text)


def current_version(root=ROOT):
    m = re.search(r'^version\s*=\s*"([^"]+)"', read(root, 'pyproject.toml'), re.M)
    if not m:
        sys.exit('version in pyproject.toml nicht gefunden')
    return m.group(1)


def section(root, version):
    """Der CHANGELOG-Abschnitt einer Version, ohne Überschrift; None, wenn es ihn nicht gibt."""
    text = read(root, 'CHANGELOG.md').replace('\r\n', '\n')
    m = re.search(r'^## \[%s\][^\n]*\n(.*?)(?=^## \[|\Z)' % re.escape(version), text, re.M | re.S)
    return m.group(1).strip() if m else None


def bump(root, version, date):
    """Versionsnummer setzen und den unveröffentlichten Abschnitt des CHANGELOG zu dieser Version machen."""
    if not VERSION_RE.match(version):
        sys.exit(f'»{version}« ist keine Versionsnummer wie 0.12.0')
    if section(root, version) is not None:
        sys.exit(f'Im CHANGELOG gibt es schon einen Abschnitt [{version}].')
    if not section(root, 'Unveröffentlicht'):
        sys.exit('Im CHANGELOG steht unter [Unveröffentlicht] nichts – was soll im Release stehen?')

    text = read(root, 'pyproject.toml')
    write(root, 'pyproject.toml', re.sub(r'^(version\s*=\s*)"[^"]+"', r'\g<1>"%s"' % version, text, count=1, flags=re.M))
    text = read(root, 'CITATION.cff')
    text = re.sub(r'^version:.*$', 'version: ' + version, text, count=1, flags=re.M)
    text = re.sub(r'^date-released:.*$', 'date-released: ' + date, text, count=1, flags=re.M)
    write(root, 'CITATION.cff', text)
    # Die leere Überschrift bleibt oben stehen, darunter kommt der Abschnitt der neuen Version
    text = read(root, 'CHANGELOG.md')
    nl = '\r\n' if '\r\n' in text else '\n'
    write(root, 'CHANGELOG.md', text.replace(UNRELEASED, f'{UNRELEASED}{nl}{nl}## [{version}] – {date}', 1))


def notes(root, tag):
    """Text des Releases zum Tag – bricht ab, wenn Tag, pyproject.toml und CHANGELOG nicht zusammenpassen."""
    version = tag[1:] if tag.startswith('v') else tag
    have = current_version(root)
    if version != have:
        sys.exit(f'Tag {tag} passt nicht zu version = "{have}" in pyproject.toml. '
                 f'Die Version mit »python scripts/release.py {version}« anlegen, nicht von Hand taggen.')
    body = section(root, version)
    if not body:
        sys.exit(f'Im CHANGELOG fehlt der Abschnitt [{version}] – oder er ist leer.')
    # Relative Links des CHANGELOG (docs/…, RELEASE.md) gelten auf der Release-Seite nicht mehr
    body = re.sub(r'\]\((?![a-z]+:|#)([^)]+)\)', lambda m: f']({REPO}/blob/{tag}/{m.group(1)})', body)
    rows = '\n'.join(f'| {label} | [{name}]({REPO}/releases/download/{tag}/{name}) |' for label, name in DOWNLOADS)
    return (f'## Herunterladen · Download\n\n| | |\n|---|---|\n{rows}\n\n'
            f'Welcher Mac? Apple-Menü (oben links) → *Über diesen Mac*: steht dort »Chip Apple M…«, ist es ein Apple-Chip, '
            f'bei »Prozessor Intel …« ein Intel-Chip. Schritt für Schritt: '
            f'[Programm installieren]({REPO}/blob/{tag}/docs/de/install.md) · '
            f'[Installing the program]({REPO}/blob/{tag}/docs/en/install.md)\n\n'
            f'## Änderungen\n\n{body}\n')


def git(*args, capture=False):
    r = subprocess.run(['git', *args], cwd=ROOT, text=True, capture_output=capture)
    if r.returncode:
        sys.exit(f'git {" ".join(args)} ist fehlgeschlagen' + (f':\n{r.stderr}' if capture else ''))
    return r.stdout.strip() if capture else None


def release(version, yes):
    tag = 'v' + version
    if git('rev-parse', '--abbrev-ref', 'HEAD', capture=True) != 'main':
        sys.exit('Bitte auf main veröffentlichen.')
    if git('status', '--porcelain', capture=True):
        sys.exit('Es gibt noch nicht eingecheckte Änderungen – erst committen oder beiseitelegen.')
    git('fetch', '--tags', 'origin')
    if git('rev-list', '--count', 'HEAD..origin/main', capture=True) != '0':
        sys.exit('origin/main ist weiter als der lokale Stand – erst »git pull«.')
    if git('tag', '--list', tag, capture=True):
        sys.exit(f'Den Tag {tag} gibt es schon.')

    bump(ROOT, version, datetime.date.today().isoformat())
    git('add', 'pyproject.toml', 'CITATION.cff', 'CHANGELOG.md')
    git('commit', '-q', '-m', f'Version {version}')
    git('tag', '-a', tag, '-m', f'Version {version}')
    print(f'Commit »Version {version}« und Tag {tag} angelegt.')

    if not yes:
        answer = input(f'Jetzt hochladen? Dann baut GitHub die Installer und veröffentlicht {tag}. [j/N] ')
        if answer.strip().lower() not in ('j', 'ja', 'y', 'yes'):
            print(f'Nicht hochgeladen. Später: git push --atomic origin main {tag}\n'
                  f'Zurücknehmen: git tag -d {tag} && git reset --hard HEAD~1')
            return
    # --atomic: Commit und Tag kommen zusammen an oder gar nicht
    git('push', '--atomic', 'origin', 'main', tag)
    print(f'Hochgeladen. Fortschritt: {REPO}/actions/workflows/release.yml\n'
          f'In gut 15 Minuten steht die Version unter {REPO}/releases/latest')


def main(argv=None):
    p = argparse.ArgumentParser(description='Eine Version veröffentlichen (siehe RELEASE.md).')
    p.add_argument('version', nargs='?', help='neue Versionsnummer, z. B. 0.12.0')
    p.add_argument('--notes', metavar='TAG', help='nur den Text des Releases zu diesem Tag ausgeben')
    p.add_argument('--ja', action='store_true', help='ohne Rückfrage hochladen')
    a = p.parse_args(argv)
    if a.notes:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stdout.write(notes(ROOT, a.notes))
    elif a.version:
        release(a.version.lstrip('v'), a.ja)
    else:
        p.error(f'Versionsnummer fehlt (zurzeit {current_version()})')


if __name__ == '__main__':
    main()
