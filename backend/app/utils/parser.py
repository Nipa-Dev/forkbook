import re
from fractions import Fraction
from typing import Any

import yaml

from app.schemas.recipe import Ingredient, RecipeComponent, RecipeCreate, Step

# Matches Component headers (### Component Name)
COMPONENT_RE = re.compile(r"^###\s+(?!Notes|Storage)(.+)$", re.MULTILINE)

# Matches Section headers inside components (#### Ingredients)
SECTION_RE = re.compile(r"^####\s+(.+)$", re.MULTILINE)

# Matches Global sections (## Notes / ## Storage)
GLOBAL_SECTION_RE = re.compile(r"^##\s+(Notes|Storage)$", re.MULTILINE | re.IGNORECASE)
# Matches quantity and the rest of the line
QUANTITY_RE = re.compile(r"^\s*([\d\s\/\.\-]+)\s+(.*)$")


def parse_quantity(qty: str) -> float | None:
    """Parse numeric quantity including fractions and mixed numbers."""
    qty = qty.strip()
    try:
        if " " in qty:
            parts = qty.split()
            return sum(float(Fraction(p)) for p in parts)
        return float(Fraction(qty))
    except Exception:
        try:
            return float(qty)
        except Exception:
            return None


def split_unit_and_name(text: str) -> tuple[str | None, str]:
    """Split unit and ingredient name using simple heuristic."""
    parts = text.strip().split()
    if not parts:
        return None, ""

    first = parts[0].lower()
    # units are usually short
    if len(parts) > 1 and len(first) <= 5:
        return first, " ".join(parts[1:])

    return None, text.strip()


def parse_ingredient_line(line: str) -> Ingredient:
    """Parse a single ingredient line into structured Ingredient."""
    line = line.strip().lstrip("-").strip()
    match = QUANTITY_RE.match(line)

    if match:
        qty_raw = match.group(1).strip()
        rest = match.group(2)
        amount_value = parse_quantity(qty_raw)
        unit, name = split_unit_and_name(rest)

        return Ingredient(
            name=name,
            amount=qty_raw,
            amount_value=amount_value,
            unit=unit,
        )

    return Ingredient(name=line)


def parse_ingredients(text: str) -> list[Ingredient]:
    """Parse Ingredients section text."""
    if not text:
        return []
    result: list[Ingredient] = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("-"):
            continue
        result.append(parse_ingredient_line(line))
    return result


def parse_steps(text: str) -> list[Step]:
    """Parse Directions section into ordered steps."""
    if not text:
        return []
    result: list[Step] = []
    order = 1
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Remove leading numbers
        line = re.sub(r"^\d+\.\s*", "", line)
        result.append(Step(step_order=order, description=line))
        order += 1
    return result


def parse_list_section(text: str | None) -> list[str]:
    """Parse simple bullet list sections (notes, storage, etc.)."""
    if not text:
        return []
    result: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("-"):
            result.append(line.lstrip("-").strip())
    return result


def parse_time_to_minutes(value: Any) -> int | None:
    """Convert time field into minutes (supports '18h', '30m', int)."""
    if value is None:
        return None
    if isinstance(value, int):
        return value
    text = str(value).strip().lower()
    if text.endswith("h"):
        try:
            return int(float(text[:-1]) * 60)
        except (ValueError, TypeError):
            return None
    if text.endswith("m"):
        try:
            return int(float(text[:-1]))
        except (ValueError, TypeError):
            return None
    try:
        return int(text)
    except (ValueError, TypeError):
        return None


def split_frontmatter(md: str) -> tuple[dict[str, Any], str]:
    """Split YAML frontmatter from markdown body."""
    if not md.startswith("---"):
        return {}, md
    parts = md.split("---", 2)
    if len(parts) < 3:
        return {}, md
    frontmatter = yaml.safe_load(parts[1]) or {}
    body = parts[2]
    return frontmatter, body


def split_inner_sections(text: str) -> dict[str, str]:
    """Splits a component body into sub-sections (ingredients/directions)."""
    sections = {}
    matches = list(SECTION_RE.finditer(text))
    for i, match in enumerate(matches):
        title = match.group(1).strip().lower()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections[title] = text[start:end].strip()
    return sections


def parse_recipe(md: str) -> RecipeCreate:
    """Parse full markdown recipe into RecipeCreate model with Components."""
    frontmatter, body = split_frontmatter(md)

    # Global Sections
    global_data: dict[str, str] = {}
    global_matches = list(GLOBAL_SECTION_RE.finditer(body))
    for i, match in enumerate(global_matches):
        title = match.group(1).strip().lower()
        start = match.end()
        end = (
            global_matches[i + 1].start() if i + 1 < len(global_matches) else len(body)
        )
        global_data[title] = body[start:end].strip()

    # Components
    components: list[RecipeComponent] = []
    comp_matches = list(COMPONENT_RE.finditer(body))

    if not comp_matches:
        # Fallback for simple recipes without components
        inner = split_inner_sections(body)
        if inner.get("ingredients") or inner.get("directions"):
            components.append(
                RecipeComponent(
                    name="Main",
                    component_order=1,
                    ingredients=parse_ingredients(inner.get("ingredients", "")),
                    steps=parse_steps(inner.get("directions", "")),
                )
            )
    else:
        # Multi-component recipe
        for i, match in enumerate(comp_matches):
            name = match.group(1).strip()
            start = match.end()

            # End is the next component OR the start of global sections
            end = (
                comp_matches[i + 1].start() if i + 1 < len(comp_matches) else len(body)
            )
            for gm in global_matches:
                if start < gm.start() < end:
                    end = gm.start()

            comp_body = body[start:end].strip()
            inner = split_inner_sections(comp_body)

            components.append(
                RecipeComponent(
                    name=name,
                    component_order=i + 1,
                    ingredients=parse_ingredients(inner.get("ingredients", "")),
                    steps=parse_steps(inner.get("directions", "")),
                )
            )

    return RecipeCreate(
        title=frontmatter.get("title", "Untitled Recipe"),
        description=frontmatter.get("description"),
        components=components,
        tags=frontmatter.get("tags", []),
        time_minutes=parse_time_to_minutes(frontmatter.get("time_minutes")),
        difficulty=frontmatter.get("difficulty"),
        image_url=frontmatter.get("image_url"),
        equipment=frontmatter.get("equipment", []),
        notes=parse_list_section(global_data.get("notes")),
        storage=parse_list_section(global_data.get("storage")),
    )
