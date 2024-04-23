#!/bin/bash

# Setze das Timeout für systemd-networkd-wait-online
TIMEOUT="1s"  # Setze das Timeout hier auf den gewünschten Wert

# Pfad zur systemd Service-Datei
SERVICE_FILE="/lib/systemd/system/systemd-networkd-wait-online.service"

# Backup der originalen Service-Datei erstellen
sudo cp "$SERVICE_FILE" "$SERVICE_FILE.bak"

# Timeout-Wert ändern
sudo sed -i "/ExecStart=/c\ExecStart=/lib/systemd/systemd-networkd-wait-online --timeout=$TIMEOUT" "$SERVICE_FILE"

# Systemd neu laden, um Änderungen zu erkennen
sudo systemctl daemon-reload

# Dienst neu starten
sudo systemctl restart systemd-networkd-wait-online.service

echo "Die Bootzeit-Konfiguration wurde aktualisiert. Timeout gesetzt auf $TIMEOUT."
