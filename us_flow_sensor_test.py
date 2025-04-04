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
        self.preferred_endian = "<"  # Default zu Little-Endian

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

    def scan_all_registers(self, start_reg=0, end_reg=1000, step=1):
        """Scannt alle Register im angegebenen Bereich und sucht nach möglichen Testwerten."""
        print(f"\n=== SCANNING ALL REGISTERS FROM {start_reg} TO {end_reg} ===")
        print("Suche nach möglichen Testwerten...")
        
        interesting_values = []
        # Liste für Register, deren Wert der Register-Nummer entspricht
        self_matching_registers = []
        
        for reg in range(start_reg, end_reg+1, step):
            try:
                # Float-Wert (Little-Endian)
                float_le = self.sensor.read_register_FOR_TAOSONIC_ONLY(reg, 2, "<f")
                print(f"✓ RAW Register {reg}: Float (LE) = {float_le}")
                # Float-Wert (Big-Endian)
                float_be = self.sensor.read_register_FOR_TAOSONIC_ONLY(reg, 2, ">f")
                print(f"✓ RAW Register {reg}: Float (BE) = {float_be}")

                # Integer-Wert (16-bit)
                int16 = self.sensor.read_register_FOR_TAOSONIC_ONLY(reg, 1, ">h")
                
                # Wenn möglich, auch 32-bit Integer lesen
                if reg < end_reg:
                    # Long-Wert (Little-Endian)
                    long_le = self.sensor.read_register_FOR_TAOSONIC_ONLY(reg, 2, "<l")
                    # Long-Wert (Big-Endian)
                    long_be = self.sensor.read_register_FOR_TAOSONIC_ONLY(reg, 2, ">l")
                else:
                    long_le = None
                    long_be = None
                
                # Prüfe, ob der Wert gleich der Register-Nummer ist
                # Float-Werte mit einer kleinen Toleranz prüfen
                if float_le is not None and abs(float_le - reg) < 0.1:
                    self_matching_registers.append((reg, "Float LE", float_le))
                    print(f"✓ Register {reg}: Float (LE) = {float_le} (ENTSPRICHT REGISTER-NUMMER!)")
                    
                if float_be is not None and abs(float_be - reg) < 0.1:
                    self_matching_registers.append((reg, "Float BE", float_be))
                    print(f"✓ Register {reg}: Float (BE) = {float_be} (ENTSPRICHT REGISTER-NUMMER!)")
                
                # Integer-Werte exakt prüfen
                if int16 is not None and int16 == reg:
                    self_matching_registers.append((reg, "Int16", int16))
                    print(f"✓ Register {reg}: Int16 = {int16} (ENTSPRICHT REGISTER-NUMMER!)")
                
                # Long-Werte exakt prüfen
                if long_le is not None and long_le == reg:
                    self_matching_registers.append((reg, "Long LE", long_le))
                    print(f"✓ Register {reg}: Long (LE) = {long_le} (ENTSPRICHT REGISTER-NUMMER!)")
                    
                if long_be is not None and long_be == reg:
                    self_matching_registers.append((reg, "Long BE", long_be))
                    print(f"✓ Register {reg}: Long (BE) = {long_be} (ENTSPRICHT REGISTER-NUMMER!)")
                
                # Prüfe, ob einer der Werte interessant ist
                # 1. Float-Werte, die nahe an einer runden Zahl liegen
                if float_le is not None and abs(float_le - round(float_le)) < 0.01 and abs(float_le) > 0.1:
                    interesting_values.append((reg, "Float LE", float_le))
                    print(f"Register {reg}: Float (LE) = {float_le}")
                    
                if float_be is not None and abs(float_be - round(float_be)) < 0.01 and abs(float_be) > 0.1:
                    interesting_values.append((reg, "Float BE", float_be))
                    print(f"Register {reg}: Float (BE) = {float_be}")
                
                # 2. Integer-Werte, die Testwerte sein könnten
                if int16 is not None and int16 > 100:
                    interesting_values.append((reg, "Int16", int16))
                    print(f"Register {reg}: Int16 = {int16}")
                
                # 3. Long-Werte, die Testwerte sein könnten
                if long_le is not None and long_le > 10000:
                    interesting_values.append((reg, "Long LE", long_le))
                    print(f"Register {reg}: Long (LE) = {long_le}")
                    
                if long_be is not None and long_be > 10000:
                    interesting_values.append((reg, "Long BE", long_be))
                    print(f"Register {reg}: Long (BE) = {long_be}")
                    
            except Exception as e:
                print(f"Fehler beim Scannen von Register {reg}: {e}")
                continue  # Weitermachen mit dem nächsten Register
                
            # Fortschritt anzeigen
            if reg % 100 == 0:
                print(f"Fortschritt: Register {reg}/{end_reg} durchsucht...")
        
        # Zusammenfassung der gefundenen interessanten Werte
        print("\n=== ZUSAMMENFASSUNG INTERESSANTER WERTE ===")
        if interesting_values:
            for reg, format, value in interesting_values:
                print(f"Register {reg}: {format} = {value}")
        else:
            print("Keine interessanten Werte gefunden.")
        
        # Zusammenfassung der Register, deren Wert der Register-Nummer entspricht
        print("\n=== REGISTER MIT WERT = REGISTER-NUMMER ===")
        if self_matching_registers:
            for reg, format, value in self_matching_registers:
                print(f"✓ Register {reg}: {format} = {value}")
            
            # Empfehlung für Endian-Format basierend auf selbst-matchenden Registern
            le_count = sum(1 for r in self_matching_registers if r[1].endswith("LE"))
            be_count = sum(1 for r in self_matching_registers if r[1].endswith("BE"))
            
            if le_count > 0 and le_count >= be_count:
                print(f"\nEmpfehlung: Little-Endian Format (LE) basierend auf {le_count} selbst-matchenden Registern.")
                self.preferred_endian = "<"
            elif be_count > 0:
                print(f"\nEmpfehlung: Big-Endian Format (BE) basierend auf {be_count} selbst-matchenden Registern.")
                self.preferred_endian = ">"
        else:
            print("Keine Register gefunden, deren Wert der Register-Nummer entspricht.")
        
        print("=== SCAN ABGESCHLOSSEN ===\n")
        return interesting_values, self_matching_registers

    def test_endian_format(self):
        print("\n=== MANUELLER ENDIAN FORMAT TEST ===")
        try:
            # Wir testen mit tatsächlich benötigten Registern, 
            # da die Register 361 und 363 keine eindeutigen Ergebnisse liefern
            
            # Teste Durchflussrate (Register 1-2)
            flow_LE = self.fetchViaDeviceManager_ForTaoSonicOnly_Helper(1, 2, "<f", "Flow (LE)")
            flow_BE = self.fetchViaDeviceManager_ForTaoSonicOnly_Helper(1, 2, ">f", "Flow (BE)")
            print(f"Flow Rate: Little-Endian={flow_LE} m³/h, Big-Endian={flow_BE} m³/h")
            
            # Teste Akkumulator (Register 9-10)
            acc_LE = self.fetchViaDeviceManager_ForTaoSonicOnly_Helper(9, 2, "<l", "Accumulator (LE)")
            acc_BE = self.fetchViaDeviceManager_ForTaoSonicOnly_Helper(9, 2, ">l", "Accumulator (BE)")
            print(f"Accumulator: Little-Endian={acc_LE}, Big-Endian={acc_BE}")
            
            # Teste Dezimalbruchteil (Register 11-12)
            frac_LE = self.fetchViaDeviceManager_ForTaoSonicOnly_Helper(11, 2, "<f", "Fraction (LE)")
            frac_BE = self.fetchViaDeviceManager_ForTaoSonicOnly_Helper(11, 2, ">f", "Fraction (BE)")
            print(f"Decimal Fraction: Little-Endian={frac_LE}, Big-Endian={frac_BE}")
            
            # Plausibilitätsprüfung
            print("\nPlausibilitätsanalyse:")
            
            # Prüfe Durchflussrate
            if 0 <= flow_LE <= 1000:
                print("✓ Little-Endian Flow Rate ist plausibel (0-1000 m³/h)")
                self.preferred_endian = "<"
            elif 0 <= flow_BE <= 1000:
                print("✓ Big-Endian Flow Rate ist plausibel (0-1000 m³/h)")
                self.preferred_endian = ">"
            else:
                print("⚠ Keine plausible Flow Rate erkannt!")
                
            # Prüfe Akkumulator
            if acc_LE >= 0:
                print("✓ Little-Endian Accumulator ist plausibel (>= 0)")
                self.preferred_endian = "<"
            elif acc_BE >= 0:
                print("✓ Big-Endian Accumulator ist plausibel (>= 0)")
                self.preferred_endian = ">"
            else:
                print("⚠ Kein plausibler Accumulator erkannt!")
                
            # Prüfe Dezimalbruchteil
            if 0 <= frac_LE <= 1:
                print("✓ Little-Endian Decimal Fraction ist plausibel (0-1)")
                self.preferred_endian = "<"
            elif 0 <= frac_BE <= 1:
                print("✓ Big-Endian Decimal Fraction ist plausibel (0-1)")
                self.preferred_endian = ">"
            else:
                print("⚠ Keine plausible Decimal Fraction erkannt!")
                
            print(f"Wahrscheinliches Endian-Format: {self.preferred_endian}")
            print("=== ENDIAN FORMAT TEST ABGESCHLOSSEN ===\n")
        except Exception as e:
            print(f"Fehler beim Testen des Endian-Formats: {e}")

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
            currentFlowValue = self.fetchViaDeviceManager_ForTaoSonicOnly_Helper(1, 2, "<f", "currentFlowValue")
            print(f"DEBUG: currentFlowValue (Little-Endian) = {currentFlowValue} m³/h")
            
            # Zeige auch die Big-Endian-Version an
            currentFlowValue_BE = self.fetchViaDeviceManager_ForTaoSonicOnly_Helper(1, 2, ">f", "currentFlowValue (BE)")
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
            totalFlowUnitNumber = self.fetchViaDeviceManager_ForTaoSonicOnly_Helper(1438, 1, ">h", "unitNumber")
            print(f"DEBUG: totalFlowUnitNumber = {totalFlowUnitNumber}")
            
            totalFlowMultiplier = self.fetchViaDeviceManager_ForTaoSonicOnly_Helper(1439, 1, ">h", "multiplier")
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
            flowValueAccumulator_LE = self.fetchViaDeviceManager_ForTaoSonicOnly_Helper(9, 2, "<l", "flowAccumulator (LE)")
            print(f"DEBUG: flowValueAccumulator (Little-Endian) = {flowValueAccumulator_LE}")
            
            flowValueAccumulator_BE = self.fetchViaDeviceManager_ForTaoSonicOnly_Helper(9, 2, ">l", "flowAccumulator (BE)")
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
            flowDecimalFraction = self.fetchViaDeviceManager_ForTaoSonicOnly_Helper(11, 2, "<f", "flowDecimalFraction")
            print(f"DEBUG: flowDecimalFraction (Little-Endian) = {flowDecimalFraction}")
            
            # Zeige auch Big-Endian
            flowDecimalFraction_BE = self.fetchViaDeviceManager_ForTaoSonicOnly_Helper(11, 2, ">f", "flowDecimalFraction (BE)")
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
    
    # Linux-Port-Format für die Ausführung unter Linux
    dev_manager = DeviceManager(port='/dev/ttyS0', baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=1)
    
    # Gerät hinzufügen (Taosonics T3-1-2-K-150 mit Adresse 0x28)
    print("Füge US Flow Sensor mit ID 0x28 hinzu...")
    # TODO: hier wieder auf 40 (0x28) zurückstellen
    # dev_manager.add_device(device_id=0x28)
    dev_manager.add_device(device_id=1)
    
    # Gerät abrufen
    # TODO: hier wieder auf 40 (0x28) zurückstellen
    # US_Flow_Sensor = dev_manager.get_device(device_id=0x28)
    US_Flow_Sensor = dev_manager.get_device(device_id=1)
    
    # UsFlowHandler initialisieren
    print("Initialisiere UsFlowHandler...")
    us_flow_handler = UsFlowHandler(US_Flow_Sensor)
    
    # Alle Register scannen
    # print("Scanne alle Register bis 1000...")
    # interesting_values, self_matching_registers = us_flow_handler.scan_all_registers(0, 1000, 1)
    print("Scanne Register 361...")
    interesting_values, self_matching_registers = us_flow_handler.scan_all_registers(361, 361, 1)
    
    # Endian-Format testen
    us_flow_handler.test_endian_format()
    
    # Sensorwerte auslesen und anzeigen
    print("Lese Sensorwerte...")
    
    try:
        # Bei einem Testprogramm mehrere Lesevorgänge durchführen, um Stabilität zu testen
        for i in range(1):  # Auf 1 Lesevorgang reduziert
            print(f"\n--- Lesevorgang {i+1} ---")
            current_flow, total_flow = us_flow_handler.fetchViaDeviceManager()
            
            print(f"\nErgebnisse:")
            print(f"Aktuelle Durchflussrate: {current_flow} m³/h")
            print(f"Gesamtdurchflussmenge: {total_flow} m³")
    
    except Exception as e:
        print(f"Fehler beim Auslesen des US Flow Sensors: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 