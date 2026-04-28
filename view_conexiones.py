import os
"""Mapa interactivo de relaciones entre personajes - Tema Jardín."""

import tkinter as tk
from tkinter import Menu, messagebox
import customtkinter as ctk
from config import FONTS, COLORS, RELATION_COLORS, NODE_RADIUS, FLOWERS_DIR
from utils import ImageUtils
from dialogs import RelacionDialog, FichaPersonajeDialog


class ConexionesView(ctk.CTkFrame):
    """Canvas interactivo para visualizar y editar relaciones entre personajes."""

    def __init__(self, parent, db, historia_id):
        super().__init__(parent, fg_color=COLORS["bg_principal"])
        self.db = db
        self.historia_id = historia_id
        self.pack(fill="both", expand=True)

        self.modo = "mover"

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=5, padx=10)
        ctk.CTkLabel(
            top, text="🕸️ Mapa de Conexiones", font=FONTS["subtitle"],
            text_color=COLORS["text_primary"]
        ).pack(side="left")

        flower = ImageUtils.load_flower("card_accent.png", (35, 35))
        if flower:
            ctk.CTkLabel(top, image=flower, text="").pack(side="left", padx=8)

        self.btn_modo = ctk.CTkButton(
            top, text="✋  Modo: Mover", command=self._toggle_modo,
            fg_color=COLORS["btn_primary"], hover_color=COLORS["btn_hover"],
            text_color=COLORS["text_light"],
            corner_radius=15, width=160, height=35
        )
        self.btn_modo.pack(side="right", padx=5)

        ctk.CTkButton(
            top, text="➕ Añadir personaje", command=self._mostrar_picker,
            corner_radius=15, width=140,
            fg_color=COLORS["btn_accent"], hover_color=COLORS["btn_accent_hover"],
            text_color=COLORS["text_light"]
        ).pack(side="right", padx=5)
        ctk.CTkButton(
            top, text="💾 Guardar posiciones", command=self._guardar_posiciones,
            corner_radius=15, width=140,
            fg_color=COLORS["success"], hover_color="#66BB6A",
            text_color=COLORS["text_light"]
        ).pack(side="right", padx=5)

        leyenda = ctk.CTkFrame(self, fg_color="transparent")
        leyenda.pack(fill="x", padx=10)
        for tipo, color in RELATION_COLORS.items():
            f = ctk.CTkFrame(leyenda, width=12, height=12, corner_radius=6, fg_color=color)
            f.pack(side="left", padx=(0, 4))
            ctk.CTkLabel(leyenda, text=tipo, font=FONTS["caption"], text_color=COLORS["text_secondary"]).pack(side="left", padx=(0, 12))

        self.lbl_ayuda = ctk.CTkLabel(
            leyenda,
            text="Arrastra nodos para moverlos  •  Doble clic para ver ficha  •  Click derecho para opciones",
            font=FONTS["caption"], text_color=COLORS["text_secondary"]
        )
        self.lbl_ayuda.pack(side="left", padx=20)

        canvas_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"],
                                    border_color=COLORS["border_card"], border_width=2)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(canvas_frame, bg="#FFF8F5", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self._fondo_floral = None
        self._cargar_fondo_floral()

        self.nodos = {}
        self.conexiones = []
        self._drag = {"nodo": None, "ox": 0, "oy": 0, "linea_temp": None}

        self.canvas.bind("<Button-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Double-Button-1>", self._on_double_click)
        self.canvas.bind("<Button-3>", self._on_right_click)

        self._cargar_datos()

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

    def _cargar_fondo_floral(self):
        try:
            from PIL import ImageTk
            img = ImageUtils.load_flower("canvas_bg.png")
            if img:
                self.canvas.update_idletasks()
                w = self.canvas.winfo_width() or 800
                h = self.canvas.winfo_height() or 600
                from PIL import Image
                pil_img = Image.open(os.path.join(FLOWERS_DIR, "canvas_bg.png"))
                pil_img = pil_img.resize((w, h), Image.LANCZOS)
                self._fondo_floral = ImageTk.PhotoImage(pil_img)
                self.canvas.create_image(0, 0, image=self._fondo_floral, anchor="nw", tags="fondo")
                self.canvas.tag_lower("fondo")
        except Exception:
            pass

    def _toggle_modo(self):
        if self.modo == "mover":
            self.modo = "conectar"
            self.btn_modo.configure(
                text="🔗  Modo: Conectar",
                fg_color=COLORS["accent"], hover_color="#C2185B"
            )
            self.lbl_ayuda.configure(
                text="Arrastra desde un nodo a otro para crear una conexión  •  Doble clic para ver ficha"
            )
            self.canvas.configure(cursor="crosshair")
        else:
            self.modo = "mover"
            self.btn_modo.configure(
                text="✋  Modo: Mover",
                fg_color=COLORS["btn_primary"], hover_color=COLORS["btn_hover"]
            )
            self.lbl_ayuda.configure(
                text="Arrastra nodos para moverlos  •  Doble clic para ver ficha  •  Click derecho para opciones"
            )
            self.canvas.configure(cursor="")

    def _cargar_datos(self):
        self.canvas.delete("all")
        self.nodos.clear()
        self.conexiones.clear()

        if self._fondo_floral:
            self.canvas.create_image(0, 0, image=self._fondo_floral, anchor="nw", tags="fondo")
            self.canvas.tag_lower("fondo")

        personajes = self.db.obtener("""
            SELECT p.id, p.nombre, p.foto_blob,
                   COALESCE(pos.x, 100 + (p.id % 5) * 150),
                   COALESCE(pos.y, 100 + (p.id / 5) * 150)
            FROM personajes p
            LEFT JOIN posiciones_nodos pos ON pos.personaje_id = p.id AND pos.historia_id = ?
            WHERE p.historia_id = ?
        """, (self.historia_id, self.historia_id))

        for pid, nombre, foto_blob, x, y in personajes:
            self._crear_nodo(pid, nombre, foto_blob, x, y)

        rels = self.db.obtener(
            "SELECT id, personaje1_id, personaje2_id, tipo FROM relaciones WHERE historia_id=?",
            (self.historia_id,)
        )
        for rid, p1, p2, tipo in rels:
            if p1 in self.nodos and p2 in self.nodos:
                self._dibujar_conexion(rid, p1, p2, tipo)

    def _crear_nodo(self, pid, nombre, foto_blob, x, y):
        foto_tk = ImageUtils.blob_a_tkimage(foto_blob)
        r = NODE_RADIUS

        circulo = self.canvas.create_oval(
            x - r, y - r, x + r, y + r,
            fill="#FFF0F5", outline="#D4A5A5", width=3, tags=f"nodo_{pid}"
        )
        imagen = self.canvas.create_image(x, y, image=foto_tk, tags=f"nodo_{pid}")
        texto = self.canvas.create_text(
            x, y + r + 15, text=nombre, fill="#5D4037",
            font=("Segoe UI", 10, "bold"), tags=f"nodo_{pid}"
        )
        hit = self.canvas.create_oval(
            x - r, y - r, x + r, y + r,
            fill="", outline="", tags=f"nodo_{pid}"
        )
        self.canvas.tag_raise(hit)

        self.nodos[pid] = {
            "x": x, "y": y, "items": [circulo, imagen, texto, hit],
            "foto_tk": foto_tk, "nombre": nombre
        }

    def _coords_conexion(self, p1, p2):
        x1, y1 = self.nodos[p1]["x"], self.nodos[p1]["y"]
        x2, y2 = self.nodos[p2]["x"], self.nodos[p2]["y"]
        dx, dy = x2 - x1, y2 - y1
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist == 0:
            return None
        dx, dy = dx / dist, dy / dist
        x1b = x1 + dx * NODE_RADIUS
        y1b = y1 + dy * NODE_RADIUS
        x2b = x2 - dx * NODE_RADIUS
        y2b = y2 - dy * NODE_RADIUS
        mx, my = (x1b + x2b) / 2, (y1b + y2b) / 2
        return x1b, y1b, x2b, y2b, mx, my

    def _dibujar_conexion(self, rid, p1, p2, tipo):
        coords = self._coords_conexion(p1, p2)
        if coords is None:
            return
        x1b, y1b, x2b, y2b, mx, my = coords
        color = RELATION_COLORS.get(tipo, "#888888")
        dash = (6, 4) if tipo == "pareja" else ()
        line_id = self.canvas.create_line(
            x1b, y1b, x2b, y2b, fill=color, width=3, dash=dash, tags=f"rel_{rid}"
        )
        text_id = self.canvas.create_text(
            mx, my - 8, text=tipo, fill=color, font=("Segoe UI", 9), tags=f"rel_{rid}"
        )
        self.conexiones.append((rid, p1, p2, tipo, line_id, text_id))

    def _actualizar_conexion(self, p1, p2, line_id, text_id):
        coords = self._coords_conexion(p1, p2)
        if coords is None:
            return
        x1b, y1b, x2b, y2b, mx, my = coords
        self.canvas.coords(line_id, x1b, y1b, x2b, y2b)
        self.canvas.coords(text_id, mx, my - 8)

    def _redibujar_conexiones(self):
        for rid, p1, p2, tipo, line_id, text_id in self.conexiones:
            self.canvas.delete(line_id)
            self.canvas.delete(text_id)
        self.conexiones.clear()

        rels = self.db.obtener(
            "SELECT id, personaje1_id, personaje2_id, tipo FROM relaciones WHERE historia_id=?",
            (self.historia_id,)
        )
        for rid, p1, p2, tipo in rels:
            if p1 in self.nodos and p2 in self.nodos:
                self._dibujar_conexion(rid, p1, p2, tipo)

    def _nodo_en_coords(self, x, y):
        items = self.canvas.find_overlapping(x - 5, y - 5, x + 5, y + 5)
        for item in items:
            for tag in self.canvas.gettags(item):
                if tag.startswith("nodo_"):
                    return int(tag.split("_")[1])
        return None

    def _on_press(self, event):
        pid = self._nodo_en_coords(event.x, event.y)
        if pid is not None:
            self._drag["nodo"] = pid
            self._drag["ox"] = event.x - self.nodos[pid]["x"]
            self._drag["oy"] = event.y - self.nodos[pid]["y"]

    def _on_drag(self, event):
        if self._drag["nodo"] is None:
            return

        pid = self._drag["nodo"]

        if self.modo == "mover":
            nx = event.x - self._drag["ox"]
            ny = event.y - self._drag["oy"]
            self._mover_nodo(pid, nx, ny)

        elif self.modo == "conectar":
            cx, cy = self.nodos[pid]["x"], self.nodos[pid]["y"]
            dx, dy = event.x - cx, event.y - cy
            d = (dx ** 2 + dy ** 2) ** 0.5
            if d == 0:
                return
            ux, uy = dx / d, dy / d
            x1 = cx + ux * NODE_RADIUS
            y1 = cy + uy * NODE_RADIUS

            if self._drag["linea_temp"] is None:
                self._drag["linea_temp"] = self.canvas.create_line(
                    x1, y1, event.x, event.y, fill="#D4A5A5", width=2, dash=(4, 4)
                )
            else:
                self.canvas.coords(self._drag["linea_temp"], x1, y1, event.x, event.y)

    def _mover_nodo(self, pid, x, y):
        dx = x - self.nodos[pid]["x"]
        dy = y - self.nodos[pid]["y"]
        self.nodos[pid]["x"] = x
        self.nodos[pid]["y"] = y

        for item in self.nodos[pid]["items"]:
            self.canvas.move(item, dx, dy)

        for rid, p1, p2, tipo, line_id, text_id in self.conexiones:
            if p1 == pid or p2 == pid:
                self._actualizar_conexion(p1, p2, line_id, text_id)

    def _on_release(self, event):
        pid_origen = self._drag["nodo"]
        linea_temp = self._drag["linea_temp"]

        if self.modo == "conectar" and linea_temp and pid_origen is not None:
            pid_destino = self._nodo_en_coords(event.x, event.y)
            if pid_destino is not None and pid_destino != pid_origen:
                self._preguntar_tipo(pid_origen, pid_destino)
            self.canvas.delete(linea_temp)

        self._drag = {"nodo": None, "ox": 0, "oy": 0, "linea_temp": None}

    def _preguntar_tipo(self, p1, p2):
        self._abrir_dialogo_embebido(
            RelacionDialog, self.db, self.historia_id, p1, p2,
            (self.nodos[p1]["nombre"], self.nodos[p2]["nombre"]),
            on_close=self._redibujar_conexiones
        )

    def _on_double_click(self, event):
        pid = self._nodo_en_coords(event.x, event.y)
        if pid:
            self._abrir_dialogo_embebido(FichaPersonajeDialog, self.db, pid)

    def _on_right_click(self, event):
        items = self.canvas.find_overlapping(event.x - 8, event.y - 8, event.x + 8, event.y + 8)
        for item in items:
            for tag in self.canvas.gettags(item):
                if tag.startswith("rel_"):
                    rid = int(tag.split("_")[1])
                    self._menu_linea(event.x_root, event.y_root, rid)
                    return

        pid = self._nodo_en_coords(event.x, event.y)
        if pid:
            self._menu_nodo(event.x_root, event.y_root, pid)

    def _menu_linea(self, x, y, rid):
        menu = Menu(self, tearoff=0, bg="#FFF0F5", fg="#5D4037", activebackground="#FFB6C1")
        menu.add_command(label="🗑 Borrar conexión", command=lambda: self._borrar_linea(rid))
        menu.tk_popup(x, y)

    def _borrar_linea(self, rid):
        if messagebox.askyesno("Confirmar", "¿Borrar esta conexión?"):
            self.db.ejecutar("DELETE FROM relaciones WHERE id=?", (rid,))
            self._redibujar_conexiones()

    def _menu_nodo(self, x, y, pid):
        menu = Menu(self, tearoff=0, bg="#FFF0F5", fg="#5D4037", activebackground="#FFB6C1")
        menu.add_command(label="👁 Ver ficha", command=lambda: self._abrir_dialogo_embebido(FichaPersonajeDialog, self.db, pid))
        menu.add_command(label="🗑 Quitar del mapa", command=lambda: self._quitar_nodo(pid))
        menu.tk_popup(x, y)

    def _quitar_nodo(self, pid):
        self.db.ejecutar(
            "DELETE FROM posiciones_nodos WHERE historia_id=? AND personaje_id=?",
            (self.historia_id, pid)
        )
        self.db.ejecutar(
            "DELETE FROM relaciones WHERE historia_id=? AND (personaje1_id=? OR personaje2_id=?)",
            (self.historia_id, pid, pid)
        )
        self._cargar_datos()

    def _mostrar_picker(self):
        overlay = ctk.CTkFrame(self, fg_color=COLORS["bg_principal"])
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        container = ctk.CTkFrame(
            overlay, fg_color=COLORS["bg_dialog"], corner_radius=20,
            border_color=COLORS["border_card"], border_width=2,
            width=420, height=450
        )
        container.place(relx=0.5, rely=0.5, anchor="center")
        container.pack_propagate(False)

        def _cerrar():
            overlay.destroy()

        scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(10, 0))
        ctk.CTkLabel(
            header, text="Añadir personajes al mapa", font=FONTS["heading"],
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        ctk.CTkButton(
            header, text="✕", width=28, height=28, corner_radius=14,
            command=_cerrar, fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"], text_color=COLORS["text_light"],
            font=FONTS["caption"]
        ).pack(side="right")

        personajes = self.db.obtener("""
            SELECT id, nombre, foto_blob FROM personajes
            WHERE historia_id=? AND id NOT IN (
                SELECT personaje_id FROM posiciones_nodos WHERE historia_id=?
            )
        """, (self.historia_id, self.historia_id))

        if not personajes:
            ctk.CTkLabel(
                scroll, text="Todos los personajes ya están en el mapa.",
                text_color=COLORS["text_secondary"]
            ).pack(pady=20)
            return

        ctk.CTkLabel(
            scroll, text="Haz clic para añadir:", font=FONTS["heading"],
            text_color=COLORS["text_primary"]
        ).pack(pady=10)

        for pid, nombre, foto in personajes:
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=3)
            img = ImageUtils.blob_a_ctkimage(foto, (40, 40))
            ctk.CTkLabel(row, image=img, text="").pack(side="left", padx=5)
            ctk.CTkLabel(
                row, text=nombre, font=FONTS["body"], text_color=COLORS["text_primary"]
            ).pack(side="left", padx=10)
            ctk.CTkButton(
                row, text="➕", width=40, corner_radius=8,
                fg_color=COLORS["btn_accent"], hover_color=COLORS["btn_accent_hover"],
                command=lambda p=pid: self._add_personaje(overlay, p)
            ).pack(side="right")

    def _add_personaje(self, overlay, pid):
        count = len(self.nodos)
        x = 150 + (count % 4) * 180
        y = 150 + (count // 4) * 180
        self.db.ejecutar(
            "INSERT OR REPLACE INTO posiciones_nodos (historia_id, personaje_id, x, y) VALUES (?, ?, ?, ?)",
            (self.historia_id, pid, x, y)
        )
        overlay.destroy()
        self._cargar_datos()

    def _guardar_posiciones(self):
        for pid, data in self.nodos.items():
            self.db.ejecutar(
                "INSERT OR REPLACE INTO posiciones_nodos (historia_id, personaje_id, x, y) VALUES (?, ?, ?, ?)",
                (self.historia_id, pid, data["x"], data["y"])
            )
        messagebox.showinfo("Guardado", "Posiciones guardadas correctamente. 🌸")