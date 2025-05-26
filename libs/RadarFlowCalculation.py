import math
import json
from scipy.interpolate import interp1d

class RadarFlowCalculation:
    def __init__(self, calibration_file):
        self.load_calibration_data(calibration_file)

    def load_calibration_data(self, calibration_file):
        with open(calibration_file, 'r') as f:
            calibration_data = json.load(f)
        self.zero_reference = calibration_data[0]['zero_point']  # store zero reference

        # Exclude zero point entry from the calibration data
        calibration_data = calibration_data[1:]

        # Extract data from the dictionaries
        x_data = [entry['water_height'] for entry in calibration_data]  # in mm
        y_data = [entry['flow_rate'] for entry in calibration_data]  # in L/s

        # Interpolation function using the calibration data
        self.calibration_function = interp1d(x_data, y_data, fill_value="extrapolate")
    
    def calculate_flow_rate(self, water_level):
        return self.calibration_function(water_level)  # flow rate in L/s


    def get_zero_reference(self):
        return self.zero_reference

    # Convert flow rate from L/s to different units
    def convert_to_liters_per_minute(self, flow_rate):
        return flow_rate * 60  # convert L/s to l/min

    def convert_to_liters_per_hour(self, flow_rate):
        return flow_rate * 3600  # convert L/s to l/h

    def convert_to_cubic_meters_per_minute(self, flow_rate):
        return (flow_rate / 1000) * 60  # convert L/s to m3/min

    def convert_to_cubic_meters_per_hour(self, flow_rate):
        return (flow_rate / 1000) * 3600  # convert L/s to m3/h
