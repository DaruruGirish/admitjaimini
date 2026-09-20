from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

from config import COLOR_LOGO_PATH, LOGO_PATH, SIGNATURE_PATH, SIGNATURE_SOURCE_PATH


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


def prepare_print_signature(source: Path | None = None, dest: Path | None = None) -> Path:
    source = Path(source or SIGNATURE_SOURCE_PATH)
    dest = Path(dest or SIGNATURE_PATH)
    if dest.exists() and source.exists() and dest.stat().st_mtime >= source.stat().st_mtime:
        return dest
    image = Image.open(source).convert("RGB")
    gray = ImageOps.grayscale(image)
    gray = ImageOps.autocontrast(gray, cutoff=1)
    black_ink = Image.new("L", gray.size, 0)
    alpha = gray.point(lambda value: 0 if value < 40 else 255)
    rgba = Image.merge("RGBA", (black_ink, black_ink, black_ink, alpha))
    dest.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(dest, format="PNG")
    return dest
