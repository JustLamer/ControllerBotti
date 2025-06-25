from .pinmap import BARREL_PINMAP

try:
    from w1thermsensor import W1ThermSensor, SensorNotReadyError
    IS_HARDWARE = True
except ImportError:
    IS_HARDWARE = False

import random

class Sensor:
    def __init__(self, barrel_name):
        self.name = barrel_name
        self.pin = BARREL_PINMAP[barrel_name]["sensor_pin"]
        self.sensor_obj = None
        if IS_HARDWARE:
            # Cerca la sonda col pin assegnato (se hai più sonde, usa il serial)
            self.sensor_obj = self._find_sensor()
        # Altrimenti mock

    def _find_sensor(self):
        """
        Se hai solo una sonda, la prende direttamente.
        Se hai più sonde, usa il campo 'serial' in BARREL_PINMAP.
        """
        try:
            # Ricerca per serial se specificato
            serial = BARREL_PINMAP[self.name].get("sensor_serial")
            if serial:
                return W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, serial)
            # Altrimenti prende la prima disponibile
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
                print(f"[ERROR] Sonda {self.name} non pronta, uso ultimo valore o mock.")
            except Exception as e:
                print(f"[ERROR] Errore lettura {self.name}: {e}")
        # MOCK di fallback (sviluppo/test)
        return round(18 + random.uniform(-1.5, 1.5), 1)

    def __repr__(self):
        return f"<Sensor name={self.name}, pin={self.pin}>"
