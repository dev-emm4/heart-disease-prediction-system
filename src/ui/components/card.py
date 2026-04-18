import tkinter as tk
from tkinter import ttk
from ui.theme import COLORS, FONTS, DIMS


def make_card(parent, title: str = "", subtitle: str = "") -> tuple[tk.Frame, tk.Frame]:
    card = tk.Frame(
        parent,
        bg=COLORS["surface"],
        highlightbackground=COLORS["border"],
        highlightthickness=1,
    )

    if title:
        header = tk.Frame(card, bg=COLORS["surface"])
        header.pack(fill=tk.X, padx=DIMS["card_pad"], pady=(DIMS["card_pad"], 4))

        tk.Label(
            header,
            text=title,
            font=FONTS["heading3"],
            bg=COLORS["surface"],
            fg=COLORS["text_primary"],
        ).pack(side=tk.LEFT)

        if subtitle:
            tk.Label(
                header,
                text=subtitle,
                font=FONTS["body_small"],
                bg=COLORS["surface"],
                fg=COLORS["text_muted"],
            ).pack(side=tk.LEFT, padx=(8, 0))

        hline(card).pack(fill=tk.X, padx=0)

    body = tk.Frame(card, bg=COLORS["surface"])
    body.pack(fill=tk.BOTH, expand=True, padx=DIMS["card_pad"], pady=DIMS["card_pad"])

    return card, body


def make_metric_card(parent, label: str, value: str, accent: str = "primary") -> tk.Frame:
    color = COLORS.get(accent, accent)

    card = tk.Frame(
        parent,
        bg=COLORS["surface"],
        highlightbackground=COLORS["border"],
        highlightthickness=1,
    )

    # Top colour stripe
    stripe = tk.Frame(card, bg=color, height=4)
    stripe.pack(fill=tk.X)

    inner = tk.Frame(card, bg=COLORS["surface"])
    inner.pack(padx=DIMS["card_pad"], pady=(10, 14))

    tk.Label(
        inner,
        text=value,
        font=FONTS["metric_value"],
        bg=COLORS["surface"],
        fg=color,
    ).pack(anchor=tk.W)

    tk.Label(
        inner,
        text=label,
        font=FONTS["metric_label"],
        bg=COLORS["surface"],
        fg=COLORS["text_muted"],
    ).pack(anchor=tk.W)

    return card


def make_badge(parent, text: str, bg: str, fg: str) -> tk.Label:
    """A small inline text badge."""
    return tk.Label(
        parent,
        text=f"  {text}  ",
        font=FONTS["badge"],
        bg=bg,
        fg=fg,
        padx=2,
        pady=1,
    )


def page_header(parent, title: str, subtitle: str = "") -> tk.Frame:
    """Top-of-page title block (placed above cards)."""
    frame = tk.Frame(parent, bg=COLORS["window_bg"])

    tk.Label(
        frame,
        text=title,
        font=FONTS["heading1"],
        bg=COLORS["window_bg"],
        fg=COLORS["text_primary"],
    ).pack(anchor=tk.W)

    if subtitle:
        tk.Label(
            frame,
            text=subtitle,
            font=FONTS["body"],
            bg=COLORS["window_bg"],
            fg=COLORS["text_secondary"],
        ).pack(anchor=tk.W, pady=(2, 0))

    return frame


def hline(parent) -> tk.Frame:
    return tk.Frame(parent, bg=COLORS["border"], height=1)


def make_button_row(parent) -> tk.Frame:
    return tk.Frame(parent, bg=COLORS["surface"])
