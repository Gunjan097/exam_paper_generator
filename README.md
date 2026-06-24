# Exam Paper Generator

A desktop application for generating randomized exam question papers from an Excel-based question bank. Built with Python + PyQt6, distributed as a Windows `.exe` via GitHub Actions.

---

## Features

- Load question bank from Excel (`.xlsx`)
- Randomly select one variant (A / B / C) per question number
- Filter by Class, Subject, and Medium (English / Hindi)
- Sectioned layout grouped by marks (Section A, Section B, ...)
- Full Hindi / Devanagari text support
- Inline question images
- Live preview before saving
- Export paper as PDF
- Export answer key as a separate PDF
- Regenerate with a new random combination
- Multiple page formats: A4, Legal, Custom

---

## Question Bank Format (Excel)

The question bank is maintained in an `.xlsx` file with the following columns:

| Column      | Description                                      | Example          |
|-------------|--------------------------------------------------|------------------|
| Question ID | Question number + variant                        | `1A`, `1B`, `1C` |
| Class       | Grade / Class                                    | `10`             |
| Subject     | Subject name                                     | `Science`        |
| Medium      | `English` or `Hindi`                             | `English`        |
| Question    | Question text (supports Unicode / Devanagari)    | `Define photosynthesis.` |
| Image Path  | Filename relative to Excel file (optional)       | `images/q1a.png` |
| Answer      | Answer text or answer key                        | `Process of converting light to food` |
| Marks       | Marks allocated                                  | `2`              |

### Variant System

Each question number has 3 variants (A, B, C). During paper generation, exactly **one variant is randomly selected** per question number:

```
Q1 → randomly picks 1A, 1B, or 1C
Q2 → randomly picks 2A, 2B, or 2C
...
```

A bank of 100 questions = 300 Excel rows (100 × 3 variants).

---

## Exam Configuration

Before generating, the user fills in:

- School Name
- Exam Name
- Class, Subject, Medium
- Exam Date
- Duration
- Maximum Marks
- Instructions

---

## Tech Stack

| Layer       | Technology                            |
|-------------|---------------------------------------|
| GUI         | PyQt6                                 |
| Preview     | QWebEngineView (Chromium-based)       |
| PDF Export  | QWebEnginePage.printToPdf()           |
| Templates   | Jinja2 (HTML/CSS)                     |
| Excel Parse | openpyxl                              |
| Hindi Fonts | Noto Sans Devanagari (bundled)        |
| Packaging   | PyInstaller → Windows `.exe`          |
| CI/CD       | GitHub Actions (`windows-latest`)     |

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
└── .github/
    └── workflows/
        └── build-windows.yml
```

---

## Building the Windows `.exe`

The `.exe` is built automatically via GitHub Actions on every push to `main`.

1. Push your code to `main`
2. Go to **Actions** → `Build Windows EXE`
3. Download the `.exe` artifact from the completed run

To build locally on Windows:

```bash
pip install -r requirements.txt
pyinstaller --onefile --windowed main.py
```

---

## Development Setup (Ubuntu)

```bash
git clone https://github.com/Gunjan097/exam_paper_generator.git
cd exam_paper_generator
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

> **Note:** Development and testing happens on Ubuntu. The Windows `.exe` is produced exclusively by GitHub Actions using a `windows-latest` runner.

---

## License

MIT
