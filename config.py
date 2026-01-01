import os
import json
import datetime

# Qui puoi mettere i dati di default del tuo sistema
default_botti_data = {
    "Botte 1": {"temperatura": 18.5, "valvola": "Chiusa", "forced": None, "min_temp": 17.0, "max_temp": 20.0, "history": []},
    "Botte 2": {"temperatura": 20.0, "valvola": "Chiusa", "forced": None, "min_temp": 18.0, "max_temp": 21.0, "history": []},
    "Botte 3": {"temperatura": 19.2, "valvola": "Chiusa", "forced": None, "min_temp": 16.5, "max_temp": 19.5, "history": []},
}
default_settings = {
    "step_temp": 0.1,
    "update_interval_s": 5,
    "min_switch_interval_s": 60,
    "save_interval_s": 30,
    "sensors_mapping": {},
}

CONFIG_PATH = "data/botti_config.json"

def save_config(botti_data, settings):
    # Serializza i datetime in stringa ISO solo per history!
    def default(obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    # (Crea la cartella se non esiste)
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

    # Serializza TUTTA la struttura dati con il default sopra
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({"botti_data": botti_data, "impostazioni": settings}, f, indent=2, default=default)

def _normalize_botti_data(botti_data):
    normalized = {}
    now = datetime.datetime.now()
    all_names = set(default_botti_data.keys()) | set(botti_data.keys())
    for name in sorted(all_names):
        defaults = default_botti_data.get(name, {"temperatura": 18.0, "min_temp": 17.0, "max_temp": 20.0})
        current = dict(defaults)
        current.update(botti_data.get(name, {}))
        current.setdefault("history", [])
        current.setdefault("valve_history", [])
        current.setdefault("forced", None)
        current.setdefault("valvola", "Chiusa")
        current.setdefault("last_valve_change", now)
        normalized[name] = current
    return normalized


def _normalize_settings(settings):
    normalized = dict(default_settings)
    normalized.update(settings or {})
    return normalized


def load_config():
    if not os.path.exists(CONFIG_PATH):
        # Carica dati di default e crea history iniziale
        botti = _normalize_botti_data({})
        now = datetime.datetime.now()
        for b in botti.values():
            if not b.get("history"):
                b["history"] = [(now - datetime.timedelta(minutes=(19 - i) * 2), b["temperatura"]) for i in range(20)]
        return botti, dict(default_settings)

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        botti_data = _normalize_botti_data(data.get("botti_data", {}))
        settings = _normalize_settings(data.get("impostazioni", {}))
        # Converti le history: stringhe --> datetime
        for b in botti_data.values():
            if "history" in b:
                new_history = []
                for t, v in b["history"]:
                    if isinstance(t, str):
                        try:
                            t = datetime.datetime.fromisoformat(t)
                        except Exception:
                            pass
                    new_history.append((t, v))
                b["history"] = new_history
            if "valve_history" in b:
                new_valve_history = []
                for t, v in b["valve_history"]:
                    if isinstance(t, str):
                        try:
                            t = datetime.datetime.fromisoformat(t)
                        except Exception:
                            pass
                    new_valve_history.append((t, v))
                b["valve_history"] = new_valve_history
            if isinstance(b.get("last_valve_change"), str):
                try:
                    b["last_valve_change"] = datetime.datetime.fromisoformat(b["last_valve_change"])
                except Exception:
                    b["last_valve_change"] = datetime.datetime.now()
        return botti_data, settings
