"""Vista de información general de la historia - Tema Otoñal."""

import customtkinter as ctk
from config import FONTS, COLORS
from utils import ImageUtils
from dialogs import HistoriaDialog


class InfoHistoriaView(ctk.CTkFrame):
    """Muestra portada, resumen y plot de la historia activa."""

    def __init__(self, parent, historia_view):
        super().__init__(parent, fg_color="transparent")
        self.hv = historia_view
        self.db = historia_view.db
        self.pack(fill="both", expand=True)
        self._build()

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

    def _build(self):
        for w in self.winfo_children():
            w.destroy()

        f = ctk.CTkFrame(self, corner_radius=20, fg_color=COLORS["bg_card"],
                        border_color=COLORS["border_card"], border_width=2)
        f.pack(fill="both", expand=True, padx=10, pady=10)

        ImageUtils.add_corner_flowers(f, (60, 60))

        top = ctk.CTkFrame(f, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(20, 0))
        ctk.CTkButton(
            top, text="✏️ Editar Historia", command=self._editar,
            corner_radius=15, width=140,
            fg_color=COLORS["btn_primary"], hover_color=COLORS["btn_hover"],
            text_color=COLORS["text_light"]
        ).pack(side="right")

        ImageUtils.add_divider(f, pady=10)

        img = ImageUtils.blob_a_ctkimage(self.hv.h_foto, (300, 300))
        ctk.CTkLabel(f, image=img, text="").pack(pady=10)

        ctk.CTkLabel(
            f, text=f"🌟 {self.hv.h_nombre} 🌟", font=FONTS["title"],
            text_color=COLORS["text_primary"]
        ).pack()

        ctk.CTkLabel(
            f, text="🍁 Resumen 🍁", font=FONTS["script"],
            text_color=COLORS["accent"]
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            f, text=self.hv.h_resumen or "Sin resumen", font=FONTS["body"],
            text_color=COLORS["text_secondary"], wraplength=600
        ).pack()

        ctk.CTkLabel(
            f, text="🌻 Plot General 🌻", font=FONTS["script"],
            text_color=COLORS["accent"]
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            f, text=self.hv.h_plot or "Sin plot", font=FONTS["body"],
            text_color=COLORS["text_secondary"], wraplength=600
        ).pack()

        flower = ImageUtils.load_flower("card_accent.png", (70, 70))
        if flower:
            ctk.CTkLabel(f, image=flower, text="").pack(pady=20)

    def _editar(self):
        self._abrir_dialogo_embebido(
            HistoriaDialog, self.db, self.hv.historia_id,
            on_close=lambda: (self.hv.recargar_datos(), self._build())
        )