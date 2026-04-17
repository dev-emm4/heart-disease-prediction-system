"""
theme.py
────────
Centralised design tokens for the CardioAI application.
Edit this file to restyle the entire UI in one place.
"""

# ── Colour Palette ──────────────────────────────────────────────────────────────
COLORS = {
    # ── Sidebar (dark navy) ──────────────────────────────────────────────────
    "sidebar_bg":           "#1A2535",
    "sidebar_active_bg":    "#1565C0",
    "sidebar_hover_bg":     "#243248",
    "sidebar_text":         "#90A4AE",
    "sidebar_text_active":  "#FFFFFF",
    "sidebar_accent":       "#42A5F5",
    "sidebar_separator":    "#253347",
    "sidebar_section_text": "#546E7A",

    # ── Main window / page ───────────────────────────────────────────────────
    "window_bg":            "#EDF1F7",

    # ── Cards / Surfaces ─────────────────────────────────────────────────────
    "surface":              "#FFFFFF",
    "surface_alt":          "#F7F9FC",
    "border":               "#DDE3ED",
    "border_strong":        "#B0BEC5",

    # ── Typography ───────────────────────────────────────────────────────────
    "text_primary":         "#1A2535",
    "text_secondary":       "#546E7A",
    "text_muted":           "#90A4AE",
    "text_on_dark":         "#FFFFFF",

    # ── Primary action ───────────────────────────────────────────────────────
    "primary":              "#1565C0",
    "primary_hover":        "#0D47A1",
    "primary_light":        "#E3F2FD",
    "primary_text":         "#FFFFFF",

    # ── Semantic ─────────────────────────────────────────────────────────────
    "success":              "#2E7D32",
    "success_bg":           "#E8F5E9",
    "success_border":       "#A5D6A7",
    "success_text":         "#1B5E20",

    "danger":               "#C62828",
    "danger_bg":            "#FFEBEE",
    "danger_border":        "#EF9A9A",
    "danger_text":          "#B71C1C",
    "danger_hover":         "#B71C1C",

    "warning":              "#E65100",
    "warning_bg":           "#FFF3E0",
    "warning_border":       "#FFCC80",

    "info":                 "#0277BD",
    "info_bg":              "#E1F5FE",
    "info_border":          "#81D4FA",

    # ── Inputs ───────────────────────────────────────────────────────────────
    "input_bg":             "#FFFFFF",
    "input_border":         "#B0BEC5",
    "input_focus_border":   "#1565C0",
    "input_disabled_bg":    "#ECEFF1",
    "input_disabled_text":  "#90A4AE",

    # ── Table (Treeview) ─────────────────────────────────────────────────────
    "table_header_bg":      "#EDF1F7",
    "table_header_fg":      "#37474F",
    "table_row_even":       "#FFFFFF",
    "table_row_odd":        "#F5F7FA",
    "table_select_bg":      "#BBDEFB",
    "table_select_fg":      "#0D47A1",

    # ── Misc ─────────────────────────────────────────────────────────────────
    "scrollbar":            "#CFD8DC",
    "divider":              "#ECEFF1",
}

# ── Fonts ────────────────────────────────────────────────────────────────────────
FONTS = {
    "app_title":        ("Segoe UI", 13, "bold"),
    "heading1":         ("Segoe UI", 17, "bold"),
    "heading2":         ("Segoe UI", 13, "bold"),
    "heading3":         ("Segoe UI", 11, "bold"),
    "subheading":       ("Segoe UI", 10, "bold"),
    "body":             ("Segoe UI", 10),
    "body_small":       ("Segoe UI", 9),
    "body_bold":        ("Segoe UI", 10, "bold"),
    "label":            ("Segoe UI", 9),
    "label_bold":       ("Segoe UI", 9, "bold"),
    "nav_item":         ("Segoe UI", 10),
    "nav_active":       ("Segoe UI", 10, "bold"),
    "metric_value":     ("Segoe UI", 26, "bold"),
    "metric_label":     ("Segoe UI", 9),
    "mono":             ("Consolas", 9),
    "badge":            ("Segoe UI", 8, "bold"),
}

# ── Dimensions ───────────────────────────────────────────────────────────────────
DIMS = {
    "sidebar_width":    228,
    "card_pad":         20,
    "inner_pad":        12,
    "widget_gap":       6,
    "btn_pad_x":        16,
    "btn_pad_y":        7,
    "field_width":      26,     # Entry widget width (chars)
    "label_width":      28,     # Label column width (chars)
    "section_gap":      14,     # Vertical gap between form sections
}
