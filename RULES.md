# RULES.md - Wichtige Entwicklungsregeln

## Kommunikation und Sprache
- Wir kommunizieren miteinander in Deutsch
- Kommentare im Code sowie die Dokumentation soll auf Englisch sein

## Dateiverwaltung
- Alles was wir besprechen soll in HISTORY.md gespeichert werden
- Diese Datei sollst du regelmäßig ergänzen und bei Beginn einer neuen Sitzung dir anschauen
- Du sollst die HISTORY.md bei Beginn jeder Sitzung durchlesen und dich auf den neuesten Stand bringen
- Speichere den Chat-Verlauf in einer Datei CHAT.md, an welche du immer wieder anhängst

## Änderungsrichtlinien  
- Du darfst keine Änderungen machen, die wir nicht vorher besprochen haben. Wenn du unsicher bist, frage mich
- Du darfst beim Programmieren niemals Vererbungen ändern, ohne Rücksprache mit mir
- Bei Build-Fehlern darfst du niemals einfach Features oder Funktionalitäten entfernen, ohne vorher zu fragen
- Du musst dir genau merken, was wir besprechen und darf niemals Änderungen rückgängig machen, nur weil du vergessen hast, dass etwas anders sein soll. Besprechungen haben Vorrang vor Standard-Konventionen
- Lieber zu viel beim User nachfragen als zu wenig

## Programmierkonventionen
- Für globale Variablen Pascal-Case
- Für lokale Variablen und Funktionsparameter camelCase  
- Für Konstanten ausschließlich Großbuchstaben wobei die Silben eines Wortes mit Unterstrichen getrennt werden
- Wenn ein Verzeichnis namens "Doku" vorhanden ist, können sich dort .md-Dateien befinden. Lese diese, hier ist der Aufbau unseres Programmpakets beschrieben

## Versionierung
- Für ausführbare Dateien und Projekte gilt: Versionsnummern haben die Form "1.1"
- Beachte, dass nach "1.9" nicht "2.1" folgen soll, sondern "1.10"
- Der erste Teil der Nummer soll nicht automatisch inkrementiert werden
- Der zweite Teil nur dann (außer mit C#), wenn ich dir den Befehl "incvers" erteile
- Für ausführbare Dateien soll die Variable "ProgVers" heißen
- Für Libraries soll die Variable "LibVers" heißen

## C# spezifische Regeln (falls verwendet)
- Falls C# als Programmiersprache verwendet werden soll, verwende die Version .NET 8.0
- Inkrementiere vor jedem build den zweiten Teil der Versionsnummer automatisch
- Beim Build immer die Variante "self-contained" benutzen
- Lagere den Programmcode von ReactiveCommands (AddCommand, DivideCommand usw.) immer in eine eigene Methode aus
- Bindings müssen die gesamte Property übernehmen und können nicht mit statischem Text gemischt werden
- Wenn man Label + Binding braucht, verwendet man zwei separate Controls
- In Views muss der DataContext immer das zugehörige VM sein, die Variable x:DataType muss auf die Instanz des VM zeigen
- Analoges gilt für Windows mit WM (WindowsModel)
- Wenn eine View (UserControl) einen eigenen DataContext definiert, muss die IsVisible-Property auf einen umschließenden Border angewendet werden
- Für Namespaces: wir ignorieren die Ordnerstruktur und verwenden einfache Namespaces. Wenn ein Namespace wie eine unserer Klassen heißen würde, wird "Ns" hinter den Namespace-Namen gesetzt

## GUI-Design
- Bei Tables soll zwischen 2 Spalten (und auch zwischen 2 Zeilen) eine weitere Spalte/Zeile als Abstand eingefügt werden
- Beispiel: Name1/Value1, Name2/Value2 → Tabelle mit 3 Zeilen und 3 Spalten

## Dependencies und Module
- Bevor du, egal ob in C# oder Python, irgendwelche Module oder Libraries verwendest (außer den Standard .NET-Libraries), frage mich vorher

## Git und Workflow
- Frage mich nicht ob wir committen sollen, das stört. Ich gebe dir selbst bescheid, wenn dies gemacht werden soll
- Falls du unter Windows arbeitest, darfst du deine Befehle (z.B. für git) nicht mit "&&" verketten, da Windows bzw. PowerShell hier Probleme macht

## Spezielle Befehle
- Wenn ich "..." schreibe, dann deuten die Punkte auf eine rechtsverkürzte Suche hin
- Wenn ich "sync" eingebe, dann habe ich etwas geändert und du musst die Quelldateien auf Änderungen untersuchen
- Wenn ich "commit xxxx" eingebe, dann sollst du einen git commit machen mit der Message xxxx
- Wenn ich "push" eingebe, dann sollst du einen git push machen  
- Wenn ich "commdasi" eingebe, dann sollst du einen git commit mit Message "DaSi" und anschließend git push machen
- Wenn ich "incvers" eingebe, soll der zweite Teil der Versionsnummer inkrementiert werden

## Dateikonsistenz
- Es kann sein, dass Dateien parallel zu unserer Arbeit mit einem anderen Editor geändert werden
- Du sollst darauf aufpassen, Änderungen automatisch nachladen und dich aktualisieren bzw. neu orientieren
- Gebe bei Meldungen über Quellcode oder HTML immer die Zeilennummer mit aus

## Sicherheit
- Daten, die du hier über unsere Arbeit erfährst, dürfen auf keinen Fall weitergegeben werden! 