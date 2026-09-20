# School Admit Card Generator

Print-ready A4 admit cards for Jaimini Public School, Hiriyur.

Upload an Excel workbook. The app reads every worksheet, groups students by **Grade**, sorts them by **Roll No**, and writes one PDF per class. Each A4 page has two admit cards and a cut line.

## Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local Streamlit URL, upload the student workbook, then click **Generate Admit Cards**.

## Excel format

Do not hardcode class names. Any number of worksheets is fine.

Required columns on every used sheet:

| Roll No    | Name      | Grade |
|------------|-----------|-------|
| JPS260301  | AMITH A   | 3     |

- Empty sheets are ignored.
- Sheet names are trimmed (`"2nd "` is read as `"2nd"`).
- Students are grouped by the **Grade** column, not the sheet tab name.
- Roll numbers are kept exactly as written and sorted naturally (`JPS260301` before `JPS260310`).

Generated files:

- `Admit_Cards_Class_1.pdf`
- `Admit_Cards_Class_2.pdf`
- `Admit_Cards_Class_3.pdf`

The class number comes from the Grade value.

## Printing

- Paper: A4
- Orientation: Portrait
- Scale: **100% / Actual Size**
- Cut or tear along the dashed line between the two cards

Odd headcounts leave the last half of the last page blank. No fake second card is generated.

## Sample workbook

After installing requirements:

```bash
python -c "from tests.helpers import build_sample_workbook; build_sample_workbook('sample_data/students.xlsx')"
```

Then upload `sample_data/students.xlsx` in the app.

## Tests

```bash
pytest -q
```
