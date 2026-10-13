from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.book_repository import BookRepository
from app.schemas.book import BookResponse, BookPagination

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("", response_model=BookPagination)
def list_books(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    category: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    only_available: bool = Query(False),
    sort_by: str = Query("title"),
    sort_order: str = Query("asc"),
    db: Session = Depends(get_db)
):
    """Lists catalogue books with pagination, filtering, and sorting."""
    valid_sorts = {"title", "author", "publication_year", "created_at", "available_copies"}
    if sort_by not in valid_sorts:
        sort_by = "title"

    items, total = BookRepository.list_paginated(
        db=db,
        page=page,
        page_size=page_size,
        category=category,
        author=author,
        search=search,
        only_available=only_available,
        sort_by=sort_by,
        sort_order=sort_order
    )

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return BookPagination(
        items=[BookResponse.model_validate(b) for b in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    """Retrieves full catalogue details for a specific book."""
    book = BookRepository.get_by_id(db, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} was not found in the catalogue."
        )
    return BookResponse.model_validate(book)


@router.get("/{book_id}/similar", response_model=List[BookResponse])
def get_similar_books(book_id: int, limit: int = Query(4, ge=1, le=10), db: Session = Depends(get_db)):
    """Retrieves verified similar books from the library catalogue sharing category or author."""
    book = BookRepository.get_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found.")

    similar = BookRepository.find_similar_books(
        db=db,
        category=book.category,
        author=book.author,
        exclude_id=book.id,
        limit=limit
    )
    return [BookResponse.model_validate(b) for b in similar]
