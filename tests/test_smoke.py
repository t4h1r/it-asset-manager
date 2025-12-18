import pytest

from app import app as flask_app


@pytest.fixture
def app():
    """Provide Flask app instance for pytest-flask."""
    flask_app.config["TESTING"] = True
    return flask_app


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


