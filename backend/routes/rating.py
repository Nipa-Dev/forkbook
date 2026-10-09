from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from backend.schemas.rating import RecipeRatingCreate
from backend.schemas.user import UserInDB
from backend.utils.auth import get_current_active_user
from backend.utils.db import GetConnection

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
        INSERT INTO recipe_ratings (
            id, recipe_id, user_id, rating, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT (recipe_id, user_id)
        DO UPDATE SET
            rating = excluded.rating,
            updated_at = CURRENT_TIMESTAMP
        RETURNING *;
    """

    try:
        async with conn.execute(
            query,
            (
                str(uuid4()),
                str(recipe_id),
                str(current_user.user_id),
                rating_data.rating,
            ),
        ) as cur:
            rating = await cur.fetchone()

        await conn.commit()

        return dict(rating) if rating else None

    except Exception:
        await conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to save rating",
        )


@router.delete("/{recipe_id}")
async def delete_rating(recipe_id: str): ...
