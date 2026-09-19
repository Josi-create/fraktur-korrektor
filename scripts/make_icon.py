"""Zeichnet das Programmsymbol: icon.png (1024 x 1024) und icon.ico (Windows).

Ein aufgeschlagenes Buch mit Textzeilen, eine davon rot markiert - das ist, was das Programm tut. Bewusst
schlicht und ohne Schrift, damit es in 16 Pixeln noch erkennbar bleibt. Das Ergebnis liegt im Repository;
dieses Skript braucht nur, wer das Symbol aendern will:

    pip install pillow && python scripts/make_icon.py

Fuer den Mac macht scripts/macos/make_icns.sh daraus icon.icns.
"""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
S = 1024                      # Kantenlaenge
RAHMEN = (47, 43, 38, 255)    # dunkles Braungrau wie die Leiste im Programm
PAPIER = (242, 239, 230, 255)
SCHATTEN = (206, 200, 187, 255)
ZEILE = (90, 84, 76, 255)
ROT = (183, 58, 46, 255)      # fragliche Woerter sind im Programm rot


def mix(a, b, t):
    return a + (b - a) * t


def seite(d, x0, x1, y_aussen, y_innen, hoehe, zeilen, rote):
    """Eine Buchseite: leicht nach aussen geneigt, mit Textzeilen. x0 ist die Aussen-, x1 die Falzkante."""
    d.polygon([(x0, y_aussen), (x1, y_innen), (x1, y_innen + hoehe), (x0, y_aussen + hoehe)],
              fill=PAPIER, outline=SCHATTEN, width=int(S * 0.006))
    rand = (x1 - x0) * 0.13
    for i in range(zeilen):
        t = (i + 1) / (zeilen + 1)
        kurz = 0.34 if i == zeilen - 1 else 0.0          # letzte Zeile eines Absatzes endet frueher
        a, b = x0 + rand, x1 - rand - (x1 - x0) * kurz
        ya = mix(y_aussen, y_aussen + hoehe, t)
        yb = mix(y_innen, y_innen + hoehe, t)
        dicke = S * 0.020
        d.polygon([(a, mix(ya, yb, (a - x0) / (x1 - x0))), (b, mix(ya, yb, (b - x0) / (x1 - x0))),
                   (b, mix(ya, yb, (b - x0) / (x1 - x0)) + dicke), (a, mix(ya, yb, (a - x0) / (x1 - x0)) + dicke)],
                  fill=ROT if i in rote else ZEILE)


def main():
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rand = S * 0.055
    d.rounded_rectangle([rand, rand, S - rand, S - rand], radius=S * 0.22, fill=RAHMEN)

    # Buchruecken in der Mitte, die Seiten fallen nach aussen ab.
    mitte, aussen, hoehe = S * 0.50, S * 0.145, S * 0.40
    oben_innen, oben_aussen = S * 0.30, S * 0.345
    seite(d, aussen, mitte - S * 0.008, oben_aussen, oben_innen, hoehe, 5, {2})
    seite(d, S - aussen, mitte + S * 0.008, oben_aussen, oben_innen, hoehe, 5, set())
    d.line([(mitte, oben_innen), (mitte, oben_innen + hoehe)], fill=SCHATTEN, width=int(S * 0.012))

    img.save(ROOT / 'icon.png')
    img.save(ROOT / 'icon.ico', sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print('icon.png und icon.ico geschrieben.')


if __name__ == '__main__':
    main()
