import re
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc, asc

from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate


def normalize_string(s: Optional[str]) -> str:
    """Normalizes a string for clean comparisons by stripping punctuation and lowercasing."""
    if not s:
        return ""
    return re.sub(r"[^\w\s]", "", s).strip().lower()


class BookRepository:
    """Repository handling all database persistence and queries for the book catalog."""

    @staticmethod
    def get_by_id(db: Session, book_id: int) -> Optional[Book]:
        return db.query(Book).filter(Book.id == book_id).first()

    @staticmethod
    def get_by_isbn(db: Session, isbn: str) -> Optional[Book]:
        cleaned = isbn.replace("-", "").replace(" ", "").strip()
        if not cleaned:
            return None
        return db.query(Book).filter(Book.isbn == cleaned).first()

    @staticmethod
    def find_exact_title(db: Session, title: str) -> List[Book]:
        """Case-insensitive exact title matching."""
        clean = title.strip()
        return db.query(Book).filter(func.lower(Book.title) == clean.lower()).all()

    @staticmethod
    def search_catalogue(
        db: Session,
        title: Optional[str] = None,
        author: Optional[str] = None,
        isbn: Optional[str] = None,
        category: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        only_available: bool = False,
        limit: int = 10
    ) -> List[Book]:
        """Multi-criteria search over actual database records with stopword filtering and relevance ranking."""
        stopwords = {
            "the", "a", "an", "and", "or", "of", "to", "in", "for", "with",
            "on", "at", "by", "from", "is", "it", "as", "about", "find",
            "search", "book", "books", "show", "me", "any", "have", "you",
            "do", "what", "where", "who", "which", "are", "there", "i", "want", "looking"
        }

        query = db.query(Book)
        if only_available:
            query = query.filter(Book.available_copies > 0)

        # 1. Exact ISBN match takes priority if valid
        if isbn:
            norm_isbn = isbn.replace("-", "").replace(" ", "").strip()
            isbn_match = query.filter(Book.isbn == norm_isbn).all()
            if isbn_match:
                return isbn_match

        # Extract non-stopword tokens
        title_tokens = [w for w in re.findall(r"\w+", (title or "").lower()) if w not in stopwords and len(w) >= 2]
        clean_kws = [k.lower().strip() for k in (keywords or []) if k.lower().strip() not in stopwords and len(k.strip()) >= 3]

        filters = []
        if title:
            filters.append(func.lower(Book.title).like(f"%{title.strip().lower()}%"))
            for tok in title_tokens:
                filters.append(func.lower(Book.title).like(f"%{tok}%"))
        if author:
            filters.append(func.lower(Book.author).like(f"%{author.strip().lower()}%"))
        if category:
            filters.append(func.lower(Book.category).like(f"%{category.strip().lower()}%"))
        if clean_kws and not title:
            for kw in clean_kws:
                filters.append(or_(
                    func.lower(Book.title).like(f"%{kw}%"),
                    func.lower(Book.author).like(f"%{kw}%"),
                    func.lower(Book.category).like(f"%{kw}%"),
                    func.lower(Book.description).like(f"%{kw}%")
                ))

        if not filters:
            return []

        candidates = query.filter(or_(*filters)).all()

        # Score and rank candidates by relevance
        scored_books = []
        for b in candidates:
            score = 0
            b_title = (b.title or "").lower()
            b_author = (b.author or "").lower()
            b_cat = (b.category or "").lower()
            b_desc = (b.description or "").lower()

            if title:
                t_clean = title.strip().lower()
                if t_clean == b_title:
                    score += 200
                elif t_clean in b_title:
                    score += 100
                elif title_tokens:
                    matched = sum(1 for tok in title_tokens if tok in b_title)
                    score += matched * 35
                    # If specific title was requested but not a single title token matches, reject candidate
                    if matched == 0 and not any(tok in b_author for tok in title_tokens):
                        score = 0

            if author:
                a_clean = author.strip().lower()
                if a_clean == b_author:
                    score += 150
                elif a_clean in b_author:
                    score += 80

            if category:
                c_clean = category.strip().lower()
                if c_clean in b_cat:
                    score += 50

            if clean_kws and not title:
                for kw in clean_kws:
                    if kw in b_title:
                        score += 40
                    elif kw in b_author:
                        score += 30
                    elif kw in b_cat:
                        score += 25
                    elif kw in b_desc:
                        score += 10

            if score > 0:
                scored_books.append((score, b))

        # Sort by relevance score descending, availability, title
        scored_books.sort(key=lambda item: (item[0], item[1].available_copies > 0, item[1].title), reverse=True)
        return [b for _, b in scored_books[:limit]]

    @staticmethod
    def find_similar_books(
        db: Session,
        category: Optional[str] = None,
        author: Optional[str] = None,
        exclude_id: Optional[int] = None,
        limit: int = 4
    ) -> List[Book]:
        """
        Grounded similar-book lookup: retrieves genuine catalogue books
        sharing the same category or author.
        """
        query = db.query(Book)
        if exclude_id:
            query = query.filter(Book.id != exclude_id)

        conditions = []
        if category:
            conditions.append(func.lower(Book.category) == category.strip().lower())
        if author:
            conditions.append(func.lower(Book.author) == author.strip().lower())

        if conditions:
            query = query.filter(or_(*conditions))

        # Prefer available books
        return query.order_by(desc(Book.available_copies > 0), Book.title.asc()).limit(limit).all()

    @staticmethod
    def list_paginated(
        db: Session,
        page: int = 1,
        page_size: int = 12,
        category: Optional[str] = None,
        author: Optional[str] = None,
        search: Optional[str] = None,
        only_available: bool = False,
        sort_by: str = "title",
        sort_order: str = "asc"
    ) -> Tuple[List[Book], int]:
        """Returns paginated books along with total record count."""
        query = db.query(Book)

        if only_available:
            query = query.filter(Book.available_copies > 0)
        if category:
            query = query.filter(func.lower(Book.category) == category.strip().lower())
        if author:
            query = query.filter(func.lower(Book.author).like(f"%{author.strip().lower()}%"))
        if search:
            term = f"%{search.strip().lower()}%"
            query = query.filter(or_(
                func.lower(Book.title).like(term),
                func.lower(Book.author).like(term),
                func.lower(Book.isbn).like(term),
                func.lower(Book.category).like(term),
                func.lower(Book.description).like(term)
            ))

        total = query.count()

        # Sorting
        sort_column = getattr(Book, sort_by, Book.title)
        order_func = desc if sort_order.lower() == "desc" else asc
        query = query.order_by(order_func(sort_column))

        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()
        return items, total

    @staticmethod
    def get_stats(db: Session) -> Dict[str, Any]:
        """Calculates live catalog metrics."""
        total_titles = db.query(func.count(Book.id)).scalar() or 0
        total_copies = db.query(func.sum(Book.total_copies)).scalar() or 0
        avail_copies = db.query(func.sum(Book.available_copies)).scalar() or 0
        borrowed = max(0, total_copies - avail_copies)

        categories = db.query(Book.category).filter(Book.category.isnot(None)).distinct().all()
        cat_list = sorted([c[0] for c in categories if c[0]])

        return {
            "total_titles": total_titles,
            "total_copies": total_copies,
            "available_copies": avail_copies,
            "borrowed_copies": borrowed,
            "total_categories": len(cat_list),
            "categories": cat_list
        }

    @staticmethod
    def create(db: Session, book_in: BookCreate) -> Book:
        db_book = Book(**book_in.model_dump())
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        return db_book

    @staticmethod
    def update(db: Session, db_book: Book, book_in: BookUpdate) -> Book:
        update_data = book_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_book, key, value)
        db.commit()
        db.refresh(db_book)
        return db_book

    @staticmethod
    def delete(db: Session, db_book: Book) -> bool:
        db.delete(db_book)
        db.commit()
        return True
