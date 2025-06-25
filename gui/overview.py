import tkinter as tk
from tkinter import ttk

class OverviewFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.labels = {}
        settings = ttk.LabelFrame(self, text="⚙️ Impostazioni", padding=10)
        settings.pack(fill='x', pady=5)
        self.sv = tk.DoubleVar(value=controller.settings['step_temp'])
        step_cb = ttk.Combobox(settings, values=[0.1, 0.2, 0.5, 1.0], textvariable=self.sv,
                               state='readonly', width=12, style='Large.TCombobox')
        step_cb.pack(side='left', padx=5)
        step_cb.bind('<<ComboboxSelected>>', self.on_step_change)
        bf = ttk.Frame(self)
        bf.pack(pady=15)
        for nome in controller.botti_data:
            f = tk.Frame(bf, bg="#2E2E2E")
            f.pack(side='left', padx=20)
            tk.Label(f, image=controller.barrel_img, bg="#2E2E2E").pack()
            state_lbl = tk.Label(f, text='🟢', font=('Helvetica', 24), bg="#2E2E2E")
            state_lbl.place(relx=0.15, rely=0.15, anchor='center')
            forced_lbl = tk.Label(f, text='', font=('Helvetica', 18), bg="#2E2E2E")
            forced_lbl.place(relx=0.85, rely=0.15, anchor='center')
            tp = ttk.Label(f, text="", font=('Helvetica', 16))
            tp.place(relx=0.5, rely=0.5, anchor='center')
            vl = ttk.Label(f, text="", font=('Helvetica', 16))
            vl.place(relx=0.5, rely=0.7, anchor='center')
            min_lbl = tk.Label(f, text="", font=('Helvetica', 12), fg='blue', bg="#2E2E2E")
            min_lbl.place(relx=0.2, rely=0.85, anchor='center')
            max_lbl = tk.Label(f, text="", font=('Helvetica', 12), fg='red', bg="#2E2E2E")
            max_lbl.place(relx=0.8, rely=0.85, anchor='center')
            self.labels[nome] = {
                'state': state_lbl, 'temp': tp, 'valve': vl, 'forced': forced_lbl,
                'min': min_lbl, 'max': max_lbl
            }
        self.refresh()

    def refresh(self):
        for nome, lbls in self.labels.items():
            e = self.controller.botti_data[nome]
            tp = e['temperatura']
            dot = '🟢' if e['min_temp'] <= tp <= e['max_temp'] else ('🔴' if tp > e['max_temp'] else '🔵')
            color = 'green' if dot == '🟢' else ('red' if dot == '🔴' else 'blue')
            lbls['state'].config(text=dot, fg=color)
            lbls['temp'].config(text=f"Temp: {tp:.1f}°C")
            lbls['valve'].config(text=f"Valvola: {e['valvola']}")
            lbls['forced'].config(text='🔒' if e['forced'] in ('Aperta', 'Chiusa') else '')
            lbls['min'].config(text=f"{e['min_temp']:.1f}°C")
            lbls['max'].config(text=f"{e['max_temp']:.1f}°C")

    def on_step_change(self, event):
        val = float(self.sv.get())
        self.controller.settings['step_temp'] = val
