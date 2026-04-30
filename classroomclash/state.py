from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class AppState:
    """Clase que encapsula el estado global de la aplicación para evitar variables sueltas."""
    current_group_id: Optional[int] = None
    current_group_name: str = "Global"
    students: List[str] = field(default_factory=list)
    teams: List[List[str]] = field(default_factory=list)
    num_teams: int = 0
    student_index: int = 0
    assign_index: int = 0
    is_animating: bool = False
    selected_student: Optional[str] = None
    wheel_mode: str = "student"

    def reset_sorteo(self):
        """Reinicia el estado específico para un nuevo sorteo."""
        self.teams = [[] for _ in range(max(1, self.num_teams))]
        self.student_index = 0
        self.assign_index = 0
        self.is_animating = False

    def clear(self):
        """Limpia todo el estado global al salir de un grupo."""
        self.current_group_id = None
        self.current_group_name = "Global"
        self.students = []
        self.teams = []
        self.num_teams = 0
        self.student_index = 0
        self.assign_index = 0
        self.is_animating = False
        self.selected_student = None
        self.wheel_mode = "student"
