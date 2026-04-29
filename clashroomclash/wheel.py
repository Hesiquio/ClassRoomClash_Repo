# =============================================================================
#  clashroomclash/wheel.py
#  Pantalla de la ruleta de puntos
# =============================================================================

import math
import random
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox

from .constants import (
    BG_MAIN, BG_CARD, BG_HEADER,
    BTN_PRIMARY, BTN_REVEAL, BTN_REVEAL_H,
    TEXT_DARK, TEXT_LIGHT, TEXT_MUTED, ACCENT_GOLD,
    SLOT_TEXT, TEAM_COLORS,
)




class WheelMixin:
    """Mixin con la pantalla y la animación de la ruleta de puntos."""

    def show_wheel_screen(self):
        """
        Muestra la pantalla de la ruleta de selección de alumnos.
        """
        self.state.wheel_mode = "student"

        # Si no hay estudiantes cargados y estamos en modo student, intentar cargar el último grupo
        if not self.state.students and self.state.wheel_mode == "student":
            groups = self.db.get_groups()
            if groups:
                data = self.db.load_group(groups[0][0])
                self.state.students = data['students']
                self.state.current_group_name = data['name']
            else:
                messagebox.showinfo("Sin datos", "Por favor, crea o selecciona un grupo primero.")
                self.show_main_menu()
                return

        self._clear()

        hdr = tk.Frame(self.container, bg=BG_HEADER, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🎡  TÓMBOLA CLASH",
                 font=self.f_header, bg=BG_HEADER, fg=ACCENT_GOLD).pack()

        body = tk.Frame(self.container, bg=BG_MAIN, padx=30, pady=20)
        body.pack(fill="both", expand=True)

        # ── Panel izquierdo: lista de estudiantes ─────────────────────────
        left_panel = tk.Frame(body, bg=BG_MAIN, width=250)
        left_panel.pack(side="left", fill="both", padx=(0, 20))

        tk.Label(left_panel, text="Selecciona un Estudiante:",
                 font=self.f_title, bg=BG_MAIN, fg=TEXT_DARK).pack(pady=10)

        recent_students = set(self.state.students) if self.state.students else set()
        lb_data = self.db.get_leaderboard(100)
        all_students = list(recent_students) + [
            s[0] for s in lb_data if s[0] not in recent_students
        ]

        if not hasattr(self.state, 'excluded_students'):
            self.state.excluded_students = []

        lb_frame = tk.Frame(left_panel, bg=BG_CARD,
                            highlightbackground="#CED4DA", highlightthickness=1)
        lb_frame.pack(fill="both", expand=True, pady=(0, 10))

        scrollbar = tk.Scrollbar(lb_frame)
        scrollbar.pack(side="right", fill="y")

        self.student_listbox = tk.Listbox(
            lb_frame, yscrollcommand=scrollbar.set,
            font=self.f_body, bg=BG_CARD, fg=TEXT_DARK,
            relief="flat", bd=3, activestyle="none",
            selectmode="single", selectforeground=TEXT_LIGHT,
            selectbackground=BTN_PRIMARY,
        )
        self.student_listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.student_listbox.yview)

        for student in all_students[:30]:
            display_name = f"🚫 {student}" if student in self.state.excluded_students else student
            self.student_listbox.insert("end", display_name)
        
        # Pre-seleccionar si ya tenemos un ganador del primer giro
        if hasattr(self.state, 'selected_student') and self.state.selected_student:
            try:
                idx = all_students.index(self.state.selected_student)
                self.student_listbox.select_set(idx)
                self.student_listbox.see(idx)
            except ValueError:
                if all_students: self.student_listbox.select_set(0)
        elif all_students:
            self.student_listbox.select_set(0)

        def _toggle_exclusion():
            sel = self.student_listbox.curselection()
            if not sel: return
            student = all_students[:30][sel[0]]
            if student in self.state.excluded_students:
                self.state.excluded_students.remove(student)
            else:
                self.state.excluded_students.append(student)
            self.show_wheel_screen()

        self._make_btn(left_panel, "🚫 Excluir / Reintegrar", _toggle_exclusion, 
                       color="#6C757D", hover="#495057", px=10, py=8).pack(fill="x", pady=5)

        # ── Panel derecho: tómbola de texto ───────────────────────────────
        right_panel = tk.Frame(body, bg=BG_MAIN)
        right_panel.pack(side="right", fill="both", expand=True)

        tk.Label(right_panel, text="🎯 ¡Selecciona al Estudiante!",
                 font=self.f_title, bg=BG_MAIN, fg=TEXT_DARK).pack(pady=(0, 15))

        # Marco para el "Slot" / Tómbola
        slot_frame = tk.Frame(right_panel, bg="#212529", padx=40, pady=60,
                              highlightbackground=ACCENT_GOLD, highlightthickness=3)
        slot_frame.pack(pady=20, fill="x")

        result_text = "—"
        if hasattr(self.state, 'selected_student') and self.state.selected_student:
            result_text = self.state.selected_student
        
        self.wheel_result_lbl = tk.Label(
            slot_frame, text=result_text,
            font=tkfont.Font(family="Helvetica", size=48, weight="bold"),
            bg="#212529", fg=ACCENT_GOLD,
            wraplength=500
        )
        self.wheel_result_lbl.pack()

        btn_frame = tk.Frame(right_panel, bg=BG_MAIN)
        btn_frame.pack(fill="x", pady=20)

        self.btn_spin_wheel = self._make_btn(
            btn_frame, "🎡   GIRAR PARA ELEGIR ALUMNO",
            self.spin_wheel, color=BTN_REVEAL, hover=BTN_REVEAL_H,
            px=40, py=14, font=self.f_btn,
        )
        self.btn_spin_wheel.pack(fill="x")

        # ── Top rápido (Específico del grupo si hay uno cargado) ──────────
        tk.Label(body, text=f"🏆 Ranking: {getattr(self.state, 'current_group_name', 'Global')}",
                 font=self.f_name, bg=BG_MAIN, fg=TEXT_DARK).pack(pady=(20, 10))

        if self.state.students:
            lb_quick = self.db.get_group_leaderboard(self.state.students)[:10]
        else:
            lb_quick = self.db.get_leaderboard(10)
        if lb_quick:
            medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
            grid_lb = tk.Frame(body, bg=BG_MAIN)
            grid_lb.pack()
            
            for rank, (name, points, _) in enumerate(lb_quick, 1):
                row = (rank-1) // 5
                col = (rank-1) % 5
                medal = medals[rank-1] if rank <= 10 else f"#{rank}"
                tk.Label(grid_lb,
                         text=f"{medal} {name}\n{points} pts",
                         font=self.f_small, bg=BG_CARD, fg=TEXT_DARK,
                         padx=10, pady=5, width=15, relief="flat",
                         highlightbackground="#DEE2E6", highlightthickness=1
                         ).grid(row=row, column=col, padx=4, pady=4)

        tk.Frame(body, height=0, bg=BG_MAIN).pack(pady=10)
        footer_btns = tk.Frame(body, bg=BG_MAIN)
        footer_btns.pack()

        self._make_btn(footer_btns, "🔄 Cambiar Grupo",
                       self._pick_group_for_wheel,
                       color="#4361EE", px=20, py=8,
                       font=self.f_body).pack(side="left", padx=5)

        back_cmd = lambda: self.show_group_dashboard(self.state.current_group_id) if getattr(self.state, 'current_group_id', None) else self.show_main_menu
        self._make_btn(footer_btns, "← Volver",
                       back_cmd,
                       color="#6C757D", hover="#495057", px=20, py=8,
                       font=self.f_body).pack(side="left", padx=5)

    def _show_wheel_from_sorteo(self):
        """Navega a la ruleta desde la pantalla de fin de sorteo."""
        self.show_wheel_screen()

    # =========================================================================
    #  DIBUJO Y ANIMACIÓN
    # =========================================================================

    def _draw_wheel(self):
        """No se usa en este modo de tómbola de texto."""
        pass

    def spin_wheel(self):
        """Gira la tómbola para elegir un alumno."""
        if not hasattr(self.state, 'excluded_students'):
            self.state.excluded_students = []

        available_students = [s for s in self.state.students if s not in self.state.excluded_students]
        if not available_students:
            messagebox.showwarning("Error", "No hay estudiantes disponibles (todos excluidos o grupo vacío).")
            return
        
        # Preparar datos de tómbola
        self.wheel_sections_data = available_students[:]
        
        self.btn_spin_wheel.config(state="disabled", bg="#ADB5BD")
        winner = random.choice(available_students)
        self._animate_wheel_spin(winner, 30)

    def _show_point_assignment_dialog(self, student):
        """Muestra un cuadro flotante para asignar puntos manualmente."""
        win = tk.Toplevel(self)
        win.title(f"Puntos para {student}")
        win.geometry("380x580")
        win.configure(bg=BG_CARD)
        win.transient(self)
        win.grab_set()
        
        # Centrar en pantalla
        win.update_idletasks()
        w, h = 380, 580
        x = self.winfo_x() + (self.winfo_width() // 2) - (w // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (h // 2)
        win.geometry(f"+{x}+{y}")

        tk.Label(win, text="⭐ ASIGNAR PUNTOS", font=self.f_header, bg=BG_CARD, fg=ACCENT_GOLD).pack(pady=20)
        tk.Label(win, text=student, font=self.f_title, bg=BG_CARD, fg=TEXT_DARK).pack()
        
        # Cuadro de texto para puntos
        entry_frame = tk.Frame(win, bg=BG_CARD, pady=20)
        entry_frame.pack()
        
        points_var = tk.StringVar(value="1")
        entry = tk.Entry(entry_frame, textvariable=points_var, font=self.f_header, width=5, justify="center",
                         relief="flat", highlightthickness=2, highlightbackground=BTN_PRIMARY)
        entry.pack(side="left", padx=10)
        entry.focus_set()
        entry.selection_range(0, "end")

        # Botones rápidos
        quick_frame = tk.Frame(win, bg=BG_CARD, pady=10)
        quick_frame.pack()

        options = [("+1", 1), ("-1", -1), ("+2", 2), ("-2", -2), ("+5", 5), ("-5", -5)]
        for i, (text, val) in enumerate(options):
            btn = tk.Button(quick_frame, text=text, font=self.f_body, width=5, bg=BG_MAIN,
                            command=lambda v=val: points_var.set(str(int(points_var.get() or 0) + v)))
            btn.grid(row=i//2, column=i%2, padx=5, pady=5)

        def _set_zero():
            points_var.set("0")

        self._make_btn(quick_frame, "0 Pts (Participó)", _set_zero, 
                       color="#FCA311", hover="#E8920C", px=20, py=6, font=self.f_body).grid(row=3, column=0, columnspan=2, pady=(15, 5))

        def _exclude_and_close():
            if not hasattr(self.state, 'excluded_students'):
                self.state.excluded_students = []
            if student not in self.state.excluded_students:
                self.state.excluded_students.append(student)
            win.destroy()
            self.show_wheel_screen()
            self.wheel_result_lbl.config(text=f"{student} Excluido", fg="#FF4D4D")

        self._make_btn(quick_frame, "🚫 Excluir de Ruleta", _exclude_and_close, 
                       color="#EF233C", hover="#D90429", px=20, py=6, font=self.f_small).grid(row=4, column=0, columnspan=2, pady=(5, 10))

        def _confirm(event=None):
            try:
                pts = int(points_var.get())
                self.db.add_points(student, pts, 
                                   group_id=getattr(self.state, 'current_group_id', None),
                                   group_name=getattr(self.state, 'current_group_name', None))
                win.destroy()
                self.show_wheel_screen()
                # Pequeño aviso visual
                msg = f"{student}: {'+' if pts > 0 else ''}{pts} pts"
                self.wheel_result_lbl.config(text=msg, fg="#00FF00" if pts >= 0 else "#FF4D4D")
            except ValueError:
                messagebox.showerror("Error", "Ingresa un número válido.")

        win.bind("<Return>", _confirm)
        
        bottom_frame = tk.Frame(win, bg=BG_CARD)
        bottom_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        self._make_btn(bottom_frame, "Confirmar Puntos", _confirm, 
                       color=BTN_PRIMARY, px=30, py=12).pack(pady=10)

    def _animate_wheel_spin(self, final_result, frame):
        """Anima el cambio de nombres tipo tómbola."""
        if frame > 0:
            random_val = random.choice(self.wheel_sections_data)
            self.wheel_result_lbl.config(text=str(random_val), fg=ACCENT_GOLD)
            delay = int(20 + (30 - frame) ** 1.5)
            self.after(delay, self._animate_wheel_spin, final_result, frame - 1)
        else:
            self.wheel_result_lbl.config(text=str(final_result), fg="#00FF00")
            self.after(1000, lambda: self._show_point_assignment_dialog(final_result))
