import requests
import subprocess
import time
import psutil  # Zusätzliches Modul zur Überprüfung laufender Prozesse

# Konfiguration
SERVER_URL = 'http://localhost:8080'
MAIN_SCRIPT_PATH = '/home/owipex_adm/owipex-sps/h2o.py'
CHECK_INTERVAL = 25  # Sekunden zwischen den Überprüfungen
MAX_RETRIES = 15  # Maximale Anzahl an Wiederholungsversuchen

def check_server_availability(url):
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def is_main_script_running(script_path):
    # Überprüft, ob ein Prozess mit dem Skriptpfad läuft
    for process in psutil.process_iter(['cmdline']):
        if script_path in process.info['cmdline']:
            return True
    return False

def start_main_script(script_path):
    if not is_main_script_running(script_path):
        subprocess.Popen(['python3', script_path])
        print("Hauptskript gestartet.")
    else:
        print("Hauptskript läuft bereits.")

def main():
    while True:  # Ändern Sie dies in eine Endlosschleife
        retries = 0
        while retries < MAX_RETRIES:
            if check_server_availability(SERVER_URL):
                print("Server ist erreichbar. Überprüfe Hauptskript.")
                start_main_script(MAIN_SCRIPT_PATH)
                break
            else:
                print(f"Server nicht erreichbar. Versuche erneut in {CHECK_INTERVAL} Sekunden...")
                time.sleep(CHECK_INTERVAL)
                retries += 1

        if retries == MAX_RETRIES:
            print("Maximale Anzahl an Versuchen erreicht. Warte, bevor erneut versucht wird...")
        time.sleep(CHECK_INTERVAL)  # Wartezeit, bevor die Überprüfungsschleife neu gestartet wird

if __name__ == '__main__':
    main()
