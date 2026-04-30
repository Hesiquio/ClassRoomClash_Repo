# =============================================================================
#  classroomclash/database.py
#  Gestor de base de datos SQLite para historial, grupos y leaderboard
# =============================================================================

import sqlite3
import json
from datetime import datetime
from contextlib import closing
from typing import List, Dict, Any, Optional, Tuple

class DatabaseManager:
    """Gestiona la persistencia de datos en SQLite."""

    def __init__(self, db_path: str = "desafio_data.db") -> None:
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self) -> None:
        """Crea las tablas necesarias si no existen."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                c = conn.cursor()
                
                # Tabla de grupos (sorteos guardados)
                c.execute('''
                    CREATE TABLE IF NOT EXISTS groups (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        students TEXT NOT NULL,
                        num_teams INTEGER NOT NULL,
                        teams TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        notes TEXT
                    )
                ''')

                # Tabla de historial de sorteos
                c.execute('''
                    CREATE TABLE IF NOT EXISTS draw_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        group_id INTEGER,
                        group_name TEXT NOT NULL,
                        teams TEXT NOT NULL,
                        drawn_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        notes TEXT,
                        FOREIGN KEY(group_id) REFERENCES groups(id)
                    )
                ''')

                # Tabla de puntos/leaderboard
                c.execute('''
                    CREATE TABLE IF NOT EXISTS leaderboard (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_name TEXT NOT NULL,
                        points INTEGER DEFAULT 0,
                        wheel_spins INTEGER DEFAULT 0,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Tabla de actividades
                c.execute('''
                    CREATE TABLE IF NOT EXISTS activities (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        group_id INTEGER,
                        name TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(group_id) REFERENCES groups(id)
                    )
                ''')

                # Migración: Añadir group_id si la tabla ya existía sin él
                try:
                    c.execute('ALTER TABLE activities ADD COLUMN group_id INTEGER')
                except sqlite3.OperationalError:
                    pass # Ya existe o la tabla es nueva y ya lo tiene

                # Migración: Añadir is_archived a groups
                try:
                    c.execute('ALTER TABLE groups ADD COLUMN is_archived INTEGER DEFAULT 0')
                except sqlite3.OperationalError:
                    pass

                # Tabla de entregas (registra el orden)
                c.execute('''
                    CREATE TABLE IF NOT EXISTS activity_submissions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        activity_id INTEGER,
                        student_name TEXT NOT NULL,
                        position INTEGER,
                        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(activity_id) REFERENCES activities(id)
                    )
                ''')

                # Tabla de Log de Actividad (Global)
                c.execute('''
                    CREATE TABLE IF NOT EXISTS activity_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_type TEXT NOT NULL,
                        group_id INTEGER,
                        group_name TEXT,
                        description TEXT NOT NULL,
                        details TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

    # ── Grupos ────────────────────────────────────────────────────────────────

    def save_group(self, name: str, students: List[str], num_teams: int, teams: List[List[str]], notes: str = "") -> int:
        """Guarda un grupo en la BD."""
        students_json = json.dumps(students)
        teams_json = json.dumps(teams)

        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                c = conn.cursor()
                c.execute('''
                    INSERT INTO groups (name, students, num_teams, teams, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (name, students_json, num_teams, teams_json, notes, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                return c.lastrowid

    def get_groups(self, include_archived: bool = False) -> List[Tuple[int, str, str, bool]]:
        """Retorna todos los grupos guardados."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            c = conn.cursor()
            if include_archived:
                c.execute('SELECT id, name, created_at, is_archived FROM groups ORDER BY created_at DESC')
            else:
                c.execute('SELECT id, name, created_at, is_archived FROM groups WHERE is_archived = 0 ORDER BY created_at DESC')
            return c.fetchall()

    def load_group(self, group_id: int) -> Optional[Dict[str, Any]]:
        """Carga un grupo por ID."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            c = conn.cursor()
            c.execute(
                'SELECT name, students, num_teams, teams, notes, is_archived FROM groups WHERE id = ?',
                (group_id,)
            )
            row = c.fetchone()

        if row:
            name, students_json, num_teams, teams_json, notes, is_archived = row
            return {
                'name': name,
                'students': json.loads(students_json),
                'num_teams': num_teams,
                'teams': json.loads(teams_json),
                'notes': notes,
                'is_archived': bool(is_archived),
            }
        return None

    def rename_group(self, group_id: int, new_name: str) -> None:
        """Renombra un grupo."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                c = conn.cursor()
                c.execute('UPDATE groups SET name = ? WHERE id = ?', (new_name, group_id))

    def toggle_archive_group(self, group_id: int, archive: bool) -> None:
        """Archiva o desarchiva un grupo."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                c = conn.cursor()
                c.execute('UPDATE groups SET is_archived = ? WHERE id = ?', (1 if archive else 0, group_id))

    def delete_group(self, group_id: int) -> None:
        """Elimina un grupo."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                c = conn.cursor()
                c.execute('DELETE FROM groups WHERE id = ?', (group_id,))

    def update_group_students(self, group_id: int, students: List[str]) -> None:
        """Actualiza la lista de alumnos de un grupo."""
        students_json = json.dumps(students)
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                c = conn.cursor()
                c.execute('UPDATE groups SET students = ? WHERE id = ?', (students_json, group_id))

    # ── Historial ─────────────────────────────────────────────────────────────

    def log_event(self, event_type: str, group_name: Optional[str], description: str, group_id: Optional[int] = None, details: Optional[Dict[str, Any]] = None) -> None:
        """Registra un evento en el log global."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                c = conn.cursor()
                c.execute('''
                    INSERT INTO activity_log (event_type, group_id, group_name, description, details, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (event_type, group_id, group_name, description, json.dumps(details) if details else None, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    def save_draw_history(self, group_name: str, teams: List[List[str]], notes: str = "", group_id: Optional[int] = None) -> None:
        """Guarda un sorteo en el historial."""
        teams_json = json.dumps(teams)

        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                c = conn.cursor()
                c.execute('''
                    INSERT INTO draw_history (group_id, group_name, teams, notes, drawn_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (group_id, group_name, teams_json, notes, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        # Log del evento
        self.log_event("sorteo", group_name, f"Sorteo de equipos realizado ({len(teams)} equipos)", group_id, {"teams": teams})

    def get_global_log(self, limit: int = 100) -> List[Tuple[str, Optional[str], str, str, Optional[str]]]:
        """Retorna el historial unificado de eventos."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT event_type, group_name, description, created_at, details 
                FROM activity_log
                ORDER BY created_at DESC LIMIT ?
            ''', (limit,))
            return c.fetchall()

    # ── Leaderboard ───────────────────────────────────────────────────────────

    def add_points(self, student_name: str, points: int, group_id: Optional[int] = None, group_name: Optional[str] = None) -> None:
        """Agrega puntos a un estudiante y lo registra en el log."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                c = conn.cursor()
                c.execute('SELECT id FROM leaderboard WHERE student_name = ?', (student_name,))
                result = c.fetchone()

                if result:
                    c.execute('''
                        UPDATE leaderboard
                        SET points = points + ?, wheel_spins = wheel_spins + 1,
                            last_updated = ?
                        WHERE student_name = ?
                    ''', (points, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), student_name))
                else:
                    c.execute('''
                        INSERT INTO leaderboard (student_name, points, wheel_spins, last_updated)
                        VALUES (?, ?, 1, ?)
                    ''', (student_name, points, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        # Log del evento
        desc = f"{student_name} recibió {points} puntos"
        self.log_event("puntos", group_name, desc, group_id, {"student": student_name, "points": points})

    def get_leaderboard(self, limit: int = 20) -> List[Tuple[str, int, int]]:
        """Retorna el leaderboard ordenado por puntos."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT student_name, points, wheel_spins FROM leaderboard
                ORDER BY points DESC LIMIT ?
            ''', (limit,))
            return c.fetchall()

    def get_group_leaderboard(self, student_names: List[str]) -> List[Tuple[str, int, int]]:
        """Retorna el leaderboard filtrado por una lista de nombres."""
        if not student_names:
            return []
        
        placeholders = ','.join(['?'] * len(student_names))
        query = f'''
            SELECT student_name, points, wheel_spins FROM leaderboard
            WHERE student_name IN ({placeholders})
            ORDER BY points DESC
        '''
        with closing(sqlite3.connect(self.db_path)) as conn:
            c = conn.cursor()
            c.execute(query, student_names)
            return c.fetchall()

    def reset_leaderboard(self) -> None:
        """Limpia el leaderboard."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                c = conn.cursor()
                c.execute('DELETE FROM leaderboard')

    # ── Actividades ───────────────────────────────────────────────────────────

    def create_activity(self, name: str, group_id: int, group_name: Optional[str] = None) -> int:
        """Crea una nueva actividad ligada a un grupo y lo registra."""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                c = conn.cursor()
                c.execute('INSERT INTO activities (name, group_id, created_at) VALUES (?, ?, ?)', (name, group_id, now))
                activity_id = c.lastrowid
        
        self.log_event("actividad", group_name, f"Nueva actividad creada: {name}", group_id)
        return activity_id

    def get_activities(self) -> List[Tuple[int, str, str, str, int]]:
        """Retorna todas las actividades con información de su grupo."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT a.id, a.name, a.created_at, g.name, a.group_id
                FROM activities a
                JOIN groups g ON a.group_id = g.id
                ORDER BY a.created_at DESC
            ''')
            return c.fetchall()

    def update_activity_name(self, activity_id: int, new_name: str) -> None:
        """Actualiza el nombre de una actividad."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                c = conn.cursor()
                c.execute('UPDATE activities SET name = ? WHERE id = ?', (new_name, activity_id))

    def register_submission(self, activity_id: int, student_name: str) -> Optional[int]:
        """Registra la entrega de un alumno y le asigna la siguiente posición disponible."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                c = conn.cursor()
                # Verificar si ya entregó
                c.execute('''
                    SELECT id FROM activity_submissions 
                    WHERE activity_id = ? AND student_name = ?
                ''', (activity_id, student_name))
                if c.fetchone():
                    return None # Ya entregó

                # Obtener la siguiente posición
                c.execute('SELECT COUNT(*) FROM activity_submissions WHERE activity_id = ?', (activity_id,))
                count = c.fetchone()[0]
                position = count + 1
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                c.execute('''
                    INSERT INTO activity_submissions (activity_id, student_name, position, submitted_at)
                    VALUES (?, ?, ?, ?)
                ''', (activity_id, student_name, position, now))
                return position

    def get_activity_ranking(self, activity_id: int) -> List[Tuple[str, int, str, int]]:
        """Obtiene el ranking de una actividad específica."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT student_name, position, submitted_at, id
                FROM activity_submissions 
                WHERE activity_id = ? 
                ORDER BY position ASC
            ''', (activity_id,))
            return c.fetchall()

    def update_submission_time(self, submission_id: int, new_time: str) -> None:
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                c = conn.cursor()
                c.execute('UPDATE activity_submissions SET submitted_at = ? WHERE id = ?', (new_time, submission_id))

    def delete_activity(self, activity_id: int) -> None:
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                c = conn.cursor()
                c.execute('DELETE FROM activity_submissions WHERE activity_id = ?', (activity_id,))
                c.execute('DELETE FROM activities WHERE id = ?', (activity_id,))

    def delete_submission(self, submission_id: int) -> None:
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                c = conn.cursor()
                c.execute('DELETE FROM activity_submissions WHERE id = ?', (submission_id,))
