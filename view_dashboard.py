"""Vista principal: grid de tarjetas con todas las novelas - Tema Jardín."""

import customtkinter as ctk
from tkinter import messagebox
from config import FONTS, COLORS, CARD_WIDTH, CARD_HEIGHT
from utils import ImageUtils
from dialogs import HistoriaDialog


class DashboardView(ctk.CTkFrame):
    """Pantalla de inicio con el listado de historias."""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg_principal"])
        self.app = app
        self.db = app.db
        self.pack(fill="both", expand=True)

        # Header con decoración
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(header, text="📚 Mis Novelas", font=FONTS["title"], text_color=COLORS["text_primary"]).pack(side="left")

        flower = ImageUtils.load_flower("card_accent.png", (50, 50))
        if flower:
            ctk.CTkLabel(header, image=flower, text="").pack(side="left", padx=10)

        ctk.CTkButton(
            header, text="+ Nueva Historia", command=self._crear_historia,
            width=150, height=40, corner_radius=20,
            fg_color=COLORS["btn_primary"], hover_color=COLORS["btn_hover"],
            text_color=COLORS["text_light"], font=FONTS["heading"]
        ).pack(side="right")

        ImageUtils.add_divider(self, pady=5)

        ctk.CTkLabel(
            self, text="✿  Cada historia es una flor que espera florecer  ✿",
            font=FONTS["script"], text_color=COLORS["btn_hover"]
        ).pack(pady=(0, 10))

        self.grid_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self._cargar_historias()

    def _abrir_dialogo_embebido(self, DialogClass, *args, on_close=None, **kwargs):
        """Muestra un diálogo como panel centrado sobre esta vista."""
        overlay = ctk.CTkFrame(self, fg_color=COLORS["bg_principal"])
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        container = ctk.CTkFrame(
            overlay, fg_color=COLORS["bg_dialog"], corner_radius=20,
            border_color=COLORS["border_card"], border_width=2
        )
        container.place(relx=0.5, rely=0.5, anchor="center")

        def _on_close():
            overlay.destroy()
            if on_close:
                on_close()

        dialog = DialogClass(container, *args, on_close=_on_close, **kwargs)
        dialog.pack(fill="both", expand=True, padx=10, pady=10)

    def _cargar_historias(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        historias = self.db.obtener(
            "SELECT id, nombre, resumen, foto_blob FROM historias ORDER BY fecha_creacion DESC"
        )

        if not historias:
            frame_empty = ctk.CTkFrame(self.grid_frame, fg_color=COLORS["bg_card"], corner_radius=20)
            frame_empty.pack(pady=50, padx=20)
            ctk.CTkLabel(
                frame_empty, text="No hay historias aún.\n¡Crea la primera!",
                font=FONTS["body"], text_color=COLORS["text_secondary"]
            ).pack(pady=40, padx=40)
            return

        for i, (hid, nombre, resumen, foto) in enumerate(historias):
            card = ctk.CTkFrame(
                self.grid_frame, corner_radius=15, width=CARD_WIDTH, height=CARD_HEIGHT,
                fg_color=COLORS["bg_card"], border_color=COLORS["border_card"], border_width=2
            )
            card.grid(row=i // 3, column=i % 3, padx=15, pady=15, sticky="nsew")
            card.grid_propagate(False)

            # Badge superior amarillo (sin flores en esquinas)
            ImageUtils.add_top_badge(card, COLORS["btn_accent"], size=28)

            img = ImageUtils.blob_a_ctkimage(foto, (CARD_WIDTH, 180))
            ctk.CTkLabel(card, image=img, text="").pack(fill="x", pady=(10, 0))

            ctk.CTkLabel(
                card, text=nombre, font=FONTS["heading"],
                text_color=COLORS["text_primary"], wraplength=250
            ).pack(pady=(10, 5))

            resumen_text = (resumen[:80] + "...") if resumen and len(resumen) > 80 else (resumen or "")
            ctk.CTkLabel(
                card, text=resumen_text, font=FONTS["small"],
                text_color=COLORS["text_secondary"], wraplength=250
            ).pack()

            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(pady=10)
            ctk.CTkButton(
                btn_frame, text="Abrir", width=80, corner_radius=15,
                fg_color=COLORS["btn_primary"], hover_color=COLORS["btn_hover"],
                text_color=COLORS["text_light"],
                command=lambda h=hid: self.app.abrir_historia(h)
            ).pack(side="left", padx=5)
            ctk.CTkButton(
                btn_frame, text="🗑", width=40,
                fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
                text_color=COLORS["text_light"], corner_radius=15,
                command=lambda h=hid, n=nombre: self._borrar_historia(h, n)
            ).pack(side="left", padx=5)

    def _crear_historia(self):
        self._abrir_dialogo_embebido(
            HistoriaDialog, self.db,
            on_close=self._cargar_historias
        )

    def _borrar_historia(self, hid, nombre):
        if messagebox.askyesno("Confirmar", f"¿Borrar '{nombre}' y todo su contenido?"):
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