import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from src.models.question import Question
from src.models.exam_config import ExamConfig
from src.utils.asset_path import get_asset_path


def _get_jinja_env() -> Environment:
    templates_dir = get_asset_path(os.path.join("assets", "templates"))
    return Environment(loader=FileSystemLoader(templates_dir), autoescape=True)


def _prepare_sections(
    sections: dict[int, list[Question]],
    excel_dir: str,
    include_images: bool,
) -> tuple[list[dict], list[str]]:
    result = []
    warnings = []
    for idx, marks in enumerate(sorted(sections.keys())):
        questions = []
        for q in sections[marks]:
            image_uri = None
            if include_images and q.image_path:
                abs_path = os.path.normpath(os.path.join(excel_dir, q.image_path))
                if os.path.exists(abs_path):
                    image_uri = Path(abs_path).as_uri()
                else:
                    warnings.append(f"Image not found: {q.image_path}")
            questions.append({
                "number": q.number,
                "text": q.text,
                "marks": q.marks,
                "image_uri": image_uri,
                "answer": q.answer,
            })
        result.append({
            "letter": chr(65 + idx),
            "marks": marks,
            "questions": questions,
        })
    return result, warnings


def build_paper_html(
    sections: dict[int, list[Question]],
    config: ExamConfig,
    excel_dir: str,
    font_path: str,
) -> tuple[str, list[str]]:
    sections_list, warnings = _prepare_sections(sections, excel_dir, include_images=True)
    font_uri = Path(font_path).as_uri()
    env = _get_jinja_env()
    template = env.get_template("paper.html")
    html = template.render(
        config=config,
        sections=sections_list,
        font_uri=font_uri,
    )
    return html, warnings


def build_answer_key_html(
    sections: dict[int, list[Question]],
    config: ExamConfig,
    font_path: str,
) -> str:
    sections_list, _ = _prepare_sections(sections, "", include_images=False)
    font_uri = Path(font_path).as_uri()
    env = _get_jinja_env()
    template = env.get_template("answer_key.html")
    return template.render(
        config=config,
        sections=sections_list,
        font_uri=font_uri,
    )
