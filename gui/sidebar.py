import customtkinter as ctk
from gui.theme import COLORS, FONT_SIZES, RADIUS, SPACING, font

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, tab_list, on_tab_click, **kwargs):
        super().__init__(master, width=96, fg_color=COLORS["panel"], **kwargs)
        self.tab_list = tab_list
        self.on_tab_click = on_tab_click
        self.btns = {}
        self.selected_tab = None

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(pady=(SPACING["lg"], SPACING["sm"]), padx=SPACING["sm"], fill="x")
        ctk.CTkLabel(
            header,
            text="Botti",
            font=font(size=FONT_SIZES["lg"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="Controllo",
            font=font(size=FONT_SIZES["xs"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w")

        for label, icon in self.tab_list:
            # "Panoramica": solo testo, senza icona
            if label.lower() == "panoramica":
                btn = ctk.CTkButton(
                    self,
                    text=label,
                    image=None,
                    width=78,
                    height=40,
                    font=font(size=FONT_SIZES["sm"], weight="bold"),
                    fg_color=COLORS["panel_alt"],
                    hover_color=COLORS["panel_soft"],
                    corner_radius=RADIUS["md"],
                    border_width=1,
                    border_color=COLORS["border"],
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
                    width=78,
                    height=52,
                    font=font(size=FONT_SIZES["sm"], weight="bold"),
                    compound="left",   # numero accanto all'icona
                    fg_color=COLORS["panel_alt"],
                    hover_color=COLORS["panel_soft"],
                    corner_radius=RADIUS["md"],
                    border_width=1,
                    border_color=COLORS["border"],
                    text_color=COLORS["text"],
                    anchor="center",
                    command=lambda l=label: self._on_tab_click(l)
                )
            btn.pack(pady=SPACING["sm"], padx=SPACING["sm"], fill="x")
            self.btns[label] = btn

    def _on_tab_click(self, label):
        btn = self.btns[label]
        btn.configure(font=font(size=FONT_SIZES["md"], weight="bold"))
        self.after(130, lambda: btn.configure(font=font(size=FONT_SIZES["sm"], weight="bold")))
        self.select(label)
        self.on_tab_click(label)

    def select(self, label):
        for l, btn in self.btns.items():
            btn.configure(
                fg_color=COLORS["accent"] if l == label else COLORS["panel_alt"],
                border_color=COLORS["accent"] if l == label else COLORS["border"],
                text_color=COLORS["panel"] if l == label else COLORS["text"],
            )
        self.selected_tab = label
