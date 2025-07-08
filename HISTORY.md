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
- [2024-12-19] Development Version auf 2.60 erhöht. OutletFlap Fallback-Werte korrigiert: `outletFlapRemoteMode`, `outletFlapLocalMode` und `outletFlapHasError` werden bei Lesefehler auf `None` gesetzt statt auf Boolean-Werte.
- [2024-12-19] Development Version auf 2.61 erhöht. Umfassendes OutletFlap-Register-Rebranding: Alle OutletFlap-Telemetrie-Variablen umbenannt mit "Register"-Präfix für bessere Erkennbarkeit in ThingsBoard. Neue Telemetrie-Werte `TelemetryTest420` und `TelemetryTestNone` hinzugefügt.
- [2024-12-19] Development Version auf 2.62 erhöht. Code-Formatierung in `config.py`: `telemetry_keys` und `shared_attributes_keys` Listen alphabetisch sortiert und auf maximal 3 Variablen pro Zeile formatiert für bessere Lesbarkeit.
- [2024-12-19] Development Version auf 2.63 erhöht (durch User). Telemetrie-Test-Variablen umbenannt: `TelemetryTest420` → `telemetryTest420`, `TelemetryTestNone` → `telemetryTestNone`. User änderte Initialwerte: `telemetryTest420 = 420`, `outletFlapRegisterIsLocalMode = False`.
- [2024-12-19] Telemetrie-Test-Variablen Korrektur: `telemetryTestNone = None` (nicht 0), beide Test-Variablen werden nur einmalig bei Initialisierung gesetzt, nicht bei jedem Schleifendurchlauf überschrieben.
- [2024-12-19] Development Version auf 2.64 erhöht. Code-Lesbarkeit verbessert: a) Variablen in config.py Blöcken alphabetisch sortiert, b) global-Statements in h2o.py main-Funktion aufgeteilt (max 4 Variablen pro Zeile, alphabetisch sortiert), c) Übersichtlichkeit deutlich erhöht.
- [2024-12-19] **AI-Neustart und Git-Bereinigung**: AI wurde neu gestartet, Orientierung an RULES.md und HISTORY.md erfolgreich. Aktueller Code-Stand: h2o.py Version 2.68. User löschte ungenutzte .txt Dateien (hk.txt, hk100.txt, hkallvalues.txt), Git-Commit 951016d erfolgreich durchgeführt. CHAT.md Dokumentationsdatei erstellt für künftige Chat-Protokollierung.
- [2024-12-19] Development Version auf 2.69 erhöht. **Telemetry Keys Vollständigkeit**: Alle 15 fehlenden `shared_attributes_keys` zu `telemetry_keys` hinzugefügt (callGpsSwitch, gemessener_high_wert, gemessener_low_wert, isDebugMode, minimumPHValStop, outletFlapIsRemoteMode, ph_intercept, ph_slope, PHValueOffset, radarSensorActive, targetPHtolerrance, targetPHValue, turbidity2Offset, turbidityOffset, useDebugReadingsIntervalls). Damit sind jetzt alle Shared Attributes auch in ThingsBoard Telemetrie sichtbar für Überwachung von Attribut-Änderungen. Liste alphabetisch sortiert, keine Duplikate. 