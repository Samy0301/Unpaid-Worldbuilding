"""Configuración global de NovelPlanner - Tema "Día Otoñal"."""

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

# ─── Paleta "Día Otoñal" ───
COLORS = {
    "bg_principal":    "#FFF8F0",   # Crema cálido otoñal
    "bg_sidebar":      "#F5E6D3",   # Beige arena
    "bg_card":         "#FFFBF5",   # Blanco cálido
    "bg_dialog":       "#FFF5E6",   # Crema vainilla
    "border_card":     "#A0522D",   # Siena / marrón canela
    "btn_primary":     "#D2691E",   # Naranja terracota
    "btn_hover":       "#8B4513",   # Marrón silla
    "btn_accent":      "#DAA520",   # Ocre dorado
    "btn_accent_hover":"#B8860B",   # Ocre oscuro
    "text_primary":    "#4E342E",   # Marrón espresso
    "text_secondary":  "#6D4C41",   # Marrón nuez
    "text_light":      "#FFFFFF",
    "accent":          "#E67E22",   # Naranja calabaza
    "accent_soft":     "#F0D5A8",   # Ocre pastel
    "success":         "#8FBC8F",   # Verde musgo suave
    "danger":          "#CD5C5C",   # Rojo ladrillo
    "danger_hover":    "#B22222",   # Rojo fuego
    "gray":            "#BCAAA4",   # Gris cálido
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

# ─── Colores de relaciones (ConexionesView) ───
RELATION_COLORS = {
    "padre":   "#8B4513",
    "madre":   "#D2691E",
    "pareja":  "#DAA520",
    "amigo":   "#CD853F",
    "enemigo": "#A52A2A",
    "familiar": "#6B8E23",
    "mentor":  "#4682B4",
    "rival":   "#B22222",
}

# ─── Dimensiones ───
WINDOW_SIZE = "1200x800"
CARD_WIDTH = 280
CARD_HEIGHT = 320
NODE_RADIUS = 35