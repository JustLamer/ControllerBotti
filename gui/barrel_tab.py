import tkinter as tk
from tkinter import ttk
from gui.graph_utils import update_graph, modifica_soglia, forza_valvola

class BarrelTab(ttk.Frame):
    def __init__(self, parent, controller, nome):
        super().__init__(parent)
        self.controller = controller
        self.nome = nome
        left = ttk.Frame(self)
        left.pack(side='left', fill='y', padx=10, pady=10)
        right = ttk.Frame(self)
        right.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        ctrl = ttk.Frame(left)
        ctrl.pack(pady=5)
        for t, a in [('Apri', 'Aperta'), ('Chiudi', 'Chiusa'), ('Auto', None)]:
            ttk.Button(ctrl, text=t, width=6, style='TButton',
                       command=lambda act=a: forza_valvola(self.controller.botti_data, self.nome, act)).pack(side='left', padx=5)
        self.forced_lbl = tk.Label(left, text='', font=('Helvetica', 18), bg="#2E2E2E")
        self.forced_lbl.pack(pady=5)
        # Soglie
        tf = ttk.Frame(left)
        tf.pack(pady=8)
        min_lbl = ttk.Label(tf, text=f"{controller.botti_data[nome]['min_temp']:.1f}", font=('Helvetica', 16))
        min_lbl.grid(row=0, column=1, padx=5)
        max_lbl = ttk.Label(tf, text=f"{controller.botti_data[nome]['max_temp']:.1f}", font=('Helvetica', 16))
        max_lbl.grid(row=1, column=1, padx=5)
        tk.Button(tf, text='-', width=4, bg='#f44336', fg='white', font=('Helvetica', 16), relief='flat',
                  command=lambda: modifica_soglia(controller, nome, 'min_temp', -1, min_lbl)).grid(row=0, column=2)
        tk.Button(tf, text='+', width=4, bg='#4CAF50', fg='white', font=('Helvetica', 16), relief='flat',
                  command=lambda: modifica_soglia(controller, nome, 'min_temp', 1, min_lbl)).grid(row=0, column=3)
        tk.Button(tf, text='-', width=4, bg='#f44336', fg='white', font=('Helvetica', 16), relief='flat',
                  command=lambda: modifica_soglia(controller, nome, 'max_temp', -1, max_lbl)).grid(row=1, column=2)
        tk.Button(tf, text='+', width=4, bg='#4CAF50', fg='white', font=('Helvetica', 16), relief='flat',
                  command=lambda: modifica_soglia(controller, nome, 'max_temp', 1, max_lbl)).grid(row=1, column=3)
        # Intervalli tempo e ticks
        self.range_var = tk.StringVar(value='Ultime 24 ore')
        range_menu = tk.OptionMenu(left, self.range_var, *controller.settings.get('delta_map', {
            'Tutto': None,
            'Ultimi 1 minuto': 1, 'Ultimi 5 minuti': 5, 'Ultimi 15 minuti': 15, 'Ultimi 30 minuti': 30
        }).keys())
        range_menu.config(font=('Helvetica', 16), width=20)
        range_menu.pack(pady=5)
        self.tick_var = tk.StringVar(value='Auto')
        tick_menu = tk.OptionMenu(left, self.tick_var, 'Auto', '15 minuti', '30 minuti', '60 minuti')
        tick_menu.config(font=('Helvetica', 16), width=15)
        tick_menu.pack(pady=5)
        # Grafico
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        NavigationToolbar2Tk(self.canvas, right).update()
        self.legend_visible = True

        btn_legend = ttk.Button(left, text='Legenda', width=8, command=self.toggle_legend)
        btn_legend.pack(pady=5)

    def toggle_legend(self):
        self.legend_visible = not self.legend_visible
        self.refresh()

    def refresh(self):
        self.forced_lbl.config(text='🔒' if self.controller.botti_data[self.nome]['forced'] in ('Aperta', 'Chiusa') else '')
        update_graph(self.controller, self.nome, self.ax, self.canvas, self.range_var.get(), self.tick_var.get(), self.legend_visible)
