import datetime
import sys
from pathlib import Path
import types

requests_stub = types.SimpleNamespace(
    get=lambda *args, **kwargs: types.SimpleNamespace(status_code=200),
    exceptions=types.SimpleNamespace(RequestException=Exception),
)
serial_stub = types.SimpleNamespace(
    Serial=lambda *args, **kwargs: None,
    EIGHTBITS=8,
    PARITY_NONE="N",
    STOPBITS_ONE=1,
)
sys.modules.setdefault("requests", requests_stub)
sys.modules.setdefault("serial", serial_stub)
sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.control import update_botti_state


class FakeSensorManager:
    def __init__(self, temps):
        self.temps = temps

    def read_temperature_by_serial(self, serial):
        return self.temps.get(serial, 18.0)


def _make_botte(min_temp=17.0, max_temp=20.0):
    return {
        "temperatura": 18.0,
        "valvola": "Chiusa",
        "forced": None,
        "min_temp": min_temp,
        "max_temp": max_temp,
        "history": [],
        "valve_history": [],
        "last_valve_change": datetime.datetime.now() - datetime.timedelta(seconds=120),
    }


def run_tests():
    botti_data = {
        "Botte 1": _make_botte(),
    }
    settings = {
        "min_switch_interval_s": 0,
        "update_interval_s": 5,
        "sensors_mapping": {"Botte 1": "Fake_Thermo_18"},
    }

    sensor_manager = FakeSensorManager({"Fake_Thermo_18": 22.0})
    update_botti_state(botti_data, settings, sensor_manager, actuators={}, test_mode=True)
    assert botti_data["Botte 1"]["valvola"] == "Aperta", "Valve should open when temp > max"

    sensor_manager.temps["Fake_Thermo_18"] = 15.0
    update_botti_state(botti_data, settings, sensor_manager, actuators={}, test_mode=True)
    assert botti_data["Botte 1"]["valvola"] == "Chiusa", "Valve should close when temp < min"

    botti_data["Botte 1"]["min_temp"] = 10.0
    botti_data["Botte 1"]["max_temp"] = 12.0
    sensor_manager.temps["Fake_Thermo_18"] = 11.0
    update_botti_state(botti_data, settings, sensor_manager, actuators={}, test_mode=True)
    assert botti_data["Botte 1"]["valvola"] == "Chiusa", "Valve should stay closed within new thresholds"

    botti_data["Botte 1"]["forced"] = "Aperta"
    update_botti_state(botti_data, settings, sensor_manager, actuators={}, test_mode=True)
    assert botti_data["Botte 1"]["valvola"] == "Aperta", "Valve should open when forced"

    botti_data["Botte 1"]["forced"] = "Chiusa"
    update_botti_state(botti_data, settings, sensor_manager, actuators={}, test_mode=True)
    assert botti_data["Botte 1"]["valvola"] == "Chiusa", "Valve should close when forced"


if __name__ == "__main__":
    run_tests()
    print("All valve logic tests passed.")
