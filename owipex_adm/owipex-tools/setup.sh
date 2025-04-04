#!/bin/bash

# Setze den Pfad zu deinem Projektverzeichnis
PROJECT_DIR="/home/owipex_adm/owipex-tools"

# Erstelle eine virtuelle Umgebung
python3 -m venv $PROJECT_DIR/venv

# Aktiviere die virtuelle Umgebung
source $PROJECT_DIR/venv/bin/activate

# Installiere die notwendigen Bibliotheken
pip install Flask Flask-Login markupsafe==2.0.1

# Deaktiviere die virtuelle Umgebung
deactivate

# Erstelle die Service-Datei mit sudo-Berechtigungen
SERVICE_FILE="/etc/systemd/system/owipex-tools.service"
sudo bash -c "echo '[Unit]
Description=OWIPEX Tools Service
After=network.target

[Service]
User=owipex_adm
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/app.py
Restart=always

[Install]
WantedBy=multi-user.target' > $SERVICE_FILE"

# Setze die richtigen Berechtigungen für die Service-Datei
sudo chmod 644 $SERVICE_FILE

# Lade die neuen Systemd-Dienste
sudo systemctl daemon-reload

# Aktiviere den Service beim Booten
sudo systemctl enable owipex-tools.service

# Starte den Service
sudo systemctl start owipex-tools.service

echo "Setup completed successfully."
