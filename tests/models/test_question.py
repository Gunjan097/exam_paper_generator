from src.models.question import Question


def test_question_fields():
    q = Question(
        question_id="1A",
        number=1,
        variant="A",
        class_="10",
        subject="Science",
        medium="English",
        text="Define photosynthesis.",
        image_path=None,
        answer="Process of converting light energy into glucose.",
        marks=2,
    )
    assert q.question_id == "1A"
    assert q.number == 1
    assert q.variant == "A"
    assert q.image_path is None
    assert q.marks == 2


def test_question_with_image():
    q = Question(
        question_id="2A", number=2, variant="A", class_="10",
        subject="Science", medium="English", text="Label the diagram.",
        image_path="images/q2a.png", answer="See diagram.", marks=3,
    )
    assert q.image_path == "images/q2a.png"
