"""
views/single_prediction_view.py
────────────────────────────────
View: Single Patient Prediction

Layout
  LEFT  — Model selector card + feature input form
  RIGHT — Result card (updates after each prediction)

Controller methods used
  makePrediction(modelName, featureJson) → dict
"""

import tkinter as tk
from tkinter import ttk
from UI.theme import COLORS, FONTS, DIMS
from UI.components.feature_form import FeatureForm
from UI.components.card import make_card, page_header, hline, make_badge
from UI.utils.formatters import fmt_timestamp, fmt_result, fmt_feature_vector


class SinglePredictionView(tk.Frame):
    """Main view for predicting heart disease for a single patient."""

    MODELS = [
        ("NaiveBayes",   "Naïve Bayes",    "Probabilistic · 13 features"),
        ("SVM",          "SVM",            "Support Vector · 11 features"),
        ("DecisionTree", "Decision Tree",  "Decision Tree  · 13 features"),
    ]

    def __init__(self, parent, controller, notify):
        super().__init__(parent, bg=COLORS["window_bg"])
        self.controller = controller
        self.notify = notify
        self._selected_model = tk.StringVar(value="NaiveBayes")
        self._build()

    # ── Layout ──────────────────────────────────────────────────────────────────
    def _build(self):
        # Outer padding frame
        outer = tk.Frame(self, bg=COLORS["window_bg"])
        outer.pack(fill=tk.BOTH, expand=True, padx=24, pady=20)

        # ── Page header ──────────────────────────────────────────────────────
        page_header(outer, "Single Prediction",
                    "Enter patient data below to predict heart disease risk.").pack(
            anchor=tk.W, pady=(0, 16))

        # ── Two-column body: left form | right result ─────────────────────────
        body = tk.Frame(outer, bg=COLORS["window_bg"])
        body.pack(fill=tk.BOTH, expand=True)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        # Left column
        left = tk.Frame(body, bg=COLORS["window_bg"])
        left.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 12))
        left.rowconfigure(1, weight=1)

        self._build_model_selector(left)
        self._build_feature_panel(left)
        self._build_action_bar(left)

        # Right column
        right = tk.Frame(body, bg=COLORS["window_bg"])
        right.grid(row=0, column=1, sticky=tk.NSEW)
        right.rowconfigure(0, weight=1)
        self._build_result_panel(right)

    # ── Sub-panels ──────────────────────────────────────────────────────────────
    def _build_model_selector(self, parent):
        card, body = make_card(parent, title="ML Model")
        card.pack(fill=tk.X, pady=(0, 10))

        model_row = tk.Frame(body, bg=COLORS["surface"])
        model_row.pack(fill=tk.X)

        for key, name, desc in self.MODELS:
            col = tk.Frame(model_row, bg=COLORS["surface"])
            col.pack(side=tk.LEFT, padx=(0, 16))

            rb = tk.Radiobutton(
                col,
                text=name,
                value=key,
                variable=self._selected_model,
                command=self._on_model_change,
                font=FONTS["body_bold"],
                bg=COLORS["surface"],
                fg=COLORS["text_primary"],
                activebackground=COLORS["surface"],
                selectcolor=COLORS["primary_light"],
                indicatoron=True,
            )
            rb.pack(anchor=tk.W)

            tk.Label(
                col,
                text=desc,
                font=FONTS["body_small"],
                bg=COLORS["surface"],
                fg=COLORS["text_muted"],
            ).pack(anchor=tk.W, padx=(20, 0))

        # SVM note
        self._svm_note = tk.Label(
            body,
            text="ℹ  SVM does not use Sex or Fasting Blood Sugar — those fields are disabled.",
            font=FONTS["body_small"],
            bg=COLORS["info_bg"],
            fg=COLORS["info"],
            padx=8, pady=4,
        )

    def _build_feature_panel(self, parent):
        card, body = make_card(parent, title="Patient Features",
                               subtitle="All fields required unless model-disabled")
        card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        body.configure(padx=0, pady=0)   # FeatureForm handles its own padding

        self.feature_form = FeatureForm(body)
        self.feature_form.pack(fill=tk.BOTH, expand=True)

    def _build_action_bar(self, parent):
        bar = tk.Frame(parent, bg=COLORS["window_bg"])
        bar.pack(fill=tk.X, pady=(0, 4))

        self._predict_btn = ttk.Button(
            bar,
            text="  ▶   Run Prediction",
            style="Primary.TButton",
            command=self._on_predict,
        )
        self._predict_btn.pack(side=tk.LEFT)

        ttk.Button(
            bar,
            text="Clear Form",
            style="Secondary.TButton",
            command=self._on_clear,
        ).pack(side=tk.LEFT, padx=(8, 0))

    def _build_result_panel(self, parent):
        card, body = make_card(parent, title="Prediction Result")
        card.pack(fill=tk.BOTH, expand=True)

        # ── Placeholder shown before any prediction ───────────────────────────
        self._placeholder_frame = tk.Frame(body, bg=COLORS["surface"])
        self._placeholder_frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(
            self._placeholder_frame,
            text="🫀",
            font=("Segoe UI", 36),
            bg=COLORS["surface"],
            fg=COLORS["border"],
        ).pack(pady=(40, 8))
        tk.Label(
            self._placeholder_frame,
            text="No prediction yet",
            font=FONTS["heading3"],
            bg=COLORS["surface"],
            fg=COLORS["text_muted"],
        ).pack()
        tk.Label(
            self._placeholder_frame,
            text="Fill in the patient form\nand click  ▶  Run Prediction",
            font=FONTS["body_small"],
            bg=COLORS["surface"],
            fg=COLORS["text_muted"],
            justify=tk.CENTER,
        ).pack(pady=(4, 0))

        # ── Result content (hidden until prediction runs) ─────────────────────
        self._result_frame = tk.Frame(body, bg=COLORS["surface"])

        # Diagnosis banner
        self._diagnosis_banner = tk.Frame(self._result_frame, bg=COLORS["surface"])
        self._diagnosis_banner.pack(fill=tk.X, pady=(0, 12))

        self._diag_icon = tk.Label(
            self._diagnosis_banner, text="", font=("Segoe UI", 30),
            bg=COLORS["surface"],
        )
        self._diag_icon.pack(pady=(8, 2))

        self._diag_text = tk.Label(
            self._diagnosis_banner, text="",
            font=FONTS["heading2"], bg=COLORS["surface"],
        )
        self._diag_text.pack()

        self._diag_sub = tk.Label(
            self._diagnosis_banner, text="",
            font=FONTS["body_small"], bg=COLORS["surface"], fg=COLORS["text_muted"],
        )
        self._diag_sub.pack()

        hline(self._result_frame).pack(fill=tk.X, pady=8)

        # Meta info grid
        meta = tk.Frame(self._result_frame, bg=COLORS["surface"])
        meta.pack(fill=tk.X)
        meta.columnconfigure(1, weight=1)

        def meta_row(r, label, var_name):
            tk.Label(meta, text=label, font=FONTS["label_bold"],
                     bg=COLORS["surface"], fg=COLORS["text_muted"],
                     anchor=tk.W).grid(row=r, column=0, sticky=tk.W, pady=2)
            lbl = tk.Label(meta, text="", font=FONTS["body"],
                           bg=COLORS["surface"], fg=COLORS["text_primary"],
                           anchor=tk.W)
            lbl.grid(row=r, column=1, sticky=tk.W, padx=(8, 0))
            setattr(self, var_name, lbl)

        meta_row(0, "Model",     "_res_model")
        meta_row(1, "Record ID", "_res_id")
        meta_row(2, "Timestamp", "_res_time")

        hline(self._result_frame).pack(fill=tk.X, pady=8)

        # Feature summary
        tk.Label(
            self._result_frame, text="Feature Vector",
            font=FONTS["label_bold"], bg=COLORS["surface"], fg=COLORS["text_muted"],
        ).pack(anchor=tk.W)

        self._fv_text = tk.Text(
            self._result_frame,
            height=10,
            font=FONTS["mono"],
            bg=COLORS["surface_alt"],
            fg=COLORS["text_secondary"],
            relief=tk.FLAT,
            padx=8, pady=6,
            state=tk.DISABLED,
            wrap=tk.NONE,
        )
        self._fv_text.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

    # ── Event handlers ──────────────────────────────────────────────────────────
    def _on_model_change(self):
        model = self._selected_model.get()
        self.feature_form.set_model(model)

        # Show / hide SVM note
        if model == "SVM":
            self._svm_note.pack(fill=tk.X, pady=(8, 0))
        else:
            self._svm_note.pack_forget()

    def _on_predict(self):
        model = self._selected_model.get()

        # Validate form
        try:
            features = self.feature_form.get_values()
        except ValueError as exc:
            self.notify(str(exc), kind="error")
            return

        # Call controller
        self._predict_btn.configure(state="disabled", text="  ⏳  Running…")
        self.update_idletasks()

        try:
            response = self.controller.makePrediction(model, features)
        except Exception as exc:
            self.notify(f"Unexpected error: {exc}", kind="error")
            self._predict_btn.configure(state="normal", text="  ▶   Run Prediction")
            return
        finally:
            self._predict_btn.configure(state="normal", text="  ▶   Run Prediction")

        # Handle response
        if response.get("status") == "success":
            self._render_result(response["message"])
            self.notify("Prediction complete.", kind="success")
        else:
            self.notify(response.get("message", "Unknown error."), kind="error")

    def _on_clear(self):
        self.feature_form.clear()
        self._show_placeholder()

    # ── Result rendering ────────────────────────────────────────────────────────
    def _show_placeholder(self):
        self._result_frame.pack_forget()
        self._placeholder_frame.pack(fill=tk.BOTH, expand=True)

    def _render_result(self, data: dict):
        self._placeholder_frame.pack_forget()
        self._result_frame.pack(fill=tk.BOTH, expand=True)

        is_positive = data.get("isMalignant", False)

        if is_positive:
            self._diag_icon.configure(text="⚠", fg=COLORS["danger"])
            self._diag_text.configure(
                text="Heart Disease: POSITIVE",
                fg=COLORS["danger"],
            )
            self._diag_sub.configure(
                text="Indicators suggest disease may be present."
            )
            self._diagnosis_banner.configure(bg=COLORS["danger_bg"])
            self._diag_icon.configure(bg=COLORS["danger_bg"])
            self._diag_text.configure(bg=COLORS["danger_bg"])
            self._diag_sub.configure(bg=COLORS["danger_bg"])
        else:
            self._diag_icon.configure(text="✓", fg=COLORS["success"])
            self._diag_text.configure(
                text="Heart Disease: NEGATIVE",
                fg=COLORS["success"],
            )
            self._diag_sub.configure(
                text="No strong indicators of heart disease detected."
            )
            self._diagnosis_banner.configure(bg=COLORS["success_bg"])
            self._diag_icon.configure(bg=COLORS["success_bg"])
            self._diag_text.configure(bg=COLORS["success_bg"])
            self._diag_sub.configure(bg=COLORS["success_bg"])

        self._res_model.configure(text=data.get("modelName", "—"))
        self._res_id.configure(text=data.get("Id", "—"))
        self._res_time.configure(text=fmt_timestamp(data.get("timeStamp", "")))

        fv_text = fmt_feature_vector(data.get("featureVector", {}))
        self._fv_text.configure(state=tk.NORMAL)
        self._fv_text.delete("1.0", tk.END)
        self._fv_text.insert("1.0", fv_text)
        self._fv_text.configure(state=tk.DISABLED)
