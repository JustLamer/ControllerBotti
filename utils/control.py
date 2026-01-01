import datetime
from utils.logger import log_botte_csv
from hardware.actuators import Actuator


def _safe_float(value, fallback):
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def update_botti_state(botti_data, settings, sensor_manager, actuators, test_mode=False):
    now = datetime.datetime.now()
    mapping = settings.get("sensors_mapping", {})
    min_switch_interval = int(_safe_float(settings.get("min_switch_interval_s", 60), 60))
    history_limit = 200
    state_changed = False

    for nome, b in botti_data.items():
        serial = mapping.get(nome) or "test"
        temp = sensor_manager.read_temperature_by_serial(serial)
        b["temperatura"] = temp
        if b["min_temp"] > b["max_temp"]:
            b["min_temp"], b["max_temp"] = b["max_temp"], b["min_temp"]
            state_changed = True

        b.setdefault("history", []).append((now, temp))
        b["history"] = b["history"][-history_limit:]

        current_valve = b.get("valvola", "Chiusa")
        forced = b.get("forced")

        if forced in ("Aperta", "Chiusa"):
            desired_valve = forced
        else:
            if temp > b["max_temp"]:
                desired_valve = "Aperta"
            elif temp < b["min_temp"]:
                desired_valve = "Chiusa"
            else:
                desired_valve = current_valve if current_valve in ("Aperta", "Chiusa") else "Chiusa"

        last_change = b.get("last_valve_change")
        if desired_valve != current_valve:
            if isinstance(last_change, datetime.datetime):
                elapsed = (now - last_change).total_seconds()
                if elapsed < min_switch_interval:
                    desired_valve = current_valve
            if desired_valve != current_valve:
                b["valvola"] = desired_valve
                b["last_valve_change"] = now
                state_changed = True

        b.setdefault("valve_history", []).append((now, b["valvola"]))
        b["valve_history"] = b["valve_history"][-history_limit:]

        log_botte_csv(
            nome_botte=nome,
            timestamp=now,
            temperatura=b["temperatura"],
            min_temp=b["min_temp"],
            max_temp=b["max_temp"],
            valvola=b["valvola"],
        )

    if not test_mode:
        state_dict = {nome: b["valvola"] for nome, b in botti_data.items()}
        Actuator.batch_set_valves(state_dict, actuators=actuators)

    return state_changed
