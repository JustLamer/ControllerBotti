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
default_impostazioni = {"step_temp": 0.1}

# --- Setup GUI ---
app = tk.Tk()
app.title("Controllo Botti")
app.geometry("1280x900")
app.configure(bg="#2E2E2E")  # Dark gray background  # Light theme background

# Stile moderno per i pulsanti
style = ttk.Style(app)
style.theme_use('clam')
# Dark theme styles
style.configure('TFrame', background='#2E2E2E')
style.configure('TLabel', background='#2E2E2E', foreground='white')
style.configure('TButton', font=('Helvetica',16), background='#4CAF50', foreground='white', relief='flat', padding=8)
style.map('TButton', background=[('active', '#388E3C')])
style.map('TButton', background=[('active', '#45A049')])
style.configure('Large.TCombobox', font=('Helvetica',16), padding=6)

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

# Esegui il caricamento della configurazione
load_config()

# Intervalli disponibili (usata sia in overview che dettaglio)
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

# Storico dati
storico = {k: [] for k in botti_data}
valve_history = {k: [] for k in botti_data}
legend_visibility = {k: True for k in botti_data}
overview = {}
frames = {}

# Utility
def save_config():
    with open(SALVATAGGIO_FILE, 'w') as f:
        json.dump({"botti_data": botti_data, "impostazioni": impostazioni}, f, indent=2)

def modifica_soglia(nome, tipo, delta, label):
    step = impostazioni.get('step_temp', 0.1)
    new_val = round(botti_data[nome][tipo] + delta * step, 1)
    botti_data[nome][tipo] = new_val
    label.config(text=f"{new_val:.1f}")
    save_config()

# Valvola con isteresi
def auto_valvola(nome, temp):
    e = botti_data[nome]
    if e['forced'] is not None: return e['forced']
    prev = e.get('valvola', 'Chiusa')
    if temp > e['max_temp']: return 'Aperta'
    if temp < e['min_temp']: return 'Chiusa'
    return prev if prev in ('Aperta','Chiusa') else 'Chiusa'

def forza_valvola(nome, action):
    botti_data[nome]['forced'] = action
    botti_data[nome]['valvola'] = action
    save_config()

# Grafico con storia valvole e toggle legenda
def update_graph(nome, ax, canvas, time_range, tick_interval):
    ax.clear()
    data = storico[nome]
    now = datetime.datetime.now()
    cutoff = now - delta_map.get(time_range, datetime.timedelta.max) if time_range!='Tutto' else None
    if cutoff: data = [(t,v) for t,v in data if t>=cutoff]
    if data:
        x,y = zip(*data)
        ax.plot(x,y,marker='o',label='Temp', color='#2196F3')
        e = botti_data[nome]
        ax.axhline(e['min_temp'], color='blue', linestyle='--', label='Min')
        ax.axhline(e['max_temp'], color='red', linestyle='--', label='Max')
        vh = valve_history[nome]
        if cutoff: vh=[(t,s) for t,s in vh if t>=cutoff]
        opens = [t for t,s in vh if s=='Aperta']
        closes= [t for t,s in vh if s=='Chiusa']
        ax.scatter(opens,[e['max_temp']]*len(opens),marker='v',color='orange',label='Open')
        ax.scatter(closes,[e['min_temp']]*len(closes),marker='^',color='purple',label='Close')
        if tick_interval!='Auto': ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=int(tick_interval.split()[0])))
        else: ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.figure.autofmt_xdate()
    leg=ax.legend(loc='upper right')
    if not legend_visibility[nome] and leg: leg.set_visible(False)
    ax.grid(True)
    canvas.draw()

# Costruzione UI
nb = ttk.Notebook(app); nb.pack(fill='both',expand=True)
# Panoramica
tab0 = ttk.Frame(nb); nb.add(tab0,text="📊 Panoramica")
settings = ttk.LabelFrame(tab0,text="⚙️ Impostazioni",padding=10); settings.pack(fill='x',pady=5)
# Step selector
sv=tk.DoubleVar(value=impostazioni['step_temp'])
step_cb = ttk.Combobox(settings,values=[0.1,0.2,0.5,1.0],textvariable=sv,state='readonly',width=12,style='Large.TCombobox')
step_cb.pack(side='left',padx=5)
step_cb.bind('<<ComboboxSelected>>',lambda e:(impostazioni.update({'step_temp':float(sv.get())}),save_config()))
# Overview
bf=ttk.Frame(tab0);bf.pack(pady=15)
for nome in botti_data:
    f=tk.Frame(bf);f.pack(side='left',padx=20)
    tk.Label(f,image=app.barrel_img).pack()
    state_lbl=tk.Label(f,text='🟢',font=('Helvetica',24));state_lbl.place(relx=0.15,rely=0.15,anchor='center')
    forced_lbl=tk.Label(f,text='',font=('Helvetica',18));forced_lbl.place(relx=0.85,rely=0.15,anchor='center')
    tp=ttk.Label(f,text=f"Temp: {botti_data[nome]['temperatura']}°C",font=('Helvetica',16));tp.place(relx=0.5,rely=0.5,anchor='center')
    vl=ttk.Label(f,text=f"Valvola: {botti_data[nome]['valvola']}",font=('Helvetica',16));vl.place(relx=0.5,rely=0.7,anchor='center')
    min_lbl=tk.Label(f,text=f"{botti_data[nome]['min_temp']:.1f}°C",font=('Helvetica',12),fg='blue');min_lbl.place(relx=0.2,rely=0.85,anchor='center')
    max_lbl=tk.Label(f,text=f"{botti_data[nome]['max_temp']:.1f}°C",font=('Helvetica',12),fg='red'); max_lbl.place(relx=0.8,rely=0.85,anchor='center')
    overview[nome]={'state':state_lbl,'temp':tp,'valve':vl,'forced':forced_lbl}
# Detail tabs
for nome in botti_data:
    tab=ttk.Frame(nb);nb.add(tab,text=f"🪵 {nome}")
    left=ttk.Frame(tab);left.pack(side='left',fill='y',padx=10,pady=10)
    right=ttk.Frame(tab);right.pack(side='right',fill='both',expand=True,padx=10,pady=10)
    ctrl=ttk.Frame(left);ctrl.pack(pady=5)
    for t,a in [('Apri','Aperta'),('Chiudi','Chiusa'),('Auto',None)]: ttk.Button(ctrl, text=t, width=6, style='TButton', command=lambda n=nome,act=a: forza_valvola(n,act)).pack(side='left',padx=5)
    fl=ttk.Frame(left);fl.pack(pady=(5,10))
    forced_lbl=tk.Label(fl,text='',font=('Helvetica',18));forced_lbl.pack(side='left')
    ttk.Button(fl,text='Legenda',width=8,command=lambda n=nome: (legend_visibility.__setitem__(n, not legend_visibility[n]), update_graph(n,frames[n]['ax'],frames[n]['canvas'],frames[n]['range'].get(),frames[n]['tick'].get()))).pack(side='left',padx=5)
    ttk.Label(left,text='Soglie (°C)',font=('Helvetica',16)).pack(pady=5)
    tf=ttk.Frame(left);tf.pack(pady=8)
    lb=ttk.Label(tf,text='Min:');lb.grid(row=0,column=0,sticky='e')
    min_lbl=ttk.Label(tf,text=f"{botti_data[nome]['min_temp']:.1f}",font=('Helvetica',16));min_lbl.grid(row=0,column=1,padx=5)
    tk.Button(tf, text='-', width=6, bg='#f44336', fg='white', font=('Helvetica',16), relief='flat', command=lambda n=nome,l=min_lbl: modifica_soglia(n,'min_temp',-1,l)).grid(row=0, column=2, padx=2)
    tk.Button(tf, text='+', width=6, bg='#4CAF50', fg='white', font=('Helvetica',16), relief='flat', command=lambda n=nome,l=min_lbl: modifica_soglia(n,'min_temp',1,l)).grid(row=0, column=3, padx=2)
    ttk.Label(tf,text='Max:').grid(row=1,column=0,sticky='e',pady=(10,0))
    max_lbl=ttk.Label(tf,text=f"{botti_data[nome]['max_temp']:.1f}",font=('Helvetica',16));max_lbl.grid(row=1,column=1,padx=5)
    tk.Button(tf, text='-', width=6, bg='#f44336', fg='white', font=('Helvetica',16), relief='flat', command=lambda n=nome,l=max_lbl: modifica_soglia(n,'max_temp',-1,l)).grid(row=1, column=2, padx=2)
    tk.Button(tf, text='+', width=6, bg='#4CAF50', fg='white', font=('Helvetica',16), relief='flat', command=lambda n=nome,l=max_lbl: modifica_soglia(n,'max_temp',1,l)).grid(row=1, column=3, padx=2)
    range_var=tk.StringVar(value='Ultime 24 ore'); range_menu=tk.OptionMenu(left,range_var,*delta_map.keys()); range_menu.config(font=('Helvetica',16),width=20);range_menu.pack(pady=5)
    tick_var=tk.StringVar(value='Auto'); tick_menu=tk.OptionMenu(left,tick_var,'Auto','15 minuti','30 minuti','60 minuti'); tick_menu.config(font=('Helvetica',16),width=15); tick_menu.pack(pady=5)
    fig,ax=plt.subplots(figsize=(8,4)); canvas=FigureCanvasTkAgg(fig,master=right);canvas.get_tk_widget().pack(fill='both',expand=True);NavigationToolbar2Tk(canvas,right).update(); canvas.draw()
    frames[nome]={'ax':ax,'canvas':canvas,'range':range_var,'tick':tick_var,'forced_lbl':forced_lbl}
# Intervalli
delta_map={
    'Tutto':None,
    'Ultimi 1 minuto':datetime.timedelta(minutes=1),'Ultimi 5 minuti':datetime.timedelta(minutes=5),'Ultimi 15 minuti':datetime.timedelta(minutes=15),'Ultimi 30 minuti':datetime.timedelta(minutes=30),
    'Ultime 2 ore':datetime.timedelta(hours=2),'Ultime 6 ore':datetime.timedelta(hours=6),'Ultime 12 ore':datetime.timedelta(hours=12),'Ultime 24 ore':datetime.timedelta(days=1),'Ultime 48 ore':datetime.timedelta(days=2),'Ultima settimana':datetime.timedelta(days=7),'Ultimo mese':datetime.timedelta(days=30)
}
# Loop di aggiornamento
def update_all():
    now=datetime.datetime.now()
    for nome,info in frames.items():
        temp=round(botti_data[nome]['temperatura']+random.uniform(-0.2,0.2),1)
        botti_data[nome]['temperatura']=temp; storico[nome].append((now,temp))
        if len(storico[nome])>1000: storico[nome]=storico[nome][-1000:]
        vstate=auto_valvola(nome,temp); botti_data[nome]['valvola']=vstate; valve_history[nome].append((now,vstate))
        if len(valve_history[nome])>1000: valve_history[nome]=valve_history[nome][-1000:]
        info['forced_lbl'].config(text='🔒' if botti_data[nome]['forced'] in ('Aperta','Chiusa') else '')
        update_graph(nome,info['ax'],info['canvas'],info['range'].get(),info['tick'].get())
    for nome,widgets in overview.items():
        e=botti_data[nome]; tp=e['temperatura']
        dot='🟢' if e['min_temp']<=tp<=e['max_temp'] else ('🔴' if tp>e['max_temp'] else '🔵')
        widgets['state'].config(text=dot); widgets['state'].config(fg='green' if dot=='🟢' else ('red' if dot=='🔴' else 'blue'))
        widgets['temp'].config(text=f"Temp: {tp:.1f}°C"); widgets['valve'].config(text=f"Valvola: {e['valvola']}"); widgets['forced'].config(text='🔒' if e['forced'] in ('Aperta','Chiusa') else '')
    save_config(); app.after(5000,update_all)
update_all(); app.mainloop()
