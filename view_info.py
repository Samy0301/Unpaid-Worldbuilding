"""Vista de información general de la historia."""

import customtkinter as ctk
from config import FONTS
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

    def _build(self):
        for w in self.winfo_children():
            w.destroy()

        f = ctk.CTkFrame(self, corner_radius=20)
        f.pack(fill="both", expand=True)

        top = ctk.CTkFrame(f, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(20, 0))
        ctk.CTkButton(
            top, text="✏️ Editar Historia", command=self._editar,
            corner_radius=15, width=140
        ).pack(side="right")

        img = ImageUtils.blob_a_ctkimage(self.hv.h_foto, (300, 300))
        ctk.CTkLabel(f, image=img, text="").pack(pady=20)
        ctk.CTkLabel(f, text=self.hv.h_nombre, font=FONTS["title"]).pack()

        ctk.CTkLabel(f, text="Resumen:", font=FONTS["heading"], text_color="#722F37").pack(pady=(20, 5))
        ctk.CTkLabel(f, text=self.hv.h_resumen or "Sin resumen", font=FONTS["body"], wraplength=600).pack()

        ctk.CTkLabel(f, text="Plot General:", font=FONTS["heading"], text_color="#722F37").pack(pady=(20, 5))
        ctk.CTkLabel(f, text=self.hv.h_plot or "Sin plot", font=FONTS["body"], wraplength=600).pack()

    def _editar(self):
        dialog = HistoriaDialog(self, self.db, self.hv.historia_id)
        self.wait_window(dialog)
        self.hv.recargar_datos()
        self._build()