"""Startprogramm der gepackten App (Windows .exe, Mac .app) – Doppelklick statt Kommandozeile.

Der Fraktur-Korrektor hat kein eigenes Fenster; der Browser ist das Fenster. Ohne ein sichtbares Symbol liefe der
Server unbemerkt weiter, darum zeigt der Starter eines: auf dem Mac im Dock und in der Menüleiste, unter Windows
im Infobereich der Taskleiste. Darüber wird das Programm auch wieder beendet.

Ein zweiter Doppelklick startet kein zweites Programm, sondern öffnet den Browser auf die laufende Instanz
(auf dem Mac über das Reopen-Ereignis, sonst über die Anfrage an /api/ping).

Die Argumente sind die von server.py (Buchordner, --port, --dic, --title, --lan, --no-browser); zusätzlich
unterdrückt --no-ui das Symbol – so lässt sich die gepackte App auch ohne Bildschirm prüfen.
"""
import sys, os, json, threading, webbrowser, subprocess, urllib.request

import korrlib
import server

APP = 'Fraktur-Korrektor'


def alert(text):
    """Fehlermeldung, die auch ohne Konsole ankommt – sonst startet die App scheinbar grundlos nicht."""
    print(text)
    if sys.platform == 'darwin':
        subprocess.run(['osascript', '-e', 'display alert "%s" message "%s"' % (APP, text.replace('"', "'"))],
                       capture_output=True)
    elif os.name == 'nt':
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, text, APP, 0x10)


# Den schon offenen Tab wiederfinden: »Im Browser öffnen« soll das Fenster zeigen und nicht ein weiteres
# aufmachen. AppleScript ist dafür der einzige Weg; Safari und die Chromium-Browser sprechen es verschieden.
TABS_SAFARI = """tell application "%(app)s"
    repeat with w in windows
        repeat with t in tabs of w
            if URL of t contains "%(mark)s" then
                set current tab of w to t
                set index of w to 1
                activate
                return "ok"
            end if
        end repeat
    end repeat
end tell"""

TABS_CHROMIUM = """tell application "%(app)s"
    repeat with w in windows
        set n to 0
        repeat with t in tabs of w
            set n to n + 1
            if URL of t contains "%(mark)s" then
                set active tab index of w to n
                set index of w to 1
                activate
                return "ok"
            end if
        end repeat
    end repeat
end tell"""

BROWSERS = [('Safari', TABS_SAFARI)] + [(name, TABS_CHROMIUM) for name in (
    'Google Chrome', 'Google Chrome Canary', 'Microsoft Edge', 'Brave Browser', 'Vivaldi', 'Chromium', 'Opera')]


def running_apps():
    """Was gerade läuft – über NSWorkspace, denn eine Abfrage per AppleScript fragte unnötig nach Erlaubnis."""
    try:
        from AppKit import NSWorkspace
        return {a.localizedName() for a in NSWorkspace.sharedWorkspace().runningApplications()}
    except ImportError:
        return set()


def focus_tab(url):
    """Holt den Tab mit dieser Adresse nach vorn; False, wenn es keinen gibt oder der Browser nicht mitspielt
    (Firefox kann das nicht, und beim ersten Mal fragt macOS, ob wir den Browser steuern dürfen)."""
    mark = url.split('//', 1)[-1]
    apps = running_apps()
    for name, script in BROWSERS:
        if name not in apps:
            continue
        try:
            r = subprocess.run(['osascript', '-e', script % dict(app=name, mark=mark)], capture_output=True, timeout=20)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if r.returncode == 0 and b'ok' in r.stdout:
            return True
    return False


def show(url):
    """Das Fenster des Programms zeigen: erst den offenen Tab suchen, sonst einen neuen öffnen."""
    if sys.platform == 'darwin' and focus_tab(url):
        return
    webbrowser.open(url)


def answering(port):
    """Antwortet auf dem Port schon ein Fraktur-Korrektor? Dann kein zweites Programm starten."""
    try:
        with urllib.request.urlopen('http://127.0.0.1:%d/api/ping' % port, timeout=3) as r:
            return json.loads(r.read().decode('utf-8')).get('app') == 'fraktur-korrektor'
    except (OSError, ValueError):
        return False


def mac_ui(url, on_quit):
    """Dock-Symbol mit Menü und Symbol in der Menüleiste; hält den Hauptthread, bis der Benutzer beendet."""
    import AppKit
    from PyObjCTools import AppHelper

    def entry(title, action, target, key=''):
        it = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(title, action, key)
        it.setTarget_(target)
        return it

    class Delegate(AppKit.NSObject):
        def applicationShouldHandleReopen_hasVisibleWindows_(self, app, visible):
            show(url)  # zweiter Doppelklick auf die App im Finder oder Dock
            return True

        def applicationDockMenu_(self, sender):
            m = AppKit.NSMenu.alloc().init()
            m.addItem_(entry('Im Browser öffnen', 'openBrowser:', self))
            return m

        def openBrowser_(self, sender):
            show(url)

        def applicationWillTerminate_(self, note):
            on_quit()

    app = AppKit.NSApplication.sharedApplication()
    app.setActivationPolicy_(AppKit.NSApplicationActivationPolicyRegular)
    delegate = Delegate.alloc().init()
    app.setDelegate_(delegate)

    # Menüleiste der App: ohne sie wäre nicht einmal Befehlstaste+Q belegt.
    bar = AppKit.NSMenu.alloc().init()
    head = AppKit.NSMenuItem.alloc().init()
    bar.addItem_(head)
    sub = AppKit.NSMenu.alloc().init()
    sub.addItem_(entry('Im Browser öffnen', 'openBrowser:', delegate))
    sub.addItem_(AppKit.NSMenuItem.separatorItem())
    sub.addItem_(entry(APP + ' beenden', 'terminate:', app, 'q'))
    head.setSubmenu_(sub)
    app.setMainMenu_(bar)

    # Symbol in der Menüleiste – sichtbar, auch wenn das Dock ausgeblendet ist.
    status = AppKit.NSStatusBar.systemStatusBar().statusItemWithLength_(AppKit.NSVariableStatusItemLength)
    img = AppKit.NSImage.imageWithSystemSymbolName_accessibilityDescription_('book.closed', APP)
    if img:
        status.button().setImage_(img)
    else:
        status.button().setTitle_('FK')
    menu = AppKit.NSMenu.alloc().init()
    menu.addItem_(entry('Im Browser öffnen', 'openBrowser:', delegate))
    menu.addItem_(AppKit.NSMenuItem.separatorItem())
    menu.addItem_(entry(APP + ' beenden', 'terminate:', app))
    status.setMenu_(menu)
    delegate.status = status  # Referenz halten, sonst verschwindet das Symbol wieder

    AppHelper.runEventLoop()


def win_ui(url, on_quit):
    """Symbol im Infobereich der Taskleiste (pystray); Doppelklick öffnet den Browser."""
    import pystray
    from PIL import Image

    icon = pystray.Icon('fraktur-korrektor', Image.open(os.path.join(server.HERE, 'icon.png')), APP,
                        pystray.Menu(pystray.MenuItem('Im Browser öffnen', lambda i, e: show(url), default=True),
                                     pystray.MenuItem(APP + ' beenden', lambda i, e: i.stop())))
    icon.run()
    on_quit()


def console_ui(url, on_quit):
    """Ohne die Bibliothek für das Symbol: wie server.py – Strg+C beendet."""
    print('%s: %s  (Strg+C beendet)' % (APP, url))
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        pass
    on_quit()


def pick_ui(noui):
    if noui:
        return console_ui
    try:
        if sys.platform == 'darwin':
            import AppKit  # noqa: F401
            return mac_ui
        import pystray  # noqa: F401
        from PIL import Image  # noqa: F401
        return win_ui
    except ImportError:
        return console_ui


def main(argv=None):
    if sys.stdout is None:  # gepackt ohne Konsole (Windows) – sonst scheitert schon das erste print
        sys.stdout = sys.stderr = open(os.devnull, 'w')
    argv = [a for a in (sys.argv[1:] if argv is None else argv) if not a.startswith('-psn_')]  # der Finder hängt eine Prozessnummer an
    noui = '--no-ui' in argv
    A = server.parse_args([a for a in argv if a != '--no-ui'])
    url = 'http://localhost:%d' % A.port

    if answering(A.port):
        if not A.no_browser:
            show(url)  # das Programm läuft schon: nur das Fenster wieder zeigen
        print('%s läuft schon: %s' % (APP, url))
        return 0
    try:
        httpd, url = server.setup(A)
    except OSError:
        alert('Der Port %d ist belegt: ein anderes Programm benutzt ihn.\n\n'
              'Abhilfe: das andere Programm beenden oder den Fraktur-Korrektor mit --port <nummer> starten.' % A.port)
        return 1

    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    if not A.no_browser:
        show(url)

    def on_quit():
        httpd.shutdown()
        korrlib.save_cache()  # das Fensterprogramm beendet ohne atexit – sonst ginge der Zwischenspeicher verloren

    pick_ui(noui)(url, on_quit)
    return 0


if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[1] == '--dialog':
        server.dialog(*sys.argv[2:4])  # Unterprozess für den Dateidialog (Windows: tkinter braucht den Hauptthread)
    else:
        try:
            sys.exit(main())
        except SystemExit:
            raise
        except Exception as e:  # ohne Konsole bliebe der Fehler unsichtbar und die App startete scheinbar grundlos nicht
            alert('%s konnte nicht starten:\n\n%r' % (APP, e))
            raise
