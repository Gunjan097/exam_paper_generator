import random
from src.models.question import Question
from src.services.question_selector import select_questions


def _make_q(qid, number, variant, class_, subject, medium, marks=2):
    return Question(
        question_id=qid, number=number, variant=variant,
        class_=class_, subject=subject, medium=medium,
        text=f"Question {qid}", image_path=None,
        answer=f"Answer {qid}", marks=marks,
    )


BANK = [
    _make_q("1A", 1, "A", "10", "Science", "English"),
    _make_q("1B", 1, "B", "10", "Science", "English"),
    _make_q("1C", 1, "C", "10", "Science", "English"),
    _make_q("2A", 2, "A", "10", "Science", "English"),
    _make_q("2B", 2, "B", "10", "Science", "English"),
    _make_q("3A", 3, "A", "10", "Science", "English", marks=5),
    _make_q("3B", 3, "B", "10", "Science", "English", marks=5),
    _make_q("1A", 1, "A", "9",  "Science", "English"),  # different class
    _make_q("4A", 4, "A", "10", "Science", "Hindi"),    # different medium
]


def test_returns_one_question_per_number():
    sections, warnings = select_questions(BANK, "10", "Science", "English")
    all_questions = [q for qs in sections.values() for q in qs]
    numbers = [q.number for q in all_questions]
    assert sorted(numbers) == [1, 2, 3]


def test_filters_by_class_subject_medium():
    sections, warnings = select_questions(BANK, "10", "Science", "English")
    all_questions = [q for qs in sections.values() for q in qs]
    for q in all_questions:
        assert q.class_ == "10"
        assert q.subject == "Science"
        assert q.medium == "English"


def test_groups_by_marks():
    sections, warnings = select_questions(BANK, "10", "Science", "English")
    assert 2 in sections
    assert 5 in sections
    assert len(sections[2]) == 2  # Q1 and Q2
    assert len(sections[5]) == 1  # Q3


def test_selected_variant_is_valid():
    sections, warnings = select_questions(BANK, "10", "Science", "English")
    all_questions = [q for qs in sections.values() for q in qs]
    for q in all_questions:
        assert q.variant in ("A", "B", "C")


def test_different_seeds_can_give_different_variants():
    results = set()
    for _ in range(20):
        sections, _ = select_questions(BANK, "10", "Science", "English")
        q1 = next(q for qs in sections.values() for q in qs if q.number == 1)
        results.add(q1.variant)
    assert len(results) > 1  # randomness works


def test_works_with_single_variant():
    bank = [_make_q("2A", 2, "A", "10", "Science", "English")]
    sections, warnings = select_questions(bank, "10", "Science", "English")
    all_questions = [q for qs in sections.values() for q in qs]
    assert len(all_questions) == 1
    assert all_questions[0].variant == "A"


def test_no_match_returns_warning():
    sections, warnings = select_questions(BANK, "99", "Physics", "Hindi")
    assert sections == {}
    assert len(warnings) == 0  # no question numbers expected, so no "missing" warnings


def test_sections_sorted_by_marks_ascending():
    sections, _ = select_questions(BANK, "10", "Science", "English")
    keys = list(sections.keys())
    assert keys == sorted(keys)
