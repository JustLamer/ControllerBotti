import customtkinter as ctk
from gui.theme import COLORS, font

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, tab_list, on_tab_click, **kwargs):
        super().__init__(master, width=70, fg_color=COLORS["panel"], **kwargs)
        self.tab_list = tab_list
        self.on_tab_click = on_tab_click
        self.btns = {}
        self.selected_tab = None

        for label, icon in self.tab_list:
            # "Panoramica": solo testo, senza icona
            if label.lower() == "panoramica":
                btn = ctk.CTkButton(
                    self,
                    text=label,
                    image=None,
                    width=64,
                    height=38,
                    font=font(size=12, weight="bold"),
                    fg_color=COLORS["panel_alt"],
                    hover_color=COLORS["panel_soft"],
                    corner_radius=12,
                    border_width=1,
                    border_color=COLORS["accent"],
                    text_color=COLORS["text"],
                    anchor="center",
                    command=lambda l=label: self._on_tab_click(l)
                )
            else:
                # Estrai il numero dal label (funziona con "1", "Botte 1", "Botte_3", ecc.)
                import re
                match = re.search(r'\d+', label)
                num = match.group(0) if match else ""
                btn = ctk.CTkButton(
                    self,
                    text=num,
                    image=icon,
                    width=54,
                    height=50,
                    font=font(size=12, weight="bold"),
                    compound="left",   # numero accanto all'icona
                    fg_color=COLORS["panel_alt"],
                    hover_color=COLORS["panel_soft"],
                    corner_radius=12,
                    border_width=1,
                    border_color=COLORS["accent"],
                    text_color=COLORS["text"],
                    anchor="center",
                    command=lambda l=label: self._on_tab_click(l)
                )
            btn.pack(pady=6, padx=6, fill="x")
            self.btns[label] = btn

    def _on_tab_click(self, label):
        btn = self.btns[label]
        btn.configure(font=font(size=13, weight="bold"))
        self.after(130, lambda: btn.configure(font=font(size=12, weight="bold")))
        self.select(label)
        self.on_tab_click(label)

    def select(self, label):
        for l, btn in self.btns.items():
            btn.configure(fg_color=COLORS["accent"] if l == label else COLORS["panel_alt"])
        self.selected_tab = label
