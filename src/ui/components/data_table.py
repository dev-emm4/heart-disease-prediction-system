"""
components/data_table.py
────────────────────────
Reusable Treeview-based table with:
  • Alternating row colours
  • Sortable columns (click heading)
  • Vertical scrollbar
  • Striped tags: 'even' / 'odd'

Usage:
    cols = [("id", "ID", 120), ("model", "Model", 110), ...]
    table = DataTable(parent, columns=cols)
    table.pack(fill=tk.BOTH, expand=True)
    table.insert_row(("abc", "NaiveBayes", ...))
    table.clear()
"""

import tkinter as tk
from tkinter import ttk
from ui.theme import COLORS, FONTS


class DataTable(tk.Frame):
    """
    Wraps ttk.Treeview with a scrollbar.
    columns: list of (key, heading_text, width_px)
    """

    def __init__(self, parent, columns: list[tuple[str, str, int]], show_index: bool = False, **kwargs):
        super().__init__(parent, bg=COLORS["surface"], **kwargs)

        self._col_keys = [c[0] for c in columns]
        self._sort_reverse: dict[str, bool] = {k: False for k in self._col_keys}

        # ── Treeview ─────────────────────────────────────────────────────────
        self.tree = ttk.Treeview(
            self,
            columns=self._col_keys,
            show="headings",
            selectmode="browse",
            style="Treeview",
        )

        # ── Configure headings & columns ─────────────────────────────────────
        for key, heading, width in columns:
            self.tree.heading(key, text=heading,
                              command=lambda k=key: self._sort_by(k))
            self.tree.column(key, width=width, minwidth=60, anchor=tk.W)

        # ── Alternating row colours ───────────────────────────────────────────
        self.tree.tag_configure("even", background=COLORS["table_row_even"])
        self.tree.tag_configure("odd",  background=COLORS["table_row_odd"])

        # ── Scrollbar ────────────────────────────────────────────────────────
        vsb = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self._row_count = 0

    # ── Public API ──────────────────────────────────────────────────────────────
    def insert_row(self, values: tuple, tags: tuple = ()) -> str:
        """Append one row.  Returns the new item's iid."""
        tag = "even" if self._row_count % 2 == 0 else "odd"
        iid = self.tree.insert("", tk.END, values=values, tags=(tag, *tags))
        self._row_count += 1
        return iid

    def clear(self):
        """Remove all rows."""
        self.tree.delete(*self.tree.get_children())
        self._row_count = 0

    def selected_values(self) -> tuple | None:
        """Return the values of the currently selected row, or None."""
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0], "values")

    def selected_iid(self) -> str | None:
        sel = self.tree.selection()
        return sel[0] if sel else None

    def delete_selected(self) -> tuple | None:
        """Delete the selected row and return its values."""
        iid = self.selected_iid()
        if iid:
            vals = self.tree.item(iid, "values")
            self.tree.delete(iid)
            self._row_count -= 1
            return vals
        return None

    def bind_select(self, callback):
        """callback(values_tuple) called when a row is selected."""
        self.tree.bind("<<TreeviewSelect>>", lambda _: self._on_select(callback))

    def get_all_values(self) -> list[tuple]:
        return [self.tree.item(iid, "values") for iid in self.tree.get_children()]

    # ── Sorting ─────────────────────────────────────────────────────────────────
    def _sort_by(self, col: str):
        rows = [(self.tree.set(iid, col), iid) for iid in self.tree.get_children()]
        rev = self._sort_reverse[col]
        rows.sort(reverse=rev, key=lambda x: x[0].lower() if isinstance(x[0], str) else x[0])
        for idx, (_, iid) in enumerate(rows):
            self.tree.move(iid, "", idx)
            tag = "even" if idx % 2 == 0 else "odd"
            self.tree.item(iid, tags=(tag,))
        self._sort_reverse[col] = not rev

    def _on_select(self, callback):
        vals = self.selected_values()
        if vals:
            callback(vals)
