import customtkinter as ctk
from PIL import Image

class OverviewFrame(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color="#191919", **kwargs)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Usa la NUOVA immagine appena caricata
        barrel_img_path = "assets/barrel.png"

        FRAME_W = 380
        FRAME_H = 480
        IMG_W = 250
        IMG_H = 340

        barrel_img_pil = Image.open(barrel_img_path).resize((IMG_W, IMG_H), Image.LANCZOS)
        barrel_ctk_img = ctk.CTkImage(light_image=barrel_img_pil, dark_image=barrel_img_pil, size=(IMG_W, IMG_H))

        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.grid(row=0, column=0, padx=20, pady=22, sticky="nsew")
        center_frame.grid_columnconfigure((0, 1, 2), weight=1)
        center_frame.grid_rowconfigure(0, weight=1)

        self.botte_widgets = {}
        for idx, nome in enumerate(app.botti_data):
            b = app.botti_data[nome]
            # Frame bordo verde scuro (più grande della barrel)
            bg_frame = ctk.CTkFrame(center_frame, width=FRAME_W, height=FRAME_H, corner_radius=48, fg_color="#232a20")
            bg_frame.grid(row=0, column=idx, padx=18, pady=8, sticky="n")
            bg_frame.grid_propagate(False)

            # Immagine barrel centrata (meglio anchor=center)
            border_lbl = ctk.CTkLabel(bg_frame, image=barrel_ctk_img, text="", fg_color="transparent")
            border_lbl.place(relx=0.5, rely=0.5, anchor="center")

            # Dati sopra
            dot = ctk.CTkLabel(bg_frame, text="●", font=ctk.CTkFont(size=44), text_color="white", fg_color="transparent")
            dot.place(relx=0.5, rely=0.17, anchor="center")

            temp_lbl = ctk.CTkLabel(
                bg_frame,
                text=f"{b['temperatura']:.1f} °C",
                font=ctk.CTkFont(size=36, weight="bold"),
                text_color="white",
                fg_color="transparent"
            )
            temp_lbl.place(relx=0.5, rely=0.29, anchor="center")

            valve_lbl = ctk.CTkLabel(
                bg_frame,
                text=f"Valvola: {b['valvola']}",
                font=ctk.CTkFont(size=25),
                text_color="white",
                fg_color="transparent"
            )
            valve_lbl.place(relx=0.5, rely=0.40, anchor="center")

            img_lock = Image.open("assets/lock.png").resize((32, 32))
            lock_icon = ctk.CTkImage(light_image=img_lock, dark_image=img_lock)
            lock_lbl = ctk.CTkLabel(bg_frame, image=None, text="", width=34, fg_color="transparent")
            lock_lbl.place(relx=0.5, rely=0.50, anchor="center")

            min_lbl = ctk.CTkLabel(
                bg_frame,
                text=f"{b['min_temp']:.1f}",
                font=ctk.CTkFont(size=22, weight="bold"),
                text_color="blue",
                fg_color="#000000",
                corner_radius=9,
                width=62,
                height=40,
                anchor="center",
                justify="center"
            )
            min_lbl.place(relx=0.18, rely=0.95, anchor="center")

            max_lbl = ctk.CTkLabel(
                bg_frame,
                text=f"{b['max_temp']:.1f}",
                font=ctk.CTkFont(size=22, weight="bold"),
                text_color="red",
                fg_color="#000000",
                corner_radius=9,
                width=62,
                height=40,
                anchor="center",
                justify="center"
            )
            max_lbl.place(relx=0.82, rely=0.95, anchor="center")

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
                widgets["dot"].configure(text_color="#459bed")
            elif temp > b["max_temp"]:
                widgets["dot"].configure(text_color="#ed4747")
            else:
                widgets["dot"].configure(text_color="#6ddb57")
            widgets["temp"].configure(text=f"{temp:.1f} °C")
            widgets["valve"].configure(text=f"Valvola: {b['valvola']}")
            widgets["min"].configure(text=f"{b['min_temp']:.1f}")
            widgets["max"].configure(text=f"{b['max_temp']:.1f}")

            # Mostra lucchetto se forzata
            show_lock = b.get("forced") in ("Aperta", "Chiusa")
            if show_lock:
                widgets["lock"].configure(image=widgets["lock_icon"])
            else:
                widgets["lock"].configure(image=None)
