import random
from collections import defaultdict
from src.models.question import Question


def select_questions(
    questions: list[Question],
    class_: str,
    subject: str,
    medium: str,
) -> tuple[dict[int, list[Question]], list[str]]:
    """Filter, randomly pick one variant per number, group by marks.

    Returns:
        sections: {marks: [Question, ...]} sorted by marks ascending
        warnings: list of human-readable warning strings
    """
    filtered = [
        q for q in questions
        if q.class_ == class_ and q.subject == subject and q.medium == medium
    ]

    by_number: dict[int, list[Question]] = defaultdict(list)
    for q in filtered:
        by_number[q.number].append(q)

    selected: list[Question] = []
    warnings: list[str] = []

    for number in sorted(by_number.keys()):
        variants = by_number[number]
        if not variants:
            warnings.append(f"Question {number}: no variants found after filtering.")
            continue
        selected.append(random.choice(variants))

    by_marks: dict[int, list[Question]] = defaultdict(list)
    for q in selected:
        by_marks[q.marks].append(q)

    sections = dict(sorted(by_marks.items()))
    return sections, warnings
