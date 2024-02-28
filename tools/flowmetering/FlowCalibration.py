# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: Calibration Tool V0.1
# Description: Calibration program for water level sensor and flow rate
# -----------------------------------------------------------------------------

print("""
-----------------------------------------------------------------------------
Company: KARIM Technologies
Author: Sayed Amir Karim
Copyright: 2023 KARIM Technologies

License: All Rights Reserved

Module: Calibration Tool V0.1
Description: Calibration program for water level sensor and flow rate
-----------------------------------------------------------------------------
""")

from libs.modbus_lib import DeviceManager
import time
import json
import atexit
import itertools
import sys


class Calibration:
    def __init__(self, device_manager):
        self.device_manager = device_manager
        self.radar_sensor = device_manager.get_device(device_id=0x01)
        self.calibration_data = []

    def fill_tank(self):
        print("Sind Sie bereit, den Tank zu füllen? (yes/no)")
        answer = input().lower()
        if answer == 'yes':
            print("Bitte starten Sie die Pumpe manuell und drücken Sie Enter.")
            input()  # Benutzer startet die Pumpe manuell
            print("Bitte warten Sie, bis das Wasser aus dem Ablauf läuft, und drücken Sie dann Enter.")
            input()  # Benutzer wartet auf den Wasserfluss
            print("Bitte stoppen Sie die Pumpe manuell und bestätigen Sie mit Enter.")
            input()  # Benutzer stoppt die Pumpe manuell

            print("Bitte warten Sie, bis sich das System eingependelt hat.")
            previous_height = None
            stable_counter = 0
            spinner = itertools.cycle(['-', '/', '|', '\\'])

            while True:
                current_height = self.radar_sensor.read_radar_sensor(register_address=0x0001)
                if previous_height is not None and abs(current_height - previous_height) < 1:
                    stable_counter += 1
                else:
                    stable_counter = 0

                if stable_counter >= 30:
                    print("\nWasserpegel stabil, soll der Nullpunkt erfasst werden? (yes/no)")
                    if input().lower() == 'yes':
                        zero_point = current_height
                        print(f'Nullpunkt: {zero_point} mm')
                        self.calibration_data.append({
                            'zero_point': zero_point
                        })
                        self.save_calibration_data()
                        self.print_table()
                        break
                    else:
                        stable_counter = 0

                previous_height = current_height
                sys.stdout.write(next(spinner))
                sys.stdout.flush()
                sys.stdout.write('\b')
                time.sleep(1)

        else:
            print("Bitte bereiten Sie sich vor und starten Sie das Programm erneut, wenn Sie bereit sind.")
            exit()

    def start_calibration(self):
        print("\nWARNUNG: Der Kalibrierungsprozess wird nun gestartet.")
        print("Sind Sie bereit, den Kalibrierungsprozess zu starten? (yes/no)")
        answer = input().lower()
        if answer == 'yes':
            print("Bitte starten Sie die Pumpe manuell und drücken Sie Enter.")
            input()  # Benutzer startet die Pumpe manuell

            vessel_size = float(input("Bitte geben Sie die Größe des Kalibriergefäßes in Litern ein: "))
            previous_height = self.calibration_data[-1]['zero_point']
            stable_counter = 0
            rising_counter = 0
            reference_height = None
            spinner = itertools.cycle(['-', '/', '|', '\\'])

            while True:
                print("Bitte stellen Sie die Pumpe auf eine höhere Durchflussrate und bestätigen Sie mit Enter.")
                input()  # Benutzer passt Durchflussrate an
                reference_height = self.radar_sensor.read_radar_sensor(register_address=0x0001)
                time.sleep(15)  # Warten, um das Niveau zu überprüfen

                while True:
                    current_height = self.radar_sensor.read_radar_sensor(register_address=0x0001)
                    if current_height < reference_height and current_height < previous_height:
                        rising_counter += 1
                    elif abs(current_height - previous_height) < 1:
                        stable_counter += 1
                        rising_counter = 0
                    else:
                        print("Fehler: Der Wasserstand steigt nicht. Möchten Sie die Messung wiederholen? (yes/no)")
                        if input().lower() == 'yes':
                            reference_height = current_height
                            time.sleep(15)
                            continue
                        else:
                            exit()

                    if rising_counter >= 30:
                        print("Wasserpegel steigt weiter, Kalibrierung kann noch nicht durchgeführt werden.")
                        rising_counter = 0

                    if stable_counter >= 30:
                        print("Wasserpegel stabil, soll die Kalibrierung fortgesetzt werden? (yes/no)")
                        if input().lower() == 'yes':
                            break
                        else:
                            stable_counter = 0

                    previous_height = current_height
                    sys.stdout.write(next(spinner))
                    sys.stdout.flush()
                    sys.stdout.write('\b')
                    time.sleep(1)

                print("Bitte geben Sie ein, wie viel Zeit es in Sekunden gedauert hat, um das Kalibriergefäß zu füllen:")
                time_to_fill = float(input())
                flow_rate = vessel_size / time_to_fill
                print(f'Flow rate: {flow_rate} L/s')
                zero_point = self.calibration_data[0]['zero_point']
                actual_water_height = zero_point - current_height
                self.calibration_data.append({
                    'water_height': actual_water_height,
                    'flow_rate': flow_rate
                })
                self.save_calibration_data()
                self.print_table()
                print("Möchten Sie weitermachen? (yes/no)")
                answer = input().lower()
                if answer != 'yes':
                    break

    def print_table(self):
        print("\nKalibrierungsdaten:")
        print(f'{"Höhe (mm)":<12} {"Durchflussrate (L/s)":<20} {"Nullpunkt (mm)":<15}')
        for data in self.calibration_data:
            height = data.get('water_height', '')
            flow_rate = data.get('flow_rate', '')
            zero_point = data.get('zero_point', '')
            print(f'{height:<12} {flow_rate:<20} {zero_point:<15}')

    def save_calibration_data(self):
        with open('calibration_data.json', 'w') as f:
            json.dump(self.calibration_data, f)

if __name__ == "__main__":
    dev_manager = DeviceManager(port='/dev/ttyS0', baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=1)
    dev_manager.add_device(device_id=0x01)
    calibrator = Calibration(dev_manager)
    calibrator.fill_tank()
    calibrator.start_calibration()
