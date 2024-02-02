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

from tqdm import tqdm
from modbus_lib import DeviceManager
import time
import json
from gpiocontrol import GPIOControl
import atexit
import itertools
import sys


class Calibration:
    def __init__(self, device_manager):
        self.device_manager = device_manager
        self.radar_sensor = device_manager.get_device(device_id=0x01)
        self.pump = GPIOControl(7)  # assuming your pump is connected to GPIO pin 7
        self.calibration_data = []
        self.pump.set_direction('out')
        self.pump.set_value('1')  # Ensure pump is off at the start

        # Register the pump shutdown function to be called on exit
        atexit.register(self.shutdown_pump)

    def fill_tank(self):
        print("Sind Sie bereit, den Tank zu füllen? (yes/no)")
        answer = input().lower()
        if answer == 'yes':
            self.pump.set_value('0')  # Turn on pump
            print("Bitte warten Sie, bis das Wasser aus dem Ablauf läuft, und drücken Sie dann Enter.")
            input()
            self.pump.set_value('1')  # Turn off pump
            print("Bitte warten Sie, bis sich das System eingependelt hat.")

            # Initialize variables for checking if water level is stable
            previous_height = None
            stable_counter = 0

            # Create a simple rotating line loader
            spinner = itertools.cycle(['-', '/', '|', '\\'])

            while True:
                current_height = self.radar_sensor.read_radar_sensor(register_address=0x0001)
                if previous_height is not None and abs(current_height - previous_height) < 1:  # Assuming the unit is mm
                    stable_counter += 1
                else:
                    stable_counter = 0

                if stable_counter >= 30:  # If the water level has been stable for 30 seconds
                    print("Wasserpegel stabil, soll der Nullpunkt erfasst werden? (yes/no)")
                    if input().lower() == 'yes':
                        zero_point = current_height
                        print(f'Nullpunkt: {zero_point} mm')
                        self.calibration_data.append({
                            'zero_point': zero_point
                        })
                        self.save_calibration_data()
                        self.print_table()  # Print the table
                        break
                    else:
                        stable_counter = 0  # Reset the counter and continue checking

                previous_height = current_height

                # Display the rotating line loader
                sys.stdout.write(next(spinner))  # write the next character
                sys.stdout.flush()               # flush stdout buffer (actual character display)
                sys.stdout.write('\b')           # erase the last written character
                time.sleep(1)  # Wait for 1 second before the next check

        else:
            print("Bitte bereiten Sie sich vor und starten Sie das Programm erneut, wenn Sie bereit sind.")
            exit()

    def start_calibration(self):
        print("\\nWARNUNG: Der Kalibrierungsprozess wird nun gestartet. Die Pumpe wird eingeschaltet.")
        print("Sind Sie bereit, den Kalibrierungsprozess zu starten? (yes/no)")
        answer = input().lower()
        if answer == 'yes':
            self.pump.set_value('0')  # Turn on pump
        else:
            print("Kalibrierungsprozess wurde nicht gestartet. Bitte bereiten Sie sich vor und starten Sie das Programm erneut, wenn Sie bereit sind.")
            exit()

        vessel_size = float(input("Bitte geben Sie die Größe des Kalibriergefäßes in Litern ein: "))

        # Initialize variables for checking if water level is rising and stable
        previous_height = self.calibration_data[-1]['zero_point']
        stable_counter = 0
        rising_counter = 0
        reference_height = None

        # Create a simple rotating line loader
        spinner = itertools.cycle(['-', '/', '|', '\\'])

        while True:
            print("Bitte stellen Sie die Pumpe auf eine höhere Durchflussrate und bestätigen Sie mit Enter.")
            input()
            reference_height = self.radar_sensor.read_radar_sensor(register_address=0x0001)
            time.sleep(15)  # Wait 15 seconds before checking water level

            while True:
                current_height = self.radar_sensor.read_radar_sensor(register_address=0x0001)

                if current_height < reference_height and current_height < previous_height:
                    rising_counter += 1
                elif abs(current_height - previous_height) < 1:  # Assuming the unit is mm
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

                if rising_counter >= 30:  # If the water level has been rising for 30 seconds
                    print("Wasserpegel steigt weiter, Kalibrierung kann noch nicht durchgeführt werden.")
                    rising_counter = 0

                if stable_counter >= 30:  # If the water level has been stable for 30 seconds
                    print("Wasserpegel stabil, soll die Kalibrierung fortgesetzt werden? (yes/no)")
                    if input().lower() == 'yes':
                        break
                    else:
                        stable_counter = 0  # Reset the counter and continue checking

                previous_height = current_height

                # Display the rotating line loader
                sys.stdout.write(next(spinner))  # write the next character
                sys.stdout.flush()               # flush stdout buffer (actual character display)
                sys.stdout.write('\b')           # erase the last written character
                time.sleep(1)  # Wait for 1 second before the next check

            print("Bitte geben Sie ein, wie viel Zeit es in Sekunden gedauert hat, um das Kalibriergefäß zu füllen:")
            time_to_fill = float(input())
            flow_rate = vessel_size / time_to_fill  # Calculate flow rate in L/s
            print(f'Flow rate: {flow_rate} L/s')
            zero_point = self.calibration_data[0]['zero_point']  # Assuming the zero point is the first data entry
            actual_water_height = zero_point - current_height
            self.calibration_data.append({
            'water_height': actual_water_height,
            'flow_rate': flow_rate
})
            self.save_calibration_data()
            self.print_table()  # Print the table
            print("Möchten Sie weitermachen? (yes/no)")
            answer = input().lower()
            if answer != 'yes':
                break

    def print_table(self):
        print(f'{"Height (mm)":<12} {"Flow rate (L/s)":<15} {"Zero point (mm)":<15}')
        for data in self.calibration_data:
            height = data.get('height', '')
            flow_rate = data.get('flow_rate', '')
            zero_point = data.get('zero_point', '')
            print(f'{height:<12} {flow_rate:<15} {zero_point:<15}')

    def save_calibration_data(self):
        with open('calibration_data.json', 'w') as f:
            json.dump(self.calibration_data, f)

    def shutdown_pump(self):
        self.pump.set_value('1')  # Ensure pump is off

if __name__ == "__main__":
    dev_manager = DeviceManager(port='/dev/ttyS0', baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=1)
    dev_manager.add_device(device_id=0x01)
    calibrator = Calibration(dev_manager)
    calibrator.fill_tank()
    calibrator.start_calibration()