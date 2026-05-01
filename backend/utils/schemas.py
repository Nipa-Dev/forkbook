from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from utils.constants import TAG_PATTERN, settings


class Ingredient(BaseModel):
    name: str
    amount: str | None = None
    amount_value: float | None = None
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


class RecipeComponent(BaseModel):
    name: str
    component_order: int

    ingredients: list[Ingredient] = Field(default_factory=list)
    steps: list[Step] = Field(default_factory=list)


class RecipeBase(BaseModel):
    title: str
    description: str | None = None

    components: list[RecipeComponent] = Field(default_factory=list)

    tags: list[str] = Field(default_factory=list)
    time_minutes: int | None = None
    difficulty: str | None = None

    image_url: str | None = None
    equipment: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    storage: list[str] = Field(default_factory=list)

    @field_validator("tags", mode="before")
    def normalize_tags(cls, v):
        if not v:
            return []

        if not isinstance(v, list):
            raise ValueError("tags must be a list")

        return [str(tag).lower().strip() for tag in v]

    @field_validator("tags")
    def validate_tags(cls, v):
        if len(v) > settings.TAG_MAX_COUNT:
            raise ValueError(f"max {settings.TAG_MAX_COUNT} tags allowed")

        seen = set()
        result = []

        for tag in v:
            if len(tag) > settings.TAG_MAX_LENGTH:
                raise ValueError(f"tag too long: {tag}")

            if not TAG_PATTERN.match(tag):
                raise ValueError(f"invalid tag: {tag}")

            if tag not in seen:
                seen.add(tag)
                result.append(tag)

        return result


class RecipeCreate(RecipeBase):
    pass


class RecipeRead(RecipeBase):
    id: str


class RecipeRatingCreate(BaseModel):
    recipe_id: str
    rating: int

    @field_validator("rating")
    def validate_rating(cls, v):
        if not 1 <= v <= 5:
            raise ValueError("rating must be between 1 and 5")
        return v


class RecipeRatingRead(BaseModel):
    id: str
    recipe_id: str
    user_id: str
    rating: int
    created_at: datetime
    updated_at: datetime


class UserBase(BaseModel):
    id: str
    username: str
    email: str
