import re
from fractions import Fraction

from app.schemas.recipe import Ingredient, RecipeComponent, RecipeCreate, Step
from app.exceptions import InvalidRecipeError

VALID_UNITS = {
    "g", "kg", "ml", "l", "tbsp", "tsp", "cup", "cups", "oz", "lb", "lbs",
    "piece", "pieces", "can", "cans", "pinch", "pinches"
}

# TODO: Add conversion helpers

def parse_list_value(key: str, value: str) -> list[str]:
    if key == "tags" and "," in value:
        return [tag.strip() for tag in value.split(",") if tag.strip()]

    list_items = []
    for line in value.strip().split("\n"):
        clean_line = line.strip()
        if clean_line.startswith("-"):
            list_items.append(re.sub(r"^-\s*", "", clean_line))

    return list_items


def parse_quantity(qty: str) -> float | None:
    qty = qty.strip().replace(",", ".")
    try:
        if " " in qty:
            # Handle mixed numbers
            return sum(float(Fraction(p)) for p in qty.split())
        return float(Fraction(qty))
    except (ValueError, ZeroDivisionError):
        return None


def split_unit_and_name(text: str) -> tuple:
    parts = text.strip().split()
    if not parts:
        return None, ""

    first = parts[0].lower()
    if first in VALID_UNITS:
        return first, " ".join(parts[1:])
    # No valid unit found, assume the whole string is the ingredient name
    return None, text.strip()


def parse_ingredients(ingredients_raw: str) -> list[Ingredient]:
    ingredients_list = []

    for line in ingredients_raw.strip().split("\n"):
        line = re.sub(r"^-\s*", "", line)
        if not line:
            continue

        num_match = re.match(r"^([\d\s/\.,]+)", line)

        qty_str = ""
        remaining_text = line

        if num_match:
            qty_str = num_match.group(1).strip()
            remaining_text = line[num_match.end() :].strip()

        amount_value = parse_quantity(qty_str) if qty_str else None
        unit, name = split_unit_and_name(remaining_text)

        amount_str = qty_str or None

        ingredients_list.append(
            Ingredient(
                name=name, amount=amount_str, amount_value=amount_value, unit=unit
            )
        )

    return ingredients_list


def parse_metadata(match_obj: re.Match) -> dict:
    parsed_data = {}
    if not match_obj:
        return parsed_data

    metadata_text = match_obj.group(1)
    sections = re.split(r"\n(?=[A-Za-z]+:)", "\n" + metadata_text.strip())

    for section in sections:
        if not section.strip():
            continue
        key, _, value = section.partition(":")
        key = key.strip().lower()
        value = value.strip()

        if key in ["title", "description", "difficulty", "time"]:
            parsed_data[key] = value
        elif key in ["tags", "equipment", "notes", "storage"]:
            parsed_data[key] = parse_list_value(key, value)

    return parsed_data


def parse_directions(directions_raw: str) -> list[Step]:
    steps = []
    dir_lines = [
        line.strip() for line in directions_raw.strip().split("\n") if line.strip()
    ]

    for idx, line in enumerate(dir_lines, start=1):
        clean_description = re.sub(r"^\d+\.\s*", "", line)
        steps.append(
            Step(step_order=idx, description=clean_description, timer_seconds=None)
        )
    return steps


def parse_recipe(full_recipe_text: str) -> RecipeCreate:
    block_match = re.search(r"<recipe>(.*?)</recipe>", full_recipe_text, flags=re.DOTALL)

    if not block_match:
        raise InvalidRecipeError("Recipe is missing the required <recipe> block")

    recipe_dict = parse_metadata(block_match)
    if "time" in recipe_dict:
        # Pydantic schema expects 'time_minutes'
        recipe_dict["time_minutes"] = recipe_dict.pop("time")

    start, end = block_match.span()
    body_text = (full_recipe_text[:start] + full_recipe_text[end:]).strip()
    # Split remaining text into separate components
    component_chunks = [
        c.strip() for c in re.split(r"\n(?=##\s)", "\n" + body_text) if c.strip()
    ]

    components = []

    for index, chunk in enumerate(component_chunks, start=1):
        title_match = re.match(r"^##[ \t]*(.*?)[ \t]*\n", chunk)
        ing_match = re.search(r"<ingredients>(.*?)</ingredients>", chunk, flags=re.DOTALL)
        dir_match = re.search(r"<directions>(.*?)</directions>", chunk, flags=re.DOTALL)

        if not ing_match or not dir_match:
            raise InvalidRecipeError(f"Component #{index} is missing mandatory tags.")

        component_name = "Main"
        if title_match and title_match.group(1).strip():
            component_name = title_match.group(1).strip()

        components.append(
            RecipeComponent(
                name=component_name,
                component_order=index,
                ingredients=parse_ingredients(ing_match.group(1)),
                steps=parse_directions(dir_match.group(1)),
            )
        )
    recipe_dict["components"] = components
    return RecipeCreate(**recipe_dict)
