import aiosqlite
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import BASE_DIR, app
from app.utils.db import _get_conn


@pytest.fixture
async def test_db():
    schema_path = BASE_DIR / "db" / "init.sql"

    # Use in-memory database
    async with aiosqlite.connect(":memory:") as db:
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA foreign_keys = ON")

        if schema_path.exists():
            await db.executescript(schema_path.read_text(encoding="utf-8"))
            await db.commit()

        yield db


@pytest.fixture
async def client(test_db):
    async def _override_get_conn():
        yield test_db

    app.dependency_overrides[_get_conn] = _override_get_conn

    app.state.db = test_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()

@pytest.fixture
async def auth_client(client):
    """AsyncClient pre-configured with a valid Bearer token header."""
    credentials = {
        "username": "testuser",
        "email": "user@example.com",
        "password": "securepassword123",
    }
    
    await client.post("/auth/add-user", json=credentials)
    
    login_res = await client.post("/auth/token", data={
        "username": credentials["username"],
        "password": credentials["password"],
    })
    token = login_res.json()["access_token"]
    
    client.headers["Authorization"] = f"Bearer {token}"
    return client