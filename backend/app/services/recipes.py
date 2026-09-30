import re
import unicodedata
from uuid import UUID, uuid4

from psycopg.rows import dict_row

from app.schemas.recipe import (
    Ingredient,
    RecipeComponent,
    RecipeCreate,
    RecipeRead,
    Step,
)
from app.utils.parser import parse_ingredients


def slugify(title: str) -> str:
    title = (
        unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    )
    title = title.lower()
    title = re.sub(r"[^a-z0-9]+", "-", title)

    return title.strip("-")


async def create_recipe(conn, recipe: RecipeCreate) -> RecipeRead:
    recipe_id = uuid4()

    short_hash = str(recipe_id).split("-")[0]

    base_slug = slugify(recipe.title)
    slug = f"{base_slug}-{short_hash}" if base_slug else short_hash
    async with conn.transaction():
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                INSERT INTO recipes (
                    id, owner_id, title, description, slug,
                    tags, cook_time_minutes, prep_time_minutes, servings, difficulty,
                    image_hero_filename, image_thumb_filename,
                    equipment, notes, storage
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    recipe_id,
                    None,
                    recipe.title,
                    recipe.description,
                    slug,
                    recipe.tags,
                    recipe.cook_time_minutes,
                    recipe.prep_time_minutes,
                    recipe.servings,
                    recipe.difficulty,
                    recipe.image_hero_filename,
                    recipe.image_thumb_filename,
                    recipe.equipment,
                    recipe.notes,
                    recipe.storage,
                ),
            )

            if recipe.components:
                await insert_recipe_components(cur, recipe_id, recipe.components)

            created_recipe = await fetch_recipe(cur, recipe_id)
            if not created_recipe:
                raise RuntimeError("Failed to retrieve created recipe")

            return created_recipe


async def insert_recipe_components(
    cur, recipe_id: UUID, components: list[RecipeComponent]
) -> None:

    for comp_idx, comp in enumerate(components, start=1):
        comp_id = uuid4()

        await cur.execute(
            """
            INSERT INTO recipe_components (id, recipe_id, name, component_order)
            VALUES (%s, %s, %s, %s)
            """,
            (
                comp_id,
                recipe_id,
                comp.name or "Main",
                comp.component_order or comp_idx,
            ),
        )

        for ing in comp.ingredients:
            ing_id = uuid4()

            raw_text = ing.raw
            name = ing.name
            amount = ing.amount
            amount_value = ing.amount_value
            unit = ing.unit

            if raw_text and not name:
                parsed_list = parse_ingredients(raw_text)
                if parsed_list:
                    parsed = parsed_list[0]
                    name = parsed.name
                    amount = parsed.amount
                    amount_value = parsed.amount_value
                    unit = parsed.unit

            await cur.execute(
                """
                INSERT INTO ingredients (id, component_id, raw, name, amount, amount_value, unit)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    ing_id,
                    comp_id,
                    raw_text,
                    name,
                    amount,
                    amount_value,
                    unit,
                ),
            )

        for step_idx, step in enumerate(comp.steps, start=1):
            step_id = uuid4()

            await cur.execute(
                """
                INSERT INTO steps (id, component_id, step_order, description, timer_seconds)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    step_id,
                    comp_id,
                    step.step_order or step_idx,
                    step.description or "",
                    step.timer_seconds,
                ),
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


async def fetch_recipe(cur, recipe_id: UUID) -> RecipeRead | None:
    await cur.execute(
        "SELECT * FROM recipes_with_ratings WHERE id = %s",
        (recipe_id,),
    )
    recipe = await cur.fetchone()
    if not recipe:
        return None

    await cur.execute(
        """
        SELECT *
        FROM recipe_components
        WHERE recipe_id = %s
        ORDER BY component_order
        """,
        (recipe_id,),
    )
    components = await cur.fetchall()

    full_components: list[RecipeComponent] = []
    for comp in components:
        comp_id = comp["id"]

        await cur.execute(
            "SELECT * FROM ingredients WHERE component_id = %s",
            (comp_id,),
        )
        ingredients_raw = await cur.fetchall()

        await cur.execute(
            """
            SELECT *
            FROM steps
            WHERE component_id = %s
            ORDER BY step_order
            """,
            (comp_id,),
        )
        steps_raw = await cur.fetchall()

        full_components.append(
            RecipeComponent(
                **comp,
                ingredients=[Ingredient(**i) for i in ingredients_raw],
                steps=[Step(**s) for s in steps_raw],
            )
        )

    return RecipeRead(
        **recipe,
        components=full_components,
    )
