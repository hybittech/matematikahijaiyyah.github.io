"""Theme configuration for the HOM GUI."""

from __future__ import annotations

import os
from dataclasses import dataclass
from tkinter import ttk
from typing import Tuple

APP_TITLE = "HOM — Hijaiyyah Operating Machine"
APP_VERSION = "HM-28-v1.0-HC18D"
MIN_SIZE = (1280, 860)
LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "Logo HOM.png")
MATH_LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "Mathematics Hijaiyyah.png")


@dataclass(frozen=True)
class Theme:
    bg: str = "#0d1117"
    fg: str = "#e6edf3"
    accent: str = "#161b22"
    highlight: str = "#1f6feb"
    success: str = "#3fb950"
    error: str = "#f85149"
    warning: str = "#d29922"
    text_bg: str = "#010409"
    header_bg: str = "#010409"
    header_fg: str = "#e6edf3"
    hijaiyyah_fg: str = "#58a6ff"
    number_fg: str = "#7ee787"
    dim_fg: str = "#8b949e"
    border: str = "#30363d"
    surface: str = "#161b22"

    font_mono: Tuple[str, int] = ("Consolas", 11)
    font_mono_sm: Tuple[str, int] = ("Consolas", 10)
    font_mono_lg: Tuple[str, int] = ("Consolas", 12)
    font_ui: Tuple[str, int] = ("Segoe UI", 10)
    font_ui_bold: Tuple = ("Segoe UI", 11, "bold")
    font_header: Tuple = ("Segoe UI", 14, "bold")
    font_hijaiyyah: Tuple[str, int] = ("Simplified Arabic", 18)


THEME = Theme()


def configure_styles() -> None:
    style = ttk.Style()
    style.theme_use("clam")

    # ── Base frames ──────────────────────────────────────────
    style.configure("TFrame", background=THEME.bg)
    style.configure("TPanedwindow", background=THEME.bg)
    style.configure("TSeparator", background=THEME.border)

    # ── Labels ───────────────────────────────────────────────
    style.configure("TLabel", background=THEME.bg, foreground=THEME.fg, font=THEME.font_mono)
    style.configure(
        "Header.TLabel",
        background=THEME.header_bg,
        foreground=THEME.header_fg,
        font=THEME.font_header,
        padding=8,
    )
    style.configure(
        "Subtitle.TLabel",
        background=THEME.header_bg,
        foreground=THEME.dim_fg,
        font=THEME.font_ui,
        padding=(8, 0),
    )
    style.configure(
        "Status.TLabel",
        background=THEME.surface,
        foreground=THEME.dim_fg,
        font=THEME.font_mono_sm,
        padding=4,
    )
    style.configure(
        "Seal.TLabel",
        background=THEME.surface,
        foreground=THEME.success,
        font=("Consolas", 9, "bold"),
        padding=4,
    )

    # ── Notebook tabs ────────────────────────────────────────
    style.configure("TNotebook", background=THEME.bg, borderwidth=0)
    style.configure(
        "TNotebook.Tab",
        background=THEME.accent,
        foreground=THEME.dim_fg,
        padding=[14, 6],
        font=THEME.font_ui,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", THEME.highlight)],
        foreground=[("selected", THEME.fg)],
    )

    # ── Buttons ──────────────────────────────────────────────
    style.configure(
        "TButton",
        background=THEME.accent,
        foreground=THEME.fg,
        font=THEME.font_ui,
        padding=6,
        borderwidth=1,
        relief="flat",
    )
    style.map(
        "TButton",
        background=[("active", THEME.highlight), ("pressed", THEME.highlight)],
        foreground=[("active", "#ffffff")],
    )
    style.configure(
        "Accent.TButton",
        background=THEME.highlight,
        foreground="#ffffff",
        font=THEME.font_ui_bold,
        padding=8,
    )

    # ── LabelFrame ───────────────────────────────────────────
    style.configure("TLabelframe", background=THEME.bg, bordercolor=THEME.border, relief="groove")
    style.configure(
        "TLabelframe.Label",
        background=THEME.bg,
        foreground=THEME.hijaiyyah_fg,
        font=THEME.font_ui_bold,
    )

    # ── Treeview ─────────────────────────────────────────────
    style.configure(
        "Treeview",
        background=THEME.text_bg,
        foreground=THEME.fg,
        fieldbackground=THEME.text_bg,
        font=THEME.font_mono_sm,
        borderwidth=0,
        rowheight=22,
    )
    style.configure(
        "Treeview.Heading", background=THEME.accent, foreground=THEME.fg, font=THEME.font_ui_bold
    )
    style.map(
        "Treeview", background=[("selected", THEME.highlight)], foreground=[("selected", "#ffffff")]
    )

    # ── Combobox ─────────────────────────────────────────────
    style.configure(
        "TCombobox", fieldbackground=THEME.text_bg, foreground=THEME.fg, background=THEME.accent
    )

    # ── Entry ────────────────────────────────────────────────
    style.configure("TEntry", fieldbackground=THEME.text_bg, foreground=THEME.fg)

    # ── Scrollbar ────────────────────────────────────────────
    style.configure(
        "Vertical.TScrollbar", background=THEME.accent, troughcolor=THEME.bg, borderwidth=0
    )
    style.configure(
        "Horizontal.TScrollbar", background=THEME.accent, troughcolor=THEME.bg, borderwidth=0
    )
