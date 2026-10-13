import pytest
from app.core.config import settings

ADMIN_HEADERS = {"X-Admin-Key": settings.ADMIN_SECRET_KEY}


def test_admin_auth_unauthorized(client):
    # Missing header -> 401
    res1 = client.get("/api/v1/admin/stats")
    assert res1.status_code == 401

    # Invalid header -> 403
    res2 = client.get("/api/v1/admin/stats", headers={"X-Admin-Key": "wrong-secret"})
    assert res2.status_code == 403


def test_admin_get_stats(client):
    response = client.get("/api/v1/admin/stats", headers=ADMIN_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["total_titles"] == 4
    assert data["total_copies"] == 10
    assert data["available_copies"] == 6
    assert data["borrowed_copies"] == 4
    assert "Computer Science" in data["categories"]


def test_admin_create_book(client):
    payload = {
        "title": "Structure and Interpretation of Computer Programs",
        "author": "Harold Abelson",
        "isbn": "9780262510875",
        "category": "Computer Science",
        "total_copies": 2,
        "available_copies": 2,
        "shelf_location": "Floor 2, Shelf CS-120"
    }
    response = client.post("/api/v1/admin/books", json=payload, headers=ADMIN_HEADERS)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["title"] == payload["title"]
    assert data["is_available"] is True


def test_admin_create_book_invalid_copies(client):
    payload = {
        "title": "Bad Book",
        "total_copies": 1,
        "available_copies": 5  # Invalid: available > total
    }
    response = client.post("/api/v1/admin/books", json=payload, headers=ADMIN_HEADERS)
    assert response.status_code == 422  # Pydantic validation error


def test_admin_update_book(client):
    update_payload = {"available_copies": 0}
    response = client.put("/api/v1/admin/books/1", json=update_payload, headers=ADMIN_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["available_copies"] == 0
    assert data["is_available"] is False


def test_admin_delete_book(client):
    response = client.delete("/api/v1/admin/books/4", headers=ADMIN_HEADERS)
    assert response.status_code == 200
    assert response.json()["success"] is True

    # Verify deleted
    get_res = client.get("/api/v1/books/4")
    assert get_res.status_code == 404
