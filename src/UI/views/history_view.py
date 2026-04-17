"""
views/history_view.py
──────────────────────
View: Prediction History

Features
  • Load all predictions, filter by model
  • Pagination — 500 records per page, Prev / Next navigation
  • Click a row to open the feature-vector detail panel on the right
  • ✕ close button on the detail panel — collapses it AND clears the
    table selection so the Delete button goes back to disabled
  • Delete a selected record
  • "Clear All History" placeholder button (wired once endpoint exists)

Controller methods used
  getAllPredictions()          → dict
  getPredictionsByModel(name) → dict
  deletePrediction(id)        → dict
  clearAllHistory()           → dict  [PLACEHOLDER]
"""

import tkinter as tk
from tkinter import ttk, messagebox
from UI.theme import COLORS, FONTS, DIMS
from UI.components.card import make_card, page_header, hline
from UI.components.data_table import DataTable
from UI.utils.formatters import fmt_timestamp, fmt_uuid_short, fmt_feature_vector


# Number of records shown per page
PAGE_SIZE = 500


class HistoryView(tk.Frame):
    """Browse, inspect, and delete stored prediction records."""

    MODELS = ["All Models", "NaiveBayes", "SVM", "DecisionTree"]

    def __init__(self, parent, controller, notify):
        super().__init__(parent, bg=COLORS["window_bg"])
        self.controller = controller
        self.notify = notify

        self._all_records: list[dict] = []       # full dataset from controller
        self._filtered_records: list[dict] = []  # after model filter is applied
        self._current_page: int = 0              # 0-based page index

        self._build()

    def on_show(self):
        """Auto-refresh every time this view is navigated to."""
        self._load_data()

    # ── Layout ──────────────────────────────────────────────────────────────────
    def _build(self):
        outer = tk.Frame(self, bg=COLORS["window_bg"])
        outer.pack(fill=tk.BOTH, expand=True, padx=24, pady=20)
        outer.rowconfigure(1, weight=1)
        outer.columnconfigure(0, weight=1)

        page_header(outer, "Prediction History",
                    "Browse and manage all stored predictions.").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 16))

        body = tk.Frame(outer, bg=COLORS["window_bg"])
        body.grid(row=1, column=0, sticky=tk.NSEW)
        body.rowconfigure(0, weight=1)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)

        self._build_list_panel(body)
        self._build_detail_panel(body)

    # ── Left panel: toolbar + table + pagination + action bar ───────────────────
    def _build_list_panel(self, parent):
        card, body = make_card(parent, title="Records")
        card.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 12))
        body.rowconfigure(1, weight=1)   # table row expands
        body.columnconfigure(0, weight=1)
        body.configure(padx=0, pady=0)

        # ── Toolbar ──────────────────────────────────────────────────────────
        toolbar = tk.Frame(body, bg=COLORS["surface"])
        toolbar.grid(row=0, column=0, sticky=tk.EW,
                     padx=DIMS["card_pad"], pady=(DIMS["card_pad"], 8))

        tk.Label(toolbar, text="Filter by model:",
                 font=FONTS["label_bold"], bg=COLORS["surface"],
                 fg=COLORS["text_secondary"]).pack(side=tk.LEFT)

        self._filter_var = tk.StringVar(value="All Models")
        filter_cb = ttk.Combobox(toolbar, textvariable=self._filter_var,
                                 values=self.MODELS, state="readonly",
                                 width=18, font=FONTS["body"])
        filter_cb.pack(side=tk.LEFT, padx=(8, 0))
        filter_cb.bind("<<ComboboxSelected>>", lambda _: self._apply_filter())

        ttk.Button(toolbar, text="↻  Refresh", style="Secondary.TButton",
                   command=self._load_data).pack(side=tk.LEFT, padx=(10, 0))

        self._count_lbl = tk.Label(toolbar, text="",
                                   font=FONTS["body_small"],
                                   bg=COLORS["surface"],
                                   fg=COLORS["text_muted"])
        self._count_lbl.pack(side=tk.RIGHT)

        # ── Table ─────────────────────────────────────────────────────────────
        cols = [
            ("model",     "Model",     110),
            ("result",    "Result",    120),
            ("timestamp", "Timestamp", 155),
            ("id",        "ID",         95),
        ]
        self._table = DataTable(body, columns=cols)
        self._table.grid(row=1, column=0, sticky=tk.NSEW, padx=0, pady=0)
        self._table.bind_select(self._on_row_select)

        # ── Pagination bar ────────────────────────────────────────────────────
        self._pagination_bar = tk.Frame(body, bg=COLORS["surface"])
        self._pagination_bar.grid(row=2, column=0, sticky=tk.EW,
                                  padx=DIMS["card_pad"],
                                  pady=(6, 0))

        self._prev_btn = ttk.Button(
            self._pagination_bar, text="◀  Prev",
            style="Secondary.TButton", command=self._go_prev,
        )
        self._prev_btn.pack(side=tk.LEFT)

        self._page_lbl = tk.Label(
            self._pagination_bar, text="",
            font=FONTS["body_small"], bg=COLORS["surface"],
            fg=COLORS["text_secondary"],
        )
        self._page_lbl.pack(side=tk.LEFT, padx=12)

        self._next_btn = ttk.Button(
            self._pagination_bar, text="Next  ▶",
            style="Secondary.TButton", command=self._go_next,
        )
        self._next_btn.pack(side=tk.LEFT)

        self._range_lbl = tk.Label(
            self._pagination_bar, text="",
            font=FONTS["body_small"], bg=COLORS["surface"],
            fg=COLORS["text_muted"],
        )
        self._range_lbl.pack(side=tk.RIGHT)

        # Hide pagination until there is more than one page of data
        self._pagination_bar.grid_remove()

        # ── Action bar ────────────────────────────────────────────────────────
        action_bar = tk.Frame(body, bg=COLORS["surface"])
        action_bar.grid(row=3, column=0, sticky=tk.EW,
                        padx=DIMS["card_pad"], pady=DIMS["inner_pad"])

        self._delete_btn = ttk.Button(
            action_bar, text="🗑  Delete Selected",
            style="Danger.TButton", command=self._on_delete,
            state="disabled",
        )
        self._delete_btn.pack(side=tk.LEFT)

        # Clear All History — PLACEHOLDER
        self._clear_btn = ttk.Button(
            action_bar,
            text="  🚫  Clear All History",
            style="ComingSoon.TButton",
            command=self._on_clear_all_placeholder,
        )
        self._clear_btn.pack(side=tk.LEFT, padx=(8, 0))

        tk.Label(
            action_bar,
            text=" COMING SOON ",
            font=FONTS["badge"],
            bg=COLORS["warning_bg"],
            fg=COLORS["warning"],
            padx=4, pady=2,
        ).pack(side=tk.LEFT, padx=(4, 0))

    # ── Right panel: record detail ───────────────────────────────────────────────
    def _build_detail_panel(self, parent):
        card, body = make_card(parent, title="")   # we build our own header below
        card.grid(row=0, column=1, sticky=tk.NSEW)
        body.configure(padx=0, pady=0)
        body.rowconfigure(1, weight=1)
        body.columnconfigure(0, weight=1)

        # ── Custom header: title on left, ✕ close button on right ────────────
        header = tk.Frame(body, bg=COLORS["surface"])
        header.grid(row=0, column=0, sticky=tk.EW,
                    padx=DIMS["card_pad"], pady=(DIMS["card_pad"], 4))

        tk.Label(
            header, text="Record Detail",
            font=FONTS["heading3"], bg=COLORS["surface"],
            fg=COLORS["text_primary"],
        ).pack(side=tk.LEFT)

        close_btn = tk.Label(
            header, text="  ✕  ",
            font=FONTS["body_bold"],
            bg=COLORS["surface"],
            fg=COLORS["text_muted"],
            cursor="hand2",
        )
        close_btn.pack(side=tk.RIGHT)
        close_btn.bind("<Button-1>", lambda _e: self._on_close_detail())
        close_btn.bind("<Enter>",
                       lambda _e: close_btn.configure(fg=COLORS["danger"],
                                                      bg=COLORS["danger_bg"]))
        close_btn.bind("<Leave>",
                       lambda _e: close_btn.configure(fg=COLORS["text_muted"],
                                                      bg=COLORS["surface"]))

        hline(body).grid(row=0, column=0, sticky=tk.EW)

        # ── Scrollable content area ───────────────────────────────────────────
        content_area = tk.Frame(body, bg=COLORS["surface"])
        content_area.grid(row=1, column=0, sticky=tk.NSEW)
        content_area.rowconfigure(0, weight=1)
        content_area.columnconfigure(0, weight=1)

        # Placeholder (default state)
        self._detail_placeholder = tk.Frame(content_area, bg=COLORS["surface"])
        self._detail_placeholder.place(relx=0, rely=0, relwidth=1, relheight=1)

        tk.Label(
            self._detail_placeholder,
            text="←  Select a record",
            font=FONTS["body"], bg=COLORS["surface"],
            fg=COLORS["text_muted"],
        ).pack(pady=60)

        # Detail content (stacked on top of placeholder, hidden until needed)
        self._detail_content = tk.Frame(content_area, bg=COLORS["surface"])

        detail_inner = tk.Frame(self._detail_content, bg=COLORS["surface"])
        detail_inner.pack(fill=tk.BOTH, expand=True,
                          padx=DIMS["card_pad"], pady=DIMS["inner_pad"])
        detail_inner.columnconfigure(1, weight=1)

        def meta_row(label, attr, row):
            tk.Label(detail_inner, text=label, font=FONTS["label_bold"],
                     bg=COLORS["surface"], fg=COLORS["text_muted"],
                     width=12, anchor=tk.W).grid(
                row=row, column=0, sticky=tk.W, pady=3)
            lbl = tk.Label(detail_inner, text="",
                           font=FONTS["body"], bg=COLORS["surface"],
                           fg=COLORS["text_primary"], anchor=tk.W)
            lbl.grid(row=row, column=1, sticky=tk.W, padx=(8, 0))
            setattr(self, attr, lbl)

        meta_row("Record ID",  "_d_id",     0)
        meta_row("Model",      "_d_model",  1)
        meta_row("Result",     "_d_result", 2)
        meta_row("Timestamp",  "_d_time",   3)

        hline(detail_inner).grid(row=4, column=0, columnspan=2,
                                 sticky=tk.EW, pady=10)

        tk.Label(detail_inner, text="Feature Vector",
                 font=FONTS["label_bold"], bg=COLORS["surface"],
                 fg=COLORS["text_muted"]).grid(
            row=5, column=0, columnspan=2, sticky=tk.W, pady=(0, 4))

        self._fv_text = tk.Text(
            detail_inner, height=14,
            font=FONTS["mono"],
            bg=COLORS["surface_alt"],
            fg=COLORS["text_secondary"],
            relief=tk.FLAT, padx=8, pady=6,
            state=tk.DISABLED, wrap=tk.NONE,
        )
        self._fv_text.grid(row=6, column=0, columnspan=2, sticky=tk.EW)

    # ── Data loading ─────────────────────────────────────────────────────────────
    def _load_data(self):
        self._filter_var.set("All Models")
        try:
            response = self.controller.getAllPredictions()
        except Exception as exc:
            self.notify(f"Failed to load history: {exc}", kind="error")
            return

        if response.get("status")[0] == "success":
            self._all_records = response["message"] or []
            self._apply_filter()          # will also reset page and render
            self.notify(
                f"Loaded {len(self._all_records)} prediction record(s).",
                kind="info",
            )
        else:
            self.notify(response.get("message", "Error loading history."), kind="error")

    def _apply_filter(self):
        model_filter = self._filter_var.get()
        if model_filter == "All Models":
            self._filtered_records = list(self._all_records)
        else:
            self._filtered_records = [
                r for r in self._all_records
                if r.get("modelName") == model_filter
            ]
        self._current_page = 0
        self._render_current_page()

    # ── Pagination helpers ───────────────────────────────────────────────────────
    def _total_pages(self) -> int:
        total = len(self._filtered_records)
        return max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

    def _page_records(self) -> list[dict]:
        """Return the slice of filtered records for the current page."""
        start = self._current_page * PAGE_SIZE
        return self._filtered_records[start: start + PAGE_SIZE]

    def _go_prev(self):
        if self._current_page > 0:
            self._current_page -= 1
            self._hide_detail()
            self._render_current_page()

    def _go_next(self):
        if self._current_page < self._total_pages() - 1:
            self._current_page += 1
            self._hide_detail()
            self._render_current_page()

    def _update_pagination_controls(self):
        total_pages = self._total_pages()
        total_records = len(self._filtered_records)
        page = self._current_page

        # Show pagination bar only when there is more than one page
        if total_pages > 1:
            self._pagination_bar.grid()
        else:
            self._pagination_bar.grid_remove()

        # Button states
        self._prev_btn.configure(
            state="normal" if page > 0 else "disabled")
        self._next_btn.configure(
            state="normal" if page < total_pages - 1 else "disabled")

        # Page label: "Page 1 of 3"
        self._page_lbl.configure(
            text=f"Page {page + 1} of {total_pages}")

        # Range label: "showing 1 – 500 of 1 243"
        start = page * PAGE_SIZE + 1
        end   = min((page + 1) * PAGE_SIZE, total_records)
        self._range_lbl.configure(
            text=f"Showing {start}–{end} of {total_records}")

    # ── Table rendering ──────────────────────────────────────────────────────────
    def _render_current_page(self):
        records = self._page_records()

        self._table.clear()
        self._hide_detail()

        for rec in records:
            is_positive = rec.get("isMalignant", False)
            result_text = "Positive  ⚠" if is_positive else "Negative  ✓"
            tag = "positive" if is_positive else "negative"

            self._table.insert_row((
                rec.get("modelName", "—"),
                result_text,
                fmt_timestamp(rec.get("timeStamp", "")),
                fmt_uuid_short(rec.get("Id", "")),
            ), tags=(tag,))

        self._table.tree.tag_configure("positive", foreground=COLORS["danger"])
        self._table.tree.tag_configure("negative", foreground=COLORS["success"])

        # Update count label and pagination controls
        total = len(self._filtered_records)
        self._count_lbl.configure(
            text=f"{total} record{'s' if total != 1 else ''}")
        self._update_pagination_controls()

    # ── Row selection & detail panel ─────────────────────────────────────────────
    def _on_row_select(self, values: tuple):
        """Called by DataTable when a row is clicked."""
        short_id = values[3].rstrip("…") if values else ""
        record = next(
            (r for r in self._all_records
             if r.get("Id", "").startswith(short_id)),
            None,
        )
        if record:
            self._show_detail(record)
            self._delete_btn.configure(state="normal")

    def _show_detail(self, record: dict):
        """Populate and raise the detail panel."""
        self._detail_placeholder.lower()
        self._detail_content.place(relx=0, rely=0, relwidth=1, relheight=1)

        is_positive = record.get("isMalignant", False)
        self._d_id.configure(text=record.get("Id", "—"))
        self._d_model.configure(text=record.get("modelName", "—"))
        self._d_result.configure(
            text="Positive ⚠" if is_positive else "Negative ✓",
            fg=COLORS["danger"] if is_positive else COLORS["success"],
        )
        self._d_time.configure(text=fmt_timestamp(record.get("timeStamp", "")))

        fv_text = fmt_feature_vector(record.get("featureVector", {}))
        self._fv_text.configure(state=tk.NORMAL)
        self._fv_text.delete("1.0", tk.END)
        self._fv_text.insert("1.0", fv_text)
        self._fv_text.configure(state=tk.DISABLED)

    def _hide_detail(self):
        """Lower the detail panel, restore placeholder, disable delete button."""
        self._detail_content.place_forget()
        self._detail_placeholder.lift()
        self._delete_btn.configure(state="disabled")

    def _on_close_detail(self):
        """
        Called by the ✕ close button.
        Hides the detail panel AND clears the table selection so nothing
        appears selected and the Delete button goes back to disabled.
        """
        # Deselect all rows in the Treeview
        self._table.tree.selection_remove(self._table.tree.selection())
        self._hide_detail()

    # ── Actions ──────────────────────────────────────────────────────────────────
    def _on_delete(self):
        vals = self._table.selected_values()
        if not vals:
            return

        short_id = vals[3].rstrip("…")
        record = next(
            (r for r in self._all_records if r.get("Id", "").startswith(short_id)),
            None,
        )
        if not record:
            self.notify("Could not find selected record.", kind="error")
            return

        full_id = record["Id"]
        confirmed = messagebox.askyesno(
            "Confirm Delete",
            f"Delete this prediction record?\n\nID: {full_id}",
            parent=self,
        )
        if not confirmed:
            return

        try:
            response = self.controller.deletePrediction(full_id)
        except Exception as exc:
            self.notify(f"Delete failed: {exc}", kind="error")
            return

        if response.get("status")[0] == "success":
            deleted = response.get("message", False)
            if deleted:
                # Remove from both master list and filtered list
                self._all_records = [
                    r for r in self._all_records if r.get("Id") != full_id]
                self._apply_filter()    # re-filters, resets page, re-renders
                self._hide_detail()
                self.notify("Record deleted successfully.", kind="success")
            else:
                self.notify("Record not found in database.", kind="warning")
        else:
            self.notify(response.get("message", "Delete failed."), kind="error")

    def _on_clear_all_placeholder(self):
        """
        Placeholder — replace the body of this method once
        clearAllHistory() is implemented in the controller.
        """
        messagebox.showinfo(
            "Coming Soon",
            "Clear All History is not yet available.\n\n"
            "This button will be activated once the corresponding\n"
            "API endpoint is implemented in the controller.",
            parent=self,
        )