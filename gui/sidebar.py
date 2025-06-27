import customtkinter as ctk

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, tabs, callback, **kwargs):
        super().__init__(master, width=120, fg_color="#243325", **kwargs)
        self.pack_propagate(False)
        self.buttons = {}
        for idx, (tab_name, icon) in enumerate(tabs):
            btn = ctk.CTkButton(
                self,
                text=tab_name,
                image=icon,
                compound="top",  # icona sopra testo
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="transparent",
                hover_color="#2e4a37",
                anchor="center",
                width=100,
                height=90,
                command=lambda n=tab_name: callback(n)
            )
            btn.pack(pady=(16 if idx == 0 else 8, 8))
            self.buttons[tab_name] = btn

    def select(self, tab_name):
        for name, btn in self.buttons.items():
            btn.configure(fg_color="#264d3a" if name == tab_name else "transparent")
