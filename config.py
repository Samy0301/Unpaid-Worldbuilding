"""Configuracion global"""

import os
import sys
import customtkinter as ctk


def _get_base_dir():
    """Detecta si estamos en un ejecutable PyInstaller o en desarrollo"""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def _get_user_data_dir():
    """Devuelve una carpeta persistente para datos del usuario."""
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")

    path = os.path.join(base, "NovelPlanner")
    os.makedirs(path, exist_ok=True)
    return path


BASE_DIR = _get_base_dir()
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
FLOWERS_DIR = os.path.join(ASSETS_DIR, "flowers")

DATA_DIR = _get_user_data_dir()
DB_PATH = os.path.join(DATA_DIR, "novel_planner.db")
os.makedirs(DATA_DIR, exist_ok=True)

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

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

FONTS = {
    "title":       ("Playfair Display", 36, "bold"),
    "subtitle":    ("Playfair Display", 28, "bold"),
    "heading":     ("Segoe UI", 18, "bold"),
    "body":        ("Segoe UI", 14),
    "small":       ("Segoe UI", 12),
    "caption":     ("Segoe UI", 11),
    "script":      ("Segoe Script", 16),
}

RELATION_COLORS = {
    "padre":        "#E63946",
    "madre":        "#8B2252",
    "hermano":      "#2E7D32",
    "hermanastro":  "#558B2F",
    "primo":        "#6A1B9A",
    "tio":          "#00695C",
    "familiar":     "#C62828",
    "pareja":       "#D81B60",
    "amigo":        "#1565C0",
    "mejor amigo":  "#0277BD",
    "aliado":       "#00838F",
    "mentor":       "#6D4C41",
    "enemigo":      "#B71C1C",
    "rival":        "#E65100",
    "traidor":      "#37474F",
    "amimenigo":    "#7B1FA2",
    "jefe":         "#283593",
    "deudor":       "#F57F17",
    "protector":    "#2E7D32",
    "informante":   "#455A64",
    "chantajista":  "#4E342E",
    "testigo":      "#5D4037",
    "extra":        "#9E9E9E",
    "ex":           "#795548",
}

WINDOW_SIZE = "1200x800"
CARD_WIDTH = 280
CARD_HEIGHT = 320
NODE_RADIUS = 35