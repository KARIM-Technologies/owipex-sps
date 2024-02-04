import serial
import time
import string
import pynmea2

# Hinweis: Pfad zum GPS-Modul korrigiert
port = "/dev/ttyACM0"
ser = serial.Serial(port, baudrate=9600, timeout=0.5)
print(f"Öffne den Serial Port: {port}")

dataout = pynmea2.NMEAStreamReader()
print("NMEA Stream Reader initialisiert.")

while True:
    newdata = ser.readline()
    
    # Debug: Ausgabe der rohen Daten
    if newdata:
        print(f"Rohdaten empfangen: {newdata}")

    if newdata[0:6] == b"$GPRMC":
        try:
            newmsg = pynmea2.parse(newdata.decode('ascii'))
            lat = newmsg.latitude
            lng = newmsg.longitude
            gps = f"Latitude={lat} and Longitude={lng}"
            print(gps)
        except pynmea2.ParseError as e:
            print(f"Parse Error: {e}")
        except Exception as e:
            print(f"Unbekannter Fehler: {e}")
    else:
        print("Keine GPRMC Daten empfangen.")
    
    # Warten, um die Ausgabe zu verlangsamen und den Prozessor zu entlasten
    time.sleep(1)
