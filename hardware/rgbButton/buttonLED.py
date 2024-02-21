import requests
import subprocess
import time
from UPBoardRGB import UPBoardRGB
from periphery import GPIO
import threading

# Konfiguration
SERVER_URL = 'http://localhost:8080'
MAIN_SCRIPT_PATH = '/home/owipex_adm/owipex-sps/h2o.py'
CHECK_INTERVAL = 10
BUTTON_GPIO_PIN = 25  # Angenommene GPIO-Pin-Nummer für den Button
rgb = UPBoardRGB()
button_gpio = GPIO("/dev/gpiochip0", BUTTON_GPIO_PIN, "in")

main_process = None

def check_server_availability(url):
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def start_main_script():
    global main_process
    main_process = subprocess.Popen(['python3', MAIN_SCRIPT_PATH])
    rgb.set_color('G')  # Grün für Skript läuft

def stop_main_script():
    if main_process:
        main_process.terminate()
        main_process.wait()
        rgb.set_color('B')  # Blau wenn Server erreichbar aber Skript gestoppt

def monitor_button_press():
    press_time = None
    while True:
        state = button_gpio.read()
        if not state:  # Button wird gedrückt
            if press_time is None:
                press_time = time.time()
            else:
                if (time.time() - press_time) > 3:  # Länger als 3 Sekunden gedrückt
                    stop_main_script()
                    break
        else:
            if press_time is not None and (time.time() - press_time) <= 3:
                start_main_script()  # Kurzer Druck, starte das Skript
                break
            press_time = None
        time.sleep(0.1)  # Entprellzeit

def main():
    while True:
        if check_server_availability(SERVER_URL):
            rgb.set_color('B')  # Blau wenn Server erreichbar
            monitor_button_press()
        else:
            rgb.set_color('R')  # Rot wenn Server nicht erreichbar
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Programm beendet.")
    finally:
        rgb.cleanup()
        button_gpio.close()
