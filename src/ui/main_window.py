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
        from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
        self._answer_key_page = QWebEnginePage()
        self._answer_key_page.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True
        )
        layout = build_page_layout(
            self._current_config.page_format,
            self._current_config.custom_width_mm,
            self._current_config.custom_height_mm,
        )
        self._answer_key_output = output_path
        base_url = QUrl.fromLocalFile(get_asset_path("") + "/")
        self._answer_key_page.setHtml(html, base_url)
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
