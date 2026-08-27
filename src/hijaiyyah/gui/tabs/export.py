"""Tab: Data export (JSON, CSV, Manifest)."""

from __future__ import annotations

import json
import tkinter as tk
from tkinter import filedialog, ttk

from ...core.master_table import MasterTable
from ..theme import APP_VERSION


class ExportTab:
    def __init__(self, notebook: ttk.Notebook, table: MasterTable):
        self._table = table
        self._tab = ttk.Frame(notebook)
        notebook.add(self._tab, text="  ⬡ Export  ")
        for label, cmd in [
            ("Export JSON", self._json),
            ("Export CSV", self._csv),
            ("Export Manifest", self._manifest),
        ]:
            ttk.Button(self._tab, text=label, command=cmd).pack(padx=10, pady=5, fill=tk.X)

    def _json(self):
        p = filedialog.asksaveasfilename(defaultextension=".json")
        if p:
            with open(p, "w", encoding="utf-8") as f:
                f.write(self._table.to_json())

    def _csv(self):
        p = filedialog.asksaveasfilename(defaultextension=".csv")
        if p:
            with open(p, "w", encoding="utf-8") as f:
                f.write(self._table.to_csv())

    def _manifest(self):
        p = filedialog.asksaveasfilename(defaultextension=".json")
        if p:
            with open(p, "w") as f:
                json.dump(
                    {"sha256": self._table.compute_sha256(), "version": APP_VERSION}, f, indent=2
                )
