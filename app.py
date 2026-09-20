from __future__ import annotations

from io import BytesIO
import importlib
import zipfile

import streamlit as st

import config
import utils.logo as logo_utils
from templates import admit_card_template
from services import pdf_generator
from services import excel_reader
from services import validator
from services import student_processor

importlib.reload(config)
importlib.reload(logo_utils)
importlib.reload(admit_card_template)
importlib.reload(excel_reader)
importlib.reload(validator)
importlib.reload(student_processor)
importlib.reload(pdf_generator)

from services.pdf_generator import generate_class_pdfs, render_preview_png
from services.excel_reader import read_workbook
from services.student_processor import class_summary, group_students
from services.validator import validate_workbook

LAYOUT_VERSION = "student-count-v6"
if st.session_state.get("layout_version") != LAYOUT_VERSION:
    st.session_state.pop("generated", None)
    st.session_state.layout_version = LAYOUT_VERSION

st.set_page_config(
    page_title="School Admit Card Generator",
    page_icon="📄",
    layout="centered",
)

st.markdown(
    """
    <style>
    .block-container {max-width: 860px; padding-top: 1.4rem;}
    h1 {letter-spacing: 0.02em;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("School Admit Card Generator")
st.caption("Jaimini Public School, Hiriyur — print-ready A4 admit cards (two per page).")


def _store_upload(uploaded) -> None:
    st.session_state.workbook_bytes = uploaded.getvalue()
    st.session_state.workbook_name = uploaded.name
    st.session_state.pop("generated", None)
    st.session_state.pop("preview_png", None)
    st.session_state.pop("preview_student", None)


uploaded = st.file_uploader(
    "STEP 1 — Upload Excel Workbook",
    type=["xlsx", "xls"],
    help="Each worksheet should contain columns: Roll No, Name, Grade.",
)
if uploaded is not None:
    _store_upload(uploaded)

workbook_bytes = st.session_state.get("workbook_bytes")
if workbook_bytes:
    upload_dir = config.BASE_DIR / "uploads"
    upload_dir.mkdir(exist_ok=True)
    (upload_dir / "last.xlsx").write_bytes(workbook_bytes)
if not workbook_bytes:
    st.info("Upload a workbook to detect classes and generate admit cards.")
    st.stop()

st.subheader("STEP 2 — Validate Workbook")
try:
    extract = read_workbook(BytesIO(workbook_bytes))
except Exception as exc:
    st.error(f"The workbook could not be opened. {exc}")
    st.stop()

result = validate_workbook(extract)
for warning in result.warnings:
    st.warning(warning)

if not result.ok:
    st.error("Validation failed. PDFs were not generated.")
    for error in result.errors:
        st.error(error)
    st.stop()

st.success("Workbook successfully loaded.")

grouped = group_students(result.students)
summary = class_summary(grouped)

st.subheader("STEP 3 — Detected Classes")
st.markdown("Detected:")
total = 0
for item in summary:
    total += item["student_count"]
    st.write(f"Class {item['grade']} — {item['student_count']} students")
st.write(f"Total — {total} students")
with st.expander("Rows read from each sheet"):
    for sheet in extract.sheets:
        st.write(f"Sheet '{sheet.name}' — {len(sheet.records)} students")

first_grade = next(iter(grouped))
preview_student = grouped[first_grade][0]
preview_png = render_preview_png(preview_student)
st.subheader("Preview")
st.caption(
    f"Rendered from the real template using {preview_student.name} "
    f"(Grade {preview_student.grade}, {preview_student.roll_no})."
)
st.image(preview_png, width="stretch")

st.subheader("STEP 4 — Generate PDFs")
if st.button("Generate Admit Cards", type="primary"):
    with st.spinner("Generating class-wise admit cards..."):
        st.session_state.generated = generate_class_pdfs(grouped)

generated = st.session_state.get("generated")
if not generated:
    st.stop()

st.subheader("STEP 5 — Generated Files")
zip_buffer = BytesIO()
with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
    for pdf in generated:
        archive.writestr(pdf.filename, pdf.data)

st.download_button(
    "Download all PDFs (ZIP)",
    data=zip_buffer.getvalue(),
    file_name="Admit_Cards.zip",
    mime="application/zip",
)

for pdf in generated:
    st.markdown(f"**Class {pdf.grade}**")
    st.write(f"{pdf.student_count} students")
    st.write(f"{pdf.page_count} pages")
    st.download_button(
        f"Download Class {pdf.grade} PDF",
        data=pdf.data,
        file_name=pdf.filename,
        mime="application/pdf",
        key=f"download-{pdf.grade}",
    )
