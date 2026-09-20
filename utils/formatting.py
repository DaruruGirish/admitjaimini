from __future__ import annotations

import re


def normalize_header(value) -> str:
    if value is None:
        return ""
    text = re.sub(r"\s+", " ", str(value).strip()).lower()
    return text.rstrip(".")


def clean_cell(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    text = str(value).strip()
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
    return text
