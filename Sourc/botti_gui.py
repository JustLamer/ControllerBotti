import tkinter as tk
from tkinter import ttk
import random, json, os, datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from PIL import Image, ImageTk

# --- Configurazioni iniziali ---
SALVATAGGIO_FILE = "botti_config.json"
BARREL_IMAGE_PATH = "barrel.png"

# --- Dati iniziali ---
default_botti_data = {
    "Botte 1": {"temperatura": 18.5, "valvola": "Auto", "forced": None, "min_temp": 17.0, "max_temp": 20.0},
    "Botte 2": {"temperatura": 20.0, "valvola": "Auto", "forced": None, "min_temp": 18.0, "max_temp": 21.0},
    "Botte 3": {"temperatura": 19.2, "valvola": "Auto", "forced": None, "min_temp": 16.5, "max_temp": 19.5},
}
default_impostazioni = {"step_temp": 0.1, "theme": "Light"}

# --- Setup GUI ---
app = tk.Tk()
app.title("Controllo Botti")
app.geometry("1280x900")

# Carica e ridimensiona immagine barile
original_img = Image.open(BARREL_IMAGE_PATH)
resized_img = original_img.resize((200, 200), Image.LANCZOS)
app.barrel_img = ImageTk.PhotoImage(resized_img)

# --- Caricamento configurazioni ---

def load_config():
    global botti_data, impostazioni
    if os.path.exists(SALVATAGGIO_FILE):
        with open(SALVATAGGIO_FILE, "r") as f:
            data = json.load(f)
            botti_data = data.get("botti_data", default_botti_data.copy())
            impostazioni = data.get("impostazioni", default_impostazioni.copy())
    else:
        botti_data = default_botti_data.copy()
        impostazioni = default_impostazioni.copy()
    for key in botti_data:
        botti_data[key].setdefault('forced', None)
    impostazioni = {**default_impostazioni, **impostazioni}

load_config()

# Storico temperature e valvole
storico = {key: [] for key in botti_data}
valve_history = {key: [] for key in botti_data}

# --- Funzioni utility ---

def save_config():
    with open(SALVATAGGIO_FILE, "w") as f:
        json.dump({"botti_data": botti_data, "impostazioni": impostazioni}, f, indent=2)

# Modifica soglie

def modifica_soglia(nome, tipo, delta, label):
    step = impostazioni.get('step_temp', 0.1)
    new_val = round(botti_data[nome][tipo] + delta * step, 1)
    botti_data[nome][tipo] = new_val
    label.config(text=f"{new_val:.1f}")
    save_config()

# Tema Light/Dark

def apply_theme():
    theme = impostazioni.get("theme", "Light")
    bg = "#333333" if theme == "Dark" else "#ffffff"
    fg = "#ffffff" if theme == "Dark" else "#000000"
    style = ttk.Style(app)
    app.configure(bg=bg)
    style.configure('TFrame', background=bg)
    style.configure('TLabel', background=bg, foreground=fg)
    style.configure('TButton', font=('Helvetica',18), padding=10)
    style.configure('Large.TCombobox', font=('Helvetica',18), padding=10)

apply_theme()

# Logica valvola

def auto_valvola(nome, temp):
    entry = botti_data[nome]
    # Manual override takes precedence
    if entry['forced'] is not None:
        return entry['forced']
    # Hysteresis: open above max, close below min, otherwise keep last state
    prev = entry.get('valvola', 'Chiusa')
    if temp > entry['max_temp']:
        return 'Aperta'
    if temp < entry['min_temp']:
        return 'Chiusa'
    return prev if prev in ('Aperta', 'Chiusa') else 'Chiusa'

def forza_valvola(nome, action):
    botti_data[nome]['forced'] = action
    botti_data[nome]['valvola'] = action
    save_config()

# Aggiorna grafico

def update_graph(nome, ax, canvas, time_range, tick_interval):
    ax.clear()
    temp_data = storico[nome]
    now = datetime.datetime.now()
    if time_range != 'Tutto':
        delta_map = {
            'Ultimi 1 minuto': datetime.timedelta(minutes=1),
            'Ultimi 5 minuti': datetime.timedelta(minutes=5),
            'Ultimi 15 minuti': datetime.timedelta(minutes=15),
            'Ultimi 30 minuti': datetime.timedelta(minutes=30),
            'Ultime 2 ore': datetime.timedelta(hours=2),
            'Ultime 6 ore': datetime.timedelta(hours=6),
            'Ultime 12 ore': datetime.timedelta(hours=12),
            'Ultime 24 ore': datetime.timedelta(days=1),
            'Ultime 48 ore': datetime.timedelta(days=2),
            'Ultima settimana': datetime.timedelta(days=7),
            'Ultimo mese': datetime.timedelta(days=30),
        }
        cutoff = now - delta_map.get(time_range, datetime.timedelta.max)
        temp_data = [(t,v) for t,v in temp_data if t >= cutoff]
    if temp_data:
        x = [t for t,_ in temp_data]
        y = [v for _,v in temp_data]
        ax.plot(x, y, marker='o', label='Temp')
        entry = botti_data[nome]
        # Soglie
        ax.axhline(entry['min_temp'], color='blue', linestyle='--', label='Min Temp')
        ax.axhline(entry['max_temp'], color='red', linestyle='--', label='Max Temp')
        # Valve history markers
        vh = valve_history[nome]
        open_times = [t for t,s in vh if s == 'Aperta']
        close_times = [t for t,s in vh if s == 'Chiusa']
        ax.scatter(open_times, [entry['max_temp']]*len(open_times), marker='v', color='orange', label='Valve Open')
        ax.scatter(close_times, [entry['min_temp']]*len(close_times), marker='^', color='purple', label='Valve Closed')
        # Locator
        if tick_interval != 'Auto':
            mins = int(tick_interval.split()[0])
            ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=mins))
        else:
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.figure.autofmt_xdate()
    ax.set_title(f"Andamento {nome}")
    ax.set_xlabel('Ora')
    ax.set_ylabel('°C')
    ax.legend(loc='upper right')
    ax.grid(True)
    canvas.draw()

# --- Costruzione UI ---
frames = {}
overview = {}

style = ttk.Style(app)
style.theme_use('clam')
nb = ttk.Notebook(app)
nb.pack(fill='both', expand=True)

# Panoramica
tab0 = ttk.Frame(nb)
nb.add(tab0, text="📊 Panoramica")
ttk.Label(tab0, text="Situazione Generale", font=('Helvetica',26)).pack(pady=10)
settings = ttk.LabelFrame(tab0, text="⚙️ Impostazioni", padding=10)
settings.pack(fill='x', pady=5)
# Theme
th_var = tk.StringVar(value=impostazioni['theme'])
th_combo = ttk.Combobox(settings, values=['Light','Dark'], textvariable=th_var,
                        state='readonly', width=14, style='Large.TCombobox')
th_combo.pack(side='left', padx=5)
th_combo.bind('<<ComboboxSelected>>', lambda e: (impostazioni.update({'theme': th_var.get()}), apply_theme(), save_config()))
# Step (ingrandito)
step_var = tk.DoubleVar(value=impostazioni['step_temp'])
step_combo = ttk.Combobox(settings, values=[0.1, 0.2, 0.5, 1.0], textvariable=step_var,
                          state='readonly', width=12, style='Large.TCombobox')
step_combo.pack(side='left', padx=5)
step_combo.bind('<<ComboboxSelected>>', lambda e: (impostazioni.update({'step_temp': float(step_var.get())}), save_config()))

barrel_frame = ttk.Frame(tab0)
barrel_frame.pack(pady=15)
for nome in botti_data:
    f = tk.Frame(barrel_frame)
    f.pack(side='left', padx=20)
    tk.Label(f, image=app.barrel_img).pack()
    state_lbl = tk.Label(f, text='🟢', font=('Helvetica',24))
    state_lbl.place(relx=0.15, rely=0.15, anchor='center')
    forced_lbl = tk.Label(f, text='', font=('Helvetica',18))
    forced_lbl.place(relx=0.85, rely=0.15, anchor='center')
    tp = ttk.Label(f, text=f"Temp: {botti_data[nome]['temperatura']}°C", font=('Helvetica',16))
    tp.place(relx=0.5, rely=0.5, anchor='center')
    vl = ttk.Label(f, text=f"Valvola: {botti_data[nome]['valvola']}", font=('Helvetica',16))
    vl.place(relx=0.5, rely=0.7, anchor='center')
    overview[nome] = {'state': state_lbl, 'temp': tp, 'valve': vl, 'forced': forced_lbl}

# Tabs dettaglio
def build_detail_tab(nome):
    tab = ttk.Frame(nb)
    nb.add(tab, text=f"🪵 {nome}")
    left = ttk.Frame(tab); left.pack(side='left', fill='y', padx=10, pady=10)
    right = ttk.Frame(tab); right.pack(side='right', fill='both', expand=True, padx=10, pady=10)
    # Controls left
    ctrl = ttk.Frame(left); ctrl.pack(pady=5)
    for text, action in [('Apri','Aperta'),('Chiudi','Chiusa'),('Auto',None)]:
        ttk.Button(ctrl, text=text, width=8, command=lambda n=nome,a=action: forza_valvola(n,a)).pack(side='left', padx=5)
    forced_lbl = tk.Label(left, text='', font=('Helvetica',18))
    forced_lbl.pack(pady=(5,10))
    # Soglie personalizzabili
    ttk.Label(left, text='Soglie (°C)', font=('Helvetica',16)).pack(pady=5)
    thr_frame = ttk.Frame(left); thr_frame.pack(pady=5)
    ttk.Label(thr_frame, text='Min:').grid(row=0, column=0, sticky='e')
    min_lbl = ttk.Label(thr_frame, text=f"{botti_data[nome]['min_temp']:.1f}", font=('Helvetica',16))
    min_lbl.grid(row=0, column=1, padx=5)
    ttk.Button(thr_frame, text='-', width=4, command=lambda n=nome,l=min_lbl: modifica_soglia(n,'min_temp',-1,l)).grid(row=0, column=2)
    ttk.Button(thr_frame, text='+', width=4, command=lambda n=nome,l=min_lbl: modifica_soglia(n,'min_temp',1,l)).grid(row=0, column=3)
    ttk.Label(thr_frame, text='Max:').grid(row=1, column=0, sticky='e', pady=5)
    max_lbl = ttk.Label(thr_frame, text=f"{botti_data[nome]['max_temp']:.1f}", font=('Helvetica',16))
    max_lbl.grid(row=1, column=1, padx=5)
    ttk.Button(thr_frame, text='-', width=4, command=lambda n=nome,l=max_lbl: modifica_soglia(n,'max_temp',-1,l)).grid(row=1, column=2)
    ttk.Button(thr_frame, text='+', width=4, command=lambda n=nome,l=max_lbl: modifica_soglia(n,'max_temp',1,l)).grid(row=1, column=3)
    # Range/tick selectors

    ttk.Label(left, text='Intervallo dati:', font=('Helvetica',14)).pack(pady=5)
    range_var = tk.StringVar(value='Ultime 24 ore')
    range_menu = tk.OptionMenu(left, range_var, *delta_map.keys())
    range_menu.config(font=('Helvetica',16), width=20)
    range_menu.pack(pady=5)
    ttk.Label(left, text='Tick X:', font=('Helvetica',14)).pack(pady=5)
    tick_var = tk.StringVar(value='Auto')
    tick_menu = tk.OptionMenu(left, tick_var, 'Auto','15 minuti','30 minuti','60 minuti')
    tick_menu.config(font=('Helvetica',16), width=15)
    tick_menu.pack(pady=5)
    # Plot right
    fig, ax = plt.subplots(figsize=(8,4))
    canvas = FigureCanvasTkAgg(fig, master=right); canvas.get_tk_widget().pack(fill='both', expand=True)
    NavigationToolbar2Tk(canvas, right).update(); canvas.draw()
    frames[nome] = {'ax': ax, 'canvas': canvas, 'range': range_var, 'tick': tick_var, 'forced_lbl': forced_lbl}

# Prepare delta_map for dynamic build
delta_map = {
    'Tutto': None,
    'Ultimi 1 minuto': datetime.timedelta(minutes=1),
    'Ultimi 5 minuti': datetime.timedelta(minutes=5),
    'Ultimi 15 minuti': datetime.timedelta(minutes=15),
    'Ultimi 30 minuti': datetime.timedelta(minutes=30),
    'Ultime 2 ore': datetime.timedelta(hours=2),
    'Ultime 6 ore': datetime.timedelta(hours=6),
    'Ultime 12 ore': datetime.timedelta(hours=12),
    'Ultime 24 ore': datetime.timedelta(days=1),
    'Ultime 48 ore': datetime.timedelta(days=2),
    'Ultima settimana': datetime.timedelta(days=7),
    'Ultimo mese': datetime.timedelta(days=30),
}

for nome in botti_data:
    build_detail_tab(nome)

# Loop di aggiornamento
def update_all():
    now = datetime.datetime.now()
    for nome, info in frames.items():
        temp = round(botti_data[nome]['temperatura'] + random.uniform(-0.2,0.2),1)
        botti_data[nome]['temperatura'] = temp
        storico[nome].append((now,temp))
        if len(storico[nome])>1000:
            storico[nome] = storico[nome][-1000:]
        # Valve logic
        vstate = auto_valvola(nome,temp)
        botti_data[nome]['valvola'] = vstate
        # Record valve history
        valve_history[nome].append((now, vstate))
        if len(valve_history[nome])>1000:
            valve_history[nome] = valve_history[nome][-1000:]
        # Update detail forced icon and no detail dot
        icon = '🔒' if botti_data[nome]['forced'] in ('Aperta','Chiusa') else ''
        info['forced_lbl'].config(text=icon)
        # Update detail graph
        update_graph(nome, info['ax'], info['canvas'], info['range'].get(), info['tick'].get())
    # Overview update
    for nome, widgets in overview.items():
        entry = botti_data[nome]; tp = entry['temperatura']
        if tp < entry['min_temp']:
            dot, color = '🔵', 'blue'
        elif tp > entry['max_temp']:
            dot, color = '🔴', 'red'
        else:
            dot, color = '🟢', 'green'
        widgets['state'].config(text=dot, fg=color)
        widgets['temp'].config(text=f"Temp: {tp:.1f}°C")
        widgets['valve'].config(text=f"Valvola: {entry['valvola']}")
        widgets['forced'].config(text='🔒' if entry['forced'] in ('Aperta','Chiusa') else '')
    save_config()
    app.after(5000, update_all)

update_all()
app.mainloop()
