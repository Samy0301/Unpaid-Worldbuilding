"""Vista de información general de la historia"""

import customtkinter as ctk
from config import FONTS, COLORS
from utils import ImageUtils, DialogMixin, TextUtils
from dialogs import HistoriaDialog


class InfoHistoriaView(ctk.CTkFrame, DialogMixin):
    """Muestra portada, resumen y plot de la historia"""

    def __init__(self, parent, historia_view):
        super().__init__(parent, fg_color="transparent")
        self.hv = historia_view
        self.db = historia_view.db
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        for w in self.winfo_children():
            w.destroy()

        # Scrollable frame principal para todo el contenido
        scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=COLORS["btn_primary"],
            scrollbar_button_hover_color=COLORS["btn_hover"]
        )
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        f = ctk.CTkFrame(
            scroll, corner_radius=20, fg_color=COLORS["bg_card"],
            border_color=COLORS["border_card"], border_width=2
        )
        f.pack(fill="x", expand=True, padx=10, pady=10)

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

        if self.hv.h_resumen:
            tb_resumen = TextUtils.justified_textbox(
                f, self.hv.h_resumen, width=600,
                font=FONTS["body"], text_color=COLORS["text_secondary"],
                fg_color=COLORS["bg_card"]
            )
            tb_resumen.pack(pady=(0, 10))
        else:
            ctk.CTkLabel(
                f, text="Sin resumen", font=FONTS["body"],
                text_color=COLORS["text_secondary"]
            ).pack()

        ctk.CTkLabel(
            f, text="🌻 Plot General 🌻", font=FONTS["script"],
            text_color=COLORS["accent"]
        ).pack(pady=(20, 5))

        if self.hv.h_plot:
            tb_plot = TextUtils.justified_textbox(
                f, self.hv.h_plot, width=600,
                font=FONTS["body"], text_color=COLORS["text_secondary"],
                fg_color=COLORS["bg_card"]
            )
            tb_plot.pack(pady=(0, 10))
        else:
            ctk.CTkLabel(
                f, text="Sin plot", font=FONTS["body"],
                text_color=COLORS["text_secondary"]
            ).pack()

        flower = ImageUtils.load_flower("card_accent.png", (70, 70))
        if flower:
            ctk.CTkLabel(f, image=flower, text="").pack(pady=20)

    def _editar(self):
        self.abrir_dialogo_embebido(
            self, HistoriaDialog, self.db, self.hv.historia_id,
            on_close=lambda: (self.hv.recargar_datos(), self._build())
        )