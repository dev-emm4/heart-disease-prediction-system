import os
import re

VALID_MODELS = {"NaiveBayes", "SVM", "DecisionTree"}


def validate_model(model_name: str) -> tuple[bool, str]:
    if model_name not in VALID_MODELS:
        return False, f"Model must be one of: {', '.join(VALID_MODELS)}"
    return True, ""


def validate_numeric_field(value: str, label: str) -> tuple[bool, str]:
    if value.strip() == "":
        return False, f"'{label}' is required."
    try:
        float(value)
        return True, ""
    except ValueError:
        return False, f"'{label}' must be a number."


def validate_csv_path(path: str) -> tuple[bool, str]:
    path = path.strip()
    if not path:
        return False, "Please select or enter a CSV file path."
    if not os.path.isfile(path):
        return False, f"File not found: {path}"
    if not path.lower().endswith(".csv"):
        return False, "File must be a .csv file."
    return True, ""


def validate_column_indices(text: str, label: str = "Drop columns") -> tuple[bool, list | None, str]:
    text = text.strip()
    if not text:
        return True, [], ""          # Empty is allowed — no columns to drop

    parts = [p.strip() for p in text.split(",") if p.strip()]
    indices = []
    for p in parts:
        try:
            indices.append(int(p))
        except ValueError:
            return False, None, f"{label}: '{p}' is not a valid integer index."
    return True, indices, ""


def validate_target_column(text: str) -> tuple[bool, int | None, str]:
    text = text.strip()
    if not text:
        return False, None, "Target column index is required."
    try:
        col = int(text)
        if col < 0:
            return False, None, "Target column must be a non-negative integer."
        return True, col, ""
    except ValueError:
        return False, None, "Target column must be an integer index."


def validate_uuid(value: str) -> tuple[bool, str]:
    pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    if not re.match(pattern, value.strip().lower()):
        return False, "Not a valid UUID format."
    return True, ""
