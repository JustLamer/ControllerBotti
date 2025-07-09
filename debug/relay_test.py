import minimalmodbus

# Configura il dispositivo
instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)  # ttyUSB0, ID Modbus = 1
instrument.serial.baudrate = 115200
instrument.serial.bytesize = 8
instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout = 2
instrument.debug = True

for baud in [115200, 9600, 19200, 38400]:
    print(f"Provo baudrate {baud}")
    instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
    instrument.serial.baudrate = baud
    instrument.serial.bytesize = 8
    instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
    instrument.serial.stopbits = 1
    instrument.serial.timeout = 1
    try:
        instrument.write_bit(0, 1, functioncode=5)
        print(f"✅ Funziona con baudrate {baud}")
        break
    except Exception:
        print(f"❌ Nessuna risposta con baudrate {baud}")
