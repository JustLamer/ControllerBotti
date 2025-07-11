import sys
sys.path.append("/home/tritecc/controller")

import customtkinter as ctk
from PIL import Image
from gui.sidebar import Sidebar
from gui.overview import OverviewFrame
from gui.barrel_tab import BarrelTab
from config import load_config, save_config
from styles import setup_styles
from utils.logger import log_botte_csv
from hardware.sensors import SensorManager
from gui.settings_tab import SettingsTab
from hardware.actuators import Actuator

import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class ModernWineApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Controllo Botti - Modern UI")
        self.geometry("1200x800")
        self.minsize(300, 150)
        setup_styles(self)
        self.wm_attributes("-fullscreen", True)
        self.state("normal")

        # --- Dati/Config ---
        self.botti_data, self.settings = load_config()

        # Inizializza SensorManager prima della GUI
        user_mapping = self.settings.get("sensors_mapping", None)
        if user_mapping:
            self.sensor_manager = SensorManager(mapping=user_mapping)
        else:
            self.sensor_manager = SensorManager()

        import datetime
        for b in self.botti_data.values():
            now = datetime.datetime.now()
            if "history" not in b:
                b["history"] = [(now - datetime.timedelta(minutes=(19 - i) * 2), b["temperatura"]) for i in range(20)]
            if "valve_history" not in b:
                b["valve_history"] = []
            if "forced" not in b:
                b["forced"] = None
            if "valvola" not in b or b["valvola"] not in ("Aperta", "Chiusa"):
                b["valvola"] = "Chiusa"

        self.actuators = {nome: Actuator(nome) for nome in self.botti_data}
        # 1. Spegne tutti i relè fisici per partire da uno stato noto
        Actuator.all_off(use_rs485=True)

        # 2. Sincronizza lo stato locale con il modulo (tutti 'Chiusa' ora)
        Actuator.update_states(use_rs485=True)

        # 3. Crea gli actuator associati alle botti


        print("[DEBUG] Stato iniziale attuatori:", Actuator.relay_states)
        for nome, b in self.botti_data.items():
            print(f"[DEBUG] Stato desiderato botti {nome}: {b['valvola']}")

        # --- Icone ---
        gear_icon_path = os.path.join("assets", "gear.png")
        self.gear_img = ctk.CTkImage(light_image=Image.open(gear_icon_path), dark_image=Image.open(gear_icon_path), size=(44, 44))
        barrel_icon_path = os.path.join("assets", "barrel.png")
        self.barrel_img = ctk.CTkImage(light_image=Image.open(barrel_icon_path), dark_image=Image.open(barrel_icon_path), size=(48, 48))

        # --- Sidebar ---
        tab_list = [("Panoramica", self.barrel_img)] + [(nome, self.barrel_img) for nome in self.botti_data] + [("Impostazioni", self.gear_img)]
        self.sidebar = Sidebar(self, tab_list, self.switch_tab)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        # --- Main Area ---
        self.pages = {}
        self.pages["Panoramica"] = OverviewFrame(self, self)
        for nome in self.botti_data:
            self.pages[nome] = BarrelTab(self, self, nome)
        self.settings_tab = SettingsTab(self, self.sensor_manager, self.on_mapping_change)
        self.pages["Impostazioni"] = self.settings_tab

        self.current_tab = None
        self.switch_tab("Panoramica")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.after(2000, self.periodic_update)

    def on_mapping_change(self):
        save_config(self.botti_data, self.settings)

    def switch_tab(self, tab_name):
        if self.current_tab:
            self.pages[self.current_tab].grid_forget()
        self.pages[tab_name].grid(row=0, column=1, sticky="nsew", padx=28, pady=28)
        self.current_tab = tab_name
        self.sidebar.select(tab_name)
        if tab_name == "Impostazioni":
            self.settings_tab.refresh()

    def periodic_update(self):
        import random, datetime
        now = datetime.datetime.now()
        for nome, b in self.botti_data.items():
            b.setdefault("history", []).append((now, b["temperatura"]))
            b["history"] = b["history"][-100:]

            if b.get("forced", None) in ("Aperta", "Chiusa"):
                b["valvola"] = b["forced"]
            else:
                if b["temperatura"] > b["max_temp"]:
                    b["valvola"] = "Aperta"
                elif b["temperatura"] < b["min_temp"]:
                    b["valvola"] = "Chiusa"
                else:
                    if b.get("valvola") not in ("Aperta", "Chiusa"):
                        b["valvola"] = "Chiusa"

            b.setdefault("valve_history", []).append((now, b["valvola"]))
            b["valve_history"] = b["valve_history"][-100:]

            self.actuators[nome].set_valve(b["valvola"])

            log_botte_csv(
                nome_botte=nome,
                timestamp=now,
                temperatura=b["temperatura"],
                min_temp=b["min_temp"],
                max_temp=b["max_temp"],
                valvola=b["valvola"]
            )

        for page in self.pages.values():
            if hasattr(page, "refresh"):
                page.refresh()
        save_config(self.botti_data, self.settings)
        self.after(5000, self.periodic_update)

if __name__ == "__main__":
    ModernWineApp().mainloop()
