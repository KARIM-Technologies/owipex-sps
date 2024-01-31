#!/bin/bash

# Überprüfen, ob das Skript als root ausgeführt wird
if [ "$EUID" -ne 0 ]; then
    echo "Bitte führen Sie das Skript als root aus."
    exit 1
fi

# Erstellen der systemd-Service-Datei
cat > /etc/systemd/system/app.service <<EOL
[Unit]
Description=My Flask App
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/OWIPEX_V1.0/flask_app/app.py
WorkingDirectory=/home/OWIPEX_V1.0/flask_app/
User=root
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Systemd aktualisieren und Service starten
systemctl daemon-reload
systemctl start app.service

# Service aktivieren, damit er beim Booten automatisch gestartet wird
systemctl enable app.service

echo "Service eingerichtet und gestartet!"
