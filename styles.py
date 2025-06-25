def setup_styles(app):
    from tkinter import ttk
    style = ttk.Style(app)
    style.theme_use('clam')
    style.configure('TFrame', background='#2E2E2E')
    style.configure('TLabel', background='#2E2E2E', foreground='white')
    style.configure('TButton', font=('Helvetica', 16), background='#4CAF50', foreground='white', relief='flat', padding=8)
    style.map('TButton', background=[('active', '#388E3C')])
    style.configure('Large.TCombobox', font=('Helvetica', 16), padding=6)
    # puoi aggiungere altri stili personalizzati qui
