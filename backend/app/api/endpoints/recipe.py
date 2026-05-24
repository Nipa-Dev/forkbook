from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from psycopg.rows import dict_row
from uuid import UUID
from app.core.dependencies import GetConnection
from app.utils.parser import parse_recipe
from app.schemas.recipe import RecipeCreate, RecipeRead
from app.services.recipes import create_recipe, get_recipe_ids

router = APIRouter()


@router.get("/", response_model=list[RecipeRead])
async def get_recipes(
    conn: GetConnection,
    tag: list[str] | None = Query(default=None),
    search: str | None = Query(default=None),
):
    result = []

    async with conn.cursor(row_factory=dict_row) as cur:
        query = "SELECT * FROM recipes"
        conditions = []
        params = []

        if tag:
            conditions.append("tags && %s::text[]")
            params.append(tag)

        if search:
            conditions.append("(title ILIKE %s OR description ILIKE %s)")
            like = f"%{search}%"
            params.extend([like, like])

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        await cur.execute(query, params)
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

    return result


@router.post("/import", response_model=RecipeRead)
async def import_recipe(conn: GetConnection, file: UploadFile = File(...)):
    md = (await file.read()).decode("utf-8")
    recipe = parse_recipe(md)
    return await create_recipe(conn, recipe)


@router.post("/", response_model=RecipeRead)
async def add_recipe(conn: GetConnection, recipe: RecipeCreate):
    return await create_recipe(conn, recipe)


@router.get("/ids", response_model=list[str])
async def list_recipe_ids(conn: GetConnection):
    return await get_recipe_ids(conn)


@router.get("/{recipe_id}", response_model=RecipeRead)
async def get_recipe(conn: GetConnection, recipe_id: UUID):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            "SELECT * FROM recipes WHERE id = %s",
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
