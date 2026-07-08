from psycopg.rows import dict_row
from uuid import uuid4
from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from app.schemas.rating import RecipeRatingCreate
from app.schemas.user import UserInDB
from app.core.dependencies import GetConnection
from app.utils.auth import get_current_active_user

router = APIRouter()


@router.get("/{recipe_id}")
async def get_rating(recipe_id: str): ...


@router.post("/{recipe_id}")
async def add_or_update_rating(
    conn: GetConnection,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    recipe_id: UUID,
    rating_data: RecipeRatingCreate,
):
    query = """
        INSERT INTO recipe_ratings (id, recipe_id, user_id, rating, created_at, updated_at)
        VALUES (%s, %s, %s, %s, NOW(), NOW())
        ON CONFLICT (recipe_id, user_id)
        DO UPDATE SET
            rating = EXCLUDED.rating,
            updated_at = NOW()
        RETURNING *;
    """
    async with conn.cursor(row_factory=dict_row) as cur:
        try:
            await cur.execute(
                query,
                (str(uuid4()), recipe_id, current_user.user_id, rating_data.rating),
            )
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


@router.delete("/{recipe_id}")
async def delete_rating(recipe_id: str): ...
