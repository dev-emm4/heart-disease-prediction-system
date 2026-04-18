"""
components/nav_sidebar.py
──────────────────────────
Left-hand navigation sidebar.

Usage:
    sidebar = NavSidebar(parent, items=[("key", "Label"), ...], on_select=callback)
    sidebar.pack(side=tk.LEFT, fill=tk.Y)
    sidebar.set_active("key")
"""

import tkinter as tk
from ui.theme import COLORS, FONTS, DIMS


class NavSidebar(tk.Frame):
    """Dark sidebar with logo, navigation buttons, and a footer."""

    def __init__(self, parent, items: list[tuple[str, str]], on_select):
        super().__init__(parent, bg=COLORS["sidebar_bg"], width=DIMS["sidebar_width"])
        self.pack_propagate(False)          # Hold fixed width
        self.on_select = on_select
        self._buttons: dict[str, _NavButton] = {}
        self._active_key: str | None = None

        self._build(items)

    # ── Construction ────────────────────────────────────────────────────────────
    def _build(self, items):
        # ── Logo / brand ─────────────────────────────────────────────────────
        logo_frame = tk.Frame(self, bg=COLORS["sidebar_bg"])
        logo_frame.pack(fill=tk.X, pady=(24, 4), padx=20)

        tk.Label(
            logo_frame,
            text="♥  CardioAI",
            font=FONTS["app_title"],
            bg=COLORS["sidebar_bg"],
            fg=COLORS["sidebar_accent"],
        ).pack(anchor=tk.W)

        tk.Label(
            logo_frame,
            text="Heart Disease Prediction",
            font=FONTS["body_small"],
            bg=COLORS["sidebar_bg"],
            fg=COLORS["sidebar_section_text"],
        ).pack(anchor=tk.W)

        # ── Separator ────────────────────────────────────────────────────────
        _HRule(self, COLORS["sidebar_separator"]).pack(fill=tk.X, padx=16, pady=(14, 10))

        # ── Section label ────────────────────────────────────────────────────
        tk.Label(
            self,
            text="NAVIGATION",
            font=FONTS["label_bold"],
            bg=COLORS["sidebar_bg"],
            fg=COLORS["sidebar_section_text"],
        ).pack(anchor=tk.W, padx=20, pady=(0, 6))

        # ── Nav buttons ──────────────────────────────────────────────────────
        nav_frame = tk.Frame(self, bg=COLORS["sidebar_bg"])
        nav_frame.pack(fill=tk.X, padx=8)

        for key, label in items:
            btn = _NavButton(nav_frame, key=key, label=label, on_click=self._handle_click)
            btn.pack(fill=tk.X, pady=1)
            self._buttons[key] = btn

        # ── Footer ───────────────────────────────────────────────────────────
        _HRule(self, COLORS["sidebar_separator"]).pack(fill=tk.X, padx=16, side=tk.BOTTOM, pady=(8, 0))
        tk.Label(
            self,
            text="v1.0  ·  UCI Heart Dataset",
            font=FONTS["body_small"],
            bg=COLORS["sidebar_bg"],
            fg=COLORS["sidebar_section_text"],
        ).pack(side=tk.BOTTOM, pady=(0, 12))

    # ── Public API ──────────────────────────────────────────────────────────────
    def set_active(self, key: str):
        if self._active_key:
            self._buttons[self._active_key].set_active(False)
        self._active_key = key
        self._buttons[key].set_active(True)

    # ── Internal ────────────────────────────────────────────────────────────────
    def _handle_click(self, key: str):
        self.set_active(key)
        self.on_select(key)


# ── Private helpers ──────────────────────────────────────────────────────────────

class _NavButton(tk.Frame):
    """A single navigation item with active / hover states."""

    def __init__(self, parent, key: str, label: str, on_click):
        super().__init__(parent, bg=COLORS["sidebar_bg"], cursor="hand2")
        self.key = key
        self.on_click = on_click
        self._active = False

        self.label_widget = tk.Label(
            self,
            text=label,
            font=FONTS["nav_item"],
            bg=COLORS["sidebar_bg"],
            fg=COLORS["sidebar_text"],
            anchor=tk.W,
            padx=14,
            pady=9,
        )
        self.label_widget.pack(fill=tk.X)

        # Bind events on both frame and label so the entire row is clickable
        for widget in (self, self.label_widget):
            widget.bind("<Button-1>", self._on_click)
            widget.bind("<Enter>",    self._on_enter)
            widget.bind("<Leave>",    self._on_leave)

    def set_active(self, active: bool):
        self._active = active
        bg = COLORS["sidebar_active_bg"] if active else COLORS["sidebar_bg"]
        fg = COLORS["sidebar_text_active"] if active else COLORS["sidebar_text"]
        font = FONTS["nav_active"] if active else FONTS["nav_item"]
        self.configure(bg=bg)
        self.label_widget.configure(bg=bg, fg=fg, font=font)

    def _on_click(self, _event):
        self.on_click(self.key)

    def _on_enter(self, _event):
        if not self._active:
            self.configure(bg=COLORS["sidebar_hover_bg"])
            self.label_widget.configure(bg=COLORS["sidebar_hover_bg"])

    def _on_leave(self, _event):
        if not self._active:
            self.configure(bg=COLORS["sidebar_bg"])
            self.label_widget.configure(bg=COLORS["sidebar_bg"])


class _HRule(tk.Frame):
    """1-pixel horizontal rule."""

    def __init__(self, parent, color: str):
        super().__init__(parent, bg=color, height=1)
