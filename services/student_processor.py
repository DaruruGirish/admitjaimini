from __future__ import annotations

from collections import defaultdict

from services.excel_reader import RawStudent
from utils.sorting import sort_grade_keys, sort_students


def group_students(students: list[RawStudent]) -> dict[str, list[RawStudent]]:
    grouped: dict[str, list[RawStudent]] = defaultdict(list)
    for student in students:
        grouped[student.grade].append(student)

    ordered: dict[str, list[RawStudent]] = {}
    for grade in sort_grade_keys(list(grouped.keys())):
        ordered[grade] = sort_students(grouped[grade])
    return ordered


def class_summary(grouped: dict[str, list[RawStudent]]) -> list[dict]:
    summary = []
    for grade, students in grouped.items():
        count = len(students)
        summary.append(
            {
                "grade": grade,
                "student_count": count,
                "page_count": (count + 1) // 2,
                "filename": f"Admit_Cards_Class_{grade}.pdf",
            }
        )
    return summary
