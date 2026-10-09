from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RecipeRatingCreate(BaseModel):
    rating: int = Field(ge=1, le=5)


class RecipeRatingRead(BaseModel):
    rating_id: UUID
    recipe_id: UUID
    user_id: UUID
    rating: int
    created_at: datetime
    updated_at: datetime
