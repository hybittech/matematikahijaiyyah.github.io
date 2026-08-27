"""
Tab: Letter Explorer — Interactive Scientific Panel
=====================================================
Professional multi-panel layout with real widgets:
  - Letter grid with visual feedback
  - Component bar charts (canvas-drawn)
  - Turning decomposition gauge
  - Properties table (treeview)
  - Exomatrix grid (colored cells)
  - Neighbor radar (canvas-drawn)
  - Real-time update on letter selection

No text dumps. Every value is a widget.
"""

from __future__ import annotations

import math
import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, List, Optional, Tuple

from ...algebra import exometric as exo
from ...algebra import intrametric as geo
from ...algebra import vektronometry as vec
from ...core.codex_entry import CodexEntry
from ...core.exomatrix import build_exomatrix
from ...core.guards import compute_rho, compute_U, guard_check, guard_detail
from ...core.master_table import MasterTable
from ..theme import THEME

# ── Color utilities ──────────────────────────────────────────────


def _lerp_color(val: float, low: str = "#2d3436", high: str = "#00cec9") -> str:
    """Linearly interpolate between two hex colors based on val (0..1)."""
    val = max(0.0, min(1.0, val))

    r1, g1, b1 = int(low[1:3], 16), int(low[3:5], 16), int(low[5:7], 16)
    r2, g2, b2 = int(high[1:3], 16), int(high[3:5], 16), int(high[5:7], 16)

    r = int(r1 + (r2 - r1) * val)
    g = int(g1 + (g2 - g1) * val)
    b = int(b1 + (b2 - b1) * val)

    return f"#{r:02x}{g:02x}{b:02x}"


def _guard_color(passed: bool) -> str:
    return "#00b894" if passed else "#d63031"


class LetterExplorerTab:
    """
    Interactive scientific panel for letter inspection.

    Layout:
    ┌────────────┬───────────────────────────────────────┐
    │            │  Header: Letter name, index, v₁₈      │
    │  Letter    ├───────────────┬───────────────────────┤
    │  Grid      │  Component    │  Turning              │
    │  (28 btns) │  Bar Chart    │  Decomposition Gauge  │
    │            ├───────────────┼───────────────────────┤
    │            │  Properties   │  Exomatrix            │
    │            │  Treeview     │  5×5 Grid             │
    │            ├───────────────┴───────────────────────┤
    │            │  Neighbor Bar + Classification         │
    └────────────┴───────────────────────────────────────┘
    """

    def __init__(self, notebook: ttk.Notebook, table: MasterTable) -> None:
        self._table = table
        self._entries = table.all_entries()
        self._tab = ttk.Frame(notebook)
        notebook.add(self._tab, text="  ✦ Letter Explorer  ")

        self._selected: Optional[CodexEntry] = None
        self._buttons: Dict[str, tk.Button] = {}

        # Widget references
        self._header_char = tk.StringVar(value="—")
        self._header_name = tk.StringVar(value="Select a letter")
        self._header_index = tk.StringVar(value="")
        self._header_vec = tk.StringVar(value="")
        self._header_guard = tk.StringVar(value="")
        self._header_theta = tk.StringVar(value="")

        self._component_canvas: Optional[tk.Canvas] = None
        self._turning_canvas: Optional[tk.Canvas] = None
        self._exo_canvas: Optional[tk.Canvas] = None
        self._neighbor_canvas: Optional[tk.Canvas] = None
        self._prop_tree: Optional[ttk.Treeview] = None
        self._class_label = tk.StringVar(value="")
        self._mod4_label = tk.StringVar(value="")

        self._build()

    def _build(self) -> None:
        main = ttk.PanedWindow(self._tab, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ── Left: Letter Grid ────────────────────────────────────
        left = ttk.Frame(main, width=180)
        main.add(left, weight=0)
        self._build_grid(left)

        # ── Right: Analysis panels ───────────────────────────────
        right = ttk.Frame(main)
        main.add(right, weight=1)
        self._build_panels(right)

    # ══════════════════════════════════════════════════════════════
    #  LEFT PANEL: LETTER GRID
    # ══════════════════════════════════════════════════════════════

    def _build_grid(self, parent: ttk.Frame) -> None:
        ttk.Label(
            parent,
            text="𝓗₂₈",
            font=("Segoe UI", 14, "bold"),
            foreground=THEME.hijaiyyah_fg,
        ).pack(pady=(5, 2))

        ttk.Label(
            parent,
            text="Select a letter:",
            foreground=THEME.dim_fg,
            font=("Segoe UI", 9),
        ).pack(pady=(0, 5))

        grid_frame = ttk.Frame(parent)
        grid_frame.pack(padx=5)

        for i, entry in enumerate(self._entries):
            row, col = divmod(i, 7)
            btn = tk.Button(
                grid_frame,
                text=entry.char,
                font=("Simplified Arabic", 18),
                width=3,
                height=1,
                bg=THEME.accent,
                fg=THEME.hijaiyyah_fg,
                activebackground=THEME.highlight,
                activeforeground="#ffffff",
                relief=tk.FLAT,
                cursor="hand2",
                command=lambda e=entry: self._select(e),
            )
            btn.grid(row=row, column=col, padx=2, pady=2)
            self._buttons[entry.char] = btn

        # Quick info below grid
        info_frame = ttk.Frame(parent)
        info_frame.pack(fill=tk.X, padx=5, pady=10)

        ttk.Label(
            info_frame,
            textvariable=self._header_guard,
            font=("Consolas", 10),
        ).pack()
        ttk.Label(
            info_frame,
            textvariable=self._class_label,
            foreground=THEME.dim_fg,
            font=("Consolas", 9),
            wraplength=170,
        ).pack()

    # ══════════════════════════════════════════════════════════════
    #  RIGHT PANELS
    # ══════════════════════════════════════════════════════════════

    def _build_panels(self, parent: ttk.Frame) -> None:
        # ── Row 0: Header ────────────────────────────────────────
        header = ttk.Frame(parent)
        header.pack(fill=tk.X, pady=(0, 5))

        tk.Label(
            header,
            textvariable=self._header_char,
            font=("Simplified Arabic", 36, "bold"),
            fg=THEME.hijaiyyah_fg,
            bg=THEME.bg,
        ).pack(side=tk.LEFT, padx=10)

        info_col = ttk.Frame(header)
        info_col.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(info_col, textvariable=self._header_name, font=("Segoe UI", 16, "bold")).pack(
            anchor=tk.W
        )
        ttk.Label(info_col, textvariable=self._header_index, foreground=THEME.dim_fg).pack(
            anchor=tk.W
        )
        ttk.Label(
            info_col,
            textvariable=self._header_theta,
            foreground=THEME.number_fg,
            font=("Consolas", 11),
        ).pack(anchor=tk.W)

        ttk.Label(
            header,
            textvariable=self._header_vec,
            font=("Consolas", 9),
            foreground=THEME.dim_fg,
            wraplength=400,
        ).pack(side=tk.RIGHT, padx=10)

        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X)

        # ── Row 1: Charts ────────────────────────────────────────
        row1 = ttk.Frame(parent)
        row1.pack(fill=tk.BOTH, expand=True, pady=5)

        # Component bar chart
        comp_frame = ttk.LabelFrame(row1, text="  Component Distribution  ")
        comp_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 3))
        self._component_canvas = tk.Canvas(
            comp_frame,
            bg=THEME.text_bg,
            highlightthickness=0,
            height=180,
        )
        self._component_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Turning decomposition gauge
        turn_frame = ttk.LabelFrame(row1, text="  Turning Decomposition  ")
        turn_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(3, 0))
        self._turning_canvas = tk.Canvas(
            turn_frame,
            bg=THEME.text_bg,
            highlightthickness=0,
            height=180,
        )
        self._turning_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ── Row 2: Table + Exomatrix ─────────────────────────────
        row2 = ttk.Frame(parent)
        row2.pack(fill=tk.BOTH, expand=True, pady=5)

        # Properties treeview
        prop_frame = ttk.LabelFrame(row2, text="  Properties  ")
        prop_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 3))

        columns = ("slot", "name", "value", "check")
        self._prop_tree = ttk.Treeview(
            prop_frame,
            columns=columns,
            show="headings",
            height=12,
        )
        self._prop_tree.heading("slot", text="#")
        self._prop_tree.heading("name", text="Component")
        self._prop_tree.heading("value", text="Value")
        self._prop_tree.heading("check", text="Status")
        self._prop_tree.column("slot", width=35, anchor=tk.CENTER)
        self._prop_tree.column("name", width=120)
        self._prop_tree.column("value", width=60, anchor=tk.CENTER)
        self._prop_tree.column("check", width=50, anchor=tk.CENTER)

        self._prop_tree.tag_configure("pass", foreground=THEME.success)
        self._prop_tree.tag_configure("fail", foreground=THEME.error)
        self._prop_tree.tag_configure("derived", foreground=THEME.warning)
        self._prop_tree.tag_configure("normal", foreground=THEME.fg)
        self._prop_tree.tag_configure("zero", foreground=THEME.dim_fg)

        self._prop_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Exomatrix 5×5 grid
        exo_frame = ttk.LabelFrame(row2, text="  Exomatrix E(h)  ")
        exo_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(3, 0))
        self._exo_canvas = tk.Canvas(
            exo_frame,
            bg=THEME.text_bg,
            highlightthickness=0,
            height=200,
        )
        self._exo_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ── Row 3: Neighbors + Classification ────────────────────
        row3 = ttk.Frame(parent)
        row3.pack(fill=tk.BOTH, expand=True, pady=5)

        nb_frame = ttk.LabelFrame(row3, text="  Nearest Neighbors (d₂)  ")
        nb_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 3))
        self._neighbor_canvas = tk.Canvas(
            nb_frame,
            bg=THEME.text_bg,
            highlightthickness=0,
            height=100,
        )
        self._neighbor_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        class_frame = ttk.LabelFrame(row3, text="  Classification & Mod-4  ")
        class_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(3, 0))
        ttk.Label(
            class_frame,
            textvariable=self._mod4_label,
            font=("Consolas", 11),
            wraplength=300,
        ).pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # ══════════════════════════════════════════════════════════════
    #  SELECTION AND UPDATE
    # ══════════════════════════════════════════════════════════════

    def _select(self, entry: CodexEntry) -> None:
        """Handle letter selection — update all panels."""
        # Update button highlighting
        for ch, btn in self._buttons.items():
            if ch == entry.char:
                btn.config(bg=THEME.highlight, fg="#ffffff")
            else:
                btn.config(bg=THEME.accent, fg=THEME.hijaiyyah_fg)

        self._selected = entry
        v = list(entry.vector)

        # Update header
        self._header_char.set(entry.char)
        self._header_name.set(f"{entry.name}")
        self._header_index.set(f"#{entry.index} of 28")
        self._header_theta.set(
            f"Θ̂ = {v[0]} ({v[0] * 90}°)  |  U = {compute_U(v)}  |  ρ = {compute_rho(v)}"
        )
        self._header_vec.set(f"v₁₈ = ({', '.join(str(x) for x in v)})")

        guard_ok = guard_check(v)
        self._header_guard.set(f"Guard: {'ALL PASS ✓' if guard_ok else 'FAIL ✗'}")

        # Update all panels
        self._update_component_chart(v)
        self._update_turning_gauge(v)
        self._update_properties(entry, v)
        self._update_exomatrix(v)
        self._update_neighbors(entry)
        self._update_classification(entry, v)

    # ── Component Bar Chart ──────────────────────────────────────

    def _update_component_chart(self, v: List[int]) -> None:
        c = self._component_canvas
        if c is None:
            return
        c.delete("all")
        c.update_idletasks()

        w = c.winfo_width()
        h = c.winfo_height()
        if w < 10 or h < 10:
            w, h = 400, 180

        # Data: 14 components + their names
        names = ["Θ̂", "Nₐ", "Nᵦ", "Nᵈ", "Kₚ", "Kₓ", "Kₛ", "Kₐ", "Kc", "Qₚ", "Qₓ", "Qₛ", "Qₐ", "Qc"]
        values = [v[i] for i in range(14)]
        max_val = max(max(values), 1)

        margin_left = 35
        margin_bottom = 25
        margin_top = 10
        bar_area_w = w - margin_left - 10
        bar_area_h = h - margin_bottom - margin_top
        n = len(values)
        bar_w = max(1, (bar_area_w - n * 2) // n)
        gap = 2

        # Group colors
        group_colors = {
            0: "#00cec9",  # Theta
            1: "#fdcb6e",
            2: "#fdcb6e",
            3: "#fdcb6e",  # N
            4: "#74b9ff",
            5: "#74b9ff",
            6: "#74b9ff",
            7: "#74b9ff",
            8: "#74b9ff",  # K
            9: "#a29bfe",
            10: "#a29bfe",
            11: "#a29bfe",
            12: "#a29bfe",
            13: "#a29bfe",  # Q
        }

        for i, val in enumerate(values):
            x = margin_left + i * (bar_w + gap)
            bar_h = int((val / max_val) * bar_area_h) if max_val > 0 else 0
            y_top = h - margin_bottom - bar_h
            y_bot = h - margin_bottom

            color = group_colors.get(i, "#636e72")
            if val == 0:
                color = "#2d3436"

            c.create_rectangle(x, y_top, x + bar_w, y_bot, fill=color, outline="")

            # Value on top
            if val > 0:
                c.create_text(
                    x + bar_w // 2,
                    y_top - 6,
                    text=str(val),
                    fill="#ffffff",
                    font=("Consolas", 8),
                )

            # Label at bottom
            c.create_text(
                x + bar_w // 2,
                y_bot + 10,
                text=names[i],
                fill=THEME.dim_fg,
                font=("Consolas", 7),
            )

        # Y-axis scale
        for tick in range(0, max_val + 1):
            y = (
                h - margin_bottom - int((tick / max_val) * bar_area_h)
                if max_val > 0
                else h - margin_bottom
            )
            c.create_text(
                margin_left - 5,
                y,
                text=str(tick),
                fill=THEME.dim_fg,
                font=("Consolas", 7),
                anchor=tk.E,
            )

        # Legend
        legend_items = [("Θ̂", "#00cec9"), ("N", "#fdcb6e"), ("K", "#74b9ff"), ("Q", "#a29bfe")]
        for i, (label, color) in enumerate(legend_items):
            lx = margin_left + i * 55
            c.create_rectangle(lx, 3, lx + 10, 13, fill=color, outline="")
            c.create_text(lx + 14, 8, text=label, fill=THEME.fg, font=("Consolas", 8), anchor=tk.W)

    # ── Turning Gauge ────────────────────────────────────────────

    def _update_turning_gauge(self, v: List[int]) -> None:
        c = self._turning_canvas
        if c is None:
            return
        c.delete("all")
        c.update_idletasks()

        w = c.winfo_width()
        h = c.winfo_height()
        if w < 10 or h < 10:
            w, h = 400, 180

        theta = v[0]
        U = compute_U(v)
        rho = theta - U

        cx, cy = w // 2, h // 2 + 10
        radius = min(w, h) // 2 - 25

        # Background arc (full circle = 8 quadrants = 720°)
        max_theta = 8
        c.create_oval(
            cx - radius, cy - radius, cx + radius, cy + radius, outline="#2d3436", width=15
        )

        # U arc (red-orange)
        if theta > 0 and U > 0:
            u_extent = -(U / max_theta) * 360
            c.create_arc(
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
                start=90,
                extent=u_extent,
                style=tk.ARC,
                outline="#e17055",
                width=15,
            )

        # Rho arc (teal, continuing from U)
        if theta > 0 and rho > 0:
            rho_start = 90 - (U / max_theta) * 360
            rho_extent = -(rho / max_theta) * 360
            c.create_arc(
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
                start=rho_start,
                extent=rho_extent,
                style=tk.ARC,
                outline="#00cec9",
                width=15,
            )

        # Center text
        c.create_text(
            cx, cy - 15, text=f"Θ̂ = {theta}", fill="#ffffff", font=("Consolas", 16, "bold")
        )
        c.create_text(cx, cy + 5, text=f"{theta * 90}°", fill=THEME.dim_fg, font=("Consolas", 12))

        # Legend
        c.create_rectangle(10, h - 35, 22, h - 25, fill="#e17055", outline="")
        c.create_text(26, h - 30, text=f"U = {U}", fill=THEME.fg, font=("Consolas", 9), anchor=tk.W)

        c.create_rectangle(10, h - 18, 22, h - 8, fill="#00cec9", outline="")
        c.create_text(
            26, h - 13, text=f"ρ = {rho}", fill=THEME.fg, font=("Consolas", 9), anchor=tk.W
        )

        # Mod-4 indicator
        mod4 = theta % 4
        mod_text = "mod4=0 (closed?)" if mod4 == 0 else f"mod4={mod4} (open)"
        mod_color = THEME.warning if mod4 == 0 else THEME.success
        c.create_text(
            w - 10, h - 13, text=mod_text, fill=mod_color, font=("Consolas", 9), anchor=tk.E
        )

    # ── Properties Treeview ──────────────────────────────────────

    def _update_properties(self, entry: CodexEntry, v: List[int]) -> None:
        tree = self._prop_tree
        if tree is None:
            return

        for item in tree.get_children():
            tree.delete(item)

        U = compute_U(v)
        rho = v[0] - U
        detail = guard_detail(v)
        n2 = vec.norm2(entry)
        pr = vec.primitive_ratios(entry)
        E = build_exomatrix(v)
        phi_val = exo.phi(E)

        # Components
        comp_data: List[Tuple[str, str, Any, str]] = [
            ("0", "Θ̂ (Inḥinā')", v[0], f"{v[0] * 90}°"),
            ("1", "Nₐ (Ascender)", v[1], "●" * v[1] if v[1] else "—"),
            ("2", "Nᵦ (Body)", v[2], "●" * v[2] if v[2] else "—"),
            ("3", "Nᵈ (Descender)", v[3], "●" * v[3] if v[3] else "—"),
            ("4", "Kₚ (Primary)", v[4], ""),
            ("5", "Kₓ (Auxiliary)", v[5], ""),
            ("6", "Kₛ (Str.Vert.)", v[6], ""),
            ("7", "Kₐ (Angular)", v[7], ""),
            ("8", "Kc (Closed)", v[8], ""),
            ("9", "Qₚ (Primary)", v[9], ""),
            ("10", "Qₓ (Auxiliary)", v[10], ""),
            ("11", "Qₛ (Smooth)", v[11], ""),
            ("12", "Qₐ (Angular)", v[12], ""),
            ("13", "Qc (Loop)", v[13], "◯" * v[13] if v[13] else "—"),
            ("14", "Aₙ (checksum)", v[14], "✓" if detail["R2"] else "✗"),
            ("15", "Aₖ (checksum)", v[15], "✓" if detail["R3"] else "✗"),
            ("16", "AQ (checksum)", v[16], "✓" if detail["R4"] else "✗"),
            ("17", "H* (Hamzah)", v[17], "← ك" if v[17] else ""),
            ("—", "U (budget)", U, "Qx+Qs+Qa+4Qc"),
            ("—", "ρ (residue)", rho, "✓" if rho >= 0 else "✗"),
            ("—", "‖v₁₄‖²", n2, f"‖v₁₄‖ = {math.sqrt(n2):.3f}"),
            ("—", "Φ (energy)", phi_val, f"surplus = {phi_val - n2}"),
            ("—", "r_N", f"{pr['r_N']:.4f}", f"{pr['r_N'] * 100:.1f}%"),
            ("—", "r_K", f"{pr['r_K']:.4f}", f"{pr['r_K'] * 100:.1f}%"),
            ("—", "r_Q", f"{pr['r_Q']:.4f}", f"{pr['r_Q'] * 100:.1f}%"),
        ]

        for slot, name, value, check in comp_data:
            tag = "normal"
            if slot == "—":
                tag = "derived"
            elif isinstance(value, int) and value == 0:
                tag = "zero"
            if "✗" in str(check):
                tag = "fail"

            tree.insert("", tk.END, values=(slot, name, value, check), tags=(tag,))

    # ── Exomatrix Grid ───────────────────────────────────────────

    def _update_exomatrix(self, v: List[int]) -> None:
        c = self._exo_canvas
        if c is None:
            return
        c.delete("all")
        c.update_idletasks()

        w = c.winfo_width()
        h = c.winfo_height()
        if w < 10 or h < 10:
            w, h = 300, 200

        E = build_exomatrix(v)
        audit_result = exo.audit(E)

        cell_w = min(50, (w - 80) // 5)
        cell_h = min(30, (h - 60) // 5)
        start_x = 70
        start_y = 30

        row_labels = ["Turn", "Nuq", "Khat", "Qaw", "Meta"]
        col_labels = ["C0", "C1", "C2", "C3", "C4"]

        max_val = max(max(max(row) for row in E), 1)

        # Column headers
        for j in range(5):
            x = start_x + j * cell_w + cell_w // 2
            c.create_text(
                x, start_y - 12, text=col_labels[j], fill=THEME.dim_fg, font=("Consolas", 8)
            )

        # Row labels + cells
        for i in range(5):
            y = start_y + i * cell_h
            c.create_text(
                start_x - 5,
                y + cell_h // 2,
                text=row_labels[i],
                fill=THEME.dim_fg,
                font=("Consolas", 8),
                anchor=tk.E,
            )

            for j in range(5):
                x = start_x + j * cell_w
                val = E[i][j]
                intensity = val / max_val if max_val > 0 else 0
                bg = _lerp_color(intensity, "#1a1a2e", "#00cec9")

                c.create_rectangle(x, y, x + cell_w, y + cell_h, fill=bg, outline="#2d3436")
                if val != 0:
                    c.create_text(
                        x + cell_w // 2,
                        y + cell_h // 2,
                        text=str(val),
                        fill="#ffffff",
                        font=("Consolas", 10, "bold"),
                    )

        # Audit results
        audit_y = start_y + 5 * cell_h + 15
        for k, key in enumerate(["R1", "R2", "R3", "R4", "R5"]):
            ax = start_x + k * 45
            passed = audit_result[key]
            color = _guard_color(passed)
            symbol = "✓" if passed else "✗"
            c.create_text(
                ax + 20, audit_y, text=f"{key}:{symbol}", fill=color, font=("Consolas", 9)
            )

        # Phi
        phi_val = exo.phi(E)
        c.create_text(
            start_x,
            audit_y + 18,
            text=f"Φ = {phi_val}",
            fill=THEME.number_fg,
            font=("Consolas", 10),
            anchor=tk.W,
        )

    # ── Neighbor Bars ────────────────────────────────────────────

    def _update_neighbors(self, entry: CodexEntry) -> None:
        c = self._neighbor_canvas
        if c is None:
            return
        c.delete("all")
        c.update_idletasks()

        w = c.winfo_width()
        h = c.winfo_height()
        if w < 10 or h < 10:
            w, h = 400, 100

        knn = geo.k_nearest(entry, 7)
        if not knn:
            return

        max_d = max(d for _, d in knn)
        if max_d == 0:
            max_d = 1

        margin_left = 30
        bar_area = w - margin_left - 20
        bar_h = max(8, (h - 10) // len(knn) - 3)

        for i, (ch, d) in enumerate(knn):
            y = 5 + i * (bar_h + 3)
            bar_w = int((d / max_d) * bar_area * 0.8)
            color = _lerp_color(1.0 - d / max_d, "#636e72", "#00cec9")

            # Letter label
            c.create_text(
                15, y + bar_h // 2, text=ch, fill=THEME.hijaiyyah_fg, font=("Simplified Arabic", 11)
            )

            # Bar
            c.create_rectangle(
                margin_left, y, margin_left + bar_w, y + bar_h, fill=color, outline=""
            )

            # Distance value
            c.create_text(
                margin_left + bar_w + 5,
                y + bar_h // 2,
                text=f"{d:.3f}",
                fill=THEME.dim_fg,
                font=("Consolas", 8),
                anchor=tk.W,
            )

    # ── Classification ───────────────────────────────────────────

    def _update_classification(self, entry: CodexEntry, v: List[int]) -> None:
        theta = v[0]
        mod4 = theta % 4
        U = compute_U(v)
        rho = theta - U
        a_total = v[14] + v[15] + v[16]

        # Structure type
        if a_total == 0:
            struct = "Empty"
        elif v[15] > 0 and v[16] == 0 and v[14] == 0:
            struct = "Pure Line"
        elif v[16] > 0 and v[15] == 0 and v[14] == 0:
            struct = "Pure Curve"
        elif v[14] >= a_total * 0.5:
            struct = "Dot-Dominated"
        else:
            struct = "Mixed"

        # Turning type
        if theta == 0:
            turn = "Zero turning"
        elif U == 0:
            turn = "Pure primary"
        elif rho == 0:
            turn = "Pure non-primary"
        else:
            turn = f"Mixed (U={U}, ρ={rho})"

        # Mod-4
        if mod4 == 0:
            if theta == 0:
                mod4_text = "Θ̂ = 0 → zero turning (straight)"
            else:
                mod4_text = f"Θ̂ = {theta} ≡ 0 (mod 4) → POSSIBLY CLOSED"
        else:
            mod4_text = f"Θ̂ = {theta} ≡ {mod4} (mod 4) → DEFINITELY OPEN"

        # Energy rank
        table = exo.energy_table()
        rank = 0
        for r in table:
            if r["letter"] == entry.char:
                rank = r["rank"]
                break

        text = (
            f"Structure: {struct}\n"
            f"Turning:   {turn}\n"
            f"Mod-4:     {mod4_text}\n"
            f"Energy:    rank #{rank}/28\n"
            f"Guard:     {'ALL PASS ✓' if guard_check(v) else 'FAIL ✗'}"
        )

        self._mod4_label.set(text)
        self._class_label.set(f"{struct} | {turn}")
