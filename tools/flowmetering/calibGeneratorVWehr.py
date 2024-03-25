import math
import json

def erzeuge_kalibrierdatei():
    # Schritt 1: Nullpunkt erfassen (Beispielwert: 281)
    zero_point = float(input("Bitte geben Sie den Nullpunkt ein (z.B. 281): "))
    
    # Schritt 2: Maximale Höhe in mm erfassen (Beispielwert: 1000)
    max_hoehe_mm = float(input("Bitte geben Sie die maximale Höhe in mm ein (z.B. 1000): "))
    
    # Schritt 3: Anzahl der Kalibrierpunkte erfassen (Beispielwert: 10)
    anzahl_kalibrierpunkte = int(input("Bitte geben Sie die Anzahl der Kalibrierpunkte ein (z.B. 10): "))
    
    # Schritt 4: Beiwert C erfassen (Standardwertebereich: 1.4 - 1.6, Beispielwert: 1.5)
    C = float(input("Bitte geben Sie den Beiwert C ein (Standardwertebereich: 1.4 - 1.6, z.B. 1.5): "))
    
    # Schritt 5: Winkel theta in Grad erfassen (Beispielwert: 90)
    theta = float(input("Bitte geben Sie den Winkel Theta in Grad ein (z.B. 90): "))
    
    # Umrechnung des Winkels in Radiant für mathematische Funktionen
    theta_rad = math.radians(theta)
    
    # Berechnung der Wasserhöhen basierend auf der maximalen Höhe und der Anzahl der Kalibrierpunkte
    hoehe_schritte = max_hoehe_mm / (anzahl_kalibrierpunkte - 1)
    wasser_hoehen_mm = [round(hoehe_schritte * i) for i in range(anzahl_kalibrierpunkte)]
    
    kalibrierdaten = [{"zero_point": zero_point}]
    
    # Durchflussraten für berechnete Wasserhöhen erfassen und in l/s umrechnen, dann auf zwei Dezimalstellen runden
    for H_mm in wasser_hoehen_mm:
        H_m = H_mm / 1000  # Umrechnung von mm in m
        flow_rate_m3_s = C * math.tan(theta_rad / 2) * H_m**2.5
        flow_rate_l_s = round(flow_rate_m3_s * 1000, 2)  # Umrechnung von m³/s in l/s und Runden auf zwei Dezimalstellen
        kalibrierdaten.append({"water_height_mm": H_mm, "flow_rate_l_s": flow_rate_l_s})
    
    # Kalibrierdaten in JSON-Format konvertieren
    kalibrierdatei_json = json.dumps(kalibrierdaten, indent=2)
    print("\nErzeugte Kalibrierdaten:")
    print(kalibrierdatei_json)
    
    # Optional: Kalibrierdatei speichern
    with open('kalibrierdatei.json', 'w') as file:
        file.write(kalibrierdatei_json)

# Zum Testen in einer lokalen Python-Umgebung den folgenden Aufruf aktivieren:
erzeuge_kalibrierdatei()
