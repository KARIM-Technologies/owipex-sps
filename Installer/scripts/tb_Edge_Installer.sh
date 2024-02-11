#!/bin/bash

# Schritt 0: Vorinstallation erforderlicher Bibliotheken/Tools
echo "Installiere erforderliche Tools..."
sudo apt update
sudo apt install -y wget curl git

# Schritt 1: Installiere Java 11
echo "Installiere OpenJDK 11..."
sudo apt install -y openjdk-11-jdk
sudo update-alternatives --config java

# Schritt 2: Installiere PostgreSQL
echo "Installiere PostgreSQL..."
sudo apt install -y wget
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
echo "deb https://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" | sudo tee  /etc/apt/sources.list.d/pgdg.list
sudo apt update
sudo apt -y install postgresql-15
sudo service postgresql start

# Setze das PostgreSQL-Passwort
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'OW!P3X?';"

# Erstelle ThingsBoard Edge DB
sudo su - postgres -c "psql -c \"CREATE DATABASE owipex_db;\""

# Schritt 3: ThingsBoard Edge Service Installation
echo "Lade ThingsBoard Edge herunter und installiere es..."
wget https://mega.nz/file/VS8lkTQZ#JRC0JjhCu5zn6d5kkMM0U9uEz8D2Bmg6kV0GxNImNmc
sudo dpkg -i tb-edge.deb

# Schritt 4: Konfiguriere ThingsBoard Edge
# Diese Schritte müssen basierend auf Ihrer spezifischen Konfiguration angepasst werden
echo "Aktualisiere die ThingsBoard Edge-Konfiguration..."
sudo nano /etc/tb-edge/conf/tb-edge.conf

# Schritt 5: Führe das Installationsskript aus und starte den ThingsBoard Edge-Dienst neu
echo "Führe das Installationsskript aus..."
sudo /usr/share/tb-edge/bin/install/install.sh

echo "Starte den ThingsBoard Edge-Dienst neu..."
sudo service tb-edge restart

echo "Installation abgeschlossen. ThingsBoard Edge läuft nun."
