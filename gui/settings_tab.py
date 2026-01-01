import customtkinter as ctk
import threading
from config import save_config
from gui.theme import COLORS, font

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

        self.build_ui()

    def build_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self,
            text="Impostazioni e associazioni",
            font=font(size=20, weight="bold"),
            text_color=COLORS["text"],
        ).grid(row=0, column=0, columnspan=4, pady=(18, 8), padx=14, sticky="w")

        serials = self.sensor_manager.rescan_serials() or [""]
        if "test" not in serials:
            serials.insert(0, "test")
        if not serials:
            serials = [""]
        botti = list(self.master.botti_data.keys())
        if botti:
            self.test_barrel_var.set(botti[0])

        for i, botte in enumerate(botti):
            ctk.CTkLabel(self, text=f"{botte}:", width=90, anchor="e", font=font(size=14)).grid(
                row=1 + i, column=0, padx=(14, 8), pady=6, sticky="e")
            selected_serial = self.master.settings.get("sensors_mapping", {}).get(botte, "")
            var = ctk.StringVar(value=selected_serial)
            cb = ctk.CTkComboBox(
                self, values=serials, variable=var, width=240, font=font(size=14),
                command=lambda _, b=botte, v=var: self.change_assoc(b, v)
            )
            cb.grid(row=1 + i, column=1, padx=(0, 20), pady=6, sticky="w")
            self.combo_vars[botte] = var
            self.combo_widgets[botte] = cb

        # Titolo e serial disponibili
        offset = 1 + len(botti)
        ctk.CTkLabel(self, text="Serial disponibili:", font=font(size=13)).grid(
            row=offset, column=0, columnspan=2, pady=(22, 4), sticky="w", padx=14)

        for j, sid in enumerate(serials):
            if sid:
                label = ctk.CTkLabel(self, text=sid, font=font(size=12), text_color=COLORS["text_muted"])
                label.grid(row=offset + 1 + j, column=0, columnspan=2, sticky="w", padx=26)
                self.serial_labels.append(label)

        # Bottone di refresh
        refresh_btn = ctk.CTkButton(
            self,
            text="🔄 Rileva sensori",
            font=font(size=13),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_dark"],
            command=self.refresh,
        )
        refresh_btn.grid(row=offset + len(serials) + 2, column=0, pady=(20, 10), padx=14, sticky="w")

        self._build_control_settings(offset + len(serials) + 3)
        self._build_diagnostics(offset + len(serials) + 7)

    def _build_control_settings(self, start_row):
        ctk.CTkLabel(
            self,
            text="Controllo automatico",
            font=font(size=16, weight="bold"),
            text_color=COLORS["text"],
        ).grid(row=start_row, column=0, columnspan=3, sticky="w", padx=14, pady=(16, 8))

        self.update_interval_var.set(str(self.master.settings.get("update_interval_s", 5)))
        self.min_switch_interval_var.set(str(self.master.settings.get("min_switch_interval_s", 60)))
        self.save_interval_var.set(str(self.master.settings.get("save_interval_s", 30)))

        ctk.CTkLabel(self, text="Aggiornamento (s):", font=font(size=12)).grid(
            row=start_row + 1, column=0, sticky="e", padx=(14, 6), pady=4
        )
        ctk.CTkEntry(self, textvariable=self.update_interval_var, width=70).grid(
            row=start_row + 1, column=1, sticky="w", pady=4
        )

        ctk.CTkLabel(self, text="Intervallo min switch (s):", font=font(size=12)).grid(
            row=start_row + 2, column=0, sticky="e", padx=(14, 6), pady=4
        )
        ctk.CTkEntry(self, textvariable=self.min_switch_interval_var, width=70).grid(
            row=start_row + 2, column=1, sticky="w", pady=4
        )

        ctk.CTkLabel(self, text="Salvataggio config (s):", font=font(size=12)).grid(
            row=start_row + 3, column=0, sticky="e", padx=(14, 6), pady=4
        )
        ctk.CTkEntry(self, textvariable=self.save_interval_var, width=70).grid(
            row=start_row + 3, column=1, sticky="w", pady=4
        )

        save_btn = ctk.CTkButton(
            self,
            text="Salva impostazioni",
            font=font(size=12),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_dark"],
            command=self.save_timing_settings,
        )
        save_btn.grid(row=start_row + 4, column=0, padx=14, pady=(8, 4), sticky="w")

        self.status_label = ctk.CTkLabel(self, text="", font=font(size=11), text_color=COLORS["text_muted"])
        self.status_label.grid(row=start_row + 4, column=1, padx=6, sticky="w")

    def _build_diagnostics(self, start_row):
        ctk.CTkLabel(
            self,
            text="Diagnostica e test installatore",
            font=font(size=16, weight="bold"),
            text_color=COLORS["text"],
        ).grid(row=start_row, column=0, columnspan=3, sticky="w", padx=14, pady=(16, 6))

        test_switch = ctk.CTkSwitch(
            self,
            text="Abilita modalità test (disabilita controllo automatico)",
            variable=self.test_mode_var,
            command=self.toggle_test_mode,
            font=font(size=12),
        )
        test_switch.grid(row=start_row + 1, column=0, columnspan=3, sticky="w", padx=14, pady=4)

        sensor_btn = ctk.CTkButton(
            self,
            text="Test sensori",
            font=font(size=12),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_dark"],
            command=self.run_sensor_test,
        )
        sensor_btn.grid(row=start_row + 2, column=0, padx=14, pady=4, sticky="w")
        self.test_buttons.append(sensor_btn)

        ctk.CTkLabel(self, text="Test valvola:", font=font(size=12)).grid(
            row=start_row + 2, column=1, sticky="e", padx=(6, 4)
        )
        barrel_menu = ctk.CTkComboBox(
            self,
            values=list(self.master.botti_data.keys()),
            variable=self.test_barrel_var,
            width=140,
            font=font(size=12),
        )
        barrel_menu.grid(row=start_row + 2, column=2, sticky="w", padx=4, pady=4)

        open_btn = ctk.CTkButton(
            self,
            text="Apri 2s",
            font=font(size=12),
            fg_color=COLORS["warning"],
            hover_color=COLORS["accent_dark"],
            command=lambda: self.run_valve_test("Aperta"),
        )
        open_btn.grid(row=start_row + 3, column=0, padx=14, pady=4, sticky="w")
        self.test_buttons.append(open_btn)

        close_btn = ctk.CTkButton(
            self,
            text="Chiudi 2s",
            font=font(size=12),
            fg_color=COLORS["panel_soft"],
            hover_color=COLORS["accent_dark"],
            command=lambda: self.run_valve_test("Chiusa"),
        )
        close_btn.grid(row=start_row + 3, column=1, padx=6, pady=4, sticky="w")
        self.test_buttons.append(close_btn)

        cycle_btn = ctk.CTkButton(
            self,
            text="Ciclo completo",
            font=font(size=12),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_dark"],
            command=self.run_cycle_test,
        )
        cycle_btn.grid(row=start_row + 3, column=2, padx=4, pady=4, sticky="w")
        self.test_buttons.append(cycle_btn)

        self.test_output = ctk.CTkTextbox(
            self,
            width=520,
            height=110,
            fg_color=COLORS["panel_alt"],
            text_color=COLORS["text"],
        )
        self.test_output.grid(row=start_row + 4, column=0, columnspan=3, padx=14, pady=(8, 12), sticky="ew")
        self._set_test_controls_state(False)

    def refresh(self):
        self.build_ui()

    def change_assoc(self, botte, var):
        new_serial = var.get() if var.get() else None
        self.master.settings.setdefault('sensors_mapping', {})[botte] = new_serial
        save_config(self.master.botti_data, self.master.settings)
        self.on_mapping_change()

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
