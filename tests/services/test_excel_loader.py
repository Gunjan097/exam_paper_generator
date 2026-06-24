from src.services.excel_loader import load_questions


def test_load_returns_question_objects(sample_xlsx):
    questions = load_questions(sample_xlsx)
    assert len(questions) == 7


def test_question_fields_parsed_correctly(sample_xlsx):
    questions = load_questions(sample_xlsx)
    q = next(q for q in questions if q.question_id == "1A" and q.class_ == "10")
    assert q.number == 1
    assert q.variant == "A"
    assert q.class_ == "10"
    assert q.subject == "Science"
    assert q.medium == "English"
    assert q.text == "Define photosynthesis."
    assert q.image_path is None
    assert q.answer == "Light to glucose."
    assert q.marks == 2


def test_image_path_populated(sample_xlsx):
    questions = load_questions(sample_xlsx)
    q = next(q for q in questions if q.question_id == "2A")
    assert q.image_path == "images/q2a.png"


def test_empty_image_path_is_none(sample_xlsx):
    questions = load_questions(sample_xlsx)
    q = next(q for q in questions if q.question_id == "1B")
    assert q.image_path is None


def test_hindi_question_loaded(sample_xlsx):
    questions = load_questions(sample_xlsx)
    q = next(q for q in questions if q.question_id == "3A")
    assert q.medium == "Hindi"
    assert "प्रकाश" in q.text


def test_invalid_question_id_skipped(invalid_row_xlsx):
    questions = load_questions(invalid_row_xlsx)
    ids = [q.question_id for q in questions]
    assert "BADID" not in ids
    assert "1A" in ids
    assert "2B" in ids
    assert len(questions) == 2
