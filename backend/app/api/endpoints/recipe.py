from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Query, UploadFile, status
from psycopg.rows import dict_row
from psycopg.types.json import Json
from pathlib import Path

from app.utils.dependencies import GetConnection
from app.schemas.recipe import RecipeCreate, RecipeRead, PaginatedRecipes, RecipeUpdate
from app.services.recipes import create_recipe, get_recipe_ids
from app.utils.parser import parse_recipe
from app.utils.config import settings
from app.utils.images import save_thumbnail


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

    image_url = None
    if image_file and image_file.filename:
        ext = Path(image_file.filename).suffix.lower()
        if ext not in settings.VALID_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file extension.",
            )
        try:
            FRONTEND_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

            filename = f"{uuid4()}.webp"
            full_save_path = FRONTEND_IMAGES_DIR / filename

            save_thumbnail(image_file.file, full_save_path)

            image_url = f"/images/{filename}"
            recipe.image_url = image_url
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process image: {str(e)}",
            )
    created_recipe = await create_recipe(conn, recipe)
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


def csv_to_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [v.strip() for v in value.split(",") if v.strip()]
    return []


@router.patch("/{recipe_id}")
async def update_recipe(
    conn: GetConnection,
    recipe_id: UUID,
    recipe: RecipeUpdate,
):
    JSON_FIELDS = {"equipment", "notes", "storage"}
    ARRAY_FIELDS = {"tags"}

    updates = recipe.model_dump(exclude_unset=True, exclude_none=True)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided")

    fields = []
    values = []

    for key, value in updates.items():
        if key in ARRAY_FIELDS:
            value = csv_to_list(value)

        elif key in JSON_FIELDS:
            value = csv_to_list(value)
            value = Json(value)

        elif isinstance(value, str):
            value = value.strip()

        fields.append(f"{key} = %s")
        values.append(value)

    values.append(recipe_id)

    query = f"""
        UPDATE recipes
        SET {", ".join(fields)}
        WHERE id = %s
        RETURNING *
    """

    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(query, values)
        updated = await cur.fetchone()

        if not updated:
            raise HTTPException(status_code=404, detail="Recipe not found")

    return await get_recipe(conn, recipe_id)
