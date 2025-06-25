import datetime
import matplotlib.dates as mdates

def auto_valvola(botti_data, nome, temp):
    e = botti_data[nome]
    if e['forced'] is not None: return e['forced']
    prev = e.get('valvola', 'Chiusa')
    if temp > e['max_temp']: return 'Aperta'
    if temp < e['min_temp']: return 'Chiusa'
    return prev if prev in ('Aperta', 'Chiusa') else 'Chiusa'

def forza_valvola(botti_data, nome, action):
    botti_data[nome]['forced'] = action
    botti_data[nome]['valvola'] = action

def modifica_soglia(controller, nome, tipo, delta, label):
    step = controller.settings.get('step_temp', 0.1)
    new_val = round(controller.botti_data[nome][tipo] + delta * step, 1)
    controller.botti_data[nome][tipo] = new_val
    label.config(text=f"{new_val:.1f}")

def update_graph(controller, nome, ax, canvas, time_range, tick_interval, legend_visible):
    ax.clear()
    data = controller.storico[nome]
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
    now = datetime.datetime.now()
    cutoff = now - delta_map.get(time_range, datetime.timedelta.max) if time_range != 'Tutto' else None
    filtered = [(t, v) for t, v in data if not cutoff or t >= cutoff]
    if filtered:
        x, y = zip(*filtered)
        ax.plot(x, y, marker='o', label='Temp', color='#2196F3')
        e = controller.botti_data[nome]
        ax.axhline(e['min_temp'], color='blue', linestyle='--', label='Min')
        ax.axhline(e['max_temp'], color='red', linestyle='--', label='Max')
        vh = controller.valve_history[nome]
        if cutoff: vh = [(t, s) for t, s in vh if t >= cutoff]
        opens = [t for t, s in vh if s == 'Aperta']
        closes = [t for t, s in vh if s == 'Chiusa']
        ax.scatter(opens, [e['max_temp']] * len(opens), marker='v', color='orange', label='Open')
        ax.scatter(closes, [e['min_temp']] * len(closes), marker='^', color='purple', label='Close')
        if tick_interval != 'Auto':
            try:
                interval = int(tick_interval.split()[0])
                ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=interval))
            except Exception:
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        else:
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.figure.autofmt_xdate()
    leg = ax.legend(loc='upper right')
    if not legend_visible and leg:
        leg.set_visible(False)
    ax.grid(True)
    canvas.draw()
