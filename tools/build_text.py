"""PAGE-XML -> Korrekturtexte mit Fußnotentrennung (Kommandozeile zu pagexml.py).
py build_text.py <page-ordner> <out-ordner>
Schreibt out/NNN.txt (Kopfzeile, Haupttext, Zeile '---' , Fußnoten) und out/lines.json
(je Seite Zeilen mit Bildkoordinaten in Transkribus-Pixeln, Bildgröße, Art)."""
import sys, os, glob; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pagexml
src, out = sys.argv[1:3]
r = pagexml.build(glob.glob(os.path.join(src, '*.xml')), out)
print(r['pages'], 'Seiten,', r['fn'], 'mit Fußnoten ->', out)
