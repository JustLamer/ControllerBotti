from .pinmap import BARREL_PINMAP

class Actuator:
    def __init__(self, barrel_name):
        self.name = barrel_name
        self.pin = BARREL_PINMAP[barrel_name]["valve_pin"]
        # in futuro: qui puoi settare il pin come output con RPi.GPIO

    def set_valve(self, state):
        # MOCK per ora
        print(f"[DEBUG] Setto la valvola '{self.name}' su pin {self.pin} a stato {state}")
        # in futuro: GPIO.output(self.pin, state == 'Aperta')
        # aggiungi anche sicurezza per evitare scritture errate

    def __repr__(self):
        return f"<Actuator name={self.name}, pin={self.pin}>"
