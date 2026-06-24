import re
import warnings
import openpyxl
from src.models.question import Question

_ID_RE = re.compile(r'^(\d+)([A-Za-z])$')
_REQUIRED_COLS = {
    "question id", "class", "subject", "medium",
    "question", "image path", "answer", "marks",
}


def load_questions(file_path: str) -> list[Question]:
    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []

    headers = [str(h).strip().lower() if h is not None else "" for h in rows[0]]
    missing = _REQUIRED_COLS - set(headers)
    if missing:
        raise ValueError(f"Excel file is missing required columns: {missing}")

    idx = {name: headers.index(name) for name in _REQUIRED_COLS}
    questions = []

    for row_num, row in enumerate(rows[1:], start=2):
        raw_id = str(row[idx["question id"]]).strip() if row[idx["question id"]] is not None else ""
        match = _ID_RE.match(raw_id)
        if not match:
            warnings.warn(f"Row {row_num}: invalid Question ID '{raw_id}', skipping.")
            continue

        number = int(match.group(1))
        variant = match.group(2).upper()
        image_raw = row[idx["image path"]]
        image_path = str(image_raw).strip() if image_raw else None
        if image_path == "":
            image_path = None

        questions.append(Question(
            question_id=raw_id,
            number=number,
            variant=variant,
            class_=str(row[idx["class"]]).strip(),
            subject=str(row[idx["subject"]]).strip(),
            medium=str(row[idx["medium"]]).strip(),
            text=str(row[idx["question"]]).strip(),
            image_path=image_path,
            answer=str(row[idx["answer"]]).strip(),
            marks=int(row[idx["marks"]]),
        ))

    return questions
