import os
import random

try:
    from w1thermsensor import W1ThermSensor, SensorNotReadyError
    IS_HARDWARE = True
except ImportError:
    IS_HARDWARE = False


class Sensor:
    def __init__(self, barrel_name, serial=None):
        self.name = barrel_name
        self.pin = 4  # GPIO4 corrisponde fisicamente al pin 7 sul Raspberry Pi
        self.serial = serial
        self.sensor_obj = None

        if IS_HARDWARE:
            self.sensor_obj = self._find_sensor()

    def _find_sensor(self):
        try:
            if self.serial:
                return W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, self.serial)
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
        return round(18 + random.uniform(-1.5, 1.5), 1)

    def __repr__(self):
        return f"<Sensor name={self.name}, serial={self.serial}>"


# --- Funzione di rilevamento serial diretta ---
def discover_all_ds18b20():
    if not IS_HARDWARE:
        return []
    try:
        return [s.id for s in W1ThermSensor.get_available_sensors()]
    except Exception:
        # fallback diretto
        base_path = "/sys/bus/w1/devices/"
        try:
            entries = os.listdir(base_path)
            return [e for e in entries if e.startswith("28-")]
        except:
            return []


class SensorManager:
    def __init__(self, mapping=None):
        self.detected_serials = discover_all_ds18b20()
        if mapping is None:
            mapping = {f"Botte{i+1}": sid for i, sid in enumerate(self.detected_serials)}
        self.sensors = {name: Sensor(name, serial) for name, serial in mapping.items()}

    def read_all(self):
        return {name: sensor.read_temperature() for name, sensor in self.sensors.items()}

    def get_serials(self):
        return {name: sensor.serial for name, sensor in self.sensors.items()}

    def print_mapping(self):
        for name, sensor in self.sensors.items():
            print(f"{name}: serial={sensor.serial}")

    def rescan_serials(self):
        self.detected_serials = discover_all_ds18b20()
        print("DEBUG: Sensori trovati nel rescan:", self.detected_serials)
        return self.detected_serials

    def read_temperature_by_serial(self, serial):
        if serial == "test" or not serial:
            return round(18 + random.uniform(-1.5, 1.5), 1)

        try:
            sensor = W1ThermSensor(sensor_id=serial)
            return round(sensor.get_temperature(), 1)
        except Exception as e:
            print(f"[ERROR] Errore lettura serial {serial}: {e}, uso mock.")
            return round(18 + random.uniform(-1.5, 1.5), 1)



if __name__ == "__main__":
    print("Serial DS18B20 rilevati:", discover_all_ds18b20())
    mgr = SensorManager()
    mgr.print_mapping()
    import time
    while True:
        print(mgr.read_all())
        time.sleep(2)
