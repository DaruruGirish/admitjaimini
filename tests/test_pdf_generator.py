from io import BytesIO

from PIL import Image
from reportlab.lib.pagesizes import A4

from services.excel_reader import RawStudent, read_workbook
from services.pdf_generator import (
    extract_pdf_text,
    generate_class_pdfs,
    render_class_pdf,
    render_preview_png,
    render_single_card_pdf,
)
from services.student_processor import group_students
from services.validator import validate_workbook
from tests.helpers import build_sample_workbook


def _student(name, roll, grade="3"):
    return RawStudent(name=name, roll_no=roll, grade=grade, sheet="3rd", row=2)


def test_page_counts_for_one_two_three_students():
    one = render_class_pdf("3", [_student("AMITH A", "JPS260301")])
    two = render_class_pdf(
        "3",
        [_student("AMITH A", "JPS260301"), _student("AMOGH C N", "JPS260302")],
    )
    three = render_class_pdf(
        "3",
        [
            _student("AMITH A", "JPS260301"),
            _student("AMOGH C N", "JPS260302"),
            _student("ANVITHA B", "JPS260303"),
        ],
    )
    assert one.page_count == 1
    assert two.page_count == 1
    assert three.page_count == 2


def test_a4_portrait_and_schedule_content():
    pdf = render_class_pdf("6", [_student("AARYAN B V", "JPS260602", "6")])
    text = extract_pdf_text(pdf.data)
    assert "AARYAN B V" in text
    assert "JPS260602" in text
    assert "KANNADA" in text
    assert "Drawing/ PE" in text
    assert "10:30AM to 12:00PM" in text
    assert "ADMIT CARD" in text
    from pypdfium2 import PdfDocument

    document = PdfDocument(pdf.data)
    width, height = document[0].get_size()
    document.close()
    assert abs(width - A4[0]) < 1
    assert abs(height - A4[1]) < 1


def test_odd_class_does_not_invent_a_second_student():
    pdf = render_class_pdf("3", [_student("AMITH A", "JPS260301")])
    text = extract_pdf_text(pdf.data)
    assert text.count("AMITH A") == 1
    assert "PHOTO" in text


def test_preview_uses_real_renderer():
    png = render_preview_png(_student("AMITH A", "JPS260301"))
    assert png.startswith(b"\x89PNG")
    image = Image.open(BytesIO(png)).convert("L")
    assert image.getextrema()[0] < 40


def test_long_name_still_renders():
    pdf = render_single_card_pdf(
        _student("KARTHIKEYA VENKATESH GOWDA", "JPS260318")
    )
    text = extract_pdf_text(pdf)
    assert "KARTHIKEYA" in text
    assert "JPS260318" in text


def test_end_to_end_class_pdf_names(tmp_path):
    path = build_sample_workbook(tmp_path / "students.xlsx")
    result = validate_workbook(read_workbook(path))
    grouped = group_students(result.students)
    pdfs = generate_class_pdfs(grouped)
    names = [item.filename for item in pdfs]
    assert names == [
        "Admit_Cards_Class_1.pdf",
        "Admit_Cards_Class_2.pdf",
        "Admit_Cards_Class_3.pdf",
    ]
    class3 = next(item for item in pdfs if item.grade == "3")
    assert class3.student_count == 12
    assert class3.page_count == 6
    text = extract_pdf_text(class3.data)
    assert text.find("JPS260301") < text.find("JPS260320")
