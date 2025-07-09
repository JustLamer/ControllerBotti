from .pinmap import BARREL_PINMAP
import serial
import serial.serialutil  # for SerialException

class Actuator:
    serial_port = None  # variabile di classe per la connessione RS485
    serial_available = True  # flag per sapere se la seriale è attiva

    def __init__(self, barrel_name):
        self.name = barrel_name
        self.channel = BARREL_PINMAP[barrel_name]["valve_pin"]  # usa valve_pin come numero canale
        self.last_state = "Chiusa"  # inizialmente valvola chiusa (NC)

        if Actuator.serial_port is None:
            try:
                Actuator.serial_port = serial.Serial('/dev/ttyUSB0', baudrate=115200, timeout=1)
                #Actuator.serial_port.write(b'ALL_OFF\n')
                Actuator.serial_port.flush()
            except serial.serialutil.SerialException as e:
                print(f"[WARNING] Serial port not available: {e}")
                Actuator.serial_port = None
                Actuator.serial_available = False

    def set_valve(self, state):
        if state not in ("Aperta", "Chiusa"):
            return
        if not Actuator.serial_available:
            print(f"[DEBUG] Skipping valve control for {self.name} (no serial connection)")
            return

        relay_address = self.channel  # int tra 0 e 5
        device_address = 0x06
        function_code = 0x05
        output_address = relay_address.to_bytes(2, byteorder='big')
        output_value = b'\xFF\x00' if state == "Aperta" else b'\x00\x00'
        message = bytes([device_address, function_code]) + output_address + output_value
        crc = Actuator.calculate_crc(message)
        full_message = message + crc

        print(f"[DEBUG] Comando in esadecimale: {full_message.hex()}")
        Actuator.serial_port.write(full_message)
        Actuator.serial_port.flush()
        self.last_state = state
        print(f"[DEBUG] Sent command to set {self.name} to {state}")

        resp = Actuator.serial_port.read(8)
        print(f"[DEBUG] Risposta relay: {resp.hex()}")

    @staticmethod
    def calculate_crc(data):
        crc = 0xFFFF
        for pos in data:
            crc ^= pos
            for _ in range(8):
                if (crc & 0x0001):
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc.to_bytes(2, byteorder='little')

    def __repr__(self):
        return f"<Actuator name={self.name}, pin={self.channel}>"



