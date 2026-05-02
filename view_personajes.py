"""Gestión de personajes organizados por categoría - Tema Otoñal."""

import customtkinter as ctk
from tkinter import messagebox
from config import FONTS, COLORS
from utils import ImageUtils
from dialogs import PersonajeDialog, FichaPersonajeDialog


class PersonajesView(ctk.CTkFrame):
    """Tabs de personajes: Principal, Secundario, Terciario."""

    CATEGORIAS = ["principal", "secundario", "terciario"]

    def __init__(self, parent, db, historia_id):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.historia_id = historia_id
        self.pack(fill="both", expand=True)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            header, text="👤 Personajes", font=FONTS["subtitle"],
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        flower = ImageUtils.load_flower("card_accent.png", (40, 40))
        if flower:
            ctk.CTkLabel(header, image=flower, text="").pack(side="left", padx=10)

        self.tabview = ctk.CTkTabview(
            self,
            fg_color=COLORS["bg_card"],
            segmented_button_fg_color=COLORS["btn_primary"],
            segmented_button_selected_color=COLORS["btn_hover"],
            segmented_button_selected_hover_color=COLORS["accent"],
            segmented_button_unselected_hover_color=COLORS["btn_hover"],
            text_color=COLORS["text_light"]
        )
        self.tabview.pack(fill="both", expand=True)

        for cat in self.CATEGORIAS:
            self.tabview.add(cat.capitalize())

        ctk.CTkButton(
            self, text="➕ Nuevo Personaje", command=self._crear,
            corner_radius=15,
            fg_color=COLORS["btn_primary"], hover_color=COLORS["btn_hover"],
            text_color=COLORS["text_light"], font=FONTS["heading"]
        ).pack(pady=15)

        self._refresh()

    def _abrir_dialogo_embebido(self, DialogClass, *args, on_close=None, **kwargs):
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

    def _refresh(self):
        for cat in self.CATEGORIAS:
            tab = self.tabview.tab(cat.capitalize())
            for w in tab.winfo_children():
                w.destroy()
            self._cargar_categoria(tab, cat)

    def _cargar_categoria(self, frame, categoria):
        scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        personajes = self.db.obtener(
            "SELECT id, nombre, foto_blob FROM personajes WHERE historia_id=? AND categoria=?",
            (self.historia_id, categoria)
        )

        if not personajes:
            empty = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=15,
                                border_color=COLORS["border_card"], border_width=2)
            empty.pack(pady=30, padx=20)
            ImageUtils.add_corner_flowers(empty, (50, 50))
            ctk.CTkLabel(
                empty, text=f"No hay personajes {categoria}s aún 🌟",
                font=FONTS["body"], text_color=COLORS["text_secondary"]
            ).pack(pady=30, padx=30)
            return

        for i, (pid, nombre, foto) in enumerate(personajes):
            card = ctk.CTkFrame(
                scroll, corner_radius=15, width=200, height=250,
                fg_color=COLORS["bg_card"], border_color=COLORS["border_card"], border_width=2
            )
            card.grid(row=i // 4, column=i % 4, padx=10, pady=10)
            card.grid_propagate(False)

            ImageUtils.add_corner_flowers(card, (40, 40))

            img = ImageUtils.blob_a_ctkimage(foto, (200, 150))
            ctk.CTkLabel(card, image=img, text="").pack(pady=(10, 0))
            ctk.CTkLabel(
                card, text=f"{nombre}", font=FONTS["heading"],
                text_color=COLORS["text_primary"]
            ).pack(pady=5)

            btnf = ctk.CTkFrame(card, fg_color="transparent")
            btnf.pack(pady=5)
            ctk.CTkButton(
                btnf, text="Ver 🌺", width=60, corner_radius=10,
                fg_color=COLORS["btn_primary"], hover_color=COLORS["btn_hover"],
                text_color=COLORS["text_light"],
                command=lambda p=pid: self._abrir_dialogo_embebido(FichaPersonajeDialog, self.db, p)
            ).pack(side="left", padx=2)
            ctk.CTkButton(
                btnf, text="✏️", width=40, corner_radius=10,
                fg_color=COLORS["btn_accent"], hover_color=COLORS["btn_accent_hover"],
                command=lambda p=pid: self._editar(p)
            ).pack(side="left", padx=2)
            ctk.CTkButton(
                btnf, text="🗑", width=40,
                fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
                text_color=COLORS["text_light"], corner_radius=10,
                command=lambda p=pid, n=nombre: self._borrar(p, n)
            ).pack(side="left", padx=2)

    def _crear(self):
        self._abrir_dialogo_embebido(
            PersonajeDialog, self.db, self.historia_id,
            on_close=self._refresh
        )

    def _editar(self, personaje_id):
        self._abrir_dialogo_embebido(
            PersonajeDialog, self.db, self.historia_id, personaje_id,
            on_close=self._refresh
        )

    def _borrar(self, pid, nombre):
        if messagebox.askyesno("Confirmar", f"¿Borrar a '{nombre}'?"):
            self.db.ejecutar(
                "DELETE FROM nodos_genealogicos WHERE personaje_id=? OR padre_id=? OR madre_id=? OR pareja_id=?",
                (pid, pid, pid, pid)
            )
            self.db.ejecutar(
                "DELETE FROM relaciones WHERE personaje1_id=? OR personaje2_id=?",
                (pid, pid)
            )
            self.db.ejecutar("DELETE FROM personajes WHERE id=?", (pid,))
            self._refresh()