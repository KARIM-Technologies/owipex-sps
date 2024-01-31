UPBoard RGB Button Controller Python-Bibliothek README
Übersicht
Die UPBoardController-Python-Bibliothek bietet eine Schnittstelle zur Steuerung von RGB-LEDs und zur Erfassung von Schaltereingaben auf dem UP Board Squared Pro über den 40-Pin-Header. Sie ermöglicht das Anzeigen verschiedener Zustände durch die Farben und Muster der LEDs sowie die Erfassung der Dauer von Schalterbetätigungen.

Funktionen
Initialisierung und GPIO-Setup: Konfiguriert die GPIO-Pins für die LEDs und den Schalter.
LED-Steuerung: Ermöglicht das Ein- und Ausschalten der LEDs, das Blinken und das Anzeigen von Zuständen durch Farben und Muster.
Schaltereingabe-Erfassung: Misst die Dauer, für die der Schalter gedrückt wird.
Anforderungen
Python 3
RPi.GPIO-Bibliothek
Zugriff auf GPIO-Pins auf dem UP Board Squared Pro
Installation
Installieren Sie die benötigten Abhängigkeiten (z.B. RPi.GPIO) über pip und laden Sie das Skript auf Ihr UP Board.

Benutzung
Importieren Sie die UPBoardController-Klasse in Ihr Python-Skript und instanziieren Sie ein Objekt. Verwenden Sie die Methoden set_led, blink_led, display_state, und read_switch_duration, um die LEDs zu steuern und die Schaltereingaben zu verarbeiten.

Beispiel
Ein Beispielcode ist im Abschnitt "Beispiel zur Nutzung der Bibliothek" des Skripts enthalten. Dies zeigt, wie man Zustände anzeigt und Schalterbetätigungen erfasst.

Anpassung
Das Skript kann leicht angepasst werden, um zusätzliche Funktionen oder Zustände hinzuzufügen. Überprüfen Sie die Pin-Zuweisungen und passen Sie sie bei Bedarf an Ihre Hardwarekonfiguration an.

Lizenz