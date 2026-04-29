# =============================================================================
#  clashroomclash/app.py
#  Clase principal ClassRoomClashApp — ensambla los mixins de pantallas y lógica
# =============================================================================

import tkinter as tk
from tkinter import font as tkfont

from .constants import BG_MAIN, BG_HEADER
from .database import DatabaseManager
from .screens import ScreensMixin
from .sorteo_screen import SorteoScreenMixin
from .wheel import WheelMixin
from .activities import ActivitiesMixin
from .state import AppState


class ClassRoomClashApp(ScreensMixin, SorteoScreenMixin, WheelMixin, ActivitiesMixin, tk.Tk):
    """
    Ventana raíz de la aplicación.
    Hereda de los mixins para mantener cada módulo enfocado:
      - ScreensMixin      → menú, config, grupos, historial, leaderboard
      - SorteoScreenMixin → pantalla de sorteo y animación de tómbola
      - WheelMixin        → pantalla y animación de la ruleta de puntos
    """

    def __init__(self):
        super().__init__()
        self.title("🎮 ClassRoom Clash — Toolkit Educativo")
        self.geometry("1050x720")
        self.minsize(850, 620)
        self.configure(bg=BG_MAIN)
        self.resizable(True, True)
        self.state('zoomed')  # Iniciar maximizado en Windows

        # ── Base de datos ─────────────────────────────────────────────────
        self.db = DatabaseManager()

        # ── Fuentes ───────────────────────────────────────────────────────
        self.f_header = tkfont.Font(family="Helvetica", size=22, weight="bold")
        self.f_title  = tkfont.Font(family="Helvetica", size=14, weight="bold")
        self.f_body   = tkfont.Font(family="Helvetica", size=11)
        self.f_slot   = tkfont.Font(family="Helvetica", size=34, weight="bold")
        self.f_name   = tkfont.Font(family="Helvetica", size=12, weight="bold")
        self.f_btn    = tkfont.Font(family="Helvetica", size=13, weight="bold")
        self.f_small  = tkfont.Font(family="Helvetica", size=9)

        # ── Estado de la aplicación ───────────────────────────────────────
        self.state = AppState()

        # ── Contenedor maestro ────────────────────────────────────────────
        self.container = tk.Frame(self, bg=BG_MAIN)
        self.container.pack(fill="both", expand=True)

        self.show_main_menu()
