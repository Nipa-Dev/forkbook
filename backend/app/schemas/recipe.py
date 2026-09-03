from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.utils.config import TAG_PATTERN, settings


def _normalize_tags(v):
    if v is None:
        return None
    if not isinstance(v, list):
        raise ValueError("tags must be a list")
    return [str(tag).lower().strip() for tag in v]


def _validate_tags(v):
    if v is None:
        return None
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


class Ingredient(BaseModel):
    raw: str = Field(max_length=255)
    name: str | None = Field(default=None, min_length=2, max_length=60)
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
    name: str = Field(min_length=2, max_length=60)
    component_order: int

    ingredients: list[Ingredient] = Field(default_factory=list)
    steps: list[Step] = Field(default_factory=list)


class RecipeBase(BaseModel):
    title: str = Field(min_length=3, max_length=60)
    description: str | None = None

    components: list[RecipeComponent] = Field(default_factory=list)

    tags: list[str] = Field(default_factory=list)
    cook_time_minutes: int | None = None
    prep_time_minutes: int | None = None
    servings: int | None = Field(default=None, gt=0)
    difficulty: str | None = None

    image_hero_filename: str | None = None
    image_thumb_filename: str | None = None

    equipment: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    storage: list[str] = Field(default_factory=list)

    @field_validator("tags", mode="before")
    def normalize_tags(cls, v):
        return _normalize_tags(v) or []

    @field_validator("tags")
    def validate_tags(cls, v):
        return _validate_tags(v)


class RecipeCreate(RecipeBase):
    pass


class RecipeRead(RecipeBase):
    id: UUID
    average_rating: float = Field(default=0.0)
    total_ratings: int = Field(default=0)


class RecipeUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=60)
    description: str | None = None
    components: list[RecipeComponent] | None = None
    cook_time_minutes: int | None = Field(default=None, ge=0)
    prep_time_minutes: int | None = Field(default=None, ge=0)
    servings: int | None = Field(default=None, gt=0)
    difficulty: str | None = None
    tags: list[str] | None = None
    equipment: list[str] | None = None
    notes: list[str] | str | None = None
    storage: list[str] | str | None = None

    @field_validator("tags", mode="before")
    def normalize_tags(cls, v):
        return _normalize_tags(v)

    @field_validator("tags")
    def validate_tags(cls, v):
        return _validate_tags(v)


class PaginatedRecipes(BaseModel):
    items: list[RecipeRead]
    total: int
    page: int
    page_size: int
