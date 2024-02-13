import subprocess
import time

# Konfiguration
SERVER_HOST = 'localhost'
MAIN_SCRIPT_PATH = '/pfad/zu/deinem/hauptscript.py'  # Aktualisiere dies entsprechend
CHECK_INTERVAL = 10  # Sekunden zwischen den Überprüfungen
MAX_RETRIES = 5  # Maximale Anzahl an Wiederholungsversuchen

def ping_server(host):
    try:
        output = subprocess.run(['ping', '-c', '1', host], stdout=subprocess.DEVNULL)
        return output.returncode == 0
    except Exception as e:
        print(f"Fehler beim Pingen: {e}")
        return False

def start_main_script(script_path):
    # `sudo` hinzugefügt und den Pfad angepasst
    subprocess.Popen(['sudo', 'python', script_path])

def main():
    retries = 0
    while retries < MAX_RETRIES:
        if ping_server(SERVER_HOST):
            print("Server ist erreichbar. Hauptskript wird gestartet.")
            start_main_script(MAIN_SCRIPT_PATH)
            break
        else:
            print(f"Server nicht erreichbar. Versuche erneut in {CHECK_INTERVAL} Sekunden...")
            time.sleep(CHECK_INTERVAL)
            retries += 1

    if retries == MAX_RETRIES:
        print("Maximale Anzahl an Versuchen erreicht. Skript wird beendet.")

if __name__ == '__main__':
    main()
