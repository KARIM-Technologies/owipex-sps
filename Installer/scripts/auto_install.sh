# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: UPBOard Installer Script V0.6
# Description: Installer script for upboard pro2 
# -----------------------------------------------------------------------------

#!/bin/bash

# Überprüfen, ob das Skript als root ausgeführt wird
if [ "$EUID" -ne 0 ]
  then echo "Bitte führen Sie das Skript als Root aus."
  exit
fi

# 4.1 PIP3 Installieren
apt update
apt install python3-pip -y

# installer GPIO Driver
sudo apt install dkms -y

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

pip3 install python-dotenv

# 4.9 thingsboard libary installieren
pip3 install tb-mqtt-client

pip3 install tqdm

#python GPIO Libary
pip3 install python-periphery

pip3 install pynmea2

#InstallGPS Driver
sudo apt install gpsd gpsd-clients -y

sudo apt install python3-gps -y

sudo gpsd /dev/ttyACM0 -F /var/run/gpsd.sock

# DEVICES-Einstellung aktualisieren
sudo sed -i 's|DEVICES=".*"|DEVICES="/dev/ttyACM0"|' /etc/default/gpsd

# START_DAEMON auf "true" setzen, falls es nicht bereits gesetzt ist
sudo sed -i 's|START_DAEMON="false"|START_DAEMON="true"|' /etc/default/gpsd

# gpsd neu starten, um Änderungen zu übernehmen

echo "Alle Bibliotheken wurden erfolgreich installiert!"
