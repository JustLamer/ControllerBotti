import os
import json
import datetime

# Qui puoi mettere i dati di default del tuo sistema
default_botti_data = {
    "Botte 1": {"temperatura": 18.5, "valvola": "Chiusa", "forced": None, "min_temp": 17.0, "max_temp": 20.0, "history": []},
    "Botte 2": {"temperatura": 20.0, "valvola": "Chiusa", "forced": None, "min_temp": 18.0, "max_temp": 21.0, "history": []},
    "Botte 3": {"temperatura": 19.2, "valvola": "Chiusa", "forced": None, "min_temp": 16.5, "max_temp": 19.5, "history": []},
}
default_settings = {"step_temp": 0.1}

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
    with open(CONFIG_PATH, "w") as f:
        json.dump({"botti_data": botti_data, "impostazioni": settings}, f, indent=2, default=default)

def load_config():
    if not os.path.exists(CONFIG_PATH):
        # Carica dati di default e crea history iniziale
        botti = {k: dict(v) for k, v in default_botti_data.items()}
        now = datetime.datetime.now()
        for b in botti.values():
            if not b.get("history"):
                # Inizializza 20 punti finti per la demo
                b["history"] = [(now - datetime.timedelta(minutes=(19-i)*2), b["temperatura"]) for i in range(20)]
        return botti, dict(default_settings)

    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)
        botti_data = data.get("botti_data", {})
        settings = data.get("impostazioni", {})
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
        return botti_data, settings
