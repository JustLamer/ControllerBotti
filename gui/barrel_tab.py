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
        super().__init__(master, corner_radius=22, fg_color="#223118", **kwargs)
        self.app = app
        self.nome = nome

        self.grid_columnconfigure(1, weight=1)

        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsw", padx=18, pady=18)

        ctk.CTkLabel(left, text=nome, font=ctk.CTkFont(size=30, weight="bold")).pack(pady=(18, 10))
        self.dot_lbl = ctk.CTkLabel(left, text="●", font=ctk.CTkFont(size=44), text_color="#6ddb57")
        self.dot_lbl.pack()
        self.temp_lbl = ctk.CTkLabel(left, text="", font=ctk.CTkFont(size=31, weight="bold"))
        self.temp_lbl.pack(pady=10)
        self.valve_lbl = ctk.CTkLabel(left, text="", font=ctk.CTkFont(size=25))
        self.valve_lbl.pack(pady=7)

        img_lock = Image.open("assets/lock.png").resize((36, 36))
        self.lock_icon = ctk.CTkImage(light_image=img_lock, dark_image=img_lock)
        self.lock_lbl = ctk.CTkLabel(left, image=None, text="", width=40)
        self.lock_lbl.pack(pady=3)

        # Modalità valvola
        self.mode_var = ctk.StringVar()
        ctk.CTkLabel(left, text="Modalità valvola:", font=ctk.CTkFont(size=21)).pack(pady=(12,2))
        self.mode_menu = ctk.CTkComboBox(
            left,
            values=["Auto", "Aperta", "Chiusa"],
            variable=self.mode_var,
            width=146,
            height=48,
            font=ctk.CTkFont(size=23),
            dropdown_font=ctk.CTkFont(size=23),
            command=self.on_mode_selected
        )
        self.mode_menu.pack(pady=(0,13))

        # Step soglia
        ctk.CTkLabel(left, text="Step soglia (°C):", font=ctk.CTkFont(size=21)).pack()
        self.step_var = ctk.StringVar(value=str(app.settings.get("step_temp", 0.1)))
        steps = ["0.1", "0.2", "0.5", "1.0"]
        self.step_menu = ctk.CTkComboBox(
            left, values=steps, variable=self.step_var,
            width=115, height=48, font=ctk.CTkFont(size=23),
            dropdown_font=ctk.CTkFont(size=23),
            command=self.change_step
        )
        self.step_menu.pack(pady=8)

        # Soglie regolabili
        soglie_frame = ctk.CTkFrame(left, fg_color="#223118", corner_radius=12)
        soglie_frame.pack(pady=13)
        ctk.CTkLabel(soglie_frame, text="Min (°C)", font=ctk.CTkFont(size=21)).grid(row=0, column=0, padx=12, pady=9)
        self.min_lbl = ctk.CTkLabel(soglie_frame, text="", font=ctk.CTkFont(size=23, weight="bold"), text_color="blue")
        self.min_lbl.grid(row=0, column=1, padx=7)
        btn_minm = ctk.CTkButton(soglie_frame, text="-", width=46, height=46, font=ctk.CTkFont(size=22),
                      command=lambda: self._button_feedback(self.modifica_soglia, "min_temp", -1))
        btn_minm.grid(row=0, column=2, padx=4)
        btn_minp = ctk.CTkButton(soglie_frame, text="+", width=46, height=46, font=ctk.CTkFont(size=22),
                      command=lambda: self._button_feedback(self.modifica_soglia, "min_temp", 1))
        btn_minp.grid(row=0, column=3, padx=4)
        ctk.CTkLabel(soglie_frame, text="Max (°C)", font=ctk.CTkFont(size=21)).grid(row=1, column=0, padx=12, pady=9)
        self.max_lbl = ctk.CTkLabel(soglie_frame, text="", font=ctk.CTkFont(size=23, weight="bold"), text_color="red")
        self.max_lbl.grid(row=1, column=1, padx=7)
        btn_maxm = ctk.CTkButton(soglie_frame, text="-", width=46, height=46, font=ctk.CTkFont(size=22),
                      command=lambda: self._button_feedback(self.modifica_soglia, "max_temp", -1))
        btn_maxm.grid(row=1, column=2, padx=4)
        btn_maxp = ctk.CTkButton(soglie_frame, text="+", width=46, height=46, font=ctk.CTkFont(size=22),
                      command=lambda: self._button_feedback(self.modifica_soglia, "max_temp", 1))
        btn_maxp.grid(row=1, column=3, padx=4)

        # Intervallo dati
        ctk.CTkLabel(left, text="Intervallo dati:", font=ctk.CTkFont(size=21)).pack(pady=(16, 2))
        self.range_var = ctk.StringVar(value="Ultime 2 ore")
        self.range_menu = ctk.CTkComboBox(
            left,
            values=list(DELTA_MAP.keys()),
            variable=self.range_var,
            width=170,
            height=48,
            font=ctk.CTkFont(size=22),
            dropdown_font=ctk.CTkFont(size=22),
            command=lambda _: self.refresh()
        )
        self.range_menu.pack(pady=(0, 15))

        # Destra: grafico
        right = ctk.CTkFrame(self, fg_color='transparent')
        right.grid(row=0, column=1, sticky="nsew", padx=18, pady=18)
        self.fig, self.ax = plt.subplots(figsize=(5.6, 2.7))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=0, pady=0)

        self.refresh()

    def _button_feedback(self, func, *args):
        btn = self.focus_get()
        if btn and isinstance(btn, ctk.CTkButton):
            orig = btn.cget("fg_color")
            btn.configure(fg_color="#44c079")
            self.after(120, lambda: btn.configure(fg_color=orig))
        func(*args)

    def animate_dot_color(self, target_color, steps=9, duration=180):
        def hex_to_rgb(hex_color):
            return tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))
        def rgb_to_hex(rgb):
            return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
        current = self.dot_lbl.cget("text_color")
        if not isinstance(current, str) or not current.startswith('#'): current = "#6ddb57"
        curr_rgb = hex_to_rgb(current)
        target_rgb = hex_to_rgb(target_color)
        for step in range(steps+1):
            ratio = step / steps
            r = int(curr_rgb[0] + (target_rgb[0] - curr_rgb[0]) * ratio)
            g = int(curr_rgb[1] + (target_rgb[1] - curr_rgb[1]) * ratio)
            b = int(curr_rgb[2] + (target_rgb[2] - curr_rgb[2]) * ratio)
            color = rgb_to_hex((r, g, b))
            self.dot_lbl.configure(text_color=color)
            self.update()
            self.after(duration // steps)

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

    def on_mode_selected(self, mode):
        b = self.app.botti_data[self.nome]
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
        expected = {
            None: "Auto",
            "Aperta": "Aperta",
            "Chiusa": "Chiusa"
        }[forced]
        if self.mode_var.get() != expected:
            self.mode_var.set(expected)
        self.animate_dot_color(self.get_dot_color())
        self.temp_lbl.configure(text=f"{b['temperatura']} °C")
        self.valve_lbl.configure(text=f"Valvola: {b['valvola']}")
        self.min_lbl.configure(text=f"{b['min_temp']:.1f}")
        self.max_lbl.configure(text=f"{b['max_temp']:.1f}")
        show_lock = b.get("forced") in ("Aperta", "Chiusa")
        self.lock_lbl.configure(image=self.lock_icon if show_lock else None)

        # Grafico
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
