# =============================================================================
#  classroomclash/__main__.py
#  Permite ejecutar el paquete directamente: python -m classroomclash
# =============================================================================

from classroomclash.app import ClassRoomClashApp

if __name__ == "__main__":
    app = ClassRoomClashApp()
    app.mainloop()
