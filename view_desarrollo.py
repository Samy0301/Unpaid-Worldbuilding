"""Vista de capítulos y sus partes."""

import customtkinter as ctk
from tkinter import messagebox
from config import FONTS
from dialogs import CapituloDialog, ParteDialog


class DesarrolloView(ctk.CTkFrame):
    """Lista de capítulos con gestión de partes internas."""

    def __init__(self, parent, db, historia_id):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.historia_id = historia_id
        self.pack(fill="both", expand=True)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=10)
        ctk.CTkLabel(top, text="📝 Desarrollo por Capítulos", font=FONTS["subtitle"]).pack(side="left")
        ctk.CTkButton(
            top, text="+ Nuevo Capítulo", command=self._crear, corner_radius=15
        ).pack(side="right")

        self.lista_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.lista_frame.pack(fill="both", expand=True)
        self._refresh()

    def _refresh(self):
        for w in self.lista_frame.winfo_children():
            w.destroy()

        caps = self.db.obtener(
            "SELECT id, numero, titulo, plot_guia FROM capitulos WHERE historia_id=? ORDER BY numero",
            (self.historia_id,)
        )

        if not caps:
            ctk.CTkLabel(self.lista_frame, text="No hay capítulos aún", text_color="gray").pack(pady=30)
            return

        for cid, num, titulo, plot in caps:
            card = ctk.CTkFrame(self.lista_frame, corner_radius=15)
            card.pack(fill="x", pady=8, padx=5)

            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=15, pady=10)
            ctk.CTkLabel(header, text=f"Cap. {num}: {titulo}", font=FONTS["heading"]).pack(side="left")

            btns = ctk.CTkFrame(header, fg_color="transparent")
            btns.pack(side="right")
            ctk.CTkButton(
                btns, text="Ver partes", width=80, corner_radius=10,
                command=lambda c=cid: self._ver_partes(c)
            ).pack(side="left", padx=2)
            ctk.CTkButton(
                btns, text="✏️", width=40, corner_radius=10,
                command=lambda c=cid, n=num, t=titulo, p=plot: self._editar(c, n, t, p)
            ).pack(side="left", padx=2)
            ctk.CTkButton(
                btns, text="🗑", width=40, fg_color="#8B0000", hover_color="#5c0000", corner_radius=10,
                command=lambda c=cid, n=num: self._borrar(c, n)
            ).pack(side="left", padx=2)

            if plot:
                ctk.CTkLabel(
                    card, text=f"Plot: {plot}", font=FONTS["small"],
                    text_color="gray", wraplength=600
                ).pack(padx=15, pady=(0, 10))

    def _crear(self):
        dialog = CapituloDialog(self, self.db, self.historia_id)
        self.wait_window(dialog)
        self._refresh()

    def _editar(self, cid, num, titulo, plot):
        dialog = CapituloDialog(self, self.db, self.historia_id, cid)
        self.wait_window(dialog)
        self._refresh()

    def _borrar(self, cid, num):
        if messagebox.askyesno("Confirmar", f"¿Borrar el Capítulo {num}?"):
            self.db.ejecutar("DELETE FROM partes_capitulo WHERE capitulo_id=?", (cid,))
            self.db.ejecutar("DELETE FROM capitulos WHERE id=?", (cid,))
            self._refresh()

    def _ver_partes(self, capitulo_id):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Partes del Capítulo")
        dialog.geometry("500x600")
        dialog.grab_set()

        ctk.CTkButton(
            dialog, text="+ Añadir Parte",
            command=lambda: self._crear_parte(scroll, capitulo_id),
            corner_radius=15
        ).pack(pady=15)

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10)

        self._render_partes(scroll, capitulo_id)

    def _render_partes(self, scroll, capitulo_id):
        for w in scroll.winfo_children():
            w.destroy()

        partes = self.db.obtener(
            "SELECT id, nombre_parte, contenido FROM partes_capitulo WHERE capitulo_id=? ORDER BY orden",
            (capitulo_id,)
        )
        for pid, nombre, contenido in partes:
            f = ctk.CTkFrame(scroll, corner_radius=12)
            f.pack(fill="x", pady=5)

            hdr = ctk.CTkFrame(f, fg_color="transparent")
            hdr.pack(fill="x", padx=10, pady=(10, 5))
            ctk.CTkLabel(hdr, text=nombre, font=FONTS["heading"]).pack(side="left")
            ctk.CTkButton(
                hdr, text="✏️", width=35, corner_radius=8,
                command=lambda p=pid, n=nombre, c=contenido: self._editar_parte(scroll, capitulo_id, p, n, c)
            ).pack(side="right", padx=2)
            ctk.CTkButton(
                hdr, text="🗑", width=35, fg_color="#8B0000", hover_color="#5c0000", corner_radius=8,
                command=lambda p=pid, n=nombre: self._borrar_parte(scroll, capitulo_id, p, n)
            ).pack(side="right", padx=2)

            ctk.CTkLabel(f, text=contenido, font=FONTS["body"], wraplength=420).pack(
                anchor="w", padx=10, pady=(0, 10)
            )

    def _crear_parte(self, scroll, capitulo_id):
        d = ParteDialog(self, self.db, capitulo_id)
        self.wait_window(d)
        self._render_partes(scroll, capitulo_id)

    def _editar_parte(self, scroll, capitulo_id, pid, nombre, contenido):
        d = ParteDialog(self, self.db, capitulo_id, pid, nombre, contenido)
        self.wait_window(d)
        self._render_partes(scroll, capitulo_id)

    def _borrar_parte(self, scroll, capitulo_id, pid, nombre):
        if messagebox.askyesno("Confirmar", f"¿Borrar la parte '{nombre}'?"):
            self.db.ejecutar("DELETE FROM partes_capitulo WHERE id=?", (pid,))
            self._render_partes(scroll, capitulo_id)