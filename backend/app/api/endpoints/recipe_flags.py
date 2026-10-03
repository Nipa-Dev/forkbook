from enum import Enum
from uuid import UUID, uuid4

from fastapi import APIRouter, Query
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


import json


@router.get("/saved")
async def get_user_saved_recipes(
    conn: GetConnection,
    current_user: CurrentUser,
    flag_type: RecipeFlagType | None = Query(None),
):
    query = """
        SELECT
            rf.id AS flag_id,
            rf.recipe_id,
            rf.flag_type,
            r.*
        FROM recipe_flags rf
        JOIN recipes r ON r.id = rf.recipe_id
        WHERE rf.user_id = ?
    """
    params = [str(current_user.user_id)]

    if flag_type:
        query += " AND rf.flag_type = ?"
        params.append(flag_type.value)

    query += " ORDER BY rf.created_at DESC"

    async with conn.execute(query, params) as cur:
        rows = await cur.fetchall()

    result = []
    for row in rows:
        recipe = dict(row)
        recipe["tags"] = json.loads(recipe["tags"])
        recipe["equipment"] = json.loads(recipe["equipment"])
        recipe["notes"] = json.loads(recipe["notes"])
        recipe["storage"] = json.loads(recipe["storage"])
        result.append(recipe)

    return result


@router.post("/{recipe_id}/toggle-saved", response_model=StatusResponse)
async def toggle_flag(
    recipe_id: UUID,
    payload: ToggleFlagRequest,
    conn: GetConnection,
    current_user: CurrentUser,
):
    if payload.active:
        await conn.execute(
            """
            INSERT INTO recipe_flags (id, user_id, recipe_id, flag_type)
            VALUES (?, ?, ?, ?)
            ON CONFLICT (user_id, recipe_id, flag_type) DO NOTHING
            """,
            (
                str(uuid4()),
                str(current_user.user_id),
                str(recipe_id),
                payload.flag_type.value,
            ),
        )
        message = f"Recipe successfully marked as {payload.flag_type.value}."

    else:
        await conn.execute(
            """
            DELETE FROM recipe_flags
            WHERE user_id = ? AND recipe_id = ? AND flag_type = ?
            """,
            (
                str(current_user.user_id),
                str(recipe_id),
                payload.flag_type.value,
            ),
        )
        message = f"Recipe {payload.flag_type.value} flag removed."

    await conn.commit()

    return {"message": message}
