from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from services.excel_reader import RawStudent, WorkbookExtract


@dataclass
class ValidationResult:
    ok: bool
    students: list[RawStudent] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_workbook(extract: WorkbookExtract) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    if extract.sheets_skipped:
        skipped = ", ".join(f"'{name}'" for name in extract.sheets_skipped)
        warnings.append(f"Ignored empty worksheet(s): {skipped}.")

    if not extract.sheets:
        errors.append("No valid worksheet found. Add at least one sheet with Roll No, Name, and Grade.")
        return ValidationResult(ok=False, errors=errors, warnings=warnings)

    students: list[RawStudent] = []
    for sheet in extract.sheets:
        if sheet.missing_columns:
            missing = ", ".join(sheet.missing_columns)
            warnings.append(
                f"Sheet '{sheet.name}' was skipped because it is missing required column(s): {missing}."
            )
            continue
        if not sheet.records:
            warnings.append(f"Sheet '{sheet.name}' has headers but no student rows.")
            continue
        students.extend(sheet.records)

    for student in students:
        location = f"sheet '{student.sheet}', row {student.row}"
        if not student.name:
            errors.append(f"Name is empty ({location}).")
        if not student.roll_no:
            errors.append(f"Roll No is empty ({location}).")
        if not student.grade:
            errors.append(f"Grade is empty ({location}).")

    duplicates: dict[tuple[str, str], list[RawStudent]] = defaultdict(list)
    for student in students:
        if student.roll_no and student.grade:
            duplicates[(student.grade, student.roll_no)].append(student)

    for (grade, roll_no), rows in sorted(duplicates.items()):
        if len(rows) < 2:
            continue
        details = "; ".join(f"sheet '{item.sheet}' row {item.row}" for item in rows)
        errors.append(
            f"Duplicate Roll No '{roll_no}' in Class {grade} ({details})."
        )

    if not students and not errors:
        errors.append("No student records found in the workbook.")

    ok = not errors
    return ValidationResult(
        ok=ok,
        students=students if ok else [],
        errors=errors,
        warnings=warnings,
    )
