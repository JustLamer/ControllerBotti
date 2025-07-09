from .pinmap import BARREL_PINMAP
import requests

class Actuator:
    BASE_URL = "http://192.168.4.1"
    wifi_available = True
    relay_states = {}  # Stato locale: {channel: "Aperta"/"Chiusa"}

    def __init__(self, barrel_name):
        self.name = barrel_name
        self.channel = BARREL_PINMAP[barrel_name]["valve_pin"]  # 0–5

    @staticmethod
    def update_states():
        try:
            r = requests.get(f"{Actuator.BASE_URL}/getData", timeout=2)
            if r.status_code == 200:
                raw = r.json()
                print(f"[DEBUG] Stato da /getData: {raw}")
                for i in range(min(len(raw), 6)):
                    stato_letto = "Aperta" if raw[i] == "1" else "Chiusa"
                    Actuator.relay_states[i] = stato_letto
            else:
                print(f"[WARNING] Errore lettura stato (HTTP {r.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"[WARNING] Fallita lettura stato: {e}")
            Actuator.wifi_available = False

    def get_current_state(self):
        stato = Actuator.relay_states.get(self.channel, "Unknown")
        print(f"[DEBUG] Stato attuale di {self.name} (canale {self.channel}): {stato}")
        return stato

    def set_valve(self, state):
        if state not in ("Aperta", "Chiusa"):
            print(f"[ERROR] Stato non valido: {state}")
            return

        if not Actuator.wifi_available:
            print(f"[DEBUG] Skipping {self.name} (Wi-Fi non disponibile)")
            return

        if self.channel not in Actuator.relay_states:
            print(f"[DEBUG] Stato relè per {self.name} non presente, forzo sync...")
            Actuator.update_states()

        current = self.get_current_state().strip()
        desired = state.strip()

        print(f"[DEBUG] Richiesta per {self.name}: voglio '{desired}', attualmente è '{current}'")
        print(f"[DEBUG] Confronto `{desired}` == `{current}` → {desired == current}")

        if desired == current:
            print(f"[DEBUG] {self.name} è già in stato {desired}, nessun comando.")
            return

        # Invia comando di toggle
        relay_number = self.channel + 1
        url = f"{Actuator.BASE_URL}/Switch{relay_number}"
        try:
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                print(f"[DEBUG] Toggle {self.name} (canale {relay_number}) inviato → nuovo stato atteso: {state}")
                Actuator.relay_states[self.channel] = state
            else:
                print(f"[WARNING] HTTP {r.status_code} per {self.name}")
        except requests.exceptions.RequestException as e:
            print(f"[WARNING] Richiesta fallita: {e}")
            Actuator.wifi_available = False

    def __repr__(self):
        return f"<Actuator name={self.name}, pin={self.channel}, state={self.get_current_state()}>"
