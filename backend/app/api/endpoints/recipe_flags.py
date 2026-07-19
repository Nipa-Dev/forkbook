from enum import Enum
from uuid import UUID, uuid4

from fastapi import APIRouter, Query
from psycopg.rows import dict_row
from pydantic import BaseModel

from app.schemas.responses import StatusResponse
from app.utils.db import GetConnection
from app.utils.dependencies import CurrentUser

router = APIRouter()


class RecipeFlagType(str, Enum):
    BOOKMARK = "bookmark"
    MADE = "made"


class ToggleFlagRequest(BaseModel):
    active: bool
    flag_type: RecipeFlagType = RecipeFlagType.BOOKMARK


@router.get("/saved")
async def get_user_saved_recipes(
    conn: GetConnection,
    current_user: CurrentUser,
    flag_type: RecipeFlagType = Query(RecipeFlagType.BOOKMARK),
):
    async with conn.transaction():
        async with conn.cursor(row_factory=dict_row) as cur:
            ...


@router.post("/{recipe_id}/toggle-saved", response_model=StatusResponse)
async def toggle_flag(
    recipe_id: UUID,
    payload: ToggleFlagRequest,
    conn: GetConnection,
    current_user: CurrentUser,
):
    async with conn.transaction():
        async with conn.cursor(row_factory=dict_row) as cur:
            if payload.active:
                await cur.execute(
                    """
                    INSERT INTO recipe_flags (id, user_id, recipe_id, flag_type)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (user_id, recipe_id, flag_type) DO NOTHING
                    """,
                    (uuid4(), current_user.user_id, recipe_id, payload.flag_type.value),
                )
                message = f"Recipe successfully marked as {payload.flag_type.value}."
            else:
                await cur.execute(
                    """
                    DELETE FROM recipe_flags
                    WHERE user_id = %s AND recipe_id = %s AND flag_type = %s
                    """,
                    (current_user.user_id, recipe_id, payload.flag_type.value),
                )
                message = f"Recipe {payload.flag_type.value} flag removed."

        return {"message": message}
