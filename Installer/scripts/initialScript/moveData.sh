#!/bin/bash

# Definiere den Zielordner
TARGET_DIR="/etc/owipex"
SOURCE_DIR="/home/owipex_adm/owipex-sps"

# Liste der Dateien, die verschoben werden sollen
FILES_TO_MOVE="calibration_data.json state.json run_time.txt total_flow.json ph_calibration.json"

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
