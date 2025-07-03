from .pinmap import BARREL_PINMAP

class Actuator:
    serial_port = None  # variabile di classe per la connessione RS485

    def __init__(self, barrel_name):
        self.name = barrel_name
        self.channel = BARREL_PINMAP[barrel_name]["valve_pin"]  # usa valve_pin come numero canale
        if Actuator.serial_port is None:
            Actuator.serial_port = serial.Serial('/dev/ttyUSB0', baudrate=115200, timeout=1)
            # eventualmente inviare un comando iniziale per resettare lo stato relè
            Actuator.serial_port.write(b'ALL_OFF\n')
            Actuator.serial_port.flush()
        self.last_state = "Chiusa"  # inizialmente valvola chiusa (NC)

    def set_valve(self, state):
        # state è "Aperta" o "Chiusa"
        if state not in ("Aperta", "Chiusa"):
            return  # ignora stati non validi
        # Decidi se inviare comando in base al cambio di stato
        if state == "Aperta" and self.last_state != "Aperta":
            cmd = f"CH{self.channel}\n".encode()  # comando toggle per aprire
            Actuator.serial_port.write(cmd)
            Actuator.serial_port.flush()
            self.last_state = "Aperta"
        elif state == "Chiusa" and self.last_state != "Chiusa":
            cmd = f"CH{self.channel}\n".encode()  # comando toggle per chiudere
            Actuator.serial_port.write(cmd)
            Actuator.serial_port.flush()
            self.last_state = "Chiusa"
        # se lo stato è invariato, non inviare nulla (evita toggle indesiderati)

    def __repr__(self):
        return f"<Actuator name={self.name}, pin={self.pin}>"
