import re
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.book import Book
from app.repositories.book_repository import BookRepository
from app.schemas.search import SearchRequest, SearchResponse, SearchIntent
from app.schemas.book import BookResponse
from app.ai.groq_service import GroqService


class SearchService:
    """Core service executing grounded catalogue search with AI-assisted intent interpretation."""

    @classmethod
    def execute_search(cls, db: Session, request: SearchRequest) -> SearchResponse:
        raw_query = request.query.strip()
        matched_by = "exact_title"

        # 1. Fast Path: Check for exact ISBN first
        isbn_candidate = re.sub(r"[^\dX]", "", raw_query.upper())
        if len(isbn_candidate) in (10, 13):
            book = BookRepository.get_by_isbn(db, isbn_candidate)
            if book:
                books = [book]
                if request.only_available and book.available_copies <= 0:
                    books = []
                if books:
                    explanation = GroqService.generate_explanation(raw_query, "found", books, [])
                    return SearchResponse(
                        query=raw_query,
                        status="found",
                        books=[BookResponse.model_validate(b) for b in books],
                        similar_books=[],
                        ai_explanation=explanation,
                        total_results=1,
                        matched_by="isbn"
                    )

        # 2. Fast Path: Exact case-insensitive title match
        exact_matches = BookRepository.find_exact_title(db, raw_query)
        if request.only_available:
            exact_matches = [b for b in exact_matches if b.available_copies > 0]

        if exact_matches:
            status = "found" if len(exact_matches) == 1 else "multiple_found"
            explanation = GroqService.generate_explanation(raw_query, status, exact_matches, [])
            return SearchResponse(
                query=raw_query,
                status=status,
                books=[BookResponse.model_validate(b) for b in exact_matches],
                similar_books=[],
                ai_explanation=explanation,
                total_results=len(exact_matches),
                matched_by="exact_title"
            )

        # 3. Conversational / Intelligent Path: Parse intent with Groq / heuristic
        intent = GroqService.parse_intent(raw_query)

        # Apply frontend filters if provided
        final_category = request.filter_category or intent.category
        final_author = request.filter_author or intent.author
        only_avail = request.only_available or bool(intent.only_available)

        # Query real database records using parsed criteria
        results = BookRepository.search_catalogue(
            db=db,
            title=intent.title,
            author=final_author,
            isbn=intent.isbn,
            category=final_category,
            keywords=intent.keywords,
            only_available=only_avail,
            limit=request.limit
        )

        similar_books: List[Book] = []

        if results:
            status = "found" if len(results) == 1 else "multiple_found"
            matched_by = "ai_semantic" if intent.keywords else "partial_match"
        else:
            status = "not_found"
            matched_by = "none"

            # Grounded similar recommendations: lookup actual books by category or author
            similar_books = BookRepository.find_similar_books(
                db=db,
                category=final_category,
                author=final_author,
                limit=4
            )

            # If still empty, provide general available books from the library
            if not similar_books:
                general_books, _ = BookRepository.list_paginated(db=db, page=1, page_size=4, only_available=True)
                similar_books = general_books

        # Generate truthful, grounded explanation based ONLY on verified database output
        explanation = GroqService.generate_explanation(raw_query, status, results, similar_books)

        return SearchResponse(
            query=raw_query,
            status=status,
            books=[BookResponse.model_validate(b) for b in results],
            similar_books=[BookResponse.model_validate(b) for b in similar_books],
            ai_explanation=explanation,
            total_results=len(results),
            matched_by=matched_by,
            extracted_intent=intent
        )
