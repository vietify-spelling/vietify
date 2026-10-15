"""Small images for the GUI: drawn flags and emoji rendered from a color font.

Emoji are shown as images because Tk text widgets cannot reliably render color
emoji. If no color emoji font is found, ``emoji_image`` returns None and the
GUI simply shows the label without the emoji.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageTk

EMOJI_FONTS = (
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
    "/usr/share/fonts/noto/NotoColorEmoji.ttf",
    "/usr/share/fonts/google-noto-emoji/NotoColorEmoji.ttf",
    r"C:\Windows\Fonts\seguiemj.ttf",
    "/System/Library/Fonts/Apple Color Emoji.ttc",
)

_font_cache: dict[str, ImageFont.FreeTypeFont | None] = {}
_image_cache: dict[tuple, ImageTk.PhotoImage | None] = {}


def _emoji_font() -> ImageFont.FreeTypeFont | None:
    if "font" not in _font_cache:
        _font_cache["font"] = None
        for path in EMOJI_FONTS:
            if not Path(path).exists():
                continue
            for size in (109, 160, 96):  # bitmap color fonts accept fixed sizes
                try:
                    _font_cache["font"] = ImageFont.truetype(path, size)
                    return _font_cache["font"]
                except OSError:
                    continue
    return _font_cache["font"]


def emoji_image(char: str, size: int) -> ImageTk.PhotoImage | None:
    """Render one emoji as a square image of the given pixel size."""
    key = ("emoji", char, size)
    if key in _image_cache:
        return _image_cache[key]

    image = None
    font = _emoji_font()
    if font is not None:
        try:
            canvas = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
            ImageDraw.Draw(canvas).text((20, 20), char, font=font, embedded_color=True)
            box = canvas.getbbox()
            if box:
                glyph = canvas.crop(box)
                side = max(glyph.size)
                square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
                square.paste(glyph, ((side - glyph.width) // 2, (side - glyph.height) // 2))
                image = ImageTk.PhotoImage(square.resize((size, size), Image.LANCZOS))
        except Exception:
            image = None
    _image_cache[key] = image
    return image


def _star(draw: ImageDraw.ImageDraw, cx: float, cy: float, radius: float, fill) -> None:
    points = []
    for i in range(10):
        r = radius if i % 2 == 0 else radius * 0.382
        angle = math.radians(-90 + 36 * i)
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(points, fill=fill)


def flag_image(code: str, width: int = 36, height: int = 24) -> ImageTk.PhotoImage:
    """Draw the flag for "vi" (Vietnam) or "en" (United Kingdom), antialiased."""
    key = ("flag", code, width, height)
    if key in _image_cache:
        return _image_cache[key]

    k = 8
    w, h = width * k, height * k
    img = Image.new("RGBA", (w, h))
    draw = ImageDraw.Draw(img)
    if code == "vi":
        draw.rectangle((0, 0, w, h), fill="#da251d")
        _star(draw, w / 2, h / 2 + h * 0.03, h * 0.32, "#ffff00")
    else:
        blue, white, red = "#012169", "#ffffff", "#c8102e"
        draw.rectangle((0, 0, w, h), fill=blue)
        for a, b in (((0, 0), (w, h)), ((0, h), (w, 0))):
            draw.line([a, b], fill=white, width=int(h * 0.22))
            draw.line([a, b], fill=red, width=int(h * 0.08))
        draw.rectangle((w * 0.40, 0, w * 0.60, h), fill=white)
        draw.rectangle((0, h * 0.34, w, h * 0.66), fill=white)
        draw.rectangle((w * 0.45, 0, w * 0.55, h), fill=red)
        draw.rectangle((0, h * 0.42, w, h * 0.58), fill=red)
    photo = ImageTk.PhotoImage(img.resize((width, height), Image.LANCZOS))
    _image_cache[key] = photo
    return photo
