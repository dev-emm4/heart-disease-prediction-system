"""
components/status_bar.py
────────────────────────
Thin status bar docked at the bottom of the window.
Colour-codes messages: success (green), error (red), info (blue), warning (orange).

Usage:
    bar = StatusBar(parent)
    bar.pack(side=tk.BOTTOM, fill=tk.X)
    bar.notify("Prediction complete.", kind="success")
"""

import tkinter as tk
from ui.theme import COLORS, FONTS


# Map kind → (background, foreground)
_THEME = {
    "success": (COLORS["success_bg"],  COLORS["success_text"]),
    "error":   (COLORS["danger_bg"],   COLORS["danger_text"]),
    "warning": (COLORS["warning_bg"],  COLORS["warning"]),
    "info":    (COLORS["info_bg"],     COLORS["info"]),
    "idle":    (COLORS["window_bg"],   COLORS["text_muted"]),
}

_ICON = {
    "success": "✓",
    "error":   "✕",
    "warning": "⚠",
    "info":    "ℹ",
    "idle":    "●",
}


class StatusBar(tk.Frame):
    """Single-line status bar with auto-clear after a timeout."""

    def __init__(self, parent, auto_clear_ms: int = 6000):
        super().__init__(parent, height=28)
        self._auto_clear_ms = auto_clear_ms
        self._after_id = None

        self._var = tk.StringVar(value="  Ready")
        self._label = tk.Label(
            self,
            textvariable=self._var,
            font=FONTS["body_small"],
            anchor=tk.W,
            padx=12,
            pady=4,
        )
        self._label.pack(fill=tk.BOTH, expand=True)
        self._set_kind("idle")

    # ── Public API ──────────────────────────────────────────────────────────────
    def notify(self, message: str, kind: str = "info"):
        """
        Display a message.
        kind: 'success' | 'error' | 'warning' | 'info'
        """
        icon = _ICON.get(kind, "")
        self._var.set(f"  {icon}  {message}")
        self._set_kind(kind)

        # Cancel any pending auto-clear and schedule a new one
        if self._after_id:
            self.after_cancel(self._after_id)
        self._after_id = self.after(self._auto_clear_ms, self._clear)

    def clear(self):
        self._clear()

    # ── Internal ────────────────────────────────────────────────────────────────
    def _set_kind(self, kind: str):
        bg, fg = _THEME.get(kind, _THEME["idle"])
        self.configure(bg=bg)
        self._label.configure(bg=bg, fg=fg)

    def _clear(self):
        self._var.set("  Ready")
        self._set_kind("idle")
        self._after_id = None
