import requests
import subprocess
import time
from periphery import GPIO
import threading
from UPBoardRGBAsync import UPBoardRGBAsync

# Konfiguration
SERVER_URL = 'http://localhost:8080'
MAIN_SCRIPT_PATH = '/home/owipex_adm/owipex-sps/h2o.py'
BUTTON_PIN = 9  # GPIO-Pin für den Button
CHECK_INTERVAL = 10

# Initialisierung
rgb = UPBoardRGBAsync()
button_gpio = GPIO(BUTTON_PIN, "in")
main_process = None

def check_server_availability(url):
    try:
        response = requests.get(url)
        print(f"Serverantwort: {response.status_code}")  # Debug-Ausgabe
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Anpingen des Servers: {e}")  # Debug-Ausgabe
        return False

def start_main_script():
    global main_process
    print("Versuche, Hauptskript zu starten...")  # Debug-Ausgabe
    main_process = subprocess.Popen(['python3', MAIN_SCRIPT_PATH])
    print("Hauptskript gestartet.")  # Debug-Ausgabe

def stop_main_script():
    global main_process
    if main_process is not None:
        print("Stoppe Hauptskript...")  # Debug-Ausgabe
        main_process.terminate()
        main_process.wait()
        main_process = None
        print("Hauptskript gestoppt.")  # Debug-Ausgabe

def button_press_handler():
    press_time = None
    while True:
        button_pressed = button_gpio.read() == False  # Button gedrückt
        if button_pressed:
            print("Button gedrückt.")  # Debug-Ausgabe
            if press_time is None:
                press_time = time.time()
            continue  # Füge continue hier hinzu, um den nächsten Iterationsschritt sofort zu starten
        else:
            if press_time is not None:
                elapsed_time = time.time() - press_time
                if elapsed_time <= 3:
                    print("Kurzer Druck erkannt.")  # Debug-Ausgabe
                    rgb.start_blinking('B', 0.5, 3)  # Korrigiert: Blau blinken vor dem Starten
                    start_main_script()
                else:
                    print("Langer Druck erkannt.")  # Debug-Ausgabe
                    rgb.start_blinking('R', 0.5, 3)  # Korrigiert: Rot blinken vor dem Stoppen
                    stop_main_script()
                press_time = None  # Zurücksetzen der press_time für den nächsten Druck
        time.sleep(0.1)  # Kurzes Delay für den Loop


def monitor_system():
    while True:
        server_available = check_server_availability(SERVER_URL)
        if not server_available:
            rgb.start_blinking('R', blink_rate=None)  # Dauerhaftes Rot, wenn der Server nicht erreichbar ist
            print("Server nicht erreichbar, LED Rot.")  # Debug-Ausgabe
        elif server_available and (main_process is None or main_process.poll() is not None):
            rgb.start_blinking('B', blink_rate=None)  # Dauerhaftes Blau, wenn der Server erreichbar ist, aber das Hauptskript nicht läuft
            print("Server erreichbar, LED Blau.")  # Debug-Ausgabe
        time.sleep(CHECK_INTERVAL)

# Startet einen Thread, um das System zu überwachen
monitor_thread = threading.Thread(target=monitor_system)
monitor_thread.start()

# Handhabt Button-Press-Ereignisse im Hauptthread
button_press_handler()

# Aufräumarbeiten
rgb.cleanup()
button_gpio.close()
