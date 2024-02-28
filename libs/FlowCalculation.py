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

    def load_calibration_data(self, calibration_file):
        with open(calibration_file, 'r') as f:
            calibration_data = json.load(f)
        self.zero_reference = calibration_data[0]['zero_point']  # store zero reference

        # Exclude zero point entry from the calibration data
        calibration_data = calibration_data[1:]

        # Extract data from the dictionaries
        x_data = [entry['water_height'] for entry in calibration_data]
        y_data = [entry['flowRate'] for entry in calibration_data]

        self.calibration_function = interp1d(x_data, y_data, fill_value="extrapolate")
    
    def calculate_flow_rate(self, water_level):
        water_level /= 1000  # convert mm to m
        return self.calibration_function(water_level)  # flow rate in m3/h

    def get_zero_reference(self):
        return self.zero_reference

    # Convert flow rate to different units
    def convert_to_liters_per_minute(self, flow_rate):
        return flow_rate * 1000 / 60  # convert m3/h to l/min

    def convert_to_liters_per_hour(self, flow_rate):
        return flow_rate * 1000  # convert m3/h to l/h

    def convert_to_cubic_meters_per_minute(self, flow_rate):
        return flow_rate / 60  # convert m3/h to m3/min

    def convert_to_cubic_meters_per_hour(self, flow_rate):
        return flow_rate  # already in m3/h
