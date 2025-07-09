import minimalmodbus
import serial
import time

PORT = '/dev/ttyUSB0'  # Cambia se usi /dev/ttyUSB1 o simili

baudrates = [115200, 9600, 19200, 38400]
modbus_ids = range(1, 11)
coil_address = 0  # Relè 1

print("🔍 Inizio scansione Modbus RTU...\n")

for baud in baudrates:
    print(f"\n🚀 Test con baudrate {baud}")
    for slave_id in modbus_ids:
        print(f"  🧪 Provo ID {slave_id}...", end=' ')
        try:
            instrument = minimalmodbus.Instrument(PORT, slave_id)
            instrument.serial.baudrate = baud
            instrument.serial.bytesize = 8
            instrument.serial.parity = serial.PARITY_NONE
            instrument.serial.stopbits = 1
            instrument.serial.timeout = 1
            instrument.clear_buffers_before_each_transaction = True

            # Prova a scrivere "True" nella coil 0 (accende relè 1)
            instrument.write_bit(coil_address, 1, functioncode=5)
            print("✅ Risposta ricevuta!")

            # Spegni relè 1 subito dopo
            time.sleep(0.5)
            instrument.write_bit(coil_address, 0, functioncode=5)
            print(f"   🔁 Relè 1 acceso e poi spento con ID {slave_id}, baud {baud}")
            exit(0)

        except Exception as e:
            print("❌ Nessuna risposta")

print("\n⛔ Nessun dispositivo trovato. Prova a invertire A/B o verificare alimentazione.")
