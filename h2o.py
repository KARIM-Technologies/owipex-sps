
import signal



import logging.handlers
import time
import os
import gpsDataLib
import json

from tb_gateway_mqtt import TBDeviceMqttClient
from modbus_lib import DeviceManager
from time import sleep
from FlowCalculation import FlowCalculation

ACCESS_TOKEN = "cX8xQLmWZcHPXTKzjHGC"  # Replace this with your actual access token
THINGSBOARD_SERVER = '192.168.100.26'  # Replace with your Thingsboard server address
THINGSBOARD_PORT = 1883

#RS485 Comunication and Devices
# Create DeviceManager
dev_manager = DeviceManager(port='/dev/ttymxc3', baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=1)
dev_manager.add_device(device_id=0x01)
dev_manager.add_device(device_id=0x02)
dev_manager.add_device(device_id=0x03)
# Get devices and read their registers
Radar_Sensor = dev_manager.get_device(device_id=0x01)
Trub_Sensor = dev_manager.get_device(device_id=0x02)
PH_Sensor = dev_manager.get_device(device_id=0x03)
#logging.basicConfig(level=logging.DEBUG)
client = None

#Import Global vars
from config import *
shared_attributes_keys


#Speichern des aktuellen Zustands:
def save_state(state_dict):
    with open('state.json', 'w') as file:
        json.dump(state_dict, file)

#Laden des gespeicherten Zustands:
def load_state():
    if os.path.exists('state.json'):
        with open('state.json', 'r') as file:
            return json.load(file)
    return {}

 #that will be called when the value of our Shared Attribute changes
def attribute_callback(result, _):
    globals().update({key: result[key] for key in result if key in globals()})
    state_to_save = {key: globals()[key] for key in shared_attributes_keys if key in globals()}
    save_state(state_to_save)
    print(result)

# Callback function that will be called when an RPC request is received
def rpc_callback(id, request_body):
    print(request_body)
    method = request_body.get('method')
    if method == 'getTelemetry':
        attributes, telemetry = get_data()
        client.send_attributes(attributes)
        client.send_telemetry(telemetry)
    else:
        print('Unknown method: ' + method)


def get_data():
    cpu_usage = round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline().replace('', '').replace(',', '.')), 2)
    ip_address = os.popen('''hostname -I''').readline().replace('', '').replace(',', '.')[:-1]
    mac_address = os.popen('''cat /sys/class/net/*/address''').readline().replace('', '').replace(',', '.')
    processes_count = os.popen('''ps -Al | grep -c bash''').readline().replace('', '').replace(',', '.')[:-1]
    swap_memory_usage = os.popen("free -m | grep Swap | awk '{print ($3/$2)*100}'").readline().replace('', '').replace(',', '.')[:-1]
    ram_usage = float(os.popen("free -m | grep Mem | awk '{print ($3/$2) * 100}'").readline().replace('', '').replace(',', '.')[:-1])
    st = os.statvfs('/')
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    boot_time = os.popen('uptime -p').read()[:-1]
    avg_load = (cpu_usage + ram_usage) / 2
    
    #calculate tank volumes

    attributes = {
        'ip_address': ip_address,
        'macaddress': mac_address
    }
    telemetry = {key: globals()[key] for key in telemetry_keys if key in globals()}

    # Adding static data
    telemetry.update({
        'cpu_usage': cpu_usage,
        'processes_count': processes_count,
        'disk_usage': used,
        'RAM_usage': ram_usage,
        'swap_memory_usage': swap_memory_usage,
        'boot_time': boot_time,
        'avg_load': avg_load
    })
    
    #print(attributes, telemetry)
    return attributes, telemetry

def sync_state(result, exception=None):
    global powerButton
    if exception is not None:
        print("Exception: " + str(exception))
    else:
        period = result.get('shared', {'powerButton': False})['powerButton']

class RuntimeTracker:
    def __init__(self, filename="runtime.txt"):
        self.start_time = None
        self.total_runtime = 0
        self.filename = filename
        
        # Lade die gespeicherte Laufzeit, wenn die Datei existiert
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                self.total_runtime = float(file.read())

    def start(self):
        self.start_time = time.time()

    def stop(self):
        if self.start_time:
            self.total_runtime += time.time() - self.start_time
            self.start_time = None
            
            # Speichere die gesamte Laufzeit in einer Datei
            with open(self.filename, 'w') as file:
                file.write(str(self.total_runtime))

    def get_total_runtime(self):
        return self.total_runtime / 3600  # Rückgabe in Stunden

class GPSHandler:
    def __init__(self):
        pass  # Hier können Sie Initialisierungscode hinzufügen, falls benötigt.

    def fetch_and_display_data(self, callGpsSwitch):
        if callGpsSwitch:
            timestamp, latitude, longitude, altitude = gpsDataLib.fetch_and_process_gps_data(timeout=10)
            if timestamp is not None:
                # Ausgabe der GPS-Daten für Debugging-Zwecke
                print(f"Zeitstempel: {timestamp}")
                print(f"Breitengrad: {latitude}")
                print(f"Längengrad: {longitude}")
                print(f"Höhe: {altitude if altitude is not None else 'nicht verfügbar'}")
                return timestamp, latitude, longitude, altitude
            else:
                print("Keine GPS-Daten verfügbar.", callGpsSwitch)
                return None, None, None, None
        else:
            print("GPS-Aufruf ist deaktiviert.", callGpsSwitch)
            return None, None, None, None
        
class TurbidityHandler:
    def __init__(self, sensor):
        self.sensor = sensor  # Hier übergeben Sie die Trub_Sensor-Instanz

    def fetch_and_display_data(self, turbiditySensorActive):
        if turbiditySensorActive:
            measuredTurbidity_telem = self.sensor.read_register(start_address=0x0001, register_count=2)
            tempTruebSens = self.sensor.read_register(start_address=0x0003, register_count=2)
            print(f'Trueb: {measuredTurbidity_telem}, Trueb Temp Sens: {tempTruebSens}')
            return measuredTurbidity_telem, tempTruebSens
        else:
            print("TruebOFF", turbiditySensorActive)
            return None, None      

class PHHandler:
    def __init__(self, sensor):
        self.sensor = sensor  # Hier übergeben Sie die PH_Sensor-Instanz
        self.slope = 1  # Anfangswert, wird durch Kalibrierung aktualisiert
        self.intercept = 0  # Anfangswert, wird durch Kalibrierung aktualisiert

    def fetch_and_display_data(self):
        raw_ph_value = self.sensor.read_register(start_address=0x0001, register_count=2)
        measuredPHValue_telem = self.correct_ph_value(raw_ph_value)
        
        temperaturPHSens_telem = self.sensor.read_register(start_address=0x0003, register_count=2)
        
        print(f'PH: {measuredPHValue_telem}, Temperature PH Sens: {temperaturPHSens_telem}, RAW_PH: {raw_ph_value}')
        return measuredPHValue_telem, temperaturPHSens_telem

    def correct_ph_value(self, raw_value):
        return self.slope * raw_value + self.intercept

    def calibrate(self, high_ph_value, low_ph_value, measured_high, measured_low):
        """
        Kalibriert den pH-Sensor mit gegebenen Hoch- und Tiefwerten.

        :param high_ph_value: Bekannter pH-Wert der High-Kalibrierlösung (z.B. 10)
        :param low_ph_value: Bekannter pH-Wert der Low-Kalibrierlösung (z.B. 7)
        :param measured_high: Gemessener Wert des Sensors in der High-Kalibrierlösung
        :param measured_low: Gemessener Wert des Sensors in der Low-Kalibrierlösung
        """
        # Berechnung der Steigung und des y-Achsenabschnitts
        self.slope = (high_ph_value - low_ph_value) / (measured_high - measured_low)
        self.intercept = high_ph_value - self.slope * measured_high

    def save_calibration(self):
        global ph_slope, ph_intercept
        ph_slope = self.slope
        ph_intercept = self.intercept
        state_to_save = {key: globals()[key] for key in shared_attributes_keys if key in globals()}
        save_state(state_to_save)
        print("Kalibrierungswerte gespeichert.")

    def load_calibration(self):
        global ph_slope, ph_intercept
        saved_state = load_state()
        self.slope = saved_state.get('ph_slope', 1)  # Standardwert ist 1
        self.intercept = saved_state.get('ph_intercept', 0)  # Standardwert ist 0
        print("Kalibrierungswerte geladen.")

class FlowRateHandler:
    def __init__(self, radar_sensor):
        self.radar_sensor = radar_sensor
        
        # Pfad zur Kalibrierungsdatei
        calibration_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "calibration_data.json")
        
        # Erstelle eine Instanz der FlowCalculation-Klasse
        self.flow_calculator = FlowCalculation(calibration_file_path)
        
        # Hole den 0-Referenzwert
        self.zero_reference = self.flow_calculator.get_zero_reference()
        print(f"Zero Reference: {self.zero_reference}")

    def fetch_and_calculate(self):
        measured_air_distance = self.radar_sensor.read_radar_sensor(register_address=0x0001)
        
        if measured_air_distance is not None:
            water_level = self.zero_reference - measured_air_distance

            # Berechne den Durchfluss für eine bestimmte Wasserhöhe
            flow_rate = self.flow_calculator.calculate_flow_rate(water_level)
            print(f"Flow Rate (m3/h): {flow_rate}")

            # Konvertiere den Durchfluss in verschiedene Einheiten
            flow_rate_l_min = self.flow_calculator.convert_to_liters_per_minute(flow_rate)
            flow_rate_l_h = self.flow_calculator.convert_to_liters_per_hour(flow_rate)
            flow_rate_m3_min = self.flow_calculator.convert_to_cubic_meters_per_minute(flow_rate)

            return {
                "water_level": water_level,
                "flow_rate": flow_rate,
                "flow_rate_l_min": flow_rate_l_min,
                "flow_rate_l_h": flow_rate_l_h,
                "flow_rate_m3_min": flow_rate_m3_min
            }
        else:
            return None

def signal_handler(sig, frame):
    print('Shutting down gracefully...')
    pumpRelaySw = False
    co2RelaisSw = False
    co2HeatingRelaySw = False
    autoSwitch = False
    powerButton = False
    exit(0)


      
pumpRelaySw = False
co2RelaisSw = False
co2HeatingRelaySw = False
minimumPHValueStop = 5
#countdownPHHigh = ph_high_delay_duration
#countdownPHLow = ph_low_delay_duration

runtime_tracker = RuntimeTracker()
ph_handler = PHHandler(PH_Sensor)
turbidity_handler = TurbidityHandler(Trub_Sensor)
gps_handler = GPSHandler()
ph_handler.load_calibration()

        
def main():
    #def Global Variables for Main Funktion
    global ph_high_delay_start_time, runtime_tracker_var, minimumPHValueStop, maximumPHVal, minimumPHVal, ph_handler, turbidity_handler, gps_handler, runtime_tracker, client, countdownPHLow, powerButton, tempTruebSens, countdownPHHigh, targetPHtolerrance, targetPHValue, calibratePH, gemessener_low_wert, gemessener_high_wert, autoSwitch, temperaturPHSens_telem, measuredPHValue_telem, measuredTurbidity_telem, gpsTimestamp, gpsLatitude, gpsLongitude, gpsHeight, waterLevelHeight_telem, calculatedFlowRate, messuredRadar_Air_telem, flow_rate_l_min, flow_rate_l_h, flow_rate_m3_min, co2RelaisSwSig, co2HeatingRelaySwSig, pumpRelaySwSig, co2RelaisSw, co2HeatingRelaySw, pumpRelaySw

    saved_state = load_state()
    globals().update(saved_state)

    client = TBDeviceMqttClient(THINGSBOARD_SERVER, THINGSBOARD_PORT, ACCESS_TOKEN)
    client.connect()
    client.request_attributes(shared_keys=['powerButton', 'callGpsSwitch'], callback=sync_state)

    # Request shared attributes
    client.request_attributes(shared_keys=shared_attributes_keys, callback=attribute_callback)
    # Subscribe to individual attributes using the defined lists
    for attribute in shared_attributes_keys:
        client.subscribe_to_attribute(attribute, attribute_callback)

    # Now rpc_callback will process rpc requests from the server
    client.set_server_side_rpc_request_handler(rpc_callback)

    #if (radarSensorActive):
    #    flow_rate_handler = FlowRateHandler(Radar_Sensor)
    #    flow_data = flow_rate_handler.fetch_and_calculate()

    previous_power_state = False

    while not client.stopped:
        attributes, telemetry = get_data()
        #PH Initial

        
        runtime_tracker_var = runtime_tracker.get_total_runtime()   
        maximumPHVal = targetPHValue + targetPHtolerrance
        minimumPHVal = targetPHValue - targetPHtolerrance
        print("targetPHValue", targetPHValue)
        print("targetPHtolerrance", targetPHtolerrance)
        print("minimumPHVal", minimumPHVal)
        print("maximumPHVal", maximumPHVal)
        print("gemessener_high_wert", gemessener_high_wert)
        print("gemessener_low_wert", gemessener_low_wert)

        pumpRelaySwSig = pumpRelaySw
        co2RelaisSwSig = co2RelaisSw
        co2HeatingRelaySwSig = co2HeatingRelaySw

        gpsTimestamp, gpsLatitude, gpsLongitude, gpsHeight = gps_handler.fetch_and_display_data(callGpsSwitch) 
        client.send_attributes(attributes)
        client.send_telemetry(telemetry)
        
        if (radarSensorActive):
            flow_rate_handler = FlowRateHandler(Radar_Sensor)
            flow_data = flow_rate_handler.fetch_and_calculate()
            if flow_data:
                print(f"Water Level: {flow_data['water_level']} mm")
                print(f"Flow Rate: {flow_data['flow_rate']} m3/h")
                print(f"Flow Rate (Liters per Minute): {flow_data['flow_rate_l_min']} L/min")
                print(f"Flow Rate (Liters per Hour): {flow_data['flow_rate_l_h']} L/h")
                print(f"Flow Rate (Cubic Meters per Minute): {flow_data['flow_rate_m3_min']} m3/min")

        print("Vor der Kalibrierung:")
        print("Steigung (slope):", ph_handler.slope)
        print("y-Achsenabschnitt (intercept):", ph_handler.intercept)

        if calibratePH:
            ph_handler.calibrate(high_ph_value=10, low_ph_value=7, measured_high=gemessener_high_wert, measured_low=gemessener_low_wert)
            ph_handler.save_calibration()
            calibratePH = False
            print("Nach der Kalibrierung:")
            print("Steigung (slope):", ph_handler.slope)
            print("y-Achsenabschnitt (intercept):", ph_handler.intercept)
        else:
            measuredPHValue_telem, temperaturPHSens_telem = ph_handler.fetch_and_display_data()  
            measuredTurbidity_telem, tempTruebSens = turbidity_handler.fetch_and_display_data(turbiditySensorActive)

        if powerButton:
            if not previous_power_state:  # Wenn der vorherige Zustand "off" war
                saved_state = load_state()
                globals().update(saved_state)
            
            runtime_tracker.start()

        
            
           
# Main Logic
            if autoSwitch:
                print("automode ON", autoSwitch)

                if minimumPHValueStop > measuredPHValue_telem:
                    powerButton = False

                if measuredPHValue_telem > maximumPHVal:
                    print("measuredPHValue_telem", measuredPHValue_telem)
                    print("maximumPHVal", maximumPHVal)
                    co2RelaisSw = True
                    co2HeatingRelaySw = True
                    pumpRelaySw = False
                    if ph_high_delay_start_time is None:
                        ph_high_delay_start_time = time.time()
                    elif time.time() - ph_high_delay_start_time >= ph_high_delay_duration:
                        autoSwitch = False
                        powerButton = False
                        countdownPHHigh = ph_high_delay_duration
                    countdownPHHigh = ph_high_delay_duration - (time.time() - ph_high_delay_start_time)
                else:
                    ph_high_delay_start_time = None

                if measuredPHValue_telem < minimumPHVal:
                    if measuredPHValue_telem < minimumPHValStop:
                        autoSwitch = False
                        powerButton = False
                    if ph_low_delay_start_time is None:
                        ph_low_delay_start_time = time.time()
                    elif time.time() - ph_low_delay_start_time >= ph_low_delay_duration:
                        autoSwitch = False
                        powerButton = False
                        countdownPHLow = ph_low_delay_duration
                    countdownPHLow = ph_low_delay_duration - (time.time() - ph_low_delay_start_time)
                else:
                    ph_low_delay_start_time = None

                # Wenn der pH-Wert innerhalb des erlaubten Fensters liegt:
                if minimumPHVal <= measuredPHValue_telem <= maximumPHVal:
                    pumpRelaySw = True
                    co2RelaisSw = False
                    co2HeatingRelaySw = False
            else:
                print("automode OFF", autoSwitch)
                #pumpRelaySw = False
                #co2RelaisSw = False
                #co2HeatingRelaySw = False
                ph_low_delay_start_time = None
                ph_high_delay_start_time = None
                
                  
                
        else:
            print("Power Switch OFF.", powerButton)
            if previous_power_state:  # Wenn der vorherige Zustand "on" war
                state_to_save = {key: globals()[key] for key in shared_attributes_keys}
                save_state(state_to_save)
            pumpRelaySw = False
            co2RelaisSw = False
            co2HeatingRelaySw = False
            autoSwitch = False
            runtime_tracker.stop() 
            print(f"Gesamtlaufzeit: {runtime_tracker.get_total_runtime()} Stunden")
        previous_power_state = powerButton
        time.sleep(2)
        
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    if ACCESS_TOKEN != "TEST_TOKEN":
        main()
    else:
        print("Please change the ACCESS_TOKEN variable to match your device access token and run the")

