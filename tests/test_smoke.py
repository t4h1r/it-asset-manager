"""
Smoke tests - basic functionality checks.
These tests use fixtures from conftest.py.
"""


def test_index_loads(client):
    """Home page should load (either directly or via redirect)."""
    response = client.get("/")
    assert response.status_code in (200, 302)


def test_login_page_loads(client):
    """Login page should return HTTP 200."""
    response = client.get("/login")
    assert response.status_code == 200


def test_register_page_loads(client):
    """Register page should return HTTP 200."""
    response = client.get("/register")
    assert response.status_code == 200


