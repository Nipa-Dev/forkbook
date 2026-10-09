import json
from pathlib import Path

import pytest
from httpx import AsyncClient

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def valid_recipe_payload():
    json_path = FIXTURES_DIR / "test_recipe.json"
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.anyio
async def test_create_recipe_success(client: AsyncClient, valid_recipe_payload: dict):
    response = await client.post("/recipes/", json=valid_recipe_payload)

    assert response.status_code == 201

    data = response.json()
    assert data["title"] == valid_recipe_payload["title"]
    assert data["description"] == valid_recipe_payload["description"]
    assert len(data["components"]) == 1
    assert data["components"][0]["name"] == "Batter"


@pytest.mark.anyio
async def test_create_recipe_invalid(client: AsyncClient):
    response = await client.post("/recipes/", json={})

    assert response.status_code == 422
