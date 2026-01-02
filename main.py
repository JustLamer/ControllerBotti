import sys
import os
sys.path.append("/home/tritecc/controller")

import customtkinter as ctk
from PIL import Image
from gui.sidebar import Sidebar
from gui.overview import OverviewFrame
from gui.barrel_tab import BarrelTab
from config import load_config, save_config
from styles import setup_styles
from hardware.sensors import SensorManager, set_fake_sensor_temps
from gui.settings_tab import SettingsTab
from hardware.actuators import Actuator
from utils.control import update_botti_state
from gui.theme import COLORS

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ModernWineApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Controllo Botti - Modern UI")
        self.geometry("1024x600")
        self.minsize(800, 480)
        setup_styles(self)
        self.wm_attributes("-fullscreen", True)
        self.state("normal")
        self.configure(fg_color=COLORS["bg"])

        # --- Dati/Config ---
        self.botti_data, self.settings = load_config()
        self.test_mode = False
        self.update_counter = 0

        set_fake_sensor_temps(self.settings.get("fake_sensor_temps", {}))

        # Inizializza SensorManager prima della GUI
        user_mapping = self.settings.get("sensors_mapping", None)
        if user_mapping:
            self.sensor_manager = SensorManager(mapping=user_mapping)
        else:
            self.sensor_manager = SensorManager()

        use_rs485 = os.name != "nt" and os.environ.get("USE_RS485", "1") == "1"
        self.actuators = {nome: Actuator(nome, use_rs485=use_rs485) for nome in self.botti_data}
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
        self.settings_tab = SettingsTab(
            self,
            self.sensor_manager,
            self.actuators,
            self.on_mapping_change,
            self.on_test_mode_change,
        )
        self.pages["Impostazioni"] = self.settings_tab

        self.current_tab = None
        self.switch_tab("Panoramica")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.after(2000, self.periodic_update)

    def on_mapping_change(self):
        save_config(self.botti_data, self.settings)

    def on_test_mode_change(self, enabled):
        self.test_mode = enabled

    def switch_tab(self, tab_name):
        if self.current_tab:
            self.pages[self.current_tab].grid_forget()
        self.pages[tab_name].grid(row=0, column=1, sticky="nsew", padx=18, pady=18)
        self.current_tab = tab_name
        self.sidebar.select(tab_name)
        if tab_name == "Impostazioni":
            self.settings_tab.refresh()

    def periodic_update(self):
        state_changed = update_botti_state(
            self.botti_data,
            self.settings,
            self.sensor_manager,
            self.actuators,
            test_mode=self.test_mode,
        )

        for page in self.pages.values():
            if hasattr(page, "refresh"):
                page.refresh()
        self.update_counter += 1
        save_interval = int(self.settings.get("save_interval_s", 30))
        if self.last_save is None or (self.update_counter * self.settings.get("update_interval_s", 5)) >= save_interval:
            save_config(self.botti_data, self.settings)
            self.update_counter = 0
        if state_changed:
            save_config(self.botti_data, self.settings)

        next_interval_ms = int(self.settings.get("update_interval_s", 5) * 1000)
        self.after(next_interval_ms, self.periodic_update)

if __name__ == "__main__":
    ModernWineApp().mainloop()
