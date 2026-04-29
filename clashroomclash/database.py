# =============================================================================
#  clashroomclash/database.py
#  Gestor de base de datos SQLite para historial, grupos y leaderboard
# =============================================================================

import sqlite3
import json
from datetime import datetime


class DatabaseManager:
    """Gestiona la persistencia de datos en SQLite."""

    def __init__(self, db_path="desafio_data.db"):
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self):
        """Crea las tablas necesarias si no existen."""
        conn = sqlite3.connect(self.db_path)
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

        conn.commit()
        conn.close()

    # ── Grupos ────────────────────────────────────────────────────────────────

    def save_group(self, name, students, num_teams, teams, notes=""):
        """Guarda un grupo en la BD."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        students_json = json.dumps(students)
        teams_json = json.dumps(teams)

        c.execute('''
            INSERT INTO groups (name, students, num_teams, teams, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, students_json, num_teams, teams_json, notes, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        conn.commit()
        group_id = c.lastrowid
        conn.close()
        return group_id

    def get_groups(self):
        """Retorna todos los grupos guardados."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT id, name, created_at FROM groups ORDER BY created_at DESC')
        groups = c.fetchall()
        conn.close()
        return groups

    def load_group(self, group_id):
        """Carga un grupo por ID."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            'SELECT name, students, num_teams, teams, notes FROM groups WHERE id = ?',
            (group_id,)
        )
        row = c.fetchone()
        conn.close()

        if row:
            name, students_json, num_teams, teams_json, notes = row
            return {
                'name': name,
                'students': json.loads(students_json),
                'num_teams': num_teams,
                'teams': json.loads(teams_json),
                'notes': notes,
            }
        return None

    def delete_group(self, group_id):
        """Elimina un grupo."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('DELETE FROM groups WHERE id = ?', (group_id,))
        conn.commit()
        conn.close()

    def update_group_students(self, group_id, students):
        """Actualiza la lista de alumnos de un grupo."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        students_json = json.dumps(students)
        c.execute('UPDATE groups SET students = ? WHERE id = ?', (students_json, group_id))
        conn.commit()
        conn.close()

    # ── Historial ─────────────────────────────────────────────────────────────

    def log_event(self, event_type, group_name, description, group_id=None, details=None):
        """Registra un evento en el log global."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO activity_log (event_type, group_id, group_name, description, details, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (event_type, group_id, group_name, description, json.dumps(details), datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()

    def save_draw_history(self, group_name, teams, notes="", group_id=None):
        """Guarda un sorteo en el historial."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        teams_json = json.dumps(teams)

        c.execute('''
            INSERT INTO draw_history (group_id, group_name, teams, notes, drawn_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (group_id, group_name, teams_json, notes, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        conn.commit()
        conn.close()
        
        # Log del evento
        self.log_event("sorteo", group_name, f"Sorteo de equipos realizado ({len(teams)} equipos)", group_id, {"teams": teams})

    def get_global_log(self, limit=100):
        """Retorna el historial unificado de eventos."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT event_type, group_name, description, created_at, details 
            FROM activity_log
            ORDER BY created_at DESC LIMIT ?
        ''', (limit,))
        logs = c.fetchall()
        conn.close()
        return logs

    # ── Leaderboard ───────────────────────────────────────────────────────────

    def add_points(self, student_name, points, group_id=None, group_name=None):
        """Agrega puntos a un estudiante y lo registra en el log."""
        conn = sqlite3.connect(self.db_path)
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

        conn.commit()
        conn.close()
        
        # Log del evento
        desc = f"{student_name} recibió {points} puntos"
        self.log_event("puntos", group_name, desc, group_id, {"student": student_name, "points": points})

    def get_leaderboard(self, limit=20):
        """Retorna el leaderboard ordenado por puntos."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT student_name, points, wheel_spins FROM leaderboard
            ORDER BY points DESC LIMIT ?
        ''', (limit,))
        leaderboard = c.fetchall()
        conn.close()
        return leaderboard

    def get_group_leaderboard(self, student_names):
        """Retorna el leaderboard filtrado por una lista de nombres."""
        if not student_names:
            return []
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        placeholders = ','.join(['?'] * len(student_names))
        query = f'''
            SELECT student_name, points, wheel_spins FROM leaderboard
            WHERE student_name IN ({placeholders})
            ORDER BY points DESC
        '''
        c.execute(query, student_names)
        leaderboard = c.fetchall()
        conn.close()
        return leaderboard

    def reset_leaderboard(self):
        """Limpia el leaderboard."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('DELETE FROM leaderboard')
        conn.commit()
        conn.close()

    # ── Actividades ───────────────────────────────────────────────────────────

    def create_activity(self, name, group_id, group_name=None):
        """Crea una nueva actividad ligada a un grupo y lo registra."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute('INSERT INTO activities (name, group_id, created_at) VALUES (?, ?, ?)', (name, group_id, now))
        conn.commit()
        activity_id = c.lastrowid
        conn.close()
        
        self.log_event("actividad", group_name, f"Nueva actividad creada: {name}", group_id)
        return activity_id

    def get_activities(self):
        """Retorna todas las actividades con información de su grupo."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT a.id, a.name, a.created_at, g.name, a.group_id
            FROM activities a
            JOIN groups g ON a.group_id = g.id
            ORDER BY a.created_at DESC
        ''')
        rows = c.fetchall()
        return rows

    def update_activity_name(self, activity_id, new_name):
        """Actualiza el nombre de una actividad."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('UPDATE activities SET name = ? WHERE id = ?', (new_name, activity_id))
        conn.commit()
        conn.close()

    def register_submission(self, activity_id, student_name):
        """Registra la entrega de un alumno y le asigna la siguiente posición disponible."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Verificar si ya entregó
        c.execute('''
            SELECT id FROM activity_submissions 
            WHERE activity_id = ? AND student_name = ?
        ''', (activity_id, student_name))
        if c.fetchone():
            conn.close()
            return False # Ya entregó

        # Obtener la siguiente posición
        c.execute('''
            SELECT COUNT(*) FROM activity_submissions WHERE activity_id = ?
        ''', (activity_id,))
        count = c.fetchone()[0]
        position = count + 1
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        c.execute('''
            INSERT INTO activity_submissions (activity_id, student_name, position, submitted_at)
            VALUES (?, ?, ?, ?)
        ''', (activity_id, student_name, position, now))
        
        conn.commit()
        conn.close()
        return position

    def get_activity_ranking(self, activity_id):
        """Obtiene el ranking de una actividad específica."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT student_name, position, submitted_at, id
            FROM activity_submissions 
            WHERE activity_id = ? 
            ORDER BY position ASC
        ''', (activity_id,))
        rows = c.fetchall()
        conn.close()
        return rows

    def update_submission_time(self, submission_id, new_time):
        """Actualiza la hora de una entrega específica."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('UPDATE activity_submissions SET submitted_at = ? WHERE id = ?', (new_time, submission_id))
        conn.commit()
        conn.close()
