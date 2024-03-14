import logging.handlers
import time
import os
import paho.mqtt.client as mqtt  # Importiere die Paho-MQTT-Client-Bibliothek

from tb_gateway_mqtt import TBDeviceMqttClient

ACCESS_TOKEN = "RxtFfxeKosRFXNQPkk6O"
THINGSBOARD_SERVER = 'portal.owipex.io'
THINGSBOARD_PORT = 1883

# MQTT-Server für den anderen MQTT-Broker
MQTT_SERVER = "localhost"
MQTT_PORT = 1883
MQTT_USER = "admin"
MQTT_PASSWORD = "admin"

logging.basicConfig(level=logging.DEBUG)

client = None
mqtt_client = None  # Initialisiere den MQTT-Client für den anderen Server

# Initialwerte für die Schalter
switch1 = False
switch2 = False

# Callback-Funktion für Paho-MQTT, wenn die Verbindung erfolgreich ist
def on_connect(client, userdata, flags, rc):
    print("Verbunden mit MQTT-Server mit Result Code " + str(rc))

# Funktion zum Senden der MQTT-Nachrichten
def send_mqtt_message(topic, message):
    mqtt_client.publish(topic, message)

def attribute_callback(result, _):
    global switch1, switch2
    print(result)
    if 'switch1' in result:
        switch1 = result['switch1']
        # Sende den neuen Zustand von switch1 an das entsprechende MQTT-Topic
        send_mqtt_message("device/256/ap/5/download", "1" if switch1 else "0")
    if 'switch2' in result:
        switch2 = result['switch2']
        # Sende den neuen Zustand von switch2 an das entsprechende MQTT-Topic
        send_mqtt_message("device/259/ap/5/download", "1" if switch2 else "0")

# Callback-Funktion, die aufgerufen wird, wenn wir RPC senden
def rpc_callback(id, request_body):
    global switch1, switch2
    # Der Anfragekörper enthält Methode und andere Parameter
    print(request_body)
    method = request_body.get('method')
    if method == 'getTelemetry':
        attributes, telemetry = get_data()
        client.send_attributes(attributes)
        client.send_telemetry(telemetry)
    elif method == 'setSwitch1':
        switch1 = request_body.get('params', False)
        client.send_attributes({"switch1": switch1})
    elif method == 'setSwitch2':
        switch2 = request_body.get('params', False)
        client.send_attributes({"switch2": switch2})
    else:
        print('Unbekannte Methode: ' + method)


def get_data():
    cpu_usage = round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline().replace('\n', '').replace(',', '.')), 2)
    ip_address = os.popen('''hostname -I''').readline().replace('\n', '').replace(',', '.')[:-1]
    mac_address = os.popen('''cat /sys/class/net/*/address''').readline().replace('\n', '').replace(',', '.')
    processes_count = os.popen('''ps -Al | grep -c bash''').readline().replace('\n', '').replace(',', '.')[:-1]
    swap_memory_usage = os.popen("free -m | grep Swap | awk '{print ($3/$2)*100}'").readline().replace('\n', '').replace(',', '.')[:-1]
    ram_usage = float(os.popen("free -m | grep Mem | awk '{print ($3/$2) * 100}'").readline().replace('\n', '').replace(',', '.')[:-1])
    st = os.statvfs('/')
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    boot_time = os.popen('uptime -p').read()[:-1]
    avg_load = (cpu_usage + ram_usage) / 2
   
    attributes = {
        'ip_address': ip_address,
        'macaddress': mac_address
    }
    telemetry = {
        'cpu_usage': cpu_usage,
        'processes_count': processes_count,
        'disk_usage': used,
        'RAM_usage': ram_usage,
        'swap_memory_usage': swap_memory_usage,
        'boot_time': boot_time,
        'avg_load': avg_load
    }
    print(attributes, telemetry)
    return attributes, telemetry

# Anfrage Attribut Callback
def sync_state(result, exception=None):
    global switch1, switch2
    if exception is not None:
        print("Exception: " + str(exception))
    else:
        if 'switch1' in result:
            switch1 = result['switch1']
        if 'switch2' in result:
            switch2 = result['switch2']

def main():
    global client, mqtt_client
    client = TBDeviceMqttClient(THINGSBOARD_SERVER, THINGSBOARD_PORT, ACCESS_TOKEN)
    client.connect()
    client.request_attributes(shared_keys=['switch1', 'switch2'], callback=sync_state)
    
    sub_id_1 = client.subscribe_to_attribute("switch1", attribute_callback)
    sub_id_2 = client.subscribe_to_attribute("switch2", attribute_callback)

    client.set_server_side_rpc_request_handler(rpc_callback)

    # Initialisiere den MQTT-Client für den anderen Server
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)  # Setze Benutzernamen und Passwort
    mqtt_client.on_connect = on_connect  # Definiere den Callback für die Verbindung
    mqtt_client.connect(MQTT_SERVER, MQTT_PORT, 60)  # Verbinde mit dem MQTT-Server
    mqtt_client.loop_start()  # Starte den Netzwerk-Loop im Hintergrund

    while not client.stopped:
        attributes, telemetry = get_data()
        client.send_attributes(attributes)
        client.send_telemetry(telemetry)
        time.sleep(60)

if __name__ == '__main__':
    main()
