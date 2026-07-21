from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtCore import pyqtSignal, QUrl
from src.utils.asset_path import get_asset_path


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
        self._view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True
        )
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
        base_url = QUrl.fromLocalFile(get_asset_path("") + "/")
        self._view.setHtml(html, base_url)
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
