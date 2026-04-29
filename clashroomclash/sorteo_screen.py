# =============================================================================
#  clashroomclash/sorteo_screen.py
#  Pantalla de sorteo con animación tipo tómbola (round-robin)
# =============================================================================

import math
import random
import tkinter as tk

from .constants import (
    BG_MAIN, BG_CARD, BG_HEADER,
    BTN_PRIMARY, BTN_REVEAL, BTN_REVEAL_H,
    TEXT_LIGHT, TEXT_MUTED, ACCENT_GOLD,
    SLOT_BG, SLOT_TEXT,
    TEAM_COLORS, TEAM_EMOJIS,
)


class SorteoScreenMixin:
    """
    Mixin con la pantalla de sorteo y toda la lógica de animación.

    Flujo de animación (sin bloquear el event-loop de Tkinter):
        reveal_next()
          └─ _run_slot_anim()   ← frames de tómbola
               └─ _show_climax()
                     └─ _blink()
                           └─ _assign_to_team()
                                 └─ _finish()  (cuando todos asignados)
    """

    # =========================================================================
    #  PANTALLA 2 — SORTEO CON ANIMACIÓN
    # =========================================================================

    def show_sorteo_screen(self):
        """Construye la pantalla principal del sorteo."""
        self._clear()

        # ── Header ───────────────────────────────────────────────────────
        hdr = tk.Frame(self.container, bg=BG_HEADER, pady=12)
        hdr.pack(fill="x")
        inner = tk.Frame(hdr, bg=BG_HEADER)
        inner.pack()
        tk.Label(inner, text="🎰  ¡EL SORTEO HA COMENZADO!",
                 font=self.f_header, bg=BG_HEADER, fg=ACCENT_GOLD).pack(side="left", padx=10)
        self.lbl_progress = tk.Label(
            inner, text=f"0 / {len(self.state.students)} asignados",
            font=self.f_body, bg=BG_HEADER, fg=TEXT_MUTED,
        )
        self.lbl_progress.pack(side="left", padx=24)

        # ── Zona de la "tómbola" ──────────────────────────────────────────
        slot_zone = tk.Frame(self.container, bg=SLOT_BG, pady=18)
        slot_zone.pack(fill="x")

        self.slot_lbl = tk.Label(
            slot_zone, text="¿ Quién será el siguiente ?",
            font=self.f_slot, bg=SLOT_BG, fg=SLOT_TEXT, pady=8,
        )
        self.slot_lbl.pack()

        self.slot_sub = tk.Label(
            slot_zone, text="Presiona el botón para revelar",
            font=self.f_body, bg=SLOT_BG, fg=TEXT_MUTED,
        )
        self.slot_sub.pack()

        # ── Botón revelar ─────────────────────────────────────────────────
        btn_zone = tk.Frame(self.container, bg=BG_MAIN, pady=12)
        btn_zone.pack(fill="x")

        self.auto_sorteo_active = False

        self.btn_reveal = self._make_btn(
            btn_zone, "🔮   Revelar (Manual)",
            self.reveal_next, color=BTN_REVEAL, hover=BTN_REVEAL_H, px=20, py=14,
        )
        self.btn_reveal.pack(side="left", expand=True, padx=(10, 5))

        self.btn_auto = self._make_btn(
            btn_zone, "⚡   Auto-Sorteo",
            self.toggle_auto_sorteo, color="#FF9F1C", px=20, py=14,
        )
        self.btn_auto.pack(side="left", expand=True, padx=(5, 5))

        back_cmd = lambda: self.show_group_dashboard(self.state.current_group_id) if getattr(self.state, 'current_group_id', None) else self.show_main_menu
        self.btn_cancel_sorteo = self._make_btn(
            btn_zone, "🏠   Abandonar Sorteo",
            back_cmd, color="#6C757D", hover="#495057", px=20, py=14,
        )
        self.btn_cancel_sorteo.pack(side="left", expand=True, padx=(5, 10))

        # ── Grid de tarjetas de equipo ────────────────────────────────────
        grid_frame = tk.Frame(self.container, bg=BG_MAIN)
        grid_frame.pack(fill="both", expand=True, padx=18, pady=8)

        cols = min(self.state.num_teams, 4)
        rows_needed = math.ceil(self.state.num_teams / cols)
        for c in range(cols):
            grid_frame.columnconfigure(c, weight=1)
        for r in range(rows_needed):
            grid_frame.rowconfigure(r, weight=1)

        self.team_cards = []
        self.team_name_frames = []

        for i in range(self.state.num_teams):
            row = i // cols
            col = i % cols
            color = TEAM_COLORS[i % len(TEAM_COLORS)]
            emoji = TEAM_EMOJIS[i % len(TEAM_EMOJIS)]

            card = tk.Frame(grid_frame, bg=BG_CARD,
                            highlightbackground=color, highlightthickness=2,
                            padx=8, pady=6)
            card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

            team_hdr = tk.Frame(card, bg=color, pady=5)
            team_hdr.pack(fill="x")
            tk.Label(team_hdr, text=f"{emoji}  Equipo {i + 1}",
                     font=self.f_name, bg=color, fg=TEXT_LIGHT).pack()

            nf = tk.Frame(card, bg=BG_CARD, pady=4)
            nf.pack(fill="both", expand=True)
            tk.Label(nf, text="— vacío —",
                     font=self.f_small, bg=BG_CARD, fg=TEXT_MUTED).pack(pady=6)

            self.team_cards.append(card)
            self.team_name_frames.append(nf)

        # El botón "Nuevo Sorteo" se empaqueta solo al terminar
        self.btn_restart = self._make_btn(
            self.container, "🔄   Nuevo Sorteo",
            self.show_config_screen,
            color="#6C757D", hover="#495057",
            px=20, py=8, font=self.f_body,
        )

    # =========================================================================
    #  LÓGICA DE ANIMACIÓN
    # =========================================================================

    def toggle_auto_sorteo(self):
        """Alterna el modo de sorteo automático."""
        if self.auto_sorteo_active:
            self.auto_sorteo_active = False
            self.btn_auto.config(text="⚡   Auto-Sorteo", bg="#FF9F1C")
        else:
            self.auto_sorteo_active = True
            self.btn_auto.config(text="🛑   Detener Auto", bg="#EF233C")
            if not self.state.is_animating:
                self.reveal_next()

    def reveal_next(self):
        """Punto de entrada: deshabilita el botón e inicia la animación."""
        if self.state.is_animating or self.state.student_index >= len(self.state.students):
            return

        self.state.is_animating = True
        self.btn_reveal.config(state="disabled", bg="#ADB5BD")
        
        if getattr(self, 'auto_sorteo_active', False):
            # Animación más rápida para el modo automático
            self._run_slot_anim(frame=0, total=15, init_delay=20)
        else:
            self._run_slot_anim(frame=0, total=34, init_delay=42)

    def _run_slot_anim(self, frame, total, init_delay):
        """
        Bucle principal de la tómbola.
        La curva de frenado sube el retardo de 1× a ~4.5× en curva cuadrática.
        """
        if frame >= total:
            chosen = self.state.students[self.state.student_index]
            self._show_climax(chosen)
            return

        self.slot_lbl.config(text=random.choice(self.state.students), fg=SLOT_TEXT)

        progress = frame / total
        next_delay = int(init_delay * (1 + progress ** 1.6 * 4.5))
        next_delay = min(next_delay, 320)

        self.after(next_delay, self._run_slot_anim, frame + 1, total, init_delay)

    def _show_climax(self, name):
        """Muestra el nombre real en dorado e inicia el parpadeo de clímax."""
        self.slot_lbl.config(text=name, fg=ACCENT_GOLD)
        self.slot_sub.config(
            text=f"➤  ¡Se une al  Equipo {self.state.assign_index + 1}!",
            fg=ACCENT_GOLD,
        )
        self._blink(name, half_cycles=6, is_visible=False)

    def _blink(self, name, half_cycles, is_visible):
        """Efecto de parpadeo: alterna dorado ↔ invisible cada 160 ms."""
        if half_cycles <= 0:
            self.slot_lbl.config(text=name, fg=ACCENT_GOLD)
            self.after(350, self._assign_to_team, name)
            return

        color = ACCENT_GOLD if is_visible else SLOT_BG
        self.slot_lbl.config(fg=color)
        self.after(160, self._blink, name, half_cycles - 1, not is_visible)

    def _assign_to_team(self, name):
        """Asigna el alumno al equipo actual (round-robin) y actualiza la tarjeta."""
        idx = self.state.assign_index
        team_color = TEAM_COLORS[idx % len(TEAM_COLORS)]

        self.state.teams[idx].append(name)

        nf = self.team_name_frames[idx]
        if len(self.state.teams[idx]) == 1:
            for w in nf.winfo_children():
                w.destroy()

        tk.Label(
            nf, text=f"  ✦  {name}",
            font=self.f_body, bg=BG_CARD, fg=team_color, anchor="w",
        ).pack(fill="x", padx=6, pady=2)

        # Flash dorado en el borde por 600 ms
        self.team_cards[idx].config(highlightbackground=ACCENT_GOLD,
                                    highlightthickness=3)
        self.after(600, lambda: self.team_cards[idx].config(
            highlightbackground=team_color, highlightthickness=2,
        ))

        self.state.student_index += 1
        self.state.assign_index = (self.state.assign_index + 1) % self.state.num_teams

        self.lbl_progress.config(
            text=f"{self.state.student_index} / {len(self.state.students)} asignados",
        )

        if self.state.student_index >= len(self.state.students):
            self.auto_sorteo_active = False
            self._finish()
        else:
            self.slot_lbl.config(text="¿ Quién será el siguiente ?", fg=SLOT_TEXT)
            self.slot_sub.config(text="Presiona el botón o espera al automático", fg=TEXT_MUTED)
            self.state.is_animating = False
            self.btn_reveal.config(state="normal", bg=BTN_REVEAL)
            
            if getattr(self, 'auto_sorteo_active', False):
                self.after(1000, self.reveal_next)

    def _finish(self):
        """Pantalla final cuando todos los alumnos han sido asignados."""
        self.state.is_animating = False
        self.slot_lbl.config(text="🏆  ¡SORTEO COMPLETADO!  🏆", fg=ACCENT_GOLD)
        self.slot_sub.config(text="¡Que gane el mejor equipo! 🎉", fg=ACCENT_GOLD)
        self.btn_reveal.config(state="disabled", text="✅   ¡Todos asignados!", bg="#06D6A0")
        if hasattr(self, 'btn_auto') and self.btn_auto.winfo_exists():
            self.btn_auto.config(state="disabled", bg="#6C757D")

        group_name = getattr(self.state, 'current_group_name', 'Sorteo')
        self.db.save_draw_history(group_name, self.state.teams, group_id=self.state.current_group_id)

        if not self.state.current_group_id:
            self.state.current_group_id = self.db.save_group(
                group_name, self.state.students, self.state.num_teams, self.state.teams,
            )

        btn_frame = tk.Frame(self.container, bg=BG_MAIN, pady=12)
        btn_frame.pack(fill="x")

        self._make_btn(btn_frame, "🎡   Ruleta de Puntos",
                       self._show_wheel_from_sorteo,
                       color=BTN_REVEAL, hover=BTN_REVEAL_H,
                       px=30, py=12, font=self.f_btn).pack(side="left", padx=5)

        self._make_btn(btn_frame, "🔄   Nuevo Sorteo",
                       self.show_config_screen,
                       color=BTN_PRIMARY, px=30, py=12, font=self.f_btn).pack(side="left", padx=5)

        back_cmd = lambda: self.show_group_dashboard(self.state.current_group_id) if getattr(self.state, 'current_group_id', None) else self.show_main_menu

        self._make_btn(btn_frame, "🏠   Panel del Grupo",
                       back_cmd,
                       color="#6C757D", hover="#495057",
                       px=30, py=12, font=self.f_btn).pack(side="left", padx=5)
