import os
# Configuration details for h2oMain.py

# Thingsboard Server Configuration
ACCESS_TOKEN = os.environ.get('THINGSBOARD_ACCESS_TOKEN')
THINGSBOARD_SERVER = 'localhost' #Standardt IP Adresse EDGE Server
THINGSBOARD_PORT = 1883

# Machine Configuration
autoSwitch = False
calculatedFlowRate = 1.0
callGpsSwitch = True
co2HeatingRelaySw = False
co2HeatingRelaySwSig = False
co2RelaisSw = False
co2RelaisSwSig = False
gpsEnabled = False  # GPS-Funktionalität standardmäßig deaktivieren
isDebugMode = False
powerButton = False
pumpRelaySw = False
pumpRelaySwSig = False
runtime_tracker_var = 0.0
useDebugReadingsIntervalls = False

# PH Configuration
calibratePH = False
countdownPHHigh = None
countdownPHLow = None
gemessener_high_wert = 10.00
gemessener_low_wert = 7.00
maximumPHVal = 7.8
measuredPHValue_telem = 0.0
minimumPHVal = 6.8
minimumPHValStop = 6.5
ph_high_delay_duration = 600  # in sek
ph_high_delay_start_time = None
ph_intercept = 0.0
ph_low_delay_duration = 180  # in sek
ph_low_delay_start_time = None
ph_slope = 1.0
PHValueOffset = 0.0
targetPHtolerrance = 0.40
targetPHValue = 7.50
temperaturPHSens_telem = 0.0

# Turbidity Configuration
maximumTurbidity = 0
measuredTurbidity_telem = 0
measuredTurbidityNormalized_telem = 0
tempTruebSens = 0.00
turbidityOffset = 0
turbiditySensorActive = False
turbidityNormalizer = 1.00

# Turbidity2 Configuration
maximumTurbidity2 = 0
measuredTurbidity2_telem = 0
measuredTurbidity2Normalized_telem = 0
tempTruebSens2 = 0.00
turbidity2Offset = 0
turbidity2SensorActive = False
turbidity2Normalizer = 1.00

# Radar Configuration
messuredRadar_Air_telem = 1
radar_1_actual_water_level = 0
radarSensorActive = False
radarSensorOffset = 0.0
waterLevelHeight_telem = 2.0

# Radar Flow Configuration
flow_rate_l_h = 20.0
flow_rate_l_min = 20.0
flow_rate_m3_min = 20.0
total_flow = 0.0

# US Configuration 
usFlowRate = 0.0
usFlowTotal = 0.0
usSensorActive = False

# US2 Configuration
us2FlowRate = 0.0
us2FlowTotal = 0.0
usSensor2Active = False

# US3 Configuration
us3FlowRate = 0.0
us3FlowTotal = 0.0
usSensor3Active = False

# OutletFlap Configuration
outletFlapRegisterErrorCode = 0
outletFlapRegisterPositionValue = 0
outletFlapRegisterRemoteOrLocalStatus = 0
outletFlapRegisterSetpointValue = 0
telemetryTest420 = 420

# OutletFlap Enhanced Configuration (FC11R-specific)
outletFlapRegisterCurrentPosition = 0.0       # Konvertierte aktuelle Position (%)
outletFlapRegisterHasError = False            # Boolean: Fehler vorhanden
outletFlapRegisterIsLocalMode = False            # Boolean: Local-Modus aktiv
outletFlapRegisterIsRemoteMode = False          # Boolean: Remote-Modus aktiv
outletFlapRegisterSetpointPosition = 0.0      # Konvertierte Sollposition (%)

# OutletFlap Turb Control
outletFlapTurbControlActive = False
outletFlapTurbControlCurrentTurbValue = 0.0

# Telemetry Test Values
telemetryTestNone = None              # Python None value

# OutletFlap Command Variables (ThingsBoard controlled)
outletFlapActive = False            # Sub-control flag (subordinate to isOutletFlapEnabled)
outletFlapIsRemoteMode = True        # Command: Remote/Local Modus setzen (True=Remote, False=Local)
outletFlapTargetPosition = 0          # Command: Zielposition setzen (0-100%)

# GPS Configuration
gpsHeight = 1.0
gpsLatitude = 1.0
gpsLongitude = 1.0
gpsTimestamp = 1.0

# Telemetry and Attribute Variables
telemetry_keys = [
    'autoSwitch',
    'calculatedFlowRate', 'calibratePH', 'callGpsSwitch', 'co2HeatingRelaySw',
    'co2HeatingRelaySwSig', 'co2RelaisSw', 'co2RelaisSwSig', 'countdownPHHigh',
    'countdownPHLow',
    'flow_rate_l_h', 'flow_rate_l_min', 'flow_rate_m3_min',
    'gemessener_high_wert', 'gemessener_low_wert', 'gpsEnabled', 'gpsHeight',
    'gpsLatitude', 'gpsLongitude', 'gpsTimestamp',
    'isDebugMode',
    'maximumPHVal', 'maximumTurbidity', 'maximumTurbidity2', 'measuredPHValue_telem',
    'measuredTurbidity_telem', 'measuredTurbidity2_telem', 'measuredTurbidity2Normalized_telem', 'measuredTurbidityNormalized_telem',
    'messuredRadar_Air_telem', 'minimumPHVal', 'minimumPHValStop',
    'outletFlapActive', 'outletFlapIsRemoteMode', 'outletFlapRegisterCurrentPosition', 'outletFlapRegisterErrorCode',
    'outletFlapRegisterHasError', 'outletFlapRegisterIsLocalMode', 'outletFlapRegisterIsRemoteMode', 'outletFlapRegisterPositionValue',
    'outletFlapRegisterRemoteOrLocalStatus', 'outletFlapRegisterSetpointPosition', 'outletFlapRegisterSetpointValue', 'outletFlapTargetPosition',
    'outletFlapTurbControlActive', 'outletFlapTurbControlCurrentTurbValue',
    # 'outletFlapTurbControlActiveTelem', 'outletFlapTurbControlCurrentTurbValueTelem',
    'ph_high_delay_duration', 'ph_intercept', 'ph_low_delay_start_time', 'ph_slope',
    'PHValueOffset', 'powerButton', 'pumpRelaySw', 'pumpRelaySwSig',
    'radar_1_actual_water_level', 'radarSensorActive', 'runtime_tracker_var',
    'targetPHtolerrance', 'targetPHValue', 'telemetryTest420', 'telemetryTestNone',
    'temperaturPHSens_telem', 'tempTruebSens', 'tempTruebSens2', 'total_flow',
    'turbidity2Normalizer', 'turbidity2Offset', 'turbidity2SensorActive', 'turbidityNormalizer',
    'turbidityOffset', 'turbiditySensorActive',
    'us2FlowRate', 'us2FlowTotal', 'us3FlowRate', 'us3FlowTotal',
    'useDebugReadingsIntervalls', 'usFlowRate', 'usFlowTotal', 'usSensor2Active',
    'usSensor3Active', 'usSensorActive',
    'waterLevelHeight_telem'
]

attributes_keys = ['ip_address', 'macaddress']

# Lists for different groups of attributes
shared_attributes_keys = [
    'autoSwitch',
    'calibratePH', 'callGpsSwitch', 'co2RelaisSwSig',
    'gemessener_high_wert', 'gemessener_low_wert', 'gpsEnabled',
    'isDebugMode',
    'maximumPHVal', 'maximumTurbidity', 'maximumTurbidity2', 'minimumPHVal',
    'minimumPHValStop',
    'outletFlapActive', 'outletFlapIsRemoteMode', 'outletFlapTargetPosition',
    'outletFlapTurbControlActive', 'outletFlapTurbControlCurrentTurbValue',
    'ph_high_delay_duration', 'ph_intercept', 'ph_low_delay_start_time', 'ph_slope',
    'PHValueOffset', 'powerButton',
    'radarSensorActive',
    'targetPHtolerrance', 'targetPHValue', 'turbidity2Normalizer', 'turbidity2Offset',
    'turbidity2SensorActive', 'turbidityNormalizer', 'turbidityOffset', 'turbiditySensorActive',
    'useDebugReadingsIntervalls', 'usSensor2Active', 'usSensor3Active', 'usSensorActive'
]
