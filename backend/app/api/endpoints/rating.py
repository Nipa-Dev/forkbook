from fastapi import APIRouter
from app.schemas.recipe import RecipeRatingCreate

router = APIRouter()


@router.get("/{recipe_id}/rating")
async def get_rating(recipe_id: str): ...


@router.post("/{recipe_id}/rating")
async def add_or_update_rating(
    recipe_id: str,
    rating: RecipeRatingCreate,
): ...


@router.delete("/{recipe_id}/rating")
async def delete_rating(recipe_id: str): ...
