import minimalmodbus

# Configura il dispositivo
instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)  # ttyUSB0, ID Modbus = 1
instrument.serial.baudrate = 115200
instrument.serial.bytesize = 8
instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout = 1

try:
    # Attiva il primo relè (coil 0)
    instrument.write_bit(0, 1, functioncode=5)
    print("Relay 1 acceso.")

    # Attendi un secondo, poi spegni
    import time
    time.sleep(1)

    instrument.write_bit(0, 0, functioncode=5)
    print("Relay 1 spento.")
except Exception as e:
    print("Errore:", e)
