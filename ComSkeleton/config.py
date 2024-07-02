import os
# Configuration details for h2oMain.py

# Thingsboard Server Configuration
ACCESS_TOKEN = "GMFmpDiHXqHg9djy96sO"
THINGSBOARD_SERVER = '165.22.26.107' #Standardt IP Adresse EDGE Server
THINGSBOARD_PORT = 1883

# Machine Configuration
powerButton = False
powerSwitchRelais1 = False
powerSwitchRelais2 = False



# Telemetry and Attribute Variables
#telemetry_keys = ['runtime_tracker_var', 'gpsHeight']

attributes_keys = ['ip_address', 'macaddress']

telemetry_keys = []

# Lists for different groups of attributes
shared_attributes_keys = ['powerSwitchRelais1', 'powerSwitchRelais2']
