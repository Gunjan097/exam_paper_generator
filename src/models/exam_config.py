from dataclasses import dataclass


@dataclass
class ExamConfig:
    school_name: str
    exam_name: str
    class_: str
    subject: str
    medium: str
    date: str
    duration: str
    max_marks: int
    instructions: list[str]
    page_format: str
    custom_width_mm: int | None
    custom_height_mm: int | None
