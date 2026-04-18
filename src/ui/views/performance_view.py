import tkinter as tk
from tkinter import ttk, filedialog
from ui.theme import COLORS, FONTS, DIMS
from ui.components.card import make_card, page_header, hline
from ui.utils.validators import (
    validate_model, validate_csv_path,
    validate_column_indices, validate_target_column,
)
from ui.utils.formatters import fmt_percent


class PerformanceView(tk.Frame):
    """View for evaluating a model's accuracy, precision, and recall."""

    MODELS = ["NaiveBayes", "SVM", "DecisionTree"]

    def __init__(self, parent, controller, notify):
        super().__init__(parent, bg=COLORS["window_bg"])
        self.controller = controller
        self.notify = notify
        self._metric_value_labels: dict[str, tk.Label] = {}
        self._build()

    # ── Layout ──────────────────────────────────────────────────────────────────
    def _build(self):
        """
        Outer frame holds a Canvas + vertical scrollbar.
        All content lives inside an inner frame on the canvas so the user
        can scroll down to see everything without widgets overlapping.
        """
        outer = tk.Frame(self, bg=COLORS["window_bg"])
        outer.pack(fill=tk.BOTH, expand=True)
        outer.rowconfigure(0, weight=1)
        outer.columnconfigure(0, weight=1)

        # ── Scrollable canvas ─────────────────────────────────────────────────
        canvas = tk.Canvas(outer, bg=COLORS["window_bg"], highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        vsb.grid(row=0, column=1, sticky=tk.NS)
        canvas.grid(row=0, column=0, sticky=tk.NSEW)

        # Inner frame — all content goes here
        inner = tk.Frame(canvas, bg=COLORS["window_bg"])
        inner.columnconfigure(0, weight=1)

        canvas_win = canvas.create_window((0, 0), window=inner, anchor=tk.NW)

        def _on_inner_configure(_event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_win, width=event.width)

        inner.bind("<Configure>", _on_inner_configure)
        canvas.bind("<Configure>", _on_canvas_configure)

        # Mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # ── Build all sections inside inner ───────────────────────────────────
        content = tk.Frame(inner, bg=COLORS["window_bg"])
        content.pack(fill=tk.BOTH, expand=True, padx=24, pady=20)
        content.columnconfigure(0, weight=1)

        row = 0

        # ① Page header
        page_header(
            content,
            "Model Evaluation",
            "Measure accuracy, precision, and recall against a labelled dataset.",
        ).grid(row=row, column=0, sticky=tk.W, pady=(0, 16))
        row += 1

        # ② Config card
        self._build_config_card(content, row)
        row += 1

        # ③ Results card (hidden until evaluation runs)
        self._build_results_card(content, row)
        row += 1

        # ④ About card
        self._build_about_card(content, row)

    # ── ② Configuration card ────────────────────────────────────────────────────
    def _build_config_card(self, parent, grid_row: int):
        card, body = make_card(parent, title="Evaluation Setup")
        card.grid(row=grid_row, column=0, sticky=tk.EW, pady=(0, 12))
        body.columnconfigure(1, weight=1)

        def row_label(r, text):
            tk.Label(
                body, text=text, font=FONTS["label_bold"],
                bg=COLORS["surface"], fg=COLORS["text_secondary"],
            ).grid(row=r, column=0, sticky=tk.NW, pady=(0, 10))

        # CSV File
        row_label(0, "CSV File")
        file_row = tk.Frame(body, bg=COLORS["surface"])
        file_row.grid(row=0, column=1, sticky=tk.EW, padx=(12, 0), pady=(0, 10))
        file_row.columnconfigure(0, weight=1)
        self._file_var = tk.StringVar()
        ttk.Entry(file_row, textvariable=self._file_var,
                  font=FONTS["body"]).grid(row=0, column=0, sticky=tk.EW)
        ttk.Button(file_row, text="Browse…", style="Secondary.TButton",
                   command=self._browse).grid(row=0, column=1, padx=(6, 0))

        # Model
        row_label(1, "Model")
        self._model_var = tk.StringVar(value=self.MODELS[0])
        ttk.Combobox(
            body, textvariable=self._model_var, values=self.MODELS,
            state="readonly", width=24, font=FONTS["body"],
        ).grid(row=1, column=1, sticky=tk.W, padx=(12, 0), pady=(0, 10))

        # Drop columns
        row_label(2, "Drop Columns\n(0-based)")
        drop_frame = tk.Frame(body, bg=COLORS["surface"])
        drop_frame.grid(row=2, column=1, sticky=tk.EW, padx=(12, 0), pady=(0, 10))
        self._drop_var = tk.StringVar(value="13")
        ttk.Entry(drop_frame, textvariable=self._drop_var, width=30,
                  font=FONTS["body"]).pack(side=tk.LEFT)
        tk.Label(
            drop_frame, text="  Column indices to exclude from feature input",
            font=FONTS["body_small"], bg=COLORS["surface"],
            fg=COLORS["text_muted"],
        ).pack(side=tk.LEFT)

        # Target column
        row_label(3, "Target Column\n(0-based index)")
        target_frame = tk.Frame(body, bg=COLORS["surface"])
        target_frame.grid(row=3, column=1, sticky=tk.EW, padx=(12, 0), pady=(0, 10))
        self._target_var = tk.StringVar(value="13")
        ttk.Entry(target_frame, textvariable=self._target_var, width=10,
                  font=FONTS["body"]).pack(side=tk.LEFT)
        tk.Label(
            target_frame,
            text="  Column containing true labels (0 = no disease, 1 = disease)",
            font=FONTS["body_small"], bg=COLORS["surface"],
            fg=COLORS["text_muted"],
        ).pack(side=tk.LEFT)

        hline(body).grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=(4, 12))

        # Evaluate button
        self._eval_btn = ttk.Button(
            body, text="  📊   Evaluate Model",
            style="Primary.TButton", command=self._on_evaluate,
        )
        self._eval_btn.grid(row=5, column=0, columnspan=2, sticky=tk.W)

    # ── ③ Results card ───────────────────────────────────────────────────────────
    def _build_results_card(self, parent, grid_row: int):
        """
        Three KPI metric cards inside a named card.
        Hidden by default; revealed (grid()) after a successful evaluation.
        """
        card, body = make_card(parent, title="Evaluation Results")
        card.grid(row=grid_row, column=0, sticky=tk.EW, pady=(0, 12))
        body.columnconfigure((0, 1, 2), weight=1)

        metrics = [
            ("accuracy",  "Accuracy",  "#1565C0"),   # blue
            ("precision", "Precision", "#2E7D32"),   # green
            ("recall",    "Recall",    "#E65100"),   # orange
        ]

        for col, (key, label, color) in enumerate(metrics):
            # Individual metric card
            metric_card = tk.Frame(
                body,
                bg=COLORS["surface"],
                highlightbackground=COLORS["border"],
                highlightthickness=1,
            )
            metric_card.grid(
                row=0, column=col, sticky=tk.NSEW,
                padx=(0 if col == 0 else 10, 0),
            )

            # Top colour stripe
            tk.Frame(metric_card, bg=color, height=4).pack(fill=tk.X)

            inner = tk.Frame(metric_card, bg=COLORS["surface"])
            inner.pack(padx=DIMS["card_pad"], pady=(10, 14), fill=tk.X)

            value_lbl = tk.Label(
                inner, text="—",
                font=FONTS["metric_value"],
                bg=COLORS["surface"],
                fg=color,
            )
            value_lbl.pack(anchor=tk.W)
            self._metric_value_labels[key] = value_lbl

            tk.Label(
                inner, text=label,
                font=FONTS["metric_label"],
                bg=COLORS["surface"],
                fg=COLORS["text_muted"],
            ).pack(anchor=tk.W)

        # Hide until evaluation runs
        card.grid_remove()
        self._results_card = card

    # ── ④ About card ─────────────────────────────────────────────────────────────
    def _build_about_card(self, parent, grid_row: int):
        card, body = make_card(parent, title="About These Metrics")
        card.grid(row=grid_row, column=0, sticky=tk.EW)

        rows = [
            ("Accuracy",
             "Proportion of all cases classified correctly.  "
             "(TP + TN) / (TP + TN + FP + FN)"),
            ("Precision",
             "Of all positive predictions, how many were actually correct.  "
             "TP / (TP + FP)"),
            ("Recall",
             "Of all actual positive cases, how many were correctly identified.  "
             "TP / (TP + FN)"),
        ]

        for i, (term, desc) in enumerate(rows):
            row_frame = tk.Frame(body, bg=COLORS["surface"])
            row_frame.pack(fill=tk.X, pady=(0 if i == 0 else 8, 0))

            tk.Label(
                row_frame, text=f"{term}:",
                font=FONTS["body_bold"], bg=COLORS["surface"],
                fg=COLORS["text_primary"], width=10, anchor=tk.W,
            ).pack(side=tk.LEFT)

            tk.Label(
                row_frame, text=desc,
                font=FONTS["body_small"], bg=COLORS["surface"],
                fg=COLORS["text_secondary"], anchor=tk.W,
                wraplength=640, justify=tk.LEFT,
            ).pack(side=tk.LEFT)

    # ── Handlers ────────────────────────────────────────────────────────────────
    def _browse(self):
        path = filedialog.askopenfilename(
            title="Select Labelled CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self._file_var.set(path)

    def _on_evaluate(self):
        ok, err = validate_csv_path(self._file_var.get())
        if not ok:
            self.notify(err, kind="error"); return

        ok, err = validate_model(self._model_var.get())
        if not ok:
            self.notify(err, kind="error"); return

        ok, drop_indices, err = validate_column_indices(
            self._drop_var.get(), "Drop columns")
        if not ok:
            self.notify(err, kind="error"); return

        ok, target_col, err = validate_target_column(self._target_var.get())
        if not ok:
            self.notify(err, kind="error"); return

        self._eval_btn.configure(state="disabled", text="  ⏳  Evaluating…")
        self.update_idletasks()

        try:
            response = self.controller.calculatePerformance(
                self._model_var.get(),
                self._file_var.get().strip(),
                drop_indices,
                target_col,
            )
        except Exception as exc:
            self.notify(f"Unexpected error: {exc}", kind="error")
            return
        finally:
            self._eval_btn.configure(state="normal", text="  📊   Evaluate Model")

        if response.get("status")[0] == "success":
            self._render_metrics(response["message"])
            self.notify("Evaluation complete.", kind="success")
        else:
            self.notify(response.get("message", "Unknown error."), kind="error")

    def _render_metrics(self, data: dict):
        for key in ("accuracy", "precision", "recall"):
            val = data.get(key)
            text = fmt_percent(val) if isinstance(val, (int, float)) else "—"
            self._metric_value_labels[key].configure(text=text)

        self._results_card.grid()