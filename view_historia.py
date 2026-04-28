"""Contenedor principal de una historia con sidebar de navegación - Tema Jardín."""

import customtkinter as ctk
from config import FONTS, COLORS
from utils import ImageUtils
from view_info import InfoHistoriaView
from view_personajes import PersonajesView
from view_conexiones import ConexionesView
from view_desarrollo import DesarrolloView


class HistoriaView(ctk.CTkFrame):
    """Frame contenedor con sidebar y área de contenido dinámico."""

    def __init__(self, parent, app, historia_id):
        super().__init__(parent, fg_color=COLORS["bg_principal"])
        self.app = app
        self.db = app.db
        self.historia_id = historia_id
        self.pack(fill="both", expand=True)

        # Datos de la historia
        row = self.db.obtener_uno(
            "SELECT nombre, resumen, plot_general, foto_blob FROM historias WHERE id=?",
            (historia_id,)
        )
        self.h_nombre, self.h_resumen, self.h_plot, self.h_foto = row

        # Sidebar con fondo floral
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=COLORS["bg_sidebar"])
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Fondo floral del sidebar
        sidebar_bg = ImageUtils.load_flower("sidebar_bg.png", (200, 800))
        if sidebar_bg:
            bg_lbl = ctk.CTkLabel(self.sidebar, image=sidebar_bg, text="")
            bg_lbl.place(relwidth=1, relheight=1)

        # Contenido del sidebar (encima del fondo)
        ctk.CTkLabel(self.sidebar, text="🌸", font=("Segoe UI", 40)).pack(pady=(30, 10))

        # Marco decorativo alrededor del nombre
        name_frame = ctk.CTkFrame(
            self.sidebar, fg_color=COLORS["bg_card"],
            corner_radius=12, border_color=COLORS["border_card"], border_width=2
        )
        name_frame.pack(pady=(0, 20), padx=10)
        self._lbl_nombre = ctk.CTkLabel(
            name_frame,
            text=self._truncate(self.h_nombre, 15),
            font=FONTS["heading"], wraplength=160, text_color=COLORS["text_primary"]
        )
        self._lbl_nombre.pack(padx=10, pady=8)

        # Separador floral en sidebar
        ImageUtils.add_divider(self.sidebar, pady=5)

        self.content = ctk.CTkFrame(self, fg_color=COLORS["bg_principal"])
        self.content.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self._current_subview = None

        botones = [
            ("🏠 Info", "info"),
            ("👤 Personajes", "personajes"),
            ("🕸️ Conexiones", "conexiones"),
            ("📝 Desarrollo", "desarrollo"),
            ("⬅ Volver", "dashboard"),
        ]

        for texto, destino in botones:
            cmd = self.app.mostrar_dashboard if destino == "dashboard" else lambda d=destino: self._cambiar_vista(d)
            ctk.CTkButton(
                self.sidebar, text=texto, command=cmd,
                width=160, height=40, corner_radius=12, anchor="w",
                fg_color=COLORS["btn_primary"], hover_color=COLORS["btn_hover"],
                text_color=COLORS["text_light"], font=FONTS["body"]
            ).pack(pady=5)

        # Viñetas decorativas entre botones (al final)
        for _ in range(3):
            sep = ctk.CTkLabel(
                self.sidebar, text="· ✿ ·",
                font=("Segoe Script", 16), text_color=COLORS["accent_soft"]
            )
            sep.pack(pady=2)

        # Flor decorativa al final del sidebar
        flower = ImageUtils.load_flower("card_accent.png", (60, 60))
        if flower:
            ctk.CTkLabel(self.sidebar, image=flower, text="").pack(pady=(20, 10))

        self.mostrar_info()

    @staticmethod
    def _truncate(text, max_len):
        return text[:max_len] + "..." if len(text) > max_len else text

    def _cambiar_vista(self, nombre):
        if self._current_subview:
            self._current_subview.destroy()
            self._current_subview = None

        if nombre == "info":
            self._current_subview = InfoHistoriaView(self.content, self)
        elif nombre == "personajes":
            self._current_subview = PersonajesView(self.content, self.db, self.historia_id)
        elif nombre == "conexiones":
            self._current_subview = ConexionesView(self.content, self.db, self.historia_id)
        elif nombre == "desarrollo":
            self._current_subview = DesarrolloView(self.content, self.db, self.historia_id)

    def mostrar_info(self):
        self._cambiar_vista("info")

    def recargar_datos(self):
        row = self.db.obtener_uno(
            "SELECT nombre, resumen, plot_general, foto_blob FROM historias WHERE id=?",
            (self.historia_id,)
        )
        self.h_nombre, self.h_resumen, self.h_plot, self.h_foto = row
        self._lbl_nombre.configure(text=self._truncate(self.h_nombre, 15))