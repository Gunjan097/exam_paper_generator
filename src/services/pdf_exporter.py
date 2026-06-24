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
