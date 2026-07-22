"""Recortador de imágenes con selección manual de área"""

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import customtkinter as ctk
from config import FONTS, COLORS


class ImageCropper(ctk.CTkToplevel):
    """
    Ventana modal para seleccionar un área cuadrada de una imagen.

    Uso:
        cropper = ImageCropper(parent, on_crop=callback)
        cropper.wait_window()  # Bloquea hasta que el usuario termine

    El callback recibe: (blob_bytes, preview_ctkimage)
    """

    SELECTION_SIZE = 300  # Tamaño del cuadrado de selección
    PREVIEW_SIZE = 200    # Tamaño de la vista previa

    def __init__(self, parent, on_crop=None, title="Recortar imagen", aspect_ratio="square"):
        super().__init__(parent)
        self.title(title)
        self.on_crop = on_crop
        self.aspect_ratio = aspect_ratio  # "square", "portrait", "landscape"
        self.result = None

        # Configurar tamaño y posición centrada
        self.geometry("900x700")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.original_image = None
        self.display_image = None
        self.photo_image = None
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0

        # Coordenadas del área de selección (en coordenadas de la imagen original)
        self.sel_x = 0
        self.sel_y = 0
        self.sel_w = 0
        self.sel_h = 0
        self.dragging = False
        self.drag_start = (0, 0)
        self.sel_start = (0, 0)

        self._build_ui()
        self._cargar_imagen()

    def _build_ui(self):
        """Construye la interfaz."""
        self.configure(fg_color=COLORS["bg_principal"])

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            header, text="Selecciona el area de la imagen que quieres guardar",
            font=FONTS["heading"], text_color=COLORS["text_primary"]
        ).pack(side="left")

        ctk.CTkButton(
            header, text="X", width=32, height=32, corner_radius=16,
            command=self._cancelar, fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"], text_color=COLORS["text_light"],
            font=FONTS["caption"]
        ).pack(side="right")

        # Contenedor principal
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=10)

        # Panel izquierdo: Canvas con imagen
        left_panel = ctk.CTkFrame(main, fg_color=COLORS["bg_card"], corner_radius=15,
                                   border_color=COLORS["border_card"], border_width=2)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.canvas = tk.Canvas(
            left_panel, bg=COLORS["bg_card"], highlightthickness=0,
            width=600, height=500
        )
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        # Panel derecho: Controles y preview
        right_panel = ctk.CTkFrame(main, fg_color="transparent", width=250)
        right_panel.pack(side="right", fill="y", padx=(10, 0))
        right_panel.pack_propagate(False)

        # Instrucciones
        instrucciones = ctk.CTkFrame(right_panel, fg_color=COLORS["bg_dialog"], corner_radius=10)
        instrucciones.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(
            instrucciones,
            text="Arrastra el cuadrado para moverlo.\n"
                 "Usa la rueda del raton para zoom.\n"
                 "Haz doble clic en el cuadrado para recortar.",
            font=FONTS["small"], text_color=COLORS["text_secondary"],
            wraplength=220
        ).pack(padx=10, pady=10)

        # Vista previa
        ctk.CTkLabel(
            right_panel, text="Vista previa:", font=FONTS["heading"],
            text_color=COLORS["text_primary"]
        ).pack(pady=(0, 5))

        self.preview_frame = ctk.CTkFrame(
            right_panel, fg_color=COLORS["bg_card"], corner_radius=10,
            border_color=COLORS["border_card"], border_width=2,
            width=self.PREVIEW_SIZE, height=self.PREVIEW_SIZE
        )
        self.preview_frame.pack(pady=5)
        self.preview_frame.pack_propagate(False)

        self.preview_label = ctk.CTkLabel(self.preview_frame, text="")
        self.preview_label.pack(expand=True)

        # Controles de tamaño
        ctk.CTkLabel(
            right_panel, text="Tamaño del recorte:", font=FONTS["body"],
            text_color=COLORS["text_primary"]
        ).pack(pady=(15, 5))

        size_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        size_frame.pack()

        self.slider_size = ctk.CTkSlider(
            size_frame, from_=100, to=600, number_of_steps=50,
            width=180, command=self._on_size_change
        )
        self.slider_size.set(self.SELECTION_SIZE)
        self.slider_size.pack()

        self.lbl_size = ctk.CTkLabel(
            size_frame, text=f"{self.SELECTION_SIZE}px", font=FONTS["caption"],
            text_color=COLORS["text_secondary"]
        )
        self.lbl_size.pack()

        # Botones
        btn_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(
            btn_frame, text="Recortar y guardar", command=self._aplicar_recorte,
            corner_radius=15, width=180, height=40,
            fg_color=COLORS["btn_primary"], hover_color=COLORS["btn_hover"],
            text_color=COLORS["text_light"], font=FONTS["heading"]
        ).pack(pady=5)

        ctk.CTkButton(
            btn_frame, text="Cancelar", command=self._cancelar,
            corner_radius=15, width=180, height=35,
            fg_color=COLORS["gray"], hover_color=COLORS["danger_hover"],
            text_color=COLORS["text_light"], font=FONTS["body"]
        ).pack(pady=5)

        # Eventos del canvas
        self.canvas.bind("<Button-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<MouseWheel>", self._on_scroll)
        self.canvas.bind("<Double-Button-1>", lambda e: self._aplicar_recorte())

    def _cargar_imagen(self):
        """Abre diálogo para seleccionar imagen y la carga."""
        ruta = filedialog.askopenfilename(
            parent=self,
            title="Seleccionar imagen",
            filetypes=[
                ("Imagenes", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("Todos", "*.*")
            ]
        )
        if not ruta:
            self._cancelar()
            return

        try:
            self.original_image = Image.open(ruta).convert("RGBA")
            self._ajustar_imagen_al_canvas()
            self._inicializar_seleccion()
            self._dibujar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen: {e}")
            self._cancelar()

    def _ajustar_imagen_al_canvas(self):
        """Escala la imagen para que quepa en el canvas manteniendo proporción."""
        canvas_w = self.canvas.winfo_width() or 600
        canvas_h = self.canvas.winfo_height() or 500

        img_w, img_h = self.original_image.size

        # Calcular escala para que quepa
        scale_w = canvas_w / img_w
        scale_h = canvas_h / img_h
        self.scale = min(scale_w, scale_h) * 0.9  # 90% para dejar margen

        # Calcular tamaño display
        disp_w = int(img_w * self.scale)
        disp_h = int(img_h * self.scale)

        # Centrar
        self.offset_x = (canvas_w - disp_w) // 2
        self.offset_y = (canvas_h - disp_h) // 2

        # Redimensionar para display
        self.display_image = self.original_image.resize((disp_w, disp_h), Image.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(self.display_image)

    def _inicializar_seleccion(self):
        """Inicializa el área de selección centrada."""
        disp_w = self.display_image.width
        disp_h = self.display_image.height

        size = min(self.SELECTION_SIZE, disp_w, disp_h)
        self.sel_w = int(size / self.scale)
        self.sel_h = int(size / self.scale)

        # Centrar en la imagen original
        img_w, img_h = self.original_image.size
        self.sel_x = (img_w - self.sel_w) // 2
        self.sel_y = (img_h - self.sel_h) // 2

        self._actualizar_preview()

    def _dibujar(self):
        """Dibuja la imagen y el área de selección en el canvas."""
        self.canvas.delete("all")

        if self.photo_image:
            self.canvas.create_image(
                self.offset_x, self.offset_y,
                image=self.photo_image, anchor="nw"
            )

        # Calcular coordenadas de la selección en pantalla
        screen_x = self.offset_x + int(self.sel_x * self.scale)
        screen_y = self.offset_y + int(self.sel_y * self.scale)
        screen_w = int(self.sel_w * self.scale)
        screen_h = int(self.sel_h * self.scale)

        # Dibujar overlay oscuro fuera de la selección
        canvas_w = self.canvas.winfo_width() or 600
        canvas_h = self.canvas.winfo_height() or 500

        # Rectángulos oscuros alrededor
        overlay_color = "#000000"
        overlay_alpha = 0.4

        # Arriba
        self.canvas.create_rectangle(
            0, 0, canvas_w, screen_y,
            fill=overlay_color, stipple="gray50", outline=""
        )
        # Abajo
        self.canvas.create_rectangle(
            0, screen_y + screen_h, canvas_w, canvas_h,
            fill=overlay_color, stipple="gray50", outline=""
        )
        # Izquierda
        self.canvas.create_rectangle(
            0, screen_y, screen_x, screen_y + screen_h,
            fill=overlay_color, stipple="gray50", outline=""
        )
        # Derecha
        self.canvas.create_rectangle(
            screen_x + screen_w, screen_y, canvas_w, screen_y + screen_h,
            fill=overlay_color, stipple="gray50", outline=""
        )

        # Borde de la selección
        self.canvas.create_rectangle(
            screen_x, screen_y, screen_x + screen_w, screen_y + screen_h,
            outline="#D2691E", width=3, dash=(6, 4)
        )

        # Esquinas de la selección
        corner_size = 8
        for cx, cy in [
            (screen_x, screen_y),  # TL
            (screen_x + screen_w, screen_y),  # TR
            (screen_x, screen_y + screen_h),  # BL
            (screen_x + screen_w, screen_y + screen_h),  # BR
        ]:
            self.canvas.create_oval(
                cx - corner_size, cy - corner_size,
                cx + corner_size, cy + corner_size,
                fill="#D2691E", outline=""
            )

    def _on_press(self, event):
        """Inicia el arrastre de la selección."""
        # Verificar si el click está dentro de la selección
        screen_x = self.offset_x + int(self.sel_x * self.scale)
        screen_y = self.offset_y + int(self.sel_y * self.scale)
        screen_w = int(self.sel_w * self.scale)
        screen_h = int(self.sel_h * self.scale)

        if (screen_x <= event.x <= screen_x + screen_w and
            screen_y <= event.y <= screen_y + screen_h):
            self.dragging = True
            self.drag_start = (event.x, event.y)
            self.sel_start = (self.sel_x, self.sel_y)

    def _on_drag(self, event):
        """Mueve la selección."""
        if not self.dragging:
            return

        dx = int((event.x - self.drag_start[0]) / self.scale)
        dy = int((event.y - self.drag_start[1]) / self.scale)

        img_w, img_h = self.original_image.size

        # Calcular nueva posición
        new_x = self.sel_start[0] + dx
        new_y = self.sel_start[1] + dy

        # Limitar a los bordes de la imagen
        new_x = max(0, min(new_x, img_w - self.sel_w))
        new_y = max(0, min(new_y, img_h - self.sel_h))

        self.sel_x = new_x
        self.sel_y = new_y

        self._dibujar()
        self._actualizar_preview()

    def _on_release(self, event):
        """Termina el arrastre."""
        self.dragging = False

    def _on_scroll(self, event):
        """Ajusta el tamaño de la selección con la rueda del ratón."""
        delta = 20 if event.delta > 0 else -20
        nuevo_size = self.sel_w + delta

        img_w, img_h = self.original_image.size
        max_size = min(img_w, img_h)
        nuevo_size = max(50, min(nuevo_size, max_size))

        # Ajustar manteniendo centrado
        centro_x = self.sel_x + self.sel_w // 2
        centro_y = self.sel_y + self.sel_h // 2

        self.sel_w = nuevo_size
        self.sel_h = nuevo_size

        self.sel_x = max(0, min(centro_x - nuevo_size // 2, img_w - nuevo_size))
        self.sel_y = max(0, min(centro_y - nuevo_size // 2, img_h - nuevo_size))

        self.slider_size.set(nuevo_size)
        self.lbl_size.configure(text=f"{nuevo_size}px")

        self._dibujar()
        self._actualizar_preview()

    def _on_size_change(self, value):
        """Cambia el tamaño desde el slider."""
        nuevo_size = int(value)

        img_w, img_h = self.original_image.size
        max_size = min(img_w, img_h)
        nuevo_size = max(50, min(nuevo_size, max_size))

        # Ajustar manteniendo centrado
        centro_x = self.sel_x + self.sel_w // 2
        centro_y = self.sel_y + self.sel_h // 2

        self.sel_w = nuevo_size
        self.sel_h = nuevo_size

        self.sel_x = max(0, min(centro_x - nuevo_size // 2, img_w - nuevo_size))
        self.sel_y = max(0, min(centro_y - nuevo_size // 2, img_h - nuevo_size))

        self.lbl_size.configure(text=f"{nuevo_size}px")
        self._dibujar()
        self._actualizar_preview()

    def _actualizar_preview(self):
        """Actualiza la vista previa del recorte."""
        if self.original_image is None:
            return

        # Recortar de la imagen original
        crop = self.original_image.crop((
            self.sel_x, self.sel_y,
            self.sel_x + self.sel_w, self.sel_y + self.sel_h
        ))

        # Redimensionar para preview
        preview = crop.resize((self.PREVIEW_SIZE, self.PREVIEW_SIZE), Image.LANCZOS)

        # Convertir a CTkImage
        self.preview_image = ctk.CTkImage(light_image=preview, dark_image=preview,
                                           size=(self.PREVIEW_SIZE, self.PREVIEW_SIZE))
        self.preview_label.configure(image=self.preview_image)

    def _aplicar_recorte(self):
        """Aplica el recorte y devuelve el resultado."""
        if self.original_image is None:
            return

        try:
            # Recortar de la imagen original
            crop = self.original_image.crop((
                self.sel_x, self.sel_y,
                self.sel_x + self.sel_w, self.sel_y + self.sel_h
            ))

            # Redimensionar a tamaño máximo razonable
            max_size = 600
            crop.thumbnail((max_size, max_size), Image.LANCZOS)

            # Convertir a blob
            import io
            buffer = io.BytesIO()
            crop.convert("RGB").save(buffer, format="PNG")
            blob = buffer.getvalue()

            # Crear preview para devolver
            preview = crop.resize((200, 200), Image.LANCZOS)
            preview_ctk = ctk.CTkImage(light_image=preview, dark_image=preview,
                                        size=(200, 200))

            self.result = (blob, preview_ctk)

            if self.on_crop:
                self.on_crop(blob, preview_ctk)

            self.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo recortar la imagen: {e}")

    def _cancelar(self):
        """Cancela sin guardar."""
        self.result = None
        if self.on_crop:
            self.on_crop(None, None)
        self.destroy()


def seleccionar_imagen_recortada(parent, on_crop):
    """
    Función utilitaria para abrir el recortador.

    Args:
        parent: Widget padre
        on_crop: Callback(blob, preview_image) o (None, None) si cancela
    """
    cropper = ImageCropper(parent, on_crop=on_crop)
    return cropper