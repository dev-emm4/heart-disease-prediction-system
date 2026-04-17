"""
components/feature_form.py
──────────────────────────
Reusable patient-feature input form.

• Dropdowns for every categorical feature (correct UCI / UCL dataset values)
• Numeric Entry for continuous features
• Groups inputs under clinical section headers for readability
• Disables sex & fbs automatically when the SVM model is selected
• get_values() → dict[str, float]  (raises ValueError on invalid input)
• clear()  → resets all fields

Usage:
    form = FeatureForm(parent)
    form.pack(fill=tk.BOTH, expand=True)
    form.set_model("SVM")        # disables sex & fbs
    values = form.get_values()   # returns feature dict
"""

import tkinter as tk
from tkinter import ttk
from UI.theme import COLORS, FONTS, DIMS


# ── Feature catalogue ────────────────────────────────────────────────────────────
# Each entry: (feature_key, display_label, unit_hint, widget_type, options_or_None)
# widget_type: "entry" | "combo"
# options: list of (display_string, numeric_value) for combo boxes

_FEATURES = [
    # ── Section: Patient Demographics ────────────────────────────────────────
    ("__section__", "Patient Demographics", None, None, None),
    (
        "age",
        "Age",
        "years",
        "entry",
        None,
    ),
    (
        "sex",
        "Sex",
        "",
        "combo",
        [("Female", 0), ("Male", 1)],
    ),

    # ── Section: Cardiac Symptoms ─────────────────────────────────────────────
    ("__section__", "Cardiac Symptoms", None, None, None),
    (
        "cp",
        "Chest Pain Type",
        "",
        "combo",
        [
            ("1 — Typical Angina",    1),
            ("2 — Atypical Angina",   2),
            ("3 — Non-Anginal Pain",  3),
            ("4 — Asymptomatic",      4),
        ],
    ),
    (
        "exang",
        "Exercise-Induced Angina",
        "",
        "combo",
        [("No", 0), ("Yes", 1)],
    ),

    # ── Section: Blood Measurements ───────────────────────────────────────────
    ("__section__", "Blood Measurements", None, None, None),
    (
        "trestbps",
        "Resting Blood Pressure",
        "mm Hg",
        "entry",
        None,
    ),
    (
        "chol",
        "Serum Cholesterol",
        "mg/dL",
        "entry",
        None,
    ),
    (
        "fbs",
        "Fasting Blood Sugar > 120 mg/dL",
        "",
        "combo",
        [("No  (≤ 120 mg/dL)", 0), ("Yes (> 120 mg/dL)", 1)],
    ),

    # ── Section: Cardiac Test Results ─────────────────────────────────────────
    ("__section__", "Cardiac Test Results", None, None, None),
    (
        "restecg",
        "Resting ECG Results",
        "",
        "combo",
        [
            ("0 — Normal",                       0),
            ("1 — ST-T Wave Abnormality",         1),
            ("2 — Left Ventricular Hypertrophy",  2),
        ],
    ),
    (
        "thalach",
        "Maximum Heart Rate Achieved",
        "bpm",
        "entry",
        None,
    ),
    (
        "oldpeak",
        "ST Depression (Exercise vs Rest)",
        "mm",
        "entry",
        None,
    ),
    (
        "slope",
        "Slope of Peak Exercise ST Segment",
        "",
        "combo",
        [
            ("1 — Upsloping",    1),
            ("2 — Flat",         2),
            ("3 — Downsloping",  3),
        ],
    ),
    (
        "ca",
        "Major Vessels (Fluoroscopy)",
        "0 – 3",
        "combo",
        [(str(i), i) for i in range(4)],
    ),
    (
        "thal",
        "Thalassemia",
        "",
        "combo",
        [
            ("3 — Normal",           3),
            ("6 — Fixed Defect",     6),
            ("7 — Reversable Defect", 7),
        ],
    ),
]

# Features unused by SVM (will be disabled when that model is selected)
_SVM_DISABLED = {"sex", "fbs"}


class FeatureForm(tk.Frame):
    """13-field patient feature input panel."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["surface"], **kwargs)

        # Stores widget references: key → (var, widget, label_widget)
        self._fields: dict[str, tuple] = {}
        # Maps combo display strings → numeric values: key → {display: value}
        self._option_maps: dict[str, dict] = {}

        self._build()

    # ── Construction ────────────────────────────────────────────────────────────
    def _build(self):
        # Scrollable canvas for the form
        canvas = tk.Canvas(self, bg=COLORS["surface"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        inner = tk.Frame(canvas, bg=COLORS["surface"])
        canvas_window = canvas.create_window((0, 0), window=inner, anchor=tk.NW)

        def _on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=event.width)

        inner.bind("<Configure>", _on_configure)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))

        # Mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # ── Render fields ─────────────────────────────────────────────────────
        pad = DIMS["card_pad"]
        row = 0

        for item in _FEATURES:
            key, label_text, hint, widget_type, options = item

            if key == "__section__":
                # Section header
                self._add_section_header(inner, label_text, row)
                row += 1
                continue

            label_var, input_widget, label_w = self._add_field(
                inner, row, key, label_text, hint, widget_type, options, pad
            )
            self._fields[key] = (label_var, input_widget, label_w)
            row += 1

        # Bottom padding
        tk.Frame(inner, bg=COLORS["surface"], height=16).grid(row=row, column=0)

    def _add_section_header(self, parent, text: str, row: int):
        """Render a coloured section divider."""
        frame = tk.Frame(parent, bg=COLORS["surface"])
        frame.grid(row=row, column=0, columnspan=3, sticky=tk.EW,
                   padx=DIMS["card_pad"], pady=(DIMS["section_gap"], 4))

        tk.Label(
            frame,
            text=text.upper(),
            font=FONTS["label_bold"],
            bg=COLORS["surface"],
            fg=COLORS["primary"],
        ).pack(side=tk.LEFT, padx=(0, 8))

        sep = tk.Frame(frame, bg=COLORS["border"], height=1)
        sep.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=6)

    def _add_field(self, parent, row, key, label_text, hint, widget_type, options, pad):
        """Render one label + input field row; return (var, widget, label_w)."""
        container = tk.Frame(parent, bg=COLORS["surface"])
        container.grid(row=row, column=0, sticky=tk.EW, padx=pad, pady=3)
        container.columnconfigure(1, weight=1)

        # Label
        full_label = f"{label_text}"
        if hint:
            full_label += f"  ({hint})"

        lbl = tk.Label(
            container,
            text=full_label,
            font=FONTS["label"],
            bg=COLORS["surface"],
            fg=COLORS["text_secondary"],
            anchor=tk.W,
            width=DIMS["label_width"],
        )
        lbl.grid(row=0, column=0, sticky=tk.W, padx=(0, 12))

        var = tk.StringVar()

        if widget_type == "combo":
            display_strings = [o[0] for o in options]
            self._option_maps[key] = {o[0]: o[1] for o in options}

            widget = ttk.Combobox(
                container,
                textvariable=var,
                values=display_strings,
                state="readonly",
                width=DIMS["field_width"],
                font=FONTS["body"],
            )
            widget.grid(row=0, column=1, sticky=tk.EW)

        else:  # entry
            widget = ttk.Entry(
                container,
                textvariable=var,
                width=DIMS["field_width"] + 2,
                font=FONTS["body"],
            )
            widget.grid(row=0, column=1, sticky=tk.EW)

        return var, widget, lbl

    # ── Public API ──────────────────────────────────────────────────────────────
    def set_model(self, model_name: str):
        """
        Adapt form to the selected model.
        SVM does not use sex or fbs — those fields are disabled and greyed out.
        """
        svm_mode = (model_name == "SVM")
        for key in _SVM_DISABLED:
            if key not in self._fields:
                continue
            _, widget, lbl = self._fields[key]
            state = "disabled" if svm_mode else "readonly"
            fg = COLORS["text_muted"] if svm_mode else COLORS["text_secondary"]
            try:
                widget.configure(state=state)
            except tk.TclError:
                pass
            lbl.configure(fg=fg)

    def get_values(self) -> dict[str, float]:
        """
        Read and validate all enabled inputs.
        Returns a dict suitable for featureJson.
        Raises ValueError with a descriptive message on bad input.
        """
        result = {}
        for key, (var, widget, _lbl) in self._fields.items():
            # Skip disabled fields (e.g. sex / fbs for SVM)
            try:
                state = str(widget.cget("state"))
            except tk.TclError:
                state = "normal"
            if state == "disabled":
                continue

            raw = var.get().strip()

            # Combo boxes: map display string → numeric value
            if key in self._option_maps:
                if not raw:
                    raise ValueError(f"Please select a value for '{self._label_for(key)}'.")
                mapped = self._option_maps[key].get(raw)
                if mapped is None:
                    raise ValueError(f"Unrecognised option for '{self._label_for(key)}': {raw}")
                result[key] = float(mapped)
            else:
                # Numeric entry
                if not raw:
                    raise ValueError(f"'{self._label_for(key)}' is required.")
                try:
                    result[key] = float(raw)
                except ValueError:
                    raise ValueError(f"'{self._label_for(key)}' must be a number, got: '{raw}'")

        return result

    def clear(self):
        """Reset every field to its default (empty / unselected)."""
        for _, (var, widget, _) in self._fields.items():
            var.set("")

    def _label_for(self, key: str) -> str:
        """Return the human label for a feature key."""
        for item in _FEATURES:
            if item[0] == key:
                return item[1]
        return key
