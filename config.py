import os
# Configuration details for h2oMain.py

# Thingsboard Server Configuration
ACCESS_TOKEN = os.environ.get('THINGSBOARD_ACCESS_TOKEN')
THINGSBOARD_SERVER = 'localhost' #Standardt IP Adresse EDGE Server
THINGSBOARD_PORT = 1883

# Machine Configuration
calculatedFlowRate = 1.0
powerButton = False
autoSwitch = False
callGpsSwitch = True
gpsEnabled = False  # GPS-Funktionalität standardmäßig deaktivieren
co2RelaisSw = False
pumpRelaySw = False
co2HeatingRelaySw = False
co2RelaisSwSig = False
pumpRelaySwSig = False
co2HeatingRelaySwSig = False
runtime_tracker_var = 0.0

# PH Configuration
minimumPHVal = 6.8
minimumPHValStop = 6.5
maximumPHVal = 7.8
ph_low_delay_duration = 180  # in sek
ph_high_delay_duration = 600  # in sek
ph_low_delay_start_time = None
ph_high_delay_start_time = None
PHValueOffset = 0.0
temperaturPHSens_telem = 0.0
measuredPHValue_telem = 0.0
gemessener_high_wert = 10.00
gemessener_low_wert = 7.00
calibratePH = False
targetPHValue = 7.50
targetPHtolerrance = 0.40
countdownPHHigh = None
countdownPHLow = None
ph_slope = 1.0
ph_intercept = 0.0

# Turbidity Configuration
measuredTurbidity = 0
maximumTurbidity = 0
turbiditySensorActive = False
turbidityOffset = 0
measuredTurbidity_telem = 0
tempTruebSens = 0.00

# Radar Configuration
waterLevelHeight = 1.0
waterLevelHeight_telem = 2.0
messuredRadar_Air_telem = 1 
radarSensorActive = False
radarSensorOffset = 0.0

# Radar Flow Configuration
flow_rate_l_min = 20.0
flow_rate_l_h = 20.0
flow_rate_m3_min = 20.0
total_flow = 0.0

# US Configuration
usSensorActive = False
usFlowRate = 0.0
usFlowTotal = 0.0

# GPS Configuration
gpsTimestamp = 1.0
gpsLatitude = 1.0
gpsLongitude = 1.0
gpsHeight = 1.0


# Telemetry and Attribute Variables
telemetry_keys = ['runtime_tracker_var','powerButton', 'autoSwitch', 'co2RelaisSw', 'co2HeatingRelaySw', 'pumpRelaySw', 'calculatedFlowRate', 'waterLevelHeight_telem', 'measuredTurbidity_telem',
                  'co2RelaisSwSig', 'co2HeatingRelaySwSig', 'pumpRelaySwSig', 'measuredPHValue_telem', 'temperaturPHSens_telem', 'gpsTimestamp', 'messuredRadar_Air_telem', 
                  'countdownPHHigh', 'countdownPHLow', 'flow_rate_l_min', 'flow_rate_l_h', 'flow_rate_m3_min', 'gpsLatitude', 'gpsLongitude', 'gpsHeight', 'ph_low_delay_start_time', 
                  'ph_high_delay_duration', 'minimumPHVal', 'maximumPHVal', 'tempTruebSens', 'calibratePH', 'total_flow', 'maximumTurbidity', 'turbiditySensorActive', 
                  'gpsEnabled', 'usSensorActive', 'usFlowRate', 'usFlowTotal']

attributes_keys = ['ip_address', 'macaddress']



# Lists for different groups of attributes
shared_attributes_keys = ['minimumPHValStop', 'ph_low_delay_start_time', 'ph_high_delay_duration', 
                          'PHValueOffset', 'maximumTurbidity', 'turbiditySensorActive', 
                          'turbidityOffset', 'radarSensorActive', 'usSensorActive', 'autoSwitch', 
                          'callGpsSwitch', 'powerButton', 'co2RelaisSwSig',
                          'calibratePH', 'targetPHValue', 'targetPHtolerrance', 'gemessener_high_wert',
                          'gemessener_low_wert', 'ph_slope', 'ph_intercept', 'maximumPHVal', 
                          'usSensorActive', 
                          'gpsEnabled']
