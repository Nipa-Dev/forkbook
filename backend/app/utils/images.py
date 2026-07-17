from PIL import Image
from pathlib import Path

THUMBNAIL_SIZE = (400, 300)
WEBP_QUALITY = 80


def save_thumbnail(image_file, save_path: Path) -> None:
    image = Image.open(image_file)

    if image.mode != "RGB":
        image = image.convert("RGB")

    image.thumbnail(THUMBNAIL_SIZE, resample=Image.Resampling.LANCZOS)

    image.save(save_path, format="WEBP", quality=WEBP_QUALITY)
