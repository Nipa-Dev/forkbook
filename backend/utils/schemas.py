from pydantic import BaseModel, field_validator
from typing import List


class Ingredient(BaseModel):
    name: str
    amount: float | None = None
    unit: str | None = None


class Step(BaseModel):
    step_order: int
    description: str
    timer_seconds: int | None = None

    @field_validator("step_order")
    def validate_order(cls, v):
        if v < 1:
            raise ValueError("step_order must be >= 1")
        return v


class RecipeBase(BaseModel):
    title: str
    description: str | None = None
    ingredients: List[Ingredient]
    steps: List[Step]
    tags: List[str] = []
    time_minutes: int | None = None
    difficulty: str | None = None

    @field_validator("tags", mode="before")
    def lowercase_unique_tags(cls, v):
        """Make all tags lowercase and remove duplicates"""
        # NOTE: order of the list may change.
        if not v:
            return []
        return list(set(tag.lower() for tag in v))


class RecipeCreate(RecipeBase):
    pass


class RecipeRead(RecipeBase):
    id: str


class UserBase(BaseModel):
    id: str
    name: str
    email: str
