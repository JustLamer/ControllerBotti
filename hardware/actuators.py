from .pinmap import BARREL_PINMAP
import requests

class Actuator:
    BASE_URL = "http://192.168.4.1"
    wifi_available = True

    def __init__(self, barrel_name):
        self.name = barrel_name
        self.channel = BARREL_PINMAP[barrel_name]["valve_pin"]  # 0–5
        self.last_state = "Chiusa"  # valore teorico, toggle non garantisce stato reale

    def set_valve(self, state):
        if state not in ("Aperta", "Chiusa"):
            return
        if not Actuator.wifi_available:
            print(f"[DEBUG] Skipping valve control for {self.name} (Wi-Fi not available)")
            return

        relay_number = self.channel + 1  # 1–6
        url = f"{Actuator.BASE_URL}/Switch{relay_number}"

        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print(f"[DEBUG] Toggled {self.name} → teoricamente {state}")
                self.last_state = state
            else:
                print(f"[WARNING] Failed to toggle {self.name} (HTTP {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"[WARNING] Wi-Fi request failed: {e}")
            Actuator.wifi_available = False

    def __repr__(self):
        return f"<Actuator name={self.name}, pin={self.channel}>"
