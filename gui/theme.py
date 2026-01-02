import customtkinter as ctk


COLORS = {
    "bg": "#0b1220",
    "panel": "#111b2b",
    "panel_alt": "#18253a",
    "panel_soft": "#22334b",
    "accent": "#38bdf8",
    "accent_dark": "#0ea5e9",
    "text": "#f8fafc",
    "text_muted": "#a3b3c2",
    "success": "#34d399",
    "warning": "#fbbf24",
    "danger": "#f87171",
    "info": "#60a5fa",
    "border": "#2b3a52",
}

RADIUS = {
    "sm": 12,
    "md": 18,
    "lg": 24,
}

SPACING = {
    "xs": 6,
    "sm": 12,
    "md": 18,
    "lg": 26,
    "xl": 34,
}

FONT_SIZES = {
    "xs": 14,
    "sm": 16,
    "md": 18,
    "lg": 22,
    "xl": 26,
    "xxl": 32,
}


def font(size=14, weight="normal"):
    return ctk.CTkFont(size=size, weight=weight)
