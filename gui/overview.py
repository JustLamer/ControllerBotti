import customtkinter as ctk
from PIL import Image
from gui.theme import COLORS, font


class OverviewFrame(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color=COLORS["bg"], **kwargs)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        barrel_img_path = "assets/barrel.png"

        FRAME_W = 190
        FRAME_H = 230
        IMG_W = 125
        IMG_H = 170

        barrel_img_pil = Image.open(barrel_img_path).resize((IMG_W, IMG_H), Image.LANCZOS)
        barrel_ctk_img = ctk.CTkImage(light_image=barrel_img_pil, dark_image=barrel_img_pil, size=(IMG_W, IMG_H))

        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.grid(row=0, column=0, padx=10, pady=14, sticky="nsew")
        center_frame.grid_columnconfigure((0, 1, 2), weight=0)
        center_frame.grid_rowconfigure(0, weight=1)

        self.botte_widgets = {}
        for idx, nome in enumerate(app.botti_data):
            b = app.botti_data[nome]

            # Frame bordo verde scuro (più piccolo)
            bg_frame = ctk.CTkFrame(
                center_frame,
                width=FRAME_W,
                height=FRAME_H,
                corner_radius=18,
                fg_color=COLORS["panel_alt"],
            )
            bg_frame.grid(row=0, column=idx, padx=6, pady=6, sticky="n")
            bg_frame.grid_propagate(False)

            # Immagine barrel
            border_lbl = ctk.CTkLabel(bg_frame, image=barrel_ctk_img, text="", fg_color="transparent")
            border_lbl.place(relx=0.5, rely=0.5, anchor="center")

            # Dati sopra
            dot = ctk.CTkLabel(
                bg_frame,
                text="●",
                font=font(size=24),
                text_color=COLORS["text"],
                fg_color="transparent",
            )
            dot.place(relx=0.5, rely=0.15, anchor="center")

            temp_lbl = ctk.CTkLabel(
                bg_frame,
                text=f"{b['temperatura']:.1f} °C",
                font=font(size=20, weight="bold"),
                text_color=COLORS["text"],
                fg_color="transparent"
            )
            temp_lbl.place(relx=0.5, rely=0.26, anchor="center")

            valve_lbl = ctk.CTkLabel(
                bg_frame,
                text=f"Valvola: {b['valvola']}",
                font=font(size=12),
                text_color=COLORS["text_muted"],
                fg_color="transparent"
            )
            valve_lbl.place(relx=0.5, rely=0.37, anchor="center")

            img_lock = Image.open("assets/lock.png").resize((18, 18))
            lock_icon = ctk.CTkImage(light_image=img_lock, dark_image=img_lock)
            lock_lbl = ctk.CTkLabel(bg_frame, image=None, text="", width=18, fg_color="transparent")
            lock_lbl.place(relx=0.5, rely=0.49, anchor="center")

            min_lbl = ctk.CTkLabel(
                bg_frame,
                text=f"{b['min_temp']:.1f}",
                font=font(size=10, weight="bold"),
                text_color=COLORS["info"],
                fg_color=COLORS["panel_soft"],
                corner_radius=8,
                width=42,
                height=24,
                anchor="center",
                justify="center"
            )
            min_lbl.place(relx=0.18, rely=0.93, anchor="center")

            max_lbl = ctk.CTkLabel(
                bg_frame,
                text=f"{b['max_temp']:.1f}",
                font=font(size=10, weight="bold"),
                text_color=COLORS["danger"],
                fg_color=COLORS["panel_soft"],
                corner_radius=8,
                width=42,
                height=24,
                anchor="center",
                justify="center"
            )
            max_lbl.place(relx=0.82, rely=0.93, anchor="center")

            self.botte_widgets[nome] = {
                "dot": dot,
                "temp": temp_lbl,
                "valve": valve_lbl,
                "min": min_lbl,
                "max": max_lbl,
                "lock": lock_lbl,
                "lock_icon": lock_icon
            }

        self.refresh()

    def refresh(self):
        for nome, b in self.app.botti_data.items():
            widgets = self.botte_widgets[nome]

            temp = b["temperatura"]

            if temp < b["min_temp"]:
                widgets["dot"].configure(text_color=COLORS["info"])
            elif temp > b["max_temp"]:
                widgets["dot"].configure(text_color=COLORS["danger"])
            else:
                widgets["dot"].configure(text_color=COLORS["success"])
            widgets["temp"].configure(text=f"{temp:.1f} °C")
            widgets["valve"].configure(text=f"Valvola: {b['valvola']}")
            widgets["min"].configure(text=f"{b['min_temp']:.1f}")
            widgets["max"].configure(text=f"{b['max_temp']:.1f}")

            show_lock = b.get("forced") in ("Aperta", "Chiusa")
            if show_lock:
                widgets["lock"].configure(image=widgets["lock_icon"])
                widgets["lock"].place(relx=0.5, rely=0.49, anchor="center")
            else:
                widgets["lock"].configure(image=None)
                widgets["lock"].place_forget()
