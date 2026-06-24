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
