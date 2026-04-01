import uuid
from typing import List

from fastapi import APIRouter, HTTPException
from psycopg.rows import dict_row

from utils.schemas import RecipeCreate, RecipeRead
from utils.dependencies import GetConnection

router = APIRouter()


@router.get("/recipe/all", response_model=List[RecipeRead])
async def get_all_recipes(conn: GetConnection):
    result = []

    async with conn.cursor(row_factory=dict_row) as cur:
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


@router.post("/recipe/new", response_model=RecipeRead)
async def add_recipe(conn: GetConnection, recipe: RecipeCreate):
    recipe_id = str(uuid.uuid4())

    async with conn.cursor() as cur:
        await cur.execute(
            """
            INSERT INTO recipes (id, owner_id, title, description, tags, time_minutes, difficulty)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                recipe_id,
                None,
                recipe.title,
                recipe.description,
                recipe.tags,
                recipe.time_minutes,
                recipe.difficulty,
            ),
        )

        for ing in recipe.ingredients:
            ing_id = str(uuid.uuid4())
            await cur.execute(
                """
                INSERT INTO ingredients (id, recipe_id, name, amount, unit)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (ing_id, recipe_id, ing.name, ing.amount, ing.unit),
            )

        for step in recipe.steps:
            step_id = str(uuid.uuid4())
            await cur.execute(
                """
                INSERT INTO steps (id, recipe_id, step_order, description, timer_seconds)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    step_id,
                    recipe_id,
                    step.step_order,
                    step.description,
                    step.timer_seconds,
                ),
            )

    return RecipeRead(
        id=recipe_id,
        title=recipe.title,
        description=recipe.description,
        ingredients=recipe.ingredients,
        steps=recipe.steps,
        tags=recipe.tags,
        time_minutes=recipe.time_minutes,
        difficulty=recipe.difficulty,
    )


@router.get("/recipe/tag", response_model=List[RecipeRead])
async def get_tag(tag: str, conn: GetConnection):
    result = []

    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            "SELECT * FROM recipes WHERE tags @> ARRAY[%s]::text[]",
            (tag,),
        )
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

            result.append(RecipeRead(**recipe, ingredients=ingredients, steps=steps))

    return result


@router.get("/recipe/id", response_model=RecipeRead)
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
