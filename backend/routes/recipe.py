import json
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status

from backend.schemas.recipe import (
    PaginatedRecipes,
    RecipeComponent,
    RecipeCreate,
    RecipeRead,
    RecipeUpdate,
)
from backend.services.recipes import (
    create_recipe,
    fetch_recipe,
    get_recipe_ids,
    insert_recipe_components,
)
from backend.utils.config import settings
from backend.utils.db import GetConnection
from backend.utils.images import save_recipe_images
from backend.utils.parser import parse_recipe

router = APIRouter()

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[3]
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

    conditions = []
    params = []

    if search:
        conditions.append("LOWER(title) LIKE LOWER(?)")
        params.append(f"%{search}%")

    where_clause = f" WHERE {' AND '.join(conditions)}" if conditions else ""

    async with conn.execute(
        f"SELECT COUNT(*) AS total FROM recipes{where_clause}",
        params,
    ) as cur:
        row = await cur.fetchone()

    total = row["total"] if row else 0

    async with conn.execute(
        f"""
        SELECT id
        FROM recipes_with_ratings
        {where_clause}
        ORDER BY title
        LIMIT ? OFFSET ?
        """,
        [*params, page_size, offset],
    ) as cur:
        rows = await cur.fetchall()

    result: list[RecipeRead] = []

    for row in rows:
        recipe = await fetch_recipe(conn, row["id"])
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
    recipe = await fetch_recipe(conn, recipe_id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return recipe


@router.delete("/{recipe_id}")
async def delete_recipe(
    conn: GetConnection,
    recipe_id: str,
):
    async with conn.execute(
        "DELETE FROM recipes WHERE id = ?",
        (recipe_id,),
    ) as cur:
        if cur.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Recipe not found",
            )

    await conn.commit()

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

    try:
        if updates:
            fields = []
            values = []
            for key, val in updates.items():
                fields.append(f"{key} = ?")
                # Serialize list/dict fields to JSON strings
                if isinstance(val, (list, dict)):
                    values.append(json.dumps(val))
                else:
                    values.append(val)

            values.append(str(recipe_id))
            query = f"""
                UPDATE recipes
                SET {", ".join(fields)}
                WHERE id = ?
                RETURNING id
            """

            async with conn.execute(query, values) as cur:
                if not await cur.fetchone():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Recipe not found",
                    )

        if components is not None:
            await conn.execute(
                "DELETE FROM recipe_components WHERE recipe_id = ?",
                (str(recipe_id),),
            )
            component_models = [
                RecipeComponent(**comp) if isinstance(comp, dict) else comp
                for comp in components
            ]
            await insert_recipe_components(conn, recipe_id, component_models)

        updated_recipe = await fetch_recipe(conn, recipe_id)

        if not updated_recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found",
            )

        await conn.commit()
        return updated_recipe

    except Exception:
        await conn.rollback()
        raise


@router.put("/{recipe_id}/image", response_model=RecipeRead)
async def update_recipe_image(
    conn: GetConnection,
    recipe_id: UUID,
    image: UploadFile = File(...),
):
    FRONTEND_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    async with conn.execute(
        """
        SELECT image_hero_filename, image_thumb_filename
        FROM recipes
        WHERE id = ?
        """,
        (str(recipe_id),),
    ) as cur:
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

    await conn.execute(
        """
        UPDATE recipes
        SET
            image_hero_filename = ?,
            image_thumb_filename = ?
        WHERE id = ?
        """,
        (
            hero_filename,
            thumbnail_filename,
            str(recipe_id),
        ),
    )
    await conn.commit()

    if old_hero_filename:
        (FRONTEND_IMAGES_DIR / old_hero_filename).unlink(missing_ok=True)

    if old_thumbnail_filename:
        (FRONTEND_IMAGES_DIR / old_thumbnail_filename).unlink(missing_ok=True)

    return await get_recipe(conn, recipe_id)
