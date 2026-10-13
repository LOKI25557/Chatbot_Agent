from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.book import BookResponse


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search term, title, author, ISBN or natural language query")
    filter_category: Optional[str] = None
    filter_author: Optional[str] = None
    only_available: bool = False
    limit: int = Field(10, ge=1, le=50)
    session_id: Optional[str] = None


class SearchIntent(BaseModel):
    intent: str = Field("search", description="search, availability, details, recommendation")
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    category: Optional[str] = None
    only_available: Optional[bool] = None
    keywords: List[str] = Field(default_factory=list)
    raw_query: str = ""


class SearchResponse(BaseModel):
    query: str
    status: str = Field(..., description="'found', 'multiple_found', 'not_found'")
    books: List[BookResponse] = Field(default_factory=list)
    similar_books: List[BookResponse] = Field(default_factory=list, description="Verified catalogue records only")
    ai_explanation: str
    total_results: int
    matched_by: str = Field("exact_title", description="exact_title, isbn, author, category, fuzzy, semantic, none")
    extracted_intent: Optional[SearchIntent] = None
