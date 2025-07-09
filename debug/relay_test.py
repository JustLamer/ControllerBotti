import minimalmodbus

# Configura il dispositivo
instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)  # ttyUSB0, ID Modbus = 1
instrument.serial.baudrate = 115200
instrument.serial.bytesize = 8
instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout = 2
instrument.debug = True

for addr in range(1, 11):
    print(f"Tentativo con ID {addr}...")
    instrument = minimalmodbus.Instrument('/dev/ttyUSB0', addr)
    instrument.serial.baudrate = 115200
    instrument.serial.bytesize = 8
    instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
    instrument.serial.stopbits = 1
    instrument.serial.timeout = 1
    instrument.clear_buffers_before_each_transaction = True

    try:
        instrument.write_bit(0, 1, functioncode=5)
        print(f"✅ Risposta ricevuta con ID {addr}")
        break
    except Exception as e:
        print(f"❌ Nessuna risposta con ID {addr}")
