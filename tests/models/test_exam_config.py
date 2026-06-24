from src.models.exam_config import ExamConfig


def test_exam_config_basic():
    cfg = ExamConfig(
        school_name="Springfield High",
        exam_name="Annual Exam 2026",
        class_="10",
        subject="Science",
        medium="English",
        date="2026-06-24",
        duration="3 hours",
        max_marks=80,
        instructions=["Attempt all questions.", "Use blue pen."],
        page_format="A4",
        custom_width_mm=None,
        custom_height_mm=None,
    )
    assert cfg.school_name == "Springfield High"
    assert cfg.max_marks == 80
    assert len(cfg.instructions) == 2
    assert cfg.page_format == "A4"
    assert cfg.custom_width_mm is None


def test_exam_config_custom_page():
    cfg = ExamConfig(
        school_name="S", exam_name="E", class_="9", subject="Math",
        medium="Hindi", date="2026-01-01", duration="2 hours",
        max_marks=50, instructions=[], page_format="Custom",
        custom_width_mm=210, custom_height_mm=297,
    )
    assert cfg.page_format == "Custom"
    assert cfg.custom_width_mm == 210
    assert cfg.custom_height_mm == 297
