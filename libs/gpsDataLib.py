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
            # Mode 2 bedeutet 2D-Fix, was mindestens Längen- und Breitengrad bedeutet.
            if packet.mode >= 2:
                return packet, gpsd.get_satellites()
        except Exception as e:
            print(f"Fehler beim Abrufen der GPS-Daten: {e}")
            time.sleep(1)  # Kurze Pause, um eine Endlosschleife bei sofortigem Fehler zu vermeiden
    return None, None

def fetch_and_process_gps_data(timeout=10):
    timestamp, latitude, longitude, height, nbOfSatellites = None, 0.0, 0.0, 0.0, 0
    
    # Abrufen der GPS-Daten
    gps_packet, satelliteData = get_gps_data(timeout)
    # Verarbeiten der abgerufenen GPS-Daten und Speichern der Ergebnisse in Variablen
    if gps_packet is not None:
        timestamp = packet.time  # Zeitstempel der GPS-Daten
        latitude, longitude = packet.position()  # Breiten- und Längengrad
        altitude = packet.alt if packet.mode == 3 else None  # Höhe (wenn verfügbar)
    # Verarbeiten der Satellitendaten
    if satelliteData is not None:
        nbOfSatellites = [s for s in satelliteData if s.used]

    return timestamp, latitude, longitude, altitude, nbOfSatellites
