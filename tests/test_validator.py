from services.excel_reader import read_workbook
from services.validator import validate_workbook


def test_valid_workbook_passes(tmp_workbook):
    result = validate_workbook(read_workbook(tmp_workbook()))
    assert result.ok
    assert result.students
    assert not result.errors


def test_missing_name_fails(tmp_workbook):
    result = validate_workbook(read_workbook(tmp_workbook("missing_name")))
    assert not result.ok
    assert any("Name is empty" in error for error in result.errors)
    assert result.students == []


def test_missing_roll_fails(tmp_workbook):
    result = validate_workbook(read_workbook(tmp_workbook("missing_roll")))
    assert not result.ok
    assert any("Roll No is empty" in error for error in result.errors)


def test_missing_grade_fails(tmp_workbook):
    result = validate_workbook(read_workbook(tmp_workbook("missing_grade")))
    assert not result.ok
    assert any("Grade is empty" in error for error in result.errors)


def test_duplicate_roll_fails(tmp_workbook):
    result = validate_workbook(read_workbook(tmp_workbook("duplicate_roll")))
    assert not result.ok
    assert any("Duplicate Roll No 'JPS260301'" in error for error in result.errors)


def test_missing_columns_on_extra_sheet_is_skipped(tmp_workbook):
    result = validate_workbook(read_workbook(tmp_workbook("missing_columns")))
    assert result.ok
    assert any("missing required column" in warning.lower() for warning in result.warnings)


def test_workbook_with_no_valid_sheet_fails(tmp_path):
    from openpyxl import Workbook
    from services.excel_reader import read_workbook

    path = tmp_path / "bad.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Notes"
    sheet.append(["Remark", "Date"])
    sheet.append(["Hello", "2026-09-23"])
    workbook.save(path)
    result = validate_workbook(read_workbook(path))
    assert not result.ok
