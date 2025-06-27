import customtkinter as ctk
from PIL import Image
import os

class OverviewFrame(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color="#252c26", **kwargs)
        self.app = app
        self.botti_data = app.botti_data

        # Immagine lucchetto
        lock_path = os.path.join("assets", "lock.png")
        lock_img = Image.open(lock_path).resize((28,28))
        self.lock_icon = ctk.CTkImage(light_image=lock_img, dark_image=lock_img)

        # Layout: centro, un riquadro per botte
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        center = ctk.CTkFrame(self, fg_color="transparent")
        center.grid(row=0, column=0, sticky="nsew")

        # Mostra tutte le botti centrati
        self.boxes = {}
        frame = ctk.CTkFrame(center, fg_color="transparent")
        frame.pack(expand=True, pady=32)
        for nome in self.botti_data:
            box = ctk.CTkFrame(frame, fg_color="#233b26", corner_radius=19, width=260, height=360)
            box.pack(side="left", padx=30, pady=8, expand=False)
            box.pack_propagate(False)
            # Immagine barrel
            img_label = ctk.CTkLabel(box, image=app.barrel_img, text="")
            img_label.pack(pady=(16, 6))
            # Stato dot
            self.boxes[nome] = {}
            self.boxes[nome]["dot"] = ctk.CTkLabel(box, text="●", font=ctk.CTkFont(size=37), text_color="#6ddb57")
            self.boxes[nome]["dot"].pack()
            # Temperatura
            self.boxes[nome]["temp"] = ctk.CTkLabel(box, text="", font=ctk.CTkFont(size=28, weight="bold"))
            self.boxes[nome]["temp"].pack(pady=4)
            # Valvola
            self.boxes[nome]["valve"] = ctk.CTkLabel(box, text="", font=ctk.CTkFont(size=23))
            self.boxes[nome]["valve"].pack(pady=(0, 2))
            # Lucchetto solo se forced
            self.boxes[nome]["lock"] = ctk.CTkLabel(box, image=None, text="", width=32)
            self.boxes[nome]["lock"].pack(pady=3)
            # Soglie min/max
            soglie_frame = ctk.CTkFrame(box, fg_color="transparent")
            soglie_frame.pack(pady=(10,0))
            self.boxes[nome]["min"] = ctk.CTkLabel(soglie_frame, text="", font=ctk.CTkFont(size=16), text_color="blue")
            self.boxes[nome]["min"].pack(side="left", padx=(0,10))
            self.boxes[nome]["max"] = ctk.CTkLabel(soglie_frame, text="", font=ctk.CTkFont(size=16), text_color="red")
            self.boxes[nome]["max"].pack(side="left", padx=(10,0))

        self.refresh()

    def refresh(self):
        # Aggiorna tutti i widget panoramica
        for nome, box in self.boxes.items():
            b = self.botti_data[nome]
            t = b["temperatura"]
            # Stato dot
            if t < b["min_temp"]:
                color = "#459bed"
            elif t > b["max_temp"]:
                color = "#ed4747"
            else:
                color = "#6ddb57"
            box["dot"].configure(text_color=color)
            box["temp"].configure(text=f"{t:.1f} °C")
            # Stato valvola
            stato_valvola = b["valvola"] if b["valvola"] in ("Aperta","Chiusa") else "Chiusa"
            box["valve"].configure(text=f"Valvola: {stato_valvola}")
            # Lucchetto solo se forzata
            if b.get("forced") in ("Aperta", "Chiusa"):
                box["lock"].configure(image=self.lock_icon)
            else:
                box["lock"].configure(image=None)
            # Soglie
            box["min"].configure(text=f"Min: {b['min_temp']:.1f}")
            box["max"].configure(text=f"Max: {b['max_temp']:.1f}")
