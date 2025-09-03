# commonvars.py
# Gemeinsame Variablen für h2o.py und modbus_lib.py

# Debug-Modus Variable
isDebugMode = False

# Setter-Funktion zum sicheren Ändern
def set_debug_mode(value) -> bool:
    global isDebugMode
    retValue = isDebugMode != value
    isDebugMode = value
    return retValue

# Getter-Funktion (optional)
def get_debug_mode():
    return isDebugMode