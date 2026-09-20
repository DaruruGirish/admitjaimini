from __future__ import annotations

import re


def normalize_header(value) -> str:
    if value is None:
        return ""
    text = str(value).replace("\ufeff", "").strip()
    text = re.sub(r"\s+", " ", text).lower()
    return text.rstrip(".")


def clean_cell(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    text = str(value).replace("\ufeff", "").strip()
    if text.lower() in {"none", "nan"}:
        return ""
    if re.fullmatch(r"-?\d+\.0+", text):
        return text.split(".", 1)[0]
    return text


def normalize_grade(value) -> str:
    text = clean_cell(value)
    if not text:
        return ""
    if re.fullmatch(r"\d+", text):
        return str(int(text))
    ordinal = re.search(r"(\d+)\s*(?:st|nd|rd|th)\b", text, flags=re.I)
    if ordinal:
        return str(int(ordinal.group(1)))
    prefixed = re.search(r"(?:grade|class|std)\s*(\d+)", text, flags=re.I)
    if prefixed:
        return str(int(prefixed.group(1)))
    if re.fullmatch(r"\d+", text.replace(" ", "")):
        return str(int(text.replace(" ", "")))
    return text
