import customtkinter as ctk
from PIL import Image
from numpy.random import random


class OverviewFrame(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color="#191919", **kwargs)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        barrel_img_path = "assets/barrel.png"

        FRAME_W = 150
        FRAME_H = 210
        IMG_W = 115
        IMG_H = 160

        barrel_img_pil = Image.open(barrel_img_path).resize((IMG_W, IMG_H), Image.LANCZOS)
        barrel_ctk_img = ctk.CTkImage(light_image=barrel_img_pil, dark_image=barrel_img_pil, size=(IMG_W, IMG_H))

        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.grid(row=0, column=0, padx=5, pady=10, sticky="nsew")
        center_frame.grid_columnconfigure((0, 1, 2), weight=0)
        center_frame.grid_rowconfigure(0, weight=1)

        self.botte_widgets = {}
        for idx, nome in enumerate(app.botti_data):
            b = app.botti_data[nome]

            # Frame bordo verde scuro (più piccolo)
            bg_frame = ctk.CTkFrame(center_frame, width=FRAME_W, height=FRAME_H, corner_radius=20, fg_color="#232a20")
            bg_frame.grid(row=0, column=idx, padx=2, pady=2, sticky="n")
            bg_frame.grid_propagate(False)

            # Immagine barrel
            border_lbl = ctk.CTkLabel(bg_frame, image=barrel_ctk_img, text="", fg_color="transparent")
            border_lbl.place(relx=0.5, rely=0.5, anchor="center")

            # Dati sopra
            dot = ctk.CTkLabel(bg_frame, text="●", font=ctk.CTkFont(size=24), text_color="white", fg_color="transparent")
            dot.place(relx=0.5, rely=0.15, anchor="center")

            temp_lbl = ctk.CTkLabel(
                bg_frame,
                text=f"{b['temperatura']:.1f} °C",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="white",
                fg_color="transparent"
            )
            temp_lbl.place(relx=0.5, rely=0.26, anchor="center")

            valve_lbl = ctk.CTkLabel(
                bg_frame,
                text=f"Valvola: {b['valvola']}",
                font=ctk.CTkFont(size=12),
                text_color="white",
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
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="blue",
                fg_color="#000000",
                corner_radius=6,
                width=36,
                height=22,
                anchor="center",
                justify="center"
            )
            min_lbl.place(relx=0.18, rely=0.93, anchor="center")

            max_lbl = ctk.CTkLabel(
                bg_frame,
                text=f"{b['max_temp']:.1f}",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="red",
                fg_color="#000000",
                corner_radius=6,
                width=36,
                height=22,
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

            # Nuova logica: ottieni temperatura da SensorManager
            serial = self.app.settings.get("sensors_mapping", {}).get(nome, "test")
            temp = self.app.sensor_manager.read_temperature_by_serial(serial)

            b["temperatura"] = temp

            if temp < b["min_temp"]:
                widgets["dot"].configure(text_color="#459bed")
            elif temp > b["max_temp"]:
                widgets["dot"].configure(text_color="#ed4747")
            else:
                widgets["dot"].configure(text_color="#6ddb57")
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
