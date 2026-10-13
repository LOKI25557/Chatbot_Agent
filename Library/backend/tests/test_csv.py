import io
import pytest
from app.core.config import settings
from app.services.csv_service import sanitize_csv_cell

ADMIN_HEADERS = {"X-Admin-Key": settings.ADMIN_SECRET_KEY}


def test_sanitize_csv_cell_formula_injection():
    # Danger chars should be escaped with a leading single quote
    assert sanitize_csv_cell("=1+1") == "'=1+1"
    assert sanitize_csv_cell("+cmd|' /C calc'!A0") == "'+cmd|' /C calc'!A0"
    assert sanitize_csv_cell("-2+3") == "'-2+3"
    assert sanitize_csv_cell("@SUM(1,2)") == "'@SUM(1,2)"
    assert sanitize_csv_cell("Normal Text") == "Normal Text"
    assert sanitize_csv_cell(123) == "123"


def test_csv_import_and_duplicate_detection(client):
    csv_content = (
        "title,author,isbn,publisher,publication_year,category,total_copies,available_copies\n"
        "Design Patterns,Gang of Four,9780201633610,Addison-Wesley,1994,Computer Science,2,2\n"
        "Clean Code,Robert C. Martin,9780132350884,Prentice Hall,2008,Computer Science,1,1\n"  # Duplicate ISBN
        "Design Patterns,Gang of Four,9789999999999,Addison-Wesley,1994,Computer Science,1,1\n"  # Duplicate Title+Author
    )

    file_obj = io.BytesIO(csv_content.encode("utf-8"))
    files = {"file": ("catalog.csv", file_obj, "text/csv")}

    response = client.post("/api/v1/admin/books/import", files=files, headers=ADMIN_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["imported_count"] == 1  # Only "Design Patterns" imported
    assert data["skipped_count"] == 2   # 2 duplicates skipped
    assert len(data["errors"]) >= 2


def test_csv_export(client):
    response = client.get("/api/v1/admin/books/export", headers=ADMIN_HEADERS)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    content = response.text
    assert "title,author,isbn" in content
    assert "Clean Code" in content
