"""Premium gallery and board renderers for Signet export proofs."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from palette_engine import hex_to_oklch
from taste_laws import mud_box_hex


GALLERY_TOKENS = {
    "ground": {
        "light": "#F4F2EE",
        "dark": "#121212",
        "dark_cool": "#121822",
        "light_label": "#6B6560",
        "dark_label": "#8A8F98",
    },
    "shadow": {
        "layers": [
            {"offset": (1, 2), "blur": 2, "alpha": 30},
            {"offset": (2, 4), "blur": 4, "alpha": 24},
            {"offset": (4, 8), "blur": 8, "alpha": 20},
            {"offset": (8, 16), "blur": 16, "alpha": 16},
        ],
    },
    "type": {
        "scale": [12, 14, 16, 20, 24, 32, 40, 48],
        "label_weight": 500,
        "tracking_pct": 4,
    },
    "grid": {
        "base": 8,
        "tile_gap": 24,
        "tile_radius": 20,
        "outer_margin": 48,
        "icon_pct": 0.66,
    },
    "hero": {
        "width": 1400,
        "height": 820,
        "layout": "dark-ramp-trio",
    },
}


def _hex(value: str) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16), 255)


def safe_gallery_ground(value: str, mode: str = "light") -> str:
    if mode == "light":
        return GALLERY_TOKENS["ground"]["light"]
    try:
        _, C, H = hex_to_oklch(value)
    except Exception:
        return GALLERY_TOKENS["ground"]["dark_cool"]
    if mud_box_hex(value) or 30 <= H <= 90 or C > 0.06:
        return GALLERY_TOKENS["ground"]["dark_cool"]
    return value


def _font(size: int) -> ImageFont.ImageFont:
    for path in [
        "/System/Library/Fonts/Inter.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
    ]:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def _as_items(icon_pngs: Iterable) -> list[tuple[str, Image.Image]]:
    items = []
    for index, item in enumerate(icon_pngs):
        label = f"icon {index + 1}"
        value = item
        if isinstance(item, tuple):
            label, value = str(item[0]), item[1]
        if isinstance(value, Image.Image):
            image = value.convert("RGBA")
        else:
            image = Image.open(value).convert("RGBA")
        items.append((label, image))
    return items


def _draw_shadow(base: Image.Image, rect: tuple[int, int, int, int], radius: int, tint: str):
    tint_rgb = _hex(tint)[:3]
    for layer in GALLERY_TOKENS["shadow"]["layers"]:
        shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
        alpha = Image.new("L", base.size, 0)
        d = ImageDraw.Draw(alpha)
        dx, dy = layer["offset"]
        shifted = (rect[0] + dx, rect[1] + dy, rect[2] + dx, rect[3] + dy)
        d.rounded_rectangle(shifted, radius=radius, fill=layer["alpha"])
        alpha = alpha.filter(ImageFilter.GaussianBlur(layer["blur"]))
        color = Image.new("RGBA", base.size, (*tint_rgb, 0))
        color.putalpha(alpha)
        base.alpha_composite(color)


def _paste_card(sheet: Image.Image, icon: Image.Image, rect: tuple[int, int, int, int],
                radius: int, card_fill: str, shadow_tint: str):
    _draw_shadow(sheet, rect, radius, shadow_tint)
    draw = ImageDraw.Draw(sheet)
    draw.rounded_rectangle(rect, radius=radius, fill=card_fill)
    side = rect[2] - rect[0]
    target = round(side * GALLERY_TOKENS["grid"]["icon_pct"])
    icon = icon.resize((target, target), Image.LANCZOS)
    x = rect[0] + (side - target) // 2
    y = rect[1] + (side - target) // 2
    sheet.alpha_composite(icon, (x, y))


def render_contact_sheet(icon_pngs, out_path, cols: int = 5, tokens=GALLERY_TOKENS, ground: str = "light"):
    items = _as_items(icon_pngs)
    cols = max(1, min(6, int(cols)))
    gap = tokens["grid"]["tile_gap"]
    margin = tokens["grid"]["outer_margin"]
    radius = tokens["grid"]["tile_radius"]
    tile = 192
    label_h = 34
    rows = (len(items) + cols - 1) // cols
    bg_hex = safe_gallery_ground(tokens["ground"]["light"] if ground == "light" else tokens["ground"]["dark"], ground)
    card_hex = "#FFFFFF" if ground == "light" else "#1C1C1E"
    label_hex = tokens["ground"]["light_label"] if ground == "light" else tokens["ground"]["dark_label"]
    width = margin * 2 + cols * tile + (cols - 1) * gap
    height = margin * 2 + rows * (tile + label_h) + max(0, rows - 1) * gap
    sheet = Image.new("RGBA", (width, height), _hex(bg_hex))
    draw = ImageDraw.Draw(sheet)
    font = _font(14)
    for index, (label, icon) in enumerate(items):
        row, col = divmod(index, cols)
        x = margin + col * (tile + gap)
        y = margin + row * (tile + label_h + gap)
        rect = (x, y, x + tile, y + tile)
        _paste_card(sheet, icon, rect, radius, card_hex, bg_hex)
        draw.text((x + tile // 2, y + tile + 22), label, anchor="mm", fill=label_hex, font=font)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(out, "PNG", optimize=True)
    return out


def render_export_ladder(icon_pngs_by_platform: dict[str, object], out_path, tokens=GALLERY_TOKENS, ground: str = "dark"):
    order = ["master", "ios", "macos", "android", "harmonyos", "tvos", "watchos", "web", "windows"]
    items = [(label, icon_pngs_by_platform[label]) for label in order if label in icon_pngs_by_platform]
    return render_contact_sheet(items, out_path, cols=min(6, max(1, len(items))), tokens=tokens, ground=ground)


def render_hero(hero_icons, out_path, tokens=GALLERY_TOKENS, layout: str = "dark-ramp-trio"):
    items = _as_items(hero_icons)[:3]
    width = tokens["hero"]["width"]
    height = tokens["hero"]["height"]
    top = _hex("#313131")
    bottom = _hex("#141414")
    sheet = Image.new("RGBA", (width, height), top)
    px = sheet.load()
    for y in range(height):
        t = y / max(1, height - 1)
        row = tuple(round(top[i] * (1 - t) + bottom[i] * t) for i in range(4))
        for x in range(width):
            px[x, y] = row
    draw = ImageDraw.Draw(sheet)
    title_font = _font(48)
    label_font = _font(16)
    draw.text((72, 86), "Signet Platform Foundry", fill="#F4F2EE", font=title_font)
    draw.text((74, 145), "one master, premium tiles, every platform", fill="#8A8F98", font=label_font)
    tile = 300
    gap = 40
    start_x = 72
    y = 280
    for index, (label, icon) in enumerate(items):
        x = start_x + index * (tile + gap)
        rect = (x, y, x + tile, y + tile)
        _paste_card(sheet, icon, rect, 24, "#1C1C1E", "#0A0E1A")
        draw.text((x + tile // 2, y + tile + 32), label, anchor="mm", fill="#8A8F98", font=label_font)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(out, "PNG", optimize=True)
    return out
