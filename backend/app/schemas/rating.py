from datetime import datetime
from pydantic import BaseModel, Field

from uuid import UUID



class RecipeRatingCreate(BaseModel):
    rating: int = Field(ge=1, le=5)


class RecipeRatingRead(BaseModel):
    rating_id: UUID
    recipe_id: UUID
    user_id: UUID
    rating: int
    created_at: datetime
    updated_at: datetime
