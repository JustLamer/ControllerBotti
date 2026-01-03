import os
import sys
import random
import re

USE_MOCK_SENSOR = (
    os.environ.get("USE_MOCK_SENSOR", "0") == "1" or
    "--mock" in sys.argv
)

if "--mock" in sys.argv:
    sys.argv.remove("--mock")  # optional, for clean CLI parsing later

FAKE_SENSOR_TEMPS = {
    "Fake_Thermo_18": 18.0,
    "Fake_Thermo_27": 27.0,
    "Fake_Thermo_32": 32.0,
}
DEFAULT_FAKE_TEMP = 18.0


def set_fake_sensor_temps(temp_map):
    if not isinstance(temp_map, dict):
        return
    FAKE_SENSOR_TEMPS.clear()
    for key, value in temp_map.items():
        try:
            FAKE_SENSOR_TEMPS[str(key)] = float(value)
        except (TypeError, ValueError):
            continue


def _parse_fake_temp(sensor_id):
    match = re.search(r"(\d+(?:\.\d+)?)$", sensor_id or "")
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None

try:
    if not USE_MOCK_SENSOR:
        from w1thermsensor import W1ThermSensor, SensorNotReadyError
        # Try to load once to verify kernel modules
        W1ThermSensor.get_available_sensors()
        IS_HARDWARE = True
    else:
        raise ImportError("Mocking forced via USE_MOCK_SENSOR")
except Exception as e:
    print(f"[INFO] Using mock sensors ({e})")
    IS_HARDWARE = False
    # Define dummy classes
    class W1ThermSensor:
        THERM_SENSOR_DS18B20 = "DS18B20"
        def __init__(self, sensor_type=THERM_SENSOR_DS18B20, sensor_id=None):
            self.id = sensor_id or f"28-{random.randint(100000, 999999)}"
            self._fake_temp = FAKE_SENSOR_TEMPS.get(self.id)
            if self._fake_temp is None:
                parsed_temp = _parse_fake_temp(self.id)
                if parsed_temp is not None:
                    self._fake_temp = parsed_temp
                else:
                    self._fake_temp = DEFAULT_FAKE_TEMP
        def get_temperature(self):
            return self._fake_temp
        @staticmethod
        def get_available_sensors():
            if FAKE_SENSOR_TEMPS:
                return [W1ThermSensor(sensor_id=sensor_id) for sensor_id in FAKE_SENSOR_TEMPS.keys()]
            return [
                W1ThermSensor(sensor_id="Fake_Thermo_18"),
                W1ThermSensor(sensor_id="Fake_Thermo_27"),
                W1ThermSensor(sensor_id="Fake_Thermo_32"),
            ]

    class SensorNotReadyError(Exception):
        pass


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
            #print(f"[WARNING] DS18B20 non trovata per {self.name}: {e}")
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
        if self.sensor_obj:
            return round(self.sensor_obj.get_temperature(), 1)
        return round(DEFAULT_FAKE_TEMP, 1)

    def __repr__(self):
        return f"<Sensor name={self.name}, serial={self.serial}>"


def discover_all_ds18b20():
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
        #print("DEBUG: Sensori trovati nel rescan:", self.detected_serials)
        return self.detected_serials

    def read_temperature_by_serial(self, serial):
        if serial == "test" or not serial:
            return round(DEFAULT_FAKE_TEMP, 1)

        try:
            sensor = W1ThermSensor(sensor_id=serial)
            return round(sensor.get_temperature(), 1)
        except Exception as e:
            #print(f"[ERROR] Errore lettura serial {serial}: {e}, uso mock.")
            return round(DEFAULT_FAKE_TEMP, 1)


if __name__ == "__main__":
    #print("Serial DS18B20 rilevati:", discover_all_ds18b20())
    mgr = SensorManager()
    mgr.print_mapping()
    import time
    while True:
        print(mgr.read_all())
        time.sleep(2)
