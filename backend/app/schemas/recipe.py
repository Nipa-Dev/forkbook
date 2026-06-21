from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.core.config import TAG_PATTERN, settings


class Ingredient(BaseModel):
    name: str = Field(min_length=2, max_length=60)
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
    id: UUID


class PaginatedRecipes(BaseModel):
    items: list[RecipeRead]
    total: int
    page: int
    page_size: int
