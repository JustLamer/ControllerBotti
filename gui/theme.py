import customtkinter as ctk
from PIL import Image, ImageColor


COLORS = {
    "bg": "#0a0a0a",
    "panel": "#141414",
    "panel_alt": "#1f1f1f",
    "panel_soft": "#2a2a2a",
    "accent": "#ff8a1c",
    "accent_dark": "#d96f08",
    "text": "#f5f5f5",
    "text_muted": "#b3b3b3",
    "success": "#37c978",
    "warning": "#ffb347",
    "danger": "#f25f5c",
    "info": "#6fb7ff",
    "border": "#2f2f2f",
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


def tint_icon(path, size, color):
    image = Image.open(path).convert("RGBA")
    if size:
        image = image.resize(size, Image.LANCZOS)
    tint = ImageColor.getrgb(color)
    colored = Image.new("RGBA", image.size, tint + (255,))
    colored.putalpha(image.split()[-1])
    return colored
