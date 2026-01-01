from gui.theme import COLORS


def setup_styles(app):
    from tkinter import ttk
    style = ttk.Style(app)
    style.theme_use("clam")
    style.configure("TFrame", background=COLORS["bg"])
    style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text"])
    style.configure(
        "TButton",
        font=("Helvetica", 14),
        background=COLORS["accent"],
        foreground=COLORS["text"],
        relief="flat",
        padding=6,
    )
    style.map("TButton", background=[("active", COLORS["accent_dark"])])
    style.configure("Large.TCombobox", font=("Helvetica", 14), padding=5)
