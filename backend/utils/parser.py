import re
import yaml
from fractions import Fraction
from typing import Dict, List, Optional, Tuple

from utils.schemas import Ingredient, Step, RecipeCreate


SECTION_RE = re.compile(r"^###\s*(.+)$", re.MULTILINE)
QUANTITY_RE = re.compile(r"^\s*([\d\s\/\.\-]+)\s+(.*)$")


def parse_quantity(qty: str) -> Optional[float]:
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


def split_unit_and_name(text: str) -> Tuple[Optional[str], str]:
    """Split unit and ingredient name using simple heuristic."""
    parts = text.strip().split()

    if not parts:
        return None, ""

    first = parts[0].lower()

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

    return Ingredient(
        name=line,
        amount=None,
        amount_value=None,
        unit=None,
    )


def parse_ingredients(text: str) -> List[Ingredient]:
    """Parse Ingredients section."""
    if not text:
        return []

    result: List[Ingredient] = []

    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("-"):
            continue

        result.append(parse_ingredient_line(line))

    return result


def parse_steps(text: str) -> List[Step]:
    """Parse Directions section into ordered steps."""
    if not text:
        return []

    result: List[Step] = []
    order = 1

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        line = re.sub(r"^\d+\.\s*", "", line)

        result.append(
            Step(
                step_order=order,
                description=line,
                timer_seconds=None,
            )
        )

        order += 1

    return result


def parse_list_section(text: Optional[str]) -> List[str]:
    """Parse simple bullet list sections (notes, storage, etc.)."""
    if not text:
        return []

    result: List[str] = []

    for line in text.splitlines():
        line = line.strip()
        if line.startswith("-"):
            result.append(line.lstrip("-").strip())

    return result


def split_frontmatter(md: str) -> Tuple[Dict, str]:
    """Split YAML frontmatter from markdown body."""
    if not md.startswith("---"):
        return {}, md

    parts = md.split("---", 2)

    if len(parts) < 3:
        return {}, md

    frontmatter = yaml.safe_load(parts[1]) or {}
    body = parts[2]

    return frontmatter, body


def split_sections(body: str) -> Dict[str, str]:
    """Split markdown into named sections."""
    sections: Dict[str, str] = {}

    matches = list(SECTION_RE.finditer(body))

    for i, match in enumerate(matches):
        title = match.group(1).strip().lower()
        start = match.end()

        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)

        sections[title] = body[start:end].strip()

    return sections


def parse_time_to_minutes(value) -> Optional[int]:
    """Convert time field into minutes (supports '18h', '30m', int)."""
    if value is None:
        return None

    if isinstance(value, int):
        return value

    text = str(value).strip().lower()

    if text.endswith("h"):
        return int(float(text[:-1]) * 60)

    if text.endswith("m"):
        return int(float(text[:-1]))

    try:
        return int(text)
    except Exception:
        return None


def parse_recipe(md: str) -> RecipeCreate:
    """Parse full markdown recipe into RecipeCreate model."""
    frontmatter, body = split_frontmatter(md)
    sections = split_sections(body)

    return RecipeCreate(
        title=frontmatter.get("title"),
        description=frontmatter.get("description"),
        ingredients=parse_ingredients(sections.get("ingredients", "")),
        steps=parse_steps(sections.get("directions", "")),
        tags=frontmatter.get("tags", []),
        time_minutes=parse_time_to_minutes(frontmatter.get("time_minutes")),
        difficulty=frontmatter.get("difficulty"),
        equipment=frontmatter.get("equipment", []),
        notes=parse_list_section(sections.get("notes")),
        storage=parse_list_section(sections.get("storage")),
    )
