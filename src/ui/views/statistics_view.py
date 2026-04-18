"""
views/statistics_view.py
─────────────────────────
View: Model Usage Statistics

Shows how many predictions each model has made via metric cards
plus a simple canvas-drawn horizontal bar chart.

Controller methods used
  getStatistics() → dict
"""

import tkinter as tk
from tkinter import ttk, font as tkfont
from ui.theme import COLORS, FONTS, DIMS
from ui.components.card import make_card, make_metric_card, page_header, hline


# Accent colour per model
_MODEL_COLORS = {
    "NaiveBayes":   COLORS["primary"],
    "SVM":          COLORS["success"],
    "DecisionTree": COLORS["warning"],
}
_MODEL_DISPLAY = {
    "NaiveBayes":   "Naïve Bayes",
    "SVM":          "SVM",
    "DecisionTree": "Decision Tree",
}


class StatisticsView(tk.Frame):
    """Usage dashboard showing per-model prediction counts."""

    def __init__(self, parent, controller, notify):
        super().__init__(parent, bg=COLORS["window_bg"])
        self.controller = controller
        self.notify = notify
        self._build()

    def on_show(self):
        """Auto-refresh when this view becomes active."""
        self._load()

    # ── Layout ──────────────────────────────────────────────────────────────────
    def _build(self):
        outer = tk.Frame(self, bg=COLORS["window_bg"])
        outer.pack(fill=tk.BOTH, expand=True, padx=24, pady=20)
        outer.rowconfigure(2, weight=1)
        outer.columnconfigure(0, weight=1)

        # Header row with refresh button
        hdr_row = tk.Frame(outer, bg=COLORS["window_bg"])
        hdr_row.grid(row=0, column=0, sticky=tk.EW, pady=(0, 16))
        hdr_row.columnconfigure(0, weight=1)

        page_header(hdr_row, "Statistics",
                    "Prediction usage breakdown across all models.").grid(
            row=0, column=0, sticky=tk.W)

        ttk.Button(hdr_row, text="↻  Refresh", style="Secondary.TButton",
                   command=self._load).grid(row=0, column=1, sticky=tk.E)

        # ── KPI cards row ─────────────────────────────────────────────────────
        self._kpi_row = tk.Frame(outer, bg=COLORS["window_bg"])
        self._kpi_row.grid(row=1, column=0, sticky=tk.EW, pady=(0, 12))
        for i in range(4):
            self._kpi_row.columnconfigure(i, weight=1)

        # We build the 4 KPI cards (Total + 3 models) and store label refs
        self._kpi_labels: dict[str, tk.Label] = {}
        self._kpi_cards = {}

        specs = [
            ("total",        "Total Predictions", "primary"),
            ("NaiveBayes",   "Naïve Bayes",       "primary"),
            ("SVM",          "SVM",               "success"),
            ("DecisionTree", "Decision Tree",     "warning"),
        ]
        for col, (key, label, accent) in enumerate(specs):
            card = make_metric_card(self._kpi_row, label=label, value="—",
                                    accent=accent)
            card.grid(row=0, column=col, sticky=tk.NSEW,
                      padx=(0 if col == 0 else 10, 0))
            # grab the value label from inside the card
            inner = card.winfo_children()[1]
            value_lbl = inner.winfo_children()[0]
            self._kpi_labels[key] = value_lbl

        # ── Bar chart card ────────────────────────────────────────────────────
        chart_card, chart_body = make_card(
            outer, title="Predictions per Model",
            subtitle="Proportional usage breakdown")
        chart_card.grid(row=2, column=0, sticky=tk.NSEW)

        self._chart_canvas = tk.Canvas(
            chart_body,
            bg=COLORS["surface"],
            highlightthickness=0,
            height=220,
        )
        self._chart_canvas.pack(fill=tk.BOTH, expand=True)
        self._chart_canvas.bind("<Configure>", lambda _: self._redraw_chart())

        # ── Empty state notice ────────────────────────────────────────────────
        self._empty_label = tk.Label(
            chart_body,
            text="No predictions recorded yet.\nRun a prediction to see statistics here.",
            font=FONTS["body"],
            bg=COLORS["surface"],
            fg=COLORS["text_muted"],
            justify=tk.CENTER,
        )

        self._stats_data: dict = {}

    # ── Data loading ─────────────────────────────────────────────────────────────
    def _load(self):
        try:
            response = self.controller.getStatistics()
        except Exception as exc:
            self.notify(f"Failed to load statistics: {exc}", kind="error")
            return

        if response.get("status")[0] == "success":
            msg = response["message"]
            stat = msg.get("stat", {})
            total = msg.get("totalCount", 0)
            self._update_display(stat, total)
            self.notify("Statistics refreshed.", kind="info")
        else:
            self.notify(response.get("message", "Error loading statistics."), kind="error")

    def _update_display(self, stat: dict, total: int):
        self._stats_data = stat

        # Update KPI cards
        self._kpi_labels["total"].configure(text=str(total))
        for model in ("NaiveBayes", "SVM", "DecisionTree"):
            self._kpi_labels[model].configure(text=str(stat.get(model, 0)))

        if total == 0:
            self._chart_canvas.pack_forget()
            self._empty_label.pack(pady=40)
        else:
            self._empty_label.pack_forget()
            self._chart_canvas.pack(fill=tk.BOTH, expand=True)
            self._redraw_chart()

    # ── Chart drawing ─────────────────────────────────────────────────────────────
    def _redraw_chart(self):
        """Draw horizontal bar chart on the canvas."""
        c = self._chart_canvas
        c.delete("all")

        if not self._stats_data:
            return

        cw = c.winfo_width()
        ch = c.winfo_height()
        if cw < 10 or ch < 10:
            return

        total  = sum(self._stats_data.values()) or 1
        models = [m for m in ("NaiveBayes", "SVM", "DecisionTree")
                  if m in self._stats_data]

        # ── Measure real text widths so nothing ever gets clipped ─────────────
        # Build tk Font objects from our theme tuples so we can call .measure()
        font_bold   = tkfont.Font(family=FONTS["body_bold"][0],
                                  size=FONTS["body_bold"][1],
                                  weight="bold")
        font_body   = tkfont.Font(family=FONTS["body"][0],
                                  size=FONTS["body"][1])

        # Widest left label (model name)
        pad_left = max(
            font_bold.measure(_MODEL_DISPLAY.get(m, m)) for m in models
        ) + 16   # 16px gap between label and bar

        # Widest right label  e.g. "1 025  (43.6%)"
        right_labels = []
        for m in models:
            count = self._stats_data.get(m, 0)
            ratio = count / total
            right_labels.append(f"{count}  ({ratio * 100:.1f}%)")

        pad_right = max(font_body.measure(t) for t in right_labels) + 16

        pad_top    = 20
        bar_h      = 36
        bar_gap    = 22
        bar_area_w = max(40, cw - pad_left - pad_right)

        for i, (model, right_text) in enumerate(zip(models, right_labels)):
            count = self._stats_data.get(model, 0)
            ratio = count / total
            bar_w = max(4, int(bar_area_w * ratio))

            y_top    = pad_top + i * (bar_h + bar_gap)
            y_bottom = y_top + bar_h
            y_mid    = (y_top + y_bottom) // 2
            x_left   = pad_left
            x_right  = x_left + bar_w

            color = _MODEL_COLORS.get(model, COLORS["primary"])

            # Background track
            c.create_rectangle(
                x_left, y_top, x_left + bar_area_w, y_bottom,
                fill=COLORS["window_bg"], outline="", width=0,
            )
            # Filled bar
            c.create_rectangle(
                x_left, y_top, x_right, y_bottom,
                fill=color, outline="", width=0,
            )

            # Model label — right-aligned flush to the start of the bar
            c.create_text(
                x_left - 10, y_mid,
                text=_MODEL_DISPLAY.get(model, model),
                anchor=tk.E,
                font=FONTS["body_bold"],
                fill=COLORS["text_primary"],
            )

            # Count + percentage — left-aligned just past the end of the track
            c.create_text(
                x_left + bar_area_w + 10, y_mid,
                text=right_text,
                anchor=tk.W,
                font=FONTS["body"],
                fill=COLORS["text_secondary"],
            )