"""Contenedor principal de una historia con sidebar de navegación - Tema Otoñal."""

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

        row = self.db.obtener_uno(
            "SELECT nombre, resumen, plot_general, foto_blob FROM historias WHERE id=?",
            (historia_id,)
        )
        self.h_nombre, self.h_resumen, self.h_plot, self.h_foto = row

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=COLORS["bg_sidebar"])
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        sidebar_bg = ImageUtils.load_flower("sidebar_bg.png", (200, 800))
        if sidebar_bg:
            bg_lbl = ctk.CTkLabel(self.sidebar, image=sidebar_bg, text="")
            bg_lbl.place(relwidth=1, relheight=1)

        ctk.CTkLabel(self.sidebar, text="🍂", font=("Segoe UI", 40)).pack(pady=(30, 10))
        self._lbl_nombre = ctk.CTkLabel(
            self.sidebar,
            text=self._truncate(self.h_nombre, 15),
            font=FONTS["heading"], wraplength=180, text_color=COLORS["text_primary"]
        )
        self._lbl_nombre.pack(pady=(0, 30))

        ImageUtils.add_divider(self.sidebar, pady=5)

        self.content = ctk.CTkFrame(self, fg_color=COLORS["bg_principal"])
        self.content.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self._current_subview = None

        botones = [
            ("🏠 Info 🍁", "info"),
            ("👤 Personajes 🦋", "personajes"),
            ("🕸️ Conexiones 🍂", "conexiones"),
            ("📝 Desarrollo 🌻", "desarrollo"),
            ("⬅ Volver 🌄", "dashboard"),
        ]

        for texto, destino in botones:
            cmd = self.app.mostrar_dashboard if destino == "dashboard" else lambda d=destino: self._cambiar_vista(d)
            ctk.CTkButton(
                self.sidebar, text=texto, command=cmd,
                width=160, height=40, corner_radius=12, anchor="w",
                fg_color=COLORS["btn_primary"], hover_color=COLORS["btn_hover"],
                text_color=COLORS["text_light"], font=FONTS["body"]
            ).pack(pady=5)

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