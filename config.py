"""Configuración global"""

import os
import customtkinter as ctk

# ─── Rutas ───
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
FLOWERS_DIR = os.path.join(ASSETS_DIR, "flowers")
DB_PATH = os.path.join(DATA_DIR, "novel_planner.db")
os.makedirs(DATA_DIR, exist_ok=True)

# ─── Tema ───
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

# ─── Paleta de colores ───
COLORS = {
    "bg_principal":    "#FFF8F0",
    "bg_sidebar":      "#F5E6D3",
    "bg_card":         "#FFFBF5",
    "bg_dialog":       "#FFF5E6",
    "border_card":     "#A0522D",
    "btn_primary":     "#D2691E",
    "btn_hover":       "#8B4513",
    "btn_active":      "#A0522D",
    "btn_accent":      "#DAA520",
    "btn_accent_hover":"#B8860B",
    "text_primary":    "#4E342E",
    "text_secondary":  "#6D4C41",
    "text_light":      "#FFFFFF",
    "accent":          "#E67E22",
    "accent_soft":     "#F0D5A8",
    "success":         "#8FBC8F",
    "danger":          "#CD5C5C",
    "danger_hover":    "#B22222",
    "gray":            "#BCAAA4",
}

# ─── Estilos ───
FONTS = {
    "title":       ("Playfair Display", 32, "bold"),
    "subtitle":    ("Playfair Display", 24, "bold"),
    "heading":     ("Segoe UI", 16, "bold"),
    "body":        ("Segoe UI", 13),
    "small":       ("Segoe UI", 11),
    "caption":     ("Segoe UI", 10),
    "script":      ("Segoe Script", 14),
}

# ─── Colores de relaciones ───
RELATION_COLORS = {
    "padre":   "#1122e2",
    "madre":   "#f204ab",
    "pareja":  "#f79204",
    "amigo":   "#08de1e",
    "enemigo": "#d00606",
    "familiar": "#a219c8",
    "mentor":  "#2bdcf3",
    "rival":   "#f674f8",
    "extra":   "#dbf326"
}

# ─── Dimensiones ───
WINDOW_SIZE = "1200x800"
CARD_WIDTH = 280
CARD_HEIGHT = 320
NODE_RADIUS = 35