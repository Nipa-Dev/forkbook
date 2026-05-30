import uuid
import unicodedata
import re

from psycopg.rows import dict_row
from psycopg.types.json import Json
from app.schemas.recipe import RecipeCreate, RecipeRead


def slugify(title: str) -> str:
    title = (
        unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    )
    title = title.lower()
    title = re.sub(r"[^a-z0-9]+", "-", title)

    return title.strip("-")


async def create_recipe(conn, recipe: RecipeCreate) -> RecipeRead:
    recipe_id = str(uuid.uuid4())
    slug = slugify(recipe.title)
    async with conn.cursor() as cur:
        await cur.execute(
            """
            INSERT INTO recipes (
                id, owner_id, title, description, slug,
                tags, time_minutes, difficulty, image_url,
                equipment, notes, storage
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                recipe_id,
                None,
                recipe.title,
                recipe.description,
                slug,
                recipe.tags,
                recipe.time_minutes,
                recipe.difficulty,
                recipe.image_url if recipe.image_url else None,
                Json(recipe.equipment),
                Json(recipe.notes),
                Json(recipe.storage),
            ),
        )

        for comp in recipe.components:
            comp_id = str(uuid.uuid4())

            await cur.execute(
                """
                INSERT INTO recipe_components (
                    id, recipe_id, name, component_order
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    comp_id,
                    recipe_id,
                    comp.name,
                    comp.component_order,
                ),
            )

            for ing in comp.ingredients:
                await cur.execute(
                    """
                    INSERT INTO ingredients (
                        id, component_id, name,
                        amount, amount_value, unit
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        str(uuid.uuid4()),
                        comp_id,
                        ing.name,
                        ing.amount,
                        ing.amount_value,
                        ing.unit,
                    ),
                )

            for step in comp.steps:
                await cur.execute(
                    """
                    INSERT INTO steps (
                        id, component_id, step_order,
                        description, timer_seconds
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        str(uuid.uuid4()),
                        comp_id,
                        step.step_order,
                        step.description,
                        step.timer_seconds,
                    ),
                )

    return RecipeRead(
        id=recipe_id,
        **recipe.model_dump(),
    )


async def get_recipe_ids(conn) -> list[str]:
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            """
            SELECT id
            FROM recipes
            ORDER BY created_at DESC
            """
        )
        rows = await cur.fetchall()

    return [str(row["id"]) for row in rows]
