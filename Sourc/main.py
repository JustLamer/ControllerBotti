import tkinter as tk
from tkinter import ttk

# Dati iniziali delle botti
botti_data = {
    "Botte 1": {"temperatura": 18.5, "valvola": "Chiusa", "min_temp": 17.0, "max_temp": 20.0},
    "Botte 2": {"temperatura": 20.0, "valvola": "Aperta", "min_temp": 18.0, "max_temp": 21.0},
    "Botte 3": {"temperatura": 19.2, "valvola": "Chiusa", "min_temp": 16.5, "max_temp": 19.5},
}

# Impostazioni generali (puoi salvarle su file più avanti)
impostazioni_generali = {
    "step_temp": 0.1
}

def mostra_dettagli(nome_botte):
    dettaglio = tk.Toplevel()
    dettaglio.title(f"Dettagli {nome_botte}")
    ttk.Label(dettaglio, text=f"Dettagli per {nome_botte}").pack(padx=20, pady=20)

def aggiorna_valore(label, nome_botte, tipo, direzione):
    step = impostazioni_generali["step_temp"]
    botti_data[nome_botte][tipo] += step * direzione
    nuovo_valore = round(botti_data[nome_botte][tipo], 1)
    botti_data[nome_botte][tipo] = nuovo_valore
    label.config(text=f"{nuovo_valore} °C")

def cambia_step_temp(event):
    valore = float(step_combo.get())
    impostazioni_generali["step_temp"] = valore
    print(f"Step temperatura aggiornato: {valore}°C")

# GUI principale
root = tk.Tk()
root.title("Controllo Botti")
root.geometry("1050x600")

# --- Impostazioni generali ---
impostazioni_frame = ttk.LabelFrame(root, text="⚙️ Impostazioni Generali", padding=10)
impostazioni_frame.pack(pady=10, fill=tk.X)

ttk.Label(impostazioni_frame, text="Step variazione temperatura (°C):", font=("Helvetica", 12)).pack(side=tk.LEFT, padx=(10, 5))

step_combo = ttk.Combobox(impostazioni_frame, values=[0.1, 0.2, 0.5, 1.0], width=5, state="readonly")
step_combo.set(impostazioni_generali["step_temp"])
step_combo.pack(side=tk.LEFT)
step_combo.bind("<<ComboboxSelected>>", cambia_step_temp)

# --- Titolo ---
ttk.Label(root, text="Situazione Botti", font=("Helvetica", 24)).pack(pady=10)

# --- Contenitore delle botti ---
container = ttk.Frame(root)
container.pack()

for nome_botte, dati in botti_data.items():
    frame = ttk.LabelFrame(container, text=nome_botte, padding=20)
    frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)

    ttk.Label(frame, text=f"Temperatura attuale: {dati['temperatura']}°C", font=("Helvetica", 14)).pack(pady=5)
    ttk.Label(frame, text=f"Valvola: {dati['valvola']}", font=("Helvetica", 14)).pack(pady=5)

    # --- Temp. Min ---
    ttk.Label(frame, text="Temperatura minima:", font=("Helvetica", 12)).pack(pady=(10, 0))
    min_label = ttk.Label(frame, text=f"{dati['min_temp']} °C", font=("Helvetica", 14))
    min_label.pack()

    min_controls = ttk.Frame(frame)
    min_controls.pack()
    ttk.Button(min_controls, text="−", width=3, command=lambda l=min_label, n=nome_botte: aggiorna_valore(l, n, "min_temp", -1)).pack(side=tk.LEFT, padx=2)
    ttk.Button(min_controls, text="+", width=3, command=lambda l=min_label, n=nome_botte: aggiorna_valore(l, n, "min_temp", +1)).pack(side=tk.LEFT, padx=2)

    # --- Temp. Max ---
    ttk.Label(frame, text="Temperatura massima:", font=("Helvetica", 12)).pack(pady=(10, 0))
    max_label = ttk.Label(frame, text=f"{dati['max_temp']} °C", font=("Helvetica", 14))
    max_label.pack()

    max_controls = ttk.Frame(frame)
    max_controls.pack()
    ttk.Button(max_controls, text="−", width=3, command=lambda l=max_label, n=nome_botte: aggiorna_valore(l, n, "max_temp", -1)).pack(side=tk.LEFT, padx=2)
    ttk.Button(max_controls, text="+", width=3, command=lambda l=max_label, n=nome_botte: aggiorna_valore(l, n, "max_temp", +1)).pack(side=tk.LEFT, padx=2)

    ttk.Button(frame, text="Dettagli", command=lambda nome=nome_botte: mostra_dettagli(nome)).pack(pady=10)

root.mainloop()
