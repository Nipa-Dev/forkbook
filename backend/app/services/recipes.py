import json
import re
import unicodedata
from uuid import UUID, uuid4

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

    try:
        await conn.execute(
            """
            INSERT INTO recipes (
                id, owner_id, title, description, slug,
                tags, cook_time_minutes, prep_time_minutes, servings, difficulty,
                image_hero_filename, image_thumb_filename,
                equipment, notes, storage
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(recipe_id),
                None,
                recipe.title,
                recipe.description,
                slug,
                json.dumps(recipe.tags),
                recipe.cook_time_minutes,
                recipe.prep_time_minutes,
                recipe.servings,
                recipe.difficulty,
                recipe.image_hero_filename,
                recipe.image_thumb_filename,
                json.dumps(recipe.equipment),
                json.dumps(recipe.notes),
                json.dumps(recipe.storage),
            ),
        )

        if recipe.components:
            await insert_recipe_components(conn, recipe_id, recipe.components)

        created_recipe = await fetch_recipe(conn, recipe_id)

        if not created_recipe:
            raise RuntimeError("Failed to retrieve created recipe")

        await conn.commit()
        return created_recipe

    except Exception:
        await conn.rollback()
        raise


async def insert_recipe_components(
    conn,
    recipe_id: UUID,
    components: list[RecipeComponent],
) -> None:
    for comp_idx, comp in enumerate(components, start=1):
        comp_id = uuid4()

        await conn.execute(
            """
            INSERT INTO recipe_components (id, recipe_id, name, component_order)
            VALUES (?, ?, ?, ?)
            """,
            (
                str(comp_id),
                str(recipe_id),
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

            await conn.execute(
                """
                INSERT INTO ingredients (
                    id, component_id, raw, name, amount, amount_value, unit
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(ing_id),
                    str(comp_id),
                    raw_text,
                    name,
                    amount,
                    amount_value,
                    unit,
                ),
            )

        for step_idx, step in enumerate(comp.steps, start=1):
            step_id = uuid4()

            await conn.execute(
                """
                INSERT INTO steps (
                    id, component_id, step_order, description, timer_seconds
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    str(step_id),
                    str(comp_id),
                    step.step_order or step_idx,
                    step.description or "",
                    step.timer_seconds,
                ),
            )


async def get_recipe_ids(conn) -> list[str]:
    async with conn.execute(
        """
        SELECT id
        FROM recipes
        ORDER BY created_at DESC
        """
    ) as cur:
        rows = await cur.fetchall()

    return [row["id"] for row in rows]


async def fetch_recipe(
    conn,
    recipe_id: UUID,
) -> RecipeRead | None:
    async with conn.execute(
        "SELECT * FROM recipes_with_ratings WHERE id = ?",
        (str(recipe_id),),
    ) as cur:
        recipe = await cur.fetchone()

    if not recipe:
        return None

    async with conn.execute(
        """
        SELECT *
        FROM recipe_components
        WHERE recipe_id = ?
        ORDER BY component_order
        """,
        (str(recipe_id),),
    ) as cur:
        components = await cur.fetchall()

    full_components: list[RecipeComponent] = []

    for comp in components:
        comp_id = comp["id"]

        async with conn.execute(
            "SELECT * FROM ingredients WHERE component_id = ?",
            (comp_id,),
        ) as cur:
            ingredients_raw = await cur.fetchall()

        async with conn.execute(
            """
            SELECT *
            FROM steps
            WHERE component_id = ?
            ORDER BY step_order
            """,
            (comp_id,),
        ) as cur:
            steps_raw = await cur.fetchall()

        full_components.append(
            RecipeComponent(
                **dict(comp),
                ingredients=[Ingredient(**dict(i)) for i in ingredients_raw],
                steps=[Step(**dict(s)) for s in steps_raw],
            )
        )

    recipe_data = dict(recipe)

    recipe_data["tags"] = json.loads(recipe_data["tags"])
    recipe_data["equipment"] = json.loads(recipe_data["equipment"])
    recipe_data["notes"] = json.loads(recipe_data["notes"])
    recipe_data["storage"] = json.loads(recipe_data["storage"])
    return RecipeRead(
        **recipe_data,
        components=full_components,
    )
