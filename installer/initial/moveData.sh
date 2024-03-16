#!/bin/bash

# Definiere den Zielordner
TARGET_DIR="/etc/owipex"
SOURCE_DIR="/home/owipex_adm/owipex-sps/src"

# Liste der Dateien, die verschoben werden sollen
FILES_TO_MOVE="calibration_data.json run_time.txt total_flow.json"

# Überprüfe, ob das Skript als Root ausgeführt wird
if [ "$(id -u)" != "0" ]; then
  echo "Dieses Skript muss als Root ausgeführt werden." 1>&2
  exit 1
fi

# Erstelle den Zielordner, falls er nicht existiert
if [ ! -d "$TARGET_DIR" ]; then
  mkdir -p "$TARGET_DIR"
  echo "Verzeichnis $TARGET_DIR erstellt."
fi

# Ändere den Eigentümer des Verzeichnisses zu owipex_adm
chown owipex_adm:owipex_adm "$TARGET_DIR"

# Füge thingsboard_gateway zur Gruppe owipex_adm hinzu
usermod -aG owipex_adm thingsboard_gateway

# Ändere Berechtigungen, um Gruppen-Lese- und Ausführungsrechte zu gewähren
chmod g+rx /home/owipex_adm

# Verschiebe die definierten Dateien
for file in $FILES_TO_MOVE; do
  if [ -f "$SOURCE_DIR/$file" ]; then
    mv "$SOURCE_DIR/$file" "$TARGET_DIR"
    echo "$file wurde nach $TARGET_DIR verschoben."
  else
    echo "Warnung: $file existiert nicht im Quellverzeichnis $SOURCE_DIR und wurde nicht verschoben."
  fi
done

echo "Setup abgeschlossen."
