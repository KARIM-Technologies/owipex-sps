# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: DTI-1 Flow Sensor Debug Script
# Description: Erweitertes Debugging für DTI-1 Flow-Sensor
# -----------------------------------------------------------------------------

import sys
import os

# Dynamisch den Pfad zum Hauptverzeichnis ermitteln
# Der Import funktioniert unabhängig davon, von wo das Skript aufgerufen wird
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../../"))
sys.path.append(project_root)

import time
import struct
import serial
import crcmod.predefined

print(f"Projektpfad: {project_root}")
print(f"Systempfade: {sys.path}")

# Direkte Modbus-RTU Kommunikation für detaillierte Fehleranalyse
class DTI1Debugger:
    def __init__(self, port='/dev/ttyS0', baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=1):
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            parity=serial.PARITY_NONE if parity == 'N' else serial.PARITY_EVEN if parity == 'E' else serial.PARITY_ODD,
            stopbits=serial.STOPBITS_ONE if stopbits == 1 else serial.STOPBITS_TWO,
            bytesize=serial.EIGHTBITS if bytesize == 8 else serial.SEVENBITS,
            timeout=timeout
        )
        self.device_id = 0x28  # DTI-1 Flow-Sensor ID
        print(f"DTI-1 Debugger initialisiert: {port}, {baudrate} Baud")
        
    def print_bytes(self, label, data):
        """Gibt Byte-Daten detailliert aus"""
        print(f"{label} ({len(data)} Bytes):")
        for i, byte in enumerate(data):
            print(f"  Byte {i}: 0x{byte:02X} ({byte})")
        
        # Auch als Hex-String ausgeben
        hex_str = ' '.join([f'{b:02X}' for b in data])
        print(f"  Hex: {hex_str}")
    
    def read_register_raw(self, start_address, register_count):
        """Liest Register und gibt alle Details aus"""
        function_code = 0x03
        
        # Kommando erstellen
        message = struct.pack('>B B H H', self.device_id, function_code, start_address, register_count)
        crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')(message)
        message += struct.pack('<H', crc16)
        
        # Kommando-Details ausgeben
        self.print_bytes("Gesendet", message)
        
        # Kommando senden
        self.ser.write(message)
        
        # Auf Antwort warten
        expected_length = 5 + 2 * register_count  # Slave-ID (1) + Func (1) + Byte count (1) + Data (2*n) + CRC (2)
        time.sleep(0.1)  # Kurz warten
        available = self.ser.in_waiting
        print(f"Verfügbare Bytes: {available} (Erwartet: {expected_length})")
        
        # Antwort lesen
        response = self.ser.read(100)  # Großzügig lesen
        
        if len(response) == 0:
            print("FEHLER: Keine Antwort erhalten")
            return None
            
        self.print_bytes("Empfangen", response)
        
        # CRC prüfen
        if len(response) >= 3:  # Mindestens 3 Bytes für sinnvolle Antwort
            received_crc = struct.unpack('<H', response[-2:])[0]
            calculated_crc = crcmod.predefined.mkPredefinedCrcFun('modbus')(response[:-2])
            print(f"Empfangene CRC: 0x{received_crc:04X}, Berechnete CRC: 0x{calculated_crc:04X}")
            
            if received_crc != calculated_crc:
                print("FEHLER: CRC stimmt nicht überein!")
            else:
                print("CRC OK")
                
            if len(response) >= 3 + 2 * register_count:
                data = response[3:-2]  # Extrahiere Daten
                print(f"Daten: {data.hex()}")
                
                # Bei 4 Bytes (2 Register) Float-Wert interpretieren
                if len(data) == 4:
                    value_le = struct.unpack('<f', data)[0]  # Little Endian
                    value_be = struct.unpack('>f', data)[0]  # Big Endian
                    print(f"Als Float (Little Endian): {value_le}")
                    print(f"Als Float (Big Endian): {value_be}")
                    
                # Bei 2 Bytes (1 Register) Integer-Wert interpretieren
                if len(data) == 2:
                    value_le = struct.unpack('<H', data)[0]  # Little Endian 
                    value_be = struct.unpack('>H', data)[0]  # Big Endian
                    print(f"Als Integer (Little Endian): {value_le}")
                    print(f"Als Integer (Big Endian): {value_be}")
                    
        return response

def debug_flow_rate():
    """Testet Durchflussrate-Register (1-2, Adresse 0-1)"""
    print("\n===== Test: Durchflussrate (Register 1-2, Adresse 0) =====")
    debugger = DTI1Debugger()
    return debugger.read_register_raw(0, 2)  # Adresse 0, 2 Register

def debug_totalizer():
    """Testet Totalizer-Register (Integer-Teil: 9-10, Adresse 8-9)"""
    print("\n===== Test: Totalizer Integer (Register 9-10, Adresse 8) =====")
    debugger = DTI1Debugger()
    return debugger.read_register_raw(8, 2)  # Adresse 8, 2 Register
    
def debug_unit():
    """Testet Einheiten-Register (1438, Adresse 1437)"""
    print("\n===== Test: Totalizer-Einheit (Register 1438, Adresse 1437) =====")
    debugger = DTI1Debugger()
    return debugger.read_register_raw(1437, 1)  # Adresse 1437, 1 Register

def check_device_present():
    """Prüft, ob das Gerät überhaupt antwortet"""
    print("\n===== Test: Geräteerkennung =====")
    # Eine Reihe von Adressen durchprobieren
    for device_id in range(1, 41):  # Von 1 bis 40
        if device_id == 0x28:  # Erwartete DTI-1 ID
            print(f"\nPrüfe Device ID 0x{device_id:02X} (DTI-1 Standard)")
        else:
            print(f"\nPrüfe Device ID 0x{device_id:02X}")
            
        function_code = 0x03
        message = struct.pack('>B B H H', device_id, function_code, 0, 1)
        crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')(message)
        message += struct.pack('<H', crc16)
        
        ser = serial.Serial(
            port='/dev/ttyS0',
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0.5  # Kurzes Timeout für schnelles Scannen
        )
        
        ser.write(message)
        response = ser.read(100)
        ser.close()
        
        if response:
            print(f"✓ Gerät mit ID 0x{device_id:02X} antwortet!")
            print(f"  Antwort: {' '.join([f'{b:02X}' for b in response])}")
        else:
            print(f"✗ Keine Antwort von ID 0x{device_id:02X}")

if __name__ == "__main__":
    print("DTI-1 Flow-Sensor Debug-Tool")
    print("============================")
    
    # Zuerst Geräte-Scan
    check_device_present()
    
    # Dann Werte lesen
    flow_result = debug_flow_rate()
    time.sleep(1)
    totalizer_result = debug_totalizer()
    time.sleep(1)
    unit_result = debug_unit()
    
    print("\nDebug-Tests abgeschlossen.") 