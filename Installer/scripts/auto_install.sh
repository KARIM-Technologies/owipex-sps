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
sudo apt install dkms 

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

#5.2 Zeitserver Sync
apt install ntp -y

echo "Alle Bibliotheken wurden erfolgreich installiert!"
