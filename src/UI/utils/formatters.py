"""
utils/formatters.py
───────────────────
Display-formatting helpers: dates, UUIDs, feature vectors, etc.
"""

from datetime import datetime


# ── Feature display names ────────────────────────────────────────────────────────
FEATURE_LABELS = {
    "age":      "Age (yrs)",
    "sex":      "Sex",
    "cp":       "Chest Pain",
    "trestbps": "Blood Pressure",
    "chol":     "Cholesterol",
    "fbs":      "Fasting Blood Sugar",
    "restecg":  "Resting ECG",
    "thalach":  "Max Heart Rate",
    "exang":    "Exercise Angina",
    "oldpeak":  "ST Depression",
    "slope":    "ST Slope",
    "ca":       "Major Vessels",
    "thal":     "Thalassemia",
}


def fmt_timestamp(ts: str) -> str:
    """'2026-04-17T10:30:00.000000'  →  'Apr 17, 2026  10:30'"""
    try:
        dt = datetime.fromisoformat(ts)
        return dt.strftime("%b %d, %Y  %H:%M")
    except (ValueError, TypeError):
        return ts or "—"


def fmt_uuid_short(uuid_str: str, chars: int = 8) -> str:
    """Show only the first N characters of a UUID for compact display."""
    return (uuid_str or "")[:chars] + "…"


def fmt_result(is_malignant: bool) -> str:
    return "Positive  ⚠" if is_malignant else "Negative  ✓"


def fmt_percent(value: float) -> str:
    return f"{value :.2f}%"


def fmt_feature_vector(fv: dict) -> str:
    """Return a multi-line string of feature: value pairs."""
    lines = []
    for key, val in fv.items():
        label = FEATURE_LABELS.get(key, key)
        lines.append(f"  {label:<22} {val}")
    return "\n".join(lines)


def fmt_model_display(model_name: str) -> str:
    """Add a friendly subtitle under each model name."""
    subtitles = {
        "NaiveBayes":   "Probabilistic · 13 features",
        "SVM":          "Support Vector · 11 features",
        "DecisionTree": "Decision Tree  · 13 features",
    }
    return subtitles.get(model_name, model_name)
