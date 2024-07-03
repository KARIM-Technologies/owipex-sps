import requests
import subprocess
import time
import signal
from periphery import GPIO
import threading
import json
from tb_gateway_mqtt import TBDeviceMqttClient

# Configuration
import os
# from dotenv import load_dotenv
# dotenv_path = '/etc/owipex/.env'
# load_dotenv(dotenv_path=dotenv_path)
# ACCESS_TOKEN = os.environ.get('THINGSBOARD_ACCESS_TOKEN')

# Konfiguration
SERVER_URL = 'http://localhost:8080'
MAIN_SCRIPT_PATH = '/home/owipex_adm/owipex-sps/h2o.py'
BUTTON_PIN = 9  # GPIO-Pin für den Button
LED_PINS = {'R': 5, 'G': 6, 'B': 26}  # Angenommene Pins für die LEDs
CHECK_INTERVAL = 10
THINGSBOARD_SERVER = 'localhost'
THINGSBOARD_PORT = 1883  # Ensure the port is an integer
ACCESS_TOKEN = '7gRqksFeFF3i7LjuRHqk'

# Initialisierung
button_gpio = GPIO(BUTTON_PIN, "in")
leds = {color: GPIO(pin, "out") for color, pin in LED_PINS.items()}
main_process = None

# Initialize ThingsBoard MQTT client
tb_client = TBDeviceMqttClient(THINGSBOARD_SERVER, username=ACCESS_TOKEN)

# Status variables
is_main_script_running = False  # Statusvariable für den Hauptskript-Zustand
manually_stopped = False  # Gibt an, ob das Skript manuell gestoppt wurde
script_status = {'ScriptRunning': True}

def set_led_color(color):
    for led in leds.values():
        led.write(True)  # Alle LEDs ausschalten
    if color in leds:
        leds[color].write(False)  # Gewünschte LED einschalten

def check_server_availability():
    try:
        response = requests.get(SERVER_URL)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def start_main_script():
    global main_process, is_main_script_running, script_status, manually_stopped
    if not is_main_script_running and check_server_availability():
        main_process = subprocess.Popen(['python3', MAIN_SCRIPT_PATH])
        if main_process.poll() is None:
            is_main_script_running = True
            manually_stopped = False
            script_status['ScriptRunning'] = True
            set_led_color('G')
            tb_client.send_attributes(script_status)

def stop_main_script():
    global main_process, is_main_script_running, manually_stopped, script_status
    if is_main_script_running and main_process:
        main_process.send_signal(signal.SIGINT)
        main_process.wait()
        main_process = None
        is_main_script_running = False
        manually_stopped = True
        script_status['ScriptRunning'] = False
        set_led_color('B')
        tb_client.send_attributes(script_status)

def rpc_callback(id, request_body):
    global is_main_script_running, script_status, tb_client
    command = request_body.get('method')
    if command == 'setScriptRunning':
        params = request_body.get('params')
        if params:
            start_main_script()
        else:
            stop_main_script()

def button_press_handler():
    global manually_stopped
    press_time = None
    while True:
        if button_gpio.read() == False:
            press_time = time.time() if press_time is None else press_time
        else:
            if press_time is not None:
                elapsed_time = time.time() - press_time
                if 2 < elapsed_time <= 5:
                    start_main_script() if not is_main_script_running else None
                elif elapsed_time > 5:
                    stop_main_script() if is_main_script_running else None
                press_time = None
        time.sleep(0.1)

def monitor_system():
    global manually_stopped, script_status
    while True:
        if check_server_availability():
            # start_main_script() if not is_main_script_running and not manually_stopped else set_led_color('G')
            start_main_script() if not is_main_script_running and not manually_stopped else None
        else:
            set_led_color('R')
        time.sleep(CHECK_INTERVAL)

# Aufräumen
def cleanup():
    for gpio in leds.values():
        gpio.write(True)  # LEDs ausschalten
        gpio.close()
    button_gpio.close()

# Set up ThingsBoard MQTT client
tb_client.set_server_side_rpc_request_handler(rpc_callback)
tb_client.connect()

# Run threads
try:
    threading.Thread(target=monitor_system).start()
    button_press_handler()
    '''
    # For running the button handler in a thread    
    threading.Thread(target=button_press_handler).start()
    threading.Event().wait()  # Keeps the main thread running
    '''
finally:
    cleanup()
    tb_client.disconnect()
