import pytest

from app.utils.config import settings


@pytest.mark.anyio
async def test_docs(client):
    response = await client.get("/docs")
    assert response.status_code == 200

@pytest.mark.anyio
async def test_openapi(client):
    response = await client.get("/openapi.json")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_root(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Hello world!"}


@pytest.mark.anyio
async def test_get_jwks_success(client):
    response = await client.get("/.well-known/jwks.json")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "public, max-age=86400"

    data = response.json()
    assert "keys" in data
    assert len(data["keys"]) == 1

    key = data["keys"][0]
    assert key["kid"] == settings.JWT_KID
    assert key["use"] == "sig"
    assert key["alg"] == "RS256"
    assert key["kty"] == "RSA"
    assert "n" in key
    assert "e" in key
