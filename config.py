"""Configuración global de NovelPlanner."""

import os
import customtkinter as ctk

# ─── Rutas ───
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "novel_planner.db")
os.makedirs(DATA_DIR, exist_ok=True)

# ─── Tema ───
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# ─── Estilos ───
FONTS = {
    "title": ("Playfair Display", 28, "bold"),
    "subtitle": ("Playfair Display", 22, "bold"),
    "heading": ("Segoe UI", 16, "bold"),
    "body": ("Segoe UI", 13),
    "small": ("Segoe UI", 11),
    "caption": ("Segoe UI", 10),
}

# ─── Colores de relaciones (ConexionesView) ───
RELATION_COLORS = {
    "padre": "#4a90d9",
    "madre": "#d94a90",
    "pareja": "#f5a623",
    "amigo": "#7ed321",
    "enemigo": "#d94a4a",
    "familiar": "#9013fe",
    "mentor": "#00bcd4",
    "rival": "#bd10e0",
}

# ─── Dimensiones ───
WINDOW_SIZE = "1200x800"
CARD_WIDTH = 280
CARD_HEIGHT = 320
NODE_RADIUS = 35