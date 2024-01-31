#!/bin/bash

# Überprüfen, ob das Skript als root ausgeführt wird
if [ "$EUID" -ne 0 ]
  then echo "Bitte führen Sie das Skript als Root aus."
  exit
fi

# Alte SSH-Hostschlüssel entfernen und neue generieren
rm /etc/ssh/ssh_host_*
dpkg-reconfigure openssh-server

# SSHD-Konfigurationsdatei bearbeiten
sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# SSH-Dienst neu starten
systemctl restart sshd

echo "SSH wurde erfolgreich konfiguriert!"
