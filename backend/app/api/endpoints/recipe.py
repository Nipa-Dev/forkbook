from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status
from psycopg.rows import dict_row

from app.schemas.recipe import PaginatedRecipes, RecipeCreate, RecipeRead, RecipeUpdate
from app.services.recipes import (
    create_recipe,
    fetch_recipe,
    get_recipe_ids,
    insert_recipe_components,
)
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
    offset = (page - 1) * page_size

    async with conn.cursor(row_factory=dict_row) as cur:
        conditions = []
        params = []

        if tag:
            conditions.append("tags && %s::text[]")
            params.append(tag)

        if search:
            conditions.append("title ILIKE %s")
            params.append(f"%{search}%")

        where_clause = f" WHERE {' AND '.join(conditions)}" if conditions else ""

        # Total count
        count_query = f"SELECT COUNT(*) AS total FROM recipes{where_clause}"
        await cur.execute(count_query, params)
        row = await cur.fetchone()
        total = row["total"] if row else 0

        id_query = f"""
            SELECT id
            FROM recipes_with_ratings
            {where_clause}
            ORDER BY title
            LIMIT %s OFFSET %s
        """
        await cur.execute(id_query, [*params, page_size, offset])
        rows = await cur.fetchall()

        result: list[RecipeRead] = []
        for row in rows:
            recipe = await fetch_recipe(cur, row["id"])
            if recipe:
                result.append(recipe)

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

    return await create_recipe(conn, recipe)


@router.post("/", response_model=RecipeRead, status_code=status.HTTP_201_CREATED)
async def add_recipe(conn: GetConnection, recipe: RecipeCreate):
    return await create_recipe(conn, recipe)


@router.get("/ids", response_model=list[str])
async def list_recipe_ids(conn: GetConnection):
    return await get_recipe_ids(conn)


@router.get("/{recipe_id}", response_model=RecipeRead)
async def get_recipe(conn: GetConnection, recipe_id: UUID):
    async with conn.cursor(row_factory=dict_row) as cur:
        recipe = await fetch_recipe(cur, recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")

    return recipe


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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided",
        )

    components = updates.pop("components", None)

    if updates:
        fields = [f"{key} = %s" for key in updates.keys()]
        values = list(updates.values())

    async with conn.transaction():
        async with conn.cursor(row_factory=dict_row) as cur:
            if updates:
                values.append(recipe_id)
                query = f"""
                    UPDATE recipes
                    SET {", ".join(fields)}
                    WHERE id = %s
                    RETURNING id
                """
                await cur.execute(query, values)
                if not await cur.fetchone():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Recipe not found",
                    )

            if components is not None:
                await cur.execute(
                    "DELETE FROM recipe_components WHERE recipe_id = %s",
                    (recipe_id,),
                )
                await insert_recipe_components(cur, recipe_id, components)

            updated_recipe = await fetch_recipe(cur, recipe_id)
            if not updated_recipe:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Recipe not found",
                )

            return updated_recipe


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
