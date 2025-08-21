from builtins import print
import sys
sys.path.append('/home/owipex_adm/owipex-sps/libs')
CONFIG_PATH = "/etc/owipex/"

import signal
import logging.handlers
import time
import os
import libs.gpsDataLib as gpsDataLib
import json
import threading

DEVELOPMENT_VERSION = "2.73" # for internal use only

# Main loop sleep configuration
MAINLOOP_SLEEP_SEC = 0.1  # Sleep time in seconds at end of main loop (0 = no sleep)

# Device reading interval configuration - Production intervals
OUTLETFLAP_READINGS_INTERVAL_SEC = 30.0  # OutletFlap readings
RADAR_READINGS_INTERVAL_SEC = 41.0       # Radar readings
PH_READINGS_INTERVAL_SEC = 42.0          # PH readings
TURBIDITY_READINGS_INTERVAL_SEC = 29.0   # Turbidity readings
TURBIDITY2_READINGS_INTERVAL_SEC = 28.0  # Turbidity2 readings
US_READINGS_INTERVAL_SEC = 39.0          # US Flow readings
US2_READINGS_INTERVAL_SEC = 38.0          # US 2 Flow readings
US3_READINGS_INTERVAL_SEC = 37.0          # US 3 Flow readings

# Device reading interval configuration - Debug intervals
DEBUG_OUTLETFLAP_READINGS_INTERVAL_SEC = 31.0  # OutletFlap readings
DEBUG_RADAR_READINGS_INTERVAL_SEC = 20.0       # Radar readings
DEBUG_PH_READINGS_INTERVAL_SEC = 22.0          # PH readings
DEBUG_TURBIDITY_READINGS_INTERVAL_SEC = 32.0   # Turbidity readings
DEBUG_TURBIDITY2_READINGS_INTERVAL_SEC = 33.0  # Turbidity2 readings
DEBUG_US_READINGS_INTERVAL_SEC = 28.0          # US Flow readings
DEBUG_US2_READINGS_INTERVAL_SEC = 27.0          # US 2 Flow readings
DEBUG_US3_READINGS_INTERVAL_SEC = 26.0          # US 3 Flow readings

# Dynamic interval variables (switchable via UseDebugReadingsIntervalls)
outletFlapReadingsIntervalSec = OUTLETFLAP_READINGS_INTERVAL_SEC
radarReadingsIntervalSec = RADAR_READINGS_INTERVAL_SEC
phReadingsIntervalSec = PH_READINGS_INTERVAL_SEC
turbidityReadingsIntervalSec = TURBIDITY_READINGS_INTERVAL_SEC
turbidity2ReadingsIntervalSec = TURBIDITY2_READINGS_INTERVAL_SEC
usReadingsIntervalSec = US_READINGS_INTERVAL_SEC
us2ReadingsIntervalSec = US2_READINGS_INTERVAL_SEC
us3ReadingsIntervalSec = US3_READINGS_INTERVAL_SEC

from periphery import GPIO
from threading import Thread
from tb_gateway_mqtt import TBDeviceMqttClient
from libs.modbus_lib import DeviceManager
from time import sleep
from libs.RadarFlowCalculation import RadarFlowCalculation

from dotenv import load_dotenv
dotenv_path = '/etc/owipex/.env'
load_dotenv(dotenv_path=dotenv_path)
ACCESS_TOKEN = os.environ.get('THINGSBOARD_ACCESS_TOKEN')
THINGSBOARD_SERVER = 'localhost'  # Replace with your Thingsboard server address
THINGSBOARD_PORT = 1883

iTest = 0
isTestFinished = False

#RS485 Comunication and Devices
# Create DeviceManager and devices
dev_manager = DeviceManager(port='/dev/ttyS0', baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=1)
Radar_Sensor = dev_manager.add_device(device_id=0x01)
Trub_Sensor = dev_manager.add_device(device_id=0x02)
Ph_Sensor = dev_manager.add_device(device_id=0x03)
OutletFlap_Sensor = dev_manager.add_device(device_id=0x0a)  # Vincer Valve
Trub_Sensor2 = dev_manager.add_device(device_id=0x0c)  # Turbidity Sensor 2
Us_Sensor = dev_manager.add_device(device_id=0x28)  # US Flow Sensor 1
Us_Sensor2 = dev_manager.add_device(device_id=0x29)  # US Flow Sensor 2
Us_Sensor3 = dev_manager.add_device(device_id=0x2a)  # US Flow Sensor 3
#logging.basicConfig(level=logging.DEBUG)
client = None

#Import Global vars
from config import *
shared_attributes_keys

def save_state(state_dict):
    state_file_path = os.path.join(CONFIG_PATH, 'state.json')
    try:
        with open(state_file_path, 'w') as file:
            json.dump(state_dict, file)
    except IOError as e:
        print(f"Fehler beim Speichern des Zustands: {e}")

def load_state():
    state_file_path = os.path.join(CONFIG_PATH, 'state.json')
    try:
        if os.path.exists(state_file_path):
            with open(state_file_path, 'r') as file:
                return json.load(file)
        else:
            print("Zustandsdatei nicht gefunden. Ein leerer Zustand wird verwendet.")
    except json.JSONDecodeError as e:
        print(f"Fehler beim Lesen des Zustands: {e}. Ein leerer Zustand wird verwendet.")
    return {}

def printTs(message):
    """Central print function with timestamp"""
    timestamp = get_timestamp()
    print(f"[{timestamp}] {message}")

def get_timestamp():
    """Generate timestamp string in format [HH:MM:SS.mmm]"""
    return time.strftime("%H:%M:%S", time.localtime()) + f".{int(time.time() * 1000) % 1000:03d}"

def update_reading_intervals():
    """Update reading interval variables based on useDebugReadingsIntervalls setting"""
    global outletFlapReadingsIntervalSec, radarReadingsIntervalSec, phReadingsIntervalSec
    global turbidityReadingsIntervalSec, turbidity2ReadingsIntervalSec
    global usReadingsIntervalSec, us2ReadingsIntervalSec, us3ReadingsIntervalSec
    global useDebugReadingsIntervalls
    
    if useDebugReadingsIntervalls:
        outletFlapReadingsIntervalSec = DEBUG_OUTLETFLAP_READINGS_INTERVAL_SEC
        radarReadingsIntervalSec = DEBUG_RADAR_READINGS_INTERVAL_SEC
        phReadingsIntervalSec = DEBUG_PH_READINGS_INTERVAL_SEC
        turbidityReadingsIntervalSec = DEBUG_TURBIDITY_READINGS_INTERVAL_SEC
        turbidity2ReadingsIntervalSec = DEBUG_TURBIDITY2_READINGS_INTERVAL_SEC
        usReadingsIntervalSec = DEBUG_US_READINGS_INTERVAL_SEC
        us2ReadingsIntervalSec = DEBUG_US2_READINGS_INTERVAL_SEC
        us3ReadingsIntervalSec = DEBUG_US3_READINGS_INTERVAL_SEC
        printTs("🔧 Debug-Leseintervalle aktiviert")
    else:
        outletFlapReadingsIntervalSec = OUTLETFLAP_READINGS_INTERVAL_SEC
        radarReadingsIntervalSec = RADAR_READINGS_INTERVAL_SEC
        phReadingsIntervalSec = PH_READINGS_INTERVAL_SEC
        turbidityReadingsIntervalSec = TURBIDITY_READINGS_INTERVAL_SEC
        turbidity2ReadingsIntervalSec = TURBIDITY2_READINGS_INTERVAL_SEC
        usReadingsIntervalSec = US_READINGS_INTERVAL_SEC
        us2ReadingsIntervalSec = US2_READINGS_INTERVAL_SEC
        us3ReadingsIntervalSec = US3_READINGS_INTERVAL_SEC
        printTs("⚡ Produktions-Leseintervalle aktiviert")

 #that will be called when the value of our Shared Attribute changes
def attribute_callback(result, _):
    global gps_handler, gpsEnabled, outletFlapActive
    
    print(f"Attribute callback: {result}")

    # Aktualisiere globale Variablen
    globals().update({key: result[key] for key in result if key in globals()})
    
    # Überprüfe, ob sich gpsEnabled geändert hat
    if 'gpsEnabled' in result:
        gpsEnabled = result['gpsEnabled']
        if gpsEnabled:
            try:
                gps_handler.gps_enabled = True
                gps_handler.start_gps_updates()
                print("GPS-Funktionalität aktiviert")
            except Exception as e:
                print(f"Fehler beim Aktivieren der GPS-Funktionalität: {e}")
                gpsEnabled = False
        else:
            gps_handler.gps_enabled = False
            gps_handler.stop_gps_updates()
            print("GPS-Funktionalität deaktiviert")

    # Überprüfe useDebugReadingsIntervalls Änderung
    if 'useDebugReadingsIntervalls' in result:
        useDebugReadingsIntervalls = result['useDebugReadingsIntervalls']
        mode_text = "Debug-Intervalle" if useDebugReadingsIntervalls else "Produktions-Intervalle"
        printTs(f"🔄 Leseintervall-Modus geändert auf: {mode_text}")
        update_reading_intervals()
    
    # Überprüfe isDebugMode Änderung
    if 'isDebugMode' in result:
        isDebugMode = result['isDebugMode']
        debug_status = "AKTIVIERT" if isDebugMode else "DEAKTIVIERT"
        printTs(f"🐛 Debug-Modus {debug_status}")

    if 'outletFlapActive' in result:
        old_active = outletFlapActive
        outletFlapActive = result['outletFlapActive']
        print(f"OutletFlap Active-Status: {old_active} → {outletFlapActive}")
    
    # OutletFlap Commands
    if outletFlapActive:
        if 'outletFlapTargetPosition' in result:
            target_pos = result['outletFlapTargetPosition']
            # TODO: RD: hier im callback dürfen keine Aktionen ausgeführt werden, 
            # da dies gerade im main laufende Lesungen stören kann.
            # Abhilfe: hier Variablen setzen, die beim nächsten Durchlauf der main loop 
            # entsprechende Aktionen auslösen.
            if isinstance(target_pos, (int, float)) and 0 <= target_pos <= 100:
                print(f"📍 OutletFlap Zielposition: {target_pos}%")
                outlet_flap_handler.set_valve_position(target_pos)
            else:
                print(f"❌ Ungültige OutletFlap Position: {target_pos}")
        
        if 'outletFlapIsRemoteMode' in result:
            new_mode = result['outletFlapIsRemoteMode']
            if isinstance(new_mode, bool):
                mode_value = 1 if new_mode else 0
                mode_name = "REMOTE-Modus (AUTO)" if new_mode else "LOCAL-Modus (MANUAL)"
                print(f"🔄 OutletFlap: Wechsle zu {mode_name}")
                outlet_flap_handler.setRemoteOrLocalMode(mode_value)
            else:
                print(f"❌ Ungültiger Wert für outletFlapIsRemoteMode: {new_mode} (erwartet: boolean)")
    else:
        # Log why commands are ignored
        if 'outletFlapTargetPosition' in result or 'outletFlapIsRemoteMode' in result:
            print("⚠️ OutletFlap Commands ignoriert - outletFlapActive was not set")

    # Speichere den Zustand
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
    attributes = {
        'SW-Version': "2.0.0",
        'HW-Version': "2.0.0",
        'DEVELOPMENT_VERSION': DEVELOPMENT_VERSION
    }
    telemetry = {key: globals()[key] for key in telemetry_keys if key in globals()}
    # Adding static data
    #telemetry.update({
    #    'cpu_usage': cpu_usage,
    #    'processes_count': processes_count,
    #    'disk_usage': used,
    #    'RAM_usage': ram_usage,
    #    'swap_memory_usage': swap_memory_usage,
    #    'boot_time': boot_time,
    #    'avg_load': avg_load,
    #    'cpu_temperature': cpu_temperature  # Hinzufügen der CPU-Temperatur
    #})
    
    #print(attributes, telemetry)
    return attributes, telemetry

def sync_state(result, exception=None):
    global powerButton
    if exception is not None:
        print("Exception: " + str(exception))
    else:
        powerButton = result.get('shared', {'powerButton': False})['powerButton']

class RuntimeTracker:
    def __init__(self, filename="run_time.txt"):
        self.start_time = None
        self.total_runtime = 0
        self.filename = os.path.join(CONFIG_PATH, filename)
        # print(f"content of {CONFIG_PATH}: \"{CONFIG_PATH}\"")
        
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

class GpsHandler:
    def __init__(self, deviceName, update_interval=60):
        self.deviceName = deviceName
        self.update_interval = update_interval
        self.callGpsSwitch = False
        self.latest_gps_data = (None, None, None, None, None)
        self.thread = None
        self.gps_enabled = True
        self.error_count = 0
        self.max_errors = 5  # Nach 5 Fehlern wird GPS als nicht verfügbar betrachtet

    def start_gps_updates(self):
        if not self.gps_enabled:
            print("GPS-Funktionalität ist deaktiviert.")
            return
            
        self.callGpsSwitch = True
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.fetch_and_display_data)
            self.thread.daemon = True
            self.thread.start()

    def stop_gps_updates(self):
        self.callGpsSwitch = False
        if self.thread and self.thread.is_alive():
            try:
                self.thread.join(timeout=2)  # Warte maximal 2 Sekunden
            except Exception as e:
                print(f"Fehler beim Beenden des GPS-Threads: {e}")

    def fetch_and_display_data(self):
        while self.callGpsSwitch:
            try:
                # Versuche, GPS-Daten zu holen
                new_timestamp, new_latitude, new_longitude, new_altitude = gpsDataLib.fetch_and_process_gps_data(timeout=5)
                
                # Überprüfe, ob neue Daten verfügbar sind (basierend auf dem Vorhandensein eines Timestamps)
                if new_timestamp is not None:
                    # Aktualisiere die gespeicherten GPS-Daten nur, wenn neue Daten empfangen wurden
                    self.latest_gps_data = (new_timestamp, new_latitude, new_longitude, new_altitude)
                    self.error_count = 0  # Zurücksetzen des Fehlerzählers bei erfolgreicher Abfrage
                    
                    # Ausgabe der neuen GPS-Daten für Debugging-Zwecke
                    print(f"Zeitstempel: {new_timestamp}")
                    print(f"Breitengrad: {new_latitude}")
                    print(f"Längengrad: {new_longitude}")
                    print(f"Höhe: {new_altitude if new_altitude is not None else 'nicht verfügbar'}")
                else:
                    # Wenn keine neuen Daten verfügbar sind, behalte den letzten gültigen Eintrag
                    # und gebe eine Meldung aus, dass keine neuen Daten verfügbar sind
                    self.error_count += 1
                    print(f"Keine neuen GPS-Daten verfügbar. Fehler #{self.error_count}")
                    
                    # Wenn zu viele Fehler auftreten, deaktiviere GPS
                    if self.error_count >= self.max_errors:
                        print("GPS scheint nicht verfügbar zu sein. GPS-Funktionalität wird deaktiviert.")
                        self.gps_enabled = False
                        self.callGpsSwitch = False
                        return
            except Exception as e:
                print(f"Fehler bei GPS-Datenverarbeitung: {e}")
                self.error_count += 1
                if self.error_count >= self.max_errors:
                    print("Zu viele GPS-Fehler. GPS-Funktionalität wird deaktiviert.")
                    self.gps_enabled = False
                    self.callGpsSwitch = False
                    return

            time.sleep(self.update_interval)  # Warten bis zum nächsten Update

    def get_latest_gps_data(self):
        return self.latest_gps_data
        
class TurbidityHandler:
    def __init__(self, deviceName, sensor):
        self.deviceName = deviceName
        self.sensor = sensor  # Hier übergeben Sie die Trub_Sensor-Instanz

    def fetch_and_display_data(self):
        measuredTurbidity_telem = self.sensor.read_register(start_address=0x0001, register_count=2)
        tempTruebSens = self.sensor.read_register(start_address=0x0003, register_count=2)
        
        if measuredTurbidity_telem is not None and tempTruebSens is not None:
            printTs(f'✅ {self.deviceName}: {measuredTurbidity_telem}, {self.deviceName} Temp Sens: {tempTruebSens}')
            return measuredTurbidity_telem, tempTruebSens
        else:
            printTs(f"❌ {self.deviceName}: Lesung fehlgeschlagen")
            return None, None

class PhHandler:
    def __init__(self, deviceName, sensor):
        self.deviceName = deviceName
        self.sensor = sensor  # Übergeben Sie die Ph_Sensor-Instanz
        self.slope = 1  # Anfangswert, wird durch Kalibrierung aktualisiert
        self.intercept = 0  # Anfangswert, wird durch Kalibrierung aktualisiert
        self.load_calibration()  # Laden der Kalibrierungsdaten beim Start

    def fetch_and_display_data(self):
        try:
            raw_ph_value = self.sensor.read_register(start_address=0x0001, register_count=2)
            if raw_ph_value is None:
                return None, None
            
            measuredPHValue_telem = self.correct_ph_value(raw_ph_value)
            temperaturPHSens_telem = self.sensor.read_register(start_address=0x0003, register_count=2)
            
            if temperaturPHSens_telem is not None:
                printTs(f'✅ PH: {measuredPHValue_telem}, Temperature PH Sens: {temperaturPHSens_telem}, RAW_PH: {raw_ph_value}')
                return measuredPHValue_telem, temperaturPHSens_telem
            else:
                printTs(f"❌ PH-Sensor: Temperatur-Lesung fehlgeschlagen")
                return measuredPHValue_telem, None
                
        except Exception as e:
            printTs(f"❌ PH-Sensor: Fehler bei der Ablesung: {e}")
            return None, None

    def correct_ph_value(self, raw_value):
        return self.slope * raw_value + self.intercept

    def calibrate(self, high_ph_value, low_ph_value, measured_high, measured_low):
        self.slope = (high_ph_value - low_ph_value) / (measured_high - measured_low)
        self.intercept = high_ph_value - self.slope * measured_high
        self.save_calibration()

    def save_calibration(self):
        calibration_file_path = os.path.join(CONFIG_PATH, 'ph_calibration.json')
        calibration_data = {'ph_slope': self.slope, 'ph_intercept': self.intercept}
        try:
            with open(calibration_file_path, 'w') as file:
                json.dump(calibration_data, file)
            print("Kalibrierungswerte gespeichert.")
        except IOError as e:
            print(f"Fehler beim Speichern der Kalibrierungsdaten: {e}")

    def load_calibration(self):
        calibration_file_path = os.path.join(CONFIG_PATH, 'ph_calibration.json')
        try:
            with open(calibration_file_path, 'r') as file:
                calibration_data = json.load(file)
            self.slope = calibration_data.get('ph_slope', 1)
            self.intercept = calibration_data.get('ph_intercept', 0)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Fehler beim Laden der Kalibrierungsdaten: {e}. Verwende Standardwerte.")
            self.slope = 1
            self.intercept = 0
        finally:
            print("Kalibrierungswerte geladen oder auf Standardwerte zurückgesetzt.")

class RadarHandler:
    def __init__(self, deviceName, radar_sensor):
        self.deviceName = deviceName
        self.radar_sensor = radar_sensor
        
        # Pfad zur Kalibrierungsdatei aktualisieren
        calibration_file_path = os.path.join(CONFIG_PATH, "calibration_data.json")
        
        # Prüfung und Reparatur der Kalibrierungsdatei
        self.calibration_data = self.load_or_repair_calibration(calibration_file_path)
        
        self.flow_calculator = RadarFlowCalculation(calibration_file_path)
        
        # Hole den 0-Referenzwert
        self.zero_reference = self.flow_calculator.get_zero_reference()
        print(f"Zero Reference: {self.zero_reference}")

    def load_or_repair_calibration(self, file_path):
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
            print("Kalibrierungsdaten erfolgreich geladen.")
            return data
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Fehler beim Laden der Kalibrierungsdatei: {e}. Erzeuge Standarddaten.")
            default_data = {"zero_reference": 250}  # Ersetze dies durch realistische Standardwerte
            with open(file_path, 'w') as file:
                json.dump(default_data, file)
            return default_data

    def fetch_and_calculate(self):
        try:
            measured_air_distance = self.radar_sensor.read_radar_sensor(register_address=0x0001)
            if measured_air_distance is None:
                raise ValueError("Keine Messung vom Radar-Sensor erhalten.")
            
            water_level = self.zero_reference - measured_air_distance
            printTs(f"Radar: Wasserhöhe: {water_level} mm")
            flow_rate = self.flow_calculator.calculate_flow_rate(water_level)
            printTs(f"Radar: Flow Rate (L/s): {flow_rate}")

            flow_rate_l_min = self.flow_calculator.convert_to_liters_per_minute(flow_rate)
            flow_rate_l_h = self.flow_calculator.convert_to_liters_per_hour(flow_rate)
            flow_rate_m3_min = self.flow_calculator.convert_to_cubic_meters_per_minute(flow_rate)
            
            return {
                "water_level_mm": water_level,
                "flow_rate_l_s": flow_rate,
                "flow_rate_l_min": flow_rate_l_min,
                "flow_rate_l_h": flow_rate_l_h,
                "flow_rate_m3_min": flow_rate_m3_min
            }
            
        except Exception as e:
            printTs(f"❌ Radar-Sensor: Fehler beim Lesen: {e}")
            return None

class RadarTotalFlowManager:
    def __init__(self, update_interval=60):
        self.update_interval = update_interval
        self.last_update_time = None  # Initialisierung des Zeitstempels der letzten Aktualisierung
        self.total_flow = 0
        self.load_total_flow()

    def load_total_flow(self):
        total_flow_file_path = os.path.join(CONFIG_PATH, 'total_flow.json')
        try:
            with open(total_flow_file_path, 'r') as file:
                data = json.load(file)
                self.total_flow = data['total_flow']
        except (FileNotFoundError, json.JSONDecodeError):
            print("Fehler: Datei nicht gefunden oder Daten sind beschädigt. Setze total_flow auf 0.")
            self.total_flow = 0
            self.save_total_flow()  # Speichere initialen Zustand, um Datei konsistent zu halten

    def save_total_flow(self):
        total_flow_file_path = os.path.join(CONFIG_PATH, 'total_flow.json')
        with open(total_flow_file_path, 'w') as file:
            json.dump({'total_flow': self.total_flow}, file)

    def reset_total_flow(self):
        self.total_flow = 0
        self.save_total_flow()

    def update_flow_rate(self, flow_rate_l_min):
        current_time = time.time()
        
        if self.last_update_time is None:
            elapsed_time_in_minutes = 0
            self.last_update_time = current_time
        else:
            elapsed_time_in_minutes = (current_time - self.last_update_time) / 60  # Verstrichene Zeit in Minuten
            self.last_update_time = current_time  # Aktualisiere den Zeitstempel der letzten Aktualisierung

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

class UsHandler:
    def __init__(self, deviceName, sensor):
        self.deviceName = deviceName
        self.sensor = sensor 
        self.last_successful_flow_rate = 0.0
        self.last_successful_total_flow = 0.0
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5

    def fetchViaDeviceManager(self):
        wasOk = False
        try:
            # Lese Durchfluss und Gesamtmenge mit Fehlerbehandlung
            current_flow = self.sensor.read_flow_rate_m3ph()
            total_flow = self.sensor.read_totalizer_m3()
            
            if current_flow is not None:
                self.consecutive_errors = 0
                self.last_successful_flow_rate = current_flow
            else:
                self.consecutive_errors += 1
                current_flow = self.last_successful_flow_rate
                printTs(f"⚠️ {self.deviceName}: Verwende letzten erfolgreichen Durchflusswert: {current_flow:.3f} m³/h")
                
            if total_flow is not None:
                self.consecutive_errors = 0
                self.last_successful_total_flow = total_flow
            else:
                self.consecutive_errors += 1
                total_flow = self.last_successful_total_flow
                printTs(f"⚠️ {self.deviceName}: Verwende letzte erfolgreiche Gesamtmenge: {total_flow:.3f} m³")
            
            # Protokolliere die gelesenen Werte
            if current_flow is not None and total_flow is not None:
                printTs(f"✅ {self.deviceName}: Aktueller Durchfluss = {current_flow:.3f} m³/h, Gesamtmenge = {total_flow:.3f} m³")
                wasOk = True
            else:
                printTs(f"❌ {self.deviceName}: Teilweise Daten - Durchfluss = {current_flow}, Gesamtmenge = {total_flow}")
            
            # Überprüfe auf zu viele aufeinanderfolgende Fehler
            if self.consecutive_errors >= self.max_consecutive_errors:
                printTs(f"⚠️ {self.deviceName}: {self.consecutive_errors} aufeinanderfolgende Fehler. Überprüfen Sie die Verbindung!")
                
            return current_flow, total_flow, wasOk
            
        except Exception as e:
            self.consecutive_errors += 1
            printTs(f"❌ UsFlowSensor ({self.deviceName}): Exception beim Lesen: {e}")
            import traceback
            traceback.print_exc()
            return None, None

class OutletFlapHandler:
    def __init__(self, deviceName, sensor):
        self.deviceName = deviceName
        self.sensor = sensor  # Übergeben Sie die OutletFlap-Instanz

        # FC11R Register Definitions (from valve_actuator.py pattern)
        self.REMOTE_LOCAL_REG = 0x0000      # Remote/Local Control (0=Local, 1=Remote)
        self.POSITION_FEEDBACK_REG = 0x0001  # Istposition lesen (read only)
        self.POSITION_SETPOINT_REG = 0x0002  # Sollposition schreiben (read/write)
        self.ERROR_CODE_REG = 0x0003         # Fehlercode (read only)
        self.TEST_REG = 0x0004               # Test register

    def fetch_and_display_data(self):
        return self.read_outletflap_sensor_data()
    
    def read_outletflap_sensor_data(self):
        """Internal method for actual sensor reading - ALWAYS use with lock!"""
        try:
            remote_local = self.sensor.read_register(start_address=0x0000, register_count=1, data_format='>H')
            valve_position = self.sensor.read_register(start_address=0x0001, register_count=1, data_format='>H')
            setpoint = self.sensor.read_register(start_address=0x0002, register_count=1, data_format='>H')
            error_code = self.sensor.read_register(start_address=0x0003, register_count=1, data_format='>H')
            test_register = self.sensor.read_register(start_address=0x0004, register_count=1, data_format='>H')
            
            # Check if all values are None (failed reading)
            if all(value is None for value in [remote_local, valve_position, setpoint, error_code, test_register]):
                printTs(f'❌ {self.deviceName} - All readings failed: Remote/Local: {remote_local}, Position: {valve_position}, Setpoint: {setpoint}, Error: {error_code}, Test: {test_register}')
                return None, None, None, None, None
            else:
                printTs(f'✅ {self.deviceName} - Remote/Local: {remote_local}, Position: {valve_position}, Setpoint: {setpoint}, Error: {error_code}, Test: {test_register}')
                return remote_local, valve_position, setpoint, error_code, test_register
        except Exception as e:
            printTs(f"❌ {self.deviceName}: ERROR - {e}")
            return None, None, None, None, None

    def read_valve_data(self):
        """NEUE Methode - Enhanced valve reading mit FC11R-spezifischer Datenkonvertierung"""
        try:
            # Istposition mit FC11R-Konvertierung: (raw_value - 1999) / 10.0
            raw_position = self.sensor.read_register(start_address=self.POSITION_FEEDBACK_REG, register_count=1, data_format='>H')
            current_position = (raw_position - 1999) / 10.0 if raw_position is not None and raw_position >= 1999 else 0.0
            
            # Remote/Local Status (0=Local/Manual, 1=Remote/Auto)
            remote_local = self.sensor.read_register(start_address=self.REMOTE_LOCAL_REG, register_count=1, data_format='>H') or 0
            
            # Sollposition mit FC11R-Konvertierung
            setpoint_raw = self.sensor.read_register(start_address=self.POSITION_SETPOINT_REG, register_count=1, data_format='>H')
            setpoint_position = (setpoint_raw - 1999) / 10.0 if setpoint_raw is not None and setpoint_raw >= 1999 else 0.0
            
            # Fehlercode
            error_code = self.sensor.read_register(start_address=self.ERROR_CODE_REG, register_count=1, data_format='>H') or 0
            
            # Aktuelle Uhrzeit für die Ausgabe
            printTs(f'✅ {self.deviceName} Enhanced - Current: {current_position}%, Setpoint: {setpoint_position}%, Mode: {"REMOTE" if remote_local == 1 else "LOCAL"}, Error: {error_code}')
            
            return {
                'current_position': round(current_position, 1),      # Konvertierte aktuelle Position
                'raw_position_value': raw_position,                  # Raw-Position-Wert
                'setpoint_position': round(setpoint_position, 1),    # Konvertierte Sollposition
                'raw_setpoint_value': setpoint_raw,                  # Raw-Sollwert
                'remote_local_status': remote_local,                 # 0=Local, 1=Remote
                'is_remote_mode': (remote_local == 1),              # Boolean
                'is_local_mode': (remote_local == 0),               # Boolean
                'error_code': error_code,                           # Fehlercode
                'has_error': (error_code != 0)                     # Boolean
            }
            
        except Exception as e:
            printTs(f"❌ {self.deviceName} read_valve_data Error: {e}")
            return None

    def set_valve_position(self, target_position):
        """Set valve position mit FC11R-Konvertierung (0-100%)"""
        try:
            if not (0 <= target_position <= 100):
                printTs(f"❌ {self.deviceName}: Position muss zwischen 0 und 100% liegen")
                return False
            
            # FC11R Konvertierung: percentage * 10 + 1999
            # Beispiel: 75.0% = 750 + 1999 = 2749
            raw_value = int(target_position * 10) + 1999
            
            # Write single register using VincerValve method
            success = self.sensor.write_VincerValve(start_address=self.POSITION_SETPOINT_REG, register_count=1, value=raw_value)
            
            if success:
                printTs(f'✅ {self.deviceName}: Sollposition {target_position}% (raw: {raw_value}) gesetzt')
                return True
            else:
                printTs(f'❌ {self.deviceName}: Fehler beim Setzen der Position {target_position}%')
                return False
                
        except Exception as e:
            printTs(f"❌ {self.deviceName}: Fehler beim Setzen der Position: {e}")
            return False

    def setRemoteOrLocalMode(self, newMode):
        """Switch valve to REMOTE (1) or LOCAL (0) mode - FC11R equivalent
        
        Args:
            newMode (int): 1 for REMOTE mode (AUTO), 0 for LOCAL mode (MANUAL)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if newMode not in [0, 1]:
                printTs(f"❌ {self.deviceName}: Ungültiger Modus {newMode}. Nur 0 (LOCAL) oder 1 (REMOTE) erlaubt")
                return False
                
            mode_name = "REMOTE-Modus (AUTO)" if newMode == 1 else "LOCAL-Modus (MANUAL)"
            
            success = self.sensor.write_VincerValve(start_address=self.REMOTE_LOCAL_REG, register_count=1, value=newMode)
            if success:
                printTs(f'✅ {self.deviceName}: {mode_name} aktiviert')
                return True
            else:
                printTs(f'❌ {self.deviceName}: Fehler beim Setzen des {mode_name}')
                return False
        except Exception as e:
            mode_name = "REMOTE-Modus (AUTO)" if newMode == 1 else "LOCAL-Modus (MANUAL)"
            printTs(f"❌ {self.deviceName}: Fehler beim Setzen des {mode_name}: {e}")
            return False

    def write_setpoint(self, setpoint_value):
        """Write setpoint - synchronized to prevent parallel Modbus access"""
        try:
            # Write to setpoint register (0x0002)
            self.sensor.write_VincerValve(start_address=0x0002, register_count=1, value=setpoint_value)
            printTs(f'OutletFlap Setpoint geschrieben: {setpoint_value}')
            return True
        except Exception as e:
            printTs(f"❌ {self.deviceName}: Fehler beim Schreiben des Setpoints: {e}")
            return False

    def write_remote_local(self, remote_local_value):
        """Write remote/local - synchronized to prevent parallel Modbus access"""
        try:
            # Write to remote/local register (0x0000)
            self.sensor.write_VincerValve(start_address=0x0000, register_count=1, value=remote_local_value)
            printTs(f'OutletFlap Remote/Local geschrieben: {remote_local_value}')
            return True
        except Exception as e:
            printTs(f"❌ {self.deviceName}: Fehler beim Schreiben von Remote/Local: {e}")
            return False

def signal_handler(sig, frame):
    print('Shutting down gracefully...')
    # TODO: Global statements fehlen - diese Zuweisungen sind momentan lokale Variablen
    # pumpRelaySw = False
    # co2RelaisSw = False
    # co2HeatingRelaySw = False
    # autoSwitch = False
    # powerButton = False
    runtime_tracker.stop() 
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
minimumPHValStop = 5
gpsEnabled = False  # Globale Initialisierung der GPS-Aktivierung

runtime_tracker = RuntimeTracker()
ph_handler = PhHandler("Ph", Ph_Sensor)
turbidity_handler = TurbidityHandler("Turbidity", Trub_Sensor)
turbidity_handler2 = TurbidityHandler("Turbidity2", Trub_Sensor2)
gps_handler = GpsHandler("Gps")
outlet_flap_handler = OutletFlapHandler("OutletFlap", OutletFlap_Sensor)
ph_handler.load_calibration()

# Vor der main-Funktion:
DATA_SEND_INTERVAL = 15  # Daten alle 60 Sekunden senden
last_send_time = time.time() - DATA_SEND_INTERVAL  # Stellt sicher, dass beim ersten Durchlauf Daten gesendet werden

# Device reading timing variables
last_outletflap_reading_time = 0  # Initialize to 0 to ensure first reading happens immediately
last_radar_reading_time = 0       # Initialize to 0 to ensure first reading happens immediately
last_ph_reading_time = 0          # Initialize to 0 to ensure first reading happens immediately
last_turbidity_reading_time = 0   # Initialize to 0 to ensure first reading happens immediately
last_turbidity2_reading_time = 0  # Initialize to 0 to ensure first reading happens immediately
last_us_reading_time = 0          # Initialize to 0 to ensure first reading happens immediately
last_us2_reading_time = 0          # Initialize to 0 to ensure first reading happens immediately
last_us3_reading_time = 0          # Initialize to 0 to ensure first reading happens immediately
        
isVersionSent = False

def check_initial_outletflap_position():
    """
    Check if the desired target position (from shared attribute) matches the current valve position.
    If not, set the valve to the desired position.
    Called once at startup after shared attributes are loaded.
    """
    global outletFlapActive, outletFlapTargetPosition
    
    try:
        # Only check if OutletFlap is active
        if not outletFlapActive:
            print("🔄 OutletFlap Startup: OutletFlap ist deaktiviert - keine Positionsprüfung")
            return
        
        # Read current valve position
        valve_data = outlet_flap_handler.read_valve_data()
        if not valve_data:
            print("❌ OutletFlap Startup: Fehler beim Lesen der aktuellen Position")
            return
        
        current_position = valve_data['current_position']
        print(f"🔄 OutletFlap Startup: Aktuelle Position: {current_position}%")
        print(f"🔄 OutletFlap Startup: Gewünschte Position: {outletFlapTargetPosition}%")
        
        # Compare with desired target position (allow small tolerance for floating point comparison)
        position_tolerance = 1.0  # 1% tolerance
        position_diff = abs(current_position - outletFlapTargetPosition)
        
        if position_diff > position_tolerance:
            print(f"📍 OutletFlap Startup: Position weicht ab ({position_diff:.1f}% Differenz)")
            print(f"📍 OutletFlap Startup: Setze Position auf {outletFlapTargetPosition}%")
            
            # Set valve to desired position
            success = outlet_flap_handler.set_valve_position(outletFlapTargetPosition)
            if success:
                print(f"✅ OutletFlap Startup: Position erfolgreich gesetzt")
            else:
                print(f"❌ OutletFlap Startup: Fehler beim Setzen der Position")
        else:
            print(f"✅ OutletFlap Startup: Position stimmt überein (Differenz: {position_diff:.1f}%)")
            
    except Exception as e:
        print(f"❌ OutletFlap Startup: Fehler bei Positionsprüfung: {e}")

def main():
    # Global Variables for Main Function (alphabetically sorted, max 4 per line)
    global autoSwitch, calculatedFlowRate, calibratePH, client
    global co2HeatingRelaySw, co2HeatingRelaySwSig, co2RelaisSw, co2RelaisSwSig
    global countdownPHHigh, countdownPHLow, flow_rate_l_h, flow_rate_l_min
    global flow_rate_m3_min, gemessener_high_wert, gemessener_low_wert, gps_handler
    global gpsEnabled, gpsHeight, gpsLatitude, gpsLongitude
    global gpsTimestamp, isDebugMode, isVersionSent, last_outletflap_reading_time
    global last_ph_reading_time, last_radar_reading_time, last_send_time, last_turbidity_reading_time
    global last_turbidity2_reading_time, last_us_reading_time, last_us2_reading_time, last_us3_reading_time, maximumPHVal, maximumTurbidity
    global maximumTurbidity2, measuredPHValue_telem, measuredTurbidity_telem, measuredTurbidity2_telem
    global messuredRadar_Air_telem, minimumPHVal, minimumPHValStop, outlet_flap_handler
    global outletFlapActive, outletFlapReadingsIntervalSec, outletFlapRegisterCurrentPosition, outletFlapRegisterErrorCode
    global outletFlapRegisterHasError, outletFlapRegisterIsLocalMode, outletFlapRegisterIsRemoteMode, outletFlapRegisterPositionValue
    global outletFlapRegisterRemoteOrLocalStatus, outletFlapRegisterSetpointPosition, outletFlapRegisterSetpointValue, outletFlapTargetPosition
    global ph_handler, ph_high_delay_start_time, ph_low_delay_start_time, phReadingsIntervalSec
    global powerButton, pumpRelaySw, pumpRelaySwSig, radar_flow_rate_l_min
    global radar_rate_Handler, radar_total_flow, radarReadingsIntervalSec, runtime_tracker
    global runtime_tracker_var, targetPHtolerrance, targetPHValue, telemetryTest420
    global telemetryTestNone, tempTruebSens, tempTruebSens2, temperaturPHSens_telem
    global turbidity_handler, turbidity_handler2, turbidity2Offset, turbidity2ReadingsIntervalSec
    global turbidity2SensorActive, turbidityOffset, turbidityReadingsIntervalSec, turbiditySensorActive
    global useDebugReadingsIntervalls
    global usFlowRate, usFlowTotal, usReadingsIntervalSec
    global us2FlowRate, us2FlowTotal, us2ReadingsIntervalSec
    global us3FlowRate, us3FlowTotal, us3ReadingsIntervalSec
    global usSensorActive, usSensor2Active, usSensor3Active, waterLevelHeight_telem

    print("=" * 25)
    print(f"OWIPEX-SPS, Version: {DEVELOPMENT_VERSION}")
    print("=" * 25)
    print("")
    print("Konfigurierte Leseintervalle:")
    print("-" * 29)
    print(f"  Main Loop Sleep:        {MAINLOOP_SLEEP_SEC} s")
    print(f"  Radar Sensor:           {radarReadingsIntervalSec} s")
    print(f"  US Flow Sensor 1:       {usReadingsIntervalSec} s")
    print(f"  US Flow Sensor 2:       {us2ReadingsIntervalSec} s")
    print(f"  US Flow Sensor 3:       {us3ReadingsIntervalSec} s")
    print(f"  PH Sensor:              {phReadingsIntervalSec} s")
    print(f"  Turbidity Sensor:       {turbidityReadingsIntervalSec} s")
    print(f"  Turbidity2 Sensor:      {turbidity2ReadingsIntervalSec} s")
    print(f"  OutletFlap Valve:       {outletFlapReadingsIntervalSec} s")
    print(f"  Telemetry Send:         {DATA_SEND_INTERVAL} s")
    print("")
    print(f"Intervall-Modus: {'DEBUG' if useDebugReadingsIntervalls else 'PRODUKTION'}")
    print(f"Debug-Modus: {'AKTIVIERT' if isDebugMode else 'DEAKTIVIERT'}")
    print("")

    # Initialisiere gpsEnabled mit Standardwert
    gpsEnabled = False
    
    saved_state = load_state()
    globals().update(saved_state)
    
    # Update reading intervals based on current UseDebugReadingsIntervalls setting
    update_reading_intervals()

    # Initialisiere Countdown-Werte, falls sie nicht gesetzt sind
    if countdownPHHigh is None:
        countdownPHHigh = ph_high_delay_duration
    if countdownPHLow is None:
        countdownPHLow = ph_low_delay_duration

    client = TBDeviceMqttClient(THINGSBOARD_SERVER, THINGSBOARD_PORT, ACCESS_TOKEN)
    client.connect()
    client.request_attributes(shared_keys=['powerButton', 'callGpsSwitch', 'gpsEnabled'], callback=sync_state)

    # Request shared attributes
    client.request_attributes(shared_keys=shared_attributes_keys, callback=attribute_callback)
    # Subscribe to individual attributes using the defined lists
    for attribute in shared_attributes_keys:
        client.subscribe_to_attribute(attribute, attribute_callback)
    client.set_server_side_rpc_request_handler(rpc_callback)

    radarTotalFlowManager = RadarTotalFlowManager()
    radarTotalFlowManager.start_periodic_save()

    # Initialisierung des GpsHandlers
    gps_handler = GpsHandler("Gps", update_interval=60)  # GPS-Daten alle 60 Sekunden aktualisieren
    
    # Nur GPS starten, wenn es aktiviert ist
    if gpsEnabled:
        try:
            gps_handler.start_gps_updates()
            print("GPS-Updates gestartet")
        except Exception as e:
            print(f"Fehler beim Starten der GPS-Updates: {e}")
            gpsEnabled = False
    else:
        print("GPS ist deaktiviert. Keine GPS-Updates werden gestartet.")
        gps_handler.gps_enabled = False  # Stelle sicher, dass auch der Handler weiß, dass GPS deaktiviert ist

    #Laden der alten werte (zweiter Durchlauf)
    saved_state = load_state()
    globals().update(saved_state)

    last_send_time = time.time()

    # Send HW and SW Version only once
    if not isVersionSent:
        version_attributes = {
            'SW-Version': "2.0.0",
            'HW-Version': "2.0.0"
        }
        client.send_attributes(version_attributes)
        isVersionSent = True  # Set flag to True after sending

    # Wait a short time for shared attributes to be loaded, then check OutletFlap position
    time.sleep(2)  # Give time for shared attributes to be received
    check_initial_outletflap_position()

    while not client.stopped:
        attributes, telemetry = get_data()
        #PH Initial
        
        runtime_tracker_var = runtime_tracker.get_total_runtime()   
        maximumPHVal = targetPHValue + targetPHtolerrance
        minimumPHVal = targetPHValue - targetPHtolerrance   
        pumpRelaySwSig = pumpRelaySw
        co2RelaisSwSig = co2RelaisSw
        co2HeatingRelaySwSig = co2HeatingRelaySw
        
        # Sichere Abfrage der GPS-Daten
        try:
            if gpsEnabled and gps_handler.gps_enabled:
                gpsTimestamp, gpsLatitude, gpsLongitude, gpsHeight = gps_handler.get_latest_gps_data()
            else:
                # Wenn GPS deaktiviert ist, setze Standardwerte
                gpsTimestamp, gpsLatitude, gpsLongitude, gpsHeight = None, 0.0, 0.0, 0.0
        except Exception as e:
            print(f"Fehler beim Abrufen der GPS-Daten: {e}")
            gpsTimestamp, gpsLatitude, gpsLongitude, gpsHeight = None, 0.0, 0.0, 0.0
            
        # client.send_attributes(attributes)

        current_time = time.time()
        if current_time - last_send_time >= DATA_SEND_INTERVAL:
            # Aktualisiere den letzten Sendungszeitpunkt
            last_send_time = current_time
            client.send_telemetry(telemetry)

        # Get current time once for all device timing checks
        device_check_time = time.time()
        
        if (radarSensorActive):
            # Check if enough time has passed since last Radar reading
            if device_check_time - last_radar_reading_time >= radarReadingsIntervalSec:
                # Update the last reading time
                last_radar_reading_time = device_check_time
                
                radar_rate_Handler = RadarHandler("Radar", Radar_Sensor)
                radar_flow_data = radar_rate_Handler.fetch_and_calculate()

                if radar_flow_data:
                    printTs("✅ Radar-Sensor: Lesung erfolgreich")
                    # Update the total flow using the calculated flow rate
                    radarTotalFlowManager.update_flow_rate(radar_flow_data['flow_rate_l_min'])
                    radar_total_flow = radarTotalFlowManager.total_flow
                    radar_flow_rate_l_min = radar_flow_data['flow_rate_m3_min']
                else:
                    printTs("❌ Radar-Sensor: Lesung fehlgeschlagen")

        if usSensorActive:
            # Check if enough time has passed since last US reading
            if device_check_time - last_us_reading_time >= usReadingsIntervalSec:
                # Update the last reading time
                last_us_reading_time = device_check_time
                
                # print(f"UsFlowSensor ist aktiv. Versuche Daten zu lesen...")
                try:
                    # print(f"Initialisiere UsFlowHandler mit Sensor ID: {Us_Sensor.device_id}")
                    us_flow_handler = UsHandler("Us", Us_Sensor)
                    usFlowRate, usFlowTotal, wasOk = us_flow_handler.fetchViaDeviceManager()
                    
                    if wasOk and usFlowRate is not None and usFlowTotal is not None:
                        printTs("✅ UsFlowSensor: Lesung erfolgreich")
                    else:
                        printTs("❌ UsFlowSensor: Unvollständige Daten")
                        
                except Exception as e:
                    printTs(f"❌ UsFlowSensor: Fehler beim Lesen: {e}")
                    import traceback
                    traceback.print_exc()
        # else:
        #     print("UsFlowSensor ist deaktiviert (usSensorActive = False)")

        if usSensor2Active:
            # Check if enough time has passed since last US reading
            if device_check_time - last_us2_reading_time >= us2ReadingsIntervalSec:
                # Update the last reading time
                last_us2_reading_time = device_check_time
                
                # print(f"UsFlowSensor 2 ist aktiv. Versuche Daten zu lesen...")
                try:
                    # print(f"Initialisiere UsFlowHandler 2 mit Sensor ID: {Us_Sensor2.device_id}")
                    us2_flow_handler = UsHandler("Us2", Us_Sensor2)
                    us2FlowRate, us2FlowTotal, wasOk2 = us2_flow_handler.fetchViaDeviceManager()
                    
                    if wasOk2 and us2FlowRate is not None and us2FlowTotal is not None:
                        printTs("✅ UsFlowSensor2: Lesung erfolgreich")
                    else:
                        printTs("❌ UsFlowSensor2: Unvollständige Daten")
                        
                except Exception as e:
                    printTs(f"❌ UsFlowSensor:2 Fehler beim Lesen: {e}")
                    import traceback
                    traceback.print_exc()
        # else:
        #     print("UsFlowSensor2 ist deaktiviert (usSensor2Active = False)")

        if usSensor3Active:
            # Check if enough time has passed since last US reading
            if device_check_time - last_us3_reading_time >= us3ReadingsIntervalSec:
                # Update the last reading time
                last_us3_reading_time = device_check_time
                
                # print(f"UsFlowSensor 3 ist aktiv. Versuche Daten zu lesen...")
                try:
                    # print(f"Initialisiere UsFlowHandler 3 mit Sensor ID: {Us_Sensor3.device_id}")
                    us3_flow_handler = UsHandler("Us3", Us_Sensor3)
                    us3FlowRate, us3FlowTotal, wasOk3 = us3_flow_handler.fetchViaDeviceManager()
                    
                    if wasOk3 and us3FlowRate is not None and us3FlowTotal is not None:
                        printTs("✅ UsFlowSensor3: Lesung erfolgreich")
                    else:
                        printTs("❌ UsFlowSensor3: Unvollständige Daten")
                        
                except Exception as e:
                    printTs(f"❌ UsFlowSensor:3 Fehler beim Lesen: {e}")
                    import traceback
                    traceback.print_exc()
        # else:
        #     print("UsFlowSensor3 ist deaktiviert (usSensor3Active = False)")
 
        if calibratePH:
            ph_handler.calibrate(high_ph_value=10, low_ph_value=7, measured_high=gemessener_high_wert, measured_low=gemessener_low_wert)
            ph_handler.save_calibration()
            calibratePH = False

        else:
            # Check if enough time has passed since last PH reading
            if device_check_time - last_ph_reading_time >= phReadingsIntervalSec:
                # Update the last reading time
                last_ph_reading_time = device_check_time
                
                measuredPHValue_telem, temperaturPHSens_telem = ph_handler.fetch_and_display_data()
                
                if measuredPHValue_telem is not None and temperaturPHSens_telem is not None:
                    # printTs("✅ PH-Sensor: Lesung erfolgreich")  # Entfernt - wird bereits bei der PH-Wert-Ausgabe angezeigt
                    pass
                else:
                    printTs("❌ PH-Sensor: Lesung fehlgeschlagen")
            
        # Check if enough time has passed since last Turbidity reading
        if turbiditySensorActive:
            if not calibratePH:
                if device_check_time - last_turbidity_reading_time >= turbidityReadingsIntervalSec:
                    # Update the last reading time
                    last_turbidity_reading_time = device_check_time
                
                    measuredTurbidity_telem, tempTruebSens = turbidity_handler.fetch_and_display_data()
                
                    if measuredTurbidity_telem is not None and tempTruebSens is not None:
                        # printTs("✅ Turbidity-Sensor: Lesung erfolgreich")  # Entfernt - wird bereits bei der Turbidity-Wert-Ausgabe angezeigt
                        pass
                    else:
                        printTs("❌ Turbidity-Sensor: Lesung fehlgeschlagen")

        if turbidity2SensorActive:
            if not calibratePH:
                if device_check_time - last_turbidity2_reading_time >= turbidity2ReadingsIntervalSec:
                    # Update the last reading time
                    last_turbidity2_reading_time = device_check_time
                
                    measuredTurbidity2_telem, tempTruebSens2 = turbidity_handler2.fetch_and_display_data()
                
                    if measuredTurbidity2_telem is not None and tempTruebSens2 is not None:
                        # printTs("✅ Turbidity2-Sensor: Lesung erfolgreich")  # Entfernt - wird bereits bei der Turbidity2-Wert-Ausgabe angezeigt
                        pass
                    else:
                        printTs("❌ Turbidity2-Sensor: Lesung fehlgeschlagen")

        if outletFlapActive:
            # Check if enough time has passed since last OutletFlap reading
            if device_check_time - last_outletflap_reading_time >= outletFlapReadingsIntervalSec:
                # Update the last reading time
                last_outletflap_reading_time = device_check_time
                
                enhanced_valve_data = outlet_flap_handler.read_valve_data()
                
                if enhanced_valve_data:
                    # Update enhanced telemetry variables
                    outletFlapRegisterCurrentPosition = enhanced_valve_data['current_position']
                    outletFlapRegisterSetpointPosition = enhanced_valve_data['setpoint_position']
                    outletFlapRegisterIsRemoteMode = enhanced_valve_data['is_remote_mode']
                    outletFlapRegisterIsLocalMode = enhanced_valve_data['is_local_mode']
                    outletFlapRegisterHasError = enhanced_valve_data['has_error']
                    
                    # Map enhanced data to register variable names
                    outletFlapRegisterRemoteOrLocalStatus = enhanced_valve_data['remote_local_status']
                    outletFlapRegisterPositionValue = enhanced_valve_data['raw_position_value']
                    outletFlapRegisterSetpointValue = enhanced_valve_data['raw_setpoint_value']
                    outletFlapRegisterErrorCode = enhanced_valve_data['error_code']
                else:
                    # Fallback values if enhanced reading fails
                    outletFlapRegisterCurrentPosition = None
                    outletFlapRegisterSetpointPosition = None
                    outletFlapRegisterIsRemoteMode = None
                    outletFlapRegisterIsLocalMode = None
                    outletFlapRegisterHasError = None
                    # Register variable fallbacks
                    outletFlapRegisterRemoteOrLocalStatus = None
                    outletFlapRegisterPositionValue = None
                    outletFlapRegisterSetpointValue = None
                    outletFlapRegisterErrorCode = None

        if powerButton:
            runtime_tracker.start()
            if autoSwitch:
                if measuredPHValue_telem is not None:
                    if measuredPHValue_telem is not None and measuredPHValue_telem > maximumPHVal:
                        co2RelaisSw = True
                        co2HeatingRelaySw = True
                        pumpRelaySw = False
                        if ph_high_delay_start_time is None:
                            ph_high_delay_start_time = time.time()
                        elif time.time() - ph_high_delay_start_time >= ph_high_delay_duration:
                            autoSwitch = False
                            powerButton = False

                        countdownPHHigh = ph_high_delay_duration - (time.time() - ph_high_delay_start_time)
                    else:
                        ph_high_delay_start_time = None
                        countdownPHHigh = ph_high_delay_duration  # Zurücksetzen des Countdowns, wenn der pH-Wert unter den Maximalwert fällt

                    if measuredPHValue_telem < minimumPHVal:
                        if measuredPHValue_telem < minimumPHValStop:
                            autoSwitch = False
                            powerButton = False
                        if ph_low_delay_start_time is None:
                            ph_low_delay_start_time = time.time()
                        elif time.time() - ph_low_delay_start_time >= ph_low_delay_duration:
                            autoSwitch = False
                            powerButton = False
                        countdownPHLow = ph_low_delay_duration - (time.time() - ph_low_delay_start_time)
                    else:
                        ph_low_delay_start_time = None

                    # Wenn der pH-Wert innerhalb des erlaubten Fensters liegt:
                    if minimumPHVal <= measuredPHValue_telem <= maximumPHVal:
                        pumpRelaySw = True
                        co2RelaisSw = False
                        co2HeatingRelaySw = False

            else:
                # print("automode OFF", autoSwitch)
                pumpRelaySw = False
                co2RelaisSw = False
                co2HeatingRelaySw = False
                ph_low_delay_start_time = None
                ph_high_delay_start_time = None
                countdownPHLow = ph_low_delay_duration
                countdownPHHigh = ph_high_delay_duration
                
        else:
            # print("Power Switch OFF.", powerButton)        
            pumpRelaySw = False
            co2RelaisSw = False
            co2HeatingRelaySw = False
            autoSwitch = False
            countdownPHLow = ph_low_delay_duration
            countdownPHHigh = ph_high_delay_duration
            runtime_tracker.stop() 
            time.sleep(2)
        
        # Main loop sleep to reduce CPU usage
        if MAINLOOP_SLEEP_SEC > 0:
            time.sleep(MAINLOOP_SLEEP_SEC)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    if ACCESS_TOKEN != "TEST_TOKEN":
        main()
    else:
        print("Please change the ACCESS_TOKEN variable to match your device access token and run the")