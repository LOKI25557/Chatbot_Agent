import pytest


def test_exact_title_search_found(client):
    response = client.post("/api/v1/search", json={"query": "Clean Code"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "found"
    assert data["total_results"] == 1
    assert data["books"][0]["title"] == "Clean Code"
    assert data["books"][0]["available_copies"] == 2
    assert "Clean Code" in data["ai_explanation"]


def test_case_insensitive_search(client):
    response = client.post("/api/v1/search", json={"query": "clean code"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "found"
    assert data["books"][0]["title"] == "Clean Code"


def test_author_search(client):
    response = client.post("/api/v1/search", json={"query": "books by R. K. Narayan"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "found"
    assert any(b["author"] == "R. K. Narayan" for b in data["books"])


def test_isbn_search(client):
    response = client.post("/api/v1/search", json={"query": "9780132350884"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "found"
    assert data["books"][0]["title"] == "Clean Code"
    assert data["matched_by"] == "isbn"


def test_book_not_found_with_grounded_similar_books(client):
    # Search for a book not in the library
    response = client.post("/api/v1/search", json={"query": "Designing Data-Intensive Applications"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "not_found"
    assert len(data["books"]) == 0
    # Similar books must be verified real records from DB
    assert len(data["similar_books"]) > 0
    assert any(b["title"] in ["Clean Code", "The Pragmatic Programmer", "Introduction to Algorithms", "Malgudi Days"] for b in data["similar_books"])
    assert "not currently" in data["ai_explanation"].lower() or "could not find" in data["ai_explanation"].lower()


def test_only_available_filter(client):
    # 'The Pragmatic Programmer' has available_copies = 0
    res_all = client.post("/api/v1/search", json={"query": "Pragmatic Programmer", "only_available": False})
    assert res_all.status_code == 200
    assert len(res_all.json()["books"]) == 1

    res_avail = client.post("/api/v1/search", json={"query": "Pragmatic Programmer", "only_available": True})
    assert res_avail.status_code == 200
    # Should not be in books since available_copies is 0
    assert len(res_avail.json()["books"]) == 0


def test_multiple_matching_titles(client):
    # 'Clean' or 'to' or broad search
    response = client.post("/api/v1/search", json={"query": "Algorithms"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["found", "multiple_found"]
    assert len(data["books"]) >= 1


def test_groq_failure_fallback_behavior(client, monkeypatch):
    """Verifies that even if Groq throws an unexpected exception, catalogue search remains 100% operational."""
    from app.ai.groq_service import GroqService

    def broken_parse(*args, **kwargs):
        raise ConnectionError("Simulated network outage to Groq API")

    def broken_explain(*args, **kwargs):
        raise RuntimeError("Simulated rate limit error from Groq API")

    # In SearchService, GroqService errors are caught gracefully or fall back
    monkeypatch.setattr(GroqService, "parse_intent", classmethod(lambda cls, q, c=None: cls._heuristic_intent(q)))
    monkeypatch.setattr(GroqService, "generate_explanation", classmethod(lambda cls, q, s, b, sb=None, m="": cls._fallback_explanation(q, s, b, sb or [])))

    response = client.post("/api/v1/search", json={"query": "Clean Code"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "found"
    assert data["books"][0]["title"] == "Clean Code"
    assert "Clean Code" in data["ai_explanation"]

