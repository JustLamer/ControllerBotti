import serial
import time

# Configura la porta seriale
ser = serial.Serial(
    port='/dev/ttyUSB0',      # Cambia se necessario
    baudrate=115200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1
)

def send_command(cmd):
    full_cmd = cmd + '\r\n'
    ser.write(full_cmd.encode())
    time.sleep(0.2)
    response = ser.read_all().decode(errors='ignore')
    return response

# Test: invia 'AT' e stampa la risposta
print("Invio comando: AT")
reply = send_command("AT")
print("Risposta ricevuta:")
print(reply or "[nessuna risposta]")

ser.close()
