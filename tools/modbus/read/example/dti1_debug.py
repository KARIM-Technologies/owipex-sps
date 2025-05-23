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
import argparse

print(f"Projektpfad: {project_root}")

# Verbesserte Version des DTI1Debuggers
class DTI1Debugger:
    def __init__(self, port='/dev/ttyS0', baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=1, 
                 device_id=0x28, protocol='RTU', verbose=True, retries=3):
        """
        Erweiterte Initialisierung mit mehr Optionen
        
        Args:
            port: Serieller Port
            baudrate: Baudrate (Standard: 9600)
            parity: Parität ('N'=None, 'E'=Even, 'O'=Odd)
            stopbits: Stoppbits (1 oder 2)
            bytesize: Datenbits (7 oder 8)
            timeout: Timeout in Sekunden
            device_id: Modbus-Geräteadresse (Standard: 0x28 = 40 dezimal für DTI-1)
            protocol: 'RTU' oder 'ASCII'
            verbose: Ausführliche Logausgabe
            retries: Anzahl der Wiederholungsversuche bei Fehlern
        """
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            parity=serial.PARITY_NONE if parity == 'N' else serial.PARITY_EVEN if parity == 'E' else serial.PARITY_ODD,
            stopbits=serial.STOPBITS_ONE if stopbits == 1 else serial.STOPBITS_TWO,
            bytesize=serial.EIGHTBITS if bytesize == 8 else serial.SEVENBITS,
            timeout=timeout
        )
        self.device_id = device_id
        self.protocol = protocol
        self.verbose = verbose
        self.retries = retries
        self.log(f"DTI-1 Debugger initialisiert: {port}, {baudrate} Baud, {protocol}-Modus, ID: 0x{device_id:02X}")
        
    def log(self, message):
        """Gibt Nachrichten aus, wenn verbose=True"""
        if self.verbose:
            print(message)
        
    def print_bytes(self, label, data):
        """Gibt Byte-Daten detailliert aus"""
        if not self.verbose:
            return
            
        print(f"{label} ({len(data)} Bytes):")
        for i, byte in enumerate(data):
            print(f"  Byte {i}: 0x{byte:02X} ({byte})")
        
        # Auch als Hex-String ausgeben
        hex_str = ' '.join([f'{b:02X}' for b in data])
        print(f"  Hex: {hex_str}")
    
    def flush_input_buffer(self):
        """Leert den seriellen Eingangspuffer vor der nächsten Anfrage"""
        self.ser.reset_input_buffer()
        time.sleep(0.05)  # Kurze Pause für Stabilität
        
    def read_register_raw(self, start_address, register_count, retry_attempt=0):
        """
        Liest Register und gibt alle Details aus
        
        Args:
            start_address: Startadresse des Registers
            register_count: Anzahl der zu lesenden Register
            retry_attempt: Aktuelle Wiederholungsnummer (intern verwendet)
        """
        # Puffer leeren vor dem Senden
        self.flush_input_buffer()
        
        function_code = 0x03
        
        # Kommando erstellen (unterschiedlich für RTU und ASCII)
        if self.protocol == 'RTU':
            # RTU-Modus
            message = struct.pack('>B B H H', self.device_id, function_code, start_address, register_count)
            crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')(message)
            message += struct.pack('<H', crc16)
        else:
            # ASCII-Modus (konvertiert Hex-Werte in ASCII-Zeichen)
            cmd = f":{self.device_id:02X}{function_code:02X}{start_address:04X}{register_count:04X}"
            lrc = 0
            for i in range(0, len(cmd)-1, 2):
                if i > 0:  # Skip the colon
                    lrc += int(cmd[i:i+2], 16)
            lrc = ((~lrc) + 1) & 0xFF
            message = (cmd + f"{lrc:02X}\r\n").encode('ascii')
        
        # Kommando-Details ausgeben
        self.print_bytes("Gesendet", message if isinstance(message, bytes) else message.encode())
        
        # Kommando senden
        self.ser.write(message)
        
        # Auf Antwort warten
        if self.protocol == 'RTU':
            expected_length = 5 + 2 * register_count  # Slave-ID (1) + Func (1) + Byte count (1) + Data (2*n) + CRC (2)
        else:
            # ASCII hat doppelt so viele Zeichen plus Startzeichen, LRC und CR+LF
            expected_length = (5 + 2 * register_count) * 2 + 1 + 2 + 2
            
        time.sleep(0.2)  # Längere Wartezeit für stabile Ergebnisse
        available = self.ser.in_waiting
        self.log(f"Verfügbare Bytes: {available} (Erwartet: {expected_length})")
        
        # Antwort lesen
        if self.protocol == 'RTU':
            # RTU-Modus: Binäre Bytes
            response = self.ser.read(100)  # Großzügig lesen
        else:
            # ASCII-Modus: ASCII-Zeichen
            response = self.ser.read(100).decode('ascii', errors='ignore')
            
        if not response:
            self.log("FEHLER: Keine Antwort erhalten")
            if retry_attempt < self.retries:
                self.log(f"Wiederholungsversuch {retry_attempt+1} von {self.retries}...")
                time.sleep(0.5)  # Längere Pause vor dem Wiederholungsversuch
                return self.read_register_raw(start_address, register_count, retry_attempt + 1)
            return None
            
        # Antwort verarbeiten
        if self.protocol == 'RTU':
            self.print_bytes("Empfangen", response)
            return self._process_rtu_response(response, register_count)
        else:
            self.log(f"Empfangen: {response}")
            return self._process_ascii_response(response, register_count)
    
    def _process_rtu_response(self, response, register_count):
        """Verarbeitet RTU-Antworten"""
        # CRC prüfen
        if len(response) >= 3:  # Mindestens 3 Bytes für sinnvolle Antwort
            # Zusätzliche Bytes zu Beginn entfernen (bei einigen Implementierungen kann das passieren)
            offset = 0
            while offset < len(response) and response[offset] != self.device_id:
                offset += 1
                
            if offset > 0:
                self.log(f"Warnung: {offset} zusätzliche Bytes am Anfang der Antwort, werden ignoriert")
                response = response[offset:]
                
            if len(response) < 3:
                self.log("Antwort zu kurz nach Korrektur des Offsets")
                return None
                
            received_crc = struct.unpack('<H', response[-2:])[0]
            calculated_crc = crcmod.predefined.mkPredefinedCrcFun('modbus')(response[:-2])
            self.log(f"Empfangene CRC: 0x{received_crc:04X}, Berechnete CRC: 0x{calculated_crc:04X}")
            
            if received_crc != calculated_crc:
                self.log("FEHLER: CRC stimmt nicht überein!")
                return None
            else:
                self.log("CRC OK")
                
            if len(response) >= 3 + 2 * register_count:
                data = response[3:-2]  # Extrahiere Daten
                self.log(f"Daten: {data.hex()}")
                return data
        return None
    
    def _process_ascii_response(self, response, register_count):
        """Verarbeitet ASCII-Antworten"""
        # Response-Format: :[SlaveID][FunctionCode][ByteCount][Data][LRC][CR][LF]
        if response.startswith(':') and response.endswith('\r\n'):
            # LRC prüfen
            data_part = response[1:-3]  # Ohne ':', LRC, CR, LF
            calculated_lrc = 0
            for i in range(0, len(data_part), 2):
                calculated_lrc += int(data_part[i:i+2], 16)
            calculated_lrc = ((~calculated_lrc) + 1) & 0xFF
            
            received_lrc = int(response[-4:-2], 16)
            self.log(f"Empfangene LRC: 0x{received_lrc:02X}, Berechnete LRC: 0x{calculated_lrc:02X}")
            
            if received_lrc != calculated_lrc:
                self.log("FEHLER: LRC stimmt nicht überein!")
                return None
            else:
                self.log("LRC OK")
            
            # Daten extrahieren
            data_start = 5  # :[ID][Func][ByteCount]
            data_length = register_count * 4  # 2 Bytes pro Register, 2 Hex-Zeichen pro Byte
            data_hex = data_part[data_start:data_start + data_length]
            
            # Hex-String in Bytes konvertieren
            data = bytes.fromhex(data_hex)
            self.log(f"Daten: {data.hex()}")
            return data
        return None

    def read_float(self, start_address):
        """Liest einen Float-Wert (REAL4) ab der Startadresse"""
        data = self.read_register_raw(start_address, 2)
        if data and len(data) == 4:
            try:
                value_le = struct.unpack('<f', data)[0]  # Little Endian
                value_be = struct.unpack('>f', data)[0]  # Big Endian
                self.log(f"Als Float (Little Endian): {value_le}")
                self.log(f"Als Float (Big Endian): {value_be}")
                return value_le  # DTI-1 verwendet Little Endian
            except Exception as e:
                self.log(f"Fehler bei Float-Konvertierung: {e}")
        return None
    
    def read_long(self, start_address):
        """Liest einen Long Integer-Wert (LONG) ab der Startadresse"""
        data = self.read_register_raw(start_address, 2)
        if data and len(data) == 4:
            try:
                value_le = struct.unpack('<l', data)[0]  # Little Endian
                value_be = struct.unpack('>l', data)[0]  # Big Endian
                self.log(f"Als Long (Little Endian): {value_le}")
                self.log(f"Als Long (Big Endian): {value_be}")
                return value_le  # DTI-1 verwendet Little Endian
            except Exception as e:
                self.log(f"Fehler bei Long-Konvertierung: {e}")
        return None
    
    def read_short(self, start_address):
        """Liest einen Short Integer-Wert (INTEGER) ab der Startadresse"""
        data = self.read_register_raw(start_address, 1)
        if data and len(data) == 2:
            try:
                value_le = struct.unpack('<h', data)[0]  # Little Endian
                value_be = struct.unpack('>h', data)[0]  # Big Endian
                self.log(f"Als Short (Little Endian): {value_le}")
                self.log(f"Als Short (Big Endian): {value_be}")
                return value_be  # DTI-1 verwendet Big Endian für Konfigurationswerte
            except Exception as e:
                self.log(f"Fehler bei Short-Konvertierung: {e}")
        return None
    
    def read_totalizer_full(self):
        """
        Liest den vollständigen Totalizer-Wert inklusive Dezimalteil und Multiplikator
        
        Formula aus Dokumentation: Totalizer = (N + Nf) × 10^(n-3)
        N: Integer-Teil (Register 0009-0010)
        Nf: Dezimal-Teil (Register 0011-0012)
        n: Multiplikator (Register 1439)
        """
        # 1. Integer-Teil lesen
        integer_part = self.read_long(8)  # Register 9-10 (Adresse 8)
        if integer_part is None:
            self.log("FEHLER: Konnte Integer-Teil des Totalizers nicht lesen")
            return None, None
            
        # 2. Dezimal-Teil lesen
        decimal_part = self.read_float(10)  # Register 11-12 (Adresse 10)
        if decimal_part is None:
            self.log("WARNUNG: Konnte Dezimal-Teil des Totalizers nicht lesen, verwende 0.0")
            decimal_part = 0.0
        
        # 3. Multiplikator lesen
        multiplier = self.read_short(1438)  # Register 1439 (Adresse 1438)
        if multiplier is None:
            self.log("WARNUNG: Konnte Multiplikator nicht lesen, verwende 0")
            multiplier = 0
            
        # 4. Einheit lesen
        unit_code = self.read_short(1437)  # Register 1438 (Adresse 1437)
        if unit_code is None:
            self.log("WARNUNG: Konnte Einheit nicht lesen, verwende Code 0 (m³)")
            unit_code = 0
            
        # Einheit als Text
        units = {
            0: "m³",
            1: "Liter",
            2: "US-Gallone",
            3: "UK-Gallone",
            4: "Million US-Gallonen",
            5: "Cubic Feet",
            6: "Oil Barrel US",
            7: "Oil Barrel UK"
        }
        unit_text = units.get(unit_code, f"Unbekannt ({unit_code})")
            
        # 5. Gesamtwert berechnen
        total_value = (integer_part + decimal_part) * (10 ** (multiplier - 3))
        
        self.log(f"Totalizer-Berechnung:")
        self.log(f"  Integer-Teil (N): {integer_part}")
        self.log(f"  Dezimal-Teil (Nf): {decimal_part}")
        self.log(f"  Multiplikator (n): {multiplier}")
        self.log(f"  Einheit: {unit_text} (Code: {unit_code})")
        self.log(f"  Formel: ({integer_part} + {decimal_part}) × 10^({multiplier}-3)")
        self.log(f"  Totalizer: {total_value} {unit_text}")
        
        return total_value, unit_text


def debug_device_detection(protocols=None, baudrates=None):
    """
    Verbesserte Geräterkennung mit mehreren Protokollen und Baudraten
    
    Args:
        protocols: Liste der zu testenden Protokolle (Standard: ['RTU', 'ASCII'])
        baudrates: Liste der zu testenden Baudraten (Standard: [9600, 19200])
    """
    protocols = protocols or ['RTU', 'ASCII']
    baudrates = baudrates or [9600, 19200]
    
    print("\n===== Test: Erweiterte Geräteerkennung =====")
    
    results = {}
    best_combination = None
    max_responses = 0
    
    for protocol in protocols:
        for baudrate in baudrates:
            print(f"\n----- Test mit {protocol}, {baudrate} Baud -----")
            
            # Eine Reihe von Adressen durchprobieren
            found_devices = []
            
            for device_id in range(1, 41):  # Von 1 bis 40
                if device_id == 0x28:  # Erwartete DTI-1 ID
                    print(f"\nPrüfe Device ID 0x{device_id:02X} (DTI-1 Standard)")
                else:
                    print(f"Prüfe Device ID 0x{device_id:02X}", end="\r")
                    
                function_code = 0x03
                
                if protocol == 'RTU':
                    message = struct.pack('>B B H H', device_id, function_code, 0, 1)
                    crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')(message)
                    message += struct.pack('<H', crc16)
                else:
                    cmd = f":{device_id:02X}{function_code:02X}00000001"
                    lrc = 0
                    for i in range(0, len(cmd)-1, 2):
                        if i > 0:  # Skip the colon
                            lrc += int(cmd[i:i+2], 16)
                    lrc = ((~lrc) + 1) & 0xFF
                    message = (cmd + f"{lrc:02X}\r\n").encode('ascii')
                
                ser = serial.Serial(
                    port='/dev/ttyS0',
                    baudrate=baudrate,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=0.5  # Kurzes Timeout für schnelles Scannen
                )
                
                # Puffer leeren
                ser.reset_input_buffer()
                time.sleep(0.05)
                
                ser.write(message)
                response = ser.read(100)
                ser.close()
                
                if response:
                    if device_id == 0x28:  # DTI-1
                        print(f"✓ DTI-1 antwortet mit {protocol}/{baudrate}!")
                    else:
                        print(f"✓ Gerät mit ID 0x{device_id:02X} antwortet!")
                    print(f"  Antwort: {' '.join([f'{b:02X}' for b in response])}")
                    found_devices.append(device_id)
                elif device_id == 0x28:  # Nur für DTI-1 die Fehler anzeigen
                    print(f"✗ DTI-1 antwortet nicht mit {protocol}/{baudrate}")
            
            num_found = len(found_devices)
            results[f"{protocol}_{baudrate}"] = found_devices
            print(f"\nMit {protocol}/{baudrate} wurden {num_found} Geräte gefunden: {found_devices}")
            
            if num_found > max_responses:
                max_responses = num_found
                best_combination = (protocol, baudrate)
    
    if best_combination:
        protocol, baudrate = best_combination
        print(f"\n=== Beste Kommunikationseinstellung: {protocol}, {baudrate} Baud ===")
        print(f"Gefundene Geräte: {results[f'{protocol}_{baudrate}']}")
        return protocol, baudrate
    else:
        print("\n=== Keine Geräte gefunden ===")
        return 'RTU', 9600  # Standardwerte


def test_flow_rate(debugger):
    """Testet Durchflussrate-Register (1-2, Adresse 0)"""
    print("\n===== Test: Durchflussrate (Register 1-2, Adresse 0) =====")
    flow_rate = debugger.read_float(0)  # Adresse 0, 2 Register
    if flow_rate is not None:
        print(f">>> Durchflussrate: {flow_rate:.3f} m³/h")
    return flow_rate


def test_totalizer(debugger):
    """Testet Totalizer-Register mit vollständiger Berechnung"""
    print("\n===== Test: Totalizer (vollständige Berechnung) =====")
    total_value, unit = debugger.read_totalizer_full()
    if total_value is not None:
        print(f">>> Gesamtmenge: {total_value:.3f} {unit}")
    return total_value, unit


def test_temperatures(debugger):
    """Testet Temperatur-Register (33-34, 35-36)"""
    print("\n===== Test: Temperaturen =====")
    
    # Inlet Temperature
    print("--- Eingangstemperatur (Register 33-34, Adresse 32) ---")
    temp_in = debugger.read_float(32)
    if temp_in is not None:
        print(f">>> Eingangstemperatur: {temp_in:.2f} °C")
        
    # Outlet Temperature
    print("\n--- Ausgangstemperatur (Register 35-36, Adresse 34) ---")
    temp_out = debugger.read_float(34)
    if temp_out is not None:
        print(f">>> Ausgangstemperatur: {temp_out:.2f} °C")
        
    return temp_in, temp_out


def run_continuous_test(debugger, duration=30, interval=2):
    """Führt einen kontinuierlichen Test über die angegebene Dauer durch"""
    print(f"\n===== Kontinuierlicher Test für {duration} Sekunden =====")
    end_time = time.time() + duration
    
    try:
        i = 1
        while time.time() < end_time:
            print(f"\n--- Messung {i} ---")
            flow_rate = debugger.read_float(0)
            total_value, unit = debugger.read_totalizer_full()
            
            print(f"Durchfluss: {flow_rate:.3f} m³/h | Gesamt: {total_value:.3f} {unit}")
            i += 1
            
            remaining = end_time - time.time()
            if remaining > interval:
                time.sleep(interval)
            else:
                break
                
    except KeyboardInterrupt:
        print("\nTest durch Benutzer unterbrochen")
    
    print("\nKontinuierlicher Test beendet")


def main():
    parser = argparse.ArgumentParser(description='DTI-1 Flow-Sensor Debug-Tool mit erweiterten Optionen')
    parser.add_argument('--port', default='/dev/ttyS0', help='Serieller Port (Standard: /dev/ttyS0)')
    parser.add_argument('--baudrate', type=int, default=9600, help='Baudrate (Standard: 9600)')
    parser.add_argument('--protocol', choices=['RTU', 'ASCII'], default='RTU', help='Protokoll (Standard: RTU)')
    parser.add_argument('--device-id', type=int, default=40, help='Geräte-ID (Standard: 40)')
    parser.add_argument('--detect', action='store_true', help='Automatische Geräteerkennung durchführen')
    parser.add_argument('--continuous', type=int, default=0, help='Kontinuierlichen Test für X Sekunden durchführen')
    parser.add_argument('--timeout', type=float, default=1.0, help='Timeout in Sekunden')
    parser.add_argument('--retries', type=int, default=3, help='Anzahl der Wiederholungsversuche')
    parser.add_argument('--no-verbose', action='store_true', help='Ausführliche Ausgabe deaktivieren')
    args = parser.parse_args()
    
    print("DTI-1 Flow-Sensor erweitertes Debug-Tool")
    print("=======================================")
    
    protocol = args.protocol
    baudrate = args.baudrate
    
    # Automatische Geräteerkennung, wenn angefordert
    if args.detect:
        protocol, baudrate = debug_device_detection()
    
    # Debugger initialisieren
    debugger = DTI1Debugger(
        port=args.port,
        baudrate=baudrate,
        protocol=protocol,
        device_id=args.device_id,
        timeout=args.timeout,
        retries=args.retries,
        verbose=not args.no_verbose
    )
    
    # Kontinuierlichen Test durchführen, wenn angefordert
    if args.continuous > 0:
        run_continuous_test(debugger, args.continuous)
    else:
        # Standardtests durchführen
        flow_rate = test_flow_rate(debugger)
        time.sleep(0.5)
        total_value, unit = test_totalizer(debugger)
        time.sleep(0.5)
        temp_in, temp_out = test_temperatures(debugger)
    
    print("\nDebug-Tests abgeschlossen.")
    

if __name__ == "__main__":
    main() 