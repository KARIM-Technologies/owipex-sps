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

# TAOSONICFLOWUNIT Konstanten
TAOSONICFLOWUNIT_M3 = 0       # Cubic meter (m3)
TAOSONICFLOWUNIT_LITER = 1    # Liter (L)
TAOSONICFLOWUNIT_GAL = 2      # American gallon (GAL)
TAOSONICFLOWUNIT_FEET3 = 3    # Cubic feet (CF)

#RS485 Comunication and Devices
# Create DeviceManager
dev_manager = DeviceManager(port='/dev/ttyS0', baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=1)
dev_manager.add_device(device_id=0x01)
dev_manager.add_device(device_id=0x02)
dev_manager.add_device(device_id=0x03)
dev_manager.add_device(device_id=0x28)  # Neuer US Flow Sensor
# Get devices and read their registers
Radar_Sensor = dev_manager.get_device(device_id=0x01)
Trub_Sensor = dev_manager.get_device(device_id=0x02)
PH_Sensor = dev_manager.get_device(device_id=0x03)
US_Flow_Sensor = dev_manager.get_device(device_id=0x28)  # Neuer US Flow Sensor
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
    global gps_handler, gpsEnabled, usFlowSensorActive
    
    print(f"DEBUG ATTRIBUTE CALLBACK START: result={result}")
    print(f"DEBUG ATTRIBUTE CALLBACK: usFlowSensorActive before update = {usFlowSensorActive}")
    
    # Aktualisiere globale Variablen
    globals().update({key: result[key] for key in result if key in globals()})
    
    print(f"DEBUG ATTRIBUTE CALLBACK: usFlowSensorActive after update = {usFlowSensorActive}")
    
    # Spezifische Behandlung für usFlowSensorActive
    if 'usFlowSensorActive' in result:
        usFlowSensorActive = result['usFlowSensorActive']
        print(f"DEBUG ATTRIBUTE CALLBACK: usFlowSensorActive directly set = {usFlowSensorActive}")
    
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
    
    # Speichere den Zustand
    state_to_save = {key: globals()[key] for key in shared_attributes_keys if key in globals()}
    print(f"DEBUG ATTRIBUTE CALLBACK: Saving state: {state_to_save}")
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
            measuredTurbidity_telem = self.sensor.read_register(start_address=0x0001, register_count=2)
            tempTruebSens = self.sensor.read_register(start_address=0x0003, register_count=2)
            print(f'Trueb: {measuredTurbidity_telem}, Trueb Temp Sens: {tempTruebSens}')
            return measuredTurbidity_telem, tempTruebSens
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
                raise ValueError("Sensorlesung fehlgeschlagen. Überprüfen Sie die Verbindung.")
        except Exception as e:
            print(f"Fehler bei der Sensorablesung für PHHandler: {e}")
            return None, None

        measuredPHValue_telem = self.correct_ph_value(raw_ph_value)
        temperaturPHSens_telem = self.sensor.read_register(start_address=0x0003, register_count=2)
        
        print(f'PH: {measuredPHValue_telem}, Temperature PH Sens: {temperaturPHSens_telem}, RAW_PH: {raw_ph_value}')
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
            print(f"Fehler beim Lesen des Radar-Sensors: {e}")
            return None

        water_level = self.zero_reference - measured_air_distance
        print(f"Hoehe: {water_level} mm")
        flow_rate = self.flow_calculator.calculate_flow_rate(water_level)
        print(f"Flow Rate (L/s): {flow_rate}")

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

class UsFlowHandler:

    def __init__(self, sensor):
        self.sensor = sensor  # Übergeben Sie die PH_Sensor-Instanz

    # def fetchViaDeviceManager_Helper(self, address, registerCount, dataformat, infoText):
    #     # get current flow
    #     try:
    #         value = self.sensor.read_register(address, registerCount, dataformat)
    #         if value is None:
    #             raise ValueError(f"US-Flow sensor reading {infoText} failed. Check the connection.")
    #         return value
    #     except Exception as e:
    #         print(f"DEBUG: Error reading register: {e}")
    #         raise

    def fetchViaDeviceManager_ForTaoSonicOnly_Helper(self, address, registerCount, dataformat, infoText):
        print(f"DEBUG: Lese Register: Adresse={address}, Anzahl={registerCount}, Format={dataformat}, Info={infoText}")
        try:
            # Rohwerte können nicht direkt ausgelesen werden, da die Methode read_registers nicht existiert
            # Wir verwenden stattdessen die vorhandene read_register Methode
            
            # Formatierte Werte lesen
            value = self.sensor.read_register_FOR_TAOSONIC_ONLY(address, registerCount, dataformat)
            print(f"DEBUG: Gelesener Wert: {value}")
            if value is None:
                print(f"DEBUG: Wert ist None!")
                raise ValueError(f"Us-Flow Sensorlesung {infoText} fehlgeschlagen. Überprüfen Sie die Verbindung.")
            return value
        except Exception as e:
            print(f"DEBUG: Fehler beim Lesen des Registers: {e}")
            raise

    def calculateSumFlowValueForTaosonic(self, totalFlowUnitNumber, totalFlowMultiplier, flowValueAccumulator, flowDecimalFraction):
        # The internal accumulator is been presented by a LONG number for the integer part together
        # with a REAL number for the decimal fraction. In general uses, only the integer part needs to be read. Reading
        # the fraction can be omitted. The final accumulator result has a relation with unit and multiplier. Assume N
        # stands for the integer part (for the positive accumulator, the integer part is the content of REG 0009, 0010, a
        # 32-bits signed LONG integer,), Nf stands for the decimal fraction part (for the positive accumulator, the
        # fraction part is the content of REG 0011, 0012, a 32-bits REAL float number,), n stands for the flow decimal
        # point (REG 1439).
        # then
        # The final positive flow rate=(N+Nf ) ×10n-3 (in unit decided by REG 1439)
        # The meaning of REG 1438 which has a range of 0~3 is as following:
        #     0 cubic meter (m3)
        #     1 liter (L)
        #     2 American gallon (GAL)
        #     3 Cubic feet (CF)
        # For example, if REG0009=123456789, REG0010=0.123, and REG1439=-1, REG1438=0
        # Then the positive flow is 12345.6789123 m3

        print(f"DEBUG: Calculation inputs: unitNumber={totalFlowUnitNumber}, multiplier={totalFlowMultiplier}, accumulator={flowValueAccumulator}, fraction={flowDecimalFraction}")

        # Validate input types
        if not isinstance(totalFlowMultiplier, int):
            print(f"WARNING: Invalid type for multiplier: {type(totalFlowMultiplier)}, converting to int")
            try:
                totalFlowMultiplier = int(totalFlowMultiplier)
            except:
                totalFlowMultiplier = 0
                print(f"ERROR: Could not convert multiplier to int, using 0")

        # Validate multiplier range
        if totalFlowMultiplier < -4 or totalFlowMultiplier > 4:
            print(f"WARNING: Multiplier {totalFlowMultiplier} out of range, clamping to valid range")
            totalFlowMultiplier = max(-4, min(4, totalFlowMultiplier))

        # Validate unit number
        if totalFlowUnitNumber not in [TAOSONICFLOWUNIT_M3, TAOSONICFLOWUNIT_LITER, TAOSONICFLOWUNIT_GAL, TAOSONICFLOWUNIT_FEET3]:
            print(f"WARNING: Invalid unit number {totalFlowUnitNumber}, defaulting to M3")
            totalFlowUnitNumber = TAOSONICFLOWUNIT_M3

        # Convert accumulator to float
        try:
            flowValueAccumulatorAsFloat = float(flowValueAccumulator)
        except:
            flowValueAccumulatorAsFloat = 0.0
            print(f"ERROR: Failed to convert accumulator to float, using 0.0")

        # Ensure decimal fraction is between 0 and 1
        if flowDecimalFraction < 0 or flowDecimalFraction > 1:
            print(f"WARNING: Decimal fraction {flowDecimalFraction} out of range (0-1), using 0.0")
            flowDecimalFraction = 0.0

        # Calculate with safe values
        flowValueAccumulatorWithFractionAsFloat = flowValueAccumulatorAsFloat + flowDecimalFraction

        # For Taosonics, the formula should be:
        # The final positive flow rate = (N+Nf) × 10^(n-3)
        # where n is the value from REG 1439 (totalFlowMultiplier)
        sumFlowValue = flowValueAccumulatorWithFractionAsFloat * (10 ** (totalFlowMultiplier - 3))
        
        # Sanity check on result
        if sumFlowValue < 0:
            print(f"WARNING: Negative flow value {sumFlowValue} calculated, something is wrong. Using absolute value.")
            sumFlowValue = abs(sumFlowValue)

        print(f"DEBUG: Calculated sumFlowValue: {sumFlowValue}")
        return sumFlowValue

    def convertFlowValueFromUnitToM3ForTaosonic(self, flowValueInUnit, unitNumber):
        if (unitNumber == TAOSONICFLOWUNIT_M3):
            return flowValueInUnit
        if (unitNumber == TAOSONICFLOWUNIT_LITER):
            return flowValueInUnit * 0.001
        if (unitNumber == TAOSONICFLOWUNIT_GAL):
            return flowValueInUnit * 0.00378541
        if (unitNumber == TAOSONICFLOWUNIT_FEET3):
            return flowValueInUnit * 0.0283168
        
        # If none of the known units match
        raise Exception(f"invalid total flow unit number for Taosonic Flow Meter (see reg 1438): {unitNumber}")

    def fetchViaDeviceManager(self):

        # Register 361 lesen und Wert (361.00) überprüfen
        try:
            reg361 = self.fetchViaDeviceManager_ForTaoSonicOnly_Helper(361, 2, "<f", "unitNumber")
            print(f"DEBUG: reg361 = {reg361}")
            
            # Validierung der Einheit
            if reg361 < 360.99 or reg361 > 361.01:
                errorText = f"WARNING: TAOSONIC Flow Meter, Register 361 check FAILED. Read {reg361} instead of {361.00}"
                print(errorText)
                raise ValueError(errorText)

            print(f"DEBUG: reg361 SUCCEEDED.")
                
        except Exception as e:
            print(f"EXCEPTION: reg361 test FAILED: {e}")
        
        # Gemäß Taosonics T3-1-2-K-150 Handbuch, exakte Registernummern verwenden
        try:
            # Aktuelle Durchflussrate von Register 1-2, gemäß Handbuch IEEE754 Format
            # Little-Endian war für viele Taosonics-Geräte die richtige Wahl
            currentFlowValue = self.fetchViaDeviceManager_ForTaoSonicOnly_Helper(1, 2, "<f", "currentFlowValue")
            print(f"DEBUG: currentFlowValue = {currentFlowValue} m³/h")
            
        except Exception as e:
            print(f"ERROR bei Lesen der aktuellen Durchflussrate: {e}")
            currentFlowValue = 0.0  # Sicherer Standardwert
            
        print(f"DEBUG: Finale aktuelle Durchflussrate = {currentFlowValue} m³/h")

        # Einheit und Multiplikator aus den korrekten Registern lesen
        try:
            # Register 1438 für Einheit, Register 1439 für Multiplikator
            totalFlowUnitNumber = self.fetchViaDeviceManager_ForTaoSonicOnly_Helper(1438, 1, "<h", "unitNumber")
            print(f"DEBUG: totalFlowUnitNumber = {totalFlowUnitNumber}")
            
            totalFlowMultiplier = self.fetchViaDeviceManager_ForTaoSonicOnly_Helper(1439, 1, "<h", "multiplier")
            print(f"DEBUG: totalFlowMultiplier = {totalFlowMultiplier}")
            
            # Validierung der Einheit
            if totalFlowUnitNumber not in [TAOSONICFLOWUNIT_M3, TAOSONICFLOWUNIT_LITER, TAOSONICFLOWUNIT_GAL, TAOSONICFLOWUNIT_FEET3]:
                print(f"WARNING: Ungültige Einheit {totalFlowUnitNumber}, verwende M3")
                totalFlowUnitNumber = TAOSONICFLOWUNIT_M3
                
            # Validierung des Multiplikators
            if totalFlowMultiplier < -4 or totalFlowMultiplier > 4:
                print(f"WARNING: Ungültiger Multiplikator {totalFlowMultiplier}, verwende 0")
                totalFlowMultiplier = 0
                
        except Exception as e:
            print(f"ERROR beim Lesen der Einheit/Multiplikator: {e}")
            totalFlowUnitNumber = TAOSONICFLOWUNIT_M3  # Standard: Kubikmeter
            totalFlowMultiplier = 0  # Standard-Multiplikator
        
        print(f"DEBUG: Finale Einheit = {totalFlowUnitNumber}, Multiplikator = {totalFlowMultiplier}")

        # Akkumulator-Werte aus den korrekten Registern lesen
        try:
            # Register 9-10 für Ganzzahlwert, LONG-Format
            flowValueAccumulator = self.fetchViaDeviceManager_ForTaoSonicOnly_Helper(9, 2, "<l", "flowAccumulator")
            print(f"DEBUG: flowValueAccumulator = {flowValueAccumulator}")
            
        except Exception as e:
            print(f"ERROR beim Lesen des Akkumulators: {e}")
            flowValueAccumulator = 0  # Sicherer Standardwert
            
        print(f"DEBUG: Finaler Akkumulator = {flowValueAccumulator}")

        # Bruch-Wert des Akkumulators aus den korrekten Registern lesen
        try:
            # Register 11-12 für Dezimalbruchteil, IEEE754 Float-Format
            flowDecimalFraction = self.fetchViaDeviceManager_ForTaoSonicOnly_Helper(11, 2, "<f", "flowDecimalFraction")
            print(f"DEBUG: flowDecimalFraction = {flowDecimalFraction}")
            
            # Wenn der Wert unplausibel erscheint, versuchen wir Big-Endian
            if flowDecimalFraction < 0 or flowDecimalFraction > 1:
                flowDecimalFraction_BE = self.fetchViaDeviceManager_ForTaoSonicOnly_Helper(11, 2, "<f", "flowDecimalFraction (BE)")
                print(f"DEBUG: flowDecimalFraction (Big-Endian) = {flowDecimalFraction_BE}")
                if 0 <= flowDecimalFraction_BE <= 1:
                    flowDecimalFraction = flowDecimalFraction_BE
                    print(f"DEBUG: Using Big-Endian flowDecimalFraction = {flowDecimalFraction}")
                else:
                    print(f"WARNING: Ungültiger Dezimalbruchteil für beide Endian-Formate, verwende 0.0")
                    flowDecimalFraction = 0.0
                
        except Exception as e:
            print(f"ERROR beim Lesen des Dezimalbruchteils: {e}")
            flowDecimalFraction = 0.0  # Sicherer Standardwert

        print(f"DEBUG: Finaler Dezimalbruchteil = {flowDecimalFraction}")

        # Gesamtdurchfluss berechnen
        sumFlowValueInUnit = self.calculateSumFlowValueForTaosonic(totalFlowUnitNumber, totalFlowMultiplier, flowValueAccumulator, flowDecimalFraction)
        print(f"DEBUG: Gesamtdurchfluss in Originaleinheit = {sumFlowValueInUnit}")
        
        sumFlowValueInM3 = self.convertFlowValueFromUnitToM3ForTaosonic(sumFlowValueInUnit, totalFlowUnitNumber)
        print(f"DEBUG: Gesamtdurchfluss in m³ = {sumFlowValueInM3}")

        print(f"DEBUG: Rückgabewerte: aktuelle Rate = {currentFlowValue} m³/h, Gesamtsumme = {sumFlowValueInM3} m³")
        return currentFlowValue, sumFlowValueInM3


def signal_handler(sig, frame):
    print('Shutting down gracefully...')
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
ph_handler.load_calibration()

# Vor der main-Funktion:
DATA_SEND_INTERVAL = 15  # Daten alle 60 Sekunden senden
last_send_time = time.time() - DATA_SEND_INTERVAL  # Stellt sicher, dass beim ersten Durchlauf Daten gesendet werden
        
isVersionSent = False

def main():
    #def Global Variables for Main Funktion
    global isVersionSent, last_send_time, total_flow, ph_low_delay_start_time,ph_high_delay_start_time, runtime_tracker_var, minimumPHValStop, maximumPHVal, minimumPHVal, ph_handler, turbidity_handler, gps_handler, runtime_tracker, client, countdownPHLow, powerButton, tempTruebSens, countdownPHHigh, targetPHtolerrance, targetPHValue, calibratePH, gemessener_low_wert, gemessener_high_wert, autoSwitch, temperaturPHSens_telem, measuredPHValue_telem, measuredTurbidity_telem, gpsTimestamp, gpsLatitude, gpsLongitude, gpsHeight, waterLevelHeight_telem, calculatedFlowRate, messuredRadar_Air_telem, flow_rate_l_min, flow_rate_l_h, flow_rate_m3_min, co2RelaisSwSig, co2HeatingRelaySwSig, pumpRelaySwSig, co2RelaisSw, co2HeatingRelaySw, pumpRelaySw, flow_rate_handler, gpsEnabled, usFlowSensorActive, usFlowRate, usFlowTotal

    # Initialisiere gpsEnabled mit Standardwert
    gpsEnabled = False
    
    saved_state = load_state()
    globals().update(saved_state)
    print(f"DEBUG AFTER LOADING STATE: usFlowSensorActive = {usFlowSensorActive}")

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
    
    print(f"DEBUG AFTER THINGSBOARD INITIALIZATION: usFlowSensorActive = {usFlowSensorActive}")

    total_flow_manager = TotalFlowManager()
    total_flow_manager.start_periodic_save()


    # Initialisierung des GPSHandlers
    gps_handler = GPSHandler(update_interval=60)  # GPS-Daten alle 60 Sekunden aktualisieren
    
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

    # Die folgende Zeile wurde entfernt, um zu verhindern, dass ThingsBoard-Werte überschrieben werden
    # saved_state = load_state()
    # globals().update(saved_state)

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
        print(f"DEBUG MAIN LOOP START: usFlowSensorActive = {usFlowSensorActive}")
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

        if (radarSensorActive):
            flow_rate_handler = FlowRateHandler(Radar_Sensor)
            flow_data = flow_rate_handler.fetch_and_calculate()

            if flow_data:
                # Update the total flow using the calculated flow rate
                total_flow_manager.update_flow_rate(flow_data['flow_rate_l_min'])
                total_flow = total_flow_manager.total_flow
                flow_rate_l_min = flow_data['flow_rate_m3_min']

        # US Flow Sensor Auslesen wenn aktiv
        if (usFlowSensorActive):
            print(f"DEBUG: US Flow Sensor is active. Trying to read data...")
            try:
                print(f"DEBUG: Initializing UsFlowHandler with Sensor ID: {US_Flow_Sensor.device_id}")
                us_flow_handler = UsFlowHandler(US_Flow_Sensor)
                usFlowRate, usFlowTotal = us_flow_handler.fetchViaDeviceManager()
                print(f"US Flow Sensor: Current flow rate = {usFlowRate}, Total flow = {usFlowTotal} m³")
            except Exception as e:
                print(f"Error reading US Flow Sensor: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("DEBUG: US Flow Sensor is disabled (usFlowSensorActive = False)")

        if calibratePH:
            ph_handler.calibrate(high_ph_value=10, low_ph_value=7, measured_high=gemessener_high_wert, measured_low=gemessener_low_wert)
            ph_handler.save_calibration()
            calibratePH = False

        else:
            measuredPHValue_telem, temperaturPHSens_telem = ph_handler.fetch_and_display_data()  
            measuredTurbidity_telem, tempTruebSens = turbidity_handler.fetch_and_display_data(turbiditySensorActive)

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