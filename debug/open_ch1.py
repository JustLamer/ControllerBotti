import serial
import time

# Apri la porta seriale RS485
ser = serial.Serial(
    port='/dev/ttyUSB0',  # cambia se necessario
    baudrate=115200,
    bytesize=8,
    parity=serial.PARITY_NONE,
    stopbits=1,
    timeout=1
)

# Comando per toggle CH1 (da tua tabella)
command = bytes.fromhex('06 05 00 FF FF 00 BD BD')

# Invia il comando
ser.write(command)
print("Comando inviato: toggle CH1")

# Aspetta la risposta (se c'è)
response = ser.read(8)
print("Risposta ricevuta:", response.hex() or "[nessuna risposta]")

ser.close()
