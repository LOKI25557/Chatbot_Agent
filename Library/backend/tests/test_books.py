import pytest


def test_list_books_pagination(client):
    response = client.get("/api/v1/books?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total"] == 4
    assert data["total_pages"] == 2
    assert len(data["items"]) == 2


def test_get_book_by_id(client):
    response = client.get("/api/v1/books/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Clean Code"
    assert data["is_available"] is True
    assert data["borrowed_copies"] == 1


def test_get_book_not_found(client):
    response = client.get("/api/v1/books/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_similar_books_endpoint(client):
    response = client.get("/api/v1/books/1/similar?limit=2")
    assert response.status_code == 200
    similar = response.json()
    assert isinstance(similar, list)
    # Book 1 is Clean Code (Computer Science), so Pragmatic Programmer should be similar
    assert all(b["id"] != 1 for b in similar)
