from dataclasses import dataclass


@dataclass
class Question:
    question_id: str
    number: int
    variant: str
    class_: str
    subject: str
    medium: str
    text: str
    image_path: str | None
    answer: str
    marks: int
