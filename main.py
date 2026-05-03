"""Punto de entrada"""

import customtkinter as ctk
from config import WINDOW_SIZE, COLORS
from database import Database
from view_dashboard import DashboardView
from view_historia import HistoriaView


class NovelPlannerApp(ctk.CTk):
    """Aplicación principal"""

    def __init__(self):
        super().__init__()
        self.title("NovelPlanner")
        self.geometry(WINDOW_SIZE)
        self.configure(fg_color=COLORS["bg_principal"])
        self.db = Database()
        self._current_view = None
        self.mostrar_dashboard()

    def mostrar_dashboard(self):
        self._cambiar_vista(DashboardView, self)

    def abrir_historia(self, historia_id):
        self._cambiar_vista(HistoriaView, self, historia_id)

    def _cambiar_vista(self, view_class, *args):
        if self._current_view:
            self._current_view.destroy()
        self._current_view = view_class(self, *args)


if __name__ == "__main__":
    app = NovelPlannerApp()
    app.mainloop()