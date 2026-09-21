from __future__ import annotations

import re
from dataclasses import dataclass, replace
from io import BytesIO
from math import ceil

import pypdfium2 as pdfium
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas

from templates import admit_card_template as card_template
from services.excel_reader import RawStudent
from utils.formatting import clean_cell, normalize_grade


@dataclass
class GeneratedPDF:
    grade: str
    filename: str
    data: bytes
    student_count: int
    page_count: int


def _page_count(student_count: int) -> int:
    if student_count <= 0:
        return 0
    return ceil(student_count / 2)


def render_class_pdf(grade: str, students: list[RawStudent]) -> GeneratedPDF:
    card_template.register_fonts()
    buffer = BytesIO()
    pdf = pdf_canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle(f"Admit Cards Class {grade}")
    pdf.setAuthor("Jaimini Public School, Hiriyur")

    top_card_y = card_template.PAGE_MARGIN_Y + card_template.CARD_HEIGHT + card_template.CUT_GAP
    bottom_card_y = card_template.PAGE_MARGIN_Y
    cut_y = card_template.PAGE_MARGIN_Y + card_template.CARD_HEIGHT + (card_template.CUT_GAP / 2.0)

    for index in range(0, len(students), 2):
        first = students[index]
        card_template.draw_admit_card(
            pdf,
            first,
            card_template.PAGE_MARGIN_X,
            top_card_y,
            card_template.CARD_WIDTH,
            card_template.CARD_HEIGHT,
        )
        card_template.draw_cut_line(
            pdf,
            cut_y,
            card_template.PAGE_MARGIN_X,
            card_template.PAGE_MARGIN_X + card_template.CARD_WIDTH,
        )
        if index + 1 < len(students):
            second = students[index + 1]
            card_template.draw_admit_card(
                pdf,
                second,
                card_template.PAGE_MARGIN_X,
                bottom_card_y,
                card_template.CARD_WIDTH,
                card_template.CARD_HEIGHT,
            )
        pdf.showPage()

    pdf.save()
    data = buffer.getvalue()
    return GeneratedPDF(
        grade=grade,
        filename=f"Admit_Cards_Class_{grade}.pdf",
        data=data,
        student_count=len(students),
        page_count=_page_count(len(students)),
    )


def generate_class_pdfs(grouped: dict[str, list[RawStudent]]) -> list[GeneratedPDF]:
    return [render_class_pdf(grade, students) for grade, students in grouped.items()]


def _safe_filename_part(value: str) -> str:
    cleaned = re.sub(r"[^\w.-]+", "_", value.strip())
    return cleaned.strip("._") or "student"


def render_manual_student_pdf(name: str, roll_no: str, grade: str) -> GeneratedPDF:
    student = RawStudent(
        name=clean_cell(name),
        roll_no=clean_cell(roll_no),
        grade=normalize_grade(grade),
        sheet="manual",
        row=1,
    )
    pdf = render_class_pdf(student.grade, [student])
    filename = f"Admit_Card_{_safe_filename_part(student.grade)}_{_safe_filename_part(student.roll_no)}.pdf"
    return replace(pdf, filename=filename)


def render_single_card_pdf(student: RawStudent) -> bytes:
    card_template.register_fonts()
    buffer = BytesIO()
    pdf = pdf_canvas.Canvas(
        buffer, pagesize=(card_template.CARD_WIDTH, card_template.CARD_HEIGHT)
    )
    card_template.draw_admit_card(
        pdf, student, 0, 0, card_template.CARD_WIDTH, card_template.CARD_HEIGHT
    )
    pdf.save()
    return buffer.getvalue()


def pdf_to_png(pdf_bytes: bytes, page_index: int = 0, scale: float = 2.4) -> bytes:
    document = pdfium.PdfDocument(pdf_bytes)
    try:
        page = document[page_index]
        bitmap = page.render(scale=scale)
        image = bitmap.to_pil()
        output = BytesIO()
        image.save(output, format="PNG")
        return output.getvalue()
    finally:
        document.close()


def render_preview_png(student: RawStudent, scale: float = 2.6) -> bytes:
    return pdf_to_png(render_single_card_pdf(student), scale=scale)


def assert_a4_pages(pdf_bytes: bytes) -> tuple[int, tuple[float, float]]:
    document = pdfium.PdfDocument(pdf_bytes)
    try:
        page = document[0]
        width, height = page.get_size()
        return len(document), (width, height)
    finally:
        document.close()


def extract_pdf_text(pdf_bytes: bytes) -> str:
    document = pdfium.PdfDocument(pdf_bytes)
    try:
        chunks = []
        for page in document:
            textpage = page.get_textpage()
            chunks.append(textpage.get_text_bounded())
            textpage.close()
        return "\n".join(chunks)
    finally:
        document.close()
