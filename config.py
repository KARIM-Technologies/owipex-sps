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

# Flow Configuration
flow_rate_l_min = 20.0
flow_rate_l_h = 20.0
flow_rate_m3_min = 20.0
total_flow = 0.0

# OutletFlap Configuration
outletFlapRemoteLocal = 0
outletFlapValvePosition = 0
outletFlapSetpoint = 0
outletFlapErrorCode = 0
outletFlapTest = 0

# OutletFlap Enhanced Configuration (FC11R-specific)
outletFlapCurrentPosition = 0.0       # Konvertierte aktuelle Position (%)
outletFlapSetpointPosition = 0.0      # Konvertierte Sollposition (%)
outletFlapRemoteMode = False          # Boolean: Remote-Modus aktiv
outletFlapLocalMode = True            # Boolean: Local-Modus aktiv
outletFlapHasError = False            # Boolean: Fehler vorhanden

# OutletFlap Command Variables (ThingsBoard controlled)
isOutletFlapActive = False            # Sub-control flag (subordinate to isOutletFlapEnabled)
outletFlapTargetPosition = 0          # Command: Zielposition setzen (0-100%)
outletFlapSetRemoteMode = False       # Command: auf Remote-Modus schalten
outletFlapSetLocalMode = False        # Command: auf Local-Modus schalten

# GPS Configuration
gpsTimestamp = 1.0
gpsLatitude = 1.0
gpsLongitude = 1.0
gpsHeight = 1.0

# REVIEW NOTE: Variables defined above but not included in any array:
# - ph_low_delay_duration: Could be added to shared_attributes_keys if ThingsBoard configuration needed
# - ph_high_delay_start_time: Internal runtime variable, should not be in arrays
# - measuredTurbidity: Possible deprecated (measuredTurbidity_telem exists), consider removal
# - waterLevelHeight: Possible deprecated (waterLevelHeight_telem exists), consider removal  
# - radarSensorOffset: Could be added to shared_attributes_keys if ThingsBoard configuration needed

# 🚨 CRITICAL INCONSISTENCY WARNING 🚨
# The following variables are defined BOTH in this file AND in h2o.py, creating dangerous conflicts:
#
# DUPLICATE DEFINITIONS (Same name, potentially different behavior):
# - gpsEnabled: Defined here AND in h2o.py (lines 704, 749) 
# - isOutletFlapActive: Defined here AND in h2o.py (line 15)
# - powerButton: Defined here AND in h2o.py (lines 688, 700, etc.)
# - autoSwitch: Defined here AND in h2o.py (lines 687, 700, etc.)
# - pumpRelaySw: Defined here AND in h2o.py (lines 700, 814, etc.)
# - co2RelaisSw: Defined here AND in h2o.py (lines 701, 815, etc.)
# - co2HeatingRelaySw: Defined here AND in h2o.py (lines 702, 816, etc.)
#
# VALUE CONFLICTS (Same name, DIFFERENT values):
# - minimumPHValStop: config.py=6.5 vs h2o.py=5 ⚠️ DIFFERENT VALUES!
#
# WHY THIS IS DANGEROUS:
# 1. ThingsBoard interface depends on variable names in telemetry_keys/shared_attributes_keys
# 2. These array names are IMMUTABLE (cannot be changed due to ThingsBoard integration)
# 3. Duplicate definitions create unpredictable behavior depending on import order
# 4. Value conflicts mean ThingsBoard sends one value but application uses another
# 5. Debugging becomes nearly impossible when values don't match expectations
#
# SOLUTION REQUIRED:
# - h2o.py should ONLY import these variables from config.py via "from config import *"
# - h2o.py should NOT define any variables that exist in telemetry_keys/shared_attributes_keys
# - config.py must be the SINGLE SOURCE OF TRUTH for all ThingsBoard-interfaced variables
# - Remove ALL duplicate definitions from h2o.py
# - Ensure h2o.py uses config.py values exclusively
#
# AFFECTED THINGSBOARD ARRAYS:
# telemetry_keys: gpsEnabled, powerButton, autoSwitch, pumpRelaySw, co2RelaisSw, co2HeatingRelaySw
# shared_attributes_keys: gpsEnabled, isOutletFlapActive, powerButton, autoSwitch, minimumPHValStop

# Telemetry and Attribute Variables
telemetry_keys = ['autoSwitch', 'calculatedFlowRate', 'calibratePH', 'co2HeatingRelaySw',
                  'co2HeatingRelaySwSig', 'co2RelaisSw', 'co2RelaisSwSig', 'countdownPHHigh',
                  'countdownPHLow', 'flow_rate_l_h', 'flow_rate_l_min', 'flow_rate_m3_min',
                  'gpsEnabled', 'gpsHeight', 'gpsLatitude', 'gpsLongitude',
                  'gpsTimestamp', 'maximumPHVal', 'maximumTurbidity', 'measuredPHValue_telem',
                  'measuredTurbidity_telem', 'messuredRadar_Air_telem', 'minimumPHVal', 'isOutletFlapActive',
                  'outletFlapCurrentPosition', 'outletFlapErrorCode', 'outletFlapHasError', 'outletFlapLocalMode',
                  'outletFlapRemoteLocal', 'outletFlapRemoteMode', 'outletFlapSetLocalMode', 'outletFlapSetpoint',
                  'outletFlapSetpointPosition', 'outletFlapSetRemoteMode', 'outletFlapTargetPosition', 'outletFlapTest',
                  'outletFlapValvePosition', 'ph_high_delay_duration', 'ph_low_delay_start_time',
                  'powerButton', 'pumpRelaySw', 'pumpRelaySwSig', 'runtime_tracker_var',
                  'tempTruebSens', 'temperaturPHSens_telem', 'total_flow', 'turbiditySensorActive',
                  'waterLevelHeight_telem']

attributes_keys = ['ip_address', 'macaddress']

# Lists for different groups of attributes
shared_attributes_keys = ['autoSwitch', 'calibratePH', 'callGpsSwitch', 'co2RelaisSwSig',
                          'gemessener_high_wert', 'gemessener_low_wert', 'gpsEnabled', 'isOutletFlapActive',
                          'maximumPHVal', 'maximumTurbidity', 'minimumPHVal', 'minimumPHValStop',
                          'outletFlapRemoteLocal', 'outletFlapSetLocalMode', 'outletFlapSetRemoteMode',
                          'outletFlapSetpoint', 'outletFlapTargetPosition', 'ph_high_delay_duration', 'ph_low_delay_start_time',
                          'ph_slope', 'ph_intercept', 'PHValueOffset', 'powerButton',
                          'radarSensorActive', 'targetPHtolerrance', 'targetPHValue', 'turbidityOffset',
                          'turbiditySensorActive']
