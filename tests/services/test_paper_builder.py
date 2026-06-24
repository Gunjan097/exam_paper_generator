import os
from pathlib import Path
from src.models.question import Question
from src.models.exam_config import ExamConfig
from src.services.paper_builder import build_paper_html, build_answer_key_html


def _make_config():
    return ExamConfig(
        school_name="Test High School",
        exam_name="Unit Test Exam",
        class_="10", subject="Science", medium="English",
        date="2026-06-24", duration="3 hours", max_marks=80,
        instructions=["Attempt all questions."],
        page_format="A4", custom_width_mm=None, custom_height_mm=None,
    )


def _make_sections():
    return {
        2: [
            Question("1A", 1, "A", "10", "Science", "English",
                     "Define photosynthesis.", None, "Light to glucose.", 2),
        ],
        5: [
            Question("2A", 2, "A", "10", "Science", "English",
                     "Explain the water cycle.", None, "Evaporation and condensation.", 5),
        ],
    }


DUMMY_FONT = "/nonexistent/font.ttf"


def test_html_contains_school_name():
    html, _ = build_paper_html(_make_sections(), _make_config(), "/tmp", DUMMY_FONT)
    assert "Test High School" in html


def test_html_contains_exam_name():
    html, _ = build_paper_html(_make_sections(), _make_config(), "/tmp", DUMMY_FONT)
    assert "Unit Test Exam" in html


def test_html_contains_section_headers():
    html, _ = build_paper_html(_make_sections(), _make_config(), "/tmp", DUMMY_FONT)
    assert "Section A" in html
    assert "Section B" in html


def test_html_contains_question_text():
    html, _ = build_paper_html(_make_sections(), _make_config(), "/tmp", DUMMY_FONT)
    assert "Define photosynthesis." in html
    assert "Explain the water cycle." in html


def test_html_contains_font_uri():
    html, _ = build_paper_html(_make_sections(), _make_config(), "/tmp", DUMMY_FONT)
    assert "font.ttf" in html


def test_html_no_img_tag_when_no_image():
    html, _ = build_paper_html(_make_sections(), _make_config(), "/tmp", DUMMY_FONT)
    assert "<img" not in html


def test_html_contains_img_tag_when_image_exists(tmp_path):
    img_file = tmp_path / "q1a.png"
    img_file.write_bytes(b"fake")
    sections = {
        2: [Question("1A", 1, "A", "10", "Science", "English",
                     "Label the diagram.", "q1a.png", "See diagram.", 2)]
    }
    html, warnings = build_paper_html(sections, _make_config(), str(tmp_path), DUMMY_FONT)
    assert "<img" in html
    assert "q1a.png" in html
    assert warnings == []


def test_missing_image_produces_warning(tmp_path):
    sections = {
        2: [Question("1A", 1, "A", "10", "Science", "English",
                     "Label the diagram.", "missing.png", "See diagram.", 2)]
    }
    html, warnings = build_paper_html(sections, _make_config(), str(tmp_path), DUMMY_FONT)
    assert "<img" not in html
    assert len(warnings) == 1
    assert "missing.png" in warnings[0]


def test_answer_key_contains_answers():
    html = build_answer_key_html(_make_sections(), _make_config(), DUMMY_FONT)
    assert "Light to glucose." in html
    assert "Evaporation and condensation." in html


def test_answer_key_contains_answer_key_label():
    html = build_answer_key_html(_make_sections(), _make_config(), DUMMY_FONT)
    assert "Answer Key" in html


def test_instructions_appear_in_paper():
    html, _ = build_paper_html(_make_sections(), _make_config(), "/tmp", DUMMY_FONT)
    assert "Attempt all questions." in html
