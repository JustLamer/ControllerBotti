import customtkinter as ctk

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, tab_list, on_tab_click, **kwargs):
        super().__init__(master, width=132, fg_color="#202d16", **kwargs)
        self.tab_list = tab_list
        self.on_tab_click = on_tab_click
        self.btns = {}
        self.selected_tab = None

        for label, icon in self.tab_list:
            btn = ctk.CTkButton(
                self,
                text=label,
                image=icon,
                width=104,
                height=104,
                font=ctk.CTkFont(size=23, weight="bold"),
                compound="top",
                fg_color="#324f2b",
                hover_color="#4db14c",
                corner_radius=24,
                border_width=2,
                border_color="#5fa659",
                text_color="#fff",
                anchor="center",
                command=lambda l=label: self._on_tab_click(l)
            )
            btn.pack(pady=14, padx=6)
            self.btns[label] = btn

    def _on_tab_click(self, label):
        # Animazione "zoom" su pressione
        btn = self.btns[label]
        btn.configure(font=ctk.CTkFont(size=27, weight="bold"))
        self.after(130, lambda: btn.configure(font=ctk.CTkFont(size=23, weight="bold")))
        self.select(label)
        self.on_tab_click(label)

    def select(self, label):
        for l, btn in self.btns.items():
            btn.configure(fg_color="#4db14c" if l == label else "#324f2b")
        self.selected_tab = label
