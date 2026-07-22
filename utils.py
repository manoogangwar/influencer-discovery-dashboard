import re


def normalize_text(value):
    """Normalize text for matching and comparison."""
    text = str(value or "").strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def convert_to_int(value, default=0):
    """Convert numeric values to integers safely."""
    if isinstance(value, int):
        return value

    if isinstance(value, float) and value.is_integer():
        return int(value)

    text = str(value or "").replace(",", "").strip()
    if not text:
        return default

    try:
        return int(float(text))
    except (ValueError, TypeError):
        return default
