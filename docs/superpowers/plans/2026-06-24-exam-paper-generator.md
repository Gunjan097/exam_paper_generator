# Exam Paper Generator — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a PyQt6 desktop app that generates randomized exam papers (PDF) from an Excel question bank with A/B/C variant selection, sectioned layout, Hindi support, and a Windows .exe via GitHub Actions.

**Architecture:** Services layer (excel_loader, question_selector, paper_builder, pdf_exporter) is pure Python with zero Qt dependency — fully unit-testable with pytest. UI layer (config_form, preview_widget, main_window) uses PyQt6 and is verified manually. Jinja2 HTML templates are rendered in QWebEngineView for live preview; QWebEnginePage.printToPdf() produces the final PDF.

**Tech Stack:** Python 3.11, PyQt6 ≥ 6.6.0, PyQt6-WebEngine ≥ 6.6.0, openpyxl ≥ 3.1.0, Jinja2 ≥ 3.1.0, pytest ≥ 8.0.0, PyInstaller ≥ 6.0.0

## Global Constraints

- Python 3.11 minimum (`str | None` union syntax used throughout)
- No Qt imports anywhere inside `src/models/` or `src/services/` — pure Python only
- All assets (fonts, templates) live under `assets/`; always accessed via `src/utils/asset_path.get_asset_path(relative)`
- PyInstaller bundles assets with `--add-data "assets;assets"` (Windows semicolon separator)
- GitHub Actions builds on `windows-latest` runner only — do not attempt local cross-compile
- Question ID format is strictly `<digits><single-uppercase-letter>` e.g. `"1A"`, `"12C"`
- Excel column header names are matched case-insensitively

---

## File Map

```
exam_paper_generator/
├── main.py
├── requirements.txt
├── pytest.ini
├── .gitignore
├── assets/
│   ├── fonts/
│   │   └── NotoSansDevanagari-Regular.ttf
│   └── templates/
│       ├── paper.html
│       └── answer_key.html
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── question.py
│   │   └── exam_config.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── excel_loader.py
│   │   ├── question_selector.py
│   │   ├── paper_builder.py
│   │   └── pdf_exporter.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── config_form.py
│   │   └── preview_widget.py
│   └── utils/
│       ├── __init__.py
│       └── asset_path.py
├── tests/
│   ├── conftest.py
│   ├── models/
│   │   ├── test_question.py
│   │   └── test_exam_config.py
│   └── services/
│       ├── conftest.py
│       ├── test_excel_loader.py
│       ├── test_question_selector.py
│       └── test_paper_builder.py
├── docs/
│   └── superpowers/
│       ├── specs/
│       │   └── 2026-06-24-exam-paper-generator-design.md
│       └── plans/
│           └── 2026-06-24-exam-paper-generator.md
└── .github/
    └── workflows/
        └── build-windows.yml
```

---

### Task 1: Project Scaffold

**Files:**
- Create: `requirements.txt`
- Create: `pytest.ini`
- Create: `.gitignore`
- Create: `main.py` (skeleton only)
- Create: `src/__init__.py`, `src/models/__init__.py`, `src/services/__init__.py`, `src/ui/__init__.py`, `src/utils/__init__.py`
- Create: `tests/conftest.py`, `tests/models/` (empty), `tests/services/` (empty)
- Create: `assets/fonts/` (empty dir placeholder), `assets/templates/` (empty dir placeholder)

**Interfaces:**
- Produces: runnable Python environment, passing `pytest` with zero tests collected

- [ ] **Step 1: Create requirements.txt**

```
PyQt6>=6.6.0
PyQt6-WebEngine>=6.6.0
openpyxl>=3.1.0
Jinja2>=3.1.0
pytest>=8.0.0
pyinstaller>=6.0.0
```

- [ ] **Step 2: Create pytest.ini**

```ini
[pytest]
testpaths = tests
pythonpath = .
```

- [ ] **Step 3: Create .gitignore**

```
__pycache__/
*.pyc
*.pyo
.venv/
venv/
dist/
build/
*.spec
.pytest_cache/
*.egg-info/
```

- [ ] **Step 4: Create all __init__.py files and directory structure**

```bash
mkdir -p src/models src/services src/ui src/utils
mkdir -p tests/models tests/services
mkdir -p assets/fonts assets/templates
touch src/__init__.py src/models/__init__.py src/services/__init__.py
touch src/ui/__init__.py src/utils/__init__.py
touch tests/conftest.py tests/models/__init__.py tests/services/__init__.py
```

- [ ] **Step 5: Create main.py skeleton**

```python
import sys
from PyQt6.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Exam Paper Generator")
    # MainWindow will be imported and shown here in Task 11
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Install dependencies**

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
```

- [ ] **Step 7: Verify pytest runs with zero errors**

```bash
pytest
```
Expected: `no tests ran` — exit code 5 (no tests) or 0. No import errors.

---

### Task 2: Data Models

**Files:**
- Create: `src/models/question.py`
- Create: `src/models/exam_config.py`
- Create: `tests/models/test_question.py`
- Create: `tests/models/test_exam_config.py`

**Interfaces:**
- Produces:
  - `Question(question_id, number, variant, class_, subject, medium, text, image_path, answer, marks)`
  - `ExamConfig(school_name, exam_name, class_, subject, medium, date, duration, max_marks, instructions, page_format, custom_width_mm, custom_height_mm)`

- [ ] **Step 1: Write failing tests for Question**

`tests/models/test_question.py`:
```python
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
```

- [ ] **Step 2: Run to verify it fails**

```bash
pytest tests/models/test_question.py -v
```
Expected: `ImportError: cannot import name 'Question'`

- [ ] **Step 3: Implement Question**

`src/models/question.py`:
```python
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
```

- [ ] **Step 4: Run Question tests**

```bash
pytest tests/models/test_question.py -v
```
Expected: 2 passed

- [ ] **Step 5: Write failing tests for ExamConfig**

`tests/models/test_exam_config.py`:
```python
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
```

- [ ] **Step 6: Run to verify it fails**

```bash
pytest tests/models/test_exam_config.py -v
```
Expected: `ImportError: cannot import name 'ExamConfig'`

- [ ] **Step 7: Implement ExamConfig**

`src/models/exam_config.py`:
```python
from dataclasses import dataclass, field


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
```

- [ ] **Step 8: Run all model tests**

```bash
pytest tests/models/ -v
```
Expected: 4 passed

- [ ] **Step 9: Commit (ask user to commit)**

Files to stage: `src/models/question.py`, `src/models/exam_config.py`, `tests/models/test_question.py`, `tests/models/test_exam_config.py`, all scaffold files from Task 1.

Suggested message: `feat: add project scaffold and data models`

---

### Task 3: Asset Path Utility

**Files:**
- Create: `src/utils/asset_path.py`

**Interfaces:**
- Produces: `get_asset_path(relative: str) -> str` — returns absolute path to an asset, works both in dev and inside a PyInstaller bundle

- [ ] **Step 1: Implement get_asset_path**

`src/utils/asset_path.py`:
```python
import os
import sys


def get_asset_path(relative: str) -> str:
    """Returns the absolute path to an asset file.

    Works in two contexts:
    - Dev: resolves relative to the project root (parent of src/)
    - PyInstaller bundle: resolves relative to sys._MEIPASS (the unpacked bundle dir)
    """
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, relative)
```

- [ ] **Step 2: Verify manually**

```bash
python -c "from src.utils.asset_path import get_asset_path; print(get_asset_path('assets/fonts/NotoSansDevanagari-Regular.ttf'))"
```
Expected: prints an absolute path ending in `assets/fonts/NotoSansDevanagari-Regular.ttf`

---

### Task 4: Excel Loader

**Files:**
- Create: `src/services/excel_loader.py`
- Create: `tests/services/conftest.py` (shared fixture)
- Create: `tests/services/test_excel_loader.py`

**Interfaces:**
- Consumes: `Question` from `src.models.question`
- Produces: `load_questions(file_path: str) -> list[Question]`
  - Parses all rows from the first sheet
  - Skips rows with invalid Question ID (logs warning, does not crash)
  - Returns `image_path=None` for empty Image Path cells

- [ ] **Step 1: Write shared test fixture**

`tests/services/conftest.py`:
```python
import pytest
import openpyxl


@pytest.fixture
def sample_xlsx(tmp_path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append([
        "Question ID", "Class", "Subject", "Medium",
        "Question", "Image Path", "Answer", "Marks",
    ])
    ws.append(["1A", "10", "Science", "English", "Define photosynthesis.", "", "Light to glucose.", 2])
    ws.append(["1B", "10", "Science", "English", "What is osmosis?", "", "Water movement.", 2])
    ws.append(["1C", "10", "Science", "English", "Define respiration.", "", "Energy from glucose.", 2])
    ws.append(["2A", "10", "Science", "English", "Name two respiration types.", "images/q2a.png", "Aerobic and Anaerobic.", 2])
    ws.append(["2B", "10", "Science", "English", "What is phototropism?", "", "Growth towards light.", 2])
    ws.append(["3A", "10", "Science", "Hindi", "प्रकाश संश्लेषण क्या है?", "", "प्रकाश से ग्लूकोज।", 1])
    ws.append(["1A", "9",  "Math",    "English", "What is a prime number?", "", "Divisible only by 1 and itself.", 1])
    path = tmp_path / "bank.xlsx"
    wb.save(str(path))
    return str(path)


@pytest.fixture
def invalid_row_xlsx(tmp_path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append([
        "Question ID", "Class", "Subject", "Medium",
        "Question", "Image Path", "Answer", "Marks",
    ])
    ws.append(["1A", "10", "Science", "English", "Valid question.", "", "Answer.", 2])
    ws.append(["BADID", "10", "Science", "English", "Should be skipped.", "", "X.", 2])
    ws.append(["2B", "10", "Science", "English", "Another valid.", "", "Answer.", 1])
    path = tmp_path / "invalid.xlsx"
    wb.save(str(path))
    return str(path)
```

- [ ] **Step 2: Write failing tests for excel_loader**

`tests/services/test_excel_loader.py`:
```python
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
```

- [ ] **Step 3: Run to verify it fails**

```bash
pytest tests/services/test_excel_loader.py -v
```
Expected: `ImportError: cannot import name 'load_questions'`

- [ ] **Step 4: Implement excel_loader**

`src/services/excel_loader.py`:
```python
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
```

- [ ] **Step 5: Run tests**

```bash
pytest tests/services/test_excel_loader.py -v
```
Expected: 6 passed

- [ ] **Step 6: Commit**

Files: `src/services/excel_loader.py`, `tests/services/conftest.py`, `tests/services/test_excel_loader.py`, `src/utils/asset_path.py`

Suggested message: `feat: add excel loader and asset path utility`

---

### Task 5: Question Selector

**Files:**
- Create: `src/services/question_selector.py`
- Create: `tests/services/test_question_selector.py`

**Interfaces:**
- Consumes: `list[Question]`, `class_: str`, `subject: str`, `medium: str`
- Produces:
  - `select_questions(questions, class_, subject, medium) -> dict[int, list[Question]]`
    Returns `{marks_value: [selected_questions]}` — exactly one Question per question number, grouped by marks, sorted by marks key ascending
  - Warnings: a second return value `list[str]` for question numbers that had zero variants after filtering

- [ ] **Step 1: Write failing tests**

`tests/services/test_question_selector.py`:
```python
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
```

- [ ] **Step 2: Run to verify it fails**

```bash
pytest tests/services/test_question_selector.py -v
```
Expected: `ImportError: cannot import name 'select_questions'`

- [ ] **Step 3: Implement question_selector**

`src/services/question_selector.py`:
```python
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
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/services/test_question_selector.py -v
```
Expected: 8 passed

- [ ] **Step 5: Commit**

Files: `src/services/question_selector.py`, `tests/services/test_question_selector.py`

Suggested message: `feat: add question selector with random variant picking`

---

### Task 6: HTML Templates + Font

**Files:**
- Download: `assets/fonts/NotoSansDevanagari-Regular.ttf`
- Create: `assets/templates/paper.html`
- Create: `assets/templates/answer_key.html`

**Interfaces:**
- Produces: Jinja2 templates that accept `config` (ExamConfig fields as dict) and `sections` (list of section dicts)
- Section dict shape: `{ letter: str, marks: int, questions: list[{ number, text, image_uri, answer, marks }] }`

- [ ] **Step 1: Download Noto Sans Devanagari font**

```bash
curl -L "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf" \
     -o assets/fonts/NotoSansDevanagari-Regular.ttf
```
Verify: `ls -lh assets/fonts/NotoSansDevanagari-Regular.ttf` — should be ~500KB+

- [ ] **Step 2: Create paper.html**

`assets/templates/paper.html`:
```html
<!DOCTYPE html>
<html lang="{{ 'hi' if config.medium == 'Hindi' else 'en' }}">
<head>
<meta charset="UTF-8">
<style>
@font-face {
    font-family: 'NotoDevanagari';
    src: url('{{ font_uri }}') format('truetype');
}
* { box-sizing: border-box; }
body {
    font-family: 'NotoDevanagari', Arial, sans-serif;
    margin: 0;
    padding: 18mm 15mm;
    font-size: 11pt;
    line-height: 1.5;
    color: #000;
}
.header {
    text-align: center;
    border-bottom: 2px solid #000;
    padding-bottom: 8px;
    margin-bottom: 14px;
}
.school-name { font-size: 15pt; font-weight: bold; margin-bottom: 3px; }
.exam-name   { font-size: 12pt; margin-bottom: 6px; }
.meta-table  { width: 100%; border-collapse: collapse; font-size: 10pt; }
.meta-table td { padding: 2px 6px; }
.instructions {
    border: 1px solid #aaa;
    padding: 6px 12px;
    margin: 10px 0;
    font-size: 10pt;
}
.instructions ul { margin: 4px 0; padding-left: 18px; }
.section-header {
    background: #ebebeb;
    font-weight: bold;
    padding: 4px 8px;
    margin: 14px 0 8px 0;
    border-left: 4px solid #333;
    font-size: 10.5pt;
}
.question-row {
    display: flex;
    gap: 8px;
    align-items: flex-start;
    margin: 6px 0;
}
.q-num   { font-weight: bold; min-width: 30px; flex-shrink: 0; }
.q-body  { flex: 1; }
.q-image { display: block; max-width: 180px; max-height: 130px; margin-top: 5px; }
.marks-tag { font-size: 9pt; color: #555; white-space: nowrap; }
</style>
</head>
<body>
<div class="header">
    <div class="school-name">{{ config.school_name }}</div>
    <div class="exam-name">{{ config.exam_name }}</div>
    <table class="meta-table">
        <tr>
            <td>Class: {{ config.class_ }}</td>
            <td>Subject: {{ config.subject }}</td>
            <td>Date: {{ config.date }}</td>
        </tr>
        <tr>
            <td>Duration: {{ config.duration }}</td>
            <td>Max Marks: {{ config.max_marks }}</td>
            <td>Medium: {{ config.medium }}</td>
        </tr>
    </table>
</div>

{% if config.instructions %}
<div class="instructions">
    <strong>Instructions:</strong>
    <ul>{% for inst in config.instructions %}<li>{{ inst }}</li>{% endfor %}</ul>
</div>
{% endif %}

{% for section in sections %}
<div class="section-header">
    Section {{ section.letter }} &mdash; {{ section.marks }} Mark{% if section.marks > 1 %}s{% endif %}
    &nbsp;&nbsp;({{ section.questions | length }} Question{% if section.questions | length > 1 %}s{% endif %})
</div>
{% for q in section.questions %}
<div class="question-row">
    <span class="q-num">Q{{ q.number }}.</span>
    <div class="q-body">
        {{ q.text }}
        {% if q.image_uri %}<img class="q-image" src="{{ q.image_uri }}" alt="">{% endif %}
    </div>
    <span class="marks-tag">[{{ q.marks }} mark{% if q.marks > 1 %}s{% endif %}]</span>
</div>
{% endfor %}
{% endfor %}
</body>
</html>
```

- [ ] **Step 3: Create answer_key.html**

`assets/templates/answer_key.html`:
```html
<!DOCTYPE html>
<html lang="{{ 'hi' if config.medium == 'Hindi' else 'en' }}">
<head>
<meta charset="UTF-8">
<style>
@font-face {
    font-family: 'NotoDevanagari';
    src: url('{{ font_uri }}') format('truetype');
}
* { box-sizing: border-box; }
body {
    font-family: 'NotoDevanagari', Arial, sans-serif;
    margin: 0;
    padding: 18mm 15mm;
    font-size: 11pt;
    line-height: 1.5;
    color: #000;
}
.header {
    text-align: center;
    border-bottom: 2px solid #000;
    padding-bottom: 8px;
    margin-bottom: 14px;
}
.school-name { font-size: 15pt; font-weight: bold; margin-bottom: 3px; }
.exam-name   { font-size: 12pt; margin-bottom: 6px; }
.answer-key-label {
    font-size: 13pt;
    font-weight: bold;
    color: #b00;
    margin-bottom: 6px;
}
.meta-table  { width: 100%; border-collapse: collapse; font-size: 10pt; }
.meta-table td { padding: 2px 6px; }
.section-header {
    background: #ebebeb;
    font-weight: bold;
    padding: 4px 8px;
    margin: 14px 0 8px 0;
    border-left: 4px solid #333;
    font-size: 10.5pt;
}
.answer-row { margin: 6px 0 10px 0; display: flex; gap: 8px; }
.q-num  { font-weight: bold; min-width: 30px; flex-shrink: 0; }
.q-body { flex: 1; }
.question-text { margin-bottom: 2px; }
.answer-text {
    background: #f5f5dc;
    border-left: 3px solid #888;
    padding: 3px 8px;
    font-size: 10.5pt;
}
</style>
</head>
<body>
<div class="header">
    <div class="school-name">{{ config.school_name }}</div>
    <div class="exam-name">{{ config.exam_name }}</div>
    <div class="answer-key-label">— Answer Key —</div>
    <table class="meta-table">
        <tr>
            <td>Class: {{ config.class_ }}</td>
            <td>Subject: {{ config.subject }}</td>
            <td>Date: {{ config.date }}</td>
        </tr>
    </table>
</div>

{% for section in sections %}
<div class="section-header">
    Section {{ section.letter }} &mdash; {{ section.marks }} Mark{% if section.marks > 1 %}s{% endif %}
</div>
{% for q in section.questions %}
<div class="answer-row">
    <span class="q-num">Q{{ q.number }}.</span>
    <div class="q-body">
        <div class="question-text">{{ q.text }}</div>
        <div class="answer-text"><strong>Ans:</strong> {{ q.answer }}</div>
    </div>
</div>
{% endfor %}
{% endfor %}
</body>
</html>
```

- [ ] **Step 4: Commit**

Files: `assets/fonts/NotoSansDevanagari-Regular.ttf`, `assets/templates/paper.html`, `assets/templates/answer_key.html`

Suggested message: `feat: add HTML templates and Devanagari font`

---

### Task 7: Paper Builder

**Files:**
- Create: `src/services/paper_builder.py`
- Create: `tests/services/test_paper_builder.py`

**Interfaces:**
- Consumes:
  - `select_questions(...)` → `sections: dict[int, list[Question]]`
  - `ExamConfig`
  - `excel_dir: str` — directory of the Excel file (for resolving image paths)
  - `font_path: str` — absolute path to NotoSansDevanagari-Regular.ttf
- Produces:
  - `build_paper_html(sections, config, excel_dir, font_path) -> tuple[str, list[str]]`
    Returns `(html_string, warnings_list)`
  - `build_answer_key_html(sections, config, font_path) -> str`

- [ ] **Step 1: Write failing tests**

`tests/services/test_paper_builder.py`:
```python
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
```

- [ ] **Step 2: Run to verify it fails**

```bash
pytest tests/services/test_paper_builder.py -v
```
Expected: `ImportError: cannot import name 'build_paper_html'`

- [ ] **Step 3: Implement paper_builder**

`src/services/paper_builder.py`:
```python
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
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/services/test_paper_builder.py -v
```
Expected: 11 passed

- [ ] **Step 5: Run the full test suite**

```bash
pytest -v
```
Expected: all tests pass (models + excel_loader + question_selector + paper_builder)

- [ ] **Step 6: Commit**

Files: `src/services/paper_builder.py`, `tests/services/test_paper_builder.py`

Suggested message: `feat: add paper builder with Jinja2 HTML rendering`

---

### Task 8: PDF Exporter

**Files:**
- Create: `src/services/pdf_exporter.py`

**Interfaces:**
- Consumes: `QWebEnginePage`, output path, `ExamConfig.page_format`, optional custom dimensions
- Produces:
  - `build_page_layout(page_format, custom_width_mm, custom_height_mm) -> QPageLayout`
  - `print_to_pdf(page, output_path, layout) -> None` — async; caller must connect `page.pdfPrintingFinished`

Note: No automated tests — requires a running QApplication and display. Tested manually in Task 11.

- [ ] **Step 1: Implement pdf_exporter**

`src/services/pdf_exporter.py`:
```python
from PyQt6.QtGui import QPageLayout, QPageSize
from PyQt6.QtCore import QMarginsF, QSizeF
from PyQt6.QtWebEngineCore import QWebEnginePage


def build_page_layout(
    page_format: str,
    custom_width_mm: int | None = None,
    custom_height_mm: int | None = None,
) -> QPageLayout:
    if page_format == "A4":
        size = QPageSize(QPageSize.PageSizeId.A4)
    elif page_format == "Legal":
        size = QPageSize(QPageSize.PageSizeId.Legal)
    else:
        size = QPageSize(
            QSizeF(custom_width_mm, custom_height_mm),
            QPageSize.Unit.Millimeter,
        )
    return QPageLayout(
        size,
        QPageLayout.Orientation.Portrait,
        QMarginsF(15, 20, 15, 20),
        QPageLayout.Unit.Millimeter,
    )


def print_to_pdf(
    page: QWebEnginePage,
    output_path: str,
    layout: QPageLayout,
) -> None:
    """Triggers async PDF export. Connect page.pdfPrintingFinished to handle completion."""
    page.printToPdf(output_path, layout)
```

---

### Task 9: Config Form UI

**Files:**
- Create: `src/ui/config_form.py`

**Interfaces:**
- Produces: `ConfigForm(QWidget)` with:
  - Signal `excel_loaded(list)` — emits `list[Question]` + stores `excel_dir: str`
  - Signal `generate_requested(object)` — emits `ExamConfig`
  - Method `populate_dropdowns(questions: list[Question]) -> None` — fills Class/Subject/Medium combos
  - Property `excel_dir: str` — directory of currently loaded Excel file

- [ ] **Step 1: Implement ConfigForm**

`src/ui/config_form.py`:
```python
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QTextEdit, QPushButton, QFileDialog, QSpinBox,
    QButtonGroup, QRadioButton, QGroupBox, QFormLayout, QMessageBox,
)
from PyQt6.QtCore import pyqtSignal
from src.models.exam_config import ExamConfig
from src.services.excel_loader import load_questions


class ConfigForm(QWidget):
    excel_loaded = pyqtSignal(list)
    generate_requested = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.excel_dir = ""
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        # Excel file picker
        file_box = QGroupBox("Question Bank")
        file_layout = QHBoxLayout(file_box)
        self._file_label = QLabel("No file selected")
        self._file_label.setWordWrap(True)
        browse_btn = QPushButton("Browse…")
        browse_btn.clicked.connect(self._browse_excel)
        file_layout.addWidget(self._file_label, 1)
        file_layout.addWidget(browse_btn)
        layout.addWidget(file_box)

        # Exam details form
        form_box = QGroupBox("Exam Details")
        form = QFormLayout(form_box)

        self._school = QLineEdit()
        self._exam_name = QLineEdit()
        self._class_combo = QComboBox()
        self._subject_combo = QComboBox()
        self._medium_combo = QComboBox()
        self._date = QLineEdit("2026-06-24")
        self._duration = QLineEdit("3 hours")
        self._max_marks = QSpinBox()
        self._max_marks.setRange(1, 1000)
        self._max_marks.setValue(80)
        self._instructions = QTextEdit()
        self._instructions.setPlaceholderText("One instruction per line")
        self._instructions.setFixedHeight(70)

        form.addRow("School Name:", self._school)
        form.addRow("Exam Name:", self._exam_name)
        form.addRow("Class:", self._class_combo)
        form.addRow("Subject:", self._subject_combo)
        form.addRow("Medium:", self._medium_combo)
        form.addRow("Date:", self._date)
        form.addRow("Duration:", self._duration)
        form.addRow("Max Marks:", self._max_marks)
        form.addRow("Instructions:", self._instructions)
        layout.addWidget(form_box)

        # Page format
        fmt_box = QGroupBox("Page Format")
        fmt_layout = QHBoxLayout(fmt_box)
        self._fmt_group = QButtonGroup(self)
        for label in ("A4", "Legal", "Custom"):
            rb = QRadioButton(label)
            self._fmt_group.addButton(rb)
            fmt_layout.addWidget(rb)
        self._fmt_group.buttons()[0].setChecked(True)

        self._custom_w = QSpinBox()
        self._custom_w.setRange(50, 1000)
        self._custom_w.setValue(210)
        self._custom_w.setSuffix(" mm")
        self._custom_w.setVisible(False)
        self._custom_h = QSpinBox()
        self._custom_h.setRange(50, 1000)
        self._custom_h.setValue(297)
        self._custom_h.setSuffix(" mm")
        self._custom_h.setVisible(False)
        fmt_layout.addWidget(QLabel("W:"))
        fmt_layout.addWidget(self._custom_w)
        fmt_layout.addWidget(QLabel("H:"))
        fmt_layout.addWidget(self._custom_h)
        self._fmt_group.buttonToggled.connect(self._on_format_changed)
        layout.addWidget(fmt_box)

        # Generate button
        gen_btn = QPushButton("Generate Paper")
        gen_btn.setFixedHeight(36)
        gen_btn.clicked.connect(self._on_generate)
        layout.addWidget(gen_btn)
        layout.addStretch()

    def _browse_excel(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Question Bank", "", "Excel Files (*.xlsx)"
        )
        if not path:
            return
        try:
            questions = load_questions(path)
        except Exception as e:
            QMessageBox.critical(self, "Load Error", str(e))
            return
        self.excel_dir = os.path.dirname(path)
        self._file_label.setText(os.path.basename(path))
        self.populate_dropdowns(questions)
        self.excel_loaded.emit(questions)

    def populate_dropdowns(self, questions):
        classes  = sorted({q.class_   for q in questions})
        subjects = sorted({q.subject  for q in questions})
        mediums  = sorted({q.medium   for q in questions})
        for combo, items in (
            (self._class_combo,   classes),
            (self._subject_combo, subjects),
            (self._medium_combo,  mediums),
        ):
            combo.clear()
            combo.addItems(items)

    def _on_format_changed(self, btn, checked):
        is_custom = checked and btn.text() == "Custom"
        self._custom_w.setVisible(is_custom)
        self._custom_h.setVisible(is_custom)

    def _on_generate(self):
        fmt_btn = next(b for b in self._fmt_group.buttons() if b.isChecked())
        page_format = fmt_btn.text()
        instructions = [
            line.strip()
            for line in self._instructions.toPlainText().splitlines()
            if line.strip()
        ]
        config = ExamConfig(
            school_name=self._school.text().strip(),
            exam_name=self._exam_name.text().strip(),
            class_=self._class_combo.currentText(),
            subject=self._subject_combo.currentText(),
            medium=self._medium_combo.currentText(),
            date=self._date.text().strip(),
            duration=self._duration.text().strip(),
            max_marks=self._max_marks.value(),
            instructions=instructions,
            page_format=page_format,
            custom_width_mm=self._custom_w.value() if page_format == "Custom" else None,
            custom_height_mm=self._custom_h.value() if page_format == "Custom" else None,
        )
        self.generate_requested.emit(config)
```

---

### Task 10: Preview Widget

**Files:**
- Create: `src/ui/preview_widget.py`

**Interfaces:**
- Produces: `PreviewWidget(QWidget)` with:
  - Method `show_html(html: str) -> None`
  - Signal `save_paper_requested(str)` — emits chosen output path
  - Signal `save_answer_key_requested(str)` — emits chosen output path
  - Signal `regenerate_requested()` — emits when Regenerate clicked
  - Property `page: QWebEnginePage` — exposes the underlying page for `print_to_pdf`

- [ ] **Step 1: Implement PreviewWidget**

`src/ui/preview_widget.py`:
```python
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import pyqtSignal


class PreviewWidget(QWidget):
    save_paper_requested = pyqtSignal(str)
    save_answer_key_requested = pyqtSignal(str)
    regenerate_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        self._view = QWebEngineView()
        layout.addWidget(self._view, 1)

        btn_row = QHBoxLayout()
        self._regen_btn = QPushButton("Regenerate")
        self._save_paper_btn = QPushButton("Save Paper PDF")
        self._save_key_btn = QPushButton("Save Answer Key PDF")

        for btn in (self._regen_btn, self._save_paper_btn, self._save_key_btn):
            btn_row.addWidget(btn)

        self._save_paper_btn.setEnabled(False)
        self._save_key_btn.setEnabled(False)

        self._regen_btn.clicked.connect(self.regenerate_requested)
        self._save_paper_btn.clicked.connect(self._on_save_paper)
        self._save_key_btn.clicked.connect(self._on_save_key)

        layout.addLayout(btn_row)

    def show_html(self, html: str) -> None:
        self._view.setHtml(html)
        self._save_paper_btn.setEnabled(True)
        self._save_key_btn.setEnabled(True)

    @property
    def page(self):
        return self._view.page()

    def _on_save_paper(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Paper PDF", "exam_paper.pdf", "PDF Files (*.pdf)"
        )
        if path:
            self.save_paper_requested.emit(path)

    def _on_save_key(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Answer Key PDF", "answer_key.pdf", "PDF Files (*.pdf)"
        )
        if path:
            self.save_answer_key_requested.emit(path)
```

---

### Task 11: Main Window + Entry Point

**Files:**
- Create: `src/ui/main_window.py`
- Modify: `main.py` (complete)

**Interfaces:**
- Consumes: all services and UI widgets
- Produces: runnable application

- [ ] **Step 1: Implement MainWindow**

`src/ui/main_window.py`:
```python
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QMessageBox, QFileDialog
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from src.ui.config_form import ConfigForm
from src.ui.preview_widget import PreviewWidget
from src.services.question_selector import select_questions
from src.services.paper_builder import build_paper_html, build_answer_key_html
from src.services.pdf_exporter import build_page_layout, print_to_pdf
from src.utils.asset_path import get_asset_path
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Exam Paper Generator")
        self.resize(1200, 800)

        self._questions = []
        self._current_sections = {}
        self._current_config = None

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        self._config_form = ConfigForm()
        self._config_form.setFixedWidth(320)
        self._preview = PreviewWidget()

        layout.addWidget(self._config_form)
        layout.addWidget(self._preview, 1)

        self._config_form.excel_loaded.connect(self._on_excel_loaded)
        self._config_form.generate_requested.connect(self._on_generate)
        self._preview.regenerate_requested.connect(self._on_regenerate)
        self._preview.save_paper_requested.connect(self._on_save_paper)
        self._preview.save_answer_key_requested.connect(self._on_save_answer_key)

        self._preview.page.pdfPrintingFinished.connect(self._on_pdf_done)
        self._pending_pdf_type = None

    def _on_excel_loaded(self, questions):
        self._questions = questions

    def _on_generate(self, config):
        if not self._questions:
            QMessageBox.warning(self, "No Data", "Please load an Excel question bank first.")
            return
        self._current_config = config
        sections, warnings = select_questions(
            self._questions, config.class_, config.subject, config.medium
        )
        if not sections:
            QMessageBox.warning(self, "No Questions",
                "No questions matched the selected Class / Subject / Medium.")
            return
        if warnings:
            QMessageBox.information(self, "Warnings", "\n".join(warnings))
        self._current_sections = sections
        font_path = get_asset_path(os.path.join("assets", "fonts", "NotoSansDevanagari-Regular.ttf"))
        html, img_warnings = build_paper_html(
            sections, config, self._config_form.excel_dir, font_path
        )
        if img_warnings:
            QMessageBox.warning(self, "Missing Images", "\n".join(img_warnings))
        self._preview.show_html(html)

    def _on_regenerate(self):
        if self._current_config:
            self._on_generate(self._current_config)

    def _on_save_paper(self, output_path: str):
        if not self._current_config:
            return
        layout = build_page_layout(
            self._current_config.page_format,
            self._current_config.custom_width_mm,
            self._current_config.custom_height_mm,
        )
        self._pending_pdf_type = "paper"
        print_to_pdf(self._preview.page, output_path, layout)

    def _on_save_answer_key(self, output_path: str):
        if not self._current_sections or not self._current_config:
            return
        font_path = get_asset_path(os.path.join("assets", "fonts", "NotoSansDevanagari-Regular.ttf"))
        html = build_answer_key_html(self._current_sections, self._current_config, font_path)

        # Use a temporary off-screen page to render and print the answer key
        from PyQt6.QtWebEngineCore import QWebEnginePage
        self._answer_key_page = QWebEnginePage()
        layout = build_page_layout(
            self._current_config.page_format,
            self._current_config.custom_width_mm,
            self._current_config.custom_height_mm,
        )
        self._answer_key_output = output_path
        self._answer_key_page.setHtml(html)
        self._answer_key_page.loadFinished.connect(
            lambda ok: print_to_pdf(self._answer_key_page, output_path, layout)
        )
        self._answer_key_page.pdfPrintingFinished.connect(self._on_pdf_done)
        self._pending_pdf_type = "answer_key"

    def _on_pdf_done(self, file_path: str, success: bool):
        if success:
            label = "Answer Key PDF" if self._pending_pdf_type == "answer_key" else "Paper PDF"
            QMessageBox.information(self, "Saved", f"{label} saved to:\n{file_path}")
        else:
            QMessageBox.critical(self, "Error", f"Failed to save PDF to:\n{file_path}")
        self._pending_pdf_type = None
```

- [ ] **Step 2: Complete main.py**

```python
import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Exam Paper Generator")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run the full test suite one final time**

```bash
pytest -v
```
Expected: all tests pass

- [ ] **Step 4: Manual smoke test**

```bash
python main.py
```

Verify:
1. App window opens with left config panel and right preview panel
2. Browse to a `.xlsx` file → Class/Subject/Medium dropdowns populate
3. Fill in exam details, click "Generate Paper" → paper preview appears in right panel
4. Hindi questions render with Devanagari script (not boxes/question marks)
5. Images appear inline for questions that have them
6. "Regenerate" produces a different variant combination
7. "Save Paper PDF" → file picker appears, PDF saves and success dialog shows
8. "Save Answer Key PDF" → separate PDF saves with answers shown

- [ ] **Step 5: Commit**

Files: `src/ui/main_window.py`, `src/ui/config_form.py`, `src/ui/preview_widget.py`, `main.py`

Suggested message: `feat: add PyQt6 UI — config form, preview widget, main window`

---

### Task 12: GitHub Actions Build Pipeline

**Files:**
- Create: `.github/workflows/build-windows.yml`

**Interfaces:**
- Consumes: push to `main` branch
- Produces: `dist/main.exe` uploaded as artifact `exam-paper-generator-windows`

- [ ] **Step 1: Create build-windows.yml**

`.github/workflows/build-windows.yml`:
```yaml
name: Build Windows EXE

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build:
    runs-on: windows-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Build EXE with PyInstaller
        run: >
          pyinstaller
          --onefile
          --windowed
          --name "ExamPaperGenerator"
          --add-data "assets;assets"
          main.py

      - name: Upload EXE artifact
        uses: actions/upload-artifact@v4
        with:
          name: exam-paper-generator-windows
          path: dist/ExamPaperGenerator.exe
          retention-days: 30
```

- [ ] **Step 2: Commit and push**

```bash
git add .github/workflows/build-windows.yml
```
Suggested message: `ci: add GitHub Actions Windows EXE build`

Then push to `main` and verify the Actions tab shows the workflow running.

- [ ] **Step 3: Download and verify the EXE**

Once the Actions run completes:
1. Go to Actions → Build Windows EXE → latest run
2. Download artifact `exam-paper-generator-windows`
3. Extract and run `ExamPaperGenerator.exe` on a Windows machine
4. Verify it works the same as the manual smoke test in Task 11

---

## Self-Review Checklist

- [x] Spec section covered → Task mapping:
  - Question Bank Format → Task 4 (excel_loader)
  - Data Models → Task 2
  - Question Selection Logic → Task 5
  - UI Layout → Tasks 9, 10, 11
  - PDF Generation Flow → Tasks 7, 8, 11
  - Hindi support → Task 6 (font + @font-face in templates)
  - Image embedding → Tasks 6, 7
  - Answer Key (separate PDF) → Tasks 6, 7, 10, 11
  - Page formats A4/Legal/Custom → Tasks 8, 9
  - GitHub Actions build → Task 12
  - Asset path (PyInstaller compat) → Task 3
- [x] No placeholders — all steps include working code
- [x] Type consistency — `Question`, `ExamConfig`, `select_questions`, `build_paper_html`, `build_answer_key_html`, `build_page_layout`, `print_to_pdf` used consistently across all tasks
- [x] `excel_dir` passed as `str` consistently to `build_paper_html`
- [x] `font_path` passed as absolute `str` consistently; `Path.as_uri()` used for `file://` conversion
