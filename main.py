import customtkinter as ctk
from PIL import Image
from gui.sidebar import Sidebar
from gui.overview import OverviewFrame
from gui.barrel_tab import BarrelTab
from config import load_config, save_config
from styles import setup_styles
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class ModernWineApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Controllo Botti - Modern UI")
        self.geometry("1200x800")
        self.minsize(950, 600)
        setup_styles(self)

        # --- Dati/Config ---
        self.botti_data, self.settings = load_config()
        import datetime
        # Inizializza history se non presente
        for b in self.botti_data.values():
            if "history" not in b:
                now = datetime.datetime.now()
                b["history"] = [(now - datetime.timedelta(minutes=(19-i)*2), b["temperatura"]) for i in range(20)]
            if "forced" not in b:
                b["forced"] = None
            if "valvola" not in b or b["valvola"] not in ("Aperta", "Chiusa"):
                b["valvola"] = "Chiusa"

        # --- Icone ---
        barrel_icon_path = os.path.join("assets", "barrel.png")
        self.barrel_img = ctk.CTkImage(light_image=Image.open(barrel_icon_path),
                                       dark_image=Image.open(barrel_icon_path),
                                       size=(48, 48))
        # --- Sidebar ---
        tab_list = [("Panoramica", self.barrel_img)] + [
            (nome, self.barrel_img) for nome in self.botti_data
        ]
        self.sidebar = Sidebar(self, tab_list, self.switch_tab)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        # --- Main Area ---
        self.pages = {}
        self.pages["Panoramica"] = OverviewFrame(self, self)
        for nome in self.botti_data:
            self.pages[nome] = BarrelTab(self, self, nome)
        self.current_tab = None
        self.switch_tab("Panoramica")

        # Layout responsive
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Loop di aggiornamento dati periodico
        self.after(2000, self.periodic_update)

    def switch_tab(self, tab_name):
        if self.current_tab:
            self.pages[self.current_tab].grid_forget()
        self.pages[tab_name].grid(row=0, column=1, sticky="nsew", padx=28, pady=28)
        self.current_tab = tab_name
        self.sidebar.select(tab_name)

    def periodic_update(self):
        import random, datetime
        for nome, b in self.botti_data.items():
            # Simulazione aggiornamento storico e temperatura
            nuova_temp = round(b["temperatura"] + random.uniform(-0.2, 0.2), 1)
            b["temperatura"] = nuova_temp
            now = datetime.datetime.now()
            b["history"].append((now, nuova_temp))
            b["history"] = b["history"][-50:]  # Tieni ultimi 50 punti
            # Logica valvola con isteresi/forzatura (mai 'Auto')
            if b.get("forced", None) in ("Aperta", "Chiusa"):
                b["valvola"] = b["forced"]
            else:
                if b["temperatura"] > b["max_temp"]:
                    b["valvola"] = "Aperta"
                elif b["temperatura"] < b["min_temp"]:
                    b["valvola"] = "Chiusa"
                else:
                    if b.get("valvola") not in ("Aperta", "Chiusa"):
                        b["valvola"] = "Chiusa"  # Default
        # Aggiorna UI
        for page in self.pages.values():
            if hasattr(page, "refresh"):
                page.refresh()
        save_config(self.botti_data, self.settings)
        self.after(5000, self.periodic_update)

if __name__ == "__main__":
    ModernWineApp().mainloop()
