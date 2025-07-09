from .pinmap import BARREL_PINMAP
import requests

class Actuator:
    BASE_URL = "http://192.168.4.1"
    wifi_available = True
    relay_states = {}  # Stato locale: {channel: "Aperta"/"Chiusa"}
    relay_states_initialized = False
    def __init__(self, barrel_name):
        self.name = barrel_name
        self.channel = BARREL_PINMAP[barrel_name]["valve_pin"]  # 0–5
        self.last_state = "Chiusa"

    @staticmethod
    def update_states():
        try:
            r = requests.get(f"{Actuator.BASE_URL}/getData", timeout=2)
            if r.status_code == 200:
                raw = r.json()
                print(f"[DEBUG] Stato da /getData: {raw}")
                for i in range(min(len(raw), 6)):
                    Actuator.relay_states[i] = "Chiusa" if raw[i] == "0" else "Aperta"
            else:
                print(f"[WARNING] Errore lettura stato (HTTP {r.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"[WARNING] Fallita lettura stato: {e}")
            Actuator.wifi_available = False

    def get_current_state(self):
        if not Actuator.relay_states_initialized:
            Actuator.update_states()
            Actuator.relay_states_initialized = True
        return Actuator.relay_states.get(self.channel, "Unknown")

    def set_valve(self, state):
        if state not in ("Aperta", "Chiusa"):
            return
        if not Actuator.wifi_available:
            print(f"[DEBUG] Skipping {self.name} (Wi-Fi non disponibile)")
            return

        current = self.get_current_state()
        if current == state:
            print(f"[DEBUG] {self.name} è già in stato {state}, nessun comando.")
            return

        # Invia comando di toggle
        relay_number = self.channel + 1
        url = f"{Actuator.BASE_URL}/Switch{relay_number}"
        try:
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                print(f"[DEBUG] Toggle {self.name} inviato → {state}")
                self.last_state = state
                Actuator.relay_states[self.channel] = state  # ⬅️ Aggiorna localmente
            else:
                print(f"[WARNING] HTTP {r.status_code} per {self.name}")
        except requests.exceptions.RequestException as e:
            print(f"[WARNING] Richiesta fallita: {e}")
            Actuator.wifi_available = False

    def __repr__(self):
        return f"<Actuator name={self.name}, pin={self.channel}, state={self.get_current_state()}>"
