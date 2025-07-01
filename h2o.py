import sys
sys.path.append('/home/owipex_adm/owipex-sps/libs')
CONFIG_PATH = "/etc/owipex/"

# Version number following the specified format
ProgVers = "2.31"

# Device enable flags
isRadarEnabled = False
isTrubEnabled = False
isPhEnabled = True
isOutletFlapEnabled = True
isGpsEnabled = False

# OutletFlap sub-control flag (controlled via ThingsBoard)
isOutletFlapActive = False

import signal
import logging.handlers
import time
import os
import libs.gpsDataLib as gpsDataLib
import json
import threading

from periphery import GPIO
from threading import Thread
from tb_gateway_mqtt import TBDeviceMqttClient
from libs.modbus_lib import DeviceManager
from time import sleep
from libs.FlowCalculation import FlowCalculation

from dotenv import load_dotenv
dotenv_path = '/etc/owipex/.env'
load_dotenv(dotenv_path=dotenv_path)
ACCESS_TOKEN = os.environ.get('THINGSBOARD_ACCESS_TOKEN')
THINGSBOARD_SERVER = 'localhost'  # Replace with your Thingsboard server address
THINGSBOARD_PORT = 1883

#RS485 Comunication and Devices
# Create DeviceManager
dev_manager = DeviceManager(port='/dev/ttyS0', baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=1)
dev_manager.add_device(device_id=1)
dev_manager.add_device(device_id=2)
dev_manager.add_device(device_id=3)
dev_manager.add_device(device_id=10)
# Get devices and read their registers
Radar_Sensor = dev_manager.get_device(device_id=1)
Trub_Sensor = dev_manager.get_device(device_id=2)
PH_Sensor = dev_manager.get_device(device_id=3)
OutletFlap = dev_manager.get_device(device_id=10)
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

 #that will be called when the value of our Shared Attribute changes
def attribute_callback(result, _):
    global gps_handler, gpsEnabled, isOutletFlapActive, powerButton
    
    # Aktualisiere globale Variablen
    globals().update({key: result[key] for key in result if key in globals()})
    
    # Überprüfe, ob sich gpsEnabled geändert hat
    if 'gpsEnabled' in result:
        gpsEnabled = result['gpsEnabled']
        if isGpsEnabled and gpsEnabled:
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
    
    # Dynamische OutletFlap Heartbeat Kontrolle bei isOutletFlapActive-Änderung
    if 'isOutletFlapActive' in result:
        old_active = isOutletFlapActive
        isOutletFlapActive = result['isOutletFlapActive']
        print(f"OutletFlap Active-Status: {old_active} → {isOutletFlapActive}")
        
        # Dynamischer Heartbeat Start/Stop bei Änderung
        if old_active != isOutletFlapActive:
            start_heartbeat_if_needed()
    
    # OutletFlap Commands - NUR wenn powerButton=True UND beide Flags aktiv
    if powerButton and isOutletFlapEnabled and isOutletFlapActive:
        if 'outletFlapTargetPosition' in result:
            target_pos = result['outletFlapTargetPosition']
            if isinstance(target_pos, (int, float)) and 0 <= target_pos <= 100:
                print(f"📍 OutletFlap Zielposition: {target_pos}%")
                outlet_flap_handler.set_valve_position(target_pos)
            else:
                print(f"❌ Ungültige OutletFlap Position: {target_pos}")
        
        if 'outletFlapSetRemoteMode' in result and result['outletFlapSetRemoteMode']:
            print("🔄 OutletFlap: Wechsle zu REMOTE-Modus (AUTO)")
            outlet_flap_handler.set_remote_mode()
        
        if 'outletFlapSetLocalMode' in result and result['outletFlapSetLocalMode']:
            print("🔄 OutletFlap: Wechsle zu LOCAL-Modus (MANUAL)")
            outlet_flap_handler.set_local_mode()
    else:
        # Log why commands are ignored
        if 'outletFlapTargetPosition' in result or 'outletFlapSetRemoteMode' in result or 'outletFlapSetLocalMode' in result:
            if not powerButton:
                print("⚠️ OutletFlap Commands ignoriert - powerButton=False")
            elif not (isOutletFlapEnabled and isOutletFlapActive):
                print("⚠️ OutletFlap Commands ignoriert - Flags nicht beide aktiv")
    
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
        'HW-Version': "2.0.0"
    }
    telemetry = {key: globals()[key] for key in telemetry_keys if key in globals()}
    telemetry['Prog-Version'] = ProgVers

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
        period = result.get('shared', {'powerButton': False})['powerButton']

class RuntimeTracker:
    def __init__(self, filename="run_time.txt"):
        self.start_time = None
        self.total_runtime = 0
        self.filename = os.path.join(CONFIG_PATH, filename)  # Diese Zeile behalten
        
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
        self.update_interval = update_interval
        self.callGpsSwitch = False
        self.latest_gps_data = (None, None, None, None)
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
    def __init__(self, sensor):
        self.sensor = sensor  # Hier übergeben Sie die Trub_Sensor-Instanz

    def fetch_and_display_data(self, turbiditySensorActive):
        if turbiditySensorActive:
            try:
                measuredTurbidity_telem = self.sensor.read_register(start_address=0x0001, register_count=2)
                tempTruebSens = self.sensor.read_register(start_address=0x0003, register_count=2)
                print(f'✅ Trueb: {measuredTurbidity_telem}, Trueb Temp Sens: {tempTruebSens}')
                return measuredTurbidity_telem, tempTruebSens
            except Exception as e:
                print(f'❌ Trubidity Sensor: ERROR - {e}')
                return None, None
        else:
            print("TruebOFF", turbiditySensorActive)
            return None, None

class PHHandler:
    def __init__(self, sensor):
        self.sensor = sensor  # Übergeben Sie die PH_Sensor-Instanz
        self.slope = 1  # Anfangswert, wird durch Kalibrierung aktualisiert
        self.intercept = 0  # Anfangswert, wird durch Kalibrierung aktualisiert
        self.load_calibration()  # Laden der Kalibrierungsdaten beim Start

    def fetch_and_display_data(self):
        try:
            raw_ph_value = self.sensor.read_register(start_address=0x0001, register_count=2)
            if raw_ph_value is None:
                raise ValueError("PH Sensorlesung fehlgeschlagen. Überprüfen Sie die Verbindung.")
            else:
                print(f'✅ PH: {raw_ph_value}')
        except Exception as e:
            print(f"❌ PH Sensor: ERROR - {e}")
            return None, None

        measuredPHValue_telem = self.correct_ph_value(raw_ph_value)
        
        # Try to read temperature with error handling
        try:
            temperaturPHSens_telem = self.sensor.read_register(start_address=0x0003, register_count=2)
        except Exception as e:
            print(f"❌ PH Temperature Sensor: ERROR - {e}")
            temperaturPHSens_telem = None
        
        print(f'✅ PH: {measuredPHValue_telem}, Temperature PH Sens: {temperaturPHSens_telem}, RAW_PH: {raw_ph_value}')
        return measuredPHValue_telem, temperaturPHSens_telem

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

class FlowRateHandler:
    def __init__(self, radar_sensor):
        self.radar_sensor = radar_sensor
        
        # Pfad zur Kalibrierungsdatei aktualisieren
        calibration_file_path = os.path.join(CONFIG_PATH, "calibration_data.json")
        
        # Prüfung und Reparatur der Kalibrierungsdatei
        self.calibration_data = self.load_or_repair_calibration(calibration_file_path)
        
        self.flow_calculator = FlowCalculation(calibration_file_path)
        
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
        except Exception as e:
            print(f"❌ Radar Sensor: ERROR - {e}")
            return None

        water_level = self.zero_reference - measured_air_distance
        print(f"✅ Hoehe: {water_level} mm")
        flow_rate = self.flow_calculator.calculate_flow_rate(water_level)
        print(f"✅ Flow Rate (L/s): {flow_rate}")

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


class OutletFlapHandler:
    def __init__(self, sensor, name="OutletFlap"):
        self.sensor = sensor  # Übergeben Sie die OutletFlap-Instanz
        self.name = name
        
        # Heartbeat attributes
        self.running = False
        self.heartbeat_thread = None
        self.last_position = None
        self.heartbeat_interval = 5  # seconds
        
        # CRITICAL: Lock für Modbus-Zugriffe - verhindert parallele Kommunikation
        self.sensor_lock = threading.Lock()
        
        # FC11R Register Definitions (from valve_actuator.py pattern)
        self.REMOTE_LOCAL_REG = 0x0000      # Remote/Local Control (0=Local, 1=Remote)
        self.POSITION_FEEDBACK_REG = 0x0001  # Istposition lesen (read only)
        self.POSITION_SETPOINT_REG = 0x0002  # Sollposition schreiben (read/write)
        self.ERROR_CODE_REG = 0x0003         # Fehlercode (read only)
        self.TEST_REG = 0x0004               # Test register

    def start_heartbeat(self):
        """Start heartbeat communication every 5 seconds"""
        self.running = True
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()
        print(f"💓 {self.name} Heartbeat gestartet (alle 5s)")
        
    def stop_heartbeat(self):
        """Stop heartbeat communication"""
        self.running = False
        if self.heartbeat_thread:
            self.heartbeat_thread.join()
        print(f"💓 {self.name} Heartbeat gestoppt")
        
    def _heartbeat_loop(self):
        """Internal heartbeat loop - prevents E1 alarm"""
        while self.running:
            try:
                # WARTEN auf freien Modbus-Zugriff - KEINE parallelen Zugriffe!
                with self.sensor_lock:
                    remote_local, valve_position, setpoint, error_code, test_register = self._read_sensor_data()
                
                # Nur loggen wenn sich Position geändert hat
                if valve_position != self.last_position and valve_position is not None:
                    print(f"💓 {self.name} - Position: {valve_position}%, Error: {error_code}")
                    self.last_position = valve_position
                    
            except Exception as e:
                print(f"💓 {self.name} Heartbeat Fehler: {e}")
                
            time.sleep(self.heartbeat_interval)

    def fetch_and_display_data(self):
        """Normal sensor read - synchronized with heartbeat to prevent parallel Modbus access"""
        # WARTEN bis Heartbeat-Modbus-Zugriff fertig ist
        with self.sensor_lock:
            return self._read_sensor_data()
    
    def _read_sensor_data(self):
        """Internal method for actual sensor reading - ALWAYS use with lock!"""
        try:
            remote_local = self.sensor.read_register(start_address=0x0000, register_count=1)
            valve_position = self.sensor.read_register(start_address=0x0001, register_count=1)
            setpoint = self.sensor.read_register(start_address=0x0002, register_count=1)
            error_code = self.sensor.read_register(start_address=0x0003, register_count=1)
            test_register = self.sensor.read_register(start_address=0x0004, register_count=1)
            
            # Check if all values are None (failed reading)
            if all(value is None for value in [remote_local, valve_position, setpoint, error_code, test_register]):
                print(f'❌ {self.name} - All readings failed: Remote/Local: {remote_local}, Position: {valve_position}, Setpoint: {setpoint}, Error: {error_code}, Test: {test_register}')
                return None, None, None, None, None
            else:
                print(f'✅ {self.name} - Remote/Local: {remote_local}, Position: {valve_position}, Setpoint: {setpoint}, Error: {error_code}, Test: {test_register}')
                return remote_local, valve_position, setpoint, error_code, test_register
        except Exception as e:
            print(f"❌ {self.name}: ERROR - {e}")
            return None, None, None, None, None

    def read_valve_data(self):
        """NEUE Methode - Enhanced valve reading mit FC11R-spezifischer Datenkonvertierung"""
        with self.sensor_lock:
            try:
                # Istposition mit FC11R-Konvertierung: (raw_value - 1999) / 10.0
                raw_position = self.sensor.read_register(start_address=self.POSITION_FEEDBACK_REG, register_count=1)
                current_position = (raw_position - 1999) / 10.0 if raw_position is not None and raw_position >= 1999 else 0.0
                
                time.sleep(0.05)  # Kurze Pause zwischen Abfragen
                
                # Remote/Local Status (0=Local/Manual, 1=Remote/Auto)
                remote_local = self.sensor.read_register(start_address=self.REMOTE_LOCAL_REG, register_count=1) or 0
                
                time.sleep(0.05)
                
                # Sollposition mit FC11R-Konvertierung
                setpoint_raw = self.sensor.read_register(start_address=self.POSITION_SETPOINT_REG, register_count=1)
                setpoint_position = (setpoint_raw - 1999) / 10.0 if setpoint_raw is not None and setpoint_raw >= 1999 else 0.0
                
                time.sleep(0.05)
                
                # Fehlercode
                error_code = self.sensor.read_register(start_address=self.ERROR_CODE_REG, register_count=1) or 0
                
                print(f'✅ {self.name} Enhanced - Current: {current_position}%, Setpoint: {setpoint_position}%, Mode: {"REMOTE" if remote_local == 1 else "LOCAL"}, Error: {error_code}')
                
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
                print(f"❌ {self.name} read_valve_data Error: {e}")
                return None

    def set_valve_position(self, target_position):
        """Set valve position mit FC11R-Konvertierung (0-100%)"""
        with self.sensor_lock:
            try:
                if not (0 <= target_position <= 100):
                    print(f"❌ {self.name}: Position muss zwischen 0 und 100% liegen")
                    return False
                
                # FC11R Konvertierung: percentage * 10 + 1999
                # Beispiel: 75.0% = 750 + 1999 = 2749
                raw_value = int(target_position * 10) + 1999
                
                # Write single register (wie in valve_actuator.py)
                success = self.sensor.write_register(start_address=self.POSITION_SETPOINT_REG, register_count=1, value=raw_value)
                
                if success:
                    print(f'✅ {self.name}: Sollposition {target_position}% (raw: {raw_value}) gesetzt')
                    return True
                else:
                    print(f'❌ {self.name}: Fehler beim Setzen der Position {target_position}%')
                    return False
                    
            except Exception as e:
                print(f"❌ {self.name}: Fehler beim Setzen der Position: {e}")
                return False

    def set_remote_mode(self):
        """Switch to REMOTE mode (AUTO) - FC11R equivalent"""
        with self.sensor_lock:
            try:
                success = self.sensor.write_register(start_address=self.REMOTE_LOCAL_REG, register_count=1, value=1)
                if success:
                    print(f'✅ {self.name}: REMOTE-Modus (AUTO) aktiviert')
                    return True
                else:
                    print(f'❌ {self.name}: Fehler beim Setzen des REMOTE-Modus')
                    return False
            except Exception as e:
                print(f"❌ {self.name}: Fehler beim Setzen des REMOTE-Modus: {e}")
                return False

    def set_local_mode(self):
        """Switch to LOCAL mode (MANUAL) - FC11R equivalent"""
        with self.sensor_lock:
            try:
                success = self.sensor.write_register(start_address=self.REMOTE_LOCAL_REG, register_count=1, value=0)
                if success:
                    print(f'✅ {self.name}: LOCAL-Modus (MANUAL) aktiviert')
                    return True
                else:
                    print(f'❌ {self.name}: Fehler beim Setzen des LOCAL-Modus')
                    return False
            except Exception as e:
                print(f"❌ {self.name}: Fehler beim Setzen des LOCAL-Modus: {e}")
                return False

    def write_setpoint(self, setpoint_value):
        """Write setpoint - synchronized to prevent parallel Modbus access"""
        # WARTEN bis andere Modbus-Zugriffe fertig sind
        with self.sensor_lock:
            try:
                # Write to setpoint register (0x0002)
                self.sensor.write_register(start_address=0x0002, register_count=1, value=setpoint_value)
                print(f'OutletFlap Setpoint geschrieben: {setpoint_value}')
                return True
            except Exception as e:
                print(f"Fehler beim Schreiben des Setpoints: {e}")
                return False

    def write_remote_local(self, remote_local_value):
        """Write remote/local - synchronized to prevent parallel Modbus access"""
        # WARTEN bis andere Modbus-Zugriffe fertig sind
        with self.sensor_lock:
            try:
                # Write to remote/local register (0x0000)
                self.sensor.write_register(start_address=0x0000, register_count=1, value=remote_local_value)
                print(f'OutletFlap Remote/Local geschrieben: {remote_local_value}')
                return True
            except Exception as e:
                print(f"Fehler beim Schreiben von Remote/Local: {e}")
                return False

class TotalFlowManager:
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


def signal_handler(sig, frame):
    print('Shutting down gracefully...')
    
    # Stop OutletFlap Heartbeat (falls läuft)
    if outlet_flap_handler.running:
        try:
            outlet_flap_handler.stop_heartbeat()
            print("OutletFlap Heartbeat gestoppt")
        except Exception as e:
            print(f"Fehler beim Stoppen des OutletFlap Heartbeat: {e}")
    
    pumpRelaySw = False
    co2RelaisSw = False
    co2HeatingRelaySw = False
    autoSwitch = False
    powerButton = False
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
ph_handler = PHHandler(PH_Sensor)
turbidity_handler = TurbidityHandler(Trub_Sensor)
gps_handler = GPSHandler()
outlet_flap_handler = OutletFlapHandler(OutletFlap, name="OutletFlap")
ph_handler.load_calibration()

# Vor der main-Funktion:
DATA_SEND_INTERVAL = 15  # Daten alle 60 Sekunden senden
last_send_time = time.time() - DATA_SEND_INTERVAL  # Stellt sicher, dass beim ersten Durchlauf Daten gesendet werden
        
isVersionSent = False

def start_heartbeat_if_needed():
    """Dynamischer Heartbeat Start/Stop - nur wenn beide Flags aktiv"""
    global isOutletFlapEnabled, isOutletFlapActive, outlet_flap_handler
    
    if isOutletFlapEnabled and isOutletFlapActive:
        if not outlet_flap_handler.running:
            try:
                outlet_flap_handler.start_heartbeat()
                print("💓 OutletFlap Heartbeat gestartet (beide Flags aktiv)")
            except Exception as e:
                print(f"Fehler beim Starten des OutletFlap Heartbeat: {e}")
    else:
        if outlet_flap_handler.running:
            try:
                outlet_flap_handler.stop_heartbeat()
                print("💓 OutletFlap Heartbeat gestoppt (Flag(s) inaktiv)")
            except Exception as e:
                print(f"Fehler beim Stoppen des OutletFlap Heartbeat: {e}")

def main():
    #def Global Variables for Main Funktion
    global isVersionSent, last_send_time, total_flow, ph_low_delay_start_time,ph_high_delay_start_time, runtime_tracker_var, minimumPHValStop, maximumPHVal, minimumPHVal, ph_handler, turbidity_handler, gps_handler, runtime_tracker, client, countdownPHLow, powerButton, tempTruebSens, countdownPHHigh, targetPHtolerrance, targetPHValue, calibratePH, gemessener_low_wert, gemessener_high_wert, autoSwitch, temperaturPHSens_telem, measuredPHValue_telem, measuredTurbidity_telem, gpsTimestamp, gpsLatitude, gpsLongitude, gpsHeight, waterLevelHeight_telem, calculatedFlowRate, messuredRadar_Air_telem, flow_rate_l_min, flow_rate_l_h, flow_rate_m3_min, co2RelaisSwSig, co2HeatingRelaySwSig, pumpRelaySwSig, co2RelaisSw, co2HeatingRelaySw, pumpRelaySw, flow_rate_handler, gpsEnabled, outlet_flap_handler, outletFlapActive, outletFlapRemoteLocal, outletFlapValvePosition, outletFlapSetpoint, outletFlapErrorCode, outletFlapTest, isOutletFlapActive, outletFlapCurrentPosition, outletFlapSetpointPosition, outletFlapRemoteMode, outletFlapLocalMode, outletFlapHasError

    # Display version at startup
    print(f"\n{'='*50}")
    print(f"OWIPEX SPS - Water Quality Control System")
    print(f"Version: {ProgVers}")
    print(f"{'='*50}\n")

    # Initialisiere gpsEnabled mit Standardwert
    gpsEnabled = False
    
    saved_state = load_state()
    globals().update(saved_state)

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

    total_flow_manager = TotalFlowManager()
    total_flow_manager.start_periodic_save()

    # Initialisierung des GPSHandlers
    gps_handler = GPSHandler(update_interval=60)  # GPS-Daten alle 60 Sekunden aktualisieren
    
    # Nur GPS starten, wenn es aktiviert ist
    if isGpsEnabled and gpsEnabled:
        try:
            gps_handler.start_gps_updates()
            print("GPS-Updates gestartet")
        except Exception as e:
            print(f"Fehler beim Starten der GPS-Updates: {e}")
            gpsEnabled = False
    else:
        print("GPS ist deaktiviert. Keine GPS-Updates werden gestartet.")
        gps_handler.gps_enabled = False  # Stelle sicher, dass auch der Handler weiß, dass GPS deaktiviert ist

    # Dynamische OutletFlap Heartbeat Kontrolle (beide Flags müssen aktiv sein)
    start_heartbeat_if_needed()

    #Laden der alten werte
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
            if isGpsEnabled and gpsEnabled and gps_handler.gps_enabled:
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

        if isRadarEnabled and radarSensorActive:
            flow_rate_handler = FlowRateHandler(Radar_Sensor)
            flow_data = flow_rate_handler.fetch_and_calculate()

            if flow_data:
                # Update the total flow using the calculated flow rate
                total_flow_manager.update_flow_rate(flow_data['flow_rate_l_min'])
                total_flow = total_flow_manager.total_flow
                flow_rate_l_min = flow_data['flow_rate_m3_min']

        if calibratePH:
            ph_handler.calibrate(high_ph_value=10, low_ph_value=7, measured_high=gemessener_high_wert, measured_low=gemessener_low_wert)
            ph_handler.save_calibration()
            calibratePH = False

        else:
            if isPhEnabled:
                measuredPHValue_telem, temperaturPHSens_telem = ph_handler.fetch_and_display_data()  
            if isTrubEnabled:
                measuredTurbidity_telem, tempTruebSens = turbidity_handler.fetch_and_display_data(turbiditySensorActive)

        # OutletFlap data reading - ALTE Methode (für Kompatibilität)
        if isOutletFlapEnabled:
            outletFlapRemoteLocal, outletFlapValvePosition, outletFlapSetpoint, outletFlapErrorCode, outletFlapTest = outlet_flap_handler.fetch_and_display_data()
        
        # OutletFlap Enhanced data reading - NEUE Methode (nur wenn beide Flags aktiv)
        if isOutletFlapEnabled and isOutletFlapActive:
            enhanced_valve_data = outlet_flap_handler.read_valve_data()
            if enhanced_valve_data:
                # Update enhanced telemetry variables
                outletFlapCurrentPosition = enhanced_valve_data['current_position']
                outletFlapSetpointPosition = enhanced_valve_data['setpoint_position']
                outletFlapRemoteMode = enhanced_valve_data['is_remote_mode']
                outletFlapLocalMode = enhanced_valve_data['is_local_mode']
                outletFlapHasError = enhanced_valve_data['has_error']
            else:
                # Fallback values if enhanced reading fails
                outletFlapCurrentPosition = None
                outletFlapSetpointPosition = None
                outletFlapRemoteMode = False
                outletFlapLocalMode = True
                outletFlapHasError = True

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
                print("automode OFF", autoSwitch)
                pumpRelaySw = False
                co2RelaisSw = False
                co2HeatingRelaySw = False
                ph_low_delay_start_time = None
                ph_high_delay_start_time = None
                countdownPHLow = ph_low_delay_duration
                countdownPHHigh = ph_high_delay_duration
                
        else:
            print("Power Switch OFF.", powerButton)        
            pumpRelaySw = False
            co2RelaisSw = False
            co2HeatingRelaySw = False
            autoSwitch = False
            countdownPHLow = ph_low_delay_duration
            countdownPHHigh = ph_high_delay_duration
            runtime_tracker.stop() 
            time.sleep(2)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    if ACCESS_TOKEN != "TEST_TOKEN":
        main()
    else:
        print("Please change the ACCESS_TOKEN variable to match your device access token and run the")