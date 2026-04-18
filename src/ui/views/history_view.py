"""
views/history_view.py
──────────────────────
View: Prediction History

Pagination strategy (memory-efficient)
───────────────────────────────────────
  Only the CURRENT PAGE of records is ever held in memory.
  The controller's getAllPaginatedPredictions(page, pageSize) returns:
    {
      "predictions":     list[dict],   ← records for this page only
      "predictionCount": int           ← total records in the database
    }
  The UI derives total pages from predictionCount and PAGE_SIZE.
  Navigating to a new page, changing the model filter, or refreshing
  all trigger a fresh controller call — nothing is cached client-side.

  NOTE: the model filter is applied server-side via the model filter
  combobox. When a specific model is selected the view calls
  getPredictionsByModel() instead so the total count reflects the
  filtered dataset.

Features
  • Server-side paginated loading (PAGE_SIZE = 500)
  • Filter by model (triggers fresh load, resets to page 1)
  • Click a row → feature-vector detail panel on the right
  • ✕ close button → collapses panel AND clears table selection
  • Delete a single record → reloads current page
  • Clear All History → calls deleteAllPrediction(), resets view
  • Detail panel is wider (weight=3) for better readability

Controller methods used
  getAllPaginatedPredictions(page: int, pageSize: int) → dict
    message: {"predictions": list, "predictionCount": int}

  getPredictionsByModel(modelName: str) → dict
    message: list[dict]   (used for filtered view)

  deletePrediction(predictionId: str) → dict
  deleteAllPrediction() → dict
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ui.theme import COLORS, FONTS, DIMS
from ui.components.card import make_card, page_header, hline
from ui.components.data_table import DataTable
from ui.utils.formatters import fmt_timestamp, fmt_uuid_short, fmt_feature_vector


PAGE_SIZE = 500   # records per page — change here to adjust globally


class HistoryView(tk.Frame):
    """Browse, inspect, and delete stored prediction records."""

    MODELS = ["All Models", "NaiveBayes", "SVM", "DecisionTree"]

    def __init__(self, parent, controller, notify):
        super().__init__(parent, bg=COLORS["window_bg"])
        self.controller = controller
        self.notify = notify

        # ── Pagination state ─────────────────────────────────────────────────
        # Only the current page's records are kept; nothing else is cached.
        self._current_page:  int        = 0      # 0-based
        self._total_count:   int        = 0      # total records (from server)
        self._page_records:  list[dict] = []     # records on the current page

        self._build()

    def on_show(self):
        """Auto-refresh every time this view becomes active."""
        self._reset_and_load()

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
        body.columnconfigure(0, weight=5)   # records list
        body.columnconfigure(1, weight=3)   # detail panel — wider than before

        self._build_list_panel(body)
        self._build_detail_panel(body)

    # ── Left panel ──────────────────────────────────────────────────────────────
    def _build_list_panel(self, parent):
        card, body = make_card(parent, title="Records")
        card.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 12))
        body.rowconfigure(1, weight=1)
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
        filter_cb.bind("<<ComboboxSelected>>", lambda _: self._on_filter_change())

        ttk.Button(toolbar, text="↻  Refresh", style="Secondary.TButton",
                   command=self._reset_and_load).pack(side=tk.LEFT, padx=(10, 0))

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
                                  padx=DIMS["card_pad"], pady=(6, 0))

        self._prev_btn = ttk.Button(
            self._pagination_bar, text="◀  Prev",
            style="Secondary.TButton", command=self._go_prev)
        self._prev_btn.pack(side=tk.LEFT)

        self._page_lbl = tk.Label(
            self._pagination_bar, text="",
            font=FONTS["body_small"], bg=COLORS["surface"],
            fg=COLORS["text_secondary"])
        self._page_lbl.pack(side=tk.LEFT, padx=12)

        self._next_btn = ttk.Button(
            self._pagination_bar, text="Next  ▶",
            style="Secondary.TButton", command=self._go_next)
        self._next_btn.pack(side=tk.LEFT)

        self._range_lbl = tk.Label(
            self._pagination_bar, text="",
            font=FONTS["body_small"], bg=COLORS["surface"],
            fg=COLORS["text_muted"])
        self._range_lbl.pack(side=tk.RIGHT)

        self._pagination_bar.grid_remove()   # hidden until data has >1 page

        # ── Action bar ────────────────────────────────────────────────────────
        action_bar = tk.Frame(body, bg=COLORS["surface"])
        action_bar.grid(row=3, column=0, sticky=tk.EW,
                        padx=DIMS["card_pad"], pady=DIMS["inner_pad"])

        self._delete_btn = ttk.Button(
            action_bar, text="🗑  Delete Selected",
            style="Danger.TButton", command=self._on_delete,
            state="disabled")
        self._delete_btn.pack(side=tk.LEFT)

        # Clear All — now wired to deleteAllPrediction()
        ttk.Button(
            action_bar,
            text="  🚫  Clear All History",
            style="Danger.TButton",
            command=self._on_clear_all,
        ).pack(side=tk.LEFT, padx=(8, 0))

    # ── Right panel: record detail ───────────────────────────────────────────────
    def _build_detail_panel(self, parent):
        card, body = make_card(parent, title="")
        card.grid(row=0, column=1, sticky=tk.NSEW)
        body.configure(padx=0, pady=0)
        body.rowconfigure(1, weight=1)
        body.columnconfigure(0, weight=1)

        # Header: title left, ✕ right
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
            bg=COLORS["surface"], fg=COLORS["text_muted"],
            cursor="hand2",
        )
        close_btn.pack(side=tk.RIGHT)
        close_btn.bind("<Button-1>", lambda _e: self._on_close_detail())
        close_btn.bind("<Enter>",
                       lambda _e: close_btn.configure(
                           fg=COLORS["danger"], bg=COLORS["danger_bg"]))
        close_btn.bind("<Leave>",
                       lambda _e: close_btn.configure(
                           fg=COLORS["text_muted"], bg=COLORS["surface"]))

        hline(body).grid(row=0, column=0, sticky=tk.EW)

        # Stacked content area
        content_area = tk.Frame(body, bg=COLORS["surface"])
        content_area.grid(row=1, column=0, sticky=tk.NSEW)
        content_area.rowconfigure(0, weight=1)
        content_area.columnconfigure(0, weight=1)

        # Placeholder
        self._detail_placeholder = tk.Frame(content_area, bg=COLORS["surface"])
        self._detail_placeholder.place(relx=0, rely=0, relwidth=1, relheight=1)
        tk.Label(
            self._detail_placeholder,
            text="←  Select a record",
            font=FONTS["body"], bg=COLORS["surface"],
            fg=COLORS["text_muted"],
        ).pack(pady=60)

        # Detail content
        self._detail_content = tk.Frame(content_area, bg=COLORS["surface"])

        detail_inner = tk.Frame(self._detail_content, bg=COLORS["surface"])
        detail_inner.pack(fill=tk.BOTH, expand=True,
                          padx=DIMS["card_pad"], pady=DIMS["inner_pad"])
        detail_inner.columnconfigure(1, weight=1)
        detail_inner.rowconfigure(6, weight=1)   # fv_frame row stretches vertically

        def meta_row(label, attr, row):
            tk.Label(detail_inner, text=label, font=FONTS["label_bold"],
                     bg=COLORS["surface"], fg=COLORS["text_muted"],
                     anchor=tk.W).grid(
                row=row, column=0, sticky=tk.W, pady=3, padx=(0, 8))
            lbl = tk.Label(detail_inner, text="",
                           font=FONTS["body"], bg=COLORS["surface"],
                           fg=COLORS["text_primary"], anchor=tk.W,
                           wraplength=1, justify=tk.LEFT)
            lbl.grid(row=row, column=1, sticky=tk.EW, padx=(0, 4))
            setattr(self, attr, lbl)

        meta_row("Record ID",  "_d_id",     0)
        meta_row("Model",      "_d_model",  1)
        meta_row("Result",     "_d_result", 2)
        meta_row("Timestamp",  "_d_time",   3)

        # When the detail panel is resized, update wraplength on value labels
        # so long text (e.g. full UUIDs) wraps cleanly instead of overflowing.
        def _update_wraplength(event):
            available = max(60, event.width - 120)   # subtract label column width
            for attr in ("_d_id", "_d_model", "_d_result", "_d_time"):
                widget = getattr(self, attr, None)
                if widget:
                    widget.configure(wraplength=available)

        detail_inner.bind("<Configure>", _update_wraplength)

        hline(detail_inner).grid(row=4, column=0, columnspan=2,
                                 sticky=tk.EW, pady=10)

        tk.Label(detail_inner, text="Feature Vector",
                 font=FONTS["label_bold"], bg=COLORS["surface"],
                 fg=COLORS["text_muted"]).grid(
            row=5, column=0, columnspan=2, sticky=tk.W, pady=(0, 4))

        # fv_frame: sticky=NSEW so it fills the row that has weight=1
        fv_frame = tk.Frame(detail_inner, bg=COLORS["surface_alt"])
        fv_frame.grid(row=6, column=0, columnspan=2, sticky=tk.NSEW, pady=(0, 4))
        fv_frame.columnconfigure(0, weight=1)
        fv_frame.rowconfigure(0, weight=1)   # text widget row stretches

        self._fv_text = tk.Text(
            fv_frame,
            font=FONTS["mono"],
            bg=COLORS["surface_alt"], fg=COLORS["text_secondary"],
            relief=tk.FLAT, padx=8, pady=6,
            state=tk.DISABLED, wrap=tk.NONE,
        )
        fv_vsb = ttk.Scrollbar(fv_frame, orient=tk.VERTICAL,
                               command=self._fv_text.yview)
        fv_hsb = ttk.Scrollbar(fv_frame, orient=tk.HORIZONTAL,
                               command=self._fv_text.xview)
        self._fv_text.configure(
            yscrollcommand=fv_vsb.set,
            xscrollcommand=fv_hsb.set,
        )
        self._fv_text.grid(row=0, column=0, sticky=tk.NSEW)
        fv_vsb.grid(row=0, column=1, sticky=tk.NS)
        fv_hsb.grid(row=1, column=0, sticky=tk.EW)

    # ── Data loading ─────────────────────────────────────────────────────────────
    def _reset_and_load(self):
        """Reset to page 0 and load from the server."""
        self._filter_var.set("All Models")
        self._current_page = 0
        self._fetch_page()

    def _on_filter_change(self):
        """Model filter changed — go back to page 0 and reload."""
        self._current_page = 0
        self._fetch_page()

    def _fetch_page(self):
        """
        Ask the controller for the current page.

        Both endpoints share the same response shape:
            {"predictions": list[dict], "predictionCount": int}

        The controller uses 1-based page numbers (page <= 0 returns an
        error), so we always pass self._current_page + 1.  Internal state
        remains 0-based throughout the UI.
        """
        model_filter   = self._filter_var.get()
        one_based_page = self._current_page + 1   # controller expects 1-based

        try:
            if model_filter == "All Models":
                # ── All predictions, paginated ────────────────────────────────
                response = self.controller.getAllPaginatedPredictions(
                    one_based_page,
                    PAGE_SIZE,
                )
            else:
                # ── Single-model predictions, paginated server-side ───────────
                response = self.controller.getPredictionsByNamePaginated(
                    model_filter,
                    one_based_page,
                    PAGE_SIZE,
                )

            if response.get("status")[0] != "success":
                self.notify(
                    response.get("message", "Error loading history."),
                    kind="error")
                return

            msg = response["message"]
            self._page_records = msg.get("predictions") or []
            self._total_count  = msg.get("predictionCount", 0)

        except Exception as exc:
            self.notify(f"Failed to load history: {exc}", kind="error")
            return

        self._render_table()

    # ── Pagination helpers ───────────────────────────────────────────────────────
    def _total_pages(self) -> int:
        return max(1, (self._total_count + PAGE_SIZE - 1) // PAGE_SIZE)

    def _go_prev(self):
        if self._current_page > 0:
            self._current_page -= 1
            self._hide_detail()
            self._fetch_page()

    def _go_next(self):
        if self._current_page < self._total_pages() - 1:
            self._current_page += 1
            self._hide_detail()
            self._fetch_page()

    def _update_pagination_controls(self):
        total_pages = self._total_pages()
        page        = self._current_page

        if total_pages > 1:
            self._pagination_bar.grid()
        else:
            self._pagination_bar.grid_remove()

        self._prev_btn.configure(
            state="normal" if page > 0 else "disabled")
        self._next_btn.configure(
            state="normal" if page < total_pages - 1 else "disabled")

        self._page_lbl.configure(
            text=f"Page {page + 1} of {total_pages}")

        start = page * PAGE_SIZE + 1
        end   = min((page + 1) * PAGE_SIZE, self._total_count)
        # Guard against 0-count edge case
        if self._total_count == 0:
            self._range_lbl.configure(text="No records")
        else:
            self._range_lbl.configure(
                text=f"Showing {start}–{end} of {self._total_count}")

    # ── Table rendering ──────────────────────────────────────────────────────────
    def _render_table(self):
        self._table.clear()
        self._hide_detail()

        for rec in self._page_records:
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

        self._count_lbl.configure(
            text=f"{self._total_count} "
                 f"record{'s' if self._total_count != 1 else ''}")
        self._update_pagination_controls()

    # ── Row selection & detail panel ─────────────────────────────────────────────
    def _on_row_select(self, values: tuple):
        short_id = values[3].rstrip("…") if values else ""
        record = next(
            (r for r in self._page_records
             if r.get("Id", "").startswith(short_id)),
            None,
        )
        if record:
            self._show_detail(record)
            self._delete_btn.configure(state="normal")

    def _show_detail(self, record: dict):
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
        self._detail_content.place_forget()
        self._detail_placeholder.lift()
        self._delete_btn.configure(state="disabled")

    def _on_close_detail(self):
        """✕ button — clear table selection and hide panel."""
        self._table.tree.selection_remove(self._table.tree.selection())
        self._hide_detail()

    # ── Actions ──────────────────────────────────────────────────────────────────
    def _on_delete(self):
        vals = self._table.selected_values()
        if not vals:
            return

        short_id = vals[3].rstrip("…")
        record = next(
            (r for r in self._page_records
             if r.get("Id", "").startswith(short_id)),
            None,
        )
        if not record:
            self.notify("Could not find selected record.", kind="error")
            return

        full_id = record["Id"]
        if not messagebox.askyesno(
            "Confirm Delete",
            f"Delete this prediction record?\n\nID: {full_id}",
            parent=self,
        ):
            return

        try:
            response = self.controller.deletePrediction(full_id)
        except Exception as exc:
            self.notify(f"Delete failed: {exc}", kind="error")
            return

        if response.get("status")[0] == "success":
            if response.get("message", False):
                # Decrement total and reload the current page so the table
                # reflects the removal without fetching the whole dataset.
                self._total_count = max(0, self._total_count - 1)
                # If this deletion emptied the current page, go back one page
                if (not self._page_records or
                        len(self._page_records) == 1) and self._current_page > 0:
                    self._current_page -= 1
                self._hide_detail()
                self._fetch_page()
                self.notify("Record deleted successfully.", kind="success")
            else:
                self.notify("Record not found in database.", kind="warning")
        else:
            self.notify(response.get("message", "Delete failed."), kind="error")

    def _on_clear_all(self):
        """
        Delete every prediction record via deleteAllPrediction().
        Shows a strong confirmation dialog before proceeding.
        """
        if self._total_count == 0:
            self.notify("There are no records to clear.", kind="info")
            return

        confirmed = messagebox.askyesno(
            "Clear All History",
            f"This will permanently delete ALL {self._total_count} prediction "
            f"record{'s' if self._total_count != 1 else ''}.\n\n"
            "This action cannot be undone.\n\n"
            "Are you sure you want to continue?",
            icon="warning",
            parent=self,
        )
        if not confirmed:
            return

        try:
            response = self.controller.deleteAllPrediction()
        except Exception as exc:
            self.notify(f"Clear all failed: {exc}", kind="error")
            return

        if response.get("status")[0] == "success":
            # Reset all pagination state and re-render the empty table
            self._current_page = 0
            self._total_count  = 0
            self._page_records = []
            self._render_table()
            self._hide_detail()
            self.notify("All prediction history cleared.", kind="success")
        else:
            self.notify(
                response.get("message", "Clear all failed."), kind="error")