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

        help_msg = "Control de Actividades.\n\nAquí puedes crear tareas o actividades para llevar un registro del orden en que los alumnos las terminan.\n\n- Usa 'Registrar Entregas' durante la clase para ir marcando a los alumnos conforme acaben.\n- Usa 'Ver Ranking' para ver la clasificación final y editar tiempos si fue necesario."
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
                               lambda a=aid, n=name: self.show_activity_ranking(a, n),
                               color="#FF9F1C", px=10, py=5, font=self.f_small).pack(side="left", padx=2)

                self._make_btn(btn_frame, "✏️", 
                               lambda a=aid, n=name: self._edit_activity_dialog(a, n),
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

        body = tk.Frame(self.container, bg=BG_MAIN, padx=30, pady=20)
        body.pack(fill="both", expand=True)

        group_data = self.db.load_group(group_id)
        if not group_data:
            tk.Label(body, text="Error: No se pudo cargar el grupo.", fg="#EF233C").pack()
            return

        # Botones de navegación arriba
        bf = tk.Frame(body, bg=BG_MAIN, pady=10)
        bf.pack(fill="x")
        self._make_btn(bf, "← Volver a Actividades", self.show_activities_menu,
                       color="#6C757D", px=15, py=8).pack(side="left", padx=5)
        self._make_btn(bf, "🏆 Ver Ranking Actual", lambda: self.show_activity_ranking(activity_id, activity_name),
                       color="#FF9F1C", px=15, py=8).pack(side="left", padx=5)

        students_list = group_data['students']
        tk.Label(body, text=f"Grupo: {group_data['name']} | Haz clic para marcar entrega:",
                 font=self.f_body, bg=BG_MAIN, fg=TEXT_DARK).pack(pady=(10, 15), fill="x")

        canvas_wrap = tk.Frame(body, bg=BG_MAIN)
        canvas_wrap.pack(fill="both", expand=True)

        scroll_frame = ScrollableFrame(canvas_wrap, bg_color=BG_MAIN)
        scroll_frame.pack(fill="both", expand=True)
        grid_frame = scroll_frame.view
        
        already_submitted = [r[0] for r in self.db.get_activity_ranking(activity_id)]

        # Determinar columnas según ancho
        cols = 4 # Más columnas para aprovechar el ancho
        for i, student in enumerate(sorted(students_list)):
            is_done = student in already_submitted
            btn_color = "#6C757D" if is_done else BTN_PRIMARY
            btn_text = f"✅ {student}" if is_done else student
            
            btn = self._make_btn(grid_frame, btn_text, None, color=btn_color)
            btn.config(command=lambda b=btn, s=student: self._mark_submission(activity_id, s, b))
            if is_done: btn.config(state="disabled")
            
            btn.grid(row=i // cols, column=i % cols, sticky="nsew", padx=5, pady=5)
        
        for j in range(cols): grid_frame.columnconfigure(j, weight=1)

    def _mark_submission(self, activity_id, student_name, button):
        pos = self.db.register_submission(activity_id, student_name)
        if pos:
            button.config(text=f"✅ #{pos} {student_name}", state="disabled", bg="#6C757D")
        else:
            messagebox.showinfo("Info", "Este alumno ya ha entregado.")

    def show_activity_ranking(self, activity_id, activity_name):
        """Muestra el orden de entrega de una actividad."""
        self._clear()

        hdr = tk.Frame(self.container, bg=BG_HEADER, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"🏆  RANKING: {activity_name}",
                 font=self.f_title, bg=BG_HEADER, fg=ACCENT_GOLD).pack()

        body = tk.Frame(self.container, bg=BG_MAIN, padx=30, pady=20)
        body.pack(fill="both", expand=True)

        # Botón de navegación arriba
        bf_top = tk.Frame(body, bg=BG_MAIN, pady=10)
        bf_top.pack(fill="x")
        self._make_btn(bf_top, "← Volver a Actividades", self.show_activities_menu,
                       color="#6C757D", px=15, py=8).pack(side="left")

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
                               lambda s=sid, a=activity_id, n=activity_name: self._delete_submission_confirm(s, a, n),
                               color="#EF233C", hover="#D90429", px=4, py=1, font=self.f_small).pack(side="right", padx=2)

                self._make_btn(info_row, "✏️", 
                               lambda s=sid, t=time, a=activity_id, n=activity_name: self._edit_submission_time_dialog(s, t, a, n),
                               color="#6C757D", px=4, py=1, font=self.f_small).pack(side="right")
            
            for j in range(cols): sf_ranking.columnconfigure(j, weight=1)

    def _edit_activity_dialog(self, activity_id, current_name):
        new_name = simpledialog.askstring("Editar Actividad", "¿Nuevo nombre para la tarea?", initialvalue=current_name)
        if new_name and new_name != current_name:
            self.db.update_activity_name(activity_id, new_name)
            self.show_activities_menu()

    def _edit_submission_time_dialog(self, submission_id, current_time, aid, aname):
        new_time = simpledialog.askstring("Editar Hora", "Formato YYYY-MM-DD HH:MM:SS", initialvalue=current_time)
        if new_time and new_time != current_time:
            self.db.update_submission_time(submission_id, new_time)
            self.show_activity_ranking(aid, aname)

    def _delete_activity_confirm(self, activity_id, target_group_id):
        if messagebox.askyesno("Confirmar", "⚠️ ¿Estás seguro de eliminar esta actividad y TODAS sus entregas?"):
            self.db.delete_activity(activity_id)
            self.show_activities_menu(target_group_id)

    def _delete_submission_confirm(self, submission_id, activity_id, activity_name):
        if messagebox.askyesno("Confirmar", "¿Eliminar esta entrega? El alumno podrá registrarla nuevamente."):
            self.db.delete_submission(submission_id)
            self.show_activity_ranking(activity_id, activity_name)
