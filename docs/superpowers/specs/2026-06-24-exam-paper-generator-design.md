# Exam Paper Generator — Design Spec

**Date:** 2026-06-24
**Status:** Approved

---

## Overview

A Windows desktop application that generates randomized exam question papers from an Excel question bank. Teachers fill in exam configuration, load an Excel file, and the app randomly selects one variant (A/B/C) per question number to produce a print-ready PDF paper and a separate answer key PDF.

---

## Platform & Tech Stack

| Concern | Choice |
|---|---|
| Platform | Windows desktop app |
| Development OS | Ubuntu (cross-built via GitHub Actions) |
| GUI | PyQt6 |
| Preview | QWebEngineView (Chromium-based) |
| PDF Export | QWebEnginePage.printToPdf() |
| Templates | Jinja2 (HTML/CSS) |
| Excel Parsing | openpyxl |
| Hindi Font | Noto Sans Devanagari (bundled TTF) |
| Packaging | PyInstaller → single `.exe` |
| CI/CD | GitHub Actions `windows-latest` runner |

---

## Question Bank Format

Single `.xlsx` file, one sheet, with these columns:

| Column | Description | Example |
|---|---|---|
| Question ID | Number + variant | `1A`, `2C` |
| Class | Grade | `10` |
| Subject | Subject name | `Science` |
| Medium | `English` or `Hindi` | `English` |
| Question | Question text (Unicode, Devanagari supported) | `Define photosynthesis.` |
| Image Path | Filename relative to Excel file (optional) | `images/q1a.png` |
| Answer | Answer text | `Process of converting light to food` |
| Marks | Marks allocated | `2` |

**Variant system:** Each question number has up to 3 variants (A, B, C). A bank of 100 questions = up to 300 rows. During generation, exactly one variant per question number is selected.

**Image location:** Images must be in the same folder as the Excel file (or a subfolder). The Image Path column holds filenames relative to the Excel file's location.

**Scale:** A single sheet handles all classes, subjects, and mediums. Performance is not a concern — even 30,000 rows (10 classes × 5 subjects × 2 mediums × 300 rows) loads in under a second.

---

## Data Models

```python
# src/models/question.py
@dataclass
class Question:
    question_id: str       # "1A", "2C"
    number: int            # 1, 2, 3 ...
    variant: str           # "A", "B", "C"
    class_: str
    subject: str
    medium: str            # "English" | "Hindi"
    text: str
    image_path: str | None # relative filename, e.g. "images/q1a.png"
    answer: str
    marks: int

# src/models/exam_config.py
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
    page_format: str           # "A4" | "Legal" | "Custom"
    custom_width_mm: int | None  # set only when page_format == "Custom"
    custom_height_mm: int | None # set only when page_format == "Custom"
```

`question_id` is parsed at load time: `"1A"` → `number=1, variant="A"`.

---

## Project Structure

```
exam_paper_generator/
├── main.py
├── requirements.txt
├── assets/
│   ├── fonts/
│   │   └── NotoSansDevanagari-Regular.ttf
│   └── templates/
│       ├── paper.html
│       └── answer_key.html
├── src/
│   ├── models/
│   │   ├── question.py
│   │   └── exam_config.py
│   ├── services/
│   │   ├── excel_loader.py
│   │   ├── question_selector.py
│   │   ├── paper_builder.py
│   │   └── pdf_exporter.py
│   └── ui/
│       ├── main_window.py
│       ├── config_form.py
│       └── preview_widget.py
├── docs/
│   └── superpowers/
│       └── specs/
│           └── 2026-06-24-exam-paper-generator-design.md
└── .github/
    └── workflows/
        └── build-windows.yml
```

---

## Core Logic — Question Selection

`src/services/question_selector.py`:

1. Receive full loaded question list + selected class/subject/medium
2. Filter: keep only matching rows
3. Group by `question.number`: `{ 1: [Q1A, Q1B, Q1C], 2: [Q2A, Q2B], ... }`
4. For each group: `random.choice(variants)` → one question selected
5. Sort by `question.number` → ordered final list
6. Group by `question.marks` → sections dict `{ 1: [questions], 2: [questions], 5: [questions] }`

**Edge cases:**
- Fewer than 3 variants for a number → picks from whatever exists, no crash
- No variants after filtering → question number skipped, warning shown in UI
- Image file not found → question renders without image, warning logged (no crash)

**Regenerate:** Re-runs step 4 only. No Excel reload, instant.

---

## UI Layout

Two-panel window:

```
┌─────────────────────────────────────────────────────────────┐
│  Exam Paper Generator                              [─][□][×] │
├──────────────────────┬──────────────────────────────────────┤
│  CONFIGURATION       │  PREVIEW                             │
│                      │                                      │
│  Excel File: [Browse]│  ┌──────────────────────────────┐   │
│                      │  │   School Name                │   │
│  School Name         │  │   Exam Name | Date           │   │
│  Exam Name           │  │   Class | Subject | Duration │   │
│  Class    [dropdown] │  ├──────────────────────────────┤   │
│  Subject  [dropdown] │  │ Section A (1 Mark)           │   │
│  Medium   [dropdown] │  │ Q1. ............             │   │
│  Date                │  │ Q2. ............             │   │
│  Duration            │  │                              │   │
│  Max Marks           │  │ Section B (2 Marks)          │   │
│  Instructions        │  │ Q3. ............  [image]    │   │
│  Page Format         │  │ Q4. ............             │   │
│  [A4][Legal][Custom] │  │                              │   │
│                      │  └──────────────────────────────┘   │
│  [Generate Paper]    │                                      │
│                      │  [Regenerate] [Save Paper PDF]       │
│                      │  [Save Answer Key PDF]               │
└──────────────────────┴──────────────────────────────────────┘
```

**Behaviours:**
- Class/Subject/Medium dropdowns auto-populated from loaded Excel (no hardcoding)
- Preview updates on "Generate Paper" and "Regenerate"
- "Save Paper PDF" and "Save Answer Key PDF" disabled until a paper is generated
- Page format change applies immediately to the preview
- When "Custom" is selected, two numeric fields (width mm, height mm) appear below the format buttons
- Instructions field is a multi-line textarea; each non-empty line becomes one instruction bullet in the paper

---

## PDF Generation Flow

```
Generate clicked
    → question_selector.py produces sections dict
    → paper_builder.py renders paper.html via Jinja2
        - exam config injected (school, date, marks, etc.)
        - sections dict injected { marks: [questions] }
        - image paths converted to absolute file:// URIs
        - NotoSansDevanagari font embedded via @font-face CSS
    → QWebEngineView.setHtml() → live preview

Save Paper PDF clicked
    → QWebEnginePage.printToPdf(output_path, page_layout)
    → success dialog shown

Save Answer Key PDF clicked
    → same flow using answer_key.html template
    → shows answers, no images
```

**Hindi support:** NotoSansDevanagari-Regular.ttf bundled inside the app, referenced via `file://` in CSS `@font-face`. Fully offline.

---

## GitHub Actions Build Pipeline

```yaml
# .github/workflows/build-windows.yml
on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: pyinstaller --onefile --windowed --add-data "assets;assets" main.py
      - uses: actions/upload-artifact@v4
        with:
          name: exam-paper-generator-windows
          path: dist/main.exe
```

**Workflow:** Push from Ubuntu → GitHub builds on `windows-latest` → `.exe` downloadable from Actions tab. No local Windows machine needed.

---

## Out of Scope (v1)

- User accounts / login
- Network / multi-user access
- Question bank editing within the app (managed externally via Excel)
- Question difficulty tagging beyond marks-based sections
- Print directly from app (save PDF → open in system viewer → print)
