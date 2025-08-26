# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: DTI-1 Flow Sensor Test Script
# Description: Beispiel zur Verwendung des DTI-1 Flow-Sensors mit der Modbus-Bibliothek
# -----------------------------------------------------------------------------

# Dieses Skript demonstriert die Verwendung des DTI-1 Flow-Sensors mit der 
# erweiterten Modbus-Bibliothek von KARIM Technologies.

import sys
import os

# Dynamisch den Pfad zum Hauptverzeichnis ermitteln
# Der Import funktioniert unabhängig davon, von wo das Skript aufgerufen wird
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../../"))
sys.path.append(project_root)

import time
from libs.modbus_lib import DeviceManager

print(f"Projektpfad: {project_root}")
print(f"Systempfade: {sys.path}")

# Create DeviceManager
dev_manager = DeviceManager(port='/dev/ttyS0', baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=1)

# Device-ID für den DTI-1 Flow-Sensor (0x28 = 40 dezimal)
DTI1_DEVICE_ID = 0x28

# Gerät zum DeviceManager hinzufügen
dev_manager.add_device(device_id=DTI1_DEVICE_ID)

# Referenz auf das Gerät erhalten
dti1_sensor = dev_manager.get_device(device_id=DTI1_DEVICE_ID)

def test_dti1_sensor():
    print("DTI-1 Flow-Sensor Test gestartet...")
    print("-" * 50)

    # 1. Durchflussrate lesen (m³/h)
    try:
        flow_rate = dti1_sensor.read_flow_rate_m3ph()
        print(f"Aktueller Durchfluss: {flow_rate:.3f} m³/h")
    except Exception as e:
        print(f"Fehler beim Lesen der Durchflussrate: {e}")

    # 2. Gesamtmenge lesen 
    try:
        total_flow, unit = dti1_sensor.read_totalizer_m3()
        print(f"Gesamterfasste Menge: {total_flow:.3f} {unit}")
    except Exception as e:
        print(f"Fehler beim Lesen der Gesamtmenge: {e}")

    # 3. Kontinuierliche Messung (optional)
    print("\nKontinuierliche Messung für 10 Sekunden (alle 2 Sekunden)...")
    end_time = time.time() + 10
    
    try:
        while time.time() < end_time:
            flow_rate = dti1_sensor.read_flow_rate_m3ph()
            total_flow, unit = dti1_sensor.read_totalizer_m3()
            
            print(f"Durchfluss: {flow_rate:.3f} m³/h | Gesamt: {total_flow:.3f} {unit}")
            time.sleep(2)
    except KeyboardInterrupt:
        print("Messung durch Benutzer unterbrochen.")
    except Exception as e:
        print(f"Fehler während der kontinuierlichen Messung: {e}")

    print("-" * 50)
    print("DTI-1 Flow-Sensor Test beendet.")

if __name__ == "__main__":
    test_dti1_sensor() 