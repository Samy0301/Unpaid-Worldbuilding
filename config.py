"""Configuración global de NovelPlanner - Tema "Jardín de Escritura"."""

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
ctk.set_appearance_mode("Light")  # Tema claro para resaltar los colores pastel
ctk.set_default_color_theme("green")  # Base que modificamos con colores custom

# ─── Paleta "Jardín de Escritura" ───
COLORS = {
    "bg_principal":    "#FFF5F0",   # Crema rosado
    "bg_sidebar":      "#FFE4E1",   # Rosa melocotón
    "bg_card":         "#FFFFFF",   # Blanco puro
    "bg_dialog":       "#FFF8F5",   # Crema más claro
    "border_card":     "#FFB6C1",   # Rosa claro
    "btn_primary":     "#D4A5A5",   # Rosa antiguo
    "btn_hover":       "#C08081",   # Rosa más oscuro
    "btn_accent":      "#F4D03F",   # Amarillo dorado
    "btn_accent_hover":"#F1C40F",   # Amarillo más intenso
    "text_primary":    "#5D4037",   # Marrón cálido
    "text_secondary":  "#8D6E63",   # Marrón suave
    "text_light":      "#FFFFFF",
    "accent":          "#E91E63",   # Rosa fucsia
    "accent_soft":     "#F8BBD0",   # Rosa pastel
    "success":         "#81C784",   # Verde suave
    "danger":          "#E57373",   # Rojo suave
    "danger_hover":    "#EF5350",
    "gray":            "#BDBDBD",
}

# ─── Estilos ───
FONTS = {
    "title":       ("Playfair Display", 32, "bold"),
    "subtitle":    ("Playfair Display", 24, "bold"),
    "heading":     ("Segoe UI", 16, "bold"),
    "body":        ("Segoe UI", 13),
    "small":       ("Segoe UI", 11),
    "caption":     ("Segoe UI", 10),
    "script":      ("Segoe Script", 14),  # Cursiva decorativa
}

# ─── Colores de relaciones (ConexionesView) ───
RELATION_COLORS = {
    "padre":   "#4a90d9",
    "madre":   "#d94a90",
    "pareja":  "#f5a623",
    "amigo":   "#7ed321",
    "enemigo": "#d94a4a",
    "familiar": "#9013fe",
    "mentor":  "#00bcd4",
    "rival":   "#bd10e0",
}

# ─── Dimensiones ───
WINDOW_SIZE = "1200x800"
CARD_WIDTH = 280
CARD_HEIGHT = 320
NODE_RADIUS = 35