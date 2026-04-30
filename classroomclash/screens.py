# =============================================================================
#  classroomclash/screens.py
#  Pantallas: Menú principal, Configuración, Grupos, Historial, Leaderboard
# =============================================================================

import math
import random
import csv
import json
import tkinter as tk
from tkinter import messagebox, filedialog

try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

from .constants import (
    BG_MAIN, BG_CARD, BG_HEADER,
    BTN_PRIMARY, BTN_HOVER, BTN_REVEAL, BTN_REVEAL_H,
    TEXT_DARK, TEXT_LIGHT, TEXT_MUTED, ACCENT_GOLD,
    TEAM_COLORS,
)
from .widgets import ScrollableFrame


class ScreensMixin:
    """
    Mixin que agrupa las pantallas estáticas de la app:
    menú principal, configuración, grupos guardados, historial y leaderboard.
    Se mezcla en ClassRoomClashApp junto con AnimationMixin y WheelMixin.
    """

    # =========================================================================
    #  UTILIDADES COMUNES
    # =========================================================================

    def _clear(self):
        """Destruye todos los widgets del contenedor para cambiar de pantalla."""
        for w in self.container.winfo_children():
            w.destroy()

    def _make_btn(self, parent, text, cmd, color=BTN_PRIMARY, hover=BTN_HOVER,
                  px=24, py=12, font=None, width=None, fg=TEXT_LIGHT):
        """
        Crea un botón flat con efecto hover.
        """
        f = font or self.f_btn
        b = tk.Button(
            parent, text=text, command=cmd,
            bg=color, fg=fg, font=f,
            relief="flat", bd=0,
            activebackground=hover, activeforeground=fg,
            cursor="hand2", padx=px, pady=py,
        )
        if width:
            b.config(width=width)
        b.bind("<Enter>", lambda e: b.config(bg=hover))
        b.bind("<Leave>", lambda e: b.config(bg=color))
        return b

    def _labeled_section(self, parent, text, row, col, colspan=1, pady=(0, 8)):
        """Crea un Label de sección con estilo uniforme."""
        lbl = tk.Label(parent, text=text, font=self.f_title,
                       bg=BG_MAIN, fg=TEXT_DARK, anchor="w")
        lbl.grid(row=row, column=col, columnspan=colspan,
                 sticky="w", pady=pady)
        return lbl

    # =========================================================================
    #  PANTALLA 0 — MENÚ PRINCIPAL
    # =========================================================================

    def show_main_menu(self):
        """Pantalla inicial: Lista de grupos y herramientas globales."""
        self._clear()

        hdr = tk.Frame(self.container, bg=BG_HEADER, pady=20)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🎮  CLASSROOM CLASH",
                 font=self.f_header, bg=BG_HEADER, fg=TEXT_LIGHT).pack()
        tk.Label(hdr, text="Tus Grupos y Herramientas",
                 font=self.f_small, bg=BG_HEADER, fg=TEXT_MUTED).pack(pady=(3, 0))

        # Botón Home en el header
        home_btn_f = tk.Frame(hdr, bg=BG_HEADER)
        home_btn_f.place(relx=0.03, rely=0.5, anchor="w")
        self._make_btn(home_btn_f, "🏠 Inicio", self.show_main_menu, color="#4361EE", px=10, py=5, font=self.f_small).pack()

        help_msg = (
            "Bienvenido a ClassRoom Clash.\n\n"
            "En esta pantalla puedes administrar tus grupos escolares. Cada grupo es un espacio separado con sus propios alumnos, historial de puntos, y actividades.\n\n"
            "Acciones:\n"
            "- ➕ Crear Nuevo Grupo: Inicia un grupo desde cero o pegando una lista.\n"
            "- 📦 Archivar: Si ya no usas un grupo, archívalo para limpiar la vista. Puedes recuperarlo marcando 'Mostrar Archivados'.\n"
            "- ✏️ Renombrar: Cambia el nombre de cualquier grupo.\n"
            "- 🗑️ Eliminar: Borra el grupo y todo su historial de forma permanente.\n\n"
            "Al final encontrarás el Historial Global y el Leaderboard con los mejores puntajes de todos tus grupos."
        )
        help_btn = tk.Frame(hdr, bg=BG_HEADER)
        help_btn.place(relx=0.97, rely=0.5, anchor="e")
        self._make_btn(help_btn, "❓ Ayuda", lambda: self._show_help_dialog("Menú Principal", help_msg), color="#4361EE", px=10, py=5, font=self.f_small).pack()

        body = tk.Frame(self.container, bg=BG_MAIN, padx=40, pady=20)
        body.pack(fill="both", expand=True)

        # Botón para crear nuevo grupo (Hero)
        self._make_btn(body, "➕  Crear Nuevo Grupo", self.show_create_group_screen,
                       color="#06D6A0", px=20, py=12, font=self.f_title).pack(pady=(0, 25))

        # Lista de Grupos
        list_hdr = tk.Frame(body, bg=BG_MAIN)
        list_hdr.pack(fill="x", pady=(0, 10))
        tk.Label(list_hdr, text="MIS GRUPOS:",
                 font=self.f_title, bg=BG_MAIN, fg=TEXT_DARK).pack(side="left")
        
        if not hasattr(self, 'show_archived_toggle'):
            self.show_archived_toggle = tk.BooleanVar(value=False)
        
        tk.Checkbutton(list_hdr, text="Mostrar Archivados", variable=self.show_archived_toggle,
                       command=self.show_main_menu, bg=BG_MAIN, font=self.f_small, fg=TEXT_MUTED).pack(side="right")

        groups = self.db.get_groups(include_archived=self.show_archived_toggle.get())

        if not groups:
            tk.Label(body, text="No hay grupos guardados aún. Crea uno para empezar.",
                     font=self.f_body, bg=BG_MAIN, fg=TEXT_MUTED).pack(pady=20)
        else:
            scroll_frame = ScrollableFrame(body, bg_color=BG_MAIN)
            scroll_frame.pack(fill="both", expand=True)
            sf = scroll_frame.view

            for group_id, group_name, created_at, is_archived in groups:
                bg_color = "#E9ECEF" if is_archived else BG_CARD
                card = tk.Frame(sf, bg=bg_color, highlightbackground="#DEE2E6", 
                                highlightthickness=1, padx=15, pady=10)
                card.pack(fill="x", pady=5)

                info = tk.Frame(card, bg=bg_color)
                info.pack(side="left", fill="both", expand=True)
                
                title_text = f"{group_name} {'(Archivado)' if is_archived else ''}"
                tk.Label(info, text=title_text, font=self.f_name, bg=bg_color, fg=TEXT_DARK).pack(anchor="w")
                tk.Label(info, text=f"Creado: {created_at}", font=self.f_small, bg=bg_color, fg=TEXT_MUTED).pack(anchor="w")

                bc = tk.Frame(card, bg=bg_color)
                bc.pack(side="right")

                self._make_btn(bc, "Gestionar →", lambda gid=group_id: self.show_group_dashboard(gid),
                               color="#4361EE", px=15, py=6, font=self.f_small).pack(side="left", padx=3)

                arch_text = "📦 Restaurar" if is_archived else "📦 Archivar"
                self._make_btn(bc, arch_text, lambda gid=group_id, arch=is_archived: self._toggle_archive(gid, not arch),
                               color="#6C757D", hover="#495057", px=10, py=6, font=self.f_small).pack(side="left", padx=3)

                self._make_btn(bc, "✏️ Renombrar", lambda gid=group_id, gname=group_name: self._rename_group_prompt(gid, gname),
                               color="#FFCA3A", hover="#FFB703", px=10, py=6, font=self.f_small).pack(side="left", padx=3)
                
                self._make_btn(bc, "🗑️", lambda gid=group_id: self._delete_group_confirm(gid),
                               color="#EF233C", px=10, py=6, font=self.f_small).pack(side="left", padx=3)

        # Footer Global
        tk.Label(body, text="Herramientas Globales",
                 font=self.f_small, bg=BG_MAIN, fg=TEXT_MUTED).pack(pady=(25, 10))

        grid_cols = tk.Frame(body, bg=BG_MAIN)
        grid_cols.pack(fill="x")
        grid_cols.columnconfigure((0, 1, 2), weight=1)

        self._make_btn(grid_cols, "📊 Historial", self.show_history,
                       color="#FF9F1C", px=10, py=8).grid(row=0, column=0, padx=5, sticky="ew")

        self._make_btn(grid_cols, "🏆 Leaderboard", self.show_leaderboard,
                       color="#FFD60A", px=10, py=8).grid(row=0, column=1, padx=5, sticky="ew")

        self._make_btn(grid_cols, "❌ Salir", self.quit,
                       color="#6C757D", px=10, py=8).grid(row=0, column=2, padx=5, sticky="ew")


    def show_group_dashboard(self, group_id):
        """Panel central de control para un grupo específico."""
        data = self.db.load_group(group_id)
        if not data: return

        self._clear()
        self.state.current_group_id = group_id
        self.state.current_group_name = data['name']
        self.state.students = data['students'][:]

        hdr = tk.Frame(self.container, bg=BG_HEADER, pady=20)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"📂  GRUPO: {data['name']}",
                 font=self.f_header, bg=BG_HEADER, fg=TEXT_LIGHT).pack()

        # Botón Home en el header
        home_btn_f = tk.Frame(hdr, bg=BG_HEADER)
        home_btn_f.place(relx=0.03, rely=0.5, anchor="w")
        self._make_btn(home_btn_f, "🏠 Inicio", self.show_main_menu, color="#4361EE", px=10, py=5, font=self.f_small).pack()

        # Botón Home en el header
        home_btn_f = tk.Frame(hdr, bg=BG_HEADER)
        home_btn_f.place(relx=0.03, rely=0.5, anchor="w")
        self._make_btn(home_btn_f, "🏠 Inicio", self.show_main_menu, color="#4361EE", px=10, py=5, font=self.f_small).pack()

        help_msg = (
            "Panel de Control del Grupo.\n\n"
            "Este es el centro de mando para el grupo seleccionado. Tienes 4 herramientas principales:\n\n"
            "1. 🎲 Sorteo: Crea equipos balanceados al azar con animaciones tipo Champions.\n"
            "2. 🎡 Tómbola: Elige alumnos al azar para participar y asígnales puntos.\n"
            "3. 📋 Actividades: Registra el orden de entrega de tareas en tiempo real.\n"
            "4. 🏆 Ranking: Mira el progreso de puntos de este grupo específico.\n\n"
            "Otras opciones:\n"
            "- 📊 Descargar Reporte Excel: Genera un informe profesional con puntos y resultados de actividades.\n"
            "- ✏️ Editar Alumnos: Agrega o quita integrantes del grupo actual."
        )
        help_btn = tk.Frame(hdr, bg=BG_HEADER)
        help_btn.place(relx=0.97, rely=0.5, anchor="e")
        self._make_btn(help_btn, "❓ Ayuda", lambda: self._show_help_dialog("Dashboard del Grupo", help_msg), color="#4361EE", px=10, py=5, font=self.f_small).pack()
        
        body = tk.Frame(self.container, bg=BG_MAIN, padx=40, pady=30)
        body.pack(fill="both", expand=True)

        # Resumen rápido en una tarjeta
        stats_card = tk.Frame(body, bg=BG_CARD, padx=20, pady=15, 
                              highlightbackground="#DEE2E6", highlightthickness=1)
        stats_card.pack(fill="x", pady=(0, 30))
        
        tk.Label(stats_card, text=f"📊 Resumen: {len(self.state.students)} alumnos inscritos", 
                 font=self.f_title, bg=BG_CARD, fg=TEXT_DARK).pack(side="left")
        
        self._make_btn(stats_card, "✏️ Editar Alumnos", 
                       lambda: self._edit_group_students(group_id),
                       color="#6C757D", px=15, py=5, font=self.f_small).pack(side="right")

        # Rejilla de acciones
        actions_frame = tk.Frame(body, bg=BG_MAIN)
        actions_frame.pack(fill="both", expand=True)
        actions_frame.columnconfigure((0, 1), weight=1, uniform="equal")

        # Fila 1: Sorteo y Ruleta
        self._make_btn(actions_frame, "🎲   Sorteo de Equipos\n(Champions Style)",
                       lambda: self.show_config_screen(group_id),
                       color="#4361EE", px=20, py=25, font=self.f_title).grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self._make_btn(actions_frame, "🎡   Tómbola Clash\nde Participación",
                       self.show_wheel_screen,
                       color="#F72585", px=20, py=25, font=self.f_title).grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Fila 2: Actividades y Ranking
        self._make_btn(actions_frame, "📋   Control de\nActividades",
                       self.show_activities_menu,
                       color="#06D6A0", px=20, py=25, font=self.f_title).grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self._make_btn(actions_frame, "🏆   Ranking / Leaderboard\ndel Grupo",
                       lambda: self.show_leaderboard(group_id),
                       color="#FFD60A", px=20, py=25, font=self.f_title).grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        # Botones inferiores
        tk.Frame(body, height=10, bg=BG_MAIN).pack()
        
        btns_low = tk.Frame(body, bg=BG_MAIN)
        btns_low.pack(fill="x")
        
        self._make_btn(btns_low, "📊  Descargar Reporte Excel", 
                       lambda: self.show_export_screen(group_id),
                       color="#3A0CA3", px=20, py=10, font=self.f_title).pack(pady=5)

        self._make_btn(body, "← Volver", self.show_main_menu,
                       color="#6C757D", px=20, py=10).pack()

    def _load_and_sort(self, group_id):
        """Carga un grupo y va directamente al sorteo."""
        data = self.db.load_group(group_id)
        if data:
            self.state.students = data['students'][:]
            random.shuffle(self.state.students)
            self.state.num_teams = data['num_teams']
            self.state.teams = [[] for _ in range(self.state.num_teams)]
            self.state.student_index = 0
            self.state.assign_index = 0
            self.state.is_animating = False
            self.state.current_group_id = group_id
            self.show_sorteo_screen()

    def _delete_group_confirm(self, group_id):
        """Confirma la eliminación de un grupo."""
        if messagebox.askyesno("Confirmar", "⚠️ ¿Estás completamente seguro de eliminar este grupo y TODO su historial? Esta acción no se puede deshacer."):
            self.db.delete_group(group_id)
            self.show_main_menu()

    def _rename_group_prompt(self, group_id, current_name):
        from tkinter import simpledialog
        new_name = simpledialog.askstring("Renombrar", f"Nuevo nombre para '{current_name}':", initialvalue=current_name)
        if new_name and new_name.strip() != current_name:
            self.db.rename_group(group_id, new_name.strip())
            self.show_main_menu()

    def _toggle_archive(self, group_id, archive):
        msg = "¿Archivar este grupo? Dejará de verse en la lista principal." if archive else "¿Restaurar este grupo?"
        if messagebox.askyesno("Confirmar", msg):
            self.db.toggle_archive_group(group_id, archive)
            self.show_main_menu()

    def _edit_group_students(self, group_id):
        """Abre un editor para los nombres de los alumnos del grupo."""
        data = self.db.load_group(group_id)
        if not data: return

        # Ventana de edición
        win = tk.Toplevel(self)
        win.title(f"Editar Alumnos: {data['name']}")
        win.geometry("500x600")
        win.configure(bg=BG_MAIN)
        win.transient(self)
        win.grab_set()

        tk.Label(win, text=f"Editando Alumnos de: {data['name']}", 
                 font=self.f_title, bg=BG_MAIN, pady=10).pack()

        txt = tk.Text(win, font=self.f_body, height=20)
        txt.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Cargar nombres actuales
        txt.insert("1.0", "\n".join(data['students']))

        def _save():
            raw = txt.get("1.0", "end-1c").strip()
            new_list = [l.strip() for l in raw.splitlines() if l.strip()]
            if not new_list:
                messagebox.showerror("Error", "La lista no puede estar vacía.")
                return
            self.db.update_group_students(group_id, new_list)
            win.destroy()
            self.show_main_menu()

        self._make_btn(win, "💾 Guardar Cambios", _save, color="#06D6A0").pack(pady=10)
        self._make_btn(win, "Cancelar", win.destroy, color="#6C757D").pack(pady=5)

    # =========================================================================
    #  PANTALLA — EXPORTACIÓN CSV
    # =========================================================================

    def show_export_screen(self, group_id):
        """Pantalla para elegir qué datos exportar."""
        data = self.db.load_group(group_id)
        if not data: return
        
        self._clear()
        hdr = tk.Frame(self.container, bg=BG_HEADER, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"📊  EXPORTAR REPORTE: {data['name']}",
                 font=self.f_header, bg=BG_HEADER, fg=TEXT_LIGHT).pack()

        # Botón Home en el header
        home_btn_f = tk.Frame(hdr, bg=BG_HEADER)
        home_btn_f.place(relx=0.03, rely=0.5, anchor="w")
        self._make_btn(home_btn_f, "🏠 Inicio", self.show_main_menu, color="#4361EE", px=10, py=5, font=self.f_small).pack()

        body = tk.Frame(self.container, bg=BG_MAIN, padx=40, pady=30)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="Selecciona los datos que deseas incluir en el reporte:",
                 font=self.f_title, bg=BG_MAIN, fg=TEXT_DARK).pack(pady=(0, 20))

        options_frame = tk.Frame(body, bg=BG_CARD, padx=20, pady=20, relief="flat", bd=1)
        options_frame.pack(fill="x")

        include_points = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Puntos de Tómbola / Participación", 
                       variable=include_points, font=self.f_body, bg=BG_CARD, activebackground=BG_CARD).pack(anchor="w", pady=5)

        activities = [a for a in self.db.get_activities() if a[4] == group_id]
        activity_vars = []
        
        if activities:
            tk.Label(options_frame, text="Actividades:", font=self.f_name, bg=BG_CARD).pack(anchor="w", pady=(10, 5))
            for aid, name, _, _, _ in activities:
                var = tk.BooleanVar(value=True)
                tk.Checkbutton(options_frame, text=f"📋 {name}", variable=var, 
                               font=self.f_body, bg=BG_CARD, activebackground=BG_CARD).pack(anchor="w", padx=20)
                activity_vars.append((aid, name, var))

        def _do_export():
            selected_activities = [(aid, name) for aid, name, var in activity_vars if var.get()]
            if EXCEL_AVAILABLE:
                self._execute_excel_export(group_id, data['name'], data['students'], include_points.get(), selected_activities)
            else:
                self._execute_csv_export(group_id, data['name'], data['students'], include_points.get(), selected_activities)

        tk.Frame(body, height=20, bg=BG_MAIN).pack()
        btn_text = "🚀 Generar Reporte Excel" if EXCEL_AVAILABLE else "🚀 Generar Reporte CSV"
        self._make_btn(body, btn_text, _do_export, color="#3A0CA3", px=40, py=15).pack()
        self._make_btn(body, "Cancelar", lambda: self.show_group_dashboard(group_id), color="#6C757D", px=20, py=8).pack(pady=10)

    def _execute_excel_export(self, group_id, group_name, students, points_enabled, selected_activities):
        """Genera un archivo Excel (.xlsx) con estilos profesionales."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Libro de Excel", "*.xlsx")],
            initialfile=f"Reporte_{group_name.replace(' ', '_')}.xlsx"
        )
        if not filepath: return

        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Reporte de Clase"

            # Estilos
            header_fill = PatternFill(start_color="3A0CA3", end_color="3A0CA3", fill_type="solid")
            header_font = Font(color="FFFFFF", bold=True, size=12)
            stripe_fill = PatternFill(start_color="F8F9FA", end_color="F8F9FA", fill_type="solid")
            center_align = Alignment(horizontal="center", vertical="center")
            border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                            top=Side(style='thin'), bottom=Side(style='thin'))

            # Cabecera
            headers = ["Estudiante"]
            if points_enabled: headers.append("Puntos Participación")
            for _, aname in selected_activities: headers.append(aname)
            
            ws.append(headers)
            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = center_align
                cell.border = border

            # Datos
            points_data = {}
            if points_enabled:
                lb = self.db.get_group_leaderboard(students)
                points_data = {name: pts for name, pts, _ in lb}

            act_results = {}
            for aid, aname in selected_activities:
                ranking = self.db.get_activity_ranking(aid)
                act_results[aname] = {name: f"#{pos}" for name, pos, _, _ in ranking}

            for row_idx, student in enumerate(sorted(students), 2):
                row_data = [student]
                if points_enabled: row_data.append(points_data.get(student, 0))
                for _, aname in selected_activities:
                    row_data.append(act_results[aname].get(student, "—"))
                
                ws.append(row_data)
                
                # Estilo de fila
                for cell in ws[row_idx]:
                    cell.border = border
                    if row_idx % 2 == 0:
                        cell.fill = stripe_fill
                    if cell.column > 1:
                        cell.alignment = center_align

            # Auto-ajustar ancho de columnas
            for column_cells in ws.columns:
                length = max(len(str(cell.value)) for cell in column_cells)
                ws.column_dimensions[column_cells[0].column_letter].width = length + 5

            wb.save(filepath)
            messagebox.showinfo("Éxito", f"Reporte Excel generado correctamente:\n{filepath}")
            self.show_group_dashboard(group_id)
            self.db.log_event("registro", group_name, "Reporte EXCEL exportado", group_id)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el Excel: {e}")

    def show_history(self):
        """Muestra el log global de actividad del ClassRoom Clash."""
        self._clear()
        
        hdr = tk.Frame(self.container, bg=BG_HEADER, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="📊  LOG GLOBAL DE ACTIVIDAD",
                 font=self.f_header, bg=BG_HEADER, fg=TEXT_LIGHT).pack()

        # Botón Home en el header
        home_btn_f = tk.Frame(hdr, bg=BG_HEADER)
        home_btn_f.place(relx=0.03, rely=0.5, anchor="w")
        self._make_btn(home_btn_f, "🏠 Inicio", self.show_main_menu, color="#4361EE", px=10, py=5, font=self.f_small).pack()

        body = tk.Frame(self.container, bg=BG_MAIN, padx=30, pady=20)
        body.pack(fill="both", expand=True)

        logs = self.db.get_global_log(100)

        if not logs:
            tk.Label(body, text="📢 ¡AÚN NO HAY ACTIVIDAD!", 
                     font=self.f_title, bg=BG_MAIN, fg=ACCENT_GOLD).pack(pady=(50, 10))
            tk.Label(body, text="Realiza sorteos, usa la tómbola o crea actividades\npara ver el historial aquí.",
                     font=self.f_body, bg=BG_MAIN, fg=TEXT_MUTED, justify="center").pack()
        else:
            scroll_frame = ScrollableFrame(body, bg_color=BG_MAIN)
            scroll_frame.pack(fill="both", expand=True)
            sf = scroll_frame.view
            
            # Iconos por tipo
            icons = {
                "sorteo": "🎲",
                "puntos": "💰",
                "actividad": "📋",
                "registro": "📂"
            }

            for etype, gname, desc, time, details in logs:
                card = tk.Frame(sf, bg=BG_CARD, highlightbackground="#DEE2E6", 
                                highlightthickness=1, padx=15, pady=8)
                card.pack(fill="x", pady=4)
                
                icon = icons.get(etype, "📝")
                
                top_row = tk.Frame(card, bg=BG_CARD)
                top_row.pack(fill="x")
                
                tk.Label(top_row, text=f"{icon} {desc}", font=self.f_body, 
                         bg=BG_CARD, fg=TEXT_DARK).pack(side="left")
                
                tk.Label(top_row, text=time, font=self.f_small, 
                         bg=BG_CARD, fg=TEXT_MUTED).pack(side="right")
                
                if gname:
                    tk.Label(card, text=f"Grupo: {gname}", font=self.f_small, 
                             bg=BG_CARD, fg="#4361EE").pack(anchor="w", padx=(25, 0))

        tk.Frame(body, height=0, bg=BG_MAIN).pack(pady=10)
        self._make_btn(body, "← Volver al Menú", self.show_main_menu,
                       color="#6C757D", hover="#495057", px=20, py=8,
                       font=self.f_body).pack()

    # =========================================================================
    #  PANTALLA — LEADERBOARD
    # =========================================================================

    def show_leaderboard(self, group_id=None):
        """Muestra el ranking de puntos de los estudiantes."""
        self._clear()

        hdr = tk.Frame(self.container, bg=BG_HEADER, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🏆  Leaderboard",
                 font=self.f_header, bg=BG_HEADER, fg=ACCENT_GOLD).pack()

        # Botón Home en el header
        home_btn_f = tk.Frame(hdr, bg=BG_HEADER)
        home_btn_f.place(relx=0.03, rely=0.5, anchor="w")
        self._make_btn(home_btn_f, "🏠 Inicio", self.show_main_menu, color="#4361EE", px=10, py=5, font=self.f_small).pack()

        body = tk.Frame(self.container, bg=BG_MAIN, padx=30, pady=20)
        body.pack(fill="both", expand=True)

        # Selector de grupo
        filter_frame = tk.Frame(body, bg=BG_MAIN)
        filter_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(filter_frame, text="Filtrar por Grupo:", font=self.f_body, 
                 bg=BG_MAIN, fg=TEXT_DARK).pack(side="left", padx=(0, 10))
        
        groups = self.db.get_groups()
        group_options = ["Todos (Global)"] + [g[1] for g in groups]
        
        current_selection = tk.StringVar()
        
        # Determinar selección inicial
        if group_id:
            data = self.db.load_group(group_id)
            initial = data['name'] if data else group_options[0]
        elif hasattr(self.state, 'current_group_id') and self.state.current_group_id:
            data = self.db.load_group(self.state.current_group_id)
            initial = data['name'] if data else group_options[0]
        else:
            initial = group_options[0]
            
        current_selection.set(initial)
        
        def _on_group_change(val):
            if val == "Todos (Global)":
                self.show_leaderboard(None)
            else:
                # Buscar ID por nombre
                gid = next((g[0] for g in groups if g[1] == val), None)
                self.show_leaderboard(gid)

        om = tk.OptionMenu(filter_frame, current_selection, *group_options, command=_on_group_change)
        om.config(font=self.f_body, bg=BG_CARD, relief="flat", highlightthickness=0)
        om.pack(side="left")

        # Cargar datos según filtro
        if initial == "Todos (Global)":
            leaderboard = self.db.get_leaderboard(50)
            title_suffix = "Global"
        else:
            gid = next((g[0] for g in groups if g[1] == initial), None)
            data = self.db.load_group(gid)
            leaderboard = self.db.get_group_leaderboard(data['students'])
            title_suffix = initial

        if not leaderboard:
            tk.Label(body, text=f"No hay puntos registrados aún para {title_suffix}.",
                     font=self.f_body, bg=BG_MAIN, fg=TEXT_MUTED).pack(pady=20)
        else:
            tk.Label(body, text=f"Top Estudiantes — {title_suffix}",
                     font=self.f_title, bg=BG_MAIN, fg=TEXT_DARK).pack(pady=10)

            scroll_frame = ScrollableFrame(body, bg_color=BG_MAIN)
            scroll_frame.pack(fill="both", expand=True)
            sf = scroll_frame.view

            from tkinter import font as tkfont
            for rank, (name, points, spins) in enumerate(leaderboard, 1):
                card = tk.Frame(sf, bg=BG_CARD,
                                highlightbackground=TEAM_COLORS[rank % len(TEAM_COLORS)],
                                highlightthickness=2, padx=15, pady=10)
                card.pack(fill="x", pady=6)

                info = tk.Frame(card, bg=BG_CARD)
                info.pack(side="left", fill="both", expand=True)
                medals = ["🥇", "🥈", "🥉"]
                medal = medals[rank - 1] if rank <= 3 else f"#{rank}"
                tk.Label(info, text=f"{medal}  {name}",
                         font=self.f_name, bg=BG_CARD, fg=TEXT_DARK).pack(anchor="w")
                tk.Label(info, text=f"Vueltas: {spins}",
                         font=self.f_small, bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w")
                tk.Label(card, text=f"{points} pts",
                         font=tkfont.Font(family="Helvetica", size=16, weight="bold"),
                         bg=BG_CARD, fg=ACCENT_GOLD).pack(side="right")

        tk.Frame(body, height=0, bg=BG_MAIN).pack(pady=10)
        bf = tk.Frame(body, bg=BG_MAIN)
        bf.pack()
        self._make_btn(bf, "Limpiar Leaderboard", self._reset_lb_confirm,
                       color="#EF233C", px=20, py=8, font=self.f_body).pack(side="left", padx=5)
        self._make_btn(bf, "← Volver", self.show_main_menu,
                       color="#6C757D", hover="#495057", px=20, py=8,
                       font=self.f_body).pack(side="left", padx=5)

    def _reset_lb_confirm(self):
        """Confirma el limpiar leaderboard."""
        if messagebox.askyesno("Confirmar", "¿Limpiar todos los puntos?"):
            self.db.reset_leaderboard()
            self.show_leaderboard()

    # =========================================================================
    #  PANTALLA 1 — CONFIGURACIÓN
    # =========================================================================

    def _pick_group_for_sorteo(self):
        """Muestra una lista rápida para elegir qué grupo sortear."""
        self._pick_group_generic(
            title="¿Qué grupo deseas sortear?",
            btn_text="Siguiente →",
            btn_color=BTN_PRIMARY,
            callback=lambda gid: self.show_config_screen(gid)
        )

    def _pick_group_for_wheel(self):
        """Muestra una lista rápida para elegir qué grupo usar en la ruleta."""
        def _on_select(gid):
            data = self.db.load_group(gid)
            if data:
                self.state.students = data['students'][:]
                self.state.current_group_name = data['name']
                self.state.current_group_id = gid
                self.show_wheel_screen()

        self._pick_group_generic(
            title="¿Para qué grupo es la ruleta?",
            btn_text="Abrir Ruleta →",
            btn_color="#F72585",
            callback=_on_select
        )

    def _pick_group_generic(self, title, btn_text, btn_color, callback):
        """Ventana genérica de selección de grupo."""
        groups = self.db.get_groups()
        if not groups:
            if messagebox.askyesno("Sin Grupos", "No tienes grupos guardados. ¿Deseas ir a Gestionar Grupos para crear uno?"):
                self.show_main_menu()
            return

        win = tk.Toplevel(self)
        win.title("Seleccionar Grupo")
        win.geometry("400x550")
        win.configure(bg=BG_MAIN)
        win.transient(self)
        win.grab_set()

        tk.Label(win, text=title, font=self.f_title, bg=BG_MAIN, pady=15).pack()

        lb_frame = tk.Frame(win, bg=BG_CARD)
        lb_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        sb = tk.Scrollbar(lb_frame)
        sb.pack(side="right", fill="y")
        
        lb = tk.Listbox(lb_frame, font=self.f_body, yscrollcommand=sb.set, relief="flat", bd=5)
        lb.pack(fill="both", expand=True)
        sb.config(command=lb.yview)
        
        for gid, gname, date in groups:
            num = len(self.db.load_group(gid)['students'])
            lb.insert("end", f"{gname} ({num} alumnos)")

        def _confirm():
            sel = lb.curselection()
            if not sel: return
            group_id = groups[sel[0]][0]
            win.destroy()
            callback(group_id)

        self._make_btn(win, btn_text, _confirm, color=btn_color).pack(pady=10)
        self._make_btn(win, "Cancelar", win.destroy, color="#6C757D").pack(pady=5)

    def show_config_screen(self, group_id):
        """Pantalla de configuración para un grupo específico."""
        data = self.db.load_group(group_id)
        if not data: return
        
        self._clear()
        self.state.current_group_id = group_id
        self.state.current_group_name = data['name']
        self.state.students = data['students']

        hdr = tk.Frame(self.container, bg=BG_HEADER, pady=18)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"🎲  SORTEO: {data['name']}",
                 font=self.f_header, bg=BG_HEADER, fg=TEXT_LIGHT).pack()

        # Botón Home en el header
        home_btn_f = tk.Frame(hdr, bg=BG_HEADER)
        home_btn_f.place(relx=0.03, rely=0.5, anchor="w")
        self._make_btn(home_btn_f, "🏠 Inicio", self.show_main_menu, color="#4361EE", px=10, py=5, font=self.f_small).pack()

        body = tk.Frame(self.container, bg=BG_MAIN, padx=40, pady=28)
        body.pack(fill="both", expand=True)
        
        # Resumen del grupo
        info_card = tk.Frame(body, bg=BG_CARD, padx=20, pady=20, 
                             highlightbackground="#DEE2E6", highlightthickness=1)
        info_card.pack(fill="x", pady=(0, 30))
        
        tk.Label(info_card, text=f"Integrantes del grupo ({len(self.state.students)}):", 
                 font=self.f_title, bg=BG_CARD, fg=TEXT_DARK).pack(anchor="w")
        
        # Lista de nombres con posibilidad de excluir
        names_wrap = tk.Frame(info_card, bg=BG_CARD)
        names_wrap.pack(fill="both", expand=True, pady=10)

        scroll_frame = ScrollableFrame(names_wrap, bg_color=BG_CARD, height=150)
        scroll_frame.pack(fill="both", expand=True)
        self.scrollable_names = scroll_frame.view

        self.student_vars = {}
        cols = 3
        for i, student in enumerate(sorted(self.state.students)):
            var = tk.BooleanVar(value=True)
            self.student_vars[student] = var
            
            cb = tk.Checkbutton(self.scrollable_names, text=student, variable=var, 
                               font=self.f_small, bg=BG_CARD, activebackground=BG_CARD,
                               fg=TEXT_DARK, selectcolor="white", cursor="hand2",
                               command=self._refresh_present_count)
            cb.grid(row=i // cols, column=i % cols, sticky="w", padx=10, pady=2)
            
            # Soporte para scroll con la rueda del ratón
            cb.bind("<MouseWheel>", lambda e: self.scrollable_names.master.yview_scroll(int(-1*(e.delta/120)), "units"))

        self.lbl_present = tk.Label(info_card, text=f"Alumnos presentes: {len(self.state.students)}", 
                                    font=self.f_small, bg=BG_CARD, fg=BTN_PRIMARY)
        self.lbl_present.pack(anchor="e")

        # Configuración de equipos
        cfg_frame = tk.Frame(body, bg=BG_MAIN)
        cfg_frame.pack()

        tk.Label(cfg_frame, text="¿En cuántos equipos deseas dividir al grupo?", 
                 font=self.f_body, bg=BG_MAIN, fg=TEXT_DARK).pack(pady=(0, 10))

        vcmd = (self.register(lambda s: s.isdigit() or s == ""), "%P")
        e_wrap = tk.Frame(cfg_frame, bg=BG_CARD, highlightbackground=BTN_PRIMARY, highlightthickness=2)
        e_wrap.pack(pady=5)
        
        self.entry_teams = tk.Entry(
            e_wrap, font=self.f_header, bg=BG_CARD, fg=TEXT_DARK,
            relief="flat", bd=8, justify="center", width=5,
            validate="key", validatecommand=vcmd
        )
        self.entry_teams.insert(0, str(data['num_teams']))
        self.entry_teams.pack()

        self.lbl_error = tk.Label(body, text="", font=self.f_small, bg=BG_MAIN, fg="#EF233C")
        self.lbl_error.pack(pady=10)

        # Botones finales
        btn_row = tk.Frame(body, bg=BG_MAIN)
        btn_row.pack(pady=20)
        
        self._make_btn(btn_row, "🚀  ¡INICIAR SORTEO!", self._start_sorteo,
                       color=BTN_PRIMARY, px=40, py=15).pack(side="left", padx=10)
        
        self._make_btn(btn_row, "← Volver", self.show_main_menu,
                       color="#6C757D", px=20, py=15).pack(side="left", padx=10)

    def _refresh_present_count(self):
        """Actualiza el contador de alumnos seleccionados."""
        present = [s for s, var in self.student_vars.items() if var.get()]
        self.lbl_present.config(text=f"Alumnos presentes: {len(present)}")

    # ── Helpers de configuración ──────────────────────────────────────────

    def _refresh_info(self, _=None):
        """Actualiza en tiempo real el resumen de alumnos/equipos."""
        names = self._parse_names()
        try:
            nt = int(self.entry_teams.get())
        except ValueError:
            nt = 0

        if names and nt >= 2:
            lo = len(names) // nt
            hi = math.ceil(len(names) / nt)
            self.lbl_info.config(
                text=f"✅  {len(names)} alumnos → {nt} equipos\n"
                     f"(~{lo}–{hi} integrantes c/u)",
                fg="#06D6A0",
            )
        else:
            self.lbl_info.config(text="Ingresa los alumnos →", fg=TEXT_MUTED)

    def _parse_names(self):
        """Extrae la lista limpia de nombres del widget Text."""
        raw = self.txt_students.get("1.0", "end-1c").strip()
        bad = {
            "Escribe o pega los nombres aquí…",
            "Ejemplo:", "Ana García", "Carlos López", "María Pérez", "…",
        }
        return [line.strip() for line in raw.splitlines()
                if line.strip() and line.strip() not in bad]

    def _start_sorteo(self):
        """Valida y arranca el sorteo usando solo los alumnos seleccionados."""
        # Filtrar alumnos presentes de la lista de checkboxes
        names = [s for s, var in self.student_vars.items() if var.get()]

        try:
            nt = int(self.entry_teams.get())
        except ValueError:
            self.lbl_error.config(text="⚠  Ingresa un número válido de equipos.")
            return

        if not names:
            self.lbl_error.config(text="⚠  No hay alumnos seleccionados para el sorteo.")
            return
        if nt < 2:
            self.lbl_error.config(text="⚠  Deben ser al menos 2 equipos.")
            return
        if nt > len(names):
            self.lbl_error.config(text="⚠  Hay más equipos que alumnos.")
            return
        if nt > 8:
            self.lbl_error.config(text="⚠  El máximo es 8 equipos.")
            return

        self.state.students = names[:]
        random.shuffle(self.state.students)
        self.state.num_teams = nt
        self.state.teams = [[] for _ in range(nt)]
        self.state.student_index = 0
        self.state.assign_index = 0
        self.state.is_animating = False
        # Mantener el ID del grupo actual para el historial
        # self.state.current_group_id ya está configurado en show_config_screen

        self.show_sorteo_screen()

    def _save_group_only(self):
        """Valida y guarda el grupo en la BD sin iniciar el sorteo."""
        names = self._parse_names()
        if not names:
            self.lbl_error.config(text="⚠  La lista de alumnos está vacía.")
            return

        group_name = self.entry_group_name.get() or "Grupo Guardado"
        # Usar un valor por defecto de 2 equipos al guardar por primera vez
        nt = 2
        empty_teams = [[] for _ in range(nt)]
        
        gid = self.db.save_group(group_name, names, nt, empty_teams)
        
        if gid:
            messagebox.showinfo("Éxito", f"Grupo '{group_name}' guardado correctamente.")
            self.show_main_menu()
        else:
            self.lbl_error.config(text="⚠  Error al guardar en la base de datos.")

    def show_create_group_screen(self):
        """Pantalla dedicada solo a la creación y guardado de grupos."""
        self._clear()

        hdr = tk.Frame(self.container, bg=BG_HEADER, pady=18)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🆕  CREAR NUEVO GRUPO",
                 font=self.f_header, bg=BG_HEADER, fg=TEXT_LIGHT).pack()

        body = tk.Frame(self.container, bg=BG_MAIN, padx=40, pady=28)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(1, weight=1)

        self._labeled_section(body, "📋  Nombres de los Alumnos (uno por línea):", 0, 0)

        txt_wrap = tk.Frame(body, bg=BG_CARD, highlightbackground="#CED4DA", highlightthickness=1)
        txt_wrap.grid(row=1, column=0, sticky="nsew", pady=(0, 20))

        sb = tk.Scrollbar(txt_wrap)
        sb.pack(side="right", fill="y")
        self.txt_students = tk.Text(txt_wrap, yscrollcommand=sb.set, font=self.f_body, 
                                   bg=BG_CARD, relief="flat", bd=10)
        self.txt_students.pack(fill="both", expand=True)
        sb.config(command=self.txt_students.yview)

        # Configuración rápida
        form_frame = tk.Frame(body, bg=BG_MAIN)
        form_frame.grid(row=2, column=0, sticky="ew")

        tk.Label(form_frame, text="Nombre del Grupo:", font=self.f_body, bg=BG_MAIN).pack(side="left")
        self.entry_group_name = tk.Entry(form_frame, font=self.f_body, width=30)
        self.entry_group_name.insert(0, "Mi Nuevo Grupo")
        self.entry_group_name.pack(side="left", padx=10)

        self.lbl_error = tk.Label(body, text="", font=self.f_small, bg=BG_MAIN, fg="#EF233C")
        self.lbl_error.grid(row=3, column=0, pady=10)

        btn_row = tk.Frame(body, bg=BG_MAIN)
        btn_row.grid(row=4, column=0)
        
        self._make_btn(btn_row, "💾  GUARDAR GRUPO", self._save_group_only,
                       color="#06D6A0", px=30, py=12).pack(side="left", padx=10)
        
        self._make_btn(btn_row, "← Cancelar", self.show_main_menu,
                       color="#6C757D", px=30, py=12).pack(side="left", padx=10)
