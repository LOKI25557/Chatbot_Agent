import csv
import io
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from app.models.book import Book
from app.repositories.book_repository import BookRepository
from app.schemas.book import BookCreate


def sanitize_csv_cell(value: Any) -> str:
    """
    Prevents CSV Formula Injection (CWE-1236) by prepending a single quote
    if the cell content starts with dangerous trigger characters (=, +, -, @, tab, cr).
    """
    if value is None:
        return ""
    val_str = str(value)
    if val_str and val_str[0] in ("=", "+", "-", "@", "\t", "\r"):
        return f"'{val_str}"
    return val_str


class CSVService:
    """Service providing secure CSV import and export for the library catalogue."""

    EXPECTED_HEADERS = [
        "title", "author", "isbn", "publisher", "publication_year",
        "category", "description", "shelf_location", "total_copies", "available_copies"
    ]

    @classmethod
    def import_csv(cls, db: Session, content: str) -> Dict[str, Any]:
        """
        Parses, validates, and imports books from CSV string.
        Detects duplicates by ISBN and (Title, Author).
        Returns detailed summary: imported_count, skipped_count, errors.
        """
        reader = csv.DictReader(io.StringIO(content))
        imported = 0
        skipped = 0
        errors = []

        if not reader.fieldnames:
            return {
                "success": False,
                "message": "Empty or invalid CSV file.",
                "imported_count": 0,
                "skipped_count": 0,
                "errors": ["No headers found in CSV."]
            }

        # Normalize header keys to lowercase
        normalized_fieldnames = {k: k.strip().lower() for k in reader.fieldnames if k}

        for row_num, raw_row in enumerate(reader, start=2):
            row = {normalized_fieldnames.get(k, k): v.strip() if v else "" for k, v in raw_row.items() if k}

            title = row.get("title", "").strip()
            if not title:
                errors.append(f"Row {row_num}: Missing required 'title'.")
                skipped += 1
                continue

            author = row.get("author", "").strip() or None
            isbn = row.get("isbn", "").replace("-", "").replace(" ", "").strip() or None
            publisher = row.get("publisher", "").strip() or None

            pub_year = None
            if row.get("publication_year"):
                try:
                    pub_year = int(row.get("publication_year"))
                except ValueError:
                    errors.append(f"Row {row_num}: Invalid publication_year '{row.get('publication_year')}'.")

            category = row.get("category", "").strip() or None
            description = row.get("description", "").strip() or None
            shelf_location = row.get("shelf_location", "").strip() or None

            try:
                total_copies = int(row.get("total_copies", 1))
                if total_copies < 0:
                    raise ValueError()
            except ValueError:
                total_copies = 1

            try:
                available_copies = int(row.get("available_copies", total_copies))
                if available_copies < 0:
                    raise ValueError()
            except ValueError:
                available_copies = total_copies

            # Validate copies constraint
            if available_copies > total_copies:
                available_copies = total_copies

            # Check duplicate by ISBN
            if isbn:
                existing_isbn = BookRepository.get_by_isbn(db, isbn)
                if existing_isbn:
                    errors.append(f"Row {row_num}: Book with ISBN '{isbn}' already exists ({existing_isbn.title}). Skipping.")
                    skipped += 1
                    continue

            # Check duplicate by exact title + author
            existing_title = db.query(Book).filter(
                Book.title.ilike(title),
                Book.author.ilike(author) if author else Book.author.is_(None)
            ).first()
            if existing_title:
                errors.append(f"Row {row_num}: Duplicate title & author '{title}' by '{author or 'Unknown'}'. Skipping.")
                skipped += 1
                continue

            try:
                book_in = BookCreate(
                    title=title,
                    author=author,
                    isbn=isbn,
                    publisher=publisher,
                    publication_year=pub_year,
                    category=category,
                    description=description,
                    shelf_location=shelf_location,
                    total_copies=total_copies,
                    available_copies=available_copies
                )
                BookRepository.create(db, book_in)
                imported += 1
            except Exception as e:
                errors.append(f"Row {row_num}: Creation error: {str(e)}")
                skipped += 1

        return {
            "success": True,
            "imported_count": imported,
            "skipped_count": skipped,
            "errors": errors
        }

    @classmethod
    def export_csv(cls, db: Session) -> str:
        """
        Exports all catalog books to CSV format with formula injection protection.
        """
        books = db.query(Book).order_by(Book.id.asc()).all()
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(cls.EXPECTED_HEADERS)

        for b in books:
            writer.writerow([
                sanitize_csv_cell(b.title),
                sanitize_csv_cell(b.author),
                sanitize_csv_cell(b.isbn),
                sanitize_csv_cell(b.publisher),
                sanitize_csv_cell(b.publication_year),
                sanitize_csv_cell(b.category),
                sanitize_csv_cell(b.description),
                sanitize_csv_cell(b.shelf_location),
                sanitize_csv_cell(b.total_copies),
                sanitize_csv_cell(b.available_copies)
            ])

        return output.getvalue()
