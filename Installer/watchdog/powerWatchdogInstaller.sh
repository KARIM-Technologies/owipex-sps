#!/bin/bash

# Konfigurationsvariablen
SERVICE_NAME=powerWatchdog
USER=owipex_adm
WORKING_DIRECTORY=/home/owipex_adm/owipex-sps
SCRIPT_PATH=/home/owipex_adm/owipex-sps/powerWatchdog.py

# Erstellen der Systemd-Service-Datei
echo "Erstelle Systemd-Service-Datei für $SERVICE_NAME..."
cat <<EOF | sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null
[Unit]
Description=Power Watchdog Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$WORKING_DIRECTORY
ExecStart=/usr/bin/python3 $SCRIPT_PATH
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Systemd informieren, dass eine neue Service-Datei vorhanden ist
echo "Lade Systemd-Konfiguration neu..."
sudo systemctl daemon-reload

# Den Service aktivieren, damit er beim Systemstart ausgeführt wird
echo "Aktiviere $SERVICE_NAME Service..."
sudo systemctl enable $SERVICE_NAME.service

# Den Service starten
echo "Starte $SERVICE_NAME Service..."
sudo systemctl start $SERVICE_NAME.service

echo "$SERVICE_NAME Service erfolgreich eingerichtet und gestartet."
