from pathlib import Path

from PIL import Image

THUMBNAIL_SIZE = (400, 300)
HERO_SIZE = (1200, 900)

WEBP_QUALITY = 80


def save_recipe_images(image_file, hero_path: Path, thumbnail_path: Path) -> None:
    image = Image.open(image_file)

    if image.mode != "RGB":
        image = image.convert("RGB")

    hero = image.copy()
    hero.thumbnail(HERO_SIZE, resample=Image.Resampling.LANCZOS)
    hero.save(hero_path, format="WEBP", quality=WEBP_QUALITY)

    thumbnail = image.copy()
    thumbnail.thumbnail(THUMBNAIL_SIZE, resample=Image.Resampling.LANCZOS)
    thumbnail.save(thumbnail_path, format="WEBP", quality=WEBP_QUALITY)
