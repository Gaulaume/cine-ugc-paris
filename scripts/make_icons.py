"""Icônes de l'appli à partir du logo (ticket de cinéma, style impression riso).

Source : scripts/logo-source.png (carré, ticket centré sur fond papier).
Régénérer : pip install pillow && python scripts/make_icons.py docs/icons
"""
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

SOURCE = Path(__file__).with_name("logo-source.png")
BG = (252, 248, 237)  # couleur du papier


def grain(img: Image.Image, amount: int = 5, seed: int = 1) -> Image.Image:
    """Léger grain de papier, pour que le fond agrandi ne soit pas trop lisse."""
    rnd, px = random.Random(seed), img.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if rnd.random() < .35:
                d = rnd.randint(-amount, amount)
                px[x, y] = tuple(max(0, min(255, c + d)) for c in px[x, y])
    return img


def icon(src: Image.Image, size: int, fill: float) -> Image.Image:
    """Logo centré occupant `fill` du carré, bords fondus dans le fond papier."""
    canvas = Image.new("RGB", (size, size), BG)
    s = int(size * fill)
    logo = src.resize((s, s), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2))
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).rectangle((s // 20, s // 20, s - s // 20, s - s // 20), fill=255)
    canvas.paste(logo, ((size - s) // 2, (size - s) // 2), mask.filter(ImageFilter.GaussianBlur(s // 40)))
    return grain(canvas)


def main(out: str) -> None:
    src = Image.open(SOURCE).convert("RGB")
    # « maskable » : Android peut rogner jusqu'à un cercle, on laisse plus de marge.
    for name, size, fill in [("icon-512", 512, .92), ("icon-192", 192, .92),
                             ("apple-touch-icon", 180, .92), ("maskable-512", 512, .74)]:
        icon(src, size, fill).save(Path(out) / f"{name}.png")


if __name__ == "__main__":
    main(sys.argv[1])
