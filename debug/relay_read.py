from pymodbus.client import ModbusSerialClient

class Relay6CHTest:
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200, slave_id=1):
        self.client = ModbusSerialClient(
            port=port,
            baudrate=baudrate,
            parity='N',
            stopbits=1,
            bytesize=8,
            timeout=1
        )
        self.slave_id = slave_id

    def connect(self):
        return self.client.connect()

    def read_coils(self, address=0, count=6):
        # pymodbus 3.x usa 'slave_id' come keyword
        result = self.client.read_coils(address, count, slave_id=self.slave_id)
        if not result.isError():
            return result.bits
        else:
            print("Errore nella lettura:", result)
            return None

    def close(self):
        self.client.close()

if __name__ == '__main__':
    relay_tester = Relay6CHTest(port='/dev/ttyUSB0')  # Cambia porta se serve
    if relay_tester.connect():
        states = relay_tester.read_coils()
        if states is not None:
            for i, state in enumerate(states, 1):
                print(f"Relay {i}: {'ON' if state else 'OFF'}")
        relay_tester.close()
    else:
        print("Impossibile connettersi al dispositivo Modbus!")
