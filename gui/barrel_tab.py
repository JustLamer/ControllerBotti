import customtkinter as ctk
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
from config import save_config

DELTA_MAP = {
    "Tutto": None,
    "Ultimi 5 min": datetime.timedelta(minutes=5),
    "Ultimi 15 min": datetime.timedelta(minutes=15),
    "Ultime 2 ore": datetime.timedelta(hours=2),
    "Ultime 6 ore": datetime.timedelta(hours=6),
    "Ultime 24 ore": datetime.timedelta(hours=24),
    "Ultima settimana": datetime.timedelta(days=7),
}

class BarrelTab(ctk.CTkFrame):
    def __init__(self, master, app, nome, **kwargs):
        super().__init__(master, corner_radius=18, fg_color="#223118", **kwargs)
        self.app = app
        self.nome = nome

        self.grid_columnconfigure(1, weight=1)

        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsw", padx=8, pady=10)

        ctk.CTkLabel(left, text=nome, font=ctk.CTkFont(size=25, weight="bold")).pack(pady=(18, 10))
        self.dot_lbl = ctk.CTkLabel(left, text="●", font=ctk.CTkFont(size=38), text_color="#6ddb57")
        self.dot_lbl.pack()
        self.temp_lbl = ctk.CTkLabel(left, text="", font=ctk.CTkFont(size=27, weight="bold"))
        self.temp_lbl.pack(pady=7)
        self.valve_lbl = ctk.CTkLabel(left, text="", font=ctk.CTkFont(size=22))
        self.valve_lbl.pack(pady=7)

        img_lock = Image.open("assets/lock.png").resize((32, 32))
        self.lock_icon = ctk.CTkImage(light_image=img_lock, dark_image=img_lock)
        self.lock_lbl = ctk.CTkLabel(left, image=None, text="", width=36)
        self.lock_lbl.pack(pady=3)

        # ComboBox modalità valvola
        self.mode_var = ctk.StringVar()
        ctk.CTkLabel(left, text="Modalità valvola:", font=ctk.CTkFont(size=17)).pack(pady=(8,2))
        self.mode_menu = ctk.CTkComboBox(
            left,
            values=["Auto", "Aperta", "Chiusa"],
            variable=self.mode_var,
            width=140,
            height=44,
            font=ctk.CTkFont(size=19),
            dropdown_font=ctk.CTkFont(size=19),
            command=self.on_mode_selected
        )
        self.mode_menu.pack(pady=(0, 10))

        # Step size
        ctk.CTkLabel(left, text="Step soglia (°C):", font=ctk.CTkFont(size=17)).pack()
        self.step_var = ctk.StringVar(value=str(app.settings.get("step_temp", 0.1)))
        steps = ["0.1", "0.2", "0.5", "1.0"]
        self.step_menu = ctk.CTkComboBox(
            left, values=steps, variable=self.step_var,
            width=110, height=44, font=ctk.CTkFont(size=21), dropdown_font=ctk.CTkFont(size=21)
        )
        self.step_menu.pack(pady=6)
        self.step_menu.bind("<<ComboboxSelected>>", self.change_step)

        # Soglie regolabili
        soglie_frame = ctk.CTkFrame(left, fg_color="#223118", corner_radius=10)
        soglie_frame.pack(pady=12)
        ctk.CTkLabel(soglie_frame, text="Soglia Min (°C)", font=ctk.CTkFont(size=19)).grid(row=0, column=0, padx=12, pady=9)
        self.min_lbl = ctk.CTkLabel(soglie_frame, text="", font=ctk.CTkFont(size=20, weight="bold"), text_color="blue")
        self.min_lbl.grid(row=0, column=1, padx=7)
        ctk.CTkButton(soglie_frame, text="-", width=44, height=44, font=ctk.CTkFont(size=20),
                      command=lambda: self.modifica_soglia("min_temp", -1)).grid(row=0, column=2, padx=4)
        ctk.CTkButton(soglie_frame, text="+", width=44, height=44, font=ctk.CTkFont(size=20),
                      command=lambda: self.modifica_soglia("min_temp", 1)).grid(row=0, column=3, padx=4)
        ctk.CTkLabel(soglie_frame, text="Soglia Max (°C)", font=ctk.CTkFont(size=19)).grid(row=1, column=0, padx=12, pady=9)
        self.max_lbl = ctk.CTkLabel(soglie_frame, text="", font=ctk.CTkFont(size=20, weight="bold"), text_color="red")
        self.max_lbl.grid(row=1, column=1, padx=7)
        ctk.CTkButton(soglie_frame, text="-", width=44, height=44, font=ctk.CTkFont(size=20),
                      command=lambda: self.modifica_soglia("max_temp", -1)).grid(row=1, column=2, padx=4)
        ctk.CTkButton(soglie_frame, text="+", width=44, height=44, font=ctk.CTkFont(size=20),
                      command=lambda: self.modifica_soglia("max_temp", 1)).grid(row=1, column=3, padx=4)

        # Intervallo dati
        ctk.CTkLabel(left, text="Intervallo dati:", font=ctk.CTkFont(size=17)).pack(pady=(15, 2))
        self.range_var = ctk.StringVar(value="Ultime 2 ore")
        self.range_menu = ctk.CTkComboBox(
            left,
            values=list(DELTA_MAP.keys()),
            variable=self.range_var,
            width=165,
            height=44,
            font=ctk.CTkFont(size=19),
            dropdown_font=ctk.CTkFont(size=19)
        )
        self.range_menu.pack(pady=(0, 12))
        self.range_menu.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        # DESTRA: GRAFICO
        right = ctk.CTkFrame(self, fg_color='transparent')
        right.grid(row=0, column=1, sticky="nsew", padx=8, pady=10)
        self.fig, self.ax = plt.subplots(figsize=(5.2, 2.6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=0, pady=0)

        self.refresh()

    def get_dot_color(self):
        b = self.app.botti_data[self.nome]
        if b["temperatura"] > b["max_temp"]:
            return "#ed4747"
        elif b["temperatura"] < b["min_temp"]:
            return "#459bed"
        else:
            return "#6ddb57"

    def change_step(self, event=None):
        self.app.settings["step_temp"] = float(self.step_var.get())

    def on_mode_selected(self, event=None):
        mode = self.mode_var.get()
        b = self.app.botti_data[self.nome]
        print(f"[DEBUG] on_mode_selected {self.nome}: user set mode to {mode}")
        if mode == "Auto":
            b["forced"] = None
        elif mode in ("Aperta", "Chiusa"):
            b["forced"] = mode
        save_config(self.app.botti_data, self.app.settings)

    def modifica_soglia(self, tipo, delta):
        step = float(self.app.settings.get("step_temp", 0.1))
        b = self.app.botti_data[self.nome]
        b[tipo] = round(b[tipo] + delta * step, 1)
        self.refresh()

    def refresh(self):
        b = self.app.botti_data[self.nome]
        forced = b.get("forced")
        print(f"[DEBUG] refresh {self.nome}: forced={forced}, mode_var={self.mode_var.get()}")
        expected = {
            None: "Auto",
            "Aperta": "Aperta",
            "Chiusa": "Chiusa"
        }[forced]
        if self.mode_var.get() != expected:
            self.mode_var.set(expected)
        self.dot_lbl.configure(text_color=self.get_dot_color())
        self.temp_lbl.configure(text=f"{b['temperatura']} °C")
        self.valve_lbl.configure(text=f"Valvola: {b['valvola']}")
        self.min_lbl.configure(text=f"{b['min_temp']:.1f}")
        self.max_lbl.configure(text=f"{b['max_temp']:.1f}")
        show_lock = b.get("forced") in ("Aperta", "Chiusa")
        self.lock_lbl.configure(image=self.lock_icon if show_lock else None)

        # GRAFICO
        self.ax.clear()
        temp_history = b.get("history", [])
        now = datetime.datetime.now()
        if temp_history and not isinstance(temp_history[0][0], datetime.datetime):
            temp_history = [
                (now - datetime.timedelta(minutes=(len(temp_history)-1-i)*2), v)
                for i, (__, v) in enumerate(temp_history)
            ]
        sel = self.range_var.get()
        cutoff = now - DELTA_MAP.get(sel, datetime.timedelta.max) if DELTA_MAP.get(sel) else None
        data = [x for x in temp_history if not cutoff or x[0] >= cutoff]
        if data:
            x = [t for t, v in data]
            y = [v for t, v in data]
            self.ax.plot(x, y, marker='o', color='#50bcdf', label="Temperatura")
            self.ax.axhline(b['min_temp'], color='blue', linestyle='--', label='Min')
            self.ax.axhline(b['max_temp'], color='red', linestyle='--', label='Max')
            self.ax.legend()
            self.ax.set_ylabel("°C")
            self.ax.grid(True)
            self.fig.tight_layout()
        self.canvas.draw()
