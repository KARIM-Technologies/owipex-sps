# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: GPS Data Library V0.1
# Description: Library to fetch and process GPS data
# -----------------------------------------------------------------------------

import gpsd
import time

# Verbindet mit dem lokalen gpsd
gpsd.connect()

def get_gps_data(timeout=10):
    start_time = time.time()
    while time.time() - start_time <= timeout:
        try:
            packet = gpsd.get_current()
            if packet.mode >= 2:  # Mode 2 bedeutet 2D-Fix, was mindestens Längen- und Breitengrad bedeutet.
                return packet
        except Exception as e:
            print(f"Fehler beim Abrufen der GPS-Daten: {e}")
            time.sleep(1)  # Kurze Pause, um eine Endlosschleife bei sofortigem Fehler zu vermeiden
    return None

def process_gps_data(packet):
    if packet is not None:
        timestamp = packet.time  # Zeitstempel der GPS-Daten
        latitude, longitude = packet.position()  # Breiten- und Längengrad
        altitude = packet.alt if packet.mode == 3 else None  # Höhe (wenn verfügbar)
        return timestamp, latitude, longitude, altitude
    else:
        return None, None, None, None

def fetch_and_process_gps_data(timeout=10):
    # Abrufen der GPS-Daten
    gps_packet = get_gps_data(timeout)
    # Verarbeiten der abgerufenen GPS-Daten und Speichern der Ergebnisse in Variablen
    return process_gps_data(gps_packet)

# Hauptprogramm
if __name__ == "__main__":
    print("Abrufen und Verarbeiten von GPS-Daten...")
    timestamp, latitude, longitude, altitude = fetch_and_process_gps_data()
    if timestamp is not None:
        print(f"Zeitstempel: {timestamp}")
        print(f"Position: Breitengrad {latitude}, Längengrad {longitude}")
        if altitude is not None:
            print(f"Höhe: {altitude} Meter")
    else:
        print("Keine GPS-Daten innerhalb des Zeitlimits erhalten.")
