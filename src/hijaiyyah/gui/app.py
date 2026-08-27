"""
HOM — Hijaiyyah Operating Machine
Main application: assembles all tabs and launches the GUI.
"""

from __future__ import annotations

import os
import tkinter as tk
from tkinter import ttk
from typing import Optional

from ..core.master_table import MASTER_TABLE
from ..hisa.machine import HISAMachine
from ..language.evaluator import HCEvaluator
from .tabs.audit import AuditTab
from .tabs.bytecode import BytecodeTab
from .tabs.csgi import CSGiTab
from .tabs.export import ExportTab
from .tabs.five_fields import FiveFieldsTab
from .tabs.geometry import GeometryTab
from .tabs.hisa_machine import HISAMachineTab
from .tabs.hisab import HISABTab
from .tabs.ide import IDETab
from .tabs.letter_explorer import LetterExplorerTab
from .tabs.master_table import MasterTableTab
from .tabs.release import ReleaseTab
from .tabs.string_integral import StringIntegralTab
from .tabs.theorems import TheoremTab
from .theme import (
    APP_TITLE,
    APP_VERSION,
    LOGO_PATH,
    MATH_LOGO_PATH,
    MIN_SIZE,
    THEME,
    configure_styles,
)


class HOMApp:
    """
    HOM: Hijaiyyah Operating Machine.
    Main application class. Owns Tk root and delegates to modular tabs.
    """

    def __init__(self) -> None:
        self._table = MASTER_TABLE
        self._machine = HISAMachine(self._table)
        self._evaluator = HCEvaluator()

        self._root = tk.Tk()
        self._root.title(APP_TITLE)
        self._root.minsize(*MIN_SIZE)
        self._root.configure(bg=THEME.bg)

        # Set window icon
        try:
            if os.path.exists(LOGO_PATH):
                icon = tk.PhotoImage(file=LOGO_PATH)
                self._root.iconphoto(True, icon)
                self._logo_img = icon  # keep reference
        except Exception:
            pass

        configure_styles()
        self._build()

    def _build(self) -> None:
        main = ttk.Frame(self._root)
        main.pack(fill=tk.BOTH, expand=True)

        self._build_header(main)

        nb = ttk.Notebook(main)
        nb.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 5))

        # Instantiate all tabs
        LetterExplorerTab(nb, self._table)
        MasterTableTab(nb, self._table)
        TheoremTab(nb, self._table, self._evaluator, self._root)
        StringIntegralTab(nb, self._table, self._evaluator)
        AuditTab(nb, self._table, self._evaluator, self._root)
        ExportTab(nb, self._table)
        FiveFieldsTab(nb, self._table, self._evaluator)
        GeometryTab(nb, self._table, self._evaluator)
        IDETab(nb, self._root)
        HISAMachineTab(nb, self._machine)
        BytecodeTab(nb)
        CSGiTab(nb, self._table)
        HISABTab(nb, self._table)
        ReleaseTab(nb, self._table, self._root)

        self._build_statusbar(main)

    def _build_header(self, parent: ttk.Frame) -> None:
        """Professional header with logo, title, and seal indicator."""
        header = tk.Frame(parent, bg=THEME.header_bg, height=70)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)

        # ── Logo ─────────────────────────────────────────────
        self._header_logo: Optional[tk.PhotoImage] = None
        try:
            if os.path.exists(LOGO_PATH):
                img = tk.PhotoImage(file=LOGO_PATH)
                # Subsample to ~48px height
                scale = max(1, img.height() // 48)
                img = img.subsample(scale, scale)
                self._header_logo = img
                tk.Label(
                    header,
                    image=img,
                    bg=THEME.header_bg,
                ).pack(side=tk.LEFT, padx=(12, 8), pady=8)
        except Exception:
            pass

        # ── Title block (Math Logo) ──────────────────────────
        title_frame = tk.Frame(header, bg=THEME.header_bg)
        title_frame.pack(side=tk.LEFT, fill=tk.Y, pady=8)

        self._header_math_logo: Optional[tk.PhotoImage] = None
        try:
            if os.path.exists(MATH_LOGO_PATH):
                img_m = tk.PhotoImage(file=MATH_LOGO_PATH)
                # Keep original size if it fits, or scale nicely
                scale_m = max(1, img_m.height() // 48)
                img_m = img_m.subsample(scale_m, scale_m)
                self._header_math_logo = img_m
                tk.Label(
                    title_frame,
                    image=img_m,
                    bg=THEME.header_bg,
                ).pack(side=tk.LEFT, padx=(0, 6))
            else:
                tk.Label(
                    title_frame,
                    text="HOM",
                    font=("Segoe UI", 22, "bold"),
                    fg=THEME.hijaiyyah_fg,
                    bg=THEME.header_bg,
                ).pack(side=tk.LEFT, padx=(0, 6))
        except Exception:
            tk.Label(
                title_frame,
                text="HOM",
                font=("Segoe UI", 22, "bold"),
                fg=THEME.hijaiyyah_fg,
                bg=THEME.header_bg,
            ).pack(side=tk.LEFT, padx=(0, 6))

        subtitle_frame = tk.Frame(title_frame, bg=THEME.header_bg)
        subtitle_frame.pack(side=tk.LEFT, anchor=tk.W)

        tk.Label(
            subtitle_frame,
            text="Hijaiyyah Operating Machine",
            font=("Segoe UI", 13, "bold"),
            fg=THEME.header_fg,
            bg=THEME.header_bg,
        ).pack(anchor=tk.W)

        tk.Label(
            subtitle_frame,
            text="Formal Computational Framework for Hijaiyyah Letterform Geometry",
            font=("Segoe UI", 9),
            fg=THEME.dim_fg,
            bg=THEME.header_bg,
        ).pack(anchor=tk.W)

        # ── Right: Seal + Version ────────────────────────────
        right_frame = tk.Frame(header, bg=THEME.header_bg)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=12, pady=8)

        sha_short = self._table.compute_sha256()[:16]

        tk.Label(
            right_frame,
            text=APP_VERSION,
            font=("Consolas", 10, "bold"),
            fg=THEME.number_fg,
            bg=THEME.header_bg,
        ).pack(anchor=tk.E)

        tk.Label(
            right_frame,
            text=f"SHA-256: {sha_short}…",
            font=("Consolas", 8),
            fg=THEME.dim_fg,
            bg=THEME.header_bg,
        ).pack(anchor=tk.E)

        tk.Label(
            right_frame,
            text="● SEALED",
            font=("Consolas", 9, "bold"),
            fg=THEME.success,
            bg=THEME.header_bg,
        ).pack(anchor=tk.E)

        # ── Accent line under header ─────────────────────────
        accent_line = tk.Frame(parent, bg=THEME.highlight, height=2)
        accent_line.pack(fill=tk.X)

    def _build_statusbar(self, parent: ttk.Frame) -> None:
        """Professional status bar with version, stats, and timestamp."""
        bar = tk.Frame(parent, bg=THEME.surface, height=24)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)

        sha_short = self._table.compute_sha256()[:16]
        self._table.all_entries()

        # Left: version + SHA
        tk.Label(
            bar,
            text=f"  {APP_VERSION}  │  SHA-256: {sha_short}…",
            font=("Consolas", 9),
            fg=THEME.dim_fg,
            bg=THEME.surface,
        ).pack(side=tk.LEFT)

        # Center: letter/dimension stats
        tk.Label(
            bar,
            text="28 letters  ·  18 dimensions  ·  252 bytes ROM",
            font=("Consolas", 9),
            fg=THEME.dim_fg,
            bg=THEME.surface,
        ).pack(side=tk.LEFT, padx=20)

        # Right: copyright
        tk.Label(
            bar,
            text="© 2026 HMCL  ",
            font=("Consolas", 9),
            fg=THEME.dim_fg,
            bg=THEME.surface,
        ).pack(side=tk.RIGHT)

    def run(self) -> None:
        self._root.mainloop()


def main() -> None:
    app = HOMApp()
    app.run()
