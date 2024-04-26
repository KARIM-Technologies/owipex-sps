import requests
import subprocess
import time
import signal
from periphery import GPIO
import threading

# Konfiguration
SERVER_URL = 'http://localhost:8080'
MAIN_SCRIPT_PATH = '/home/owipex_adm/owipex-sps/h2o.py'
BUTTON_PIN = 9  # GPIO-Pin für den Button
LED_PINS = {'R': 5, 'G': 6, 'B': 26}  # Angenommene Pins für die LEDs
CHECK_INTERVAL = 10

# Initialisierung
button_gpio = GPIO(BUTTON_PIN, "in")
leds = {color: GPIO(pin, "out") for color, pin in LED_PINS.items()}
main_process = None

is_main_script_running = False  # Statusvariable für den Hauptskript-Zustand
manually_stopped = False  # Gibt an, ob das Skript manuell gestoppt wurde

def set_led_color(color):
    # Alle LEDs ausschalten
    for led in leds.values():
        led.write(True)
    # Gewünschte LED einschalten (False bedeutet "an")
    if color in leds:
        leds[color].write(False)

def check_server_availability(url):
    try:
        response = requests.get(url)
        print(f"Serverantwort: {response.status_code}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Anpingen des Servers: {e}")
        return False

def start_main_script():
    global main_process, is_main_script_running, manually_stopped
    if not is_main_script_running:
        print("Versuche, Hauptskript zu starten...")
        main_process = subprocess.Popen(['python3', MAIN_SCRIPT_PATH])
        time.sleep(1)
        if main_process.poll() is None:
            print("Hauptskript erfolgreich gestartet.")
            is_main_script_running = True
            manually_stopped = False  # Zurücksetzen beim Start
            set_led_color('G')

def stop_main_script():
    global main_process, is_main_script_running, manually_stopped
    if is_main_script_running:
        print("Send SIGINT to Hauptskript...")
        main_process.send_signal(signal.SIGINT)
        main_process.wait()
        main_process = None
        is_main_script_running = False
        manually_stopped = True  # Setzen, da manuell gestoppt
        print("Hauptskript gestoppt.")
        set_led_color('B')

def button_press_handler():
    global manually_stopped
    press_time = None
    while True:
        button_pressed = button_gpio.read() == False
        if button_pressed:
            if press_time is None:
                press_time = time.time()
        else:
            if press_time is not None:
                elapsed_time = time.time() - press_time
                if 2 < elapsed_time <= 5:
                    print("Mittlerer Druck erkannt, starte Hauptskript.")
                    start_main_script()
                elif elapsed_time > 5:
                    print("Langer Druck erkannt, stoppe Hauptskript.")
                    stop_main_script()
                press_time = None
        time.sleep(0.1)

def monitor_system():
    global manually_stopped
    while True:
        server_available = check_server_availability(SERVER_URL)
        if main_process is not None and main_process.poll() is None:
            set_led_color('G')
            print("Hauptskript läuft, LED Grün.")
        elif main_process is not None and main_process.poll() is not None and not manually_stopped:
            # Hauptskript wurde unerwartet beendet, nicht durch manuelles Stoppen
            print("Hauptskript unerwartet gestoppt, versuche neu zu starten.")
            start_main_script()
        elif not server_available:
            set_led_color('R')
            print("Server nicht erreichbar, LED Rot.")
        else:
            set_led_color('B')
            print("Server erreichbar, Hauptskript nicht gestartet oder bereits gestoppt, LED Blau.")
        time.sleep(CHECK_INTERVAL)

# Aufräumen
def cleanup():
    for gpio in leds.values():
        gpio.write(True)  # LEDs ausschalten
        gpio.close()
    button_gpio.close()

try:
    # Startet einen Thread, um das System zu überwachen
    monitor_thread = threading.Thread(target=monitor_system)
    monitor_thread.start()

    # Handhabt Button-Press-Ereignisse im Hauptthread
    button_press_handler()
finally:
    cleanup()
