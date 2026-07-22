"""Vista de notas libres para la historia"""

import customtkinter as ctk
from tkinter import messagebox
from config import FONTS, COLORS
from utils import ImageUtils, DialogMixin, TextUtils


class NotasView(ctk.CTkFrame, DialogMixin):
    """Panel de notas libres: ideas, bocetos, fragmentos, cualquier cosa que surja."""

    def __init__(self, parent, db, historia_id):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.historia_id = historia_id
        self.pack(fill="both", expand=True)

        self._crear_tabla_notas()

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=10)
        ctk.CTkLabel(
            top, text="Bloc de Notas", font=FONTS["subtitle"],
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        flower = ImageUtils.load_flower("card_accent.png", (35, 35))
        if flower:
            ctk.CTkLabel(top, image=flower, text="").pack(side="left", padx=8)

        ctk.CTkButton(
            top, text="Nueva Nota", command=self._nueva_nota, corner_radius=15,
            fg_color=COLORS["btn_primary"], hover_color=COLORS["btn_hover"],
            text_color=COLORS["text_light"], font=FONTS["heading"]
        ).pack(side="right")

        ImageUtils.add_divider(self, pady=5)

        filtros_frame = ctk.CTkFrame(self, fg_color="transparent")
        filtros_frame.pack(fill="x", padx=5, pady=(0, 5))

        ctk.CTkLabel(
            filtros_frame, text="Filtrar por etiqueta:", font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(0, 8))

        self.combo_filtro = ctk.CTkComboBox(
            filtros_frame, values=["Todas"], width=180,
            fg_color=COLORS["bg_card"], text_color=COLORS["text_primary"],
            border_color=COLORS["border_card"], button_color=COLORS["btn_primary"],
            font=FONTS["body"], dropdown_font=FONTS["body"],
            command=self._filtrar_notas
        )
        self.combo_filtro.set("Todas")
        self.combo_filtro.pack(side="left")

        self.lista_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.lista_frame.pack(fill="both", expand=True)

        self._refresh()

    def _crear_tabla_notas(self):
        self.db.ejecutar("""
            CREATE TABLE IF NOT EXISTS notas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                historia_id INTEGER NOT NULL,
                titulo TEXT,
                contenido TEXT,
                etiqueta TEXT DEFAULT 'idea',
                fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP,
                fecha_edicion TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (historia_id) REFERENCES historias(id) ON DELETE CASCADE
            )
        """)

    def _refresh(self):
        for w in self.lista_frame.winfo_children():
            w.destroy()

        filtro = self.combo_filtro.get()
        if filtro == "Todas":
            notas = self.db.obtener(
                "SELECT id, titulo, contenido, etiqueta, fecha_edicion FROM notas WHERE historia_id=? ORDER BY fecha_edicion DESC",
                (self.historia_id,)
            )
        else:
            notas = self.db.obtener(
                "SELECT id, titulo, contenido, etiqueta, fecha_edicion FROM notas WHERE historia_id=? AND etiqueta=? ORDER BY fecha_edicion DESC",
                (self.historia_id, filtro)
            )

        etiquetas = self.db.obtener(
            "SELECT DISTINCT etiqueta FROM notas WHERE historia_id=? ORDER BY etiqueta",
            (self.historia_id,)
        )
        valores = ["Todas"] + [e[0] for e in etiquetas if e[0]]
        self.combo_filtro.configure(values=valores)

        if not notas:
            empty = ctk.CTkFrame(
                self.lista_frame, fg_color=COLORS["bg_card"], corner_radius=15,
                border_color=COLORS["border_card"], border_width=2
            )
            empty.pack(pady=30, padx=20)
            ImageUtils.add_corner_flowers(empty, (50, 50))
            ctk.CTkLabel(
                empty, text="El bloc esta vacio.\nAnota esa idea que te acaba de venir a la cabeza...",
                font=FONTS["body"], text_color=COLORS["text_secondary"]
            ).pack(pady=30, padx=30)
            return

        for nid, titulo, contenido, etiqueta, fecha in notas:
            self._crear_tarjeta_nota(nid, titulo, contenido, etiqueta, fecha)

    def _crear_tarjeta_nota(self, nid, titulo, contenido, etiqueta, fecha):
        card = ctk.CTkFrame(
            self.lista_frame, corner_radius=15,
            fg_color=COLORS["bg_card"], border_color=COLORS["border_card"], border_width=2
        )
        card.pack(fill="x", pady=8, padx=5)
        ImageUtils.add_corner_flowers(card, (30, 30))

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(12, 5))

        color_etiqueta = self._color_etiqueta(etiqueta)
        indicador = ctk.CTkFrame(header, width=10, height=10, corner_radius=5, fg_color=color_etiqueta)
        indicador.pack(side="left", padx=(0, 8))

        titulo_text = titulo if titulo else "(Sin titulo)"
        ctk.CTkLabel(
            header, text=titulo_text, font=FONTS["heading"],
            text_color=COLORS["text_primary"]
        ).pack(side="left")

        meta = ctk.CTkFrame(header, fg_color="transparent")
        meta.pack(side="right")
        ctk.CTkLabel(
            meta, text=f"{etiqueta or 'idea'}", font=FONTS["caption"],
            text_color=COLORS["accent"]
        ).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(
            meta, text=str(fecha)[:16] if fecha else "", font=FONTS["caption"],
            text_color=COLORS["gray"]
        ).pack(side="left")

        if contenido:
            TextUtils.justified_textbox(
                card, contenido, padx=15,
                font=FONTS["body"], text_color=COLORS["text_secondary"],
                fg_color=COLORS["bg_card"]
            )

        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.pack(fill="x", padx=15, pady=(5, 10))
        ctk.CTkButton(
            btns, text="Editar", width=70, corner_radius=10,
            fg_color=COLORS["btn_accent"], hover_color=COLORS["btn_accent_hover"],
            text_color=COLORS["text_light"], font=FONTS["small"],
            command=lambda n=nid: self._editar_nota(n)
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            btns, text="X", width=35,
            fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
            text_color=COLORS["text_light"], corner_radius=10,
            command=lambda n=nid, t=titulo_text: self._borrar_nota(n, t)
        ).pack(side="left", padx=2)

    def _color_etiqueta(self, etiqueta):
        colores = {
            "idea": "#ECDC82",
            "personaje": "#E9737D",
            "escena": "#6BA8E5",
            "dialogo": "#87EF87",
            "plot": "#B67CEC",
            "mundo": "#93EBE6",
            "duda": "#F3AB7B",
            "recordatorio": "#7893AE",
        }
        return colores.get(etiqueta, "#D2691E")

    def _nueva_nota(self):
        self.abrir_dialogo_embebido(
            self, NotaDialog, self.db, self.historia_id,
            on_close=self._refresh
        )

    def _editar_nota(self, nota_id):
        self.abrir_dialogo_embebido(
            self, NotaDialog, self.db, self.historia_id, nota_id,
            on_close=self._refresh
        )

    def _borrar_nota(self, nota_id, titulo):
        if messagebox.askyesno("Confirmar", f"Borrar la nota '{titulo}'?"):
            self.db.ejecutar("DELETE FROM notas WHERE id=?", (nota_id,))
            self._refresh()

    def _filtrar_notas(self, filtro):
        self._refresh()


class NotaDialog(ctk.CTkFrame):
    """Dialogo para crear o editar una nota."""

    ETIQUETAS = [
        "idea", "personaje", "escena", "dialogo",
        "plot", "mundo", "duda", "recordatorio"
    ]

    def __init__(self, parent, db, historia_id, nota_id=None, on_close=None):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.historia_id = historia_id
        self.nota_id = nota_id
        self.on_close = on_close

        if nota_id:
            row = self.db.obtener_uno(
                "SELECT titulo, contenido, etiqueta FROM notas WHERE id=?",
                (nota_id,)
            )
            titulo, contenido, etiqueta = row if row else ("", "", "idea")
            dialog_title = "Editar Nota"
        else:
            titulo = contenido = ""
            etiqueta = "idea"
            dialog_title = "Nueva Nota"

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(5, 0))
        ctk.CTkLabel(
            header, text=dialog_title, font=FONTS["subtitle"],
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            header, text="X", width=32, height=32, corner_radius=16,
            command=self._cerrar, fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"], text_color=COLORS["text_light"],
            font=FONTS["caption"]
        ).pack(side="right", padx=5)

        flower = ImageUtils.load_flower("card_accent.png", (50, 50))
        if flower:
            ctk.CTkLabel(self, image=flower, text="").pack(pady=(10, 5))

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll, text="Titulo (opcional):", font=FONTS["heading"],
            text_color=COLORS["text_primary"]
        ).pack(pady=(10, 5), anchor="w")
        self.entry_titulo = ctk.CTkEntry(
            scroll, width=420,
            fg_color=COLORS["bg_card"], text_color=COLORS["text_primary"],
            border_color=COLORS["border_card"],
            font=FONTS["body"]
        )
        self.entry_titulo.insert(0, titulo or "")
        self.entry_titulo.pack()

        ctk.CTkLabel(
            scroll, text="Etiqueta:", font=FONTS["heading"],
            text_color=COLORS["text_primary"]
        ).pack(pady=(18, 5), anchor="w")
        self.combo_etiqueta = ctk.CTkComboBox(
            scroll, values=self.ETIQUETAS, width=420,
            fg_color=COLORS["bg_card"], text_color=COLORS["text_primary"],
            border_color=COLORS["border_card"], button_color=COLORS["btn_primary"],
            font=FONTS["body"], dropdown_font=FONTS["body"]
        )
        self.combo_etiqueta.set(etiqueta)
        self.combo_etiqueta.pack()

        ctk.CTkLabel(
            scroll, text="Contenido:", font=FONTS["heading"],
            text_color=COLORS["text_primary"]
        ).pack(pady=(18, 5), anchor="w")
        self.text_contenido = ctk.CTkTextbox(
            scroll, width=420, height=280,
            fg_color=COLORS["bg_card"], text_color=COLORS["text_primary"],
            border_color=COLORS["border_card"], wrap="word",
            font=FONTS["body"]
        )
        if contenido:
            self.text_contenido.insert("1.0", contenido)
        self.text_contenido.pack()

        ctk.CTkButton(
            scroll, text="Guardar", command=self._guardar, corner_radius=15,
            fg_color=COLORS["btn_primary"], hover_color=COLORS["btn_hover"],
            text_color=COLORS["text_light"], font=FONTS["heading"],
            width=200, height=40
        ).pack(pady=24)

    def _guardar(self):
        titulo = self.entry_titulo.get().strip()
        contenido = self.text_contenido.get("1.0", "end").strip()
        etiqueta = self.combo_etiqueta.get()

        if not contenido:
            messagebox.showwarning("Contenido vacio", "Escribe algo en la nota.")
            return

        if self.nota_id:
            self.db.ejecutar(
                "UPDATE notas SET titulo=?, contenido=?, etiqueta=?, fecha_edicion=CURRENT_TIMESTAMP WHERE id=?",
                (titulo, contenido, etiqueta, self.nota_id)
            )
        else:
            self.db.ejecutar(
                "INSERT INTO notas (historia_id, titulo, contenido, etiqueta) VALUES (?, ?, ?, ?)",
                (self.historia_id, titulo, contenido, etiqueta)
            )
        self._cerrar()

    def _cerrar(self):
        if self.on_close:
            self.on_close()