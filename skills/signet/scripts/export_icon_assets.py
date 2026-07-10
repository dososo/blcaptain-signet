#!/usr/bin/env python3
"""
Signet — export_icon_assets.py
Turn one high-resolution master image into a full cross-platform icon asset bundle.

Clean-room original. No third-party product code or assets are used or reproduced.

What it does
------------
Given a single square master PNG (ideally 1024x1024, transparent OR opaque), it emits:
  - PNG size ladder (favicon + web + generic app)
  - favicon.ico (multi-resolution)
  - WebP copies
  - Apple iOS AppIcon.appiconset  (FLAT / legacy path, with Contents.json, opaque)
  - macOS .iconset  (ready for `iconutil -c icns`)
  - Android mipmap densities + adaptive-icon foreground/background + XML
  - PWA icons + web app manifest.json + maskable icons
  - social preview (1200x630)
  - a contact-sheet preview.png for READMEs
  - everything zipped

Design decisions (see references/output-spec.md for the why):
  * Image models output raster formats (PNG/JPEG/WebP), not native SVG. Even when a
    model can output larger or flexible raster sizes, Signet downscales the size ladder
    locally with high-quality LANCZOS so outputs are deterministic, auditable, and
    repeatable across runs.
  * Apple app icons MUST be opaque and full-bleed (no alpha, no self-rounded corners).
    If the master has alpha, we flatten it onto --ios-bg before writing the Apple set.
  * A native iOS 26 "Liquid Glass" .icon file requires per-layer artwork in Apple's
    Icon Composer and CANNOT be produced from a single flat raster. We deliberately do
    NOT fake it. We emit the flat AppIcon.appiconset, which iOS still renders (the
    system applies its own material). This limitation is inherent to raster generation
    and applies equally to any tool that outputs a single flat image.

Usage
-----
  python3 export_icon_assets.py MASTER.png --out ./dist \
      --name "FlowPilot" --platforms web,ios,macos,android,pwa,social \
      --ios-bg "#0E1116" --zip

Dependencies: Pillow >= 10.  (pip install Pillow)
"""

from __future__ import annotations
import argparse, functools, json, os, shutil, sys, zipfile
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageStat
except ImportError:
    sys.exit("Pillow is required:  pip install Pillow")

from palette_engine import hex_to_oklch, normalize_hex, oklch_to_hex
from taste_laws import GROUND_TIERS, mud_box, premium_ground
from gallery import render_contact_sheet as render_gallery_contact_sheet

# ---------------------------------------------------------------- size tables
WEB_PNG   = [16, 32, 48, 64, 96, 128, 180, 192, 256, 384, 512, 1024]
FAVICON   = [16, 32, 48]
PWA       = [72, 96, 128, 144, 152, 192, 384, 512]
SOCIAL    = (1200, 630)

# iOS flat AppIcon (idiom, size_pt, scale) -> pixel size = size_pt*scale
IOS_SET = [
    ("iphone", 20, 2), ("iphone", 20, 3),
    ("iphone", 29, 2), ("iphone", 29, 3),
    ("iphone", 40, 2), ("iphone", 40, 3),
    ("iphone", 60, 2), ("iphone", 60, 3),
    ("ipad",   20, 1), ("ipad",   20, 2),
    ("ipad",   29, 1), ("ipad",   29, 2),
    ("ipad",   40, 1), ("ipad",   40, 2),
    ("ipad",   76, 2), ("ipad",   83.5, 2),
    ("ios-marketing", 1024, 1),
]
MACOS_ICONSET = [16, 32, 64, 128, 256, 512]  # 1x + @2x pairs handled below
MACOS_BOXED = [824, 1024]
WATCHOS_SIZES = [32, 36, 40, 48, 55, 58, 87, 88, 108, 172, 196, 1024]
WINDOWS_TARGETS = [16, 20, 24, 30, 32, 36, 40, 48, 60, 64, 72, 80, 96, 256]

ANDROID_DENSITIES = {  # launcher icon px per density bucket
    "mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192,
}
ANDROID_ADAPTIVE = 108  # dp; foreground/background at each density = 108*scale
ANDROID_SAFE = 66 / 108

TILE_CORNER_RADIUS_PCT = 0.2237
TILE_CORNER_SMOOTHING = 0.60
TILE_SUPERELLIPSE_N = 5
TILE_MODES = ("saturated-sibling", "dark-anchor", "cream-tint", "jewel-ground", "near-black-ground")
MASTER_SIZE = 1024
MASTER_EDGE_PCT = 0.05
OPAQUE_PLATFORM_TARGETS = {"ios", "macos", "android", "watchos", "windows"}

# ---------------------------------------------------------------- helpers
def load_master(path: str) -> Image.Image:
    return Image.open(path).convert("RGBA")

def _luminance(rgb: tuple[float, float, float]) -> float:
    r, g, b = rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def _mean_luminance(im: Image.Image, box: tuple[int, int, int, int]) -> float:
    mean = ImageStat.Stat(im.crop(box).convert("RGB")).mean
    return _luminance((mean[0], mean[1], mean[2]))

def _ios_bg_was_explicit(argv: list[str]) -> bool:
    return any(arg == "--ios-bg" or arg.startswith("--ios-bg=") for arg in argv)

def _platforms_need_opaque_master_path(platforms: list[str]) -> bool:
    return bool(OPAQUE_PLATFORM_TARGETS.intersection(platforms))

def _edge_contract_errors(im: Image.Image) -> list[str]:
    w, h = im.size
    edge = max(1, round(min(w, h) * MASTER_EDGE_PCT))
    center = _mean_luminance(im, (w // 4, h // 4, (w * 3) // 4, (h * 3) // 4))
    sides = {
        "top": ((0, 0, w, edge), (0, edge, w, edge * 2), (0, h - edge, w, h)),
        "bottom": ((0, h - edge, w, h), (0, h - edge * 2, w, h - edge), (0, 0, w, edge)),
        "left": ((0, 0, edge, h), (edge, 0, edge * 2, h), (w - edge, 0, w, h)),
        "right": ((w - edge, 0, w, h), (w - edge * 2, 0, w - edge, h), (0, 0, edge, h)),
    }
    errors = []
    for side, (edge_box, inner_box, opposite_box) in sides.items():
        edge_lum = _mean_luminance(im, edge_box)
        inner_lum = _mean_luminance(im, inner_box)
        opposite_lum = _mean_luminance(im, opposite_box)
        reference_lum = max(inner_lum, opposite_lum, center)
        if edge_lum < 20 and reference_lum - edge_lum > 35:
            errors.append(f"{side} edge has black bar/border")
        if edge_lum > 235 and edge_lum - inner_lum > 35:
            errors.append(f"{side} edge has white frame/pre-rounded border")
    return errors

def validate_master_contract(master: Image.Image, platforms: list[str], flatten_explicit: bool, bg: str):
    errors = []
    if master.size != (MASTER_SIZE, MASTER_SIZE):
        errors.append(f"master must be {MASTER_SIZE}x{MASTER_SIZE}, got {master.size[0]}x{master.size[1]}")
    master_has_alpha = has_alpha(master)
    if master_has_alpha and _platforms_need_opaque_master_path(platforms) and not flatten_explicit:
        errors.append(
            "transparent master targets opaque app platforms without explicit --ios-bg or --brand-tile-platforms"
        )
    if master.size == (MASTER_SIZE, MASTER_SIZE) and not master_has_alpha:
        errors.extend(_edge_contract_errors(master.convert("RGB")))
    if errors:
        raise ValueError("MASTER_CONTRACT_FAILED: " + "; ".join(errors))

def resize(im: Image.Image, px: int) -> Image.Image:
    return im.resize((px, px), Image.LANCZOS)

def has_alpha(im: Image.Image) -> bool:
    if im.mode != "RGBA":
        return False
    return im.getchannel("A").getextrema()[0] < 255

def flatten(im: Image.Image, hexbg: str) -> Image.Image:
    bg = Image.new("RGBA", im.size, _hex(hexbg))
    return Image.alpha_composite(bg, im).convert("RGB")

def _hex(h: str):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)

def save_png(im, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, "PNG", optimize=True)

def _hex_rgb(h: str) -> tuple[int, int, int]:
    return _hex(h)[:3]

def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))

def _hue_delta(a: float, b: float) -> float:
    return abs((a - b + 180) % 360 - 180)

def _relative_luminance(hex_color: str) -> float:
    def channel(v: int) -> float:
        c = v / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = _hex_rgb(hex_color)
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)

def wcag_contrast(hex_a: str, hex_b: str) -> float:
    y1, y2 = sorted((_relative_luminance(hex_a), _relative_luminance(hex_b)), reverse=True)
    return (y1 + 0.05) / (y2 + 0.05)

def apca_lc(hex_text: str, hex_bg: str) -> float:
    """Small deterministic APCA-style contrast proxy for export guards."""
    y_text = _relative_luminance(hex_text)
    y_bg = _relative_luminance(hex_bg)
    if y_bg > y_text:
        return abs((y_bg ** 0.56 - y_text ** 0.57) * 160)
    return abs((y_bg ** 0.65 - y_text ** 0.62) * 160)

def extract_identity(master: Image.Image, white_threshold: int = 248) -> Image.Image:
    """Turn a white-ground master into a transparent identity layer."""
    src = master.convert("RGBA")
    out = Image.new("RGBA", src.size, (0, 0, 0, 0))
    src_px = src.load()
    out_px = out.load()
    for y in range(src.size[1]):
        for x in range(src.size[0]):
            r, g, b, a = src_px[x, y]
            if a == 0 or (r >= white_threshold and g >= white_threshold and b >= white_threshold):
                out_px[x, y] = (r, g, b, 0)
            else:
                out_px[x, y] = (r, g, b, a)
    return out

def subject_sample_hex(master: Image.Image) -> str:
    sample = resize(extract_identity(master), 96)
    total = [0, 0, 0]
    count = 0
    px = sample.load()
    for y in range(sample.size[1]):
        for x in range(sample.size[0]):
            r, g, b, a = px[x, y]
            if a > 16:
                total[0] += r
                total[1] += g
                total[2] += b
                count += 1
    if not count:
        return "#808080"
    return "#" + "".join(f"{round(v / count):02X}" for v in total)

def derive_tile_color(primary_hex: str, mode: str, subject_hex: str) -> tuple[str, dict]:
    primary_hex = normalize_hex(primary_hex)
    mode = mode if mode in TILE_MODES else "saturated-sibling"
    _, primary_c, primary_h = hex_to_oklch(primary_hex)
    subject_l, subject_c, _ = hex_to_oklch(subject_hex)

    if mode in {"jewel-ground", "near-black-ground"}:
        tier = "deep-jewel" if mode == "jewel-ground" else "near-black"
        tile_hex, ground_report = premium_ground(subject_hex, primary_h, tier)
        tile_l, tile_c, tile_h = hex_to_oklch(tile_hex)
    elif mode == "dark-anchor":
        lch = (0.14, min(primary_c * 0.12, 0.03), primary_h + 32)
        tile_l, tile_c, tile_h = lch
        ground_report = None
    elif mode == "cream-tint":
        lch = (0.965, _clamp(max(primary_c * 0.18, 0.012), 0.012, 0.035), 82)
        tile_l, tile_c, tile_h = lch
        ground_report = None
    else:
        lch = (0.78, _clamp(max(primary_c * 0.70, 0.10), 0.10, 0.16), primary_h + 32)
        tile_l, tile_c, tile_h = lch
        ground_report = None
    if _hue_delta(tile_h, primary_h) < 12 and tile_c > 0.06:
        tile_h += 28
    if subject_c > 0 and tile_c >= subject_c:
        tile_c = max(0.012, subject_c * 0.72)
    if mode not in {"jewel-ground", "near-black-ground"}:
        tile_hex = oklch_to_hex((tile_l, tile_c, tile_h))

    contrast = wcag_contrast(subject_hex, tile_hex)
    apca = apca_lc(subject_hex, tile_hex)
    if contrast < 3 or apca < 60:
        fallback_l = 0.14 if subject_l > 0.56 else 0.965
        fallback_c = min(tile_c, 0.03 if fallback_l < 0.5 else 0.025)
        tile_hex = oklch_to_hex((fallback_l, fallback_c, tile_h))
        contrast = wcag_contrast(subject_hex, tile_hex)
        apca = apca_lc(subject_hex, tile_hex)

    _, final_c, final_h = hex_to_oklch(tile_hex)
    report = {
        "mode": mode,
        "primary": primary_hex,
        "subject_sample": subject_hex,
        "tile_fill": tile_hex,
        "guards": {
            "tile_chroma_lt_subject": final_c < subject_c if subject_c > 0 else True,
            "tile_hue_outside_primary_12deg": _hue_delta(final_h, primary_h) >= 12 or final_c <= 0.06,
            "not_mud_box": not mud_box(*hex_to_oklch(tile_hex)),
            "wcag_contrast": round(contrast, 2),
            "wcag_contrast_pass": contrast >= 3,
            "apca_lc": round(apca, 1),
            "apca_lc_pass": apca >= 60,
        },
    }
    if ground_report:
        report["ground_report"] = ground_report
    return tile_hex, report

@functools.lru_cache(maxsize=24)
def superellipse_mask(size: int, n: int = TILE_SUPERELLIPSE_N) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    pix = mask.load()
    half = size / 2.0
    for y in range(size):
        ny = abs((y + 0.5 - half) / half)
        yn = ny ** n
        for x in range(size):
            nx = abs((x + 0.5 - half) / half)
            if (nx ** n) + yn <= 1:
                pix[x, y] = 255
    return mask

def circle_mask(size: int) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size - 1, size - 1], fill=255)
    return mask

def stage_identity(identity: Image.Image, size: int, live_pct: float = 0.78) -> Image.Image:
    alpha = identity.getchannel("A")
    bbox = alpha.getbbox()
    if not bbox:
        return Image.new("RGBA", (size, size), (0, 0, 0, 0))
    crop = identity.crop(bbox)
    scale = (size * live_pct) / max(crop.size)
    new_size = (max(1, round(crop.size[0] * scale)), max(1, round(crop.size[1] * scale)))
    glyph = crop.resize(new_size, Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    x = (size - glyph.size[0]) // 2
    y = (size - glyph.size[1]) // 2 - round(size * 0.012)
    canvas.paste(glyph, (x, y), glyph)
    return canvas

def stage_identity_rect(identity: Image.Image, size: tuple[int, int], live_pct: float = 0.72) -> Image.Image:
    alpha = identity.getchannel("A")
    bbox = alpha.getbbox()
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    if not bbox:
        return canvas
    crop = identity.crop(bbox)
    max_w = size[0] * live_pct
    max_h = size[1] * live_pct
    scale = min(max_w / crop.size[0], max_h / crop.size[1])
    glyph = crop.resize((max(1, round(crop.size[0] * scale)), max(1, round(crop.size[1] * scale))), Image.LANCZOS)
    x = (size[0] - glyph.size[0]) // 2
    y = (size[1] - glyph.size[1]) // 2
    canvas.paste(glyph, (x, y), glyph)
    return canvas

def solid_from_alpha(identity: Image.Image, fill: tuple[int, int, int, int], size: int | None = None,
                     live_pct: float = 0.78) -> Image.Image:
    layer = stage_identity(identity, size, live_pct) if size else identity.copy()
    solid = Image.new("RGBA", layer.size, fill)
    solid.putalpha(layer.getchannel("A"))
    return solid

def compose_square_tile(master: Image.Image, tile_hex: str, size: int = 1024,
                        live_pct: float = 0.78, shadow: bool = True) -> Image.Image:
    identity = extract_identity(master)
    staged = stage_identity(identity, size, live_pct)
    canvas = Image.new("RGBA", (size, size), _hex(tile_hex))
    if shadow:
        shadow_alpha = staged.getchannel("A").filter(ImageFilter.GaussianBlur(max(1, round(size * 0.016))))
        shadow_alpha = shadow_alpha.point(lambda p: round(p * 0.16))
        offset = Image.new("L", (size, size), 0)
        offset.paste(shadow_alpha, (0, round(size * 0.008)))
        shadow_layer = Image.new("RGBA", (size, size), (*_hex_rgb(tile_hex), 0))
        shadow_layer.putalpha(offset)
        canvas.alpha_composite(shadow_layer)
    canvas.alpha_composite(staged)
    return canvas

def compose_squircle_tile(master: Image.Image, tile_hex: str, size: int = 1024) -> Image.Image:
    square = compose_square_tile(master, tile_hex, size=size, live_pct=0.78, shadow=True)
    mask = superellipse_mask(size)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(square, (0, 0), mask)
    return out

def compose_circle_tile(master: Image.Image, tile_hex: str, size: int) -> Image.Image:
    square = compose_square_tile(master, tile_hex, size=size, live_pct=0.72, shadow=False)
    mask = circle_mask(size)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(square, (0, 0), mask)
    return out

def make_export_context(master: Image.Image, args) -> dict:
    subject_hex = subject_sample_hex(master)
    _, _, family_hue = hex_to_oklch(args.brand_primary)
    if args.ground_tier != "auto":
        tile_hex, ground_report = premium_ground(subject_hex, family_hue, args.ground_tier, args.seed)
        contrast = wcag_contrast(subject_hex, tile_hex)
        apca = apca_lc(subject_hex, tile_hex)
        _, final_c, final_h = hex_to_oklch(tile_hex)
        _, subject_c, _ = hex_to_oklch(subject_hex)
        tile_report = {
            "mode": f"ground-tier:{args.ground_tier}",
            "primary": args.brand_primary,
            "subject_sample": subject_hex,
            "tile_fill": tile_hex,
            "guards": {
                "tile_chroma_lt_subject": final_c < subject_c if subject_c > 0 else True,
                "tile_hue_outside_primary_12deg": _hue_delta(final_h, family_hue) >= 12 or final_c <= 0.06,
                "not_mud_box": not mud_box(*hex_to_oklch(tile_hex)),
                "wcag_contrast": round(contrast, 2),
                "wcag_contrast_pass": contrast >= 3,
                "apca_lc": round(apca, 1),
                "apca_lc_pass": apca >= 60,
            },
            "ground_report": ground_report,
        }
    else:
        tile_hex, tile_report = derive_tile_color(args.brand_primary, args.tile_mode, subject_hex)
    platform_bg = tile_hex if args.brand_tile_platforms else args.ios_bg
    identity = extract_identity(master)
    return {
        "identity": identity,
        "subject_sample": subject_hex,
        "tile_fill": tile_hex,
        "tile_report": tile_report,
        "platform_bg": platform_bg,
        "seed": args.seed or "",
        "brand_tile_platforms": bool(args.brand_tile_platforms),
    }

def build_tile_assets(master: Image.Image, out: Path, context: dict):
    d = out / "tile"
    for s in [1024, 512]:
        save_png(compose_squircle_tile(master, context["tile_fill"], s), d / f"tile-{s}.png")
    save_png(compose_square_tile(master, context["tile_fill"], 1024), d / "tile-square-1024.png")

    v = out / "variants"
    identity = context["identity"]
    save_png(solid_from_alpha(identity, (255, 255, 255, 255)), v / "pure-white-1024.png")
    save_png(solid_from_alpha(identity, (255, 255, 255, 255)), v / "alpha-mask-1024.png")
    save_png(solid_from_alpha(identity, (0, 0, 0, 255)), v / "monochrome-1024.png")
    print("  tile     -> squircle tile + identity variants")

# ---------------------------------------------------------------- platform builders
def build_web(master, out: Path, name: str, bg: str, context: dict):
    d = out / "web"
    for s in WEB_PNG:
        save_png(resize(master, s), d / f"icon-{s}.png")
    apple_touch = compose_square_tile(master, context["platform_bg"], 180, live_pct=0.76, shadow=False).convert("RGB")
    save_png(apple_touch, d / "apple-touch-icon.png")
    for s in [192, 512]:  # webp
        resize(master, s).save(d / f"icon-{s}.webp", "WEBP", quality=90, method=6)
    # multi-resolution favicon.ico. Save from the master so Pillow can encode
    # every requested size instead of being limited by a 16px source frame.
    master.save(d / "favicon.ico", format="ICO", sizes=[(s, s) for s in FAVICON])
    print(f"  web      -> {len(WEB_PNG)} png + webp + favicon.ico + apple-touch")

def build_pwa(master, out: Path, name: str, bg: str, context: dict):
    d = out / "pwa"
    icons = []
    for s in PWA:
        save_png(resize(master, s), d / f"pwa-{s}.png")
        icons.append({"src": f"pwa-{s}.png", "sizes": f"{s}x{s}", "type": "image/png", "purpose": "any"})
    # maskable: restage identity inside the central 80% safe circle on an opaque brand ground.
    for s in [192, 512]:
        canvas = compose_square_tile(master, context["platform_bg"], s, live_pct=0.72, shadow=False).convert("RGB")
        save_png(canvas, d / f"maskable-{s}.png")
        icons.append({"src": f"maskable-{s}.png", "sizes": f"{s}x{s}",
                      "type": "image/png", "purpose": "maskable"})
        mono = solid_from_alpha(context["identity"], (0, 0, 0, 255), s, live_pct=0.72)
        save_png(mono, d / f"monochrome-{s}.png")
        icons.append({"src": f"monochrome-{s}.png", "sizes": f"{s}x{s}",
                      "type": "image/png", "purpose": "monochrome"})
    manifest = {
        "name": name, "short_name": name[:12], "icons": icons,
        "start_url": "/", "display": "standalone",
        "background_color": context["platform_bg"], "theme_color": context["platform_bg"],
    }
    (d / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f"  pwa      -> {len(PWA)} png + maskable + monochrome + manifest.json")

def build_ios(master, out: Path, name: str, bg: str, context: dict):
    d = out / "ios" / "AppIcon.appiconset"
    if context["brand_tile_platforms"]:
        platform = compose_square_tile(master, context["platform_bg"], 1024, shadow=False)
        src = flatten(platform, context["platform_bg"]) if has_alpha(platform) else platform.convert("RGB")
    else:
        src = flatten(master, bg) if has_alpha(master) else master.convert("RGB")
    images = []
    seen = {}
    for idiom, pt, scale in IOS_SET:
        px = int(round(pt * scale))
        fn = f"AppIcon-{px}.png"
        if px not in seen:
            resize(src.convert("RGBA"), px).convert("RGB").save(
                (d / fn).parent.mkdir(parents=True, exist_ok=True) or (d / fn), "PNG")
            seen[px] = fn
        size_str = (f"{pt:g}x{pt:g}")
        images.append({"idiom": idiom, "size": size_str,
                       "scale": f"{scale}x", "filename": seen[px]})
    (d / "Contents.json").write_text(json.dumps(
        {"images": images, "info": {"version": 1, "author": "signet"}}, indent=2))
    print(f"  ios      -> flat AppIcon.appiconset (opaque, {len(seen)} px sizes)")
    print(f"             note: native iOS 26 .icon (Liquid Glass) needs Icon Composer layering")

def build_macos(master, out: Path, name: str, bg: str, context: dict):
    d = out / "macos" / f"{name}.iconset"
    src = (flatten(master, bg) if has_alpha(master) else master.convert("RGB")).convert("RGBA")
    for s in MACOS_ICONSET:
        save_png(resize(src, s), d / f"icon_{s}x{s}.png")
        if s * 2 <= 1024:
            save_png(resize(src, s * 2), d / f"icon_{s}x{s}@2x.png")
    boxed_dir = out / "macos" / "boxed"
    for s in MACOS_BOXED:
        boxed = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        shape = 824 if s == 1024 else s
        tile = compose_square_tile(master, context["platform_bg"], shape, live_pct=0.76, shadow=False)
        mask = superellipse_mask(shape)
        x = (s - shape) // 2
        y = (s - shape) // 2
        if s == 1024:
            shadow = Image.new("RGBA", (s, s), (0, 0, 0, 0))
            shadow_alpha = mask.filter(ImageFilter.GaussianBlur(28)).point(lambda p: round(p * 0.50))
            shadow.paste((0, 0, 0, 255), (x, y + 12), shadow_alpha)
            boxed.alpha_composite(shadow)
        boxed.paste(tile, (x, y), mask)
        save_png(boxed, boxed_dir / f"boxed-{s}.png")
    (out / "macos" / "BUILD_ICNS.txt").write_text(
        f"Run on macOS:\n  iconutil -c icns \"{name}.iconset\" -o \"{name}.icns\"\n")
    print(f"  macos    -> .iconset + boxed squircle assets")

def build_android(master, out: Path, name: str, bg: str, context: dict):
    base = out / "android"
    for bucket, px in ANDROID_DENSITIES.items():
        save_png(resize(master, px), base / f"mipmap-{bucket}" / "ic_launcher.png")
        # adaptive layers
        adp = int(round(ANDROID_ADAPTIVE * (px / 48)))
        fg = Image.new("RGBA", (adp, adp), (0, 0, 0, 0))
        inner = stage_identity(context["identity"], adp, ANDROID_SAFE)
        fg.alpha_composite(inner)
        save_png(fg, base / f"mipmap-{bucket}" / "ic_launcher_foreground.png")
        save_png(Image.new("RGBA", (adp, adp), _hex(context["platform_bg"])),
                 base / f"mipmap-{bucket}" / "ic_launcher_background.png")
        mono = solid_from_alpha(context["identity"], (255, 255, 255, 255), adp, ANDROID_SAFE)
        save_png(mono, base / f"mipmap-{bucket}" / "ic_launcher_monochrome.png")
    save_png(compose_square_tile(master, context["platform_bg"], 512, live_pct=0.76, shadow=False),
             base / "play-store" / "icon-512.png")
    xml = ('<?xml version="1.0" encoding="utf-8"?>\n'
           '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
           '    <background android:drawable="@mipmap/ic_launcher_background"/>\n'
           '    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>\n'
           '    <monochrome android:drawable="@mipmap/ic_launcher_monochrome"/>\n'
           '</adaptive-icon>\n')
    p = base / "mipmap-anydpi-v26" / "ic_launcher.xml"
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(xml)
    print(f"  android  -> densities + adaptive fg/bg/monochrome + Play512 + xml")

def build_watchos(master, out: Path, name: str, bg: str, context: dict):
    d = out / "watchos"
    for s in WATCHOS_SIZES:
        save_png(compose_circle_tile(master, context["platform_bg"], s), d / f"icon-{s}.png")
    print(f"  watchos  -> circular mask ladder ({len(WATCHOS_SIZES)} sizes)")

def build_harmonyos(master, out: Path, name: str, bg: str, context: dict):
    d = out / "harmonyos"
    foreground = stage_identity(context["identity"], 1024, 450 / 1024)
    background = Image.new("RGB", (1024, 1024), _hex_rgb(context["platform_bg"]))
    save_png(foreground, d / "foreground.png")
    save_png(background, d / "background.png")
    layered = {
        "layered-image": {
            "background": "$media:background",
            "foreground": "$media:foreground",
        }
    }
    d.mkdir(parents=True, exist_ok=True)
    (d / "layered_image.json").write_text(json.dumps(layered, indent=2, ensure_ascii=False))
    (d / "README_HARMONYOS.txt").write_text(
        "Place foreground.png, background.png, and layered_image.json in "
        "AppScope/resources/base/media/.\n"
        "Reference it from module.json5 as: \"icon\": \"$media:layered_image\".\n"
        "Reprocess with DevEco Studio >= 5.0.5.315. Do not pre-round or self-pad layers.\n",
        encoding="utf-8",
    )
    print("  harmonyos-> foreground(alpha)+background(opaque)+layered_image.json")

def _tvos_layer(master: Image.Image, context: dict, size: tuple[int, int], layer: str) -> Image.Image:
    if layer == "back":
        return Image.new("RGB", size, _hex_rgb(context["platform_bg"]))
    if layer == "highlight":
        identity = stage_identity_rect(context["identity"], size, 0.70)
        alpha = identity.getchannel("A").filter(ImageFilter.GaussianBlur(max(1, round(size[0] * 0.018))))
        alpha = alpha.point(lambda p: round(p * 0.18))
        highlight = Image.new("RGBA", size, (255, 255, 255, 0))
        highlight.putalpha(alpha)
        return highlight
    return stage_identity_rect(context["identity"], size, 0.72)

def build_tvos(master, out: Path, name: str, bg: str, context: dict):
    d = out / "tvos"
    for scale, size in [("1x", (400, 240)), ("2x", (800, 480))]:
        save_png(_tvos_layer(master, context, size, "back"), d / scale / "layer0_back.png")
        save_png(_tvos_layer(master, context, size, "graphic"), d / scale / "layer1_graphic.png")
        save_png(_tvos_layer(master, context, size, "highlight"), d / scale / "layer2_highlight.png")
    store = Image.new("RGBA", (1280, 768), _hex(context["platform_bg"]))
    store.alpha_composite(stage_identity_rect(context["identity"], (1280, 768), 0.72))
    save_png(store.convert("RGB"), d / "AppStore-1280x768.png")
    top_shelf = Image.new("RGBA", (1920, 720), _hex(context["platform_bg"]))
    top_shelf.alpha_composite(stage_identity_rect(context["identity"], (1920, 720), 0.52))
    save_png(top_shelf.convert("RGB"), d / "TopShelf-1920x720.png")
    top_shelf_wide = Image.new("RGBA", (2320, 720), _hex(context["platform_bg"]))
    top_shelf_wide.alpha_composite(stage_identity_rect(context["identity"], (2320, 720), 0.46))
    save_png(top_shelf_wide.convert("RGB"), d / "TopShelfWide-2320x720.png")
    (d / "README_TVOS.txt").write_text(
        "tvOS icons use layered parallax artwork. Import the 1x/2x PNG layers "
        "into Xcode or use layerutil to build .lsr/.car. Layer order: back, graphic, highlight.\n"
        "Top Shelf assets are TopShelf-1920x720.png and TopShelfWide-2320x720.png.\n",
        encoding="utf-8",
    )
    print("  tvos     -> 3 parallax layers @400x240/800x480 + store 1280x768 + top shelf")

def build_windows(master, out: Path, name: str, bg: str, context: dict):
    d = out / "windows"
    identity = context["identity"]
    ico_frames = []
    for s in WINDOWS_TARGETS:
        plated = resize(compose_square_tile(master, context["platform_bg"], 256, live_pct=0.76, shadow=False), s)
        unplated = stage_identity(identity, s, 0.82)
        save_png(plated, d / f"AppList.targetsize-{s}.png")
        save_png(unplated, d / f"AppList.targetsize-{s}_altform-unplated.png")
        save_png(unplated, d / f"AppList.targetsize-{s}_altform-lightunplated.png")
    for s in [16, 20, 24, 32, 40, 48, 64, 256]:
        ico_frames.append(stage_identity(identity, s, 0.82))
    d.mkdir(parents=True, exist_ok=True)
    ico_frames[-1].save(d / "app.ico", format="ICO", sizes=[(im.size[0], im.size[1]) for im in ico_frames])
    print(f"  windows  -> targetsize + unplated/lightunplated + app.ico")

def build_social(master, out: Path, name: str, bg: str, context: dict):
    d = out / "social"; d.mkdir(parents=True, exist_ok=True)
    card = Image.new("RGBA", SOCIAL, _hex(context["platform_bg"]))
    icon = resize(master, 320)
    card.paste(icon, ((SOCIAL[0] - 320) // 2, (SOCIAL[1] - 320) // 2), icon)
    card.convert("RGB").save(d / "social-preview.png", "PNG")
    print(f"  social   -> 1200x630 preview")

def build_contact_sheet(master, out: Path, name: str):
    sizes = [16, 32, 48, 64, 128, 256]
    icons = [(f"{s}px", master) for s in sizes]
    render_gallery_contact_sheet(icons, out / "preview.png", cols=6, ground="light")
    print("  preview  -> premium contact sheet (preview.png)")

def build_export_manifest(master_path: str, master: Image.Image, out: Path, name: str,
                          platforms: list[str], context: dict):
    manifest = {
        "name": name,
        "source_master": str(Path(master_path).resolve()),
        "master_size": list(master.size),
        "seed": context["seed"],
        "platforms": platforms,
        "tile": {
            "fill": context["tile_fill"],
            "mode": context["tile_report"]["mode"],
            "corner_radius_pct": TILE_CORNER_RADIUS_PCT,
            "corner_smoothing": TILE_CORNER_SMOOTHING,
            "superellipse_n": TILE_SUPERELLIPSE_N,
            "guards": context["tile_report"]["guards"],
            "subject_sample": context["subject_sample"],
        },
        "variants": {
            "pure_white": "variants/pure-white-1024.png",
            "alpha_mask": "variants/alpha-mask-1024.png",
            "monochrome": "variants/monochrome-1024.png",
        },
        "derived_platform_background": context["platform_bg"],
        "brand_tile_platforms": context["brand_tile_platforms"],
    }
    (out / "export-manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print("  manifest -> export-manifest.json")

def zip_dir(out: Path, name: str):
    zpath = out.parent / f"{name}-icons.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in out.rglob("*"):
            if f.is_file():
                z.write(f, f.relative_to(out.parent))
    print(f"  zip      -> {zpath.name}")

# ---------------------------------------------------------------- main
BUILDERS = {
    "web": build_web, "pwa": build_pwa, "ios": build_ios, "macos": build_macos,
    "android": build_android, "watchos": build_watchos, "windows": build_windows,
    "harmonyos": build_harmonyos, "tvos": build_tvos, "social": build_social,
}

def main():
    ap = argparse.ArgumentParser(description="Signet cross-platform icon exporter")
    ap.add_argument("master", help="master image (square PNG, 1024px recommended)")
    ap.add_argument("--out", default="./dist", help="output directory")
    ap.add_argument("--name", default="AppIcon", help="project/app name")
    ap.add_argument("--platforms", default="web,pwa,ios,macos,android,social",
                    help="comma list: web,pwa,ios,macos,android,watchos,windows,harmonyos,tvos,social")
    ap.add_argument("--ios-bg", default="#FFFFFF",
                    help="opaque background for Apple/Android icons if master is transparent")
    ap.add_argument("--brand-primary", default="#2F6BFF",
                    help="brand primary hex used to derive the squircle tile color")
    ap.add_argument("--tile-mode", default="saturated-sibling", choices=TILE_MODES,
                    help="tile recipe: saturated-sibling, dark-anchor, cream-tint, jewel-ground, near-black-ground")
    ap.add_argument("--ground-tier", default="auto", choices=GROUND_TIERS,
                    help="premium ground override: auto, near-black, deep-jewel, or pale-tint")
    ap.add_argument("--seed", default="", help="optional deterministic export seed recorded in manifest")
    ap.add_argument("--brand-tile-platforms", action="store_true",
                    help="use the derived tile color as the opaque platform background")
    ap.add_argument("--zip", action="store_true", help="also produce a .zip bundle")
    a = ap.parse_args()
    try:
        a.ios_bg = normalize_hex(a.ios_bg)
        a.brand_primary = normalize_hex(a.brand_primary)
    except ValueError as exc:
        sys.exit(str(exc))
    plats = [p.strip() for p in a.platforms.split(",") if p.strip()]
    unknown = [p for p in plats if p not in BUILDERS]
    if unknown:
        sys.exit(f"Unknown platform(s): {', '.join(unknown)}")
    master = load_master(a.master)
    try:
        validate_master_contract(
            master,
            plats,
            flatten_explicit=_ios_bg_was_explicit(sys.argv[1:]) or bool(a.brand_tile_platforms),
            bg=a.ios_bg,
        )
    except ValueError as exc:
        sys.exit(str(exc))
    out = Path(a.out) / a.name
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    context = make_export_context(master, a)

    print(f"Signet export  '{a.name}'  ({master.size[0]}px master, "
          f"{'transparent' if has_alpha(master) else 'opaque'})")
    build_tile_assets(master, out, context)
    for platform in plats:
        BUILDERS[platform](master, out, a.name, a.ios_bg, context)
    build_contact_sheet(master, out, a.name)
    build_export_manifest(a.master, master, out, a.name, plats, context)
    if a.zip: zip_dir(out, a.name)
    print(f"Done -> {out}")

if __name__ == "__main__":
    main()
