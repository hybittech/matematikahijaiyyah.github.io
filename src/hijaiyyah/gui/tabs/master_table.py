"""Tab: Master Table — treeview of all 28 letters."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ...core.constants import V18_SLOTS
from ...core.master_table import MasterTable
from ..theme import THEME

TABLE_COLUMNS = ["#", "Huruf", "Name", *list(V18_SLOTS)]


class MasterTableTab:
    def __init__(self, notebook: ttk.Notebook, table: MasterTable):
        self._table = table
        self._tab = ttk.Frame(notebook)
        notebook.add(self._tab, text="  ▦ Master Table  ")
        self._build()

    def _build(self):
        frame = ttk.Frame(self._tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        tree = ttk.Treeview(frame, columns=TABLE_COLUMNS, show="headings", height=28)
        for col in TABLE_COLUMNS:
            w = 60 if col in ("#", "Huruf", "Name") else 40
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor=tk.CENTER)

        # Configure alternating row colors
        tree.tag_configure("odd", background=THEME.text_bg)
        tree.tag_configure("even", background=THEME.bg)

        for i, entry in enumerate(self._table.all_entries()):
            tag = "even" if i % 2 == 0 else "odd"
            tree.insert("", tk.END, values=[entry.index, entry.char, entry.name, *entry.vector], tags=(tag,))
        sb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
