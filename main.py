import sys
from PyQt6.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Exam Paper Generator")
    # MainWindow will be imported and shown here in Task 11
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
