from .pinmap import BARREL_PINMAP

try:
    from w1thermsensor import W1ThermSensor, SensorNotReadyError, NoSensorFound
    IS_HARDWARE = True
except ImportError:
    IS_HARDWARE = False

import random

class Sensor:
    def __init__(self, barrel_name, serial=None):
        self.name = barrel_name
        self.pin = BARREL_PINMAP[barrel_name].get("sensor_pin", 4)  # default GPIO4
        self.serial = serial or BARREL_PINMAP[barrel_name].get("sensor_serial")
        self.sensor_obj = None
        if IS_HARDWARE:
            self.sensor_obj = self._find_sensor()
        # fallback: mock



    def _find_sensor(self):
        try:
            if self.serial:
                # Cerca la sonda con serial specifico
                return W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, self.serial)
            # Se nessun serial, prende la prima disponibile
            return W1ThermSensor()
        except Exception as e:
            print(f"[WARNING] DS18B20 non trovata per {self.name}: {e}")
            return None

    def read_temperature(self):
        if IS_HARDWARE and self.sensor_obj:
            try:
                temp = self.sensor_obj.get_temperature()
                return round(temp, 1)
            except SensorNotReadyError:
                print(f"[ERROR] Sonda {self.name} non pronta, uso mock.")
            except Exception as e:
                print(f"[ERROR] Errore lettura {self.name}: {e}")
        # MOCK per sviluppo
        return round(18 + random.uniform(-1.5, 1.5), 1)

    def __repr__(self):
        return f"<Sensor name={self.name}, pin={self.pin}, serial={self.serial}>"

# --- Utility per gestione gruppo sensori ---

def discover_all_ds18b20():
    """Ritorna lista di serial disponibili sul bus 1-wire."""
    if not IS_HARDWARE:
        return []
    try:
        return [s.id for s in W1ThermSensor.get_available_sensors()]
    except Exception:
        return []



class SensorManager:
    def __init__(self, mapping=None):
        """
        mapping: dict { nome_botte: serial_ds18b20 }
        Se non fornito, crea 'Botte1', 'Botte2', ... nell'ordine in cui trova i serial.
        """
        self.detected_serials = discover_all_ds18b20()
        if mapping is None:
            mapping = {f"Botte{i+1}": sid for i, sid in enumerate(self.detected_serials)}
        self.sensors = {name: Sensor(name, serial) for name, serial in mapping.items()}

    def read_all(self):
        """Ritorna dict {nome_botte: temperatura}"""
        return {name: sensor.read_temperature() for name, sensor in self.sensors.items()}

    def get_serials(self):
        """Ritorna dict {nome_botte: serial}"""
        return {name: sensor.serial for name, sensor in self.sensors.items()}

    def print_mapping(self):
        for name, sensor in self.sensors.items():
            print(f"{name}: serial={sensor.serial}")

    def rescan_serials(self):
        """Aggiorna la lista dei serial disponibili sul bus 1-Wire"""
        self.detected_serials = discover_all_ds18b20()
        print("DEBUG: Sensori trovati nel rescan:", self.detected_serials)
        return self.detected_serials

# --- Esempio standalone ---
if __name__ == "__main__":
    print("Serial DS18B20 rilevati:", discover_all_ds18b20())
    mgr = SensorManager()
    mgr.print_mapping()
    import time
    while True:
        print(mgr.read_all())
        time.sleep(2)
