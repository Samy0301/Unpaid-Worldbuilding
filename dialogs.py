"""Paneles reutilizables para formularios - Tema Otoñal."""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from config import FONTS, COLORS, FLOWERS_DIR
from utils import ImageUtils


class _BaseDialog(ctk.CTkFrame):
    """Panel base con scroll automático y selector de foto."""

    def __init__(self, parent, title: str = "", geometry: str = None, on_close=None):
        super().__init__(parent, fg_color="transparent")
        self.on_close = on_close

        if title:
            header = ctk.CTkFrame(self, fg_color="transparent")
            header.pack(fill="x", pady=(5, 0))
            ctk.CTkLabel(
                header, text=title, font=FONTS["subtitle"],
                text_color=COLORS["text_primary"]
            ).pack(side="left", padx=5)
            ctk.CTkButton(
                header, text="✕", width=28, height=28, corner_radius=14,
                command=self._cerrar, fg_color=COLORS["danger"],
                hover_color=COLORS["danger_hover"], text_color=COLORS["text_light"],
                font=FONTS["caption"]
            ).pack(side="right", padx=5)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=10, pady=10)

        self._foto_blob = None

    def _add_field(self, label: str, widget_type: str, values=None, default="", height=80):
        ctk.CTkLabel(
            self.scroll, text=label, font=FONTS["heading"],
            text_color=COLORS["text_primary"]
        ).pack(pady=(15, 3))
        if widget_type == "entry":
            w = ctk.CTkEntry(
                self.scroll, width=400,
                fg_color=COLORS["bg_card"], text_color=COLORS["text_primary"],
                border_color=COLORS["border_card"]
            )
            if default:
                w.insert(0, default)
            w.pack()
        elif widget_type == "combo":
            w = ctk.CTkComboBox(
                self.scroll, values=values or [], width=400,
                fg_color=COLORS["bg_card"], text_color=COLORS["text_primary"],
                border_color=COLORS["border_card"], button_color=COLORS["btn_primary"]
            )
            if default:
                w.set(default)
            w.pack()
        elif widget_type == "text":
            w = ctk.CTkTextbox(
                self.scroll, width=400, height=height,
                fg_color=COLORS["bg_card"], text_color=COLORS["text_primary"],
                border_color=COLORS["border_card"]
            )
            if default:
                w.insert("1.0", default)
            w.pack()
        else:
            raise ValueError(f"Tipo de widget desconocido: {widget_type}")
        return w

    def _add_foto_selector(self, label: str = "📷 Subir foto", existing_blob=None):
        self._foto_blob = existing_blob
        btn_text = "✅ Foto cargada" if existing_blob else label
        btn_color = COLORS["success"] if existing_blob else COLORS["btn_primary"]

        def seleccionar():
            ruta = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png *.jpg *.jpeg")])
            if ruta:
                self._foto_blob = ImageUtils.archivo_a_blob(ruta)
                btn.configure(text="✅ Foto cargada 🍂", fg_color=COLORS["success"])

        btn = ctk.CTkButton(
            self.scroll, text=btn_text, command=seleccionar, corner_radius=15,
            fg_color=btn_color, hover_color=COLORS["btn_hover"],
            text_color=COLORS["text_light"]
        )
        btn.pack(pady=15)

    def _cerrar(self):
        if self.on_close:
            self.on_close()

    @property
    def foto_blob(self):
        return self._foto_blob


class HistoriaDialog(_BaseDialog):
    """Crear o editar una historia."""

    def __init__(self, parent, db, historia_id=None, on_close=None):
        self.db = db
        self.historia_id = historia_id
        title = "🍁 Editar Historia 🍂" if historia_id else "🍂 Nueva Historia 🍁"
        super().__init__(parent, title=title, on_close=on_close)

        if historia_id:
            row = self.db.obtener_uno(
                "SELECT nombre, resumen, plot_general, foto_blob FROM historias WHERE id=?",
                (historia_id,)
            )
            nombre, resumen, plot, foto = row if row else ("", "", "", None)
        else:
            nombre = resumen = plot = ""
            foto = None

        flower = ImageUtils.load_flower("card_accent.png", (60, 60))
        if flower:
            ctk.CTkLabel(self.scroll, image=flower, text="").pack(pady=(10, 5))

        self.entry_nombre = self._add_field("Nombre de la novela *", "entry", default=nombre)
        self.entry_resumen = self._add_field("Resumen general", "text", default=resumen)
        self.entry_plot = self._add_field("Plot / Trama general", "text", default=plot)
        self._add_foto_selector("📷 Subir portada", foto)

        ctk.CTkButton(
            self.scroll, text="Guardar 🍂", command=self._guardar,
            fg_color=COLORS["btn_primary"], hover_color=COLORS["btn_hover"],
            text_color=COLORS["text_light"], corner_radius=15,
            font=FONTS["heading"]
        ).pack(pady=20)

    def _guardar(self):
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Falta nombre", "Escribe un nombre para la historia.")
            return

        resumen = self.entry_resumen.get("1.0", "end").strip()
        plot = self.entry_plot.get("1.0", "end").strip()

        if self.historia_id:
            self.db.ejecutar(
                "UPDATE historias SET nombre=?, resumen=?, plot_general=?, foto_blob=? WHERE id=?",
                (nombre, resumen, plot, self.foto_blob, self.historia_id)
            )
        else:
            self.db.ejecutar(
                "INSERT INTO historias (nombre, resumen, plot_general, foto_blob) VALUES (?, ?, ?, ?)",
                (nombre, resumen, plot, self.foto_blob)
            )
        self._cerrar()


class PersonajeDialog(_BaseDialog):
    """Crear o editar un personaje."""

    CATEGORIAS = ["principal", "secundario", "terciario"]

    def __init__(self, parent, db, historia_id, personaje_id=None, on_close=None):
        self.db = db
        self.historia_id = historia_id
        self.personaje_id = personaje_id
        title = "🍁 Editar Personaje 🍂" if personaje_id else "🍂 Nuevo Personaje 🍁"
        super().__init__(parent, title=title, on_close=on_close)

        if personaje_id:
            p = self.db.obtener_uno("SELECT * FROM personajes WHERE id=?", (personaje_id,))
            defaults = {
                "nombre": p[2], "categoria": p[3], "edad": p[4], "familia": p[5],
                "historia": p[6], "trauma": p[7], "rol": p[8], "guia": p[9], "foto": p[10]
            }
        else:
            defaults = {k: "" for k in ["nombre", "edad", "familia", "historia", "trauma", "rol", "guia"]}
            defaults["categoria"] = "principal"
            defaults["foto"] = None

        flower = ImageUtils.load_flower("card_accent.png", (50, 50))
        if flower:
            ctk.CTkLabel(self.scroll, image=flower, text="").pack(pady=(10, 5))

        self.entry_nombre = self._add_field("Nombre *", "entry", default=defaults["nombre"])
        self.combo_cat = self._add_field("Categoría", "combo", values=self.CATEGORIAS, default=defaults["categoria"])
        self.entry_edad = self._add_field("Edad", "entry", default=defaults["edad"])
        self.entry_familia = self._add_field("Familia / Apellido", "entry", default=defaults["familia"])
        self.text_historia = self._add_field("Historia personal", "text", default=defaults["historia"])
        self.text_trauma = self._add_field("Traumas / Conflictos", "text", default=defaults["trauma"])
        self.text_rol = self._add_field("Rol en el plot", "text", default=defaults["rol"])
        self.text_guia = self._add_field("Guía de trama por capítulo", "text", default=defaults["guia"])
        self._add_foto_selector("📷 Foto del personaje", defaults["foto"])

        ctk.CTkButton(
            self.scroll, text="Guardar 🍂", command=self._guardar,
            fg_color=COLORS["btn_primary"], hover_color=COLORS["btn_hover"],
            text_color=COLORS["text_light"], corner_radius=15,
            font=FONTS["heading"]
        ).pack(pady=20)

    def _guardar(self):
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Falta nombre", "El personaje necesita un nombre.")
            return

        data = (
            self.historia_id, nombre, self.combo_cat.get(),
            self.entry_edad.get(), self.entry_familia.get(),
            self.text_historia.get("1.0", "end").strip(),
            self.text_trauma.get("1.0", "end").strip(),
            self.text_rol.get("1.0", "end").strip(),
            self.text_guia.get("1.0", "end").strip(),
            self.foto_blob
        )

        if self.personaje_id:
            self.db.ejecutar("""
                UPDATE personajes SET nombre=?, categoria=?, edad=?, familia=?,
                historia_personal=?, trauma=?, plot_rol=?, guia_trama=?, foto_blob=?
                WHERE id=?
            """, (data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], self.personaje_id))
        else:
            self.db.ejecutar("""
                INSERT INTO personajes (historia_id, nombre, categoria, edad, familia,
                historia_personal, trauma, plot_rol, guia_trama, foto_blob)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, data)
        self._cerrar()


class CapituloDialog(_BaseDialog):
    """Crear o editar un capítulo."""

    def __init__(self, parent, db, historia_id, capitulo_id=None, on_close=None):
        self.db = db
        self.historia_id = historia_id
        self.capitulo_id = capitulo_id
        title = "🍁 Editar Capítulo 🍂" if capitulo_id else "🍂 Nuevo Capítulo 🍁"
        super().__init__(parent, title=title, on_close=on_close)

        if capitulo_id:
            c = self.db.obtener_uno("SELECT numero, titulo, plot_guia FROM capitulos WHERE id=?", (capitulo_id,))
            num, titulo, plot = c if c else ("", "", "")
        else:
            num = titulo = plot = ""

        flower = ImageUtils.load_flower("card_accent.png", (40, 40))
        if flower:
            ctk.CTkLabel(self.scroll, image=flower, text="").pack(pady=(10, 5))

        self.entry_num = self._add_field("Número:", "entry", default=str(num))
        self.entry_titulo = self._add_field("Título:", "entry", default=titulo or "")
        self.entry_plot = self._add_field("Plot guía:", "text", default=plot or "")

        ctk.CTkButton(
            self.scroll, text="Guardar 🍂", command=self._guardar, corner_radius=15,
            fg_color=COLORS["btn_primary"], hover_color=COLORS["btn_hover"],
            text_color=COLORS["text_light"], font=FONTS["heading"]
        ).pack(pady=20)

    def _guardar(self):
        num = self.entry_num.get()
        titulo = self.entry_titulo.get()
        plot = self.entry_plot.get("1.0", "end").strip()

        if self.capitulo_id:
            self.db.ejecutar(
                "UPDATE capitulos SET numero=?, titulo=?, plot_guia=? WHERE id=?",
                (num, titulo, plot, self.capitulo_id)
            )
        else:
            self.db.ejecutar(
                "INSERT INTO capitulos (historia_id, numero, titulo, plot_guia) VALUES (?, ?, ?, ?)",
                (self.historia_id, num, titulo, plot)
            )
        self._cerrar()


class ParteDialog(_BaseDialog):
    """Crear o editar una parte de capítulo."""

    def __init__(self, parent, db, capitulo_id, parte_id=None, nombre="", contenido="", on_close=None):
        self.db = db
        self.capitulo_id = capitulo_id
        self.parte_id = parte_id
        title = "🍁 Editar Parte 🍂" if parte_id else "🍂 Nueva Parte 🍁"
        super().__init__(parent, title=title, on_close=on_close)

        flower = ImageUtils.load_flower("card_accent.png", (35, 35))
        if flower:
            ctk.CTkLabel(self.scroll, image=flower, text="").pack(pady=(10, 5))

        self.entry_nombre = self._add_field("Nombre de la parte:", "entry", default=nombre)
        self.entry_cont = self._add_field("Contenido:", "text", default=contenido)

        ctk.CTkButton(
            self.scroll, text="Guardar 🍂", command=self._guardar, corner_radius=15,
            fg_color=COLORS["btn_primary"], hover_color=COLORS["btn_hover"],
            text_color=COLORS["text_light"], font=FONTS["heading"]
        ).pack(pady=15)

    def _guardar(self):
        nombre = self.entry_nombre.get()
        contenido = self.entry_cont.get("1.0", "end").strip()

        if self.parte_id:
            self.db.ejecutar(
                "UPDATE partes_capitulo SET nombre_parte=?, contenido=? WHERE id=?",
                (nombre, contenido, self.parte_id)
            )
        else:
            orden = len(self.db.obtener("SELECT id FROM partes_capitulo WHERE capitulo_id=?", (self.capitulo_id,))) + 1
            self.db.ejecutar(
                "INSERT INTO partes_capitulo (capitulo_id, nombre_parte, contenido, orden) VALUES (?, ?, ?, ?)",
                (self.capitulo_id, nombre, contenido, orden)
            )
        self._cerrar()


class RelacionDialog(ctk.CTkFrame):
    """Elegir tipo de relación entre dos personajes."""

    def __init__(self, parent, db, historia_id, p1_id, p2_id, nombres: tuple, on_close=None):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.historia_id = historia_id
        self.p1_id = p1_id
        self.p2_id = p2_id
        self.on_close = on_close

        from config import RELATION_COLORS

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(5, 0))
        ctk.CTkLabel(
            header, text="🍂 Tipo de conexión 🍁", font=FONTS["subtitle"],
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            header, text="✕", width=28, height=28, corner_radius=14,
            command=self._cerrar, fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"], text_color=COLORS["text_light"],
            font=FONTS["caption"]
        ).pack(side="right", padx=5)

        flower = ImageUtils.load_flower("card_accent.png", (50, 50))
        if flower:
            ctk.CTkLabel(self, image=flower, text="").pack(pady=(10, 5))

        ctk.CTkLabel(
            self, text="Conectar:", font=FONTS["heading"],
            text_color=COLORS["text_primary"]
        ).pack(pady=(5, 5))
        ctk.CTkLabel(
            self, text=f"{nombres[0]}  →  {nombres[1]}",
            font=FONTS["heading"], text_color=COLORS["accent"]
        ).pack()

        ctk.CTkLabel(
            self, text="Tipo de relación:", font=FONTS["heading"],
            text_color=COLORS["text_primary"]
        ).pack(pady=(15, 5))
        self.combo = ctk.CTkOptionMenu(
            self, values=list(RELATION_COLORS.keys()), width=250,
            fg_color=COLORS["bg_card"], text_color=COLORS["text_primary"],
            button_color=COLORS["btn_primary"], button_hover_color=COLORS["btn_hover"]
        )
        self.combo.pack()

        ctk.CTkButton(
            self, text="Conectar 🍂", command=self._guardar, corner_radius=15,
            fg_color=COLORS["btn_primary"], hover_color=COLORS["btn_hover"],
            text_color=COLORS["text_light"], font=FONTS["heading"]
        ).pack(pady=20)

    def _guardar(self):
        tipo = self.combo.get()
        existing = self.db.obtener_uno(
            "SELECT id FROM relaciones WHERE historia_id=? AND personaje1_id=? AND personaje2_id=?",
            (self.historia_id, self.p1_id, self.p2_id)
        )
        if existing:
            self.db.ejecutar("UPDATE relaciones SET tipo=? WHERE id=?", (tipo, existing[0]))
        else:
            self.db.ejecutar(
                "INSERT INTO relaciones (historia_id, personaje1_id, personaje2_id, tipo) VALUES (?, ?, ?, ?)",
                (self.historia_id, self.p1_id, self.p2_id, tipo)
            )
        self._cerrar()

    def _cerrar(self):
        if self.on_close:
            self.on_close()


class FichaPersonajeDialog(ctk.CTkFrame):
    """Muestra la ficha completa de un personaje (solo lectura)."""

    def __init__(self, parent, db, personaje_id, on_close=None):
        super().__init__(parent, fg_color="transparent")
        self.on_close = on_close

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(5, 0))
        ctk.CTkLabel(
            header, text="🍁 Ficha de Personaje 🍂", font=FONTS["subtitle"],
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            header, text="✕", width=28, height=28, corner_radius=14,
            command=self._cerrar, fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"], text_color=COLORS["text_light"],
            font=FONTS["caption"]
        ).pack(side="right", padx=5)

        p = db.obtener_uno("SELECT * FROM personajes WHERE id=?", (personaje_id,))
        if not p:
            ctk.CTkLabel(self, text="Personaje no encontrado", text_color=COLORS["text_primary"]).pack(pady=20)
            return

        flower = ImageUtils.load_flower("card_accent.png", (60, 60))
        if flower:
            ctk.CTkLabel(self, image=flower, text="").pack(pady=10)

        img = ImageUtils.blob_a_ctkimage(p[10], (200, 200))
        ctk.CTkLabel(self, image=img, text="").pack(pady=10)
        ctk.CTkLabel(
            self, text=p[2], font=("Playfair Display", 24, "bold"),
            text_color=COLORS["text_primary"]
        ).pack()
        ctk.CTkLabel(
            self, text=f"Categoría: {p[3].capitalize()}  |  Edad: {p[4] or 'N/A'}",
            font=FONTS["body"], text_color=COLORS["text_secondary"]
        ).pack()

        ImageUtils.add_divider(self, pady=10)

        campos = [
            ("Familia", p[5]), ("Historia", p[6]), ("Trauma", p[7]),
            ("Rol en Plot", p[8]), ("Guía de Trama", p[9])
        ]
        for titulo, valor in campos:
            if valor:
                ctk.CTkLabel(
                    self, text=f"🍂 {titulo}:", font=FONTS["heading"],
                    text_color=COLORS["accent"]
                ).pack(pady=(10, 2))
                ctk.CTkLabel(
                    self, text=valor, font=FONTS["body"],
                    text_color=COLORS["text_secondary"], wraplength=450
                ).pack()

        ctk.CTkButton(
            self, text="Cerrar", command=self._cerrar, corner_radius=15,
            fg_color=COLORS["btn_primary"], hover_color=COLORS["btn_hover"],
            text_color=COLORS["text_light"], font=FONTS["heading"]
        ).pack(pady=20)

        flower2 = ImageUtils.load_flower("card_accent.png", (50, 50))
        if flower2:
            ctk.CTkLabel(self, image=flower2, text="").pack(pady=15)

    def _cerrar(self):
        if self.on_close:
            self.on_close()