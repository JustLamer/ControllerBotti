from .pinmap import BARREL_PINMAP
import requests

class Actuator:
    BASE_URL = "http://192.168.4.1"
    wifi_available = True
    relay_states = None  # Stato cache da /getData

    def __init__(self, barrel_name):
        self.name = barrel_name
        self.channel = BARREL_PINMAP[barrel_name]["valve_pin"]  # 0–5
        self.last_state = "Unknown"

    @classmethod
    def update_states(cls):
        try:
            r = requests.get(f"{cls.BASE_URL}/getData", timeout=2)
            if r.status_code == 200:
                cls.relay_states = r.json()
                print(f"[DEBUG] Stato attuale relè: {cls.relay_states}")
            else:
                print(f"[WARNING] Errore lettura stato relè (HTTP {r.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"[WARNING] Fallita lettura stato: {e}")
            cls.relay_states = None
            cls.wifi_available = False

    def get_current_state(self):
        if Actuator.relay_states is None:
            Actuator.update_states()
        if Actuator.relay_states:
            raw = Actuator.relay_states[self.channel]
            return "Aperta" if raw == "1" else "Chiusa"
        return "Unknown"

    def set_valve(self, state):
        if state not in ("Aperta", "Chiusa"):
            return
        if not Actuator.wifi_available:
            print(f"[DEBUG] Skipping {self.name} (Wi-Fi non disponibile)")
            return

        current = self.get_current_state()
        if current == state:
            print(f"[DEBUG] {self.name} è già in stato {state}, nessun comando inviato.")
            return

        relay_number = self.channel + 1
        url = f"{Actuator.BASE_URL}/Switch{relay_number}"

        try:
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                print(f"[DEBUG] Toggled {self.name} → {state}")
                self.last_state = state
                Actuator.update_states()  # aggiorna lo stato globale
            else:
                print(f"[WARNING] Errore HTTP per {self.name} (HTTP {r.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"[WARNING] Richiesta fallita: {e}")
            Actuator.wifi_available = False

    def __repr__(self):
        return f"<Actuator name={self.name}, pin={self.channel}>"
