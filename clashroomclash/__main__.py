# =============================================================================
#  clashroomclash/__main__.py
#  Permite ejecutar el paquete directamente: python -m clashroomclash
# =============================================================================

from clashroomclash.app import ClassRoomClashApp

if __name__ == "__main__":
    app = ClassRoomClashApp()
    app.mainloop()
