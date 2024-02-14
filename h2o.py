import sys
sys.path.append('./libs')

import signal
import logging.handlers
import time
import os
import gpsDataLib
import json
import threading


from periphery import GPIO
from threading import Thread
from tb_gateway_mqtt import TBDeviceMqttClient
from modbus_lib import DeviceManager
from time import sleep
from FlowCalculation import FlowCalculation

from dotenv import load_dotenv
load_dotenv()
ACCESS_TOKEN = os.environ.get('THINGSBOARD_ACCESS_TOKEN')
THINGSBOARD_SERVER = 'localhost'  # Replace with your Thingsboard server address
THINGSBOARD_PORT = 1883

#RS485 Comunication and Devices
# Create DeviceManager
dev_manager = DeviceManager(port='/dev/ttyS0', baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=1)
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


class UPBoardRGBAsync:
    def __init__(self):
        self.led_pins = {'R': 5, 'G': 6, 'B': 26}
        self.gpio_pins = {}
        self.blink_thread = None
        self.stop_blink = threading.Event()

        for color, pin in self.led_pins.items():
            self.gpio_pins[color] = GPIO(pin, "out")
            self.set_led(color, False)  # Initial ausschalten

    def set_led(self, color, state):
        # Zustand für jede Farbe setzen
        for c in color:
            self.gpio_pins[c].write(not state)

    def start_blinking(self, color_code, blink_rate=None, blink_count=999):
        if self.blink_thread is not None:
            self.stop_blinking()

        self.stop_blink.clear()
        # Übergebe None oder einen speziellen Wert für blink_rate, um dauerhaftes Leuchten zu signalisieren
        self.blink_thread = threading.Thread(target=self._blink_led, args=(color_code, blink_rate, blink_count))
        self.blink_thread.start()

    def _blink_led(self, color_code, blink_rate, blink_count):
        if blink_rate is None:  # Wenn blink_rate None ist, leuchte dauerhaft
            self.set_led(color_code, True)
            while not self.stop_blink.is_set() and blink_count == 999:
                time.sleep(0.1)  # Kurzes Schlafen, um CPU-Zeit zu sparen und auf stop-Befehl zu überprüfen
        else:
            count = 0
            while not self.stop_blink.is_set() and (blink_count == 999 or count < blink_count):
                self.set_led(color_code, True)
                time.sleep(blink_rate)
                self.set_led(color_code, False)
                time.sleep(blink_rate)
                count += 1


    def stop_blinking(self):
        if self.blink_thread is not None:
            self.stop_blink.set()
            self.blink_thread.join()
            self.blink_thread = None

    def cleanup(self):
        self.stop_blinking()
        for gpio in self.gpio_pins.values():
            gpio.close()

class RuntimeTracker:
    def __init__(self, filename="run_time.txt"):
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
    def __init__(self, update_interval=60):
        self.update_interval = update_interval  # Zeitintervall für GPS-Updates in Sekunden
        self.callGpsSwitch = False
        self.latest_gps_data = (None, None, None, None)
        
        # Initialisierungscode...

    def start_gps_updates(self):
        self.callGpsSwitch = True
        thread = threading.Thread(target=self.fetch_and_display_data)
        thread.daemon = True  # Damit der Thread mit dem Hauptprogramm beendet wird
        thread.start()

    def stop_gps_updates(self):
        self.callGpsSwitch = False

    def fetch_and_display_data(self):
        while self.callGpsSwitch:
            # Versuche, GPS-Daten zu holen
            new_timestamp, new_latitude, new_longitude, new_altitude = gpsDataLib.fetch_and_process_gps_data(timeout=10)
            
            # Überprüfe, ob neue Daten verfügbar sind (basierend auf dem Vorhandensein eines Timestamps)
            if new_timestamp is not None:
                # Aktualisiere die gespeicherten GPS-Daten nur, wenn neue Daten empfangen wurden
                self.latest_gps_data = (new_timestamp, new_latitude, new_longitude, new_altitude)
                
                # Ausgabe der neuen GPS-Daten für Debugging-Zwecke
                print(f"Zeitstempel: {new_timestamp}")
                print(f"Breitengrad: {new_latitude}")
                print(f"Längengrad: {new_longitude}")
                print(f"Höhe: {new_altitude if new_altitude is not None else 'nicht verfügbar'}")
            else:
                # Wenn keine neuen Daten verfügbar sind, behalte den letzten gültigen Eintrag
                # und gebe eine Meldung aus, dass keine neuen Daten verfügbar sind
                print("Keine neuen GPS-Daten verfügbar. Letzte gültige Daten werden beibehalten.")

            time.sleep(self.update_interval)  # Warten bis zum nächsten Update


    def get_latest_gps_data(self):
        return self.latest_gps_data
        
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
        if raw_value is None:
            print("Fehler: raw_value ist None. Überprüfen Sie die Sensorverbindung.")
            return 7  # Oder einen anderen Standardwert oder Fehlerbehandlungsmechanismus verwenden
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

class TotalFlowManager:
    def __init__(self, update_interval=60):
        self.last_update_time = time.time()  # Zeitstempel der letzten Aktualisierung
        self.total_flow = 0
        self.load_total_flow()

    def load_total_flow(self):
        try:
            with open('total_flow.json', 'r') as file:
                data = json.load(file)
                self.total_flow = data['total_flow']
        except FileNotFoundError:
            self.total_flow = 0

    def save_total_flow(self):
        with open('total_flow.json', 'w') as file:
            json.dump({'total_flow': self.total_flow}, file)

    def reset_total_flow(self):
        self.total_flow = 0
        self.save_total_flow()

    def update_flow_rate(self, flow_rate_l_min):
        current_time = time.time()
        elapsed_time_in_minutes = (current_time - self.last_update_time) / 60  # Verstrichene Zeit in Minuten
        self.last_update_time = current_time  # Aktualisiere den Zeitstempel der letzten Aktualisierung

        # Berechne die zusätzliche Menge basierend auf der verstrichenen Zeit
        additional_flow = flow_rate_l_min * elapsed_time_in_minutes
        self.total_flow += additional_flow

        print(f"Aktualisierte Gesamtdurchflussmenge: {self.total_flow} L")
        self.save_total_flow()

    def start_periodic_save(self):
        def save_periodically():
            while True:
                self.save_total_flow()
                time.sleep(self.update_interval)
        threading.Thread(target=save_periodically, daemon=True).start()


def signal_handler(sig, frame):
    print('Shutting down gracefully...')
    pumpRelaySw = False
    co2RelaisSw = False
    co2HeatingRelaySw = False
    autoSwitch = False
    powerButton = False
    runtime_tracker.stop() 
    rgb_controller.stop_blinking()
    rgb_controller.cleanup()
    print(f"Gesamtlaufzeit: {runtime_tracker.get_total_runtime()} Stunden")
    state_to_save = {key: globals()[key] for key in shared_attributes_keys}
    save_state(state_to_save)
    print('Speichere Daten.')
    time.sleep(3)  # Das Skript wartet hier 2 Sekunden
    print('Shutting down now.')  # Diese Zeile wird nach 2 Sekunden ausgeführt
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
rgb_controller = UPBoardRGBAsync()
        
def main():
    #def Global Variables for Main Funktion
    global switch_monitor, total_flow, ph_low_delay_start_time,ph_high_delay_start_time, runtime_tracker_var, minimumPHValueStop, maximumPHVal, minimumPHVal, ph_handler, turbidity_handler, gps_handler, runtime_tracker, client, countdownPHLow, powerButton, tempTruebSens, countdownPHHigh, targetPHtolerrance, targetPHValue, calibratePH, gemessener_low_wert, gemessener_high_wert, autoSwitch, temperaturPHSens_telem, measuredPHValue_telem, measuredTurbidity_telem, gpsTimestamp, gpsLatitude, gpsLongitude, gpsHeight, waterLevelHeight_telem, calculatedFlowRate, messuredRadar_Air_telem, flow_rate_l_min, flow_rate_l_h, flow_rate_m3_min, co2RelaisSwSig, co2HeatingRelaySwSig, pumpRelaySwSig, co2RelaisSw, co2HeatingRelaySw, pumpRelaySw, flow_rate_handler

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

    rgb_controller.start_blinking('B', blink_rate=None)  # Rote LED leuchtet dauerhaft
    #rgb_controller.start_blinking('G', 0.5, blink_count=99)
    # Now rpc_callback will process rpc requests from the server
    client.set_server_side_rpc_request_handler(rpc_callback)

    

    total_flow_manager = TotalFlowManager()
    total_flow_manager.start_periodic_save()


    # Initialisierung des GPSHandlers
    gps_handler = GPSHandler(update_interval=15)  # GPS-Daten alle 60 Sekunden aktualisieren
    gps_handler.start_gps_updates()

    #Laden der alten werte
    saved_state = load_state()
    globals().update(saved_state)
    previous_power_state = False

    while not client.stopped:
        attributes, telemetry = get_data()
        #PH Initial

        
        runtime_tracker_var = runtime_tracker.get_total_runtime()   
        maximumPHVal = targetPHValue + targetPHtolerrance
        minimumPHVal = targetPHValue - targetPHtolerrance   
        #print("targetPHValue", targetPHValue)
        #print("targetPHtolerrance", targetPHtolerrance)
        #print("minimumPHVal", minimumPHVal)
        #print("maximumPHVal", maximumPHVal)
        #print("gemessener_high_wert", gemessener_high_wert)
        #print("gemessener_low_wert", gemessener_low_wert)
        # Optional: Sie können hier die aktuelle Gesamtdurchflussmenge ausgeben oder anderweitig verwenden
        
        pumpRelaySwSig = pumpRelaySw
        co2RelaisSwSig = co2RelaisSw
        co2HeatingRelaySwSig = co2HeatingRelaySw
        print("co2RelaisSwSig", co2RelaisSwSig)
        print("co2RelaisSw", co2RelaisSw)
            

        gpsTimestamp, gpsLatitude, gpsLongitude, gpsHeight = gps_handler.get_latest_gps_data() 
        client.send_attributes(attributes)
        client.send_telemetry(telemetry)
        
        

        if (radarSensorActive):
            flow_rate_handler = FlowRateHandler(Radar_Sensor)
            flow_data = flow_rate_handler.fetch_and_calculate()

            if flow_data:
                # Update the total flow using the calculated flow rate
                total_flow_manager.update_flow_rate(flow_data['flow_rate_l_min'])
                total_flow = total_flow_manager.total_flow
                flow_rate_l_min = flow_data['flow_rate_m3_min']
                #print(f"Water Level: {flow_data['water_level']} mm")
                #print(f"Flow Rate: {flow_data['flow_rate']} m3/h")
                #print(f"Flow Rate (Liters per Minute): {flow_data['flow_rate_l_min']} L/min")
                #print(f"Flow Rate (Liters per Hour): {flow_data['flow_rate_l_h']} L/h")
                #print(f"Flow Rate (Cubic Meters per Minute): {flow_data['flow_rate_m3_min']} m3/min")
                #print(f"Aktuelle Gesamtdurchflussmenge: {total_flow_manager.total_flow} L")

        #print("Vor der Kalibrierung:")
        #print("Steigung (slope):", ph_handler.slope)
        #print("y-Achsenabschnitt (intercept):", ph_handler.intercept)

        if calibratePH:
            ph_handler.calibrate(high_ph_value=10, low_ph_value=7, measured_high=gemessener_high_wert, measured_low=gemessener_low_wert)
            ph_handler.save_calibration()
            calibratePH = False
            #print("Nach der Kalibrierung:")
            #print("Steigung (slope):", ph_handler.slope)
            #print("y-Achsenabschnitt (intercept):", ph_handler.intercept)
        else:
            measuredPHValue_telem, temperaturPHSens_telem = ph_handler.fetch_and_display_data()  
            measuredTurbidity_telem, tempTruebSens = turbidity_handler.fetch_and_display_data(turbiditySensorActive)

        if powerButton:
            runtime_tracker.start()
            if autoSwitch:
                if minimumPHValueStop > measuredPHValue_telem:
                    powerButton = False
                if measuredPHValue_telem > maximumPHVal:
                    #print("measuredPHValue_telem", measuredPHValue_telem)
                    print("maximumPHVal", maximumPHVal)
                    co2RelaisSw = True
                    print("co2RelaisSw", co2RelaisSw)
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
                pumpRelaySw = False
                co2RelaisSw = False
                co2HeatingRelaySw = False
                ph_low_delay_start_time = None
                ph_high_delay_start_time = None
        else:
            print("Power Switch OFF.", powerButton)        
            pumpRelaySw = False
            co2RelaisSw = False
            co2HeatingRelaySw = False
            autoSwitch = False
            runtime_tracker.stop() 
            #print(f"Gesamtlaufzeit: {runtime_tracker.get_total_runtime()} Stunden")
            print("co2RelaisSwSig", co2RelaisSwSig)
            print("co2RelaisSw", co2RelaisSw)
            time.sleep(2)

    
    
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    if ACCESS_TOKEN != "TEST_TOKEN":
        main()
    else:
        print("Please change the ACCESS_TOKEN variable to match your device access token and run the")

