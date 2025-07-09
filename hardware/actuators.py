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
                Actuator.serial_port.write(b'ALL_OFF\n')
                Actuator.serial_port.flush()
            except serial.serialutil.SerialException as e:
                print(f"[WARNING] Serial port not available: {e}")
                Actuator.serial_port = None
                Actuator.serial_available = False

    def set_valve(self, state):
        # state è "Aperta" o "Chiusa"
        print(f"[DEBUG] set_valve called for {self.name}: requested state='{state}', last state='{self.last_state}'")
        if state not in ("Aperta", "Chiusa"):
            return  # ignora stati non validi
        if not Actuator.serial_available:
            print(f"[DEBUG] Skipping valve control for {self.name} (no serial connection)")
            return
        if state == "Aperta" and self.last_state != "Aperta":
            cmd = f"CH{self.channel}\n".encode()
            Actuator.serial_port.write(cmd)
            Actuator.serial_port.flush()
            self.last_state = "Aperta"
        elif state == "Chiusa" and self.last_state != "Chiusa":
            cmd = f"CH{self.channel}\n".encode()
            Actuator.serial_port.write(cmd)
            Actuator.serial_port.flush()
            self.last_state = "Chiusa"

    def __repr__(self):
        return f"<Actuator name={self.name}, pin={self.channel}>"
