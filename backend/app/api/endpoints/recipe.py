import json
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status
from psycopg.rows import dict_row

from app.schemas.recipe import PaginatedRecipes, RecipeCreate, RecipeRead, RecipeUpdate
from app.services.recipes import create_recipe, get_recipe_ids
from app.utils.config import settings
from app.utils.db import GetConnection
from app.utils.images import save_recipe_images
from app.utils.parser import parse_recipe

router = APIRouter()

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[4]
FRONTEND_IMAGES_DIR = PROJECT_ROOT / "frontend" / "static" / "images"


@router.get("/", response_model=PaginatedRecipes)
async def get_recipes(
    conn: GetConnection,
    tag: list[str] | None = Query(default=None),
    search: str | None = Query(default=None),
    page_size: int = Query(default=10, ge=1, le=100),
    page: int = Query(default=1, ge=1),
):
    result = []
    offset = (page - 1) * page_size

    async with conn.cursor(row_factory=dict_row) as cur:
        conditions = []
        params = []

        if tag:
            conditions.append("tags && %s::text[]")
            params.append(tag)

        if search:
            conditions.append("(title ILIKE %s OR description ILIKE %s)")
            like = f"%{search}%"
            params.extend([like, like])

        where_clause = ""
        if conditions:
            where_clause += " WHERE " + " AND ".join(conditions)

        count_query = f"""
            SELECT COUNT(*) AS total
            FROM recipes
            {where_clause}
        """

        await cur.execute(count_query, params)
        total = (await cur.fetchone())["total"]

        recipe_query = f"""
            SELECT *
            FROM recipes_with_ratings
            {where_clause}
            ORDER BY title
            LIMIT %s
            OFFSET %s
        """

        await cur.execute(recipe_query, [*params, page_size, offset])
        recipes = await cur.fetchall()
        for recipe in recipes:
            recipe_id = recipe["id"]

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

            full_components = []

            for comp in components:
                comp_id = comp["id"]

                await cur.execute(
                    """
                    SELECT *
                    FROM ingredients
                    WHERE component_id = %s
                    """,
                    (comp_id,),
                )
                ingredients = await cur.fetchall()

                await cur.execute(
                    """
                    SELECT *
                    FROM steps
                    WHERE component_id = %s
                    ORDER BY step_order
                    """,
                    (comp_id,),
                )
                steps = await cur.fetchall()

                full_components.append(
                    {
                        **comp,
                        "ingredients": ingredients,
                        "steps": steps,
                    }
                )
            try:
                result.append(
                    RecipeRead(
                        **recipe,
                        components=full_components,
                    )
                )
            except Exception as e:
                print(e)
                raise

    return PaginatedRecipes(
        items=result,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/import", response_model=RecipeRead)
async def import_recipe(
    conn: GetConnection,
    recipe_file: UploadFile,
    image_file: UploadFile | None = None,
):
    md = (await recipe_file.read()).decode("utf-8")
    recipe = parse_recipe(md)

    if image_file and image_file.filename:
        ext = Path(image_file.filename).suffix.lower()

        if ext not in settings.VALID_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file extension.",
            )

        try:
            FRONTEND_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

            image_id = uuid4()
            hero_filename = f"{image_id}.webp"
            thumb_filename = f"{image_id}_thumb.webp"

            hero_path = FRONTEND_IMAGES_DIR / hero_filename
            thumb_path = FRONTEND_IMAGES_DIR / thumb_filename

            save_recipe_images(
                image_file.file,
                hero_path,
                thumb_path,
            )

            recipe.image_hero_filename = hero_filename
            recipe.image_thumb_filename = thumb_filename

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process image: {e}",
            )

    created_recipe = await create_recipe(
        conn,
        recipe,
    )

    return RecipeRead(
        **created_recipe.model_dump(),
    )


@router.post("/", response_model=RecipeRead)
async def add_recipe(conn: GetConnection, recipe: RecipeCreate):
    created_recipe = await create_recipe(conn, recipe)
    return RecipeRead(
        **created_recipe.model_dump(), average_rating=0.0, total_ratings=0
    )


@router.get("/ids", response_model=list[str])
async def list_recipe_ids(conn: GetConnection):
    return await get_recipe_ids(conn)


@router.get("/{recipe_id}", response_model=RecipeRead)
async def get_recipe(conn: GetConnection, recipe_id: UUID):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            "SELECT * FROM recipes_with_ratings WHERE id = %s",
            (recipe_id,),
        )
        recipe = await cur.fetchone()

        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")

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

        full_components = []

        for comp in components:
            comp_id = comp["id"]

            await cur.execute(
                """
                SELECT *
                FROM ingredients
                WHERE component_id = %s
                """,
                (comp_id,),
            )
            ingredients = await cur.fetchall()

            await cur.execute(
                """
                SELECT *
                FROM steps
                WHERE component_id = %s
                ORDER BY step_order
                """,
                (comp_id,),
            )
            steps = await cur.fetchall()

            full_components.append(
                {
                    **comp,
                    "ingredients": ingredients,
                    "steps": steps,
                }
            )

    return RecipeRead(
        **recipe,
        components=full_components,
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


@router.patch("/{recipe_id}", response_model=RecipeRead)
async def update_recipe(
    conn: GetConnection,
    recipe_id: UUID,
    recipe: RecipeUpdate,
):
    updates = recipe.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided")

    components_data = updates.pop("components", None)

    JSON_FIELDS = {"equipment", "notes", "storage"}
    fields = []
    values = []

    for key, value in updates.items():
        if value is None:
            continue

        if key in JSON_FIELDS:
            fields.append(f"{key} = %s::jsonb")
            values.append(json.dumps(value if isinstance(value, list) else [value]))
        elif isinstance(value, str):
            fields.append(f"{key} = %s")
            values.append(value.strip())
        else:
            fields.append(f"{key} = %s")
            values.append(value)

    if fields:
        values.append(recipe_id)
        query = f"""
            UPDATE recipes
            SET {", ".join(fields)}
            WHERE id = %s
            RETURNING id
        """
        async with conn.cursor() as cur:
            await cur.execute(query, values)
            if not await cur.fetchone():
                raise HTTPException(status_code=404, detail="Recipe not found")

    if components_data is not None:
        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM recipe_components WHERE recipe_id = %s", (recipe_id,)
            )

            for comp_idx, comp in enumerate(components_data, start=1):
                comp_id = uuid4()
                await cur.execute(
                    """
                    INSERT INTO recipe_components (id, recipe_id, name, component_order)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        comp_id,
                        recipe_id,
                        comp.get("name", "Main"),
                        comp.get("component_order", comp_idx),
                    ),
                )

                for ing in comp.get("ingredients", []):
                    ing_id = uuid4()
                    await cur.execute(
                        """
                        INSERT INTO ingredients (id, component_id, raw,  name, amount, amount_value, unit)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            ing_id,
                            comp_id,
                            ing.get("raw"),
                            ing.get("name"),
                            ing.get("amount"),
                            ing.get("amount_value"),
                            ing.get("unit"),
                        ),
                    )

                for step_idx, step in enumerate(comp.get("steps", []), start=1):
                    step_id = uuid4()
                    await cur.execute(
                        """
                        INSERT INTO steps (id, component_id, step_order, description, timer_seconds)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            step_id,
                            comp_id,
                            step.get("step_order", step_idx),
                            step.get("description", ""),
                            step.get("timer_seconds"),
                        ),
                    )

    return await get_recipe(conn, recipe_id)


@router.put("/{recipe_id}/image", response_model=RecipeRead)
async def update_recipe_image(
    conn: GetConnection,
    recipe_id: UUID,
    image: UploadFile = File(...),
):
    FRONTEND_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    async with conn.cursor() as cur:
        await cur.execute(
            """
            SELECT image_hero_filename, image_thumb_filename
            FROM recipes
            WHERE id = %s
            """,
            (recipe_id,),
        )
        row = await cur.fetchone()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Recipe not found",
        )

    old_hero_filename = row[0]
    old_thumbnail_filename = row[1]

    image_id = uuid4()

    hero_filename = f"{image_id}-hero.webp"
    thumbnail_filename = f"{image_id}-thumb.webp"

    hero_path = FRONTEND_IMAGES_DIR / hero_filename
    thumbnail_path = FRONTEND_IMAGES_DIR / thumbnail_filename

    try:
        save_recipe_images(
            image.file,
            hero_path,
            thumbnail_path,
        )
    except (ValueError, OSError):
        # Clean up anything that may have been written
        hero_path.unlink(missing_ok=True)
        thumbnail_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail="Invalid image file",
        )

    async with conn.cursor() as cur:
        await cur.execute(
            """
            UPDATE recipes
            SET
                image_hero_filename = %s,
                image_thumb_filename = %s
            WHERE id = %s
            """,
            (
                hero_filename,
                thumbnail_filename,
                recipe_id,
            ),
        )

    if old_hero_filename:
        (FRONTEND_IMAGES_DIR / old_hero_filename).unlink(missing_ok=True)

    if old_thumbnail_filename:
        (FRONTEND_IMAGES_DIR / old_thumbnail_filename).unlink(missing_ok=True)

    return await get_recipe(conn, recipe_id)
