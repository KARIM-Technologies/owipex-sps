#!/bin/bash

# Überprüfen, ob das Skript als root ausgeführt wird
if [ "$EUID" -ne 0 ]
  then echo "Bitte führen Sie das Skript als Root aus."
  exit
fi

# Sprachpakete installieren
apt update
apt install locales -y

# Sprache konfigurieren
echo "Bitte wählen Sie die gewünschten Sprachen aus der Liste aus."
dpkg-reconfigure locales

# Benutzer nach der gewünschten Standardsprache fragen
read -p "Bitte geben Sie die gewünschte Standardsprache ein (z.B. de_DE.UTF-8): " LANG_CHOICE
export LANG=$LANG_CHOICE
export LANGUAGE=${LANG_CHOICE%.*}:${LANG_CHOICE%_*}

# Tastaturlayout ändern (optional)
read -p "Möchten Sie das Tastaturlayout ändern? (j/n): " KEYBOARD_CHOICE
if [ "$KEYBOARD_CHOICE" = "j" ]; then
    dpkg-reconfigure keyboard-configuration
fi

echo "Sprache und Tastaturlayout wurden erfolgreich konfiguriert!"
