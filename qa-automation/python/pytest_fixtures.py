# conftest.py
# Reusable pytest fixtures for API testing: a Flask app factory, a test
# client, an authenticated token, and automatic database cleanup between
# tests. The "database" here is an in-memory dict to keep the example
# self-contained and runnable without external services.

import pytest
from flask import Flask, jsonify, request

# --- In-memory "database" shared across the app ---------------------------
_DB = {"users": {}, "tokens": {}}


def create_app():
    app = Flask(__name__)

    @app.post("/login")
    def login():
        username = request.json.get("username", "tester")
        token = f"token-{username}"
        _DB["tokens"][token] = username
        return jsonify(token=token)

    @app.post("/users")
    def create_user():
        data = request.json
        _DB["users"][data["id"]] = data
        return jsonify(data), 201

    @app.get("/users/<user_id>")
    def get_user(user_id):
        user = _DB["users"].get(user_id)
        return (jsonify(user), 200) if user else (jsonify(error="not found"), 404)

    return app


@pytest.fixture(scope="session")
def app():
    """Create the Flask application once per test session."""
    return create_app()


@pytest.fixture(scope="session")
def client(app):
    """Session-scoped test client for issuing HTTP requests."""
    return app.test_client()


@pytest.fixture(scope="session")
def auth_token(client):
    """Authenticate once per session and reuse the resulting token."""
    response = client.post("/login", json={"username": "tester"})
    assert response.status_code == 200
    return response.get_json()["token"]


@pytest.fixture(autouse=True)
def database_cleanup():
    """Ensure each test starts with a clean database and cleans up after."""
    yield
    _DB["users"].clear()
    _DB["tokens"].clear()
