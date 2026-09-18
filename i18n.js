// Oberflächentexte Deutsch/Englisch für reader.html und bibliothek.html.
// Sprache: gemerkte Wahl, sonst Browsersprache. t('schluessel', {platzhalter: wert}) liefert den Text.
const LANGS = ['de', 'en'];
let LANG = 'de';
try { LANG = localStorage.getItem('lang') || ((navigator.language || 'de').toLowerCase().startsWith('de') ? 'de' : 'en'); } catch (e) {}
if (!LANGS.includes(LANG)) LANG = 'de';

const T = {
de: {
  library: 'Bibliothek', help: 'Hilfe', help_f1: 'Hilfe (F1)', page: 'Seite', p_abbr: 'S.',
  loading: 'Buch wird geladen … Beim ersten Öffnen prüft das Programm jedes Wort gegen das Wörterbuch – das kann bis zu einer Minute dauern. Danach geht es schnell.',
  mode_read: 'Lesen', mode_fix: 'Korrektur', mode_free: 'Zeile bearbeiten',
  pos: 'Zeile {a}/{b} · rot auf dieser Seite: {c} · im Buch: {d}', nogeo: ' · (keine Bildzuordnung für diese Seite)',
  help_read: '<kbd>↓</kbd> <kbd>↑</kbd> Zeile · <kbd>Leertaste</kbd> zum nächsten roten Wort · <kbd>F8</kbd> nächstes rotes Wort ist richtig · <kbd>Enter</kbd> rotes Wort der Zeile ändern bzw. Zeile frei bearbeiten (<kbd>F2</kbd> immer frei) · <kbd>Bild↓</kbd> <kbd>Bild↑</kbd> Seite · <kbd>Pos1</kbd> <kbd>Ende</kbd> · <kbd>G</kbd> gehe zu Seite · <kbd>+</kbd> <kbd>−</kbd> <kbd>0</kbd> Zoom · <kbd>R</kbd> neu laden · <kbd>F9</kbd> Serienkorrektur · <kbd>U</kbd> letzte Serie zurücknehmen · <kbd>W</kbd> Whitelist · <kbd>F</kbd> Fußnoten beginnen hier',
  help_fix: '<kbd>Enter</kbd> übernehmen, weiterlesen · <kbd>F7</kbd> Trennzeichen ¬ · <kbd>F8</kbd> Wort ist richtig (merken) · <kbd>Tab</kbd> nächstes rotes Wort · <kbd>F9</kbd> Serienkorrektur · <kbd>Esc</kbd> zurück zum Lesen',
  help_free: '<kbd>Enter</kbd> übernehmen · <kbd>F7</kbd> Trennzeichen ¬ · <kbd>Esc</kbd> verwerfen',
  pending: '„{old}“ kommt noch <b>{n}×</b> im Buch vor – <kbd>F9</kbd> zeigt alle Stellen zum Ersetzen durch „{new}“',
  flags_1: '{n} fragliche Stelle in dieser Zeile', flags_n: '{n} fragliche Stellen in dieser Zeile', reading: 'Lesemodus',
  kind_auto: 'automatisch ersetzt: ', kind_oov: 'unbekannt: ', edit_line: 'Zeile {n} bearbeiten',
  edit2_title: 'Folgezeile (zweiter Teil des getrennten Wortes)',
  no_more: 'Keine weiteren fraglichen Stellen.',
  conflict: 'Die Datei wurde inzwischen außerhalb geändert – Seite wird neu geladen, bitte Korrektur wiederholen.',
  wl_head: 'Whitelist (als richtig gemerkte Wörter, neueste zuerst)', filter: 'Filter',
  wl_help: '<kbd>←</kbd> <kbd>→</kbd> <kbd>↑</kbd> <kbd>↓</kbd> Wort · <kbd>Entf</kbd> oder <kbd>Leertaste</kbd> oder Klick: herausnehmen / wieder aufnehmen · <kbd>Tab</kbd> Filter · <kbd>Esc</kbd> schließen',
  wl_count: '{n} Wörter', wl_gone: ' · {g} herausgenommen (werden wieder rot)',
  ser_head: 'Serienkorrektur:', ser_word: 'Wort', ser_new: 'ersetzen durch',
  ser_help: '<kbd>↓</kbd> <kbd>↑</kbd> Stelle · <kbd>Leertaste</kbd> Haken an/aus · <kbd>A</kbd> alle an/aus · <kbd>Tab</kbd> Ersetzung ändern · <kbd>Enter</kbd> alle angehakten ersetzen · <kbd>Esc</kbd> abbrechen',
  ser_checked: '{on} von {n} Stellen angehakt', ser_none: 'keine Fundstellen für „{w}“', ser_enter: 'Wort eingeben, Enter',
  ser_done: 'Serie „{w}“ → „{nw}“: {done} Stellen ersetzt', ser_skipped: ', {n} übersprungen', ser_undo_hint: ' (U nimmt sie zurück)',
  undo_confirm: 'Letzte Serienkorrektur zurücknehmen?', undo_done: 'Serie {id} zurückgenommen: {done} Zeilen',
  undo_skipped: ', {n} inzwischen geändert und belassen', undo_none: 'Keine Serie zum Zurücknehmen.',
  no_red: 'Kein rotes Wort mehr auf dieser Seite.', remembered: '„{w}“ als richtig gemerkt.',
  fn_set: 'Fußnoten beginnen jetzt mit dieser Zeile (nochmal F nimmt den Trenner wieder weg).', fn_removed: 'Fußnotentrenner entfernt.',
  changed_outside: 'Seite wurde außerhalb geändert – neu geladen.', goto: 'Gehe zu Seite (PDF-Seite):',

  lib_intro: 'Lesen und Korrekturlesen in einem: links das Seitenbild, rechts der erkannte Text.',
  open_folder: 'Buchordner öffnen …', import_tk: 'Transkribus-Export importieren …',
  col_title: 'Titel', col_pages: 'Seiten', col_pos: 'Lesezeichen', col_last: 'zuletzt geöffnet', col_folder: 'Ordner',
  missing: 'Ordner nicht gefunden', forget: 'aus der Liste entfernen',
  forget_confirm: 'Eintrag „{t}“ aus der Bibliothek entfernen? Die Dateien bleiben erhalten.',
  empty: 'Noch keine Bücher. Öffnen Sie einen vorhandenen Buchordner oder importieren Sie einen Export aus Transkribus – die Hilfe erklärt beides Schritt für Schritt.',
  remote: 'Bücher hinzufügen geht nur an dem Rechner, auf dem das Programm läuft.',
  path_prompt: 'Pfad des Buchordners:',
  imp_title: 'Transkribus-Export importieren', imp_source: 'Export aus Transkribus (ZIP-Datei oder entpackter Ordner)',
  choose_zip: 'ZIP-Datei wählen …', choose_folder: 'Ordner wählen …',
  imp_name: 'Titel des Buchs', imp_name_ph: 'leer = Titel aus dem Export',
  imp_images: 'Ordner mit Seitenbildern – nur nötig, wenn der Export keine Bilder enthält',
  imp_target: 'Das Buch wird angelegt unter: {dir}',
  imp_go: 'Importieren', cancel: 'Abbrechen', importing: 'Import läuft …',
  imp_done: '{n} Seiten importiert, {i} Seitenbilder.',
  warn_bilder_fehlen: 'Es fehlen Seitenbilder – ohne sie zeigt das Programm nur den Text. Bilder lassen sich nachträglich in den Unterordner „img“ legen (001.png, 002.png, … oder .jpg).',
  open_now: 'Buch öffnen',
  err_kein_buch: 'In diesem Ordner liegen keine Seitendateien (001.txt, 002.txt, …).',
  err_quelle_fehlt: 'Die angegebene Datei bzw. der Ordner wurde nicht gefunden.',
  err_keine_xml: 'Darin wurden keine PAGE-XML-Dateien gefunden. Beim Export in Transkribus muss „PAGE XML“ angehakt sein.',
  err_nur_lokal: 'Das geht nur an dem Rechner, auf dem das Programm läuft.',
  err_unknown: 'Das hat nicht geklappt.',
  donate: 'Gefällt Ihnen das Programm? Kaffee spendieren ☕', source: 'Quelltext und Mitarbeit auf GitHub',
},
en: {
  library: 'Library', help: 'Help', help_f1: 'Help (F1)', page: 'Page', p_abbr: 'p.',
  loading: 'Loading book … The first time a book is opened, every word is checked against the dictionary – this can take up to a minute. After that it is fast.',
  mode_read: 'Reading', mode_fix: 'Correction', mode_free: 'Edit line',
  pos: 'Line {a}/{b} · red on this page: {c} · in the book: {d}', nogeo: ' · (no image alignment for this page)',
  help_read: '<kbd>↓</kbd> <kbd>↑</kbd> line · <kbd>Space</kbd> next red word · <kbd>F8</kbd> next red word is correct · <kbd>Enter</kbd> change red word of this line, or edit the line (<kbd>F2</kbd> always edits) · <kbd>PgDn</kbd> <kbd>PgUp</kbd> page · <kbd>Home</kbd> <kbd>End</kbd> · <kbd>G</kbd> go to page · <kbd>+</kbd> <kbd>−</kbd> <kbd>0</kbd> zoom · <kbd>R</kbd> reload · <kbd>F9</kbd> batch correction · <kbd>U</kbd> undo last batch · <kbd>W</kbd> whitelist · <kbd>F</kbd> footnotes start here',
  help_fix: '<kbd>Enter</kbd> apply and read on · <kbd>F7</kbd> hyphenation mark ¬ · <kbd>F8</kbd> word is correct (remember) · <kbd>Tab</kbd> next red word · <kbd>F9</kbd> batch correction · <kbd>Esc</kbd> back to reading',
  help_free: '<kbd>Enter</kbd> apply · <kbd>F7</kbd> hyphenation mark ¬ · <kbd>Esc</kbd> discard',
  pending: '“{old}” occurs <b>{n}</b> more times in the book – <kbd>F9</kbd> lists them all for replacing with “{new}”',
  flags_1: '{n} doubtful word in this line', flags_n: '{n} doubtful words in this line', reading: 'Reading mode',
  kind_auto: 'replaced automatically: ', kind_oov: 'unknown: ', edit_line: 'Edit line {n}',
  edit2_title: 'Next line (second part of the hyphenated word)',
  no_more: 'No more doubtful words.',
  conflict: 'The file was changed outside the program – the page will be reloaded, please repeat your correction.',
  wl_head: 'Whitelist (words remembered as correct, newest first)', filter: 'Filter',
  wl_help: '<kbd>←</kbd> <kbd>→</kbd> <kbd>↑</kbd> <kbd>↓</kbd> word · <kbd>Del</kbd> or <kbd>Space</kbd> or click: remove / restore · <kbd>Tab</kbd> filter · <kbd>Esc</kbd> close',
  wl_count: '{n} words', wl_gone: ' · {g} removed (will turn red again)',
  ser_head: 'Batch correction:', ser_word: 'word', ser_new: 'replace with',
  ser_help: '<kbd>↓</kbd> <kbd>↑</kbd> occurrence · <kbd>Space</kbd> tick on/off · <kbd>A</kbd> all on/off · <kbd>Tab</kbd> change replacement · <kbd>Enter</kbd> replace all ticked · <kbd>Esc</kbd> cancel',
  ser_checked: '{on} of {n} occurrences ticked', ser_none: 'no occurrences of “{w}”', ser_enter: 'type a word, Enter',
  ser_done: 'Batch “{w}” → “{nw}”: {done} occurrences replaced', ser_skipped: ', {n} skipped', ser_undo_hint: ' (U undoes it)',
  undo_confirm: 'Undo the last batch correction?', undo_done: 'Batch {id} undone: {done} lines',
  undo_skipped: ', {n} changed since and left alone', undo_none: 'No batch to undo.',
  no_red: 'No more red words on this page.', remembered: '“{w}” remembered as correct.',
  fn_set: 'Footnotes now start with this line (F again removes the separator).', fn_removed: 'Footnote separator removed.',
  changed_outside: 'Page was changed outside the program – reloaded.', goto: 'Go to page (PDF page):',

  lib_intro: 'Reading and proofreading in one: the page image on the left, the recognised text on the right.',
  open_folder: 'Open book folder …', import_tk: 'Import Transkribus export …',
  col_title: 'Title', col_pages: 'Pages', col_pos: 'Bookmark', col_last: 'last opened', col_folder: 'Folder',
  missing: 'folder not found', forget: 'remove from list',
  forget_confirm: 'Remove “{t}” from the library? The files stay where they are.',
  empty: 'No books yet. Open an existing book folder or import an export from Transkribus – the help explains both step by step.',
  remote: 'Books can only be added on the computer the program runs on.',
  path_prompt: 'Path of the book folder:',
  imp_title: 'Import Transkribus export', imp_source: 'Export from Transkribus (ZIP file or unpacked folder)',
  choose_zip: 'Choose ZIP file …', choose_folder: 'Choose folder …',
  imp_name: 'Title of the book', imp_name_ph: 'empty = title from the export',
  imp_images: 'Folder with page images – only needed if the export contains no images',
  imp_target: 'The book will be created in: {dir}',
  imp_go: 'Import', cancel: 'Cancel', importing: 'Importing …',
  imp_done: '{n} pages imported, {i} page images.',
  warn_bilder_fehlen: 'Page images are missing – without them only the text is shown. You can add images later to the subfolder “img” (001.png, 002.png, … or .jpg).',
  open_now: 'Open book',
  err_kein_buch: 'This folder contains no page files (001.txt, 002.txt, …).',
  err_quelle_fehlt: 'The file or folder was not found.',
  err_keine_xml: 'No PAGE XML files found in there. When exporting from Transkribus, “PAGE XML” must be ticked.',
  err_nur_lokal: 'This only works on the computer the program runs on.',
  err_unknown: 'That did not work.',
  donate: 'Do you like the program? Buy me a coffee ☕', source: 'Source code and contributing on GitHub',
}};

function t(k, v) {
  let s = T[LANG][k] ?? T.de[k] ?? k;
  if (v) for (const [a, b] of Object.entries(v)) s = s.split('{' + a + '}').join(b);
  return s;
}
function setLang(l) { try { localStorage.setItem('lang', l); } catch (e) {} location.reload(); }
function applyI18n() {
  document.documentElement.lang = LANG;
  for (const el of document.querySelectorAll('[data-t]')) el.innerHTML = t(el.dataset.t);
  for (const el of document.querySelectorAll('[data-t-ph]')) el.placeholder = t(el.dataset.tPh);
  for (const el of document.querySelectorAll('[data-t-title]')) el.title = t(el.dataset.tTitle);
  for (const el of document.querySelectorAll('[data-help]')) el.href = '/hilfe/' + LANG + '/' + el.dataset.help;
  for (const el of document.querySelectorAll('.langsw')) {
    el.innerHTML = LANGS.map(l => l == LANG ? '<b>' + l.toUpperCase() + '</b>' : '<a href="#" data-l="' + l + '">' + l.toUpperCase() + '</a>').join(' | ');
    for (const a of el.querySelectorAll('a')) a.onclick = e => { e.preventDefault(); setLang(a.dataset.l); };
  }
}
