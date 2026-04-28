"""Utilidades de imágenes y UI - Tema Jardín."""

import io
import os
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk
from config import FLOWERS_DIR


class ImageUtils:
    """Manejo de imágenes para avatares, portadas, nodos y decoraciones florales."""

    @staticmethod
    def blob_a_ctkimage(blob, size=(150, 150)):
        if not blob:
            return ImageUtils.avatar_default(size)
        img = Image.open(io.BytesIO(blob))
        img = ImageUtils.recortar_cuadrado(img)
        img = img.resize(size, Image.LANCZOS)
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
        img = Image.new("RGB", size, color="#FFF0F5")
        draw = ImageDraw.Draw(img)
        draw.ellipse([10, 10, size[0]-10, size[1]-10], outline="#D4A5A5", width=3)
        # Pequeña flor en el centro
        cx, cy = size[0]//2, size[1]//2
        draw.ellipse([cx-8, cy-8, cx+8, cy+8], fill="#F4D03F")
        draw.ellipse([cx-3, cy-3, cx+3, cy+3], fill="#E91E63")
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)

    @staticmethod
    def blob_a_tkimage(blob, size=(60, 60)):
        """Convierte BLOB a PhotoImage circular para Canvas (tkinter)."""
        if not blob:
            img = Image.new("RGBA", size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.ellipse([2, 2, size[0]-2, size[1]-2], outline="#D4A5A5", width=2)
            # Flor mini
            cx, cy = size[0]//2, size[1]//2
            draw.ellipse([cx-4, cy-4, cx+4, cy+4], fill="#F4D03F", outline="#E91E63")
        else:
            img = Image.open(io.BytesIO(blob))
            img = ImageUtils.recortar_cuadrado(img)
            img = img.resize(size, Image.LANCZOS).convert("RGBA")
            mask = Image.new("L", size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size[0], size[1]), fill=255)
            img.putalpha(mask)
        return ImageTk.PhotoImage(img)

    # ─── Decoraciones florales ───

    @staticmethod
    def load_flower(name: str, size=None):
        """Carga una imagen decorativa de flores."""
        path = os.path.join(FLOWERS_DIR, name)
        if not os.path.exists(path):
            return None
        img = Image.open(path)
        if size:
            img = img.resize(size, Image.LANCZOS)
        return ctk.CTkImage(light_image=img, dark_image=img, size=img.size)

    @staticmethod
    def add_corner_flowers(parent_frame, size=(80, 80)):
        """Añade flores en las 4 esquinas de un frame."""
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
        """Añade un separador floral horizontal."""
        img = ImageUtils.load_flower("divider.png", (300, 30))
        if img:
            lbl = ctk.CTkLabel(parent, image=img, text="")
            lbl.pack(pady=pady)
            return lbl
        return None