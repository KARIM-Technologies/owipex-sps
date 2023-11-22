#!/bin/bash

# Überprüfen, ob das Skript als root ausgeführt wird
if [ "$EUID" -ne 0 ]; then
    echo "Bitte führen Sie das Skript als root aus."
    exit 1
fi

# Erstellen der systemd-Service-Datei
cat <<EOL > /etc/systemd/system/chromium-root.service
[Unit]
Description=Start Chromium as root

[Service]
ExecStart=/usr/bin/chromium --no-sandbox
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOL

# Aktivieren des systemd-Service
systemctl enable chromium-root.service

# Starten des systemd-Service
systemctl start chromium-root.service

# Überprüfen des Status des systemd-Service
echo "Überprüfen des Status von chromium-root.service:"
systemctl status chromium-root.service
