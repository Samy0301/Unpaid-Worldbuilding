"""Utilidades de imagenes, UI y mixins"""

import io
import os
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk
from config import FLOWERS_DIR, COLORS, FONTS


class DialogMixin:
    """Mixin reutilizable para abrir dialogos embebidos con overlay"""

    def abrir_dialogo_embebido(self, parent, DialogClass, *args, on_close=None, width=720, height=680, **kwargs):
        overlay = ctk.CTkFrame(parent, fg_color=COLORS["bg_principal"])
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        container = ctk.CTkFrame(
            overlay, fg_color=COLORS["bg_dialog"], corner_radius=20,
            border_color=COLORS["border_card"], border_width=2,
            width=width, height=height
        )
        container.place(relx=0.5, rely=0.5, anchor="center")
        container.pack_propagate(False)

        def _on_close():
            overlay.destroy()
            if on_close:
                on_close()

        dialog = DialogClass(container, *args, on_close=_on_close, **kwargs)
        dialog.pack(fill="both", expand=True, padx=15, pady=15)


class ImageUtils:
    """Manejo de imagenes para avatares, portadas, nodos y decoraciones"""

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


class TextUtils:
    """Utilidades para manejo de texto con justificacion y adaptacion automatica"""

    @staticmethod
    def _estimate_height(text: str, width_px: int, font_name: str, font_size: int) -> int:
        """Estima la altura en pixeles necesaria para mostrar todo el texto wrappeado."""
        # Ancho aproximado por caracter (Segoe UI es proporcional, ~0.55 del tamano de fuente)
        avg_char_width = font_size * 0.55
        # Ancho util: restar padding interno del CTkTextbox (~20px cada lado)
        usable_width = max(50, width_px - 40)
        chars_per_line = max(10, int(usable_width / avg_char_width))

        lines = 0
        for paragraph in text.split(chr(10)):
            if not paragraph.strip():
                lines += 1
                continue
            # Contar palabras y calcular wrapping
            words = paragraph.split(" ")
            current_line_len = 0
            for word in words:
                word_len = len(word)
                if current_line_len == 0:
                    current_line_len = word_len
                elif current_line_len + 1 + word_len > chars_per_line:
                    lines += 1
                    current_line_len = word_len
                else:
                    current_line_len += 1 + word_len
            lines += 1  # ultima linea del parrafo

        # Altura por linea: tamano de fuente + interlineado
        line_height = font_size + 6
        padding = 16  # padding interno top+bottom del textbox
        return max(40, lines * line_height + padding)

    @staticmethod
    def justified_textbox(parent, text: str, font=None, text_color=None, fg_color=None, padx=15):
        """Crea un CTkTextbox en modo solo lectura que se adapta al ancho del padre.

        El texto se muestra con word-wrap automatico, ocupando todo el ancho disponible
        del contenedor padre menos el margen especificado por `padx`.
        """
        if font is None:
            font = FONTS["body"]
        if text_color is None:
            text_color = COLORS["text_secondary"]
        if fg_color is None:
            fg_color = COLORS["bg_card"]

        font_name, font_size = font[0], font[1]

        # Frame contenedor: ocupa todo el ancho del padre, con margen padx
        wrapper = ctk.CTkFrame(parent, fg_color="transparent")
        wrapper.pack(fill="x", padx=padx, pady=5)

        # CTkTextbox: solo lectura, sin scrollbars, con wrap por palabra
        tb = ctk.CTkTextbox(
            wrapper,
            fg_color=fg_color,
            text_color=text_color,
            border_color=COLORS["border_card"],
            font=font,
            wrap="word",
            activate_scrollbars=False,
            state="disabled"
        )
        tb.pack(fill="x", expand=True)

        # Insertar texto (temporalmente habilitar edicion)
        tb.configure(state="normal")
        tb.delete("1.0", "end")
        tb.insert("1.0", text)
        tb.configure(state="disabled")

        def _update_size(event=None):
            """Ajusta la altura del textbox para que quepa todo el texto wrappeado."""
            try:
                # Si el evento es del wrapper, usar su ancho; si no, obtenerlo directamente
                if event and hasattr(event, "widget") and event.widget == wrapper._w:
                    wrapper_width = event.width
                else:
                    wrapper.update_idletasks()
                    wrapper_width = wrapper.winfo_width()

                if wrapper_width < 50:
                    return  # Aun no esta renderizado

                # Calcular altura necesaria
                height = TextUtils._estimate_height(text, wrapper_width, font_name, font_size)

                # Actualizar solo la altura; el ancho se maneja con pack fill="x"
                tb.configure(height=height)
            except Exception:
                pass

        # Actualizar cuando el wrapper cambie de tamano
        wrapper.bind("<Configure>", _update_size)
        # Actualizaciones diferidas para cuando todo este renderizado
        wrapper.after(50, _update_size)
        wrapper.after(150, lambda: _update_size())
        wrapper.after(300, lambda: _update_size())

        return wrapper