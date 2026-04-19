import uuid
from utils.schemas import RecipeCreate, RecipeRead


async def create_recipe(conn, recipe: RecipeCreate) -> RecipeRead:
    recipe_id = str(uuid.uuid4())

    async with conn.cursor() as cur:
        await cur.execute(
            """
            INSERT INTO recipes (
                id, owner_id, title, description,
                tags, time_minutes, difficulty
            )
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
            await cur.execute(
                """
                INSERT INTO ingredients (
                    id, recipe_id, name, amount, amount_value, unit
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    str(uuid.uuid4()),
                    recipe_id,
                    ing.name,
                    ing.amount,
                    ing.amount_value,
                    ing.unit,
                ),
            )

        for step in recipe.steps:
            await cur.execute(
                """
                INSERT INTO steps (
                    id, recipe_id, step_order,
                    description, timer_seconds
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    str(uuid.uuid4()),
                    recipe_id,
                    step.step_order,
                    step.description,
                    step.timer_seconds,
                ),
            )

    return RecipeRead(
        id=recipe_id,
        **recipe.model_dump(),
    )
