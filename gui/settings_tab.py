import customtkinter as ctk
import threading
import datetime
from config import save_config
from gui.theme import COLORS, FONT_SIZES, RADIUS, SPACING, font

class SettingsTab(ctk.CTkFrame):
    def __init__(self, master, sensor_manager, actuators, on_mapping_change, on_test_mode_change, **kwargs):
        super().__init__(master, fg_color=COLORS["panel"], **kwargs)
        self.sensor_manager = sensor_manager
        self.actuators = actuators
        self.on_mapping_change = on_mapping_change
        self.on_test_mode_change = on_test_mode_change
        self.combo_vars = {}
        self.combo_widgets = {}
        self.serial_labels = []
        self.test_mode_var = ctk.BooleanVar(value=False)
        self.test_output = None
        self.test_buttons = []
        self.status_label = None
        self.update_interval_var = ctk.StringVar()
        self.min_switch_interval_var = ctk.StringVar()
        self.save_interval_var = ctk.StringVar()
        self.test_barrel_var = ctk.StringVar(value="")
        self.fake_sensor_entries = []

        self.build_ui()

    def build_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self,
            text="Impostazioni",
            font=font(size=FONT_SIZES["xl"], weight="bold"),
            text_color=COLORS["text"],
        ).grid(row=0, column=0, columnspan=4, pady=(SPACING["lg"], SPACING["sm"]), padx=SPACING["xl"], sticky="w")
        ctk.CTkLabel(
            self,
            text="Associa sensori, regola i tempi di controllo e verifica l'hardware.",
            font=font(size=FONT_SIZES["md"]),
            text_color=COLORS["text_muted"],
        ).grid(row=1, column=0, columnspan=4, padx=SPACING["xl"], sticky="w")

        serials = self.sensor_manager.rescan_serials() or [""]
        if "test" not in serials:
            serials.insert(0, "test")
        if not serials:
            serials = [""]
        botti = list(self.master.botti_data.keys())
        if botti:
            self.test_barrel_var.set(botti[0])

        mapping_card = ctk.CTkFrame(
            self,
            fg_color=COLORS["panel_alt"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
        )
        mapping_card.grid(row=2, column=0, columnspan=4, padx=SPACING["xl"], pady=(SPACING["sm"], SPACING["md"]), sticky="ew")
        mapping_card.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            mapping_card,
            text="Associa ogni botte a una sonda",
            font=font(size=FONT_SIZES["md"], weight="bold"),
            text_color=COLORS["text"],
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=SPACING["md"], pady=(SPACING["sm"], SPACING["xs"]))

        for i, botte in enumerate(botti):
            ctk.CTkLabel(mapping_card, text=f"{botte}:", width=120, anchor="e", font=font(size=FONT_SIZES["sm"])).grid(
                row=1 + i, column=0, padx=(SPACING["md"], SPACING["sm"]), pady=SPACING["xs"], sticky="e")
            selected_serial = self.master.settings.get("sensors_mapping", {}).get(botte, "")
            var = ctk.StringVar(value=selected_serial)
            cb = ctk.CTkComboBox(
                mapping_card,
                values=serials,
                variable=var,
                width=280,
                height=42,
                font=font(size=FONT_SIZES["sm"]),
                dropdown_font=font(size=FONT_SIZES["sm"]),
            )
            cb.grid(row=1 + i, column=1, padx=(0, SPACING["md"]), pady=SPACING["xs"], sticky="w")
            apply_btn = ctk.CTkButton(
                mapping_card,
                text="Applica",
                font=font(size=FONT_SIZES["sm"]),
                fg_color=COLORS["accent"],
                hover_color=COLORS["accent_dark"],
                height=42,
                width=120,
                command=lambda b=botte: self.change_assoc(b, self.combo_vars[b]),
            )
            apply_btn.grid(row=1 + i, column=2, padx=(0, SPACING["md"]), pady=SPACING["xs"], sticky="w")
            self.combo_vars[botte] = var
            self.combo_widgets[botte] = cb

        # Titolo e serial disponibili
        serial_card = ctk.CTkFrame(
            self,
            fg_color=COLORS["panel_alt"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
        )
        serial_card.grid(row=3, column=0, columnspan=4, padx=SPACING["xl"], pady=(0, SPACING["md"]), sticky="ew")
        ctk.CTkLabel(serial_card, text="Serial disponibili", font=font(size=FONT_SIZES["sm"], weight="bold")).grid(
            row=0, column=0, pady=(SPACING["sm"], SPACING["xs"]), sticky="w", padx=SPACING["md"])

        for j, sid in enumerate(serials):
            if sid:
                label = ctk.CTkLabel(serial_card, text=sid, font=font(size=FONT_SIZES["xs"]), text_color=COLORS["text_muted"])
                label.grid(row=1 + j, column=0, sticky="w", padx=SPACING["md"])
                self.serial_labels.append(label)

        refresh_btn = ctk.CTkButton(
            serial_card,
            text="🔄 Rileva sensori",
            font=font(size=FONT_SIZES["sm"]),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_dark"],
            command=self.refresh,
            height=42,
        )
        refresh_btn.grid(row=1 + len(serials), column=0, pady=(SPACING["sm"], SPACING["md"]), padx=SPACING["md"], sticky="w")

        self._build_fake_sensors(4)
        self._build_control_settings(5)
        self._build_diagnostics(6)

    def _build_fake_sensors(self, start_row):
        self.fake_sensor_entries = []
        card = ctk.CTkFrame(
            self,
            fg_color=COLORS["panel_alt"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
        )
        card.grid(row=start_row, column=0, columnspan=4, padx=SPACING["xl"], pady=(0, SPACING["md"]), sticky="ew")
        card.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(
            card,
            text="Sensori fake (test)",
            font=font(size=FONT_SIZES["md"], weight="bold"),
            text_color=COLORS["text"],
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=SPACING["md"], pady=(SPACING["sm"], SPACING["xs"]))

        ctk.CTkLabel(card, text="Nome", font=font(size=FONT_SIZES["sm"])).grid(
            row=1, column=0, padx=SPACING["md"], pady=SPACING["xs"], sticky="w"
        )
        ctk.CTkLabel(card, text="Temperatura (°C)", font=font(size=FONT_SIZES["sm"])).grid(
            row=1, column=1, padx=SPACING["md"], pady=SPACING["xs"], sticky="w"
        )

        fake_map = dict(self.master.settings.get("fake_sensor_temps", {}))
        if not fake_map:
            fake_map = {"Fake_Thermo_18": 18.0}
            self.master.settings["fake_sensor_temps"] = fake_map

        for row_idx, (name, temp) in enumerate(fake_map.items(), start=2):
            name_var = ctk.StringVar(value=str(name))
            temp_var = ctk.StringVar(value=str(temp))
            name_entry = ctk.CTkEntry(card, textvariable=name_var, width=200)
            name_entry.grid(row=row_idx, column=0, padx=SPACING["md"], pady=SPACING["xs"], sticky="w")
            temp_entry = ctk.CTkEntry(card, textvariable=temp_var, width=140)
            temp_entry.grid(row=row_idx, column=1, padx=SPACING["md"], pady=SPACING["xs"], sticky="w")
            self.fake_sensor_entries.append((name_var, temp_var))

        add_btn = ctk.CTkButton(
            card,
            text="Aggiungi sensore fake",
            font=font(size=FONT_SIZES["sm"]),
            fg_color=COLORS["panel_soft"],
            hover_color=COLORS["accent_dark"],
            command=self.add_fake_sensor_row,
            height=42,
        )
        add_btn.grid(row=len(fake_map) + 2, column=0, padx=SPACING["md"], pady=(SPACING["sm"], SPACING["sm"]), sticky="w")

        apply_btn = ctk.CTkButton(
            card,
            text="Applica sensori fake",
            font=font(size=FONT_SIZES["sm"]),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_dark"],
            command=self.apply_fake_sensors,
            height=42,
        )
        apply_btn.grid(row=len(fake_map) + 2, column=1, padx=SPACING["md"], pady=(SPACING["sm"], SPACING["sm"]), sticky="w")

    def _build_control_settings(self, start_row):
        card = ctk.CTkFrame(
            self,
            fg_color=COLORS["panel_alt"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
        )
        card.grid(row=start_row, column=0, columnspan=4, padx=SPACING["xl"], pady=(0, SPACING["md"]), sticky="ew")
        ctk.CTkLabel(
            card,
            text="Controllo automatico",
            font=font(size=FONT_SIZES["md"], weight="bold"),
            text_color=COLORS["text"],
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=SPACING["md"], pady=(SPACING["sm"], SPACING["xs"]))

        self.update_interval_var.set(str(self.master.settings.get("update_interval_s", 5)))
        self.min_switch_interval_var.set(str(self.master.settings.get("min_switch_interval_s", 60)))
        self.save_interval_var.set(str(self.master.settings.get("save_interval_s", 30)))

        ctk.CTkLabel(card, text="Aggiornamento (s):", font=font(size=FONT_SIZES["sm"])).grid(
            row=1, column=0, sticky="e", padx=(SPACING["md"], SPACING["sm"]), pady=SPACING["xs"]
        )
        ctk.CTkEntry(card, textvariable=self.update_interval_var, width=140).grid(
            row=1, column=1, sticky="w", pady=SPACING["xs"]
        )

        ctk.CTkLabel(card, text="Intervallo min switch (s):", font=font(size=FONT_SIZES["sm"])).grid(
            row=2, column=0, sticky="e", padx=(SPACING["md"], SPACING["sm"]), pady=SPACING["xs"]
        )
        ctk.CTkEntry(card, textvariable=self.min_switch_interval_var, width=140).grid(
            row=2, column=1, sticky="w", pady=SPACING["xs"]
        )

        ctk.CTkLabel(card, text="Salvataggio config (s):", font=font(size=FONT_SIZES["sm"])).grid(
            row=3, column=0, sticky="e", padx=(SPACING["md"], SPACING["sm"]), pady=SPACING["xs"]
        )
        ctk.CTkEntry(card, textvariable=self.save_interval_var, width=140).grid(
            row=3, column=1, sticky="w", pady=SPACING["xs"]
        )

        save_btn = ctk.CTkButton(
            card,
            text="Salva impostazioni",
            font=font(size=FONT_SIZES["sm"]),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_dark"],
            command=self.save_timing_settings,
            height=42,
        )
        save_btn.grid(row=4, column=0, padx=SPACING["md"], pady=(SPACING["sm"], SPACING["sm"]), sticky="w")

        self.status_label = ctk.CTkLabel(card, text="", font=font(size=FONT_SIZES["sm"]), text_color=COLORS["text_muted"])
        self.status_label.grid(row=4, column=1, padx=SPACING["sm"], sticky="w")

    def _build_diagnostics(self, start_row):
        card = ctk.CTkFrame(
            self,
            fg_color=COLORS["panel_alt"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
        )
        card.grid(row=start_row, column=0, columnspan=4, padx=SPACING["xl"], pady=(0, SPACING["md"]), sticky="ew")
        ctk.CTkLabel(
            card,
            text="Diagnostica e test installatore",
            font=font(size=FONT_SIZES["md"], weight="bold"),
            text_color=COLORS["text"],
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=SPACING["md"], pady=(SPACING["sm"], SPACING["xs"]))

        test_switch = ctk.CTkSwitch(
            card,
            text="Abilita modalità test (disabilita controllo automatico)",
            variable=self.test_mode_var,
            command=self.toggle_test_mode,
            font=font(size=FONT_SIZES["sm"]),
        )
        test_switch.grid(row=1, column=0, columnspan=3, sticky="w", padx=SPACING["md"], pady=SPACING["xs"])

        sensor_btn = ctk.CTkButton(
            card,
            text="Test sensori",
            font=font(size=FONT_SIZES["sm"]),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_dark"],
            command=self.run_sensor_test,
            height=42,
        )
        sensor_btn.grid(row=2, column=0, padx=SPACING["md"], pady=SPACING["xs"], sticky="w")
        self.test_buttons.append(sensor_btn)

        ctk.CTkLabel(card, text="Test valvola:", font=font(size=FONT_SIZES["sm"])).grid(
            row=2, column=1, sticky="e", padx=(SPACING["sm"], SPACING["xs"])
        )
        barrel_menu = ctk.CTkComboBox(
            card,
            values=list(self.master.botti_data.keys()),
            variable=self.test_barrel_var,
            width=180,
            height=42,
            font=font(size=FONT_SIZES["sm"]),
        )
        barrel_menu.grid(row=2, column=2, sticky="w", padx=SPACING["xs"], pady=SPACING["xs"])

        open_btn = ctk.CTkButton(
            card,
            text="Apri 2s",
            font=font(size=FONT_SIZES["sm"]),
            fg_color=COLORS["warning"],
            hover_color=COLORS["accent_dark"],
            command=lambda: self.run_valve_test("Aperta"),
            height=42,
        )
        open_btn.grid(row=3, column=0, padx=SPACING["md"], pady=SPACING["xs"], sticky="w")
        self.test_buttons.append(open_btn)

        close_btn = ctk.CTkButton(
            card,
            text="Chiudi 2s",
            font=font(size=FONT_SIZES["sm"]),
            fg_color=COLORS["panel_soft"],
            hover_color=COLORS["accent_dark"],
            command=lambda: self.run_valve_test("Chiusa"),
            height=42,
        )
        close_btn.grid(row=3, column=1, padx=SPACING["sm"], pady=SPACING["xs"], sticky="w")
        self.test_buttons.append(close_btn)

        cycle_btn = ctk.CTkButton(
            card,
            text="Ciclo completo",
            font=font(size=FONT_SIZES["sm"]),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_dark"],
            command=self.run_cycle_test,
            height=42,
        )
        cycle_btn.grid(row=3, column=2, padx=SPACING["xs"], pady=SPACING["xs"], sticky="w")
        self.test_buttons.append(cycle_btn)

        self.test_output = ctk.CTkTextbox(
            card,
            width=560,
            height=140,
            fg_color=COLORS["panel_alt"],
            text_color=COLORS["text"],
        )
        self.test_output.grid(row=4, column=0, columnspan=3, padx=SPACING["md"], pady=(SPACING["sm"], SPACING["md"]), sticky="ew")
        self._set_test_controls_state(False)

    def refresh(self):
        self.build_ui()

    def change_assoc(self, botte, var):
        new_serial = var.get() if var.get() else None
        self.master.settings.setdefault('sensors_mapping', {})[botte] = new_serial
        save_config(self.master.botti_data, self.master.settings)
        self.on_mapping_change()
        if new_serial:
            temp = self.sensor_manager.read_temperature_by_serial(new_serial)
        else:
            temp = self.sensor_manager.read_temperature_by_serial("test")
        now = datetime.datetime.now()
        self.master.botti_data[botte]["temperatura"] = temp
        self.master.botti_data[botte].setdefault("history", []).append((now, temp))

    def save_timing_settings(self):
        update_interval = self._parse_int(self.update_interval_var.get(), fallback=5, min_value=2, max_value=60)
        min_switch_interval = self._parse_int(self.min_switch_interval_var.get(), fallback=60, min_value=10, max_value=3600)
        save_interval = self._parse_int(self.save_interval_var.get(), fallback=30, min_value=10, max_value=300)

        self.master.settings["update_interval_s"] = update_interval
        self.master.settings["min_switch_interval_s"] = min_switch_interval
        self.master.settings["save_interval_s"] = save_interval
        save_config(self.master.botti_data, self.master.settings)
        if self.status_label:
            self.status_label.configure(text="Impostazioni salvate ✔")

    def toggle_test_mode(self):
        enabled = bool(self.test_mode_var.get())
        self._set_test_controls_state(enabled)
        if self.on_test_mode_change:
            self.on_test_mode_change(enabled)

    def _set_test_controls_state(self, enabled):
        for btn in self.test_buttons:
            btn.configure(state="normal" if enabled else "disabled")

    def run_sensor_test(self):
        if not self.test_output:
            return
        lines = []
        mapping = self.master.settings.get("sensors_mapping", {})
        for botte in self.master.botti_data.keys():
            serial = mapping.get(botte) or "test"
            temp = self.sensor_manager.read_temperature_by_serial(serial)
            lines.append(f"{botte}: {serial} → {temp:.1f} °C")
        self._write_test_output("Test sensori:\n" + "\n".join(lines))

    def add_fake_sensor_row(self):
        fake_map = dict(self.master.settings.get("fake_sensor_temps", {}))
        index = len(fake_map) + 1
        new_key = f"Fake_Thermo_{18 + index}"
        while new_key in fake_map:
            index += 1
            new_key = f"Fake_Thermo_{18 + index}"
        fake_map[new_key] = 18.0
        self.master.settings["fake_sensor_temps"] = fake_map
        self.build_ui()

    def apply_fake_sensors(self):
        fake_map = {}
        for name_var, temp_var in self.fake_sensor_entries:
            name = name_var.get().strip()
            if not name:
                continue
            try:
                temp = float(temp_var.get())
            except ValueError:
                continue
            fake_map[name] = temp
        if not fake_map:
            return
        self.master.settings["fake_sensor_temps"] = fake_map
        self.master.apply_fake_sensor_temps(fake_map)
        save_config(self.master.botti_data, self.master.settings)
        serials = self.sensor_manager.rescan_serials() or [""]
        if "test" not in serials:
            serials.insert(0, "test")
        for botte, cb in self.combo_widgets.items():
            cb.configure(values=serials)

    def run_valve_test(self, state):
        botte = self.test_barrel_var.get()
        if not botte:
            return
        self._write_test_output(f"Test valvola {botte}: {state} per 2s...")
        thread = threading.Thread(target=self._pulse_valve, args=(botte, state))
        thread.daemon = True
        thread.start()

    def run_cycle_test(self):
        botte = self.test_barrel_var.get()
        if not botte:
            return
        self._write_test_output(f"Ciclo completo per {botte} (Apri → Chiudi)...")
        thread = threading.Thread(target=self._cycle_valve, args=(botte,))
        thread.daemon = True
        thread.start()

    def _pulse_valve(self, botte, state):
        try:
            actuator = self.actuators[botte]
            actuator.pulse_valve(state, seconds=2)
            self._write_test_output(f"Test valvola {botte} completato.")
        except Exception as exc:
            self._write_test_output(f"Errore test valvola {botte}: {exc}")

    def _cycle_valve(self, botte):
        try:
            actuator = self.actuators[botte]
            actuator.pulse_valve("Aperta", seconds=2)
            actuator.pulse_valve("Chiusa", seconds=2)
            self._write_test_output(f"Ciclo completo {botte} completato.")
        except Exception as exc:
            self._write_test_output(f"Errore ciclo valvola {botte}: {exc}")

    def _write_test_output(self, message):
        if not self.test_output:
            return
        def update_text():
            self.test_output.delete("1.0", "end")
            self.test_output.insert("end", message)

        self.after(0, update_text)

    @staticmethod
    def _parse_int(value, fallback=0, min_value=None, max_value=None):
        try:
            parsed = int(float(value))
        except (TypeError, ValueError):
            parsed = fallback
        if min_value is not None:
            parsed = max(parsed, min_value)
        if max_value is not None:
            parsed = min(parsed, max_value)
        return parsed
