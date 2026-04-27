"""Gestión de personajes organizados por categoría."""

import customtkinter as ctk
from tkinter import messagebox
from config import FONTS
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

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True)

        for cat in self.CATEGORIAS:
            self.tabview.add(cat.capitalize())

        ctk.CTkButton(
            self, text="+ Nuevo Personaje", command=self._crear,
            corner_radius=15
        ).pack(pady=15)

        self._refresh()

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
            ctk.CTkLabel(scroll, text=f"No hay personajes {categoria}s", text_color="gray").pack(pady=30)
            return

        for i, (pid, nombre, foto) in enumerate(personajes):
            card = ctk.CTkFrame(scroll, corner_radius=15, width=200, height=250)
            card.grid(row=i // 4, column=i % 4, padx=10, pady=10)
            card.grid_propagate(False)

            img = ImageUtils.blob_a_ctkimage(foto, (200, 150))
            ctk.CTkLabel(card, image=img, text="").pack()
            ctk.CTkLabel(card, text=nombre, font=FONTS["heading"]).pack(pady=5)

            btnf = ctk.CTkFrame(card, fg_color="transparent")
            btnf.pack(pady=5)
            ctk.CTkButton(
                btnf, text="Ver", width=60, corner_radius=10,
                command=lambda p=pid: FichaPersonajeDialog(self, self.db, p)
            ).pack(side="left", padx=2)
            ctk.CTkButton(
                btnf, text="✏️", width=40, corner_radius=10,
                command=lambda p=pid: self._editar(p)
            ).pack(side="left", padx=2)
            ctk.CTkButton(
                btnf, text="🗑", width=40, fg_color="#8B0000", hover_color="#5c0000", corner_radius=10,
                command=lambda p=pid, n=nombre: self._borrar(p, n)
            ).pack(side="left", padx=2)

    def _crear(self):
        dialog = PersonajeDialog(self, self.db, self.historia_id)
        self.wait_window(dialog)
        self._refresh()

    def _editar(self, personaje_id):
        dialog = PersonajeDialog(self, self.db, self.historia_id, personaje_id)
        self.wait_window(dialog)
        self._refresh()

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