"""Recortador de imagenes con seleccion manual de area - VERSION EMBEBIDA"""

import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import customtkinter as ctk
from config import FONTS, COLORS


class ImageCropper(ctk.CTkFrame):
    """
    Panel embebido para seleccionar un area de una imagen.
    Se inserta dentro de un contenedor padre (scrollable frame, dialogo, etc.)

    Uso:
        cropper = ImageCropper(parent, on_crop=callback, shape="square")
        cropper.pack(fill="both", expand=True)
        # Luego llamar a cropper.cargar_imagen(ruta)

    El callback recibe: (blob_bytes, preview_ctkimage)
    """

    SELECTION_SIZE = 600
    PREVIEW_SIZE = 200

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

        self.sel_x = 0
        self.sel_y = 0
        self.sel_w = 0
        self.sel_h = 0
        self.dragging = False
        self.drag_start = (0, 0)
        self.sel_start = (0, 0)

        self._build_ui()

    def _build_ui(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=5, pady=5)

        left_panel = ctk.CTkFrame(main, fg_color=COLORS["bg_card"], corner_radius=15,
                                border_color=COLORS["border_card"], border_width=2)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.canvas = tk.Canvas(
            left_panel, bg=COLORS["bg_card"], highlightthickness=0,
            width=520, height=480
        )
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        right_panel = ctk.CTkFrame(main, fg_color="transparent", width=300)
        right_panel.pack(side="right", fill="y", padx=(10, 0))
        right_panel.pack_propagate(False)

        instrucciones = ctk.CTkFrame(right_panel, fg_color=COLORS["bg_dialog"], corner_radius=10)
        instrucciones.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            instrucciones,
            text="Arrastra el area para moverla.\n"
                "Usa el deslizador para ajustar el tamano.\n"
                "Haz doble clic para recortar.",
            font=FONTS["small"], text_color=COLORS["text_secondary"],
            wraplength=200
        ).pack(padx=10, pady=10)

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

        ctk.CTkLabel(
            right_panel, text="Tamaño del recorte:", font=FONTS["body"],
            text_color=COLORS["text_primary"]
        ).pack(pady=(15, 8))

        size_frame = ctk.CTkFrame(
            right_panel, fg_color=COLORS["bg_card"], corner_radius=10,
            border_color=COLORS["border_card"], border_width=1
        )
        size_frame.pack(fill="x", padx=10, pady=5)

        self.slider_size = ctk.CTkSlider(
            size_frame, from_=100, to=800, number_of_steps=70,
            width=240, height=24,
            fg_color=COLORS["accent_soft"],
            progress_color=COLORS["btn_primary"],
            button_color=COLORS["btn_primary"],
            button_hover_color=COLORS["btn_hover"],
            command=self._on_size_change
        )
        self.slider_size.set(self.SELECTION_SIZE)
        self.slider_size.pack(pady=(12, 5), padx=10)

        self.lbl_size = ctk.CTkLabel(
            size_frame, text=f"{self.SELECTION_SIZE}px", font=FONTS["caption"],
            text_color=COLORS["text_secondary"]
        )
        self.lbl_size.pack(pady=(0, 10))

        btn_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        btn_frame.pack(pady=15)

        ctk.CTkButton(
            btn_frame, text="Recortar y guardar", command=self._aplicar_recorte,
            corner_radius=15, width=180, height=40,
            fg_color=COLORS["btn_primary"], hover_color=COLORS["btn_hover"],
            text_color=COLORS["text_light"], font=FONTS["heading"]
        ).pack(pady=5)

        self.canvas.bind("<Button-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Double-Button-1>", lambda e: self._aplicar_recorte())

    def cargar_imagen(self, ruta):
        """Carga una imagen desde una ruta."""
        try:
            self.original_image = Image.open(ruta).convert("RGBA")
            self._ajustar_imagen_al_canvas()
            self._inicializar_seleccion()
            self._dibujar()
            return True
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"No se pudo cargar la imagen: {e}")
            self._cancelar()
            return False

    def _ajustar_imagen_al_canvas(self):
        self.canvas.update_idletasks()
        canvas_w = self.canvas.winfo_width() or 500
        canvas_h = self.canvas.winfo_height() or 400

        img_w, img_h = self.original_image.size

        scale_w = canvas_w / img_w
        scale_h = canvas_h / img_h
        self.scale = min(scale_w, scale_h) * 0.9

        disp_w = int(img_w * self.scale)
        disp_h = int(img_h * self.scale)

        self.offset_x = (canvas_w - disp_w) // 2
        self.offset_y = (canvas_h - disp_h) // 2

        self.display_image = self.original_image.resize((disp_w, disp_h), Image.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(self.display_image)

    def _inicializar_seleccion(self):
        disp_w = self.display_image.width
        disp_h = self.display_image.height

        size = min(self.SELECTION_SIZE, disp_w, disp_h)
        self.sel_w = int(size / self.scale)
        self.sel_h = int(size / self.scale)

        img_w, img_h = self.original_image.size
        self.sel_x = (img_w - self.sel_w) // 2
        self.sel_y = (img_h - self.sel_h) // 2

        self._actualizar_preview()

    def _dibujar(self):
        self.canvas.delete("all")

        if self.photo_image:
            self.canvas.create_image(
                self.offset_x, self.offset_y,
                image=self.photo_image, anchor="nw"
            )

        screen_x = self.offset_x + int(self.sel_x * self.scale)
        screen_y = self.offset_y + int(self.sel_y * self.scale)
        screen_w = int(self.sel_w * self.scale)
        screen_h = int(self.sel_h * self.scale)

        self.canvas.update_idletasks()
        canvas_w = self.canvas.winfo_width() or 500
        canvas_h = self.canvas.winfo_height() or 400

        overlay_color = "#000000"

        if self.shape == "circle":
            overlay_img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 100))

            cx = screen_x + screen_w // 2
            cy = screen_y + screen_h // 2
            radius = min(screen_w, screen_h) // 2

            for y in range(canvas_h):
                for x in range(canvas_w):
                    dx = x - cx
                    dy = y - cy
                    if dx*dx + dy*dy <= radius*radius:
                        overlay_img.putpixel((x, y), (0, 0, 0, 0))

            self.overlay_photo = ImageTk.PhotoImage(overlay_img)
            self.canvas.create_image(0, 0, image=self.overlay_photo, anchor="nw")

            self.canvas.create_oval(
                cx - radius, cy - radius, cx + radius, cy + radius,
                outline="#D2691E", width=3, dash=(6, 4)
            )
        else:
            self.canvas.create_rectangle(
                0, 0, canvas_w, screen_y,
                fill=overlay_color, stipple="gray50", outline=""
            )
            self.canvas.create_rectangle(
                0, screen_y + screen_h, canvas_w, canvas_h,
                fill=overlay_color, stipple="gray50", outline=""
            )
            self.canvas.create_rectangle(
                0, screen_y, screen_x, screen_y + screen_h,
                fill=overlay_color, stipple="gray50", outline=""
            )
            self.canvas.create_rectangle(
                screen_x + screen_w, screen_y, canvas_w, screen_y + screen_h,
                fill=overlay_color, stipple="gray50", outline=""
            )

            self.canvas.create_rectangle(
                screen_x, screen_y, screen_x + screen_w, screen_y + screen_h,
                outline="#D2691E", width=3, dash=(6, 4)
            )

            corner_size = 8
            for cx, cy in [
                (screen_x, screen_y),
                (screen_x + screen_w, screen_y),
                (screen_x, screen_y + screen_h),
                (screen_x + screen_w, screen_y + screen_h),
            ]:
                self.canvas.create_oval(
                    cx - corner_size, cy - corner_size,
                    cx + corner_size, cy + corner_size,
                    fill="#D2691E", outline=""
                )

    def _on_press(self, event):
        screen_x = self.offset_x + int(self.sel_x * self.scale)
        screen_y = self.offset_y + int(self.sel_y * self.scale)
        screen_w = int(self.sel_w * self.scale)
        screen_h = int(self.sel_h * self.scale)

        if self.shape == "circle":
            cx = screen_x + screen_w // 2
            cy = screen_y + screen_h // 2
            radius = min(screen_w, screen_h) // 2
            dx = event.x - cx
            dy = event.y - cy
            dentro = dx*dx + dy*dy <= radius*radius
        else:
            dentro = (screen_x <= event.x <= screen_x + screen_w and
                    screen_y <= event.y <= screen_y + screen_h)

        if dentro:
            self.dragging = True
            self.drag_start = (event.x, event.y)
            self.sel_start = (self.sel_x, self.sel_y)

    def _on_drag(self, event):
        if not self.dragging:
            return

        dx = int((event.x - self.drag_start[0]) / self.scale)
        dy = int((event.y - self.drag_start[1]) / self.scale)

        img_w, img_h = self.original_image.size

        new_x = self.sel_start[0] + dx
        new_y = self.sel_start[1] + dy

        new_x = max(0, min(new_x, img_w - self.sel_w))
        new_y = max(0, min(new_y, img_h - self.sel_h))

        self.sel_x = new_x
        self.sel_y = new_y

        self._dibujar()
        self._actualizar_preview()

    def _on_release(self, event):
        self.dragging = False

    def _on_size_change(self, value):
        nuevo_size = int(value)

        img_w, img_h = self.original_image.size
        max_size = min(img_w, img_h)
        nuevo_size = max(50, min(nuevo_size, max_size))

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
        if self.original_image is None:
            return

        crop = self.original_image.crop((
            self.sel_x, self.sel_y,
            self.sel_x + self.sel_w, self.sel_y + self.sel_h
        ))

        if self.shape == "circle":
            mask = Image.new("L", crop.size, 0)
            draw = ImageDraw.Draw(mask)
            w, h = crop.size
            draw.ellipse((0, 0, w, h), fill=255)
            crop.putalpha(mask)

        preview = crop.resize((self.PREVIEW_SIZE, self.PREVIEW_SIZE), Image.LANCZOS)

        self.preview_image = ctk.CTkImage(light_image=preview, dark_image=preview,
                                        size=(self.PREVIEW_SIZE, self.PREVIEW_SIZE))
        self.preview_label.configure(image=self.preview_image)

    def _aplicar_recorte(self):
        if self.original_image is None:
            return

        try:
            crop = self.original_image.crop((
                self.sel_x, self.sel_y,
                self.sel_x + self.sel_w, self.sel_y + self.sel_h
            ))

            if self.shape == "circle":
                mask = Image.new("L", crop.size, 0)
                draw = ImageDraw.Draw(mask)
                w, h = crop.size
                draw.ellipse((0, 0, w, h), fill=255)
                crop.putalpha(mask)

            max_size = 1200
            crop.thumbnail((max_size, max_size), Image.LANCZOS)

            import io
            buffer = io.BytesIO()
            if self.shape == "circle":
                crop.save(buffer, format="PNG")
            else:
                crop.convert("RGB").save(buffer, format="PNG")
            blob = buffer.getvalue()

            preview = crop.resize((200, 200), Image.LANCZOS)
            preview_ctk = ctk.CTkImage(light_image=preview, dark_image=preview,
                                        size=(200, 200))

            self.result = (blob, preview_ctk)

            if self.on_crop:
                self.on_crop(blob, preview_ctk)

        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"No se pudo recortar la imagen: {e}")

    def _cancelar(self):
        self.result = None
        if self.on_cancel:
            self.on_cancel()