from __future__ import annotations

import re
from typing import Iterable, Sequence


def natural_key(value) -> list:
    text = "" if value is None else str(value).strip()
    parts = re.split(r"(\d+)", text)
    key = []
    for part in parts:
        if part == "":
            continue
        if part.isdigit():
            key.append((0, int(part)))
        else:
            key.append((1, part.casefold()))
    return key


def sort_students(students: Iterable, roll_attr: str = "roll_no") -> list:
    records = list(students)
    records.sort(key=lambda item: natural_key(getattr(item, roll_attr)))
    return records


def sort_grade_keys(grades: Sequence[str]) -> list[str]:
    return sorted(grades, key=natural_key)
