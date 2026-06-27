import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QTextEdit, QPushButton, QFileDialog, QSpinBox,
    QButtonGroup, QRadioButton, QGroupBox, QFormLayout, QMessageBox,
)
from PyQt6.QtCore import pyqtSignal, QDate
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
        self._date = QLineEdit(QDate.currentDate().toString("yyyy-MM-dd"))
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
        self._custom_w_label = QLabel("W:")
        self._custom_w_label.setVisible(False)
        self._custom_h_label = QLabel("H:")
        self._custom_h_label.setVisible(False)
        fmt_layout.addWidget(self._custom_w_label)
        fmt_layout.addWidget(self._custom_w)
        fmt_layout.addWidget(self._custom_h_label)
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
        self._custom_w_label.setVisible(is_custom)
        self._custom_w.setVisible(is_custom)
        self._custom_h_label.setVisible(is_custom)
        self._custom_h.setVisible(is_custom)

    def _on_generate(self):
        if not self.excel_dir:
            QMessageBox.warning(self, "No File", "Please load an Excel question bank first.")
            return
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
