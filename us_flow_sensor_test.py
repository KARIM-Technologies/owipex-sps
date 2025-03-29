#!/usr/bin/env python3
# Testdatei für den US Flow Sensor

import sys
import time
import os

# Füge den Pfad zu den Bibliotheken hinzu
sys.path.append('/home/owipex_adm/owipex-sps/libs')

from libs.modbus_lib import DeviceManager

# TAOSONICFLOWUNIT Konstanten
TAOSONICFLOWUNIT_M3 = 0       # Kubikmeter (m3)
TAOSONICFLOWUNIT_LITER = 1    # Liter (L)
TAOSONICFLOWUNIT_GAL = 2      # Amerikanische Gallone (GAL)
TAOSONICFLOWUNIT_FEET3 = 3    # Kubikfuß (CF)

class UsFlowHandler:
    def __init__(self, sensor):
        self.sensor = sensor

    def fetchViaDeviceManager_Helper(self, address, registerCount, dataformat, infoText):
        print(f"DEBUG: Lese Register: Adresse={address}, Anzahl={registerCount}, Format={dataformat}, Info={infoText}")
        try:
            value = self.sensor.read_register(address, registerCount, dataformat)
            print(f"DEBUG: Gelesener Wert: {value}")
            if value is None:
                print(f"DEBUG: Wert ist None!")
                raise ValueError(f"Us-Flow Sensorlesung {infoText} fehlgeschlagen. Überprüfen Sie die Verbindung.")
            return value
        except Exception as e:
            print(f"DEBUG: Fehler beim Lesen des Registers: {e}")
            raise

    def test_endian_format(self):
        print("\n=== ENDIAN FORMAT TEST USING REGISTER 361 ===")
        try:
            # Laut Handbuch sollte Register 361 immer 361.00 zurückgeben, wenn das Format richtig ist
            reg361_LE = self.fetchViaDeviceManager_Helper(361, 2, "<f", "REG361 (LE)")
            print(f"REG361 (Little-Endian): {reg361_LE}")
            
            reg361_BE = self.fetchViaDeviceManager_Helper(361, 2, ">f", "REG361 (BE)")
            print(f"REG361 (Big-Endian): {reg361_BE}")
            
            # Prüfe, welches Format korrekt ist
            if abs(reg361_LE - 361.0) < 0.1:
                print("✓ Little-Endian Format erkannt (REG361 = 361.00)")
                self.preferred_endian = "<"
            elif abs(reg361_BE - 361.0) < 0.1:
                print("✓ Big-Endian Format erkannt (REG361 = 361.00)")
                self.preferred_endian = ">"
            else:
                print("⚠ Kein passendes Endian-Format erkannt! Verwende Little-Endian als Standard.")
                self.preferred_endian = "<"
                
            # Zusätzlich den Test von REG363 (soll 363348858 sein laut Handbuch)
            reg363_LE = self.fetchViaDeviceManager_Helper(363, 2, "<l", "REG363 (LE)")
            print(f"REG363 (Little-Endian): {reg363_LE}")
            
            reg363_BE = self.fetchViaDeviceManager_Helper(363, 2, ">l", "REG363 (BE)")
            print(f"REG363 (Big-Endian): {reg363_BE}")
            
            # Prüfe, welches Format korrekt ist
            if reg363_LE == 363348858:
                print("✓ Little-Endian Format bestätigt (REG363 = 363348858)")
            elif reg363_BE == 363348858:
                print("✓ Big-Endian Format bestätigt (REG363 = 363348858)")
            else:
                print("⚠ Kein passendes Endian-Format für REG363 erkannt!")
                
            print("=== ENDIAN FORMAT TEST ABGESCHLOSSEN ===\n")
        except Exception as e:
            print(f"Fehler beim Testen des Endian-Formats: {e}")
            self.preferred_endian = "<"  # Default zu Little-Endian

    def calculateSumFlowValueForTaosonic(self, totalFlowUnitNumber, totalFlowMultiplier, flowValueAccumulator, flowDecimalFraction):
        # The final positive flow rate=(N+Nf) ×10^(n-3) (in unit decided by REG 1439)
        # where N is the integer part, Nf is the decimal fraction and n is the multiplier
        
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
        # Gemäß Taosonics T3-1-2-K-150 Handbuch, exakte Registernummern verwenden
        try:
            # Aktuelle Durchflussrate von Register 1-2, gemäß Handbuch IEEE754 Format
            # Little-Endian war für viele Taosonics-Geräte die richtige Wahl
            currentFlowValue = self.fetchViaDeviceManager_Helper(1, 2, "<f", "currentFlowValue")
            print(f"DEBUG: currentFlowValue (Little-Endian) = {currentFlowValue} m³/h")
            
            # Zeige auch die Big-Endian-Version an
            currentFlowValue_BE = self.fetchViaDeviceManager_Helper(1, 2, ">f", "currentFlowValue (BE)")
            print(f"DEBUG: currentFlowValue (Big-Endian) = {currentFlowValue_BE} m³/h")
            
            # Wenn der Wert unplausibel erscheint, versuchen wir Big-Endian
            if currentFlowValue < 0 or currentFlowValue > 1000:
                if 0 <= currentFlowValue_BE <= 1000:
                    currentFlowValue = currentFlowValue_BE
                    print(f"DEBUG: Using Big-Endian currentFlowValue = {currentFlowValue}")
                
        except Exception as e:
            print(f"ERROR bei Lesen der aktuellen Durchflussrate: {e}")
            currentFlowValue = 0.0  # Sicherer Standardwert
            
        print(f"DEBUG: Finale aktuelle Durchflussrate = {currentFlowValue} m³/h")

        # Einheit und Multiplikator aus den korrekten Registern lesen
        try:
            # Register 1438 für Einheit, Register 1439 für Multiplikator
            totalFlowUnitNumber = self.fetchViaDeviceManager_Helper(1438, 1, ">h", "unitNumber")
            print(f"DEBUG: totalFlowUnitNumber = {totalFlowUnitNumber}")
            
            totalFlowMultiplier = self.fetchViaDeviceManager_Helper(1439, 1, ">h", "multiplier")
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
            # Zeige explizit beide Endian-Formate für Register 9-10 an
            flowValueAccumulator_LE = self.fetchViaDeviceManager_Helper(9, 2, "<l", "flowAccumulator (LE)")
            print(f"DEBUG: flowValueAccumulator (Little-Endian) = {flowValueAccumulator_LE}")
            
            flowValueAccumulator_BE = self.fetchViaDeviceManager_Helper(9, 2, ">l", "flowAccumulator (BE)")
            print(f"DEBUG: flowValueAccumulator (Big-Endian) = {flowValueAccumulator_BE}")
            
            # Verwende Little-Endian als Ausgangswert
            flowValueAccumulator = flowValueAccumulator_LE
            
            # Wenn der Wert unplausibel erscheint, versuchen wir Big-Endian
            if flowValueAccumulator < 0:
                if flowValueAccumulator_BE >= 0:
                    flowValueAccumulator = flowValueAccumulator_BE
                    print(f"DEBUG: Using Big-Endian flowValueAccumulator = {flowValueAccumulator}")
                else:
                    print(f"WARNING: Negative Werte für beide Endian-Formate, verwende 0")
                    flowValueAccumulator = 0
            
        except Exception as e:
            print(f"ERROR beim Lesen des Akkumulators: {e}")
            flowValueAccumulator = 0  # Sicherer Standardwert
            
        print(f"DEBUG: Finaler Akkumulator = {flowValueAccumulator}")

        # Bruch-Wert des Akkumulators aus den korrekten Registern lesen
        try:
            # Register 11-12 für Dezimalbruchteil, IEEE754 Float-Format
            flowDecimalFraction = self.fetchViaDeviceManager_Helper(11, 2, "<f", "flowDecimalFraction")
            print(f"DEBUG: flowDecimalFraction (Little-Endian) = {flowDecimalFraction}")
            
            # Zeige auch Big-Endian
            flowDecimalFraction_BE = self.fetchViaDeviceManager_Helper(11, 2, ">f", "flowDecimalFraction (BE)")
            print(f"DEBUG: flowDecimalFraction (Big-Endian) = {flowDecimalFraction_BE}")
            
            # Wenn der Wert unplausibel erscheint, versuchen wir Big-Endian
            if flowDecimalFraction < 0 or flowDecimalFraction > 1:
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

def main():
    # RS485 Kommunikation und Geräte initialisieren
    # Ändern Sie die Port-Einstellungen entsprechend Ihrer Umgebung
    print("Initialisiere DeviceManager...")
    
    # Windows-Port-Format
    dev_manager = DeviceManager(port='COM1', baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=1)
    print("HINWEIS: Bitte passe den COM-Port in der main()-Funktion an deine Umgebung an (aktuell: COM1)")
    
    # Gerät hinzufügen (Taosonics T3-1-2-K-150 mit Adresse 0x28)
    print("Füge US Flow Sensor mit ID 0x28 hinzu...")
    dev_manager.add_device(device_id=0x28)
    
    # Gerät abrufen
    US_Flow_Sensor = dev_manager.get_device(device_id=0x28)
    
    # UsFlowHandler initialisieren
    print("Initialisiere UsFlowHandler...")
    us_flow_handler = UsFlowHandler(US_Flow_Sensor)
    
    # Endian-Format testen
    us_flow_handler.test_endian_format()
    
    # Sensorwerte auslesen und anzeigen
    print("Lese Sensorwerte...")
    
    try:
        # Bei einem Testprogramm mehrere Lesevorgänge durchführen, um Stabilität zu testen
        for i in range(3):
            print(f"\n--- Lesevorgang {i+1} ---")
            current_flow, total_flow = us_flow_handler.fetchViaDeviceManager()
            
            print(f"\nErgebnisse:")
            print(f"Aktuelle Durchflussrate: {current_flow} m³/h")
            print(f"Gesamtdurchflussmenge: {total_flow} m³")
            
            # Kurze Pause zwischen den Lesevorgängen
            if i < 2:  # Keine Pause nach dem letzten Lesevorgang
                print("Warte 2 Sekunden bis zum nächsten Lesevorgang...")
                time.sleep(2)
    
    except Exception as e:
        print(f"Fehler beim Auslesen des US Flow Sensors: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 