import sys
sys.path.append('/home/owipex_adm/owipex-sps/libs')
CONFIG_PATH = "/etc/owipex/"

import signal
import logging.handlers
import time
import os
import json
import threading

from threading import Thread
from tb_gateway_mqtt import TBDeviceMqttClient

from time import sleep

ACCESS_TOKEN = "GMFmpDiHXqHg9djy96sO"
THINGSBOARD_SERVER = '165.22.26.107'  # Replace with your Thingsboard server address
THINGSBOARD_PORT = 1883

client = None

#Import Global vars
from config import *
shared_attributes_keys


 #that will be called when the value of our Shared Attribute changes
def attribute_callback(result, _):
    globals().update({key: result[key] for key in result if key in globals()})
    print(result)

# Callback function that will be called when an RPC request is received
def rpc_callback(id, request_body):
    print(request_body)
    method = request_body.get('method')
    if method == 'getTelemetry':
        attributes, telemetry = get_data()
        client.send_attributes(attributes)
        client.send_telemetry(telemetry)
    else:
        print('Unknown method: ' + method)

def sync_state(result, exception=None):
    global powerButton
    if exception is not None:
        print("Exception: " + str(exception))
    else:
        period = result.get('shared', {'powerButton': False})['powerButton']

def get_data():
    #cpu_usage = round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline().replace('', '').replace(',', '.')), 2)
    #ip_address = os.popen('''hostname -I''').readline().replace('', '').replace(',', '.')[:-1]
    #mac_address = os.popen('''cat /sys/class/net/*/address''').readline().replace('', '').replace(',', '.')
    #processes_count = os.popen('''ps -Al | grep -c bash''').readline().replace('', '').replace(',', '.')[:-1]
    #swap_memory_usage = os.popen("free -m | grep Swap | awk '{print ($3/$2)*100}'").readline().replace('', '').replace(',', '.')[:-1]
    #ram_usage = float(os.popen("free -m | grep Mem | awk '{print ($3/$2) * 100}'").readline().replace('', '').replace(',', '.')[:-1])
    #st = os.statvfs('/')
    #used = (st.f_blocks - st.f_bfree) * st.f_frsize
    #boot_time = os.popen('uptime -p').read()[:-1]
    #avg_load = (cpu_usage + ram_usage) / 2

    #attributes = {
    #    'ip_address': ip_address,
    #    'macaddress': mac_address
    #}
    telemetry = {key: globals()[key] for key in telemetry_keys if key in globals()}

    # Adding static data
    telemetry.update({
    #    'cpu_usage': cpu_usage,
    #    'processes_count': processes_count,
    #    'disk_usage': used,
    #    'RAM_usage': ram_usage,
    #    'swap_memory_usage': swap_memory_usage,
    #    'boot_time': boot_time,
    #    'avg_load': avg_load
    })
    
    #print(attributes, telemetry)
    return attributes, telemetry





def signal_handler(sig, frame):
    print('Shutting down gracefully...')
    print('Speichere Daten.')
    time.sleep(3)  # Das Skript wartet hier 2 Sekunden
    print('Shutting down now.')  # Diese Zeile wird nach 2 Sekunden ausgeführt
    exit(0)




# Vor der main-Funktion:
DATA_SEND_INTERVAL = 15  # Daten alle 60 Sekunden senden
last_send_time = time.time() - DATA_SEND_INTERVAL  # Stellt sicher, dass beim ersten Durchlauf Daten gesendet werden
        
def main():
    #def Global Variables for Main Funktion
    global powerSwitchRelais1, powerSwitchRelais2

    client = TBDeviceMqttClient(THINGSBOARD_SERVER, THINGSBOARD_PORT, ACCESS_TOKEN)
    client.connect()
    client.request_attributes(shared_keys=['powerButton', 'callGpsSwitch'])

    # Request shared attributes
    client.request_attributes(shared_keys=shared_attributes_keys, callback=attribute_callback)
    # Subscribe to individual attributes using the defined lists
    for attribute in shared_attributes_keys:
        client.subscribe_to_attribute(attribute, attribute_callback)
    client.set_server_side_rpc_request_handler(rpc_callback)



    last_send_time = time.time()

    while not client.stopped:
        attributes, telemetry = get_data()
        client.send_attributes(attributes)

        current_time = time.time()
        if current_time - last_send_time >= DATA_SEND_INTERVAL:
            # Aktualisiere den letzten Sendungszeitpunkt
            last_send_time = current_time
            client.send_telemetry(telemetry)

        
            time.sleep(2)

    
    
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    if ACCESS_TOKEN != "TEST_TOKEN":
        main()
    else:
        print("Please change the ACCESS_TOKEN variable to match your device access token and run the")

