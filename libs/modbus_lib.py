# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: Modbus Lib V1.0
# Description: Erweiterte Modbus-Kommunikation für alle Sensoren (Radar, PH, Trübe, DTI-1 Flow)
# -----------------------------------------------------------------------------

import struct
import serial
import crcmod.predefined
from threading import Thread
from time import sleep
import time
import sys
import os
sys.path.append('/home/owipex_adm/owipex-sps')

def get_timestamp():
    """Generate timestamp string in format [HH:MM:SS.mmm]"""
    return time.strftime("%H:%M:%S", time.localtime()) + f".{int(time.time() * 1000) % 1000:03d}"

def printTs(message):
    """Prints a message with a timestamp."""
    print(f"[{get_timestamp()}] {message}")

class ModbusClient:
    def __init__(self, device_manager, device_id, device_name):
        self.device_manager = device_manager
        self.device_id = device_id
        self.device_name = device_name
        self.auto_read_enabled = False

    def getDeviceInfo(self) -> str:
        return f"{self.device_name}({self.device_id})";

    def read_register(self, start_address, register_count, data_format='>f'):
        return self.device_manager.read_register(self.device_id, start_address, register_count, data_format)
    
    def read_radar_sensor(self, register_address):
        return self.device_manager.read_radar_sensor(self.device_id, register_address)

    def auto_read_registers(self, start_address, register_count, data_format='>f', interval=1):
        self.auto_read_enabled = True
        def read_loop():
            while self.auto_read_enabled:
                value = self.read_register(start_address, register_count, data_format)
                printTs(f'Auto Read: {value}')
                sleep(interval)

        Thread(target=read_loop).start()

    def stop_auto_read(self):
        self.auto_read_enabled = False

    # DTI-1 spezifische Methoden
    def read_flow_rate_m3ph(self):
        return self.device_manager.read_flow_rate_m3ph(self.device_id)

    def read_totalizer_m3(self):
        return self.device_manager.read_totalizer_m3(self.device_id)

    def read_pipediameter_mm(self):
        return self.device_manager.read_pipediameter_mm(self.device_id)

    def read_deviceid(self):
        return self.device_manager.read_deviceid(self.device_id)
    
    def write_VincerValve(self, start_address, register_count, value):
        """Write to VincerValve register - forwards to DeviceManager"""
        return self.device_manager.write_VincerValve(self.device_id, start_address, register_count, value)

class DeviceManager:
    def __init__(self, port, baudrate, parity, stopbits, bytesize, timeout):
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            parity=serial.PARITY_NONE if parity == 'N' else serial.PARITY_EVEN if parity == 'E' else serial.PARITY_ODD,
            stopbits=serial.STOPBITS_ONE if stopbits == 1 else serial.STOPBITS_TWO,
            bytesize=serial.EIGHTBITS if bytesize == 8 else serial.SEVENBITS,
            timeout=timeout
        )
        self.devices = {}
        self.last_read_values = {}  # Dictionary to store last read values for each device and register

    def getDevicesInfo(self) -> str:
        
        device_info_lines = []
        device_info_lines.append("")
        device_info_lines.append("Known devices")
        device_info_lines.append("-------------")

        if self.devices:
            for device_id, device in self.devices.items():
                device_info_lines.append(device.getDeviceInfo())
        else:
            device_info_lines.append("(no devices registered)")
        
        return "\n".join(device_info_lines)
    
    def printDevicesInfo(self):
        """Print information about all registered devices"""
        print(self.getDevicesInfo())

    def add_device(self, device_id, device_name) -> ModbusClient:
        self.devices[device_id] = ModbusClient(self, device_id, device_name)
        return self.devices.get(device_id)

    def get_device(self, device_id) -> ModbusClient:
        return self.devices.get(device_id)

    def read_register(self, device_id, start_address, register_count, data_format):
        function_code = 0x03

        message = struct.pack('>B B H H', device_id, function_code, start_address, register_count)

        crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')(message)
        message += struct.pack('<H', crc16)

        self.ser.write(message)

        response = self.ser.read(100)
        
        # Check if the response is at least 2 bytes long
        if len(response) < 2:
            printTs(f'⚠️  Device {device_id}: Received response is shorter than expected ({len(response)} bytes)')
            return self.last_read_values.get((device_id, start_address), None)

        received_crc = struct.unpack('<H', response[-2:])[0]
        calculated_crc = crcmod.predefined.mkPredefinedCrcFun('modbus')(response[:-2])
        if received_crc != calculated_crc:
            printTs(f'⚠️  Device {device_id}: CRC error in response')
            return self.last_read_values.get((device_id, start_address), None)

        data = response[3:-2]
        swapped_data = data[2:4] + data[0:2]
        try:
            floating_point = struct.unpack(data_format, swapped_data)[0]
        except struct.error:
            printTs(f'⚠️  Device {device_id}: Error decoding data')
            return self.last_read_values.get((device_id, start_address), None)

        if floating_point is None:
            printTs(f'⚠️  Device {device_id}: Error reading register')
            return self.last_read_values.get((device_id, start_address), None)

        # Store the read value in the last_read_values dictionary
        self.last_read_values[(device_id, start_address)] = floating_point

        return floating_point

    def print_bytes_info(self, info, b):
        print(f"print_bytes_info: {info}")
        for byte in b:
            print(f"Hex: {byte:02x}, Dec: {byte}")
        print(f"================")
        pass
    
    # Wandelt eine Ganzzahl (0-99) in ein BCD-codiertes Byte um.
    def int_to_bcd(self, n: int) -> int:
        if not (0 <= n <= 99):
            raise ValueError("Zahl muss zwischen 0 und 99 liegen")
        
        zehner = (n // 10) << 4
        einer = n % 10
        return zehner | einer

    def read_radar_sensor(self, device_id, register_address):
        return self.read_register(device_id, register_address, 1, data_format='>H')

    # DTI-1 Spezifische Methoden
    def read_UsFlowSensor_holding_raw(self, device_id, start_address, register_count):
        """
        Liest Rohwerte aus Modbus-Holdings-Registern ohne Interpretation/Konvertierung.
        Gibt die Rohdaten zurück.
        """
        # Puffer leeren vor der Anfrage
        self.ser.reset_input_buffer()
        time.sleep(0.05)  # Kurze Pause für Stabilität
        
        function_code = 0x03
        message = struct.pack('>B B H H', device_id, function_code, start_address, register_count)
        crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')(message)
        message += struct.pack('<H', crc16)
        
        self.ser.write(message)
        time.sleep(0.1)  # Warten auf vollständige Antwort
        
        # Mehr Bytes lesen als minimal notwendig, falls zusätzliche Bytes kommen
        response = self.ser.read(100)
        
        # Prüfen, ob die Antwort minimal sinnvoll ist
        if len(response) < 5:
            raise Exception("Antwort zu kurz")
            
        # Korrektur für zusätzliche Bytes am Anfang der Antwort
        offset = 0
        while offset < len(response) and response[offset] != device_id:
            offset += 1
            
        if offset > 0:
            printTs(f"⚠️  Device {device_id}: {offset} zusätzliche Bytes am Anfang der Antwort, werden ignoriert")
            response = response[offset:]
            
        if len(response) < 5:
            raise Exception("Antwort nach Offset-Korrektur zu kurz")
        
        # CRC prüfen
        received_crc = struct.unpack('<H', response[-2:])[0]
        calculated_crc = crcmod.predefined.mkPredefinedCrcFun('modbus')(response[:-2])
        
        if received_crc != calculated_crc:
            raise Exception("CRC-Fehler!")
            
        data = response[3:-2]  # Slave-ID (1) + Func (1) + Byte count (1) + ... + CRC (2)
        return data

    def read_flow_rate_m3ph(self, device_id, isDebugMode):
        """
        Liest den aktuellen Durchflusswert (m³/h, REAL4/Float) aus Register 1+2 (Adresse 0, 2 Register)
        """
        # Bis zu 3 Versuche bei Fehlern
        for attempt in range(3):
            try:
                data = self.read_UsFlowSensor_holding_raw(device_id, 1, 2)
                value = struct.unpack('>f', data)[0]
                if isDebugMode:
                    printTs(f"DTI-1 Device {device_id}: Durchflusswert (aus Register 1+2): {value}")

                # Nicht-plausible Werte abfangen (extreme Ausreißer)
                if value > 1000000:  # Unrealistisch hoher Durchfluss
                    printTs(f"⚠️  Device {device_id}: Unplausibel hoher Durchflusswert: {value}, setze auf 0")
                    return 0.0

                return value  # m³/h
            except Exception as e:
                printTs(f"❌ DTI-1 Device {device_id}: Fehler beim Lesen des Durchflusswerts (Versuch {attempt+1}/3): {e}")
                time.sleep(0.2 * (attempt + 1))  # Längere Pause bei jedem Versuch
                
        return None  # Nach allen Versuchen gescheitert

    def gallonsToCubicMeters(self, gallons):
        # 1 US gallon = 0.003785411784 m³
        return gallons * 0.003785411784

    def read_totalizer_m3(self, device_id, isDebugMode):
        """
        Liest die gesamterfasste Menge in m³ aus dem Register 113
        """
        # Bis zu 3 Versuche bei Fehlern
        for attempt in range(3):
            try:
                data = self.read_UsFlowSensor_holding_raw(device_id, 113, 2)
                value = struct.unpack('>f', data)[0]
                if isDebugMode:
                    printTs(f"DTI-1 Device {device_id}: NetAccumulator im m3 (aus Register 113): {value}")
                return value

            except Exception as e:
                printTs(f"❌ DTI-1 Device {device_id}: Fehler beim Lesen des Totalizers (Versuch {attempt+1}/3): {e}")
                time.sleep(0.2 * (attempt + 1))  # Längere Pause bei jedem Versuch
                
        return None  # Nach allen Versuchen gescheitert

    def read_pipediameter_mm(self, device_id):
        """
        Liest den Pipe Durchmesser (mm, REAL4/Float) aus Register 221 (Address 221, 2 Register)
        """
        # Bis zu 3 Versuche bei Fehlern
        for attempt in range(3):
            try:
                data = self.read_UsFlowSensor_holding_raw(device_id, 221, 2)
                value = struct.unpack('>f', data)[0]
                # Nicht-plausible Werte abfangen (extreme Ausreißer)
                if value < 0 or value > 1000000:  # Unrealistisch
                    printTs(f"⚠️  Device {device_id}: Unplausibler Pipe Diameter: {value}, setze auf 0")
                    return 0.0
                return value  # mm
            except Exception as e:
                printTs(f"❌ DTI-1 Device {device_id}: Fehler beim Lesen des Pipe Diameter (Versuch {attempt+1}/3): {e}")
                time.sleep(0.2 * (attempt + 1))  # Längere Pause bei jedem Versuch
                
        return None  # Nach allen Versuchen gescheitert

    def read_deviceid(self, device_id):
        """
        Liest die DeviceId (INTEGER) aus Register 1442 (Address 1442, 1 Register)
        """
        # Bis zu 3 Versuche bei Fehlern
        for attempt in range(3):
            try:
                data = self.read_UsFlowSensor_holding_raw(device_id, 1442, 1)
                value = struct.unpack(">h", data)[0]
                # Nicht-plausible Werte abfangen (extreme Ausreißer)
                if value < 0 or value > 1000000:  # Unrealistisch
                    printTs(f"⚠️  Device {device_id}: Unplausibler DeviceId: {value}, setze auf 0")
                    return 0
                return value  # ID
            except Exception as e:
                printTs(f"❌ DTI-1 Device {device_id}: Fehler beim Lesen des DeviceId (Versuch {attempt+1}/3): {e}")
                time.sleep(0.2 * (attempt + 1))  # Längere Pause bei jedem Versuch

        return None  # Nach allen Versuchen gescheitert

    def write_VincerValve(self, device_id, start_address, register_count, value):
        """
        Write to VincerValve register using Modbus Function Code 0x06 (Write Single Register)
        """
        try:
            # Für einzelne Register verwenden wir Function Code 0x06
            if register_count == 1:
                function_code = 0x06
                # Nachricht: Device ID, Function Code, Register Address, Value
                message = struct.pack('>B B H H', device_id, function_code, start_address, value)
                
                # CRC berechnen und anhängen
                crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')(message)
                message += struct.pack('<H', crc16)
                
                # Puffer leeren vor dem Senden
                self.ser.reset_input_buffer()
                
                # Nachricht senden
                self.ser.write(message)
                time.sleep(0.1)  # Warten auf Antwort
                
                # Antwort lesen
                response = self.ser.read(100)
                
                # Minimale Antwortlänge prüfen
                if len(response) < 8:
                    printTs(f'⚠️  Device {device_id} VincerValve Write: Antwort zu kurz ({len(response)} Bytes)')
                    return False
                
                # CRC der Antwort prüfen
                received_crc = struct.unpack('<H', response[-2:])[0]
                calculated_crc = crcmod.predefined.mkPredefinedCrcFun('modbus')(response[:-2])
                
                if received_crc != calculated_crc:
                    printTs(f'⚠️  Device {device_id} VincerValve Write: CRC-Fehler in Antwort')
                    return False
                
                # Bei erfolgreicher Antwort sollte die Antwort die geschriebenen Werte zurückgeben
                printTs(f'✅ VincerValve Write erfolgreich: Device {device_id}, Adresse {start_address}, Wert {value}')
                return True
                
            else:
                printTs(f'⚠️  Device {device_id} VincerValve Write: Mehrere Register ({register_count}) noch nicht implementiert')
                return False
                
        except Exception as e:
            printTs(f'⚠️  Device {device_id} VincerValve Write Fehler: {e}')
            return False

# # Beispiel-Nutzung:
# if __name__ == "__main__":
#     # Passe ggf. Port und Device-ID an!
#     dev = DeviceManager(port="/dev/ttyS0", baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=1)
#     device_id = 0x28  # Beispiel

#     sensor = dev.get_device(device_id)
#     flow = sensor.read_flow_rate_m3ph()
#     print(f"Aktueller Durchfluss: {flow:.3f} m³/h")

#     total, einheit = sensor.read_totalizer_m3()
#     print(f"Gesamterfasste Menge: {total:.3f} {einheit}")
