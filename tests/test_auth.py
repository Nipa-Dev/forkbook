import pytest

from backend.utils.auth import decrypt_email


@pytest.fixture
async def registered_user(client):
    """Creates a default user for auth tests and returns credentials."""
    credentials = {
        "username": "authtestuser",
        "email": "authuser@example.com",
        "password": "securepassword123",
    }

    response = await client.post("/auth/add-user", json=credentials)
    assert response.status_code == 201
    return credentials


@pytest.mark.anyio
async def test_create_user_success(client, test_db):
    payload = {
        "username": "testuser",
        "email": "user@example.com",
        "password": "securepassword123",
    }

    response = await client.post("/auth/add-user", json=payload)
    assert response.status_code == 201

    async with test_db.execute(
        "SELECT user_id, username, email_bidx, email_enc, key_version FROM users WHERE username = ?",
        ("testuser",),
    ) as cursor:
        user = await cursor.fetchone()
        assert user is not None
        assert user["username"] == "testuser"
        assert user["email_bidx"] is not None
        assert user["email_enc"] is not None

        decrypted = decrypt_email(user["email_enc"], user["key_version"])
        assert decrypted == "user@example.com"


@pytest.mark.anyio
async def test_login_for_access_token(client, registered_user):
    login_data = {
        "username": registered_user["username"],
        "password": registered_user["password"],
    }

    response = await client.post("/auth/token", data=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


@pytest.mark.anyio
async def test_login_invalid_password(client, registered_user):
    login_data = {
        "username": registered_user["username"],
        "password": "wrongpassword123",
    }

    response = await client.post("/auth/token", data=login_data)

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.anyio
async def test_protected_route(auth_client):
    response = await auth_client.get("/auth/users/me")
    assert response.status_code == 200
