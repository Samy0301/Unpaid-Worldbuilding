"""Contenedor principal de una historia con sidebar de navegación."""

import customtkinter as ctk
from config import FONTS
from view_info import InfoHistoriaView
from view_personajes import PersonajesView
from view_conexiones import ConexionesView
from view_desarrollo import DesarrolloView


class HistoriaView(ctk.CTkFrame):
    """Frame contenedor con sidebar y área de contenido dinámico."""

    def __init__(self, parent, app, historia_id):
        super().__init__(parent, fg_color="transparent")
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

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(self.sidebar, text="📖", font=("Segoe UI", 40)).pack(pady=(30, 10))
        self._lbl_nombre = ctk.CTkLabel(
            self.sidebar,
            text=self._truncate(self.h_nombre, 15),
            font=FONTS["heading"], wraplength=180
        )
        self._lbl_nombre.pack(pady=(0, 30))

        self.content = ctk.CTkFrame(self, fg_color="transparent")
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
                width=160, height=40, corner_radius=12, anchor="w"
            ).pack(pady=5)

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
        """Recarga los datos de la historia tras edición."""
        row = self.db.obtener_uno(
            "SELECT nombre, resumen, plot_general, foto_blob FROM historias WHERE id=?",
            (self.historia_id,)
        )
        self.h_nombre, self.h_resumen, self.h_plot, self.h_foto = row
        self._lbl_nombre.configure(text=self._truncate(self.h_nombre, 15))