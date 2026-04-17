"""
views/bulk_prediction_view.py
──────────────────────────────
View: Bulk CSV Predictions

Layout
  Page header
  └── ttk.PanedWindow (vertical, draggable sash)
        ├── TOP PANE  — Configuration card
        └── BOT PANE  — Results card (two-column: table | detail panel)

The sash between the two panes can be dragged up/down so the user can
give as much or as little space to the results table as they need.

Controller methods used
  makeBulkPredictions(modelName, filePath, dropColumn) → dict
"""

import tkinter as tk
from tkinter import ttk, filedialog
from UI.theme import COLORS, FONTS, DIMS
from UI.components.card import make_card, page_header, hline
from UI.components.data_table import DataTable
from UI.utils.validators import validate_model, validate_csv_path, validate_column_indices
from UI.utils.formatters import fmt_timestamp, fmt_result, fmt_feature_vector


class BulkPredictionView(tk.Frame):
    """View for running predictions on an entire CSV dataset."""

    MODELS = ["NaiveBayes", "SVM", "DecisionTree"]

    # Minimum pixel heights for each pane so neither collapses entirely
    _CONFIG_MIN_H  = 180
    _RESULTS_MIN_H = 200

    def __init__(self, parent, controller, notify):
        super().__init__(parent, bg=COLORS["window_bg"])
        self.controller = controller
        self.notify = notify
        self._predictions: list = []
        self._build()

    # ── Top-level layout ────────────────────────────────────────────────────────
    def _build(self):
        outer = tk.Frame(self, bg=COLORS["window_bg"])
        outer.pack(fill=tk.BOTH, expand=True, padx=24, pady=20)
        outer.rowconfigure(1, weight=1)
        outer.columnconfigure(0, weight=1)

        # Page title
        page_header(
            outer,
            "Bulk Prediction",
            "Run predictions on multiple patients from a CSV file.",
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 12))

        # ── Draggable PanedWindow ─────────────────────────────────────────────
        # orient=VERTICAL means the sash runs horizontally and you drag it up/down
        self._paned = ttk.PanedWindow(outer, orient=tk.VERTICAL)
        self._paned.grid(row=1, column=0, sticky=tk.NSEW)

        # Apply sash styling so it is clearly visible / grabbable
        style = ttk.Style()
        style.configure(
            "Sash",
            sashthickness=6,
            sashpad=2,
            relief="flat",
            background=COLORS["border"],
        )

        # ── Top pane: config ──────────────────────────────────────────────────
        config_host = tk.Frame(self._paned, bg=COLORS["window_bg"])
        self._build_config_card(config_host)
        self._paned.add(config_host, weight=0)   # weight=0 → doesn't grab extra space

        # ── Bottom pane: results ──────────────────────────────────────────────
        results_host = tk.Frame(self._paned, bg=COLORS["window_bg"])
        results_host.rowconfigure(0, weight=1)
        results_host.columnconfigure(0, weight=1)
        self._build_results_card(results_host)
        self._paned.add(results_host, weight=1)  # weight=1 → absorbs all extra space

        # After the window is drawn, push the sash down so the results pane
        # gets roughly 65 % of the available height by default.
        self._paned.bind("<Map>", self._set_initial_sash, add="+")

    def _set_initial_sash(self, _event=None):
        """Position the sash once the widget has a real size."""
        self._paned.unbind("<Map>")          # run only once
        self.update_idletasks()
        total = self._paned.winfo_height()
        if total > 10:
            # Place sash so the config pane gets ~35 % of height
            sash_pos = max(self._CONFIG_MIN_H, int(total * 0.35))
            self._paned.sashpos(0, sash_pos)

    # ── Configuration card (top pane) ───────────────────────────────────────────
    def _build_config_card(self, parent):
        card, body = make_card(parent, title="Configuration")
        card.pack(fill=tk.BOTH, expand=True)
        body.columnconfigure(1, weight=1)

        # CSV File
        tk.Label(
            body, text="CSV File", font=FONTS["label_bold"],
            bg=COLORS["surface"], fg=COLORS["text_secondary"],
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 8))

        file_row = tk.Frame(body, bg=COLORS["surface"])
        file_row.grid(row=0, column=1, sticky=tk.EW, padx=(12, 0), pady=(0, 8))
        file_row.columnconfigure(0, weight=1)

        self._file_path_var = tk.StringVar()
        ttk.Entry(
            file_row, textvariable=self._file_path_var, font=FONTS["body"],
        ).grid(row=0, column=0, sticky=tk.EW)
        ttk.Button(
            file_row, text="Browse…", style="Secondary.TButton",
            command=self._browse_file,
        ).grid(row=0, column=1, padx=(6, 0))

        # Model
        tk.Label(
            body, text="Model", font=FONTS["label_bold"],
            bg=COLORS["surface"], fg=COLORS["text_secondary"],
        ).grid(row=1, column=0, sticky=tk.W, pady=(0, 8))

        self._model_var = tk.StringVar(value=self.MODELS[0])
        ttk.Combobox(
            body, textvariable=self._model_var, values=self.MODELS,
            state="readonly", width=24, font=FONTS["body"],
        ).grid(row=1, column=1, sticky=tk.W, padx=(12, 0), pady=(0, 8))

        # Drop columns
        tk.Label(
            body, text="Drop Columns\n(0-based indices)",
            font=FONTS["label_bold"], bg=COLORS["surface"],
            fg=COLORS["text_secondary"], justify=tk.LEFT,
        ).grid(row=2, column=0, sticky=tk.NW, pady=(0, 8))

        drop_frame = tk.Frame(body, bg=COLORS["surface"])
        drop_frame.grid(row=2, column=1, sticky=tk.EW, padx=(12, 0), pady=(0, 8))

        self._drop_col_var = tk.StringVar(value="13")
        ttk.Entry(
            drop_frame, textvariable=self._drop_col_var, width=30, font=FONTS["body"],
        ).pack(side=tk.LEFT)
        tk.Label(
            drop_frame,
            text="  e.g. 13  or  13, 14  — columns to exclude before feeding to the model",
            font=FONTS["body_small"], bg=COLORS["surface"], fg=COLORS["text_muted"],
        ).pack(side=tk.LEFT)

        hline(body).grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=(4, 12))

        # Action bar
        action_row = tk.Frame(body, bg=COLORS["surface"])
        action_row.grid(row=4, column=0, columnspan=2, sticky=tk.W)

        self._run_btn = ttk.Button(
            action_row, text="  ▶   Run Bulk Prediction",
            style="Primary.TButton", command=self._on_run,
        )
        self._run_btn.pack(side=tk.LEFT)

        ttk.Button(
            action_row, text="Clear Results",
            style="Secondary.TButton", command=self._clear_results,
        ).pack(side=tk.LEFT, padx=(8, 0))

        self._progress_lbl = tk.Label(
            action_row, text="", font=FONTS["body_small"],
            bg=COLORS["surface"], fg=COLORS["text_muted"],
        )
        self._progress_lbl.pack(side=tk.LEFT, padx=(12, 0))

    # ── Results card (bottom pane) ───────────────────────────────────────────────
    def _build_results_card(self, parent):
        """
        Fills the entire bottom pane.
        Two-column split inside:
          LEFT  (weight 3) — summary bar + predictions table
          RIGHT (weight 2) — feature vector detail panel
        """
        card, body = make_card(parent, title="Results")
        card.grid(row=0, column=0, sticky=tk.NSEW)
        body.configure(padx=0, pady=0)
        body.rowconfigure(0, weight=1)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)

        self._build_table_column(body)
        self._build_detail_column(body)

    # ── Left: summary + table ────────────────────────────────────────────────────
    def _build_table_column(self, parent):
        left = tk.Frame(parent, bg=COLORS["surface"])
        left.grid(row=0, column=0, sticky=tk.NSEW)
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        # Summary bar
        self._summary_bar = tk.Frame(left, bg=COLORS["surface"])
        self._summary_bar.grid(
            row=0, column=0, sticky=tk.EW,
            padx=DIMS["card_pad"], pady=(DIMS["inner_pad"], 6),
        )

        self._lbl_total    = self._summary_label("Total: —")
        self._lbl_positive = self._summary_label("Positive ⚠: —", COLORS["danger"])
        self._lbl_negative = self._summary_label("Negative ✓: —", COLORS["success"])

        tk.Label(
            self._summary_bar,
            text="Click a row to inspect its features  →",
            font=FONTS["body_small"], bg=COLORS["surface"], fg=COLORS["text_muted"],
        ).pack(side=tk.RIGHT)

        # Table
        table_frame = tk.Frame(left, bg=COLORS["surface"])
        table_frame.grid(row=1, column=0, sticky=tk.NSEW)
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        cols = [
            ("row",       "#",         44),
            ("model",     "Model",     118),
            ("result",    "Result",    130),
            ("timestamp", "Timestamp", 162),
            ("id",        "Record ID", 260),
        ]
        self._table = DataTable(table_frame, columns=cols)
        self._table.grid(row=0, column=0, sticky=tk.NSEW)
        self._table.bind_select(self._on_row_select)

    # ── Right: feature detail panel ──────────────────────────────────────────────
    def _build_detail_column(self, parent):
        # Vertical separator
        tk.Frame(parent, bg=COLORS["border"], width=1).grid(
            row=0, column=0, sticky=tk.NS,
        )

        right = tk.Frame(parent, bg=COLORS["surface"])
        right.grid(row=0, column=1, sticky=tk.NSEW)
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        # Panel header — title on the left, close button on the right
        panel_hdr = tk.Frame(right, bg=COLORS["surface"])
        panel_hdr.grid(row=0, column=0, sticky=tk.EW,
                       padx=DIMS["card_pad"], pady=(DIMS["inner_pad"], 4))

        tk.Label(
            panel_hdr, text="Prediction Detail",
            font=FONTS["heading3"], bg=COLORS["surface"], fg=COLORS["text_primary"],
        ).pack(side=tk.LEFT)

        # Close button — dismisses the detail panel back to the placeholder
        close_btn = tk.Label(
            panel_hdr, text="  ✕  ",
            font=FONTS["body_bold"],
            bg=COLORS["surface"],
            fg=COLORS["text_muted"],
            cursor="hand2",
        )
        close_btn.pack(side=tk.RIGHT)
        close_btn.bind("<Button-1>", lambda _e: self._hide_detail())
        close_btn.bind("<Enter>",
                       lambda _e: close_btn.configure(fg=COLORS["danger"],
                                                      bg=COLORS["danger_bg"]))
        close_btn.bind("<Leave>",
                       lambda _e: close_btn.configure(fg=COLORS["text_muted"],
                                                      bg=COLORS["surface"]))

        hline(right).grid(row=0, column=0, sticky=tk.EW)

        detail_body = tk.Frame(right, bg=COLORS["surface"])
        detail_body.grid(row=1, column=0, sticky=tk.NSEW,
                         padx=DIMS["card_pad"], pady=DIMS["inner_pad"])
        detail_body.columnconfigure(1, weight=1)

        # Placeholder
        self._detail_placeholder = tk.Frame(detail_body, bg=COLORS["surface"])
        self._detail_placeholder.grid(row=0, column=0, columnspan=2,
                                      sticky=tk.NSEW, pady=60)
        tk.Label(
            self._detail_placeholder,
            text="←  Select a prediction",
            font=FONTS["body"], bg=COLORS["surface"], fg=COLORS["text_muted"],
        ).pack()

        # Detail content
        self._detail_content = tk.Frame(detail_body, bg=COLORS["surface"])

        def _meta(r, label, attr):
            tk.Label(
                self._detail_content, text=label,
                font=FONTS["label_bold"], bg=COLORS["surface"],
                fg=COLORS["text_muted"], width=14, anchor=tk.W,
            ).grid(row=r, column=0, sticky=tk.W, pady=3)
            lbl = tk.Label(
                self._detail_content, text="",
                font=FONTS["body"], bg=COLORS["surface"],
                fg=COLORS["text_primary"], anchor=tk.W,
            )
            lbl.grid(row=r, column=1, sticky=tk.W, padx=(6, 0))
            setattr(self, attr, lbl)

        _meta(0, "Record ID",  "_d_id")
        _meta(1, "Model",      "_d_model")
        _meta(2, "Result",     "_d_result")
        _meta(3, "Timestamp",  "_d_time")

        hline(self._detail_content).grid(
            row=4, column=0, columnspan=2, sticky=tk.EW, pady=(8, 8),
        )

        tk.Label(
            self._detail_content, text="Feature Vector",
            font=FONTS["label_bold"], bg=COLORS["surface"], fg=COLORS["text_muted"],
        ).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(0, 4))

        self._fv_text = tk.Text(
            self._detail_content,
            height=14,
            font=FONTS["mono"],
            bg=COLORS["surface_alt"],
            fg=COLORS["text_secondary"],
            relief=tk.FLAT,
            padx=8, pady=6,
            state=tk.DISABLED,
            wrap=tk.NONE,
        )
        self._fv_text.grid(row=6, column=0, columnspan=2, sticky=tk.EW)

    # ── Summary label helper ─────────────────────────────────────────────────────
    def _summary_label(self, text: str, color: str = None) -> tk.Label:
        lbl = tk.Label(
            self._summary_bar, text=text,
            font=FONTS["body_bold"], bg=COLORS["surface"],
            fg=color or COLORS["text_secondary"],
        )
        lbl.pack(side=tk.LEFT, padx=(0, 20))
        return lbl

    # ── Event handlers ──────────────────────────────────────────────────────────
    def _browse_file(self):
        path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self._file_path_var.set(path)

    def _on_run(self):
        ok, err = validate_csv_path(self._file_path_var.get())
        if not ok:
            self.notify(err, kind="error"); return

        ok, err = validate_model(self._model_var.get())
        if not ok:
            self.notify(err, kind="error"); return

        ok, indices, err = validate_column_indices(self._drop_col_var.get(), "Drop columns")
        if not ok:
            self.notify(err, kind="error"); return

        self._run_btn.configure(state="disabled", text="  ⏳  Processing…")
        self._progress_lbl.configure(text="Running predictions…")
        self.update_idletasks()

        try:
            response = self.controller.makeBulkPredictions(
                self._model_var.get(),
                self._file_path_var.get().strip(),
                indices,
            )
        except Exception as exc:
            self.notify(f"Unexpected error: {exc}", kind="error")
            return
        finally:
            self._run_btn.configure(state="normal", text="  ▶   Run Bulk Prediction")
            self._progress_lbl.configure(text="")

        if response.get("status")[0] == "success":
            self._render_results(response["message"])
        else:
            self.notify(response.get("message", "Unknown error."), kind="error")

    def _on_row_select(self, values: tuple):
        """Called by DataTable when the user clicks a row."""
        full_id = values[4] if len(values) > 4 else ""
        record = next(
            (p for p in self._predictions if p.get("Id") == full_id),
            None,
        )
        if record:
            self._show_detail(record)

    def _show_detail(self, record: dict):
        self._detail_placeholder.grid_remove()
        self._detail_content.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)

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
        self._detail_content.grid_remove()
        self._detail_placeholder.grid(row=0, column=0, columnspan=2,
                                      sticky=tk.NSEW, pady=60)

    # ── Render & clear ───────────────────────────────────────────────────────────
    def _render_results(self, predictions: list):
        self._table.clear()
        self._hide_detail()
        self._predictions = predictions

        positive = sum(1 for p in predictions if p.get("isMalignant"))
        negative = len(predictions) - positive

        self._lbl_total.configure(text=f"Total: {len(predictions)}")
        self._lbl_positive.configure(text=f"Positive ⚠: {positive}")
        self._lbl_negative.configure(text=f"Negative ✓: {negative}")

        for i, pred in enumerate(predictions, start=1):
            result_text = fmt_result(pred.get("isMalignant", False))
            tag = "positive" if pred.get("isMalignant") else "negative"
            self._table.insert_row((
                i,
                pred.get("modelName", "—"),
                result_text,
                fmt_timestamp(pred.get("timeStamp", "")),
                pred.get("Id", "—"),
            ), tags=(tag,))

        self._table.tree.tag_configure("positive", foreground=COLORS["danger"])
        self._table.tree.tag_configure("negative", foreground=COLORS["success"])

        self.notify(
            f"Bulk prediction complete: {len(predictions)} records "
            f"({positive} positive, {negative} negative).",
            kind="success",
        )

    def _clear_results(self):
        self._table.clear()
        self._predictions = []
        self._hide_detail()
        for lbl, text in [
            (self._lbl_total,    "Total: —"),
            (self._lbl_positive, "Positive ⚠: —"),
            (self._lbl_negative, "Negative ✓: —"),
        ]:
            lbl.configure(text=text)