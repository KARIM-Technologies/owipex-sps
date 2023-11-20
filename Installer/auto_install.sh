#!/bin/bash

# Überprüfen, ob das Skript als root ausgeführt wird
if [ "$EUID" -ne 0 ]
  then echo "Bitte führen Sie das Skript als Root aus."
  exit
fi

# 5.1 User owipex_usr hinzufügen
adduser owipex_usr

# 5.2 User in Sudoer List hinzufügen
usermod -aG sudo owipex_usr

# 4.1 PIP3 Installieren
apt update
apt install python3-pip -y

# ONBOARD Tastatur installieren
apt install onboard -y

# 4.1.1 PIP3 upgraden
python3 -m pip install --upgrade pip

# 4.2 GPSD Python3 Libary Installieren
pip3 install gpsd-py3

# 4.3 mmh3 Libary installieren
pip3 install mmh3

# 4.4 pymmh3 installieren
pip3 install pymmh3

# 4.5 pyserial libary installieren
pip3 install pyserial

# 4.6 crcmod installieren
pip3 install crcmod

# 4.7 numpy installieren
pip3 install numpy

# 4.8 scipy installieren
python3 -m pip install scipy

# 4.9 thingsboard libary installieren
pip3 install tb-mqtt-client

# 5.0 flask installieren
pip3 install flask

# 5.1 flask installieren
apt install sudo -y

# 5.1 flask installieren
apt install onboard -y

# Alte SSH-Hostschlüssel entfernen und neue generieren
rm /etc/ssh/ssh_host_*
dpkg-reconfigure openssh-server

# SSHD-Konfigurationsdatei bearbeiten
sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# SSH-Dienst neu starten
systemctl restart sshd

# Sprache konfigurieren
echo "Bitte wählen Sie die gewünschten Sprachen aus der Liste aus."
dpkg-reconfigure locales

echo "Alle Bibliotheken wurden erfolgreich installiert!"
