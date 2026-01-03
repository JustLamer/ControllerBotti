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
        self.grid_columnconfigure(0, weight=1)
        self.show_legend = True

        # Font settings
        font_xs = font(size=FONT_SIZES["xs"])
        font_s = font(size=FONT_SIZES["sm"])
        font_m = font(size=FONT_SIZES["md"], weight="bold")
        font_l = font(size=FONT_SIZES["lg"], weight="bold")

        # HEADER: titolo + dot + temperatura + valvola + lock su una riga compatta
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(SPACING["md"], SPACING["sm"]), padx=(SPACING["lg"], SPACING["lg"]))
        header.grid_columnconfigure(0, weight=1)
        title_block = ctk.CTkFrame(header, fg_color="transparent")
        title_block.grid(row=0, column=0, sticky="w")
        self.title_lbl = ctk.CTkLabel(title_block, text=nome, font=font(size=FONT_SIZES["xl"], weight="bold"))
        self.title_lbl.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            title_block,
            text="Controllo singola botte",
            font=font(size=FONT_SIZES["md"]),
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
        self.dot_lbl = ctk.CTkLabel(status_card, text="●", font=font(size=24), text_color=COLORS["success"])
        self.dot_lbl.grid(row=0, column=0, padx=(SPACING["sm"], 6), pady=SPACING["sm"])
        self.temp_lbl = ctk.CTkLabel(status_card, text="", font=font(size=FONT_SIZES["xl"], weight="bold"))
        self.temp_lbl.grid(row=0, column=1, padx=SPACING["sm"], pady=SPACING["sm"])
        self.valve_lbl = ctk.CTkLabel(status_card, text="", font=font_m)
        self.valve_lbl.grid(row=0, column=2, padx=SPACING["sm"], pady=SPACING["sm"])
        self.lock_lbl = ctk.CTkLabel(status_card, image=None, text="", width=24)
        self.lock_lbl.grid(row=0, column=3, padx=(SPACING["xs"], SPACING["sm"]), pady=SPACING["sm"])
        img_lock = Image.open("assets/lock.png").resize((22, 22))
        self.lock_icon = ctk.CTkImage(light_image=img_lock, dark_image=img_lock)

        # Tab view per separare controlli e grafico
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=COLORS["panel"],
            corner_radius=RADIUS["lg"],
            segmented_button_fg_color=COLORS["panel_alt"],
            segmented_button_selected_color=COLORS["accent"],
            segmented_button_selected_hover_color=COLORS["accent_dark"],
            segmented_button_unselected_color=COLORS["panel_soft"],
            segmented_button_unselected_hover_color=COLORS["panel_alt"],
        )
        if hasattr(self.tabview, "_segmented_button"):
            self.tabview._segmented_button.configure(
                height=56,
                font=font(size=FONT_SIZES["lg"], weight="bold"),
            )
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=SPACING["lg"], pady=(0, SPACING["lg"]))
        self.tabview.add("Controlli")
        self.tabview.add("Grafico")

        controls_tab = self.tabview.tab("Controlli")
        graph_tab = self.tabview.tab("Grafico")
        controls_tab.grid_columnconfigure(0, weight=1)
        graph_tab.grid_columnconfigure(0, weight=1)

        # Controlli principali
        control_card = ctk.CTkFrame(
            controls_tab,
            fg_color=COLORS["panel_alt"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
        )
        control_card.grid(row=0, column=0, sticky="ew", pady=(SPACING["md"], SPACING["sm"]), padx=SPACING["sm"])
        control_card.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(control_card, text="Modalità valvola", font=font_m).grid(
            row=0, column=0, padx=SPACING["md"], pady=SPACING["sm"], sticky="w"
        )
        self.mode_var = ctk.StringVar()
        self.mode_segmented = ctk.CTkSegmentedButton(
            control_card,
            values=["Auto", "Aperta", "Chiusa"],
            variable=self.mode_var,
            command=self.on_mode_selected,
            font=font_s,
            height=48,
            corner_radius=RADIUS["sm"],
        )
        self.mode_segmented.grid(row=0, column=1, padx=SPACING["md"], pady=SPACING["sm"], sticky="e")

        # Soglie e step
        soglie_frame = ctk.CTkFrame(
            controls_tab,
            fg_color=COLORS["panel_alt"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
        )
        soglie_frame.grid(row=1, column=0, sticky="ew", padx=SPACING["sm"], pady=SPACING["sm"])
        soglie_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        ctk.CTkLabel(soglie_frame, text="Soglia minima", font=font_s, text_color=COLORS["info"]).grid(
            row=0, column=0, padx=SPACING["sm"], pady=(SPACING["sm"], SPACING["xs"]), sticky="w"
        )
        ctk.CTkLabel(soglie_frame, text="Soglia massima", font=font_s, text_color=COLORS["danger"]).grid(
            row=0, column=3, padx=SPACING["sm"], pady=(SPACING["sm"], SPACING["xs"]), sticky="w"
        )

        btn_minm = ctk.CTkButton(
            soglie_frame,
            text="−",
            width=56,
            height=56,
            font=font(size=FONT_SIZES["xl"], weight="bold"),
            fg_color=COLORS["panel_soft"],
            hover_color=COLORS["panel_alt"],
            text_color=COLORS["accent"],
            border_width=0,
            command=lambda: self._button_feedback(self.modifica_soglia, "min_temp", -1),
        )
        btn_minm.grid(row=1, column=0, padx=SPACING["sm"], pady=SPACING["sm"], sticky="w")
        self.min_lbl = ctk.CTkLabel(soglie_frame, text="", font=font_m, width=80)
        self.min_lbl.grid(row=1, column=1, padx=SPACING["xs"], pady=SPACING["sm"], sticky="w")
        btn_minp = ctk.CTkButton(
            soglie_frame,
            text="+",
            width=56,
            height=56,
            font=font(size=FONT_SIZES["xl"], weight="bold"),
            fg_color=COLORS["panel_soft"],
            hover_color=COLORS["panel_alt"],
            text_color=COLORS["accent"],
            border_width=0,
            command=lambda: self._button_feedback(self.modifica_soglia, "min_temp", 1),
        )
        btn_minp.grid(row=1, column=2, padx=SPACING["sm"], pady=SPACING["sm"], sticky="w")

        btn_maxm = ctk.CTkButton(
            soglie_frame,
            text="−",
            width=56,
            height=56,
            font=font(size=FONT_SIZES["xl"], weight="bold"),
            fg_color=COLORS["panel_soft"],
            hover_color=COLORS["panel_alt"],
            text_color=COLORS["accent"],
            border_width=0,
            command=lambda: self._button_feedback(self.modifica_soglia, "max_temp", -1),
        )
        btn_maxm.grid(row=1, column=3, padx=SPACING["sm"], pady=SPACING["sm"], sticky="w")
        self.max_lbl = ctk.CTkLabel(soglie_frame, text="", font=font_m, width=80)
        self.max_lbl.grid(row=1, column=4, padx=SPACING["xs"], pady=SPACING["sm"], sticky="w")
        btn_maxp = ctk.CTkButton(
            soglie_frame,
            text="+",
            width=56,
            height=56,
            font=font(size=FONT_SIZES["xl"], weight="bold"),
            fg_color=COLORS["panel_soft"],
            hover_color=COLORS["panel_alt"],
            text_color=COLORS["accent"],
            border_width=0,
            command=lambda: self._button_feedback(self.modifica_soglia, "max_temp", 1),
        )
        btn_maxp.grid(row=1, column=5, padx=SPACING["sm"], pady=SPACING["sm"], sticky="w")

        step_frame = ctk.CTkFrame(controls_tab, fg_color="transparent")
        step_frame.grid(row=2, column=0, sticky="ew", padx=SPACING["sm"], pady=(0, SPACING["sm"]))
        ctk.CTkLabel(step_frame, text="Passo regolazione", font=font_s).grid(
            row=0, column=0, sticky="w", padx=SPACING["sm"]
        )
        self.step_var = ctk.StringVar(value=str(app.settings.get("step_temp", 0.1)))
        steps = ["0.1", "0.2", "0.5", "1.0"]
        self.step_menu = ctk.CTkComboBox(
            step_frame,
            values=steps,
            variable=self.step_var,
            width=120,
            height=42,
            font=font_s,
            dropdown_font=font_s,
            command=self.change_step,
        )
        self.step_menu.grid(row=0, column=1, padx=SPACING["sm"], sticky="w")

        # Grafico con controlli dedicati
        graph_controls = ctk.CTkFrame(graph_tab, fg_color="transparent")
        graph_controls.grid(row=0, column=0, sticky="ew", padx=SPACING["sm"], pady=(SPACING["sm"], SPACING["xs"]))
        ctk.CTkLabel(graph_controls, text="Intervallo grafico", font=font_s).grid(
            row=0, column=0, padx=SPACING["sm"], sticky="w"
        )
        self.range_var = ctk.StringVar(value="Ultime 2 ore")
        self.range_menu = ctk.CTkComboBox(
            graph_controls,
            values=list(DELTA_MAP.keys()),
            variable=self.range_var,
            width=180,
            height=42,
            font=font_s,
            dropdown_font=font_s,
            command=lambda _: self.refresh(),
        )
        self.range_menu.grid(row=0, column=1, padx=SPACING["sm"], sticky="w")

        self.legend_btn = ctk.CTkButton(
            graph_controls,
            text="Legenda: ON",
            width=160,
            font=font_s,
            height=42,
            command=self.toggle_legend,
            fg_color=COLORS["panel_alt"],
            hover_color=COLORS["panel_soft"],
            border_width=1,
            border_color=COLORS["border"],
        )
        self.legend_btn.grid(row=0, column=2, padx=SPACING["sm"], sticky="w")

        right = ctk.CTkFrame(
            graph_tab,
            fg_color=COLORS["panel_alt"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
        )
        right.grid(row=1, column=0, sticky="nsew", padx=SPACING["sm"], pady=SPACING["sm"])
        self.fig, self.ax = plt.subplots(figsize=(7.2, 3.4))
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
            b["valvola"] = mode
            b["last_valve_change"] = datetime.datetime.now()
            b.setdefault("valve_history", []).append((b["last_valve_change"], b["valvola"]))
        save_config(self.app.botti_data, self.app.settings)
        overview = getattr(self.app, "pages", {}).get("Panoramica")
        if overview and hasattr(overview, "refresh"):
            overview.refresh()
        self.refresh()
        if old_forced != b["forced"]:
            log_event("CambioModalità", self.nome, f"Da {old_forced} a {b['forced']}")

    def modifica_soglia(self, tipo, delta):
        step = float(self.app.settings.get("step_temp", 0.1))
        b = self.app.botti_data[self.nome]
        old_val = b[tipo]
        b[tipo] = round(b[tipo] + delta * step, 1)
        self.refresh()
        overview = getattr(self.app, "pages", {}).get("Panoramica")
        if overview and hasattr(overview, "refresh"):
            overview.refresh()
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
        self.ax.tick_params(colors=COLORS["text_muted"], labelsize=9)
        if data:
            x = [t for t, v in data]
            y = [v for t, v in data]
            self.ax.plot(x, y, marker='o', markersize=3, color=COLORS["accent"], label="Temperatura")
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
                self.ax.legend(fontsize=9, loc='best')
            else:
                leg = self.ax.get_legend()
                if leg:
                    leg.remove()
            self.ax.set_ylabel("°C", fontsize=10, color=COLORS["text_muted"])
            self.ax.grid(True, linewidth=0.5, color=COLORS["panel_soft"])
            self.fig.tight_layout()
        self.canvas.draw()
