import customtkinter as ctk
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import datetime
from config import save_config
from utils.logger import log_event
from gui.theme import COLORS, FONT_SIZES, RADIUS, SPACING, font

DELTA_MAP = {
    "Tutto": None,
    "Ultimi 5 min": datetime.timedelta(minutes=5),
    "Ultimi 15 min": datetime.timedelta(minutes=15),
    "Ultime 2 ore": datetime.timedelta(hours=2),
    "Ultime 6 ore": datetime.timedelta(hours=6),
    "Ultime 24 ore": datetime.timedelta(hours=24),
    "Ultima settimana": datetime.timedelta(days=7),
}


def ensure_dt(t):
    if isinstance(t, datetime.datetime):
        return t
    try:
        return datetime.datetime.fromisoformat(t)
    except Exception:
        return t  # fallback


class BarrelTab(ctk.CTkFrame):
    def __init__(self, master, app, nome, **kwargs):
        super().__init__(master, corner_radius=16, fg_color=COLORS["panel"], **kwargs)
        self.app = app
        self.nome = nome
        self.grid_columnconfigure(1, weight=1)
        self.show_legend = True

        # Font settings
        font_xs = font(size=FONT_SIZES["xs"])
        font_s = font(size=FONT_SIZES["sm"])
        font_m = font(size=FONT_SIZES["md"], weight="bold")
        font_l = font(size=FONT_SIZES["lg"], weight="bold")

        # HEADER: titolo + dot + temperatura + valvola + lock su una riga compatta
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(SPACING["sm"], SPACING["xs"]), padx=(SPACING["sm"], SPACING["sm"]))
        header.grid_columnconfigure(0, weight=1)
        title_block = ctk.CTkFrame(header, fg_color="transparent")
        title_block.grid(row=0, column=0, sticky="w")
        self.title_lbl = ctk.CTkLabel(title_block, text=nome, font=font(size=FONT_SIZES["xl"], weight="bold"))
        self.title_lbl.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            title_block,
            text="Controllo singola botte",
            font=font(size=FONT_SIZES["sm"]),
            text_color=COLORS["text_muted"],
        ).grid(row=1, column=0, sticky="w")

        status_card = ctk.CTkFrame(
            header,
            fg_color=COLORS["panel_alt"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
        )
        status_card.grid(row=0, column=1, padx=(SPACING["sm"], 0), sticky="e")
        self.dot_lbl = ctk.CTkLabel(status_card, text="●", font=font(size=18), text_color=COLORS["success"])
        self.dot_lbl.grid(row=0, column=0, padx=(SPACING["sm"], 4), pady=SPACING["sm"])
        self.temp_lbl = ctk.CTkLabel(status_card, text="", font=font(size=FONT_SIZES["lg"], weight="bold"))
        self.temp_lbl.grid(row=0, column=1, padx=SPACING["xs"], pady=SPACING["sm"])
        self.valve_lbl = ctk.CTkLabel(status_card, text="", font=font_m)
        self.valve_lbl.grid(row=0, column=2, padx=SPACING["xs"], pady=SPACING["sm"])
        self.lock_lbl = ctk.CTkLabel(status_card, image=None, text="", width=18)
        self.lock_lbl.grid(row=0, column=3, padx=(SPACING["xs"], SPACING["sm"]), pady=SPACING["sm"])
        img_lock = Image.open("assets/lock.png").resize((16, 16))
        self.lock_icon = ctk.CTkImage(light_image=img_lock, dark_image=img_lock)

        # ComboBox affiancati
        cb_frame = ctk.CTkFrame(self, fg_color="transparent")
        cb_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(SPACING["xs"], SPACING["sm"]), padx=(SPACING["sm"], SPACING["sm"]))
        cb_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=0)
        ctk.CTkLabel(cb_frame, text="Modalità:", font=font_s).grid(row=0, column=0, sticky="e", padx=2)
        self.mode_var = ctk.StringVar()
        self.mode_menu = ctk.CTkComboBox(cb_frame, values=["Auto", "Aperta", "Chiusa"], variable=self.mode_var,
                                         width=72, height=24, font=font_s, dropdown_font=font_s,
                                         command=self.on_mode_selected)
        self.mode_menu.grid(row=0, column=1, sticky="w", padx=2)

        ctk.CTkLabel(cb_frame, text="Intervallo:", font=font_s).grid(row=0, column=2, sticky="e", padx=(10, 2))
        self.range_var = ctk.StringVar(value="Ultime 2 ore")
        self.range_menu = ctk.CTkComboBox(cb_frame, values=list(DELTA_MAP.keys()), variable=self.range_var,
                                          width=90, height=24, font=font_s, dropdown_font=font_s,
                                          command=lambda _: self.refresh())
        self.range_menu.grid(row=0, column=3, sticky="w", padx=2)

        self.legend_btn = ctk.CTkButton(
            cb_frame,
            text="Legenda: ON",
            width=74,
            font=font_xs,
            height=26,
            command=self.toggle_legend,
            fg_color=COLORS["panel_alt"],
            hover_color=COLORS["panel_soft"],
            border_width=1,
            border_color=COLORS["border"],
        )
        self.legend_btn.grid(row=0, column=4, padx=(8, 0), sticky="w")

        # Soglie e step (in una riga compatta)
        soglie_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["panel_alt"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
        )
        soglie_frame.grid(row=2, column=0, sticky="ew", padx=SPACING["sm"], pady=SPACING["sm"])
        soglie_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=0)
        ctk.CTkLabel(soglie_frame, text="Min:", font=font_xs, text_color=COLORS["info"]).grid(row=0, column=0)
        btn_minm = ctk.CTkButton(soglie_frame, text="-", width=18, height=18, font=font_xs,
                                 command=lambda: self._button_feedback(self.modifica_soglia, "min_temp", -1))
        btn_minm.grid(row=0, column=1, padx=1)
        self.min_lbl = ctk.CTkLabel(soglie_frame, text="", font=font_xs, width=22)
        self.min_lbl.grid(row=0, column=2)
        btn_minp = ctk.CTkButton(soglie_frame, text="+", width=18, height=18, font=font_xs,
                                 command=lambda: self._button_feedback(self.modifica_soglia, "min_temp", 1))
        btn_minp.grid(row=0, column=3, padx=1)
        ctk.CTkLabel(soglie_frame, text="Max:", font=font_xs, text_color=COLORS["danger"]).grid(row=0, column=4, padx=(8, 0))
        btn_maxm = ctk.CTkButton(soglie_frame, text="-", width=18, height=18, font=font_xs,
                                 command=lambda: self._button_feedback(self.modifica_soglia, "max_temp", -1))
        btn_maxm.grid(row=0, column=5, padx=1)
        self.max_lbl = ctk.CTkLabel(soglie_frame, text="", font=font_xs, width=22)
        self.max_lbl.grid(row=0, column=6)
        btn_maxp = ctk.CTkButton(soglie_frame, text="+", width=18, height=18, font=font_xs,
                                 command=lambda: self._button_feedback(self.modifica_soglia, "max_temp", 1))
        btn_maxp.grid(row=0, column=7, padx=1)
        ctk.CTkLabel(soglie_frame, text="Step:", font=font_xs).grid(row=0, column=8, padx=(8, 2))
        self.step_var = ctk.StringVar(value=str(app.settings.get("step_temp", 0.1)))
        steps = ["0.1", "0.2", "0.5", "1.0"]
        self.step_menu = ctk.CTkComboBox(
            soglie_frame, values=steps, variable=self.step_var,
            width=44, height=20, font=font_xs,
            dropdown_font=font_xs,
            command=self.change_step
        )
        self.step_menu.grid(row=0, column=9, padx=2)

        # Grafico (allargato)
        right = ctk.CTkFrame(
            self,
            fg_color=COLORS["panel_alt"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
        )
        right.grid(row=3, column=0, sticky="nsew", padx=SPACING["sm"], pady=SPACING["sm"])
        # Nuove dimensioni: larghezza +40%, altezza +20%
        self.fig, self.ax = plt.subplots(figsize=(6, 2.8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=SPACING["xs"], pady=SPACING["xs"])

        self.refresh()

    def _button_feedback(self, func, *args):
        btn = self.focus_get()
        if btn and isinstance(btn, ctk.CTkButton):
            orig = btn.cget("fg_color")
            btn.configure(fg_color=COLORS["accent"])
            self.after(80, lambda: btn.configure(fg_color=orig))
        func(*args)

    def animate_dot_color(self, target_color, steps=7, duration=80):
        def hex_to_rgb(hex_color):
            return tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))

        def rgb_to_hex(rgb):
            return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'

        current = self.dot_lbl.cget("text_color")
        if not isinstance(current, str) or not current.startswith('#'): current = "#6ddb57"
        curr_rgb = hex_to_rgb(current)
        target_rgb = hex_to_rgb(target_color)
        for step in range(steps + 1):
            ratio = step / steps
            r = int(curr_rgb[0] + (target_rgb[0] - curr_rgb[0]) * ratio)
            g = int(curr_rgb[1] + (target_rgb[1] - curr_rgb[1]) * ratio)
            b = int(curr_rgb[2] + (target_rgb[2] - curr_rgb[2]) * ratio)
            color = rgb_to_hex((r, g, b))
            # --- AGGIUNGI QUESTO CONTROLLO ---
            try:
                if self.dot_lbl.winfo_exists():
                    self.dot_lbl.configure(text_color=color)
                    self.update()
            except Exception as e:
                # Widget non più valido, interrompi
                break
            self.after(duration // steps)

    def get_dot_color(self):
        b = self.app.botti_data[self.nome]
        if b["temperatura"] > b["max_temp"]:
            return COLORS["danger"]
        elif b["temperatura"] < b["min_temp"]:
            return COLORS["info"]
        else:
            return COLORS["success"]

    def change_step(self, event=None):
        self.app.settings["step_temp"] = float(self.step_var.get())

    def on_mode_selected(self, mode):
        b = self.app.botti_data[self.nome]
        old_forced = b.get("forced")
        if mode == "Auto":
            b["forced"] = None
        elif mode in ("Aperta", "Chiusa"):
            b["forced"] = mode
        save_config(self.app.botti_data, self.app.settings)
        if old_forced != b["forced"]:
            log_event("CambioModalità", self.nome, f"Da {old_forced} a {b['forced']}")

    def modifica_soglia(self, tipo, delta):
        step = float(self.app.settings.get("step_temp", 0.1))
        b = self.app.botti_data[self.nome]
        old_val = b[tipo]
        b[tipo] = round(b[tipo] + delta * step, 1)
        self.refresh()
        if b[tipo] != old_val:
            log_event("CambioSoglia", self.nome, f"{tipo}: {old_val} -> {b[tipo]}")

    def toggle_legend(self):
        self.show_legend = not self.show_legend
        self.legend_btn.configure(text=f"Legenda: {'ON' if self.show_legend else 'OFF'}")
        self.refresh()

    def refresh(self):
        b = self.app.botti_data[self.nome]

        if hasattr(self, 'temp_lbl') and self.temp_lbl.winfo_exists():
            self.temp_lbl.configure(text=f"{b['temperatura']:.1f} °C")
        forced = b.get("forced")
        expected = {
            None: "Auto",
            "Aperta": "Aperta",
            "Chiusa": "Chiusa"
        }[forced]
        if self.mode_var.get() != expected:
            self.mode_var.set(expected)
        self.animate_dot_color(self.get_dot_color())
        self.temp_lbl.configure(text=f"{b['temperatura']:.1f} °C")
        self.valve_lbl.configure(text=f"Valvola: {b['valvola']}")
        self.min_lbl.configure(text=f"{b['min_temp']:.1f}")
        self.max_lbl.configure(text=f"{b['max_temp']:.1f}")
        show_lock = b.get("forced") in ("Aperta", "Chiusa")
        self.lock_lbl.configure(image=self.lock_icon if show_lock else None)
        if show_lock:
            self.lock_lbl.grid(row=0, column=4)
        else:
            self.lock_lbl.grid_remove()

        # --- GRAFICO ---
        temp_history = b.get("history", [])
        if "valve_history" not in b:
            b["valve_history"] = []
        valve_history = b.get("valve_history", [])
        now = datetime.datetime.now()
        sel = self.range_var.get()
        cutoff = now - DELTA_MAP.get(sel, datetime.timedelta.max) if DELTA_MAP.get(sel) else None

        data = [(ensure_dt(t), v) for t, v in temp_history]
        vdata = [(ensure_dt(t), v) for t, v in valve_history]
        if cutoff:
            data = [x for x in data if x[0] >= cutoff]
            vdata = [x for x in vdata if x[0] >= cutoff]

        self.ax.clear()
        self.fig.patch.set_facecolor(COLORS["panel"])
        self.ax.set_facecolor(COLORS["panel_alt"])
        self.ax.tick_params(colors=COLORS["text_muted"], labelsize=7)
        if data:
            x = [t for t, v in data]
            y = [v for t, v in data]
            self.ax.plot(x, y, marker='o', markersize=2, color=COLORS["accent"], label="Temperatura")
            self.ax.axhline(b['min_temp'], color=COLORS["info"], linestyle='--', label='Min')
            self.ax.axhline(b['max_temp'], color=COLORS["danger"], linestyle='--', label='Max')
            opens = [t for t, v in vdata if v == "Aperta"]
            closes = [t for t, v in vdata if v == "Chiusa"]
            self.ax.scatter(opens, [b['max_temp']] * len(opens), marker='v', color=COLORS["warning"], label='Aperta')
            self.ax.scatter(closes, [b['min_temp']] * len(closes), marker='^', color=COLORS["panel_soft"], label='Chiusa')
            locator = mdates.AutoDateLocator(minticks=2, maxticks=4)
            self.ax.xaxis.set_major_locator(locator)
            self.ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))
            self.fig.autofmt_xdate(rotation=20)
            if self.show_legend:
                self.ax.legend(fontsize=7, loc='best')
            else:
                leg = self.ax.get_legend()
                if leg:
                    leg.remove()
            self.ax.set_ylabel("°C", fontsize=8, color=COLORS["text_muted"])
            self.ax.grid(True, linewidth=0.5, color=COLORS["panel_soft"])
            self.fig.tight_layout()
        self.canvas.draw()
