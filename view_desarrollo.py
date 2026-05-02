"""Vista de capítulos y sus partes - Tema Otoñal."""

import customtkinter as ctk
from tkinter import messagebox
from config import FONTS, COLORS
from utils import ImageUtils
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
        ctk.CTkLabel(
            top, text="📝 Desarrollo por Capítulos", font=FONTS["subtitle"],
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        flower = ImageUtils.load_flower("card_accent.png", (35, 35))
        if flower:
            ctk.CTkLabel(top, image=flower, text="").pack(side="left", padx=8)
        ctk.CTkButton(
            top, text="➕ Nuevo Capítulo", command=self._crear, corner_radius=15,
            fg_color=COLORS["btn_primary"], hover_color=COLORS["btn_hover"],
            text_color=COLORS["text_light"], font=FONTS["heading"]
        ).pack(side="right")

        ImageUtils.add_divider(self, pady=5)

        self.lista_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.lista_frame.pack(fill="both", expand=True)
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
        for w in self.lista_frame.winfo_children():
            w.destroy()

        caps = self.db.obtener(
            "SELECT id, numero, titulo, plot_guia FROM capitulos WHERE historia_id=? ORDER BY numero",
            (self.historia_id,)
        )

        if not caps:
            empty = ctk.CTkFrame(self.lista_frame, fg_color=COLORS["bg_card"], corner_radius=15,
                                border_color=COLORS["border_card"], border_width=2)
            empty.pack(pady=30, padx=20)
            ImageUtils.add_corner_flowers(empty, (50, 50))
            ctk.CTkLabel(
                empty, text="No hay capítulos aún\n¡Empieza a escribir tu historia! 🌟",
                font=FONTS["body"], text_color=COLORS["text_secondary"]
            ).pack(pady=30, padx=30)
            return

        for cid, num, titulo, plot in caps:
            card = ctk.CTkFrame(
                self.lista_frame, corner_radius=15,
                fg_color=COLORS["bg_card"], border_color=COLORS["border_card"], border_width=2
            )
            card.pack(fill="x", pady=8, padx=5)
            ImageUtils.add_corner_flowers(card, (35, 35))

            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=15, pady=10)
            ctk.CTkLabel(
                header, text=f"➡️ Cap. {num}: {titulo}", font=FONTS["heading"],
                text_color=COLORS["text_primary"]
            ).pack(side="left")

            btns = ctk.CTkFrame(header, fg_color="transparent")
            btns.pack(side="right")
            ctk.CTkButton(
                btns, text="Ver partes 🌺", width=90, corner_radius=10,
                fg_color=COLORS["btn_primary"], hover_color=COLORS["btn_hover"],
                text_color=COLORS["text_light"],
                command=lambda c=cid: self._ver_partes(c)
            ).pack(side="left", padx=2)
            ctk.CTkButton(
                btns, text="✏️", width=40, corner_radius=10,
                fg_color=COLORS["btn_accent"], hover_color=COLORS["btn_accent_hover"],
                command=lambda c=cid, n=num, t=titulo, p=plot: self._editar(c, n, t, p)
            ).pack(side="left", padx=2)
            ctk.CTkButton(
                btns, text="🗑", width=40,
                fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
                text_color=COLORS["text_light"], corner_radius=10,
                command=lambda c=cid, n=num: self._borrar(c, n)
            ).pack(side="left", padx=2)

            if plot:
                ctk.CTkLabel(
                    card, text=f"Plot: {plot}", font=FONTS["small"],
                    text_color=COLORS["text_secondary"], wraplength=600
                ).pack(padx=15, pady=(0, 10))

    def _crear(self):
        self._abrir_dialogo_embebido(
            CapituloDialog, self.db, self.historia_id,
            on_close=self._refresh
        )

    def _editar(self, cid, num, titulo, plot):
        self._abrir_dialogo_embebido(
            CapituloDialog, self.db, self.historia_id, cid,
            on_close=self._refresh
        )

    def _borrar(self, cid, num):
        if messagebox.askyesno("Confirmar", f"¿Borrar el Capítulo {num}?"):
            self.db.ejecutar("DELETE FROM partes_capitulo WHERE capitulo_id=?", (cid,))
            self.db.ejecutar("DELETE FROM capitulos WHERE id=?", (cid,))
            self._refresh()

    def _ver_partes(self, capitulo_id):
        overlay = ctk.CTkFrame(self, fg_color=COLORS["bg_principal"])
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        container = ctk.CTkFrame(
            overlay, fg_color=COLORS["bg_dialog"], corner_radius=20,
            border_color=COLORS["border_card"], border_width=2,
            width=520, height=620
        )
        container.place(relx=0.5, rely=0.5, anchor="center")
        container.pack_propagate(False)

        def _cerrar_overlay():
            overlay.destroy()

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(
            header, text="🔆 Partes del Capítulo 🔆", font=FONTS["subtitle"],
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        ctk.CTkButton(
            header, text="✕", width=28, height=28, corner_radius=14,
            command=_cerrar_overlay, fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"], text_color=COLORS["text_light"],
            font=FONTS["caption"]
        ).pack(side="right")

        ctk.CTkButton(
            header, text="➕ Añadir Parte",
            command=lambda: self._crear_parte(scroll, capitulo_id),
            corner_radius=15,
            fg_color=COLORS["btn_primary"], hover_color=COLORS["btn_hover"],
            text_color=COLORS["text_light"]
        ).pack(side="right", padx=10)

        ImageUtils.add_divider(container, pady=5)

        scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
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
            f = ctk.CTkFrame(
                scroll, corner_radius=12,
                fg_color=COLORS["bg_card"], border_color=COLORS["border_card"], border_width=2
            )
            f.pack(fill="x", pady=5)
            ImageUtils.add_corner_flowers(f, (30, 30))

            hdr = ctk.CTkFrame(f, fg_color="transparent")
            hdr.pack(fill="x", padx=10, pady=(10, 5))
            ctk.CTkLabel(
                hdr, text=f"➡️ {nombre}", font=FONTS["heading"],
                text_color=COLORS["text_primary"]
            ).pack(side="left")
            ctk.CTkButton(
                hdr, text="✏️", width=35, corner_radius=8,
                fg_color=COLORS["btn_accent"], hover_color=COLORS["btn_accent_hover"],
                command=lambda p=pid, n=nombre, c=contenido: self._editar_parte(scroll, capitulo_id, p, n, c)
            ).pack(side="right", padx=2)
            ctk.CTkButton(
                hdr, text="🗑", width=35,
                fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
                text_color=COLORS["text_light"], corner_radius=8,
                command=lambda p=pid, n=nombre: self._borrar_parte(scroll, capitulo_id, p, n)
            ).pack(side="right", padx=2)
            ctk.CTkLabel(
                f, text=contenido, font=FONTS["body"],
                text_color=COLORS["text_secondary"], wraplength=420
            ).pack(anchor="w", padx=10, pady=(0, 10))

    def _crear_parte(self, scroll, capitulo_id):
        self._abrir_dialogo_embebido(
            ParteDialog, self.db, capitulo_id,
            on_close=lambda: self._render_partes(scroll, capitulo_id)
        )

    def _editar_parte(self, scroll, capitulo_id, pid, nombre, contenido):
        self._abrir_dialogo_embebido(
            ParteDialog, self.db, capitulo_id, pid, nombre, contenido,
            on_close=lambda: self._render_partes(scroll, capitulo_id)
        )

    def _borrar_parte(self, scroll, capitulo_id, pid, nombre):
        if messagebox.askyesno("Confirmar", f"¿Borrar la parte '{nombre}'?"):
            self.db.ejecutar("DELETE FROM partes_capitulo WHERE id=?", (pid,))
            self._render_partes(scroll, capitulo_id)