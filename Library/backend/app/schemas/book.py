from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Book title")
    author: Optional[str] = Field(None, max_length=255, description="Author name")
    isbn: Optional[str] = Field(None, max_length=32, description="International Standard Book Number")
    publisher: Optional[str] = Field(None, max_length=255)
    publication_year: Optional[int] = Field(None, ge=1000, le=2100)
    category: Optional[str] = Field(None, max_length=100, description="Subject genre / category")
    description: Optional[str] = None
    cover_image_url: Optional[str] = Field(None, max_length=500)
    shelf_location: Optional[str] = Field(None, max_length=100)
    total_copies: int = Field(1, ge=0, description="Total physical copies owned")
    available_copies: int = Field(1, ge=0, description="Copies currently available on shelf")

    @field_validator("title")
    @classmethod
    def clean_title(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Title cannot be whitespace only")
        return cleaned

    @field_validator("isbn")
    @classmethod
    def clean_isbn(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        # Normalize ISBN by stripping dashes and spaces
        cleaned = v.replace("-", "").replace(" ", "").strip()
        return cleaned or None

    @model_validator(mode="after")
    def validate_copies_relationship(self):
        if self.available_copies > self.total_copies:
            raise ValueError(
                f"available_copies ({self.available_copies}) cannot exceed total_copies ({self.total_copies})"
            )
        return self


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, max_length=255)
    isbn: Optional[str] = Field(None, max_length=32)
    publisher: Optional[str] = Field(None, max_length=255)
    publication_year: Optional[int] = Field(None, ge=1000, le=2100)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    cover_image_url: Optional[str] = Field(None, max_length=500)
    shelf_location: Optional[str] = Field(None, max_length=100)
    total_copies: Optional[int] = Field(None, ge=0)
    available_copies: Optional[int] = Field(None, ge=0)


class BookResponse(BookBase):
    id: int
    is_available: bool
    borrowed_copies: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookPagination(BaseModel):
    items: List[BookResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class CatalogStats(BaseModel):
    total_titles: int
    total_copies: int
    available_copies: int
    borrowed_copies: int
    total_categories: int
    categories: List[str]
