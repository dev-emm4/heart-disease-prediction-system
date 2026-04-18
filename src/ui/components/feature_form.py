import tkinter as tk
from tkinter import ttk
from ui.theme import COLORS, FONTS, DIMS


# ── Feature catalogue ────────────────────────────────────────────────────────────
_FEATURES = [
    # ── Patient Demographics ─────────────────────────────────────────────────
    ("__section__", "Patient Demographics", None, None, None),
    ("age",  "Age",  "years", "entry", None),
    ("sex",  "Sex",  "",      "combo", [("Female", 0), ("Male", 1)]),

    # ── Cardiac Symptoms ──────────────────────────────────────────────────────
    ("__section__", "Cardiac Symptoms", None, None, None),
    ("cp", "Chest Pain Type", "", "combo", [
        ("1 — Typical Angina",   1),
        ("2 — Atypical Angina",  2),
        ("3 — Non-Anginal Pain", 3),
        ("4 — Asymptomatic",     4),
    ]),
    ("exang", "Exercise-Induced Angina", "", "combo",
     [("No", 0), ("Yes", 1)]),

    # ── Blood Measurements ────────────────────────────────────────────────────
    ("__section__", "Blood Measurements", None, None, None),
    ("trestbps", "Resting Blood Pressure", "mm Hg", "entry", None),
    ("chol",     "Serum Cholesterol",      "mg/dL", "entry", None),
    ("fbs", "Fasting Blood Sugar > 120 mg/dL", "", "combo",
     [("No  (≤ 120 mg/dL)", 0), ("Yes (> 120 mg/dL)", 1)]),

    # ── Cardiac Test Results ──────────────────────────────────────────────────
    ("__section__", "Cardiac Test Results", None, None, None),
    ("restecg", "Resting ECG Results", "", "combo", [
        ("0 — Normal",                      0),
        ("1 — ST-T Wave Abnormality",        1),
        ("2 — Left Ventricular Hypertrophy", 2),
    ]),
    ("thalach", "Maximum Heart Rate Achieved", "bpm", "entry", None),
    ("oldpeak", "ST Depression (Exercise vs Rest)", "mm", "entry", None),
    ("slope", "Slope of Peak Exercise ST Segment", "", "combo", [
        ("1 — Upsloping",   1),
        ("2 — Flat",        2),
        ("3 — Downsloping", 3),
    ]),
    ("ca",   "Major Vessels (Fluoroscopy)", "0 – 3", "combo",
     [(str(i), i) for i in range(4)]),
    ("thal", "Thalassemia", "", "combo", [
        ("3 — Normal",            3),
        ("6 — Fixed Defect",      6),
        ("7 — Reversable Defect", 7),
    ]),
]

_SVM_DISABLED = {"sex", "fbs"}

_KEY_SCROLL_UNITS = 2


class FeatureForm(tk.Frame):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["surface"], **kwargs)
        self._fields: dict[str, tuple] = {}
        self._option_maps: dict[str, dict] = {}
        self._canvas: tk.Canvas | None = None   
        self._inner: tk.Frame | None = None     
        self._field_row_count: int = 0
        self._build()

    # ── Construction ────────────────────────────────────────────────────────────
    def _build(self):
        canvas = tk.Canvas(self, bg=COLORS["surface"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        inner = tk.Frame(canvas, bg=COLORS["surface"])
        canvas_window = canvas.create_window((0, 0), window=inner, anchor=tk.NW)

        def _on_configure(_event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_resize(event):
            canvas.itemconfig(canvas_window, width=event.width)

        inner.bind("<Configure>", _on_configure)
        canvas.bind("<Configure>", _on_canvas_resize)

        self._wheel_bind_id:  str | None = None
        self._up_bind_id:     str | None = None
        self._down_bind_id:   str | None = None

        def _scroll_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _scroll_up(_event):
            canvas.yview_scroll(-_KEY_SCROLL_UNITS, "units")

        def _scroll_down(_event):
            canvas.yview_scroll(_KEY_SCROLL_UNITS, "units")

        def _activate_scroll(_event=None):
            canvas.focus_set()
            if self._wheel_bind_id is None:
                self._wheel_bind_id = canvas.bind_all(
                    "<MouseWheel>", _scroll_wheel)
            if self._up_bind_id is None:
                self._up_bind_id = canvas.bind("<Up>", _scroll_up)
            if self._down_bind_id is None:
                self._down_bind_id = canvas.bind("<Down>", _scroll_down)

        def _deactivate_scroll(_event=None):
            if self._wheel_bind_id is not None:
                canvas.unbind_all("<MouseWheel>")
                self._wheel_bind_id = None
            if self._up_bind_id is not None:
                canvas.unbind("<Up>")
                self._up_bind_id = None
            if self._down_bind_id is not None:
                canvas.unbind("<Down>")
                self._down_bind_id = None

        canvas.bind("<Enter>",   _activate_scroll)
        canvas.bind("<Leave>",   _deactivate_scroll)
        canvas.bind("<Button-1>", _activate_scroll)

        inner.bind("<Enter>",    _activate_scroll)
        inner.bind("<Button-1>", _activate_scroll)

        self._canvas           = canvas
        self._inner            = inner
        self._activate_scroll  = _activate_scroll
        self._deactivate_scroll = _deactivate_scroll

        # ── Render feature fields ─────────────────────────────────────────────
        row = 0
        for item in _FEATURES:
            key, label_text, hint, widget_type, options = item

            if key == "__section__":
                self._add_section_header(inner, label_text, row)
                row += 1
                continue

            label_var, input_widget, label_w = self._add_field(
                inner, row, key, label_text, hint, widget_type, options)
            self._fields[key] = (label_var, input_widget, label_w)
            row += 1

        self._field_row_count = row

        tk.Frame(inner, bg=COLORS["surface"], height=8).grid(
            row=row, column=0)
        row += 1
        self._action_bar_row = row   

        tk.Frame(inner, bg=COLORS["surface"], height=16).grid(
            row=row + 1, column=0)

    def _add_section_header(self, parent: tk.Frame, text: str, row: int):
        frame = tk.Frame(parent, bg=COLORS["surface"])
        frame.grid(row=row, column=0, columnspan=3, sticky=tk.EW,
                   padx=DIMS["card_pad"], pady=(DIMS["section_gap"], 4))

        tk.Label(
            frame, text=text.upper(),
            font=FONTS["label_bold"], bg=COLORS["surface"],
            fg=COLORS["primary"],
        ).pack(side=tk.LEFT, padx=(0, 8))

        tk.Frame(frame, bg=COLORS["border"], height=1).pack(
            side=tk.LEFT, fill=tk.X, expand=True, pady=6)

    def _add_field(self, parent, row, key, label_text, hint, widget_type, options):
        pad = DIMS["card_pad"]
        container = tk.Frame(parent, bg=COLORS["surface"])
        container.grid(row=row, column=0, sticky=tk.EW, padx=pad, pady=3)
        container.columnconfigure(1, weight=1)

        full_label = label_text + (f"  ({hint})" if hint else "")

        lbl = tk.Label(
            container, text=full_label,
            font=FONTS["label"], bg=COLORS["surface"],
            fg=COLORS["text_secondary"], anchor=tk.W,
            width=DIMS["label_width"],
        )
        lbl.grid(row=0, column=0, sticky=tk.W, padx=(0, 12))

        var = tk.StringVar()

        if widget_type == "combo":
            display_strings = [o[0] for o in options]
            self._option_maps[key] = {o[0]: o[1] for o in options}
            widget = ttk.Combobox(
                container, textvariable=var,
                values=display_strings, state="readonly",
                width=DIMS["field_width"], font=FONTS["body"],
            )
            widget.grid(row=0, column=1, sticky=tk.EW)
        else:
            widget = ttk.Entry(
                container, textvariable=var,
                width=DIMS["field_width"] + 2, font=FONTS["body"],
            )
            widget.grid(row=0, column=1, sticky=tk.EW)

        widget.bind("<Enter>",    self._activate_scroll)
        widget.bind("<Button-1>", self._activate_scroll)

        return var, widget, lbl

    # ── Public API ──────────────────────────────────────────────────────────────
    def inject_action_bar(self, build_fn) -> tk.Frame:
        bar = tk.Frame(self._inner, bg=COLORS["surface"])
        bar.grid(row=self._action_bar_row, column=0,
                 sticky=tk.EW, padx=DIMS["card_pad"], pady=(4, 0))
        build_fn(bar)
        # Update scroll region now that content height has changed
        self._inner.update_idletasks()
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        return bar

    def set_model(self, model_name: str):
        svm_mode = (model_name == "SVM")
        for key in _SVM_DISABLED:
            if key not in self._fields:
                continue
            _, widget, lbl = self._fields[key]
            state = "disabled" if svm_mode else "readonly"
            fg    = COLORS["text_muted"] if svm_mode else COLORS["text_secondary"]
            try:
                widget.configure(state=state)
            except tk.TclError:
                pass
            lbl.configure(fg=fg)

    def get_values(self) -> dict[str, float]:
        result = {}
        for key, (var, widget, _lbl) in self._fields.items():
            try:
                state = str(widget.cget("state"))
            except tk.TclError:
                state = "normal"
            if state == "disabled":
                continue

            raw = var.get().strip()

            if key in self._option_maps:
                if not raw:
                    raise ValueError(
                        f"Please select a value for '{self._label_for(key)}'.")
                mapped = self._option_maps[key].get(raw)
                if mapped is None:
                    raise ValueError(
                        f"Unrecognised option for '{self._label_for(key)}': {raw}")
                result[key] = float(mapped)
            else:
                if not raw:
                    raise ValueError(f"'{self._label_for(key)}' is required.")
                try:
                    result[key] = float(raw)
                except ValueError:
                    raise ValueError(
                        f"'{self._label_for(key)}' must be a number, got: '{raw}'")

        return result

    def clear(self):
        for _, (var, _widget, _) in self._fields.items():
            var.set("")

    def scroll_to_top(self):
        self._canvas.yview_moveto(0)

    def _label_for(self, key: str) -> str:
        for item in _FEATURES:
            if item[0] == key:
                return item[1]
        return key