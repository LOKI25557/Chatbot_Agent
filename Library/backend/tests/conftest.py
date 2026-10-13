import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure backend directory is in sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.models.book import Book

# In-memory SQLite for test isolation
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Creates a fresh in-memory database schema for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    # Seed sample verified test records
    books = [
        Book(
            title="Clean Code",
            author="Robert C. Martin",
            isbn="9780132350884",
            category="Computer Science",
            description="A handbook of agile software craftsmanship.",
            shelf_location="Floor 2, Shelf CS-101",
            total_copies=3,
            available_copies=2
        ),
        Book(
            title="The Pragmatic Programmer",
            author="David Thomas",
            isbn="9780135957059",
            category="Computer Science",
            description="Your journey to mastery.",
            shelf_location="Floor 2, Shelf CS-104",
            total_copies=2,
            available_copies=0  # Out of stock
        ),
        Book(
            title="Introduction to Algorithms",
            author="Thomas H. Cormen",
            isbn="9780262033848",
            category="Algorithms",
            description="Comprehensive guide to algorithms.",
            shelf_location="Floor 2, Shelf ALGO-201",
            total_copies=1,
            available_copies=1
        ),
        Book(
            title="Malgudi Days",
            author="R. K. Narayan",
            isbn="9780140103182",
            category="Fiction",
            description="Stories from Malgudi.",
            shelf_location="Floor 1, Shelf LIT-405",
            total_copies=4,
            available_copies=3
        )
    ]
    session.add_all(books)
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def mock_groq(monkeypatch):
    """
    Ensures tests run hermetically without calling external Groq APIs,
    using the deterministic heuristic fallback methods in GroqService.
    """
    from app.ai.groq_service import GroqService

    def mock_parse_intent(cls, query: str, context=None):
        return cls._heuristic_intent(query)

    def mock_generate_explanation(cls, query, status, books, similar_books=None, matched_by="search"):
        return cls._fallback_explanation(query, status, books, similar_books or [])

    monkeypatch.setattr(GroqService, "parse_intent", classmethod(mock_parse_intent))
    monkeypatch.setattr(GroqService, "generate_explanation", classmethod(mock_generate_explanation))


@pytest.fixture(scope="function")
def client(db_session):
    """TestClient that uses the isolated test database session."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

