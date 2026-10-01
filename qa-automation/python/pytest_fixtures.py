"""conftest.py

Reusable, session-scoped pytest fixtures for API integration testing.
Includes a minimal in-process FastAPI app (acting as the system under test)
so this file is fully self-contained and runnable with `pytest`.
"""

import pytest
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.testclient import TestClient

# --- In-memory "database" and app under test -------------------------------

db: dict[int, dict] = {}
VALID_TOKEN = "test-token-123"  # noqa: S105 - test-only credential

app = FastAPI()


def _verify_token(authorization: str = Header(...)) -> None:
    if authorization != f"Bearer {VALID_TOKEN}":
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/login")
def login():
    return {"access_token": VALID_TOKEN}


@app.post("/items")
def create_item(item: dict, _: None = Depends(_verify_token)):
    item_id = len(db) + 1
    db[item_id] = item
    return {"id": item_id, **item}


# --- Fixtures ----------------------------------------------------------------

@pytest.fixture(scope="session")
def client() -> TestClient:
    """A single TestClient instance shared across the whole test session."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def auth_token(client: TestClient) -> str:
    """Authenticate once per session and reuse the resulting token."""
    response = client.post("/login")
    response.raise_for_status()
    return response.json()["access_token"]


@pytest.fixture(scope="session", autouse=True)
def database_cleanup():
    """Ensure the test database starts empty and is wiped after the session."""
    db.clear()
    yield db
    db.clear()
