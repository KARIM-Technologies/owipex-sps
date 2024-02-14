#!/bin/bash

# Service-Datei erstellen
echo "[Unit]
Description=H2O Watchdog Service
After=network.target

[Service]
Type=simple
User=owipex_adm
WorkingDirectory=/home/owipex_adm/owipex-sps
ExecStart=/usr/bin/python3 /home/owipex_adm/owipex-sps/watchdog.py
Restart=on-failure

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/h2o_watchdog.service

# Berechtigungen setzen
sudo chmod 644 /etc/systemd/system/h2o_watchdog.service

# Systemd neu laden, um die Änderungen zu erkennen
sudo systemctl daemon-reload

# Service aktivieren, damit er beim Booten startet
sudo systemctl enable h2o_watchdog.service

# Service starten
sudo systemctl start h2o_watchdog.service

# Status des Service überprüfen
sudo systemctl status h2o_watchdog.service
