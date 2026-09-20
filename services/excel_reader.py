from __future__ import annotations

from dataclasses import dataclass, field
from typing import BinaryIO, Union

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from config import HEADER_ALIASES, REQUIRED_COLUMNS
from utils.formatting import clean_cell, normalize_grade, normalize_header

Source = Union[str, BinaryIO]


@dataclass
class RawStudent:
    name: str
    roll_no: str
    grade: str
    sheet: str
    row: int


@dataclass
class SheetExtract:
    name: str
    original_name: str
    is_empty: bool
    missing_columns: list[str] = field(default_factory=list)
    records: list[RawStudent] = field(default_factory=list)
    header_row: int | None = None


@dataclass
class WorkbookExtract:
    sheets: list[SheetExtract]
    sheets_read: list[str]
    sheets_skipped: list[str]


def _is_empty_sheet(sheet: Worksheet) -> bool:
    for row in sheet.iter_rows(max_row=sheet.max_row or 1, values_only=True):
        if any(clean_cell(cell) for cell in row):
            return False
    return True


def _find_header(sheet: Worksheet) -> tuple[int, dict[str, int]] | None:
    max_scan = min(sheet.max_row or 0, 20)
    for row_idx in range(1, max_scan + 1):
        mapping: dict[str, int] = {}
        for col_idx, cell in enumerate(sheet[row_idx], start=1):
            key = HEADER_ALIASES.get(normalize_header(cell.value))
            if key and key not in mapping:
                mapping[key] = col_idx
        if {"roll_no", "name", "grade"}.issubset(mapping):
            return row_idx, mapping
    return None


def _extract_sheet(sheet: Worksheet) -> SheetExtract:
    original_name = sheet.title
    name = original_name.strip()
    if _is_empty_sheet(sheet):
        return SheetExtract(name=name, original_name=original_name, is_empty=True)

    header = _find_header(sheet)
    if header is None:
        missing = list(REQUIRED_COLUMNS)
        return SheetExtract(
            name=name,
            original_name=original_name,
            is_empty=False,
            missing_columns=missing,
        )

    header_row, mapping = header
    records: list[RawStudent] = []
    for row_idx in range(header_row + 1, (sheet.max_row or header_row) + 1):
        name_val = clean_cell(sheet.cell(row_idx, mapping["name"]).value)
        roll_val = clean_cell(sheet.cell(row_idx, mapping["roll_no"]).value)
        grade_val = normalize_grade(sheet.cell(row_idx, mapping["grade"]).value)
        if not name_val and not roll_val and not grade_val:
            continue
        records.append(
            RawStudent(
                name=name_val,
                roll_no=roll_val,
                grade=grade_val,
                sheet=name,
                row=row_idx,
            )
        )

    return SheetExtract(
        name=name,
        original_name=original_name,
        is_empty=False,
        missing_columns=[],
        records=records,
        header_row=header_row,
    )


def read_workbook(source: Source) -> WorkbookExtract:
    if hasattr(source, "seek"):
        source.seek(0)
    workbook = load_workbook(source, data_only=True)
    try:
        sheets: list[SheetExtract] = []
        sheets_read: list[str] = []
        sheets_skipped: list[str] = []
        for sheet in workbook.worksheets:
            extract = _extract_sheet(sheet)
            if extract.is_empty:
                sheets_skipped.append(extract.name or extract.original_name)
                continue
            sheets.append(extract)
            sheets_read.append(extract.name)
        return WorkbookExtract(
            sheets=sheets,
            sheets_read=sheets_read,
            sheets_skipped=sheets_skipped,
        )
    finally:
        workbook.close()
