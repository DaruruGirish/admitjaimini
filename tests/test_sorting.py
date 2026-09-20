from services.excel_reader import RawStudent
from services.student_processor import group_students
from utils.sorting import natural_key, sort_students


def test_natural_sort_orders_embedded_numbers():
    rolls = ["JPS260305", "JPS260301", "JPS260310", "JPS260302"]
    assert sorted(rolls, key=natural_key) == [
        "JPS260301",
        "JPS260302",
        "JPS260305",
        "JPS260310",
    ]


def test_students_sorted_by_roll_and_grouped_by_grade():
    students = [
        RawStudent("B", "JPS260205", "2", "2nd", 2),
        RawStudent("A", "JPS260201", "2", "2nd", 3),
        RawStudent("C", "JPS260310", "3", "3rd", 2),
        RawStudent("D", "JPS260301", "3", "3rd", 3),
    ]
    grouped = group_students(students)
    assert list(grouped.keys()) == ["2", "3"]
    assert [item.roll_no for item in grouped["3"]] == ["JPS260301", "JPS260310"]
    assert [item.roll_no for item in grouped["2"]] == ["JPS260201", "JPS260205"]
    assert [item.roll_no for item in sort_students(students)][0] == "JPS260201"
