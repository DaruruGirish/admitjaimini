from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

from config import COLOR_LOGO_PATH, LOGO_PATH


def prepare_print_logo(source: Path | None = None, dest: Path | None = None) -> Path:
    source = Path(source or COLOR_LOGO_PATH)
    dest = Path(dest or LOGO_PATH)
    if dest.exists() and dest.stat().st_mtime >= source.stat().st_mtime:
        return dest
    image = Image.open(source).convert("RGBA")
    background = Image.new("RGBA", image.size, (255, 255, 255, 255))
    background.paste(image, mask=image.split()[-1])
    gray = ImageOps.grayscale(background.convert("RGB"))
    gray = ImageOps.autocontrast(gray, cutoff=2)
    gray = ImageEnhance.Contrast(gray).enhance(1.55)
    gray = ImageEnhance.Sharpness(gray).enhance(1.2)
    dest.parent.mkdir(parents=True, exist_ok=True)
    gray.save(dest, format="PNG")
    return dest
