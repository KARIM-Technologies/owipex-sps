#!/bin/bash

# Erstellen des SSH-Startup-Skripts
SSH_TUNNEL_SCRIPT="/usr/local/bin/start_ssh_tunnel.sh"

cat << EOF > "$SSH_TUNNEL_SCRIPT"
#!/bin/bash
# SSH Reverse Tunnel einrichten
ssh -fN -R 10003:localhost:22 ssh@portal.owipex.io
EOF

# Ausführungsrechte für das Skript setzen
chmod +x "$SSH_TUNNEL_SCRIPT"

# Erstellen der systemd Service-Datei
SYSTEMD_SERVICE_FILE="/etc/systemd/system/ssh_tunnel.service"

cat << EOF > "$SYSTEMD_SERVICE_FILE"
[Unit]
Description=Start SSH Tunnel at boot

[Service]
ExecStart=$SSH_TUNNEL_SCRIPT

[Install]
WantedBy=multi-user.target
EOF

# Aktivieren und Starten des systemd Service
systemctl enable ssh_tunnel.service
systemctl start ssh_tunnel.service

echo "SSH Reverse Tunnel Service wurde eingerichtet und gestartet."
