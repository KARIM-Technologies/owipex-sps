# HISTORY.md

## Regeln und wichtige Hinweise

- Wir kommunizieren miteinander in Deutsch.
- Kommentare im Code sowie die Dokumentation sollen auf Englisch sein.
- Alles, was wir hier besprechen, soll in einer Datei namens HISTORY.md gespeichert werden. Diese Datei soll regelmäßig ergänzt und bei Beginn einer neuen Sitzung angeschaut werden, damit der Verlauf nachvollziehbar bleibt.
- Du darfst keine Änderungen machen, die wir nicht vorher besprochen haben. Wenn du unsicher bist, frage nach.
- Du darfst beim Programmieren niemals Vererbungen ändern, ohne Rücksprache.
- Beim Programmieren werden für globale Variablen Pascal-Case, für lokale Variablen und Funktionsparameter camelCase und für Konstanten ausschließlich Großbuchstaben mit Unterstrichen verwendet.
- Falls C# als Programmiersprache verwendet werden soll, verwende die Version .NET 9.0.
- Bevor du, egal ob in C# oder Python, irgendwelche Module oder Libraries verwendest (außer den Standard .NET-Libraries), frage vorher.
- Frage nicht, ob wir committen sollen, das stört. Ich gebe selbst Bescheid, wenn dies gemacht werden soll.
- Daten, die du hier über unsere Arbeit erfährst, dürfen auf keinen Fall weitergegeben werden!
- Falls du unter Windows arbeitest, darfst du deine Befehle (z.B. für git) nicht mit "&&" verketten, da Windows bzw. PowerShell hier Probleme macht.
- Wenn ich irgendwas... schreibe, dann deuten die Punkte auf eine rechtsverkürzte Suche hin.
- **Neue Regel:** Wenn ich den Befehl "sync" eingebe, dann habe ich etwas geändert und du musst die Quelldateien auf Änderungen untersuchen und dies zur Kenntnis nehmen.

## Chronik

- [Datum eintragen] Neue Regel zur Synchronisation bei "sync" ergänzt.
- [2024-12-19] Neustart der AI-Sitzung: RULES.md Datei erstellt mit allen wichtigen Entwicklungsregeln. Orientierung am Projekt: IoT-Steuerungssystem mit ThingsBoard Edge Server für Sensorikdaten über RS485 und GPS. Aktueller Code ist `h2o.py` (Version 2.58).
- [2024-12-19] OutletFlap Variable Refactoring: `outletFlapRemoteLocal` umbenannt zu `outletFlapIsInRemoteMode`. Variable aus `shared_attributes_keys` entfernt (nur noch read-only), bleibt aber in `telemetry_keys` für Datenübertragung an ThingsBoard.
- [2024-12-19] OutletFlap Command Vereinfachung: Development Version erhöht auf 2.59. `set_remote_mode()` und `set_local_mode()` zu einer einzigen Funktion `setRemoteOrLocalMode(newMode)` zusammengefasst. Shared Attributes `outletFlapSetRemoteMode` und `outletFlapSetLocalMode` ersetzt durch ein einzelnes `outletFlapIsRemoteMode` (boolean). 