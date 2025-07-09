from .pinmap import BARREL_PINMAP
import requests

class Actuator:
    BASE_URL = "http://192.168.4.1"
    wifi_available = True

    def __init__(self, barrel_name):
        self.name = barrel_name
        self.channel = BARREL_PINMAP[barrel_name]["valve_pin"]  # 0–5 → usati come 1–6
        self.last_state = "Chiusa"

    def set_valve(self, state):
        if state not in ("Aperta", "Chiusa"):
            return
        if not Actuator.wifi_available:
            print(f"[DEBUG] Skipping valve control for {self.name} (Wi-Fi not available)")
            return

        relay_channel = self.channel + 1  # converti da 0–5 a 1–6
        relay_state = 1 if state == "Aperta" else 0

        url = f"{Actuator.BASE_URL}/relay?ch={relay_channel}&on={relay_state}"

        print(f"[DEBUG] Sending request: {url}")
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print(f"[DEBUG] Set {self.name} to {state} → OK")
                self.last_state = state
            else:
                print(f"[WARNING] Failed to set {self.name} (HTTP {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"[WARNING] Wi-Fi communication failed: {e}")
            Actuator.wifi_available = False

    def __repr__(self):
        return f"<Actuator name={self.name}, pin={self.channel}>"
