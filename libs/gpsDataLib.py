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

                for p in packet.json['raw']:
                if p.get('class') == 'SKY':
                    sats = p.get('satellites', [])
                    if sats is not None:
                        used = [s for s in sats if s.get('used')]
                        nbOfSatellites = len(used)
                        print(f"get_gps_data(): Verwendete Satelliten: {nbOfSatellites}")
                    else
                        nbOfSatellites = 0
                return packet, nbOfSatellites
        except Exception as e:
            print(f"Fehler beim Abrufen der GPS-Daten: {e}")
            time.sleep(1)  # Kurze Pause, um eine Endlosschleife bei sofortigem Fehler zu vermeiden
    return None, None

def fetch_and_process_gps_data(timeout=10):
    timestamp, latitude, longitude, height = None, 0.0, 0.0, 0.0
    
    # Abrufen der GPS-Daten
    gps_packet, nbOfSatellites = get_gps_data(timeout)
    # Verarbeiten der abgerufenen GPS-Daten und Speichern der Ergebnisse in Variablen
    if gps_packet is not None:
        timestamp = packet.time  # Zeitstempel der GPS-Daten
        latitude, longitude = packet.position()  # Breiten- und Längengrad
        altitude = packet.alt if packet.mode == 3 else None  # Höhe (wenn verfügbar)
    return timestamp, latitude, longitude, altitude, nbOfSatellites
