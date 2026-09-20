from services.excel_reader import read_workbook


def test_reads_all_sheets_and_strips_sheet_names(tmp_workbook):
    extract = read_workbook(tmp_workbook())
    assert "2nd" in extract.sheets_read
    assert "3rd" in extract.sheets_read
    assert "1st" in extract.sheets_read
    assert "Empty" in extract.sheets_skipped


def test_ignores_empty_rows_and_preserves_roll_text(tmp_workbook):
    extract = read_workbook(tmp_workbook())
    class3 = next(sheet for sheet in extract.sheets if sheet.name == "3rd")
    rolls = [item.roll_no for item in class3.records]
    assert "JPS260301" in rolls
    assert all(item.grade == "3" for item in class3.records)


def test_missing_required_columns(tmp_workbook):
    extract = read_workbook(tmp_workbook("missing_columns"))
    bad = next(sheet for sheet in extract.sheets if sheet.name == "Bad")
    assert bad.missing_columns
