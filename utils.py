"""Utilidades de imágenes, UI y mixins"""

import io
import os
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk
from config import FLOWERS_DIR, COLORS


class DialogMixin:
    """Mixin reutilizable para abrir diálogos embebidos con overlay"""

    def abrir_dialogo_embebido(self, parent, DialogClass, *args, on_close=None, **kwargs):
        overlay = ctk.CTkFrame(parent, fg_color=COLORS["bg_principal"])
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


class ImageUtils:
    """Manejo de imágenes para avatares, portadas, nodos y decoraciones"""

    @staticmethod
    def blob_a_ctkimage(blob, size=(150, 150)):
        if not blob:
            return ImageUtils.avatar_default(size)
        img = Image.open(io.BytesIO(blob))
        img = ImageUtils.recortar_cuadrado(img)
        img = img.resize(size, Image.LANCZOS)
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)

    @staticmethod
    def blob_a_ctkimage_rounded(blob, size=(150, 150), radius=15, top_only=False):
        if not blob:
            img = Image.new("RGBA", size, "#FFF8F0")
            draw = ImageDraw.Draw(img)
            fill = "#FFF8F0"
        else:
            img = Image.open(io.BytesIO(blob)).convert("RGBA")
            img = img.resize(size, Image.LANCZOS)

        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        w, h = size

        if top_only:
            draw.rounded_rectangle([0, 0, w, h + radius], radius=radius, fill=255)
        else:
            draw.rounded_rectangle([0, 0, w, h], radius=radius, fill=255)

        if img.mode != "RGBA":
            img = img.convert("RGBA")
        img.putalpha(mask)

        return ctk.CTkImage(light_image=img, dark_image=img, size=size)

    @staticmethod
    def archivo_a_blob(ruta: str, max_size=(400, 400)):
        img = Image.open(ruta)
        img = ImageUtils.recortar_cuadrado(img)
        img.thumbnail(max_size, Image.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    @staticmethod
    def recortar_cuadrado(img: Image.Image):
        w, h = img.size
        min_dim = min(w, h)
        left = (w - min_dim) // 2
        top = (h - min_dim) // 2
        return img.crop((left, top, left + min_dim, top + min_dim))

    @staticmethod
    def avatar_default(size=(150, 150)):
        img = Image.new("RGB", size, color="#FFF8F0")
        draw = ImageDraw.Draw(img)
        draw.ellipse([10, 10, size[0]-10, size[1]-10], outline="#D2691E", width=3)
        cx, cy = size[0]//2, size[1]//2
        draw.ellipse([cx-8, cy-8, cx+8, cy+8], fill="#DAA520")
        draw.ellipse([cx-3, cy-3, cx+3, cy+3], fill="#E67E22")
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)

    @staticmethod
    def blob_a_tkimage(blob, size=(60, 60)):
        """Convierte BLOB a PhotoImage circular para Canvas"""
        if not blob:
            img = Image.new("RGBA", size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.ellipse([2, 2, size[0]-2, size[1]-2], outline="#D2691E", width=2)
            cx, cy = size[0]//2, size[1]//2
            draw.ellipse([cx-4, cy-4, cx+4, cy+4], fill="#DAA520", outline="#E67E22")
        else:
            img = Image.open(io.BytesIO(blob))
            img = ImageUtils.recortar_cuadrado(img)
            img = img.resize(size, Image.LANCZOS).convert("RGBA")
            mask = Image.new("L", size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size[0], size[1]), fill=255)
            img.putalpha(mask)
        return ImageTk.PhotoImage(img)

    @staticmethod
    def load_flower(name: str, size=None):
        path = os.path.join(FLOWERS_DIR, name)
        if not os.path.exists(path):
            return None
        img = Image.open(path)
        if size:
            img = img.resize(size, Image.LANCZOS)
        return ctk.CTkImage(light_image=img, dark_image=img, size=img.size)

    @staticmethod
    def add_corner_flowers(parent_frame, size=(80, 80)):
        corners = [
            ("corner_top_left.png", 0, 0, "nw"),
            ("corner_top_right.png", 1, 0, "ne"),
            ("corner_bottom_left.png", 0, 1, "sw"),
            ("corner_bottom_right.png", 1, 1, "se"),
        ]
        for fname, col, row, anchor in corners:
            img = ImageUtils.load_flower(fname, size)
            if img:
                lbl = ctk.CTkLabel(parent_frame, image=img, text="")
                lbl.place(relx=col, rely=row, anchor=anchor)

    @staticmethod
    def add_divider(parent, pady=10):
        img = ImageUtils.load_flower("divider.png", (300, 30))
        if img:
            lbl = ctk.CTkLabel(parent, image=img, text="")
            lbl.pack(pady=pady)
            return lbl
        return None