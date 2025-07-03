import customtkinter as ctk

from ControllerBotti.config import save_config


class SettingsTab(ctk.CTkFrame):
    def __init__(self, master, sensor_manager, on_mapping_change, **kwargs):
        super().__init__(master, fg_color="#202d16", **kwargs)
        self.sensor_manager = sensor_manager
        self.on_mapping_change = on_mapping_change
        self.combo_vars = {}

        ctk.CTkLabel(self, text="Associa ogni botte a una sonda:", font=ctk.CTkFont(size=19, weight="bold")).grid(
            row=0, column=0, columnspan=3, pady=18, padx=10, sticky="w")

        serials = self.sensor_manager.rescan_serials() or [""]
        botti = list(self.master.botti_data.keys())

        for i, botte in enumerate(botti):
            ctk.CTkLabel(self, text=f"{botte}:", width=90, anchor="e", font=ctk.CTkFont(size=16)).grid(
                row=1+i, column=0, padx=(10, 8), pady=6, sticky="e")
            selected_serial = self.master.settings.get("sensors_mapping", {}).get(botte, "")
            var = ctk.StringVar(value=selected_serial)
            cb = ctk.CTkComboBox(
                self, values=serials, variable=var, width=240, font=ctk.CTkFont(size=15),
                command=lambda _, b=botte, v=var: self.change_assoc(b, v)
            )
            cb.grid(row=1+i, column=1, padx=(0, 20), pady=6, sticky="w")
            self.combo_vars[botte] = var

        # Titolo per serial disponibili
        offset = 1 + len(botti)
        ctk.CTkLabel(self, text="Serial disponibili:", font=ctk.CTkFont(size=14)).grid(
            row=offset, column=0, columnspan=2, pady=(30, 5), sticky="w", padx=10)
        for j, sid in enumerate(serials):
            if sid:
                ctk.CTkLabel(self, text=sid, font=ctk.CTkFont(size=13), text_color="#94bfb6").grid(
                    row=offset+1+j, column=0, columnspan=2, sticky="w", padx=30)

        refresh_button = ctk.CTkButton(
            self, text="🔄 Rileva sensori", font=ctk.CTkFont(size=14),
            command=self.refresh_sensor_list
        )
        refresh_button.grid(row=offset + len(serials) + 2, column=0, pady=(30, 10), padx=10, sticky="w")

    def refresh_sensor_list(self):
        serials = self.sensor_manager.rescan_serials() or [""]
        # Aggiorna tutte le combo box
        for botte, var in self.combo_vars.items():
            current_value = var.get()
            combo_box = var._variable._tk.globalgetvar(var._name)  # workaround
            var.set(current_value if current_value in serials else "")
            # You may need to recreate combo boxes if they can't update values dynamically
        # TODO: Ricostruire la GUI o le combo se serve
        print("Sonde aggiornate:", serials)

    def change_assoc(self, botte, var):
        new_serial = var.get() if var.get() else None
        self.master.settings.setdefault('sensors_mapping', {})[botte] = new_serial
        save_config(self.master.botti_data, self.master.settings)
        self.on_mapping_change()
