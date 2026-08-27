"""Tab: CSGi skeleton graph processor."""

from __future__ import annotations

import os
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Optional

from ...core.master_table import MasterTable
from ..theme import APP_VERSION, THEME
from ..widgets import OutputWriter, make_text

try:
    import numpy as np
    from PIL import Image, ImageTk
    from scipy import ndimage

    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False
    np = None  # type: ignore[assignment]
    Image = None  # type: ignore[assignment]
    ImageTk = None  # type: ignore[assignment]
    ndimage = None  # type: ignore[assignment]


class CSGiTab:
    """Tab: CSGi skeleton graph processor."""

    def __init__(self, notebook: ttk.Notebook, table: MasterTable) -> None:
        self._table = table
        self._tab = ttk.Frame(notebook)
        notebook.add(self._tab, text="  🕸 CSGi  ")

        self._orig_photo: Any = None
        self._skel_photo: Any = None
        self._orig_lbl: Optional[ttk.Label] = None
        self._skel_lbl: Optional[ttk.Label] = None
        self._rtext: Optional[tk.Text] = None
        self._rout: Optional[OutputWriter] = None
        self._names: list = []
        self._var: Optional[tk.StringVar] = None

        if not HAS_DEPS:
            ttk.Label(
                self._tab,
                text="CSGi requires: pip install numpy Pillow scipy",
                foreground=THEME.error,
            ).pack(pady=20)
            return

        self._build()

    def _build(self) -> None:
        ctrl = ttk.Frame(self._tab)
        ctrl.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(ctrl, text="Glyph:").pack(side=tk.LEFT)
        entries = self._table.all_entries()
        self._names = [f"{e.char} ({e.name})" for e in entries]
        self._var = tk.StringVar(value=self._names[1] if len(self._names) > 1 else "")
        ttk.Combobox(
            ctrl,
            textvariable=self._var,
            values=self._names,
            width=15,
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            ctrl,
            text="▶ Process",
            command=self._process,
        ).pack(side=tk.LEFT, padx=2)

        workspace = ttk.PanedWindow(self._tab, orient=tk.VERTICAL)
        workspace.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        img_panel = ttk.Frame(workspace)
        workspace.add(img_panel, weight=1)
        self._orig_lbl = ttk.Label(img_panel, text="[Original]")
        self._orig_lbl.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._skel_lbl = ttk.Label(img_panel, text="[Skeleton]")
        self._skel_lbl.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        res_panel = ttk.Frame(workspace)
        workspace.add(res_panel, weight=1)
        self._rtext, _ = make_text(res_panel, font=THEME.font_mono_sm)
        self._rout = OutputWriter(self._rtext)

    def _process(self) -> None:
        if not HAS_DEPS or self._rout is None or self._var is None:
            return

        selection = self._var.get()
        if not selection:
            return

        char = selection.split()[0]
        letter = self._table.get_by_char(char)
        if letter is None:
            messagebox.showerror("Error", f"Letter not found: {char}")
            return

        # Resolve relative to the location of this file (src/hijaiyyah/gui/tabs)
        base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        )
        glyph_path = os.path.join(base_dir, "data", "kfgqpc", "glyphs", f"{letter.index}.png")
        if not os.path.exists(glyph_path):
            messagebox.showerror("Error", f"Glyph not found: {glyph_path}")
            return

        try:
            from ...skeleton.contractor import SkeletonContractor
            from ...skeleton.skeletonizer import zhang_suen_thinness

            img_pil = Image.open(glyph_path).convert("L")
            arr = np.array(img_pil)
            binary = (arr < 128).astype(np.uint8)
            disp_size = (300, 300)

            # Show original
            self._orig_photo = ImageTk.PhotoImage(img_pil.resize(disp_size))
            if self._orig_lbl is not None:
                self._orig_lbl.config(image=self._orig_photo, text="")

            # Separate body from dots
            label_result: Any = ndimage.label(binary)
            labeled: Any = label_result[0]
            num_features: int = int(label_result[1])

            if num_features > 1:
                component_sizes_arr: Any = ndimage.sum(binary, labeled, range(1, num_features + 1))
                component_sizes: list = list(component_sizes_arr)
                largest = int(np.argmax(component_sizes)) + 1
                binary_body = (labeled == largest).astype(np.uint8)
            else:
                binary_body = binary

            # Skeletonize
            skeleton = zhang_suen_thinness(binary_body)

            # Show skeleton
            skel_display = ((1 - skeleton) * 255).astype(np.uint8)
            skel_img = Image.fromarray(skel_display).convert("L")
            self._skel_photo = ImageTk.PhotoImage(skel_img.resize(disp_size))
            if self._skel_lbl is not None:
                self._skel_lbl.config(image=self._skel_photo, text="")

            # Contract to graph
            contractor = SkeletonContractor(
                letter_hijaiyyah=letter.char,
                letter_name=letter.name,
                release_id=APP_VERSION,
            )
            graph = contractor.contract(skeleton)

            # Report
            body_px = int(np.sum(binary_body))
            skel_px = int(np.sum(skeleton))
            dot_count = max(0, num_features - 1) if num_features > 1 else 0

            lines = [
                f"CSGi ANALYSIS: {letter.char} ({letter.name})",
                "=" * 50,
                "",
                f"  Body pixels:     {body_px}",
                f"  Skeleton pixels: {skel_px}",
                f"  Nuqtah detected: {dot_count}",
                f"  Graph nodes:     {len(graph.nodes)}",
                f"  Graph edges:     {len(graph.edges)}",
                "",
                f"  Master Table A_N: {letter.vector[14]}",
                f"  CSGi dots:        {dot_count}",
                f"  Match: {'✓' if dot_count == letter.vector[14] else '✗'}",
                "",
                graph.to_json(indent=2),
            ]

            self._rout.set_text("\n".join(lines))

        except Exception as e:
            messagebox.showerror("CSGi Error", str(e))
