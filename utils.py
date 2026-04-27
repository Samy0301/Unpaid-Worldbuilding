"""Utilidades de imágenes y UI."""

import io
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk


class ImageUtils:
    """Manejo de imágenes para avatares, portadas y nodos del canvas."""

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
        img = Image.new("RGB", size, color="#2B2B2B")
        draw = ImageDraw.Draw(img)
        draw.ellipse([10, 10, size[0] - 10, size[1] - 10], outline="#555555", width=3)
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)

    @staticmethod
    def blob_a_tkimage(blob, size=(60, 60)):
        """Convierte BLOB a PhotoImage circular para Canvas (tkinter)."""
        if not blob:
            img = Image.new("RGBA", size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.ellipse([2, 2, size[0] - 2, size[1] - 2], outline="#666666", width=2)
        else:
            img = Image.open(io.BytesIO(blob))
            img = ImageUtils.recortar_cuadrado(img)
            img = img.resize(size, Image.LANCZOS).convert("RGBA")
            mask = Image.new("L", size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size[0], size[1]), fill=255)
            img.putalpha(mask)
        return ImageTk.PhotoImage(img)