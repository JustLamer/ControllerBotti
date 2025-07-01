import customtkinter as ctk

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, tab_list, on_tab_click, **kwargs):
        super().__init__(master, width=44, fg_color="#202d16", **kwargs)
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
                    width=56,
                    height=34,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    fg_color="#324f2b",
                    hover_color="#4db14c",
                    corner_radius=13,
                    border_width=2,
                    border_color="#5fa659",
                    text_color="#fff",
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
                    width=44,
                    height=44,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    compound="left",   # numero accanto all'icona
                    fg_color="#324f2b",
                    hover_color="#4db14c",
                    corner_radius=13,
                    border_width=2,
                    border_color="#5fa659",
                    text_color="#fff",
                    anchor="center",
                    command=lambda l=label: self._on_tab_click(l)
                )
            btn.pack(pady=4, padx=1, fill="x")
            self.btns[label] = btn

    def _on_tab_click(self, label):
        btn = self.btns[label]
        btn.configure(font=ctk.CTkFont(size=14, weight="bold"))
        self.after(130, lambda: btn.configure(font=ctk.CTkFont(size=12, weight="bold")))
        self.select(label)
        self.on_tab_click(label)

    def select(self, label):
        for l, btn in self.btns.items():
            btn.configure(fg_color="#4db14c" if l == label else "#324f2b")
        self.selected_tab = label
