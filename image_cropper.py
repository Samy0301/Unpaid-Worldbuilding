"""Recortador de imagenes con seleccion tipo galeria - arrastra esquinas/bordes"""

import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageOps  # Añadido ImageOps
import customtkinter as ctk
from config import FONTS, COLORS

class ImageCropper(ctk.CTkFrame):
    PREVIEW_SIZE = 220
    HANDLE_SIZE = 10
    MIN_CROP = 40

    def __init__(self, parent, on_crop=None, on_cancel=None, shape="square"):
        super().__init__(parent, fg_color=COLORS["bg_principal"])
        self.on_crop = on_crop
        self.on_cancel = on_cancel
        self.shape = shape
        self.result = None

        self.original_image = None
        self.display_image = None
        self.photo_image = None
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0

        self.crop_x1 = 0
        self.crop_y1 = 0
        self.crop_x2 = 0
        self.crop_y2 = 0

        self.drag_mode = None
        self.drag_start = (0, 0)
        self.crop_start = (0, 0, 0, 0)

        self._build_ui()

    def _build_ui(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=5, pady=5)

        # Panel izquierdo: El lienzo de edición es ahora más ancho para fotos horizontales
        left_panel = ctk.CTkFrame(main, fg_color=COLORS["bg_card"], corner_radius=15,
                                border_color=COLORS["border_card"], border_width=2)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.canvas = tk.Canvas(
            left_panel, bg=COLORS["bg_card"], highlightthickness=0,
            width=600, height=450
        )
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        right_panel = ctk.CTkFrame(main, fg_color="transparent", width=250)
        right_panel.pack(side="right", fill="y", padx=(10, 0))
        right_panel.pack_propagate(False)

        ctk.CTkLabel(
            right_panel, text="Vista previa:", font=FONTS["heading"],
            text_color=COLORS["text_primary"]
        ).pack(pady=(10, 5))

        self.preview_frame = ctk.CTkFrame(
            right_panel, fg_color=COLORS["bg_card"], corner_radius=10,
            border_color=COLORS["border_card"], border_width=1,
            width=self.PREVIEW_SIZE, height=self.PREVIEW_SIZE
        )
        self.preview_frame.pack(pady=5)
        self.preview_frame.pack_propagate(False)

        self.preview_label = ctk.CTkLabel(self.preview_frame, text="")
        self.preview_label.pack(expand=True)

        self.lbl_dims = ctk.CTkLabel(
            right_panel, text="", font=FONTS["caption"],
            text_color=COLORS["text_secondary"]
        )
        self.lbl_dims.pack(pady=(10, 5))

        # Solo el botón de guardar
        ctk.CTkButton(
            right_panel, text="Guardar", command=self._aplicar_recorte,
            corner_radius=15, width=200, height=45,
            fg_color=COLORS["btn_primary"], hover_color=COLORS["btn_hover"],
            text_color=COLORS["text_light"], font=FONTS["heading"]
        ).pack(side="bottom", pady=20)

        self.canvas.bind("<Button-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

    def cargar_imagen(self, ruta):
        try:
            # ImageOps.exif_transpose corrige la rotación automática de cámaras/móviles
            img = Image.open(ruta)
            self.original_image = ImageOps.exif_transpose(img).convert("RGBA")
            
            self._ajustar_imagen_al_canvas()
            
            # Inicializar recorte a toda la imagen (respeta si es horizontal)
            self.crop_x1, self.crop_y1 = 0, 0
            self.crop_x2, self.crop_y2 = self.original_image.size
            
            self._dibujar()
            self._actualizar_preview()
            return True
        except Exception as e:
            print(f"Error cargando imagen: {e}")
            return False

    def _ajustar_imagen_al_canvas(self):
        self.canvas.update_idletasks()
        canvas_w = self.canvas.winfo_width() or 600
        canvas_h = self.canvas.winfo_height() or 450

        img_w, img_h = self.original_image.size
        scale_w = canvas_w / img_w
        scale_h = canvas_h / img_h
        self.scale = min(scale_w, scale_h) * 0.95

        disp_w = int(img_w * self.scale)
        disp_h = int(img_h * self.scale)

        self.offset_x = (canvas_w - disp_w) // 2
        self.offset_y = (canvas_h - disp_h) // 2

        self.display_image = self.original_image.resize((disp_w, disp_h), Image.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(self.display_image)

    def _img_to_screen(self, ix, iy):
        return self.offset_x + int(ix * self.scale), self.offset_y + int(iy * self.scale)

    def _dibujar(self):
        self.canvas.delete("all")
        if self.photo_image:
            self.canvas.create_image(self.offset_x, self.offset_y, image=self.photo_image, anchor="nw")

        sx1, sy1 = self._img_to_screen(self.crop_x1, self.crop_y1)
        sx2, sy2 = self._img_to_screen(self.crop_x2, self.crop_y2)

        # Overlay oscuro
        self.canvas.create_rectangle(0, 0, 2000, sy1, fill="black", stipple="gray50", outline="")
        self.canvas.create_rectangle(0, sy2, 2000, 2000, fill="black", stipple="gray50", outline="")
        self.canvas.create_rectangle(0, sy1, sx1, sy2, fill="black", stipple="gray50", outline="")
        self.canvas.create_rectangle(sx2, sy1, 2000, sy2, fill="black", stipple="gray50", outline="")

        # Borde
        self.canvas.create_rectangle(sx1, sy1, sx2, sy2, outline=COLORS["btn_accent"], width=2, dash=(4,4))

        # Handles
        hs = self.HANDLE_SIZE
        pts = [("nw", sx1, sy1), ("ne", sx2, sy1), ("sw", sx1, sy2), ("se", sx2, sy2)]
        for name, hx, hy in pts:
            self.canvas.create_oval(hx-hs, hy-hs, hx+hs, hy+hs, fill=COLORS["btn_accent"], outline="white")

        self.lbl_dims.configure(text=f"{self.crop_x2-self.crop_x1} x {self.crop_y2-self.crop_y1} px")

    def _on_press(self, event):
        sx1, sy1 = self._img_to_screen(self.crop_x1, self.crop_y1)
        sx2, sy2 = self._img_to_screen(self.crop_x2, self.crop_y2)
        hs = self.HANDLE_SIZE + 5
        
        if abs(event.x - sx1) < hs and abs(event.y - sy1) < hs: self.drag_mode = "nw"
        elif abs(event.x - sx2) < hs and abs(event.y - sy1) < hs: self.drag_mode = "ne"
        elif abs(event.x - sx1) < hs and abs(event.y - sy2) < hs: self.drag_mode = "sw"
        elif abs(event.x - sx2) < hs and abs(event.y - sy2) < hs: self.drag_mode = "se"
        elif sx1 < event.x < sx2 and sy1 < event.y < sy2: self.drag_mode = "move"
        else: self.drag_mode = None

        self.drag_start = (event.x, event.y)
        self.crop_start = (self.crop_x1, self.crop_y1, self.crop_x2, self.crop_y2)

    def _on_drag(self, event):
        if not self.drag_mode: return
        dx = int((event.x - self.drag_start[0]) / self.scale)
        dy = int((event.y - self.drag_start[1]) / self.scale)
        x1, y1, x2, y2 = self.crop_start
        iw, ih = self.original_image.size

        if self.drag_mode == "move":
            nx1 = max(0, min(x1 + dx, iw - (x2-x1)))
            ny1 = max(0, min(y1 + dy, ih - (y2-y1)))
            self.crop_x1, self.crop_y1 = nx1, ny1
            self.crop_x2, self.crop_y2 = nx1 + (x2-x1), ny1 + (y2-y1)
        elif self.drag_mode == "se":
            self.crop_x2 = max(x1 + self.MIN_CROP, min(iw, x2 + dx))
            self.crop_y2 = max(y1 + self.MIN_CROP, min(ih, y2 + dy))
        elif self.drag_mode == "nw":
            self.crop_x1 = max(0, min(x2 - self.MIN_CROP, x1 + dx))
            self.crop_y1 = max(0, min(y2 - self.MIN_CROP, y1 + dy))
        elif self.drag_mode == "ne":
            self.crop_x2 = max(x1 + self.MIN_CROP, min(iw, x2 + dx))
            self.crop_y1 = max(0, min(y2 - self.MIN_CROP, y1 + dy))
        elif self.drag_mode == "sw":
            self.crop_x1 = max(0, min(x2 - self.MIN_CROP, x1 + dx))
            self.crop_y2 = max(y1 + self.MIN_CROP, min(ih, y2 + dy))

        self._dibujar()
        self._actualizar_preview()

    def _on_release(self, event):
        self.drag_mode = None

    def _actualizar_preview(self):
        if not self.original_image: return
        crop = self.original_image.crop((self.crop_x1, self.crop_y1, self.crop_x2, self.crop_y2))
        
        # Ajustar la preview para que no deforme la imagen horizontal
        cw, ch = crop.size
        if cw > ch:
            pw, ph = self.PREVIEW_SIZE, int(ch * (self.PREVIEW_SIZE / cw))
        else:
            ph, pw = self.PREVIEW_SIZE, int(cw * (self.PREVIEW_SIZE / ch))
            
        preview_img = crop.resize((pw, ph), Image.LANCZOS)
        self.preview_tk = ctk.CTkImage(light_image=preview_img, dark_image=preview_img, size=(pw, ph))
        self.preview_label.configure(image=self.preview_tk)

    def _aplicar_recorte(self):
        if not self.original_image: return
        crop = self.original_image.crop((self.crop_x1, self.crop_y1, self.crop_x2, self.crop_y2))
        
        import io
        buffer = io.BytesIO()
        crop.convert("RGB").save(buffer, format="JPEG", quality=90)
        blob = buffer.getvalue()

        if self.on_crop:
            self.on_crop(blob, None)