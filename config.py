from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "school_logo.png"
COLOR_LOGO_PATH = ASSETS_DIR / "school_logo_color.png"

SCHOOL_NAME = "JAIMINI PUBLIC SCHOOL, HIRIYUR."
EXAM_NAME = "SUMMATIVE ASSESSMENT (SA) - 1"
ACADEMIC_YEAR = "2026 - 27"
CARD_TITLE = "ADMIT CARD"

HEADMISTRESS_NAME = "Seamanthini"
HEADMISTRESS_LABEL = "Headmistress Sign."
STUDENT_SIGN_LABEL = "Student's Sign."
TEACHER_SIGN_LABEL = "Class Teacher's Sign."
PHOTO_LABEL = "PHOTO"

REQUIRED_COLUMNS = ("Roll No", "Name", "Grade")

HEADER_ALIASES = {
    "roll no": "roll_no",
    "roll no.": "roll_no",
    "roll_no": "roll_no",
    "roll number": "roll_no",
    "rollnumber": "roll_no",
    "name": "name",
    "student name": "name",
    "student": "name",
    "grade": "grade",
    "class": "grade",
    "std": "grade",
}

EXAM_SCHEDULE = [
    {
        "sl_no": "1",
        "date": "23-09-2026",
        "subject": "KANNADA",
        "written": "10:30AM to 12:00PM",
        "oral": "1:00PM TO 4:00PM",
    },
    {
        "sl_no": "2",
        "date": "24-09-2026",
        "subject": "MATHEMATICS",
        "written": "10:30AM to 12:00PM",
        "oral": "1:00PM TO 4:00PM",
    },
    {
        "sl_no": "3",
        "date": "25-09-2026",
        "subject": "ENGLISH",
        "written": "10:30AM to 12:00PM",
        "oral": "1:00PM TO 4:00PM",
    },
    {
        "sl_no": "4",
        "date": "26-09-2026",
        "subject": "Drawing/ PE",
        "written": "10:30AM to 12:00PM",
        "oral": "",
    },
    {
        "sl_no": "5",
        "date": "28-09-2026",
        "subject": "EVS",
        "written": "10:30AM to 12:00PM",
        "oral": "1:00PM TO 4:00PM",
    },
    {
        "sl_no": "6",
        "date": "29-09-2026",
        "subject": "HINDI",
        "written": "10:30AM to 12:00PM",
        "oral": "1:00PM TO 4:00PM",
    },
]

WINDOWS_SERIF_REGULAR = Path(r"C:\Windows\Fonts\times.ttf")
WINDOWS_SERIF_BOLD = Path(r"C:\Windows\Fonts\timesbd.ttf")
WINDOWS_SCRIPT = Path(r"C:\Windows\Fonts\segoesc.ttf")
