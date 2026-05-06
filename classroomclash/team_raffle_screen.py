# =============================================================================
#  classroomclash/team_raffle_screen.py
#  Tómbola de Equipos — Define el orden de participación de equipos al azar
# =============================================================================

import random
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox

from .constants import (
    BG_MAIN, BG_CARD, BG_HEADER,
    BTN_PRIMARY, BTN_HOVER, BTN_REVEAL, BTN_REVEAL_H,
    TEXT_DARK, TEXT_LIGHT, TEXT_MUTED, ACCENT_GOLD,
    SLOT_TEXT, TEAM_COLORS, TEAM_EMOJIS,
)


class TeamRaffleMixin:
    """
    Mixin con la pantalla de Tómbola de Equipos.
    Permite ingresar nombres de equipos manualmente y sortear el orden
    de participación de forma aleatoria, usando la misma animación
    tipo slot-machine de la tómbola de alumnos.
    """

    # =========================================================================
    #  PANTALLA PRINCIPAL
    # =========================================================================

    def show_team_raffle_screen(self):
        """Muestra la pantalla de la Tómbola de Equipos."""
        self._clear()

        # Inicializar estado específico de esta tómbola si no existe
        if not hasattr(self, '_tr_team_names'):
            self._tr_team_names = []
        if not hasattr(self, '_tr_order_result'):
            self._tr_order_result = []
        if not hasattr(self, '_tr_spinning'):
            self._tr_spinning = False

        # ── Header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(self.container, bg=BG_HEADER, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🎰  TÓMBOLA DE EQUIPOS",
                 font=self.f_header, bg=BG_HEADER, fg=ACCENT_GOLD).pack()
        tk.Label(hdr, text="Define el orden de participación al azar",
                 font=self.f_small, bg=BG_HEADER, fg=TEXT_MUTED).pack(pady=(2, 0))

        home_btn_f = tk.Frame(hdr, bg=BG_HEADER)
        home_btn_f.place(relx=0.03, rely=0.5, anchor="w")
        self._make_btn(home_btn_f, "🏠 Inicio", self.show_main_menu,
                       color="#4361EE", px=10, py=5, font=self.f_small).pack()

        help_msg = (
            "Tómbola de Equipos — Orden de Participación.\n\n"
            "Esta herramienta te permite sortear el orden en que los equipos "
            "participarán en clase, de forma completamente independiente a la "
            "tómbola de alumnos.\n\n"
            "¿Cómo usarla?\n"
            "1. Escribe los nombres de tus equipos en el cuadro de texto del "
            "panel izquierdo, UN equipo por línea.\n"
            "2. Puedes cargar los equipos del último sorteo automáticamente "
            "con el botón 'Cargar del Último Sorteo'.\n"
            "3. Presiona '🎰 GIRAR TÓMBOLA' para animar el sorteo completo.\n"
            "4. El resultado muestra el orden de participación (1°, 2°, 3°...).\n"
            "5. Presiona '🔄 Nuevo Sorteo' para volver a girar con los mismos equipos.\n\n"
            "¡El botón 'Girar de uno en uno' permite revelar el orden "
            "de forma dramática, equipo por equipo!"
        )
        help_btn_f = tk.Frame(hdr, bg=BG_HEADER)
        help_btn_f.place(relx=0.97, rely=0.5, anchor="e")
        self._make_btn(help_btn_f, "❓ Ayuda",
                       lambda: self._show_help_dialog("Tómbola de Equipos", help_msg),
                       color="#4361EE", px=10, py=5, font=self.f_small).pack()

        # ── Body layout ───────────────────────────────────────────────────────
        body = tk.Frame(self.container, bg=BG_MAIN, padx=20, pady=15)
        body.pack(fill="both", expand=True)

        # Dividir en panel izquierdo (entrada) y panel derecho (resultado)
        pane_left = tk.Frame(body, bg=BG_MAIN, width=300)
        pane_left.pack(side="left", fill="both", padx=(0, 15))
        pane_left.pack_propagate(False)

        pane_right = tk.Frame(body, bg=BG_MAIN)
        pane_right.pack(side="right", fill="both", expand=True)

        self._build_team_input_panel(pane_left)
        self._build_team_result_panel(pane_right)

    # =========================================================================
    #  PANEL IZQUIERDO — ENTRADA DE EQUIPOS
    # =========================================================================

    def _build_team_input_panel(self, parent):
        """Construye el panel de entrada de equipos con cuadro de texto multilinea."""
        # ── Título + hint ─────────────────────────────────────────────────────
        tk.Label(parent, text="🏷️ Equipos a Sortear:",
                 font=self.f_title, bg=BG_MAIN, fg=TEXT_DARK).pack(anchor="w", pady=(0, 2))
        tk.Label(parent, text="Escribe un nombre por línea",
                 font=self.f_small, bg=BG_MAIN, fg=TEXT_MUTED).pack(anchor="w", pady=(0, 6))

        # ── Cuadro de texto multilinea ────────────────────────────────────────
        txt_frame = tk.Frame(parent, bg=BG_CARD,
                             highlightbackground=BTN_PRIMARY, highlightthickness=2)
        txt_frame.pack(fill="both", expand=True, pady=(0, 6))

        sb = tk.Scrollbar(txt_frame)
        sb.pack(side="right", fill="y")

        self._tr_textbox = tk.Text(
            txt_frame,
            yscrollcommand=sb.set,
            font=self.f_body,
            bg=BG_CARD, fg=TEXT_DARK,
            relief="flat", bd=8,
            insertbackground=BTN_PRIMARY,   # cursor de texto
            selectbackground=BTN_PRIMARY,
            selectforeground=TEXT_LIGHT,
            wrap="word",
            undo=True,
        )
        self._tr_textbox.pack(fill="both", expand=True)
        sb.config(command=self._tr_textbox.yview)

        # Poblar con los nombres actuales
        if self._tr_team_names:
            self._tr_textbox.insert("1.0", "\n".join(self._tr_team_names))

        # Contador dinámico que se actualiza al escribir
        self._tr_count_lbl = tk.Label(
            parent, text=self._tr_count_text(),
            font=self.f_small, bg=BG_MAIN, fg=TEXT_MUTED
        )
        self._tr_count_lbl.pack(anchor="e", pady=(0, 4))

        def _on_text_change(event=None):
            """Actualiza el contador en tiempo real al escribir."""
            names = self._tr_get_names_from_textbox()
            count = len(names)
            color = "#06D6A0" if count >= 2 else "#EF233C"
            self._tr_count_lbl.config(
                text=f"Total: {count} equipo(s)",
                fg=color
            )

        self._tr_textbox.bind("<KeyRelease>", _on_text_change)
        _on_text_change()  # Inicializar contador

        # ── Botón limpiar ─────────────────────────────────────────────────────
        self._make_btn(parent, "🧹 Limpiar Todo",
                       self._tr_clear_teams,
                       color="#6C757D", hover="#495057",
                       px=8, py=6, font=self.f_small).pack(fill="x", pady=(0, 4))

        # Separador
        tk.Frame(parent, height=1, bg="#DEE2E6").pack(fill="x", pady=6)

        # ── Carga rápida desde sorteo ─────────────────────────────────────────
        tk.Label(parent, text="⚡ Carga Rápida:",
                 font=self.f_small, bg=BG_MAIN, fg=TEXT_MUTED).pack(anchor="w")

        self._make_btn(parent, "📥 Cargar del Último Sorteo",
                       self._tr_load_from_last_sorteo,
                       color="#4361EE", hover=BTN_HOVER,
                       px=8, py=8, font=self.f_small).pack(fill="x", pady=4)

    # =========================================================================
    #  PANEL DERECHO — ANIMACIÓN Y RESULTADO
    # =========================================================================

    def _build_team_result_panel(self, parent):
        """Construye el panel de animación y resultado del sorteo."""

        tk.Label(parent, text="🎯 Orden de Participación:",
                 font=self.f_title, bg=BG_MAIN, fg=TEXT_DARK).pack(pady=(0, 10))

        # ── Slot principal (equipo animado) ───────────────────────────────────
        slot_outer = tk.Frame(parent, bg="#212529",
                              highlightbackground=ACCENT_GOLD, highlightthickness=3)
        slot_outer.pack(fill="x", pady=(0, 15))

        slot_inner = tk.Frame(slot_outer, bg="#212529", pady=35, padx=20)
        slot_inner.pack(fill="x")

        self._tr_slot_lbl = tk.Label(
            slot_inner,
            text="—",
            font=tkfont.Font(family="Helvetica", size=44, weight="bold"),
            bg="#212529", fg=ACCENT_GOLD,
            wraplength=480,
        )
        self._tr_slot_lbl.pack()

        self._tr_sub_lbl = tk.Label(
            slot_inner,
            text="Presiona GIRAR para empezar",
            font=self.f_small,
            bg="#212529", fg=TEXT_MUTED,
        )
        self._tr_sub_lbl.pack(pady=(6, 0))

        # ── Botones de acción ─────────────────────────────────────────────────
        action_frame = tk.Frame(parent, bg=BG_MAIN)
        action_frame.pack(fill="x", pady=(0, 15))

        self._tr_btn_spin = self._make_btn(
            action_frame,
            "🎰   GIRAR TÓMBOLA  (Orden Completo)",
            self._tr_spin_all,
            color=BTN_REVEAL, hover=BTN_REVEAL_H,
            px=30, py=14, font=self.f_btn,
        )
        self._tr_btn_spin.pack(fill="x", pady=(0, 6))

        self._tr_btn_one = self._make_btn(
            action_frame,
            "🎲  Revelar de Uno en Uno",
            self._tr_spin_one,
            color="#7B2FBE", hover="#6A1FA3",
            px=20, py=10, font=self.f_body,
        )
        self._tr_btn_one.pack(fill="x", pady=(0, 6))

        self._tr_btn_reset = self._make_btn(
            action_frame,
            "🔄 Nuevo Sorteo (mismos equipos)",
            self._tr_reset,
            color="#6C757D", hover="#495057",
            px=20, py=8, font=self.f_body,
        )
        self._tr_btn_reset.pack(fill="x")

        # ── Panel de resultado (orden final) ──────────────────────────────────
        result_lbl = tk.Label(parent, text="📋 Resultado:",
                              font=self.f_name, bg=BG_MAIN, fg=TEXT_DARK)
        result_lbl.pack(anchor="w", pady=(10, 4))

        result_container = tk.Frame(parent, bg=BG_CARD,
                                    highlightbackground="#DEE2E6",
                                    highlightthickness=1)
        result_container.pack(fill="both", expand=True)

        self._tr_result_frame = tk.Frame(result_container, bg=BG_CARD, padx=10, pady=10)
        self._tr_result_frame.pack(fill="both", expand=True)

        # Mostrar resultado previo si ya había uno
        if self._tr_order_result:
            self._tr_draw_result(self._tr_order_result)
        else:
            tk.Label(self._tr_result_frame,
                     text="El orden de participación aparecerá aquí.",
                     font=self.f_small, bg=BG_CARD, fg=TEXT_MUTED,
                     wraplength=350).pack(pady=20)

    # =========================================================================
    #  GESTIÓN DE EQUIPOS
    # =========================================================================

    def _tr_count_text(self):
        count = len(self._tr_team_names)
        return f"Total: {count} equipo(s)"

    def _tr_get_names_from_textbox(self):
        """Lee el cuadro de texto y devuelve la lista limpia de nombres."""
        raw = self._tr_textbox.get("1.0", "end-1c")
        return [line.strip() for line in raw.splitlines() if line.strip()]

    def _tr_sync_from_textbox(self):
        """Sincroniza self._tr_team_names desde el cuadro de texto."""
        self._tr_team_names = self._tr_get_names_from_textbox()

    def _tr_clear_teams(self):
        """Limpia el cuadro de texto y el estado."""
        try:
            content = self._tr_textbox.get("1.0", "end-1c").strip()
        except tk.TclError:
            content = ""
        if content and messagebox.askyesno("Confirmar", "¿Limpiar todos los equipos?"):
            self._tr_textbox.delete("1.0", "end")
            self._tr_team_names = []
            self._tr_order_result = []
            # Actualizar contador
            self._tr_count_lbl.config(text="Total: 0 equipo(s)", fg="#EF233C")

    def _tr_load_from_last_sorteo(self):
        """Intenta cargar los nombres de equipos del último sorteo realizado."""
        # Buscar en el estado si hay equipos recientes del SorteoMixin
        teams = getattr(self.state, 'teams', [])
        team_names_from_sorteo = []

        if teams:
            for i, team in enumerate(teams):
                if team:  # Solo equipos con integrantes
                    emoji = TEAM_EMOJIS[i % len(TEAM_EMOJIS)]
                    team_names_from_sorteo.append(f"{emoji} Equipo {i + 1}")

        if not team_names_from_sorteo:
            # Intentar cargar desde la base de datos (log de sorteos)
            groups = self.db.get_groups()
            if groups:
                # Construir nombres genéricos de equipos basados en el último grupo
                data = self.db.load_group(groups[0][0])
                if data and data.get('num_teams'):
                    for i in range(data['num_teams']):
                        emoji = TEAM_EMOJIS[i % len(TEAM_EMOJIS)]
                        team_names_from_sorteo.append(f"{emoji} Equipo {i + 1}")

        if not team_names_from_sorteo:
            messagebox.showinfo(
                "Sin datos",
                "No se encontraron equipos de un sorteo reciente.\n"
                "Realiza un sorteo primero, o agrega los equipos manualmente."
            )
            return

        if messagebox.askyesno(
            "Cargar Equipos",
            f"Se encontraron {len(team_names_from_sorteo)} equipo(s).\n"
            "¿Deseas reemplazar el contenido actual con estos equipos?\n\n"
            + "\n".join(team_names_from_sorteo)
        ):
            self._tr_team_names = team_names_from_sorteo
            self._tr_order_result = []
            # Escribir en el textbox directamente si ya está en pantalla
            try:
                self._tr_textbox.delete("1.0", "end")
                self._tr_textbox.insert("1.0", "\n".join(team_names_from_sorteo))
            except (tk.TclError, AttributeError):
                pass
            # Refrescar pantalla para asegurar consistencia
            self.show_team_raffle_screen()

    # =========================================================================
    #  LÓGICA DE SORTEO Y ANIMACIÓN
    # =========================================================================

    def _tr_validate_teams(self):
        """Lee el textbox, valida que haya al menos 2 equipos y retorna la lista."""
        self._tr_sync_from_textbox()
        names = self._tr_team_names
        if len(names) < 2:
            messagebox.showwarning(
                "Pocos Equipos",
                "Necesitas al menos 2 equipos para realizar el sorteo.\n"
                "Escribe uno por línea en el cuadro de texto."
            )
            return None
        return names

    def _tr_spin_all(self):
        """Sortea el orden completo de todos los equipos con animación."""
        if self._tr_spinning:
            return
        names = self._tr_validate_teams()
        if not names:
            return

        # Generar orden shuffled
        shuffled = names[:]
        random.shuffle(shuffled)
        self._tr_order_result = shuffled
        self._tr_remaining_reveal = []  # Reset reveal-one mode

        # Deshabilitar botones durante animación
        self._tr_set_buttons_state("disabled")
        self._tr_spinning = True

        # Limpiar resultado anterior
        for w in self._tr_result_frame.winfo_children():
            w.destroy()

        # Animación: mostrar todos los nombres mezclados rápidamente
        self._tr_animate_spin(shuffled, names, frame=28)

    def _tr_spin_one(self):
        """Revela el orden de un equipo por vez de forma dramática."""
        if self._tr_spinning:
            return

        # Si no hay resultado generado todavía, generar uno nuevo
        if not self._tr_order_result:
            names = self._tr_validate_teams()
            if not names:
                return
            shuffled = names[:]
            random.shuffle(shuffled)
            self._tr_order_result = shuffled

            # Limpiar resultado
            for w in self._tr_result_frame.winfo_children():
                w.destroy()
            self._tr_remaining_reveal = shuffled[:]
        else:
            # Continuar revelando si quedan equipos
            if not hasattr(self, '_tr_remaining_reveal') or not self._tr_remaining_reveal:
                messagebox.showinfo(
                    "Sorteo Completo",
                    "Ya se revelaron todos los equipos.\n"
                    "Presiona '🔄 Nuevo Sorteo' para empezar de nuevo."
                )
                return

        if not self._tr_remaining_reveal:
            return

        next_team = self._tr_remaining_reveal.pop(0)
        position = len(self._tr_order_result) - len(self._tr_remaining_reveal)
        all_names = self._tr_team_names[:] or [next_team]

        self._tr_set_buttons_state("disabled")
        self._tr_spinning = True

        self._tr_animate_single(next_team, position, all_names, frame=22)

    def _tr_reset(self):
        """Resetea el resultado para un nuevo sorteo con los mismos equipos."""
        self._tr_order_result = []
        self._tr_remaining_reveal = []
        try:
            self._tr_sub_lbl.config(text="Presiona GIRAR para empezar", fg=TEXT_MUTED)
            self._tr_slot_lbl.config(text="—", fg=ACCENT_GOLD)
            for w in self._tr_result_frame.winfo_children():
                w.destroy()
            tk.Label(self._tr_result_frame,
                     text="El orden de participación aparecerá aquí.",
                     font=self.f_small, bg=BG_CARD, fg=TEXT_MUTED,
                     wraplength=350).pack(pady=20)
        except tk.TclError:
            pass
        self._tr_set_buttons_state("normal")

    def _tr_set_buttons_state(self, state):
        """Habilita o deshabilita los botones de acción."""
        color_spin  = BTN_REVEAL  if state == "normal" else "#ADB5BD"
        color_one   = "#7B2FBE"   if state == "normal" else "#ADB5BD"
        color_reset = "#6C757D"   if state == "normal" else "#ADB5BD"

        try:
            self._tr_btn_spin.config(state=state, bg=color_spin)
            self._tr_btn_one.config(state=state,  bg=color_one)
            self._tr_btn_reset.config(state=state, bg=color_reset)
        except tk.TclError:
            pass  # El widget fue destruido durante navegación

    # ── Animación completa ────────────────────────────────────────────────────

    def _tr_animate_spin(self, final_order, all_names, frame):
        """Animación tipo slot-machine: mezcla nombres rápido y frena."""
        try:
            if frame > 0:
                random_val = random.choice(all_names)
                self._tr_slot_lbl.config(text=random_val, fg=ACCENT_GOLD)
                delay = int(18 + (28 - frame) ** 1.6)
                self.after(delay, self._tr_animate_spin, final_order, all_names, frame - 1)
            else:
                # Mostrar el primero del orden final con fanfarria
                winner = final_order[0]
                self._tr_slot_lbl.config(text=winner, fg="#00FF00")
                self._tr_sub_lbl.config(
                    text=f"🥇 ¡{winner} PARTICIPA PRIMERO!",
                    fg="#00FF00"
                )
                self._tr_spinning = False
                self._tr_set_buttons_state("normal")
                # Dibujar el resultado completo
                self.after(600, lambda: self._tr_draw_result(final_order))
        except tk.TclError:
            pass  # Widget destruido, ignorar

    # ── Animación de uno en uno ───────────────────────────────────────────────

    def _tr_animate_single(self, final_team, position, all_names, frame):
        """Animación para revelar un solo equipo en su posición."""
        ordinals = ["1°", "2°", "3°", "4°", "5°", "6°", "7°", "8°", "9°", "10°"]
        ordinal = ordinals[position - 1] if position <= len(ordinals) else f"{position}°"
        try:
            if frame > 0:
                random_val = random.choice(all_names)
                self._tr_slot_lbl.config(text=random_val, fg=ACCENT_GOLD)
                delay = int(18 + (22 - frame) ** 1.7)
                self.after(delay, self._tr_animate_single, final_team, position, all_names, frame - 1)
            else:
                self._tr_slot_lbl.config(text=final_team, fg="#00FF00")
                self._tr_sub_lbl.config(
                    text=f"✅  {ordinal} lugar → {final_team}",
                    fg="#00FF00"
                )
                self._tr_spinning = False
                self._tr_set_buttons_state("normal")

                # Agregar a la lista de resultados visualmente
                self._tr_append_result_row(final_team, position)

                if not self._tr_remaining_reveal:
                    self._tr_sub_lbl.config(
                        text="🏆 ¡Orden completo revelado!",
                        fg=ACCENT_GOLD
                    )
        except tk.TclError:
            pass  # Widget destruido, ignorar

    # =========================================================================
    #  RENDERIZADO DEL RESULTADO
    # =========================================================================

    def _tr_draw_result(self, order):
        """Dibuja el resultado completo en el panel de resultado."""
        for w in self._tr_result_frame.winfo_children():
            w.destroy()

        medals = ["🥇", "🥈", "🥉"]
        for i, team_name in enumerate(order):
            pos = i + 1
            color = TEAM_COLORS[i % len(TEAM_COLORS)]
            medal = medals[i] if i < 3 else f"{pos}°"

            row = tk.Frame(self._tr_result_frame, bg=BG_CARD)
            row.pack(fill="x", pady=3)

            # Indicador de color del equipo
            tk.Frame(row, bg=color, width=6).pack(side="left", fill="y", padx=(0, 8))

            medal_lbl = tk.Label(row, text=medal,
                                 font=self.f_name, bg=BG_CARD, fg=TEXT_DARK, width=4)
            medal_lbl.pack(side="left")

            tk.Label(row, text=team_name,
                     font=self.f_body, bg=BG_CARD, fg=TEXT_DARK,
                     anchor="w").pack(side="left", fill="x", expand=True)

            pos_lbl = tk.Label(row, text=f"Turno {pos}",
                               font=self.f_small, bg=BG_CARD, fg=color)
            pos_lbl.pack(side="right", padx=8)

    def _tr_append_result_row(self, team_name, position):
        """Agrega una fila al panel de resultado (modo uno-en-uno)."""
        # Limpiar placeholder si es la primera fila
        children = self._tr_result_frame.winfo_children()
        if children and isinstance(children[0], tk.Label):
            children[0].destroy()

        i = position - 1
        color = TEAM_COLORS[i % len(TEAM_COLORS)]
        medals = ["🥇", "🥈", "🥉"]
        medal = medals[i] if i < 3 else f"{position}°"

        row = tk.Frame(self._tr_result_frame, bg=BG_CARD)
        row.pack(fill="x", pady=3)

        tk.Frame(row, bg=color, width=6).pack(side="left", fill="y", padx=(0, 8))

        tk.Label(row, text=medal,
                 font=self.f_name, bg=BG_CARD, fg=TEXT_DARK, width=4).pack(side="left")

        tk.Label(row, text=team_name,
                 font=self.f_body, bg=BG_CARD, fg=TEXT_DARK,
                 anchor="w").pack(side="left", fill="x", expand=True)

        tk.Label(row, text=f"Turno {position}",
                 font=self.f_small, bg=BG_CARD, fg=color).pack(side="right", padx=8)
