import customtkinter as ctk

class OverviewFrame(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color="#202d16", **kwargs)
        self.app = app
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.card_widgets = {}
        self._build_ui()

    def _build_ui(self):
        from PIL import Image
        botti = list(self.app.botti_data.keys())
        for i, nome in enumerate(botti):
            b = self.app.botti_data[nome]
            card = ctk.CTkFrame(self, width=340, height=280, corner_radius=24, fg_color="#293f23")
            card.grid(row=0, column=i, padx=30, pady=32, sticky="n")
            card.grid_propagate(False)
            img = self.app.barrel_img
            img_lbl = ctk.CTkLabel(card, image=img, text="", width=90, height=90)
            img_lbl.pack(pady=(17, 7))
            title = ctk.CTkLabel(card, text=nome, font=ctk.CTkFont(size=28, weight="bold"))
            title.pack()
            self.card_widgets[nome] = {}

            # Dot
            dot = ctk.CTkLabel(card, text="●", font=ctk.CTkFont(size=42), text_color="#6ddb57")
            dot.pack(pady=(3, 0))
            self.card_widgets[nome]["dot"] = dot

            temp_lbl = ctk.CTkLabel(card, text="Temp: --°C", font=ctk.CTkFont(size=32, weight="bold"))
            temp_lbl.pack(pady=(9, 0))
            self.card_widgets[nome]["temp"] = temp_lbl

            valve_lbl = ctk.CTkLabel(card, text="Valvola: --", font=ctk.CTkFont(size=27))
            valve_lbl.pack(pady=(6, 0))
            self.card_widgets[nome]["valve"] = valve_lbl

            min_lbl = ctk.CTkLabel(card, text="Min: --°C", font=ctk.CTkFont(size=22), text_color="blue")
            min_lbl.pack(side="left", anchor="w", padx=(28, 0), pady=(13, 0))
            max_lbl = ctk.CTkLabel(card, text="Max: --°C", font=ctk.CTkFont(size=22), text_color="red")
            max_lbl.pack(side="right", anchor="e", padx=(0, 28), pady=(13, 0))
            self.card_widgets[nome]["min"] = min_lbl
            self.card_widgets[nome]["max"] = max_lbl

            lock_lbl = ctk.CTkLabel(card, image=None, text="", width=36)
            lock_lbl.pack(pady=(0, 2))
            self.card_widgets[nome]["lock"] = lock_lbl

    def refresh(self):
        for nome, widgets in self.card_widgets.items():
            b = self.app.botti_data[nome]
            temp = b["temperatura"]
            widgets["temp"].configure(text=f"Temp: {temp:.1f}°C")
            widgets["valve"].configure(text=f"Valvola: {b['valvola']}")
            widgets["min"].configure(text=f"Min: {b['min_temp']:.1f}°C")
            widgets["max"].configure(text=f"Max: {b['max_temp']:.1f}°C")
            if temp < b["min_temp"]:
                color = "#459bed"
            elif temp > b["max_temp"]:
                color = "#ed4747"
            else:
                color = "#6ddb57"
            widgets["dot"].configure(text_color=color)
            forced = b.get("forced")
            try:
                from PIL import Image
                if forced in ("Aperta", "Chiusa"):
                    img = Image.open("assets/lock.png").resize((32, 32))
                    widgets["lock"].configure(image=ctk.CTkImage(light_image=img, dark_image=img))
                else:
                    widgets["lock"].configure(image=None)
            except Exception:
                widgets["lock"].configure(image=None)
