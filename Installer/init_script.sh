#!/bin/bash

# Verzeichnis, in dem sich Ihre Installations-Skripte befinden
SCRIPT_DIR="/home/OWIPEX_V1.0/installer/scripts"

# Logdatei für die Installationsergebnisse
LOGFILE="/home/OWIPEX_V1.0/installer/logfile.txt"

# Iterieren über jedes .sh-Skript im Verzeichnis
for script in "$SCRIPT_DIR"/*.sh; do
    echo "Mache Skript ausführbar: $script" | tee -a "$LOGFILE"
    chmod +x "$script"

    echo "Starte Installationsskript: $script" | tee -a "$LOGFILE"
    bash "$script" | tee -a "$LOGFILE" && echo "Installation von $script erfolgreich abgeschlossen." | tee -a "$LOGFILE" || echo "Fehler bei der Installation von $script." | tee -a "$LOGFILE"
done

echo "Alle Installationsskripte wurden ausgeführt." | tee -a "$LOGFILE"
