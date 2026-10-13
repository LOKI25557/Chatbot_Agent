from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import verify_admin_access
from app.repositories.book_repository import BookRepository
from app.schemas.book import BookCreate, BookUpdate, BookResponse, CatalogStats
from app.services.csv_service import CSVService

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(verify_admin_access)])


@router.get("/stats", response_model=CatalogStats)
def get_catalogue_stats(db: Session = Depends(get_db)):
    """Retrieves live catalogue inventory statistics."""
    stats = BookRepository.get_stats(db)
    return CatalogStats(**stats)


@router.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book_in: BookCreate, db: Session = Depends(get_db)):
    """Adds a new verified book to the library catalogue."""
    if book_in.isbn:
        existing = BookRepository.get_by_isbn(db, book_in.isbn)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Book with ISBN '{book_in.isbn}' already exists ({existing.title})."
            )
    created = BookRepository.create(db, book_in)
    return BookResponse.model_validate(created)


@router.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book_in: BookUpdate, db: Session = Depends(get_db)):
    """Updates catalogue records for an existing book."""
    db_book = BookRepository.get_by_id(db, book_id)
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found."
        )

    # Validate copy count consistency if updated
    total = book_in.total_copies if book_in.total_copies is not None else db_book.total_copies
    avail = book_in.available_copies if book_in.available_copies is not None else db_book.available_copies
    if avail > total:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"available_copies ({avail}) cannot exceed total_copies ({total})."
        )

    updated = BookRepository.update(db, db_book, book_in)
    return BookResponse.model_validate(updated)


@router.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """Deletes a book from the library catalogue."""
    db_book = BookRepository.get_by_id(db, book_id)
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found."
        )
    BookRepository.delete(db, db_book)
    return {"success": True, "message": f"Book '{db_book.title}' (ID {book_id}) deleted successfully."}


@router.post("/books/import")
async def import_csv_catalogue(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Imports books from a validated CSV file with duplicate and injection protection."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a .csv extension."
        )

    content_bytes = await file.read()
    try:
        content_str = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        content_str = content_bytes.decode("latin-1")

    result = CSVService.import_csv(db, content_str)
    return result


@router.get("/books/export")
def export_csv_catalogue(db: Session = Depends(get_db)):
    """Exports all library catalogue records to a downloadable CSV with formula injection protection."""
    csv_data = CSVService.export_csv(db)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=library_catalogue_export.csv"}
    )
