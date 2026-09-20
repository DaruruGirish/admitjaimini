from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def tmp_workbook(tmp_path):
    def _make(include_issues=None):
        from tests.helpers import build_sample_workbook

        return build_sample_workbook(tmp_path / "students.xlsx", include_issues=include_issues)

    return _make
