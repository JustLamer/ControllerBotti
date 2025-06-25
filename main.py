import tkinter as tk
from tkinter import ttk
from gui.overview import OverviewFrame
from gui.barrel_tab import BarrelTab
from config import load_config, save_config, BARREL_IMAGE_PATH, DEFAULT_BOTTI_DATA
from styles import setup_styles
from PIL import Image, ImageTk

class WineApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Controllo Botti - Livello 2")
        self.geometry("1280x900")
        self.configure(bg="#2E2E2E")
        setup_styles(self)
        self.botti_data, self.settings = load_config()
        self.storico = {k: [] for k in self.botti_data}
        self.valve_history = {k: [] for k in self.botti_data}

        # Carica immagine barile (unica istanza condivisa)
        self.barrel_img = ImageTk.PhotoImage(Image.open(BARREL_IMAGE_PATH).resize((200,200), Image.LANCZOS))

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill='both', expand=True)
        self.overview_frame = OverviewFrame(self.nb, self)
        self.nb.add(self.overview_frame, text="📊 Panoramica")
        self.tabs = {}
        for nome in self.botti_data:
            tab = BarrelTab(self.nb, self, nome)
            self.nb.add(tab, text=f"🪵 {nome}")
            self.tabs[nome] = tab

        self.update_all()

    def update_all(self):
        from gui.graph_utils import auto_valvola
        import datetime, random

        now = datetime.datetime.now()
        for nome in self.botti_data:
            temp = round(self.botti_data[nome]['temperatura'] + random.uniform(-0.2,0.2), 1)
            self.botti_data[nome]['temperatura'] = temp
            self.storico[nome].append((now, temp))
            if len(self.storico[nome]) > 1000:
                self.storico[nome] = self.storico[nome][-1000:]
            val = auto_valvola(self.botti_data, nome, temp)
            self.botti_data[nome]['valvola'] = val
            self.valve_history[nome].append((now, val))
            if len(self.valve_history[nome]) > 1000:
                self.valve_history[nome] = self.valve_history[nome][-1000:]
            self.tabs[nome].refresh()
        self.overview_frame.refresh()
        save_config(self.botti_data, self.settings)
        self.after(5000, self.update_all)

if __name__ == "__main__":
    app = WineApp()
    app.mainloop()
