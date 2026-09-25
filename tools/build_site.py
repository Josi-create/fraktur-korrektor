"""Hilfe als Website: docs/de und docs/en mit derselben Vorlage wie im Programm (server.help_html) nach site/.
py tools/build_site.py [<zielordner>]        Standard: site/ neben server.py
Ansehen: site/index.html im Browser öffnen. Veröffentlicht wird sie von .github/workflows/pages.yml
unter https://josi-create.github.io/fraktur-korrektor/ – eine zweite Quelle gibt es nicht."""
import sys, os, re, glob, shutil; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import server

REPO = 'https://github.com/Josi-create/fraktur-korrektor'
LANGS = ('de', 'en')
WORDS = dict(de=dict(home='Startseite', app='im Programm', choose='Hilfe auf Deutsch', title='Hilfe',
                     more='Quelltext, Fehlermeldungen und alle Fassungen auf GitHub', releases='Programm herunterladen'),
             en=dict(home='Home', app='in the program', choose='Help in English', title='Help',
                     more='Source code, bug reports and all versions on GitHub', releases='Download the program'))


def href(lang, name, cur):
    """Adresse einer Hilfeseite aus Sicht einer Seite der Sprache cur: usage.html bzw. ../en/usage.html."""
    return name + '.html' if lang == cur else '../%s/%s.html' % (lang, name)


def app_links(html, lang):
    """Links auf Programmfunktionen (/bibliothek, /buch/…) führen auf der Website nirgendwohin: Der Text bleibt,
    dazu der Hinweis, dass es sie im Programm gibt."""
    return re.sub(r'<a href="/(?:bibliothek|buch)(?:[/?#][^"]*)?">(.*?)</a>',
                  lambda m: '%s (%s)' % (m.group(1), WORDS[lang]['app']), html)


def page(lang, name):
    html = server.help_html(lang, name, href=lambda l, n: href(l, n, lang), home=('../index.html', WORDS[lang]['home']))
    return app_links(html, lang)


def readme_intro():
    """Der Überblick aus der README: alles zwischen der Überschrift und dem ersten Abschnitt – ohne den Verweis auf die
    englische README, die es auf der Website nicht gibt (die Sprachwahl steht darüber)."""
    src = open(os.path.join(server.HERE, 'README.md'), encoding='utf-8').read()
    m = re.search(r'^# .*?\n(.*?)^## ', src, re.S | re.M)
    return re.sub(r'^\*English version:.*$', '', m.group(1), flags=re.M).strip() if m else ''


def index_html():
    """Startseite: Sprachwahl und der kurze Programmüberblick aus der README, in derselben Vorlage."""
    import markdown
    choice = ''.join('<p><a href="%s/index.html"><b>%s</b></a></p>' % (l, WORDS[l]['choose']) for l in LANGS)
    intro = markdown.markdown(readme_intro())
    intro = re.sub(r'href="docs/(de|en)/([\w-]+)\.md"', r'href="\1/\2.html"', intro)
    body = '<h1>Fraktur-Korrektor</h1>%s%s<p><a href="%s/releases/latest">%s</a> · <a href="%s">%s</a></p>' % (
        choice, intro, REPO, WORDS['de']['releases'], REPO, WORDS['de']['more'])
    nav = ''.join('<a href="%s/index.html">%s</a>' % (l, WORDS[l]['title']) for l in LANGS)
    langs = ' · '.join('<a href="%s/index.html">%s</a>' % (l, 'Deutsch' if l == 'de' else 'English') for l in LANGS)
    return server.HELP_PAGE % dict(lang='de', title='Fraktur-Korrektor', nav=nav, body=body, langs=langs,
                                   home='GitHub', home_url=REPO)


def build(out):
    """Schreibt die ganze Website nach out und gibt die erzeugten Dateien zurück."""
    written = []
    for lang in LANGS:
        d = os.path.join(out, lang)
        shutil.rmtree(d, ignore_errors=True)  # keine Seiten übrig lassen, die es in docs/ nicht mehr gibt
        os.makedirs(d)
        for f in sorted(glob.glob(os.path.join(server.HERE, 'docs', lang, '*.md'))):
            name = os.path.basename(f)[:-3]
            p = os.path.join(d, name + '.html')
            with open(p, 'w', encoding='utf-8', newline='\n') as w:
                w.write(page(lang, name))
            written.append(p)
        img = os.path.join(server.HERE, 'docs', lang, 'img')
        if os.path.isdir(img):
            shutil.copytree(img, os.path.join(d, 'img'))
    os.makedirs(out, exist_ok=True)
    p = os.path.join(out, 'index.html')
    with open(p, 'w', encoding='utf-8', newline='\n') as w:
        w.write(index_html())
    written.append(p)
    return written


if __name__ == '__main__':
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(server.HERE, 'site'))
    print(len(build(out)), 'Seiten ->', out)
