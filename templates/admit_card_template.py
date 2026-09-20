from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import black, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from config import (
    ACADEMIC_YEAR,
    CARD_TITLE,
    EXAM_NAME,
    EXAM_SCHEDULE,
    HEADMISTRESS_LABEL,
    HEADMISTRESS_NAME,
    LOGO_PATH,
    PHOTO_LABEL,
    SCHOOL_NAME,
    STUDENT_SIGN_LABEL,
    TEACHER_SIGN_LABEL,
    WINDOWS_SCRIPT,
    WINDOWS_SERIF_BOLD,
    WINDOWS_SERIF_REGULAR,
)
from utils.logo import prepare_print_logo
from services.excel_reader import RawStudent

PAGE_WIDTH, PAGE_HEIGHT = A4
PAGE_MARGIN_X = 18
PAGE_MARGIN_Y = 14
CUT_GAP = 18

CARD_WIDTH = PAGE_WIDTH - (PAGE_MARGIN_X * 2)
CARD_HEIGHT = (PAGE_HEIGHT - (PAGE_MARGIN_Y * 2) - CUT_GAP) / 2.0

FONT_REGULAR = "Times-Roman"
FONT_BOLD = "Times-Bold"
FONT_SCRIPT = "Times-BoldItalic"
_FONTS_READY = False


def card_size() -> tuple[float, float]:
    return CARD_WIDTH, CARD_HEIGHT


def register_fonts() -> None:
    global FONT_REGULAR, FONT_BOLD, FONT_SCRIPT, _FONTS_READY
    if _FONTS_READY:
        return
    prepare_print_logo()
    if WINDOWS_SERIF_REGULAR.exists() and WINDOWS_SERIF_BOLD.exists():
        pdfmetrics.registerFont(TTFont("SchoolSerif", str(WINDOWS_SERIF_REGULAR)))
        pdfmetrics.registerFont(TTFont("SchoolSerif-Bold", str(WINDOWS_SERIF_BOLD)))
        FONT_REGULAR = "SchoolSerif"
        FONT_BOLD = "SchoolSerif-Bold"
    if WINDOWS_SCRIPT.exists():
        pdfmetrics.registerFont(TTFont("SchoolScript", str(WINDOWS_SCRIPT)))
        FONT_SCRIPT = "SchoolScript"
    _FONTS_READY = True


def _fit_font_size(canvas: Canvas, text: str, font: str, max_size: float, min_size: float, max_width: float) -> float:
    size = max_size
    while size > min_size and canvas.stringWidth(text, font, size) > max_width:
        size -= 0.25
    return size


def _wrap_text(canvas: Canvas, text: str, font: str, size: float, max_width: float) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        if canvas.stringWidth(trial, font, size) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    if len(lines) == 1 and canvas.stringWidth(lines[0], font, size) > max_width:
        # Unbroken long token: shrink is handled by caller; keep as one line.
        return lines
    return lines[:2]


def _draw_centered(canvas: Canvas, text: str, x: float, y: float, font: str, size: float) -> None:
    canvas.setFillColor(black)
    canvas.setFont(font, size)
    canvas.drawCentredString(x, y, text)


def _draw_logo(canvas: Canvas, x: float, y: float, size: float) -> None:
    logo = Path(LOGO_PATH)
    cx = x + size / 2.0
    cy = y + size / 2.0
    canvas.saveState()
    if logo.exists():
        canvas.drawImage(
            str(logo),
            x,
            y,
            width=size,
            height=size,
            mask="auto",
            preserveAspectRatio=True,
            anchor="c",
        )
    canvas.setStrokeColor(black)
    canvas.setLineWidth(1.15)
    canvas.circle(cx, cy, size / 2.0, stroke=1, fill=0)
    canvas.restoreState()


def _draw_student_value(
    canvas: Canvas,
    text: str,
    x: float,
    y: float,
    width: float,
    row_height: float,
    font: str,
    size: float,
) -> None:
    fitted = _fit_font_size(canvas, text, font, size, 7.0, width)
    if canvas.stringWidth(text, font, fitted) <= width:
        canvas.setFont(font, fitted)
        canvas.drawString(x, y + (row_height / 2.0) - (fitted * 0.35), text)
        return

    lines = _wrap_text(canvas, text, font, fitted, width)
    if len(lines) == 1:
        canvas.setFont(font, fitted)
        canvas.drawString(x, y + (row_height / 2.0) - (fitted * 0.35), lines[0])
        return

    line_size = min(fitted, 8.5)
    lines = _wrap_text(canvas, text, font, line_size, width)
    total = line_size * 1.15 * len(lines)
    start_y = y + (row_height / 2.0) + (total / 2.0) - line_size
    canvas.setFont(font, line_size)
    for index, line in enumerate(lines):
        canvas.drawString(x, start_y - (index * line_size * 1.15), line)


def draw_admit_card(
    canvas: Canvas,
    student: RawStudent,
    x: float,
    y: float,
    width: float = CARD_WIDTH,
    height: float = CARD_HEIGHT,
) -> None:
    register_fonts()
    canvas.saveState()
    canvas.setFillColor(white)
    canvas.setStrokeColor(black)
    canvas.setLineWidth(1.6)
    canvas.rect(x, y, width, height, stroke=1, fill=1)
    canvas.setFillColor(black)

    pad = 10.0
    inner_left = x + pad
    inner_right = x + width - pad
    inner_top = y + height - pad
    inner_width = width - (pad * 2)

    logo_size = 62.0
    logo_x = inner_left + 1
    logo_y = inner_top - logo_size + 2
    _draw_logo(canvas, logo_x, logo_y, logo_size)

    center_x = x + (width / 2.0)
    school_size = 17.0
    school_width = canvas.stringWidth(SCHOOL_NAME, FONT_BOLD, school_size)
    max_school_width = inner_width - logo_size - 12
    if school_width > max_school_width:
        school_size = _fit_font_size(
            canvas, SCHOOL_NAME, FONT_BOLD, school_size, 11.0, max_school_width
        )
    _draw_centered(canvas, SCHOOL_NAME, center_x, inner_top - 18, FONT_BOLD, school_size)

    exam_size = 10.8
    exam_gap = 16.0
    exam_width = canvas.stringWidth(EXAM_NAME, FONT_BOLD, exam_size)
    year_width = canvas.stringWidth(ACADEMIC_YEAR, FONT_BOLD, exam_size)
    exam_total = exam_width + exam_gap + year_width
    exam_start = center_x - (exam_total / 2.0)
    canvas.setFont(FONT_BOLD, exam_size)
    canvas.drawString(exam_start, inner_top - 34, EXAM_NAME)
    canvas.drawString(exam_start + exam_width + exam_gap, inner_top - 34, ACADEMIC_YEAR)

    _draw_centered(canvas, CARD_TITLE, center_x, inner_top - 50, FONT_BOLD, 13.6)

    photo_size = 66.0
    photo_x = inner_right - photo_size
    details_top = inner_top - 58
    photo_y = details_top - photo_size
    canvas.setLineWidth(1.15)
    canvas.rect(photo_x, photo_y, photo_size, photo_size, stroke=1, fill=0)
    _draw_centered(
        canvas,
        PHOTO_LABEL,
        photo_x + (photo_size / 2.0),
        photo_y + (photo_size / 2.0) - 3.5,
        FONT_REGULAR,
        8.2,
    )

    table_x = inner_left
    table_w = photo_x - table_x - 8
    table_h = photo_size
    table_y = photo_y
    row_h = table_h / 3.0
    canvas.setLineWidth(1.0)
    canvas.rect(table_x, table_y, table_w, table_h, stroke=1, fill=0)
    canvas.line(table_x, table_y + row_h, table_x + table_w, table_y + row_h)
    canvas.line(table_x, table_y + (row_h * 2), table_x + table_w, table_y + (row_h * 2))

    label_font_size = 10.3
    canvas.setFont(FONT_BOLD, label_font_size)
    label_width = canvas.stringWidth("Roll No.", FONT_BOLD, label_font_size)
    label_x = table_x + 8
    colon_x = label_x + label_width + 6
    value_x = colon_x + 12
    value_width = table_x + table_w - value_x - 8

    fields = [
        ("Name", student.name),
        ("Grade", student.grade),
        ("Roll No.", student.roll_no),
    ]
    for index, (label, value) in enumerate(fields):
        row_top = table_y + table_h - (index * row_h)
        row_bottom = row_top - row_h
        text_y = row_bottom + (row_h / 2.0) - 3.6
        canvas.setFont(FONT_BOLD, label_font_size)
        canvas.drawString(label_x, text_y, label)
        canvas.drawString(colon_x, text_y, ":")
        _draw_student_value(
            canvas,
            value,
            value_x,
            row_bottom,
            value_width,
            row_h,
            FONT_BOLD,
            10.6,
        )

    timetable_top = table_y - 10
    timetable_bottom = y + 52
    timetable_h = timetable_top - timetable_bottom
    col_fracs = (0.09, 0.145, 0.17, 0.215, 0.20, 0.18)
    col_widths = [inner_width * frac for frac in col_fracs]
    headers = ["Sl. No.", "Date", "Subject", "Written Exam", "Oral Exam", "Invigilator Sign."]
    rows = [headers] + [
        [item["sl_no"], item["date"], item["subject"], item["written"], item["oral"], ""]
        for item in EXAM_SCHEDULE
    ]
    row_count = len(rows)
    exam_row_h = timetable_h / row_count
    canvas.setLineWidth(0.95)
    canvas.rect(inner_left, timetable_bottom, inner_width, timetable_h, stroke=1, fill=0)

    col_x = inner_left
    for width_col in col_widths[:-1]:
        col_x += width_col
        canvas.line(col_x, timetable_bottom, col_x, timetable_top)

    for row_index in range(1, row_count):
        line_y = timetable_top - (row_index * exam_row_h)
        canvas.line(inner_left, line_y, inner_right, line_y)

    for row_index, row in enumerate(rows):
        row_top = timetable_top - (row_index * exam_row_h)
        row_bottom = row_top - exam_row_h
        font = FONT_BOLD if row_index == 0 else FONT_REGULAR
        size = 8.6 if row_index == 0 else 8.15
        canvas.setFont(font, size)
        cell_x = inner_left
        for col_index, (cell, col_w) in enumerate(zip(row, col_widths)):
            if col_index == 2 and row_index > 0:
                cell_size = _fit_font_size(canvas, cell, font, size, 6.5, col_w - 4)
                canvas.setFont(font, cell_size)
                text_y = row_bottom + (exam_row_h / 2.0) - (cell_size * 0.32)
            else:
                canvas.setFont(font, size)
                text_y = row_bottom + (exam_row_h / 2.0) - (size * 0.32)
            canvas.drawCentredString(cell_x + (col_w / 2.0), text_y, cell)
            cell_x += col_w

    sign_y = y + 28
    line_y = sign_y + 12
    sign_width = 92
    left_line_x = inner_left + 18
    canvas.setLineWidth(1.0)
    canvas.line(left_line_x, line_y, left_line_x + sign_width, line_y)
    _draw_centered(
        canvas,
        STUDENT_SIGN_LABEL,
        left_line_x + (sign_width / 2.0),
        sign_y,
        FONT_REGULAR,
        8.1,
    )

    teacher_center = center_x - 8
    canvas.line(teacher_center - (sign_width / 2.0), line_y, teacher_center + (sign_width / 2.0), line_y)
    _draw_centered(canvas, TEACHER_SIGN_LABEL, teacher_center, sign_y, FONT_REGULAR, 8.1)

    script_size = 15.5
    canvas.setFont(FONT_SCRIPT, script_size)
    canvas.drawRightString(inner_right - 4, line_y - 1, HEADMISTRESS_NAME)
    canvas.setFont(FONT_REGULAR, 8.1)
    head_label_width = canvas.stringWidth(HEADMISTRESS_LABEL, FONT_REGULAR, 8.1)
    canvas.drawString(inner_right - 4 - head_label_width, sign_y, HEADMISTRESS_LABEL)

    canvas.restoreState()


def draw_cut_line(canvas: Canvas, y: float, x0: float, x1: float) -> None:
    canvas.saveState()
    canvas.setStrokeColor(black)
    canvas.setLineWidth(0.7)
    canvas.setDash(2.2, 2.0)
    canvas.line(x0, y, x1, y)
    canvas.setDash()
    canvas.setLineWidth(1.0)
    tick = 5
    canvas.line(x0, y - tick, x0, y + tick)
    canvas.line(x1, y - tick, x1, y + tick)
    canvas.restoreState()
