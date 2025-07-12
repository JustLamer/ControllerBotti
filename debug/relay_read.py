from pymodbus.client import ModbusSerialClient

class Relay6CHTest:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, slave_id=1):
        self.client = ModbusSerialClient(
            method='rtu',
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
        """
        Legge lo stato dei relay (coil) dal modulo
        :param address: Indirizzo di partenza (di solito 0)
        :param count: Numero di coil da leggere (per 6 relè, count=6)
        :return: Lista di booleani con lo stato dei relay
        """
        result = self.client.read_coils(address, count, slave=self.slave_id)
        if not result.isError():
            return result.bits
        else:
            print("Errore nella lettura:", result)
            return None

    def close(self):
        self.client.close()


# --- Esempio d’uso ---
if __name__ == '__main__':
    relay_tester = Relay6CHTest(port='/dev/ttyUSB0')  # Cambia la porta se necessario
    if relay_tester.connect():
        states = relay_tester.read_coils()
        if states is not None:
            for i, state in enumerate(states, 1):
                print(f"Relay {i}: {'ON' if state else 'OFF'}")
        relay_tester.close()
    else:
        print("Impossibile connettersi al dispositivo Modbus!")
