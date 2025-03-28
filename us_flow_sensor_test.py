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

    def calculateSumFlowValueForTaosonic(self, totalFlowUnitNumber, totalFlowMultiplier, flowValueAccumulator, flowDecimalFraction):
        if not isinstance(totalFlowMultiplier, int):
            raise Exception(f"invalid type for total flow multiplier: {type(totalFlowMultiplier)}")
        if totalFlowMultiplier < -4 or totalFlowMultiplier > 4:
            raise Exception(f"invalid total flow multiplier value found in Taosonic Flow Meter (see reg 1439): {totalFlowMultiplier}")

        if totalFlowUnitNumber != TAOSONICFLOWUNIT_M3 and totalFlowUnitNumber != TAOSONICFLOWUNIT_LITER and totalFlowUnitNumber != TAOSONICFLOWUNIT_GAL and totalFlowUnitNumber != TAOSONICFLOWUNIT_FEET3:
            raise Exception(f"invalid total flow unit number found in Taosonic Flow Meter (see reg 1438): {totalFlowUnitNumber}")

        flowValueAccumulatorAsFloat = float(flowValueAccumulator)
        flowValueAccumulatorWithFractionAsFloat = flowValueAccumulatorAsFloat + flowDecimalFraction

        sumFlowValue = flowValueAccumulatorWithFractionAsFloat * 10**(totalFlowMultiplier-3)
        print("calculateSumFlowValueForTaosonic, sumFlowValue: " + str(sumFlowValue))
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
        
        # Falls keine der bekannten Einheiten übereinstimmt
        raise Exception(f"invalid total flow unit number for Taosonic Flow Meter (see reg 1438): {unitNumber}")

    def fetchViaDeviceManager(self):
        try:
            # get current flow
            currentFlowValue = self.fetchViaDeviceManager_Helper(1, 2, ">f", "current flow")
            print("fetchViaDeviceManager, currentFlowValue: " + str(currentFlowValue))

            # get registers for overall flow sum
            totalFlowUnitNumber = self.fetchViaDeviceManager_Helper(1438, 1, ">h", "flow unit")
            print("fetchViaDeviceManager, totalFlowUnitNumber: " + str(totalFlowUnitNumber))

            totalFlowMultiplier = self.fetchViaDeviceManager_Helper(1439, 1, ">h", "flow multiplier")
            print("fetchViaDeviceManager, totalFlowMultiplier: " + str(totalFlowMultiplier))

            flowValueAccumulator = self.fetchViaDeviceManager_Helper(25, 2, ">l", "flow accumulator")
            print("fetchViaDeviceManager, flowValueAccumulator: " + str(flowValueAccumulator))

            flowDecimalFraction = self.fetchViaDeviceManager_Helper(27, 2, ">f", "decimal fraction")
            print("fetchViaDeviceManager, flowDecimalFraction: " + str(flowDecimalFraction))

            # calculate overall flow sum
            sumFlowValueInUnit = self.calculateSumFlowValueForTaosonic(totalFlowUnitNumber, totalFlowMultiplier, flowValueAccumulator, flowDecimalFraction)
            print("fetchViaDeviceManager, sumFlowValueInUnit: " + str(sumFlowValueInUnit))
            sumFlowValueInM3 = self.convertFlowValueFromUnitToM3ForTaosonic(sumFlowValueInUnit, totalFlowUnitNumber)
            print("fetchViaDeviceManager, sumFlowValueInM3: " + str(sumFlowValueInM3))

            print(f"Ergebnis: currentFlowValue={currentFlowValue}, sumFlowValue={sumFlowValueInM3}")
            return currentFlowValue, sumFlowValueInM3
            
        except Exception as e:
            print(f"Fehler beim Abrufen der Durchflusswerte: {e}")
            import traceback
            traceback.print_exc()
            return None, None


if __name__ == "__main__":
    print("US Flow Sensor Test startet...")
    
    # Teste verschiedene Device-IDs
    device_ids_to_test = [0x01, 0x04, 0x28, 0x40]
    
    for device_id in device_ids_to_test:
        print(f"=== Teste Device ID: 0x{device_id:02X} ===")
        try:
            # Initialisiere den DeviceManager
            dev_manager = DeviceManager(port='/dev/ttyS0', baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=2)
            
            # Füge das Gerät hinzu und hole es
            dev_manager.add_device(device_id=device_id)
            flow_sensor = dev_manager.get_device(device_id=device_id)
            
            # Erstelle den UsFlowHandler
            flow_handler = UsFlowHandler(flow_sensor)
            
            print(f"Versuche Flow-Daten mit Device ID 0x{device_id:02X} zu lesen...")
            
            # Lese den aktuellen Durchfluss
            try:
                currentFlow, totalFlow = flow_handler.fetchViaDeviceManager()
                if currentFlow is not None:
                    print(f"Erfolgreich! Aktueller Durchfluss={currentFlow}, Gesamtdurchfluss={totalFlow}")
                else:
                    print(f"Fehler: Konnte keine Daten mit Device ID 0x{device_id:02X} lesen.")
            except Exception as e:
                print(f"Fehler beim Lesen mit Device ID 0x{device_id:02X}: {e}")
                import traceback
                traceback.print_exc()
                
        except Exception as e:
            print(f"Fehler bei der Initialisierung mit Device ID 0x{device_id:02X}: {e}")
        
        print(f"=== Test für Device ID: 0x{device_id:02X} abgeschlossen ===\n")
        
    print("US Flow Sensor Test abgeschlossen.") 