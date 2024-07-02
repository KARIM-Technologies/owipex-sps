import struct
import serial
import crcmod.predefined

class ModbusClient:
    def __init__(self, device_manager, device_id):
        self.device_manager = device_manager
        self.device_id = device_id
        self.auto_read_enabled = False

    def read_register(self, start_address, register_count, data_format='>f'):
        return self.device_manager.read_register(self.device_id, start_address, register_count, data_format)

    def auto_read_registers(self, start_address, register_count, data_format='>f', interval=1):
        self.auto_read_enabled = True
        def read_loop():
            while self.auto_read_enabled:
                value = self.read_register(start_address, register_count, data_format)
                print(f'Auto Read: {value}')
                sleep(interval)
        Thread(target=read_loop).start()

    def stop_auto_read(self):
        self.auto_read_enabled = False

class DeviceManager:
    def __init__(self, port, baudrate, parity, stopbits, bytesize, timeout):
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            parity=serial.PARITY_NONE if parity == 'N' else serial.PARITY_EVEN if parity == 'E' else serial.PARITY_ODD,
            stopbits=serial.STOPBITS_ONE if stopbits == 1 else serial.STOPBITS_TWO,
            bytesize=serial.EIGHTBITS if bytesize == 8 else serial.SEVENBITS,
            timeout=timeout
        )
        self.devices = {}

    def add_device(self, device_id):
        self.devices[device_id] = ModbusClient(self, device_id)

    def get_device(self, device_id):
        return self.devices.get(device_id)

    def read_register(self, device_id, start_address, register_count, data_format):
        function_code = 0x03
        message = struct.pack('>B B H H', device_id, function_code, start_address, register_count)
        crc16_func = crcmod.predefined.mkPredefinedCrcFun('modbus')
        crc16 = crc16_func(message)
        message += struct.pack('<H', crc16)

        self.ser.write(message)
        expected_length = 5 + 2 * register_count  # Adjusted expected length
        response = self.ser.read(expected_length)

        print(f"Sent: {message.hex()}")
        print(f"Received: {response.hex()}")

        if len(response) < expected_length:
            print(f'Error: Response too short, received {len(response)} bytes, expected {expected_length}')
            return None

        if crc16_func(response[:-2]) != struct.unpack('<H', response[-2:])[0]:
            received_crc = struct.unpack('<H', response[-2:])[0]
            calculated_crc = crc16_func(response[:-2])
            print(f'CRC error: Expected 0x{calculated_crc:04x}, but got 0x{received_crc:04x}')
            return None

        data = response[3:-2]  # Remove address, function, and CRC
        try:
            return struct.unpack(data_format, data)[0]
        except struct.error as e:
            print(f"Error unpacking data: {e}")
            return None