import customtkinter as ctk


COLORS = {
    "bg": "#0f141a",
    "panel": "#16202a",
    "panel_alt": "#1c2733",
    "panel_soft": "#223041",
    "accent": "#4dd0e1",
    "accent_dark": "#2bb3c4",
    "text": "#f1f5f9",
    "text_muted": "#9aa5b1",
    "success": "#4ade80",
    "warning": "#ffb347",
    "danger": "#ff6b6b",
    "info": "#60a5fa",
}


def font(size=14, weight="normal"):
    return ctk.CTkFont(size=size, weight=weight)
