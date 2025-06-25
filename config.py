import os, json

CONFIG_PATH = "data/botti_config.json"
BARREL_IMAGE_PATH = "assets/barrel.png"

DEFAULT_BOTTI_DATA = {
    "Botte 1": {"temperatura": 18.5, "valvola": "Auto", "forced": None, "min_temp": 17.0, "max_temp": 20.0},
    "Botte 2": {"temperatura": 20.0, "valvola": "Auto", "forced": None, "min_temp": 18.0, "max_temp": 21.0},
    "Botte 3": {"temperatura": 19.2, "valvola": "Auto", "forced": None, "min_temp": 16.5, "max_temp": 19.5},
}
DEFAULT_SETTINGS = {"step_temp": 0.1}

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)
            botti_data = data.get("botti_data", DEFAULT_BOTTI_DATA.copy())
            settings = data.get("impostazioni", DEFAULT_SETTINGS.copy())
    else:
        botti_data = DEFAULT_BOTTI_DATA.copy()
        settings = DEFAULT_SETTINGS.copy()
    for k in botti_data:
        botti_data[k].setdefault('forced', None)
    settings = {**DEFAULT_SETTINGS, **settings}
    return botti_data, settings

def save_config(botti_data, settings):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump({"botti_data": botti_data, "impostazioni": settings}, f, indent=2)
