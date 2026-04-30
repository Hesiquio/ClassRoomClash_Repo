# =============================================================================
#  classroomclash/activities.py
#  Control de entregas y ranking de actividades (Independiente del sorteo)
# =============================================================================

import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from .constants import (
    BG_MAIN, BG_CARD, BG_HEADER, BTN_PRIMARY, BTN_HOVER,
    TEXT_DARK, TEXT_LIGHT, TEXT_MUTED, ACCENT_GOLD
)
from .widgets import ScrollableFrame

class ActivitiesMixin:
    """Mixin para la gestión de actividades y control de entregas."""

    def show_activities_menu(self, group_id=None):
        """Pantalla principal de gestión de actividades."""
        self._clear()
        
        # Si venimos de un grupo específico, usarlo como contexto
        target_group_id = group_id or getattr(self.state, 'current_group_id', None)
        group_name = getattr(self.state, 'current_group_name', 'Global') if target_group_id else "Global"

        hdr = tk.Frame(self.container, bg=BG_HEADER, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"📋  ACTIVIDADES: {group_name.upper()}",
                 font=self.f_header, bg=BG_HEADER, fg=TEXT_LIGHT).pack()

        # Botón Home en el header
        home_btn_f = tk.Frame(hdr, bg=BG_HEADER)
        home_btn_f.place(relx=0.03, rely=0.5, anchor="w")
        self._make_btn(home_btn_f, "🏠 Inicio", self.show_main_menu, color="#4361EE", px=10, py=5, font=self.f_small).pack()

        help_msg = (
            "Control de Actividades.\n\n"
            "Registra el orden en que los alumnos terminan las tareas para motivar la competencia sana.\n\n"
            "- 📥 Registrar Entregas: Haz clic en cada alumno conforme terminen para asignar su posición.\n"
            "- 🏆 Ver Ranking: Consulta la tabla de posiciones de la actividad actual.\n"
            "- ✏️ Editar/🗑️ Eliminar: Gestiona las actividades creadas.\n\n"
            "Los resultados de estas actividades se pueden exportar a Excel desde el Panel del Grupo."
        )
        help_btn = tk.Frame(hdr, bg=BG_HEADER)
        help_btn.place(relx=0.97, rely=0.5, anchor="e")
        self._make_btn(help_btn, "❓ Ayuda", lambda: self._show_help_dialog("Control de Actividades", help_msg), color="#4361EE", px=10, py=5, font=self.f_small).pack()

        body = tk.Frame(self.container, bg=BG_MAIN, padx=30, pady=20)
        body.pack(fill="both", expand=True)

        # Botón nueva actividad
        # Botón nueva actividad (si hay grupo cargado, se asigna automáticamente)
        cmd = lambda: self._create_activity_auto(target_group_id) if target_group_id else self._create_activity_dialog
        self._make_btn(body, "➕  Nueva Actividad", cmd,
                       color="#06D6A0", px=20, py=10).pack(pady=(0, 20))

        tk.Label(body, text="Actividades Recientes:",
                 font=self.f_title, bg=BG_MAIN, fg=TEXT_DARK).pack(anchor="w")

        # Lista de actividades con scroll
        canvas_wrap = tk.Frame(body, bg=BG_MAIN)
        canvas_wrap.pack(fill="both", expand=True)

        scroll_frame = ScrollableFrame(canvas_wrap, bg_color=BG_MAIN)
        scroll_frame.pack(fill="both", expand=True)
        sf = scroll_frame.view

        try:
            all_activities = self.db.get_activities()
            if target_group_id:
                activities = [a for a in all_activities if a[4] == target_group_id]
            else:
                activities = all_activities
        except Exception:
            activities = []

        if not activities:
            tk.Label(sf, text="No hay actividades creadas.",
                     font=self.f_body, bg=BG_MAIN, fg=TEXT_MUTED).pack(pady=20)
        else:
            for aid, name, created, gname, gid in activities:
                card = tk.Frame(sf, bg=BG_CARD, highlightbackground="#DEE2E6",
                                highlightthickness=1, padx=15, pady=10)
                card.pack(fill="x", pady=5)

                info = tk.Frame(card, bg=BG_CARD)
                info.pack(side="left", fill="both", expand=True)
                tk.Label(info, text=name, font=self.f_name, bg=BG_CARD, fg=TEXT_DARK).pack(anchor="w")
                tk.Label(info, text=f"Grupo: {gname}  |  Iniciada: {created}", 
                         font=self.f_small, bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w")

                btn_frame = tk.Frame(card, bg=BG_CARD)
                btn_frame.pack(side="right")
                
                self._make_btn(btn_frame, "Registrar Entregas", 
                               lambda a=aid, n=name, g=gid: self.show_submission_screen(a, n, g),
                               color=BTN_PRIMARY, px=10, py=5, font=self.f_small).pack(side="left", padx=2)
                
                self._make_btn(btn_frame, "Ver Ranking", 
                               lambda a=aid, n=name, g=gid: self.show_activity_ranking(a, n, g),
                               color="#FF9F1C", px=10, py=5, font=self.f_small).pack(side="left", padx=2)

                self._make_btn(btn_frame, "✏️", 
                               lambda a=aid, n=name, g=gid: self._edit_activity_dialog(a, n, g),
                               color="#4361EE", px=8, py=5, font=self.f_small).pack(side="left", padx=2)

                self._make_btn(btn_frame, "🗑️", 
                               lambda a=aid: self._delete_activity_confirm(a, target_group_id),
                               color="#EF233C", hover="#D90429", px=8, py=5, font=self.f_small).pack(side="left", padx=2)

        back_cmd = lambda: self.show_group_dashboard(target_group_id) if target_group_id else self.show_main_menu
        self._make_btn(body, "← Volver", back_cmd,
                       color="#6C757D", hover="#495057", px=20, py=8, font=self.f_body).pack(pady=10)

    def _create_activity_auto(self, group_id):
        """Crea una actividad directamente para el grupo actual."""
        name = simpledialog.askstring("Nueva Actividad", "¿Nombre de la tarea?")
        if name:
            self.db.create_activity(name, group_id, group_name=getattr(self.state, 'current_group_name', None))
            self.show_activities_menu(group_id)

    def _create_activity_dialog(self):
        """Diálogo para crear actividad eligiendo un grupo."""
        groups = self.db.get_groups()
        if not groups:
            messagebox.showwarning("Atención", "Primero debes crear o guardar al menos un grupo.")
            return

        name = simpledialog.askstring("Nueva Actividad", "¿Nombre de la tarea?")
        if not name: return

        win = tk.Toplevel(self)
        win.title("Seleccionar Grupo")
        win.geometry("350x450")
        win.configure(bg=BG_MAIN)
        win.transient(self)
        win.grab_set()

        tk.Label(win, text="¿Para qué grupo es la actividad?", 
                 font=self.f_title, bg=BG_MAIN, pady=10).pack()

        lb = tk.Listbox(win, font=self.f_body, height=10)
        lb.pack(fill="both", expand=True, padx=20, pady=10)
        
        for gid, gname, date in groups:
            lb.insert("end", f"{gname} ({date.split(' ')[0]})")

        def _confirm():
            sel = lb.curselection()
            if not sel: return
            group_id = groups[sel[0]][0]
            group_name = groups[sel[0]][1]
            self.db.create_activity(name, group_id, group_name=group_name)
            win.destroy()
            self.show_activities_menu()

        self._make_btn(win, "Crear Actividad", _confirm, color="#06D6A0").pack(pady=5)
        self._make_btn(win, "Cancelar", win.destroy, color="#6C757D").pack(pady=5)

    def show_submission_screen(self, activity_id, activity_name, group_id):
        """Pantalla para marcar entregas basada en los alumnos del grupo de la actividad."""
        self._clear()

        hdr = tk.Frame(self.container, bg=BG_HEADER, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"📥  REGISTRANDO: {activity_name}",
                 font=self.f_title, bg=BG_HEADER, fg=ACCENT_GOLD).pack()

        # Botón Home en el header
        home_btn_f = tk.Frame(hdr, bg=BG_HEADER)
        home_btn_f.place(relx=0.03, rely=0.5, anchor="w")
        self._make_btn(home_btn_f, "🏠 Inicio", self.show_main_menu, color="#4361EE", px=10, py=5, font=self.f_small).pack()

        body = tk.Frame(self.container, bg=BG_MAIN, padx=30, pady=20)
        body.pack(fill="both", expand=True)

        group_data = self.db.load_group(group_id)
        if not group_data:
            tk.Label(body, text="Error: No se pudo cargar el grupo.", fg="#EF233C").pack()
            return

        # Botones de navegación arriba
        bf = tk.Frame(body, bg=BG_MAIN, pady=10)
        bf.pack(fill="x")
        self._make_btn(bf, "← Volver a Actividades", lambda: self.show_activities_menu(group_id),
                       color="#6C757D", px=15, py=8, font=self.f_small).pack(side="left", padx=5)
        self._make_btn(bf, "🏆 Ver Ranking Actual", lambda: self.show_activity_ranking(activity_id, activity_name, group_id),
                       color="#FF9F1C", px=15, py=8, font=self.f_small).pack(side="left", padx=5)
        
        # Botón Home a la derecha
        self._make_btn(bf, "🏠 Inicio", self.show_main_menu,
                       color="#2B2D42", px=15, py=8, font=self.f_small).pack(side="right")

        students_list = group_data['students']
        tk.Label(body, text=f"Grupo: {group_data['name']} | Haz clic para marcar entrega:",
                 font=self.f_body, bg=BG_MAIN, fg=TEXT_DARK).pack(pady=(10, 15), fill="x")

        canvas_wrap = tk.Frame(body, bg=BG_MAIN)
        canvas_wrap.pack(fill="both", expand=True)

        scroll_frame = ScrollableFrame(canvas_wrap, bg_color=BG_MAIN)
        scroll_frame.pack(fill="both", expand=True)
        grid_frame = scroll_frame.view
        
        submissions_raw = self.db.get_activity_ranking(activity_id)
        # submission_map: {nombre: posicion}
        # submissions_raw trae (student_name, position, submitted_at, id)
        submission_map = {row[0]: row[1] for row in submissions_raw}

        # Determinar columnas según ancho
        cols = 4 
        for i, student in enumerate(sorted(students_list)):
            pos = submission_map.get(student)
            is_done = pos is not None
            from .constants import PASTEL_COLORS
            
            # Color por defecto si no ha entregado
            btn_color = BTN_PRIMARY
            text_color = TEXT_LIGHT
            btn_text = student
            
            if is_done:
                # Si ya entregó, usar un color pastel de la lista basado en su posición o índice
                btn_color = PASTEL_COLORS[i % len(PASTEL_COLORS)]
                text_color = TEXT_DARK
                btn_text = f"✅ #{pos} {student}"
            
            btn = self._make_btn(grid_frame, btn_text, None, color=btn_color, fg=text_color)
            btn.config(command=lambda b=btn, s=student, idx=i: self._mark_submission(activity_id, s, b, idx))
            if is_done: btn.config(state="disabled")
            
            btn.grid(row=i // cols, column=i % cols, sticky="nsew", padx=5, pady=5)
        
        for j in range(cols): grid_frame.columnconfigure(j, weight=1)

    def _mark_submission(self, activity_id, student_name, button, student_index):
        pos = self.db.register_submission(activity_id, student_name)
        if pos:
            from .constants import PASTEL_COLORS
            # Cambiar a un color pastel suave y texto oscuro
            new_bg = PASTEL_COLORS[student_index % len(PASTEL_COLORS)]
            button.config(text=f"✅ #{pos} {student_name}", state="disabled", bg=new_bg, fg=TEXT_DARK)
        else:
            messagebox.showinfo("Info", "Este alumno ya ha entregado.")

    def show_activity_ranking(self, activity_id, activity_name, group_id):
        """Muestra el orden de entrega de una actividad."""
        self._clear()

        hdr = tk.Frame(self.container, bg=BG_HEADER, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"🏆  RANKING: {activity_name}",
                 font=self.f_title, bg=BG_HEADER, fg=ACCENT_GOLD).pack()

        # Botón Home en el header
        home_btn_f = tk.Frame(hdr, bg=BG_HEADER)
        home_btn_f.place(relx=0.03, rely=0.5, anchor="w")
        self._make_btn(home_btn_f, "🏠 Inicio", self.show_main_menu, color="#4361EE", px=10, py=5, font=self.f_small).pack()

        body = tk.Frame(self.container, bg=BG_MAIN, padx=30, pady=20)
        body.pack(fill="both", expand=True)

        # Botón de navegación arriba
        bf_top = tk.Frame(body, bg=BG_MAIN, pady=10)
        bf_top.pack(fill="x")
        
        self._make_btn(bf_top, "← Volver a Entregas", 
                       lambda: self.show_submission_screen(activity_id, activity_name, group_id),
                       color="#4361EE", px=15, py=8, font=self.f_small).pack(side="left", padx=(0, 10))
        
        self._make_btn(bf_top, "📋 Menú Actividades", lambda: self.show_activities_menu(group_id),
                       color="#6C757D", px=15, py=8, font=self.f_small).pack(side="left")

        # Botón Home a la derecha
        self._make_btn(bf_top, "🏠 Inicio", self.show_main_menu,
                       color="#2B2D42", px=15, py=8, font=self.f_small).pack(side="right")

        ranking = self.db.get_activity_ranking(activity_id)

        if not ranking:
            tk.Label(body, text="Aún no hay entregas registradas.",
                     font=self.f_body, bg=BG_MAIN, fg=TEXT_MUTED).pack(pady=20)
        else:
            canvas_wrap = tk.Frame(body, bg=BG_MAIN)
            canvas_wrap.pack(fill="both", expand=True)

            scroll_frame = ScrollableFrame(canvas_wrap, bg_color=BG_MAIN)
            scroll_frame.pack(fill="both", expand=True)
            sf_ranking = scroll_frame.view

            cols = 4 # Cuadrícula para ahorrar espacio
            for i, (student, pos, time, sid) in enumerate(ranking):
                is_podium = pos <= 3
                card = tk.Frame(sf_ranking, bg=BG_CARD, 
                                highlightbackground=ACCENT_GOLD if is_podium else "#DEE2E6",
                                highlightthickness=2 if is_podium else 1, padx=10, pady=8)
                card.grid(row=i // cols, column=i % cols, sticky="nsew", padx=5, pady=5)
                
                # Medalla o Posición
                medal = "🥇" if pos == 1 else "🥈" if pos == 2 else "🥉" if pos == 3 else f"#{pos}"
                tk.Label(card, text=medal, font=self.f_title if is_podium else self.f_body, 
                         bg=BG_CARD, fg=TEXT_DARK).pack()
                
                # Nombre
                tk.Label(card, text=student, font=self.f_name if is_podium else self.f_body, 
                         bg=BG_CARD, fg=TEXT_DARK, wraplength=150).pack()
                
                # Hora y Edición
                info_row = tk.Frame(card, bg=BG_CARD)
                info_row.pack(fill="x", pady=(5, 0))
                
                tk.Label(info_row, text=time.split(' ')[1] if ' ' in time else time, 
                         font=self.f_small, bg=BG_CARD, fg=TEXT_MUTED).pack(side="left", expand=True)
                
                self._make_btn(info_row, "🗑️", 
                               lambda s=sid, a=activity_id, n=activity_name, g=group_id: self._delete_submission_confirm(s, a, n, g),
                               color="#EF233C", hover="#D90429", px=4, py=1, font=self.f_small).pack(side="right", padx=2)

                self._make_btn(info_row, "✏️", 
                               lambda s=sid, t=time, a=activity_id, n=activity_name, g=group_id: self._edit_submission_time_dialog(s, t, a, n, g),
                               color="#6C757D", px=4, py=1, font=self.f_small).pack(side="right")
            
            for j in range(cols): sf_ranking.columnconfigure(j, weight=1)

    def _edit_activity_dialog(self, activity_id, current_name, gid):
        new_name = simpledialog.askstring("Editar Actividad", "¿Nuevo nombre para la tarea?", initialvalue=current_name)
        if new_name and new_name != current_name:
            self.db.update_activity_name(activity_id, new_name)
            self.show_activities_menu(gid)

    def _edit_submission_time_dialog(self, submission_id, current_time, aid, aname, gid):
        new_time = simpledialog.askstring("Editar Hora", "Formato YYYY-MM-DD HH:MM:SS", initialvalue=current_time)
        if new_time and new_time != current_time:
            self.db.update_submission_time(submission_id, new_time)
            self.show_activity_ranking(aid, aname, gid)

    def _delete_activity_confirm(self, activity_id, target_group_id):
        if messagebox.askyesno("Confirmar", "⚠️ ¿Estás seguro de eliminar esta actividad y TODAS sus entregas?"):
            self.db.delete_activity(activity_id)
            self.show_activities_menu(target_group_id)

    def _delete_submission_confirm(self, submission_id, activity_id, activity_name, group_id):
        if messagebox.askyesno("Confirmar", "¿Eliminar esta entrega? El alumno podrá registrarla nuevamente."):
            self.db.delete_submission(submission_id)
            self.show_activity_ranking(activity_id, activity_name, group_id)
