# History of owipex-sps Development

## 2024-12-19

### Version 2.26
- **Cache Management**: Implemented error counting system in DeviceManager
- **Cache Clearing**: After 5 failed attempts to read from a device/register, the cache is automatically cleared
- **Error Tracking**: Added `error_counts` dictionary to track failed attempts per device and register
- **Version Update**: Increased version number from 2.25 to 2.26

### Previous Changes
- **OutletFlap Device**: Added new device with Device-ID 0x05 and registers 0x0000-0x0004
- **Version Management**: Implemented ProgVers variable with format "x.xx"
- **Device Detection**: Improved and later removed unreliable device detection
- **Status Indicators**: Added green/red status symbols for sensor measurements
- **Code Formatting**: Removed consecutive empty lines throughout the project
- **Baudrate Management**: Standardized to 9600 baud for all devices
- **PH Sensor Issue**: Identified cache problem with removed sensors returning old values

## Technical Details

### Device Configuration
- **Radar Sensor**: Device-ID 0x01, Baudrate 9600
- **Turbidity Sensor**: Device-ID 0x02, Baudrate 9600  
- **PH Sensor**: Device-ID 0x03, Baudrate 9600 (removed physically)
- **OutletFlap**: Device-ID 0x05, Baudrate 9600

### Cache Management
- Cache is cleared after 5 consecutive failed read attempts
- Error counting is per device and register combination
- Successful reads reset the error counter
- Prevents display of stale data from disconnected sensors 