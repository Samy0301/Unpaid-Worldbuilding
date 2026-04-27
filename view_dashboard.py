"""Vista principal: grid de tarjetas con todas las novelas."""

import customtkinter as ctk
from tkinter import messagebox
from config import FONTS, CARD_WIDTH, CARD_HEIGHT
from utils import ImageUtils
from dialogs import HistoriaDialog


class DashboardView(ctk.CTkFrame):
    """Pantalla de inicio con el listado de historias."""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.db = app.db
        self.pack(fill="both", expand=True)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(header, text="📚 Mis Novelas", font=FONTS["title"]).pack(side="left")
        ctk.CTkButton(
            header, text="+ Nueva Historia", command=self._crear_historia,
            width=150, height=40, corner_radius=20
        ).pack(side="right")

        # Grid scrollable
        self.grid_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self._cargar_historias()

    def _cargar_historias(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        historias = self.db.obtener(
            "SELECT id, nombre, resumen, foto_blob FROM historias ORDER BY fecha_creacion DESC"
        )

        if not historias:
            ctk.CTkLabel(
                self.grid_frame, text="No hay historias aún. ¡Crea la primera!",
                font=FONTS["body"], text_color="gray"
            ).pack(pady=50)
            return

        for i, (hid, nombre, resumen, foto) in enumerate(historias):
            card = ctk.CTkFrame(self.grid_frame, corner_radius=15, width=CARD_WIDTH, height=CARD_HEIGHT)
            card.grid(row=i // 3, column=i % 3, padx=15, pady=15, sticky="nsew")
            card.grid_propagate(False)

            img = ImageUtils.blob_a_ctkimage(foto, (CARD_WIDTH, 180))
            ctk.CTkLabel(card, image=img, text="").pack(fill="x")

            ctk.CTkLabel(card, text=nombre, font=FONTS["heading"], wraplength=250).pack(pady=(10, 5))
            resumen_text = (resumen[:80] + "...") if resumen and len(resumen) > 80 else (resumen or "")
            ctk.CTkLabel(card, text=resumen_text, font=FONTS["small"], text_color="gray", wraplength=250).pack()

            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(pady=10)
            ctk.CTkButton(
                btn_frame, text="Abrir", width=80, corner_radius=15,
                command=lambda h=hid: self.app.abrir_historia(h)
            ).pack(side="left", padx=5)
            ctk.CTkButton(
                btn_frame, text="🗑", width=40,
                fg_color="#8B0000", hover_color="#5c0000", corner_radius=15,
                command=lambda h=hid, n=nombre: self._borrar_historia(h, n)
            ).pack(side="left", padx=5)

    def _crear_historia(self):
        dialog = HistoriaDialog(self, self.db)
        self.wait_window(dialog)
        self._cargar_historias()

    def _borrar_historia(self, hid, nombre):
        if messagebox.askyesno("Confirmar", f"¿Borrar '{nombre}' y todo su contenido?"):
            # Borrado en cascada manual (por si acaso)
            self.db.ejecutar(
                "DELETE FROM partes_capitulo WHERE capitulo_id IN (SELECT id FROM capitulos WHERE historia_id=?)",
                (hid,)
            )
            self.db.ejecutar("DELETE FROM capitulos WHERE historia_id=?", (hid,))
            self.db.ejecutar("DELETE FROM relaciones WHERE historia_id=?", (hid,))
            self.db.ejecutar(
                "DELETE FROM nodos_genealogicos WHERE arbol_id IN (SELECT id FROM arboles_genealogicos WHERE historia_id=?)",
                (hid,)
            )
            self.db.ejecutar("DELETE FROM arboles_genealogicos WHERE historia_id=?", (hid,))
            self.db.ejecutar("DELETE FROM posiciones_nodos WHERE historia_id=?", (hid,))
            self.db.ejecutar("DELETE FROM personajes WHERE historia_id=?", (hid,))
            self.db.ejecutar("DELETE FROM historias WHERE id=?", (hid,))
            self._cargar_historias()