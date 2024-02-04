# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: FlowCalculation
# Version: 1.6
# Description: Dieses Modul enthält die FlowCalculation-Klasse, die die Methode 
# zur Berechnung der Durchflussrate basierend auf den Kalibrierungsdaten bereitstellt.
# Es werden Werte in "mm" für die Eingaben akzeptiert und die Ausgabe kann in l/min, 
# l/h, m3/min und m3/h erfolgen.
# -----------------------------------------------------------------------------

import math
import json
from scipy.interpolate import interp1d

class FlowCalculation:
    def __init__(self, calibration_file):
        self.g = 9.81  # gravitational constant, m/s^2
        self.load_calibration_data(calibration_file)
        self.total_volume = 0.0  # Initialisiert die Variable für die Gesamtdurchflussmenge

    def load_calibration_data(self, calibration_file):
        with open(calibration_file, 'r') as f:
            calibration_data = json.load(f)
        self.zero_reference = calibration_data[0]['zero_point']
        calibration_data = calibration_data[1:]
        x_data = [entry['water_height'] for entry in calibration_data]
        y_data = [entry['flow_rate'] for entry in calibration_data]
        self.calibration_function = interp1d(x_data, y_data, fill_value="extrapolate")

    def calculate_flow_rate(self, water_level):
        water_level /= 1000  # Konvertiert mm in m
        flow_rate = self.calibration_function(water_level)  # Berechnet die Durchflussrate in m3/h
        if flow_rate < 0:
            flow_rate = 0.0
        self.total_volume += flow_rate / 60  # Aktualisiert die Gesamtdurchflussmenge (angenommen stündliche Aktualisierung)
        return flow_rate
    
    def get_zero_reference(self):
        return self.zero_reference

    def save_total_volume_to_file(self, file_path="total_volume.txt"):
        """Speichert die gesamte Durchflussmenge in einer Datei."""
        with open(file_path, 'w') as file:
            file.write(str(self.total_volume))

    def load_total_volume_from_file(self, file_path="total_volume.txt"):
        """Lädt die gespeicherte Gesamtdurchflussmenge aus einer Datei."""
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                stored_volume = file.read()
                self.total_volume = float(stored_volume) if stored_volume else 0.0
        else:
            self.total_volume = 0.0

    def reset_total_volume(self, file_path="total_volume.txt"):
        """Setzt die gespeicherte Gesamtdurchflussmenge zurück und aktualisiert die Datei."""
        self.total_volume = 0.0
        self.save_total_volume_to_file(file_path)

    def convert_to_liters_per_minute(self, flow_rate):
        return flow_rate * 1000 / 60  # Konvertiert m3/h in l/min

    def convert_to_liters_per_hour(self, flow_rate):
        return flow_rate * 1000  # Konvertiert m3/h in l/h

    def convert_to_cubic_meters_per_minute(self, flow_rate):
        return flow_rate / 60  # Konvertiert m3/h in m3/min

    def convert_to_cubic_meters_per_hour(self, flow_rate):
        return flow_rate  # Bereits in m3/h
