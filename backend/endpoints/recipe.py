import uuid
from typing import List

from fastapi import APIRouter, HTTPException, UploadFile, File
from psycopg.rows import dict_row

from utils.schemas import RecipeCreate, RecipeRead
from utils.dependencies import GetConnection
from utils.services.recipes import create_recipe
from utils.parser import parse_recipe

router = APIRouter()


@router.get("/", response_model=List[RecipeRead])
async def get_recipes(conn: GetConnection, tag: str | None = None):
    result = []

    async with conn.cursor(row_factory=dict_row) as cur:
        if tag:
            await cur.execute(
                "SELECT * FROM recipes WHERE tags @> ARRAY[%s]::text[]",
                (tag,),
            )
        else:
            await cur.execute("SELECT * FROM recipes")

        recipes = await cur.fetchall()

        for recipe in recipes:
            recipe_id = recipe["id"]

            await cur.execute(
                "SELECT * FROM ingredients WHERE recipe_id = %s",
                (recipe_id,),
            )
            ingredients = await cur.fetchall()

            await cur.execute(
                "SELECT * FROM steps WHERE recipe_id = %s ORDER BY step_order",
                (recipe_id,),
            )
            steps = await cur.fetchall()

            result.append(
                RecipeRead(
                    **recipe,
                    ingredients=ingredients,
                    steps=steps,
                )
            )

    return result


@router.post("/import", response_model=RecipeRead)
async def import_recipe(conn: GetConnection, file: UploadFile = File(...)):
    md = (await file.read()).decode("utf-8")
    recipe = parse_recipe(md)
    return await create_recipe(conn, recipe)


@router.post("/", response_model=RecipeRead)
async def add_recipe(conn: GetConnection, recipe: RecipeCreate):
    return await create_recipe(conn, recipe)


@router.get("/{recipe_id}", response_model=RecipeRead)
async def get_recipe(conn: GetConnection, recipe_id: str):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute("SELECT * FROM recipes WHERE id = %s", (recipe_id,))
        recipe = await cur.fetchone()
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")

        await cur.execute(
            "SELECT * FROM ingredients WHERE recipe_id = %s", (recipe_id,)
        )
        ingredients = await cur.fetchall()

        await cur.execute(
            "SELECT * FROM steps WHERE recipe_id = %s ORDER BY step_order",
            (recipe_id,),
        )
        steps = await cur.fetchall()

    return RecipeRead(
        **recipe,
        ingredients=ingredients,
        steps=steps,
    )


@router.delete("/{recipe_id}")
async def delete_recipe(conn: GetConnection, recipe_id: str):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            "DELETE FROM recipes WHERE id = %s",
            (recipe_id,),
        )

        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Recipe not found")

    return {"deleted_id": recipe_id}
