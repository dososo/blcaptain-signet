#!/usr/bin/env python3
"""Deterministic Signet v3 palette engine.

The engine emits color only. It does not alter material, lighting, glass budget,
or character DNA. All public entry points are pure functions of brief + seed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import math
import re
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - build_prompt handles this in normal use
    yaml = None


ROLE_ORDER = ("primary", "secondary", "tertiary", "accent", "detail")
BRIGHT_ROLES = ("primary", "secondary", "tertiary", "accent")
ROLE_ALIASES = {
    "p": "primary",
    "primary": "primary",
    "主色": "primary",
    "s": "secondary",
    "secondary": "secondary",
    "辅色": "secondary",
    "t": "tertiary",
    "tertiary": "tertiary",
    "第三色": "tertiary",
    "a": "accent",
    "accent": "accent",
    "点缀": "accent",
    "d": "detail",
    "detail": "detail",
    "深色锚": "detail",
}
HEX_RE = re.compile(r"#[0-9a-fA-F]{6}")
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
HOUSE_PALETTES_PATH = DATA_DIR / "house_palettes.yaml"
HOUSE_PALETTES_VIVID_PATH = DATA_DIR / "house_palettes_vivid.yaml"

AREAS = {
    "primary": 62,
    "secondary": 23,
    "tertiary": 9,
    "accent": 4,
    "detail": 2,
}
ROLE_BANDS = {
    "primary": ((0.78, 0.92), (0.09, 0.16)),
    "secondary": ((0.72, 0.88), (0.08, 0.15)),
    "tertiary": ((0.70, 0.85), (0.10, 0.17)),
    "accent": ((0.88, 0.96), (0.05, 0.11)),
    "detail": ((0.30, 0.42), (0.05, 0.11)),
}
VIVID_ROLE_BANDS = {
    "primary": ((0.62, 0.82), (0.14, 0.30)),
    "secondary": ((0.60, 0.82), (0.11, 0.28)),
    "tertiary": ((0.55, 0.90), (0.13, 0.32)),
    "accent": ((0.90, 0.98), (0.02, 0.11)),
    "detail": ((0.25, 0.45), (0.05, 0.12)),
}

TEMPLATES = {
    "DRIFT": {
        "offsets": {"primary": 0, "secondary": 28, "tertiary": 55, "accent": 160},
        "tags": {"calm", "natural", "fresh"},
    },
    "MEADOW": {
        "offsets": {"primary": 0, "secondary": 30, "tertiary": 170, "accent": 195},
        "tags": {"fresh", "playful"},
    },
    "SORBET": {
        "offsets": {"primary": 0, "secondary": 90, "tertiary": 180, "accent": 270},
        "tags": {"candy", "bold", "toy", "playful"},
    },
    "TWILIGHT": {
        "offsets": {"primary": 0, "secondary": 85, "tertiary": 40, "accent": 230},
        "tags": {"dreamy", "elegant", "premium"},
    },
    "EMBER": {
        "offsets": {"primary": 0, "secondary": 25, "tertiary": 180, "accent": 205},
        "tags": {"warm", "energetic"},
    },
    "LAGOON": {
        "offsets": {"primary": 0, "secondary": 40, "tertiary": 75, "accent": -35},
        "tags": {"cool", "technical", "quiet"},
    },
    "CONFETTI": {
        "offsets": {"primary": 0, "secondary": 45, "tertiary": 90, "accent": 135},
        "tags": {"festive", "kids", "maximal", "playful"},
    },
    "PORCELAIN": {
        "offsets": {"primary": 0, "secondary": 0, "tertiary": 15, "accent": 180},
        "tags": {"minimal", "premium", "porcelain"},
    },
}

SET_PALETTE_CONTRACT = {
    "family_arc_deg": 60,
    "anchor_cluster_deg": 15,
    "member_spacing_min_deg": 12,
    "member_spacing_max_deg": 30,
    "accent_offset_deg": (150, 210),
    "accent_area_max_pct": 10,
    "cohesion_carrier": "material+D-family",
    "modes": ("signature-family", "spectrum-sweep"),
}


@dataclass(frozen=True)
class PaletteResult:
    roles: dict[str, str]
    areas: dict[str, int]
    tile: dict[str, str]
    report: dict[str, Any] = field(default_factory=dict)

    def prompt_palette(self, background: str = "tile") -> dict[str, str]:
        out = {role: self.roles[role] for role in ROLE_ORDER}
        out["background"] = background
        return out


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _wrap_hue(hue: float) -> float:
    return hue % 360.0


def _stable_int(seed: str, salt: str) -> int:
    digest = hashlib.sha256(f"{seed}:{salt}".encode("utf-8")).hexdigest()
    return int(digest[:12], 16)


def _choice(seq: list[Any], seed: str, salt: str) -> Any:
    return seq[_stable_int(seed, salt) % len(seq)]


def _rgb_to_linear(c: float) -> float:
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def _linear_to_rgb(c: float) -> float:
    if c <= 0.0031308:
        return 12.92 * c
    return 1.055 * (c ** (1 / 2.4)) - 0.055


def _hex_to_rgb01(value: str) -> tuple[float, float, float]:
    value = normalize_hex(value)
    return tuple(int(value[i : i + 2], 16) / 255.0 for i in (1, 3, 5))


def _rgb01_to_hex(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{round(_clamp(v, 0, 1) * 255):02X}" for v in rgb)


def rgb_to_oklab(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    r, g, b = (_rgb_to_linear(v) for v in rgb)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = math.copysign(abs(l) ** (1 / 3), l), math.copysign(abs(m) ** (1 / 3), m), math.copysign(abs(s) ** (1 / 3), s)
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def oklab_to_rgb(lab: tuple[float, float, float]) -> tuple[float, float, float]:
    L, a, b = lab
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    r = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return (_linear_to_rgb(r), _linear_to_rgb(g), _linear_to_rgb(bl))


def rgb_to_oklch(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    L, a, b = rgb_to_oklab(rgb)
    C = math.hypot(a, b)
    h = _wrap_hue(math.degrees(math.atan2(b, a)))
    return L, C, h


def hex_to_oklch(value: str) -> tuple[float, float, float]:
    return rgb_to_oklch(_hex_to_rgb01(value))


def oklch_to_rgb(lch: tuple[float, float, float]) -> tuple[float, float, float]:
    L, C, h = lch
    rad = math.radians(h)
    return oklab_to_rgb((L, C * math.cos(rad), C * math.sin(rad)))


def oklch_to_hex(lch: tuple[float, float, float]) -> str:
    L, C, h = lch
    c = C
    for _ in range(40):
        rgb = oklch_to_rgb((L, c, h))
        if all(-0.0001 <= v <= 1.0001 for v in rgb):
            return _rgb01_to_hex(rgb)
        c *= 0.94
    return _rgb01_to_hex(tuple(_clamp(v, 0, 1) for v in oklch_to_rgb((L, 0, h))))


def normalize_hex(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"not a hex color: {value!r}")
    match = HEX_RE.search(value.strip())
    if not match:
        raise ValueError(f"not a #RRGGBB hex color: {value!r}")
    return match.group(0).upper()


def _rgb_to_xyz(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    r, g, b = (_rgb_to_linear(v) for v in rgb)
    return (
        r * 0.4124564 + g * 0.3575761 + b * 0.1804375,
        r * 0.2126729 + g * 0.7151522 + b * 0.0721750,
        r * 0.0193339 + g * 0.1191920 + b * 0.9503041,
    )


def _xyz_to_lab(xyz: tuple[float, float, float]) -> tuple[float, float, float]:
    xr, yr, zr = xyz[0] / 0.95047, xyz[1] / 1.0, xyz[2] / 1.08883

    def f(t: float) -> float:
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    fx, fy, fz = f(xr), f(yr), f(zr)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def hex_to_lab(value: str) -> tuple[float, float, float]:
    return _xyz_to_lab(_rgb_to_xyz(_hex_to_rgb01(value)))


def delta_e00(hex1: str, hex2: str) -> float:
    L1, a1, b1 = hex_to_lab(hex1)
    L2, a2, b2 = hex_to_lab(hex2)
    avg_lp = (L1 + L2) / 2
    c1 = math.hypot(a1, b1)
    c2 = math.hypot(a2, b2)
    avg_c = (c1 + c2) / 2
    g = 0.5 * (1 - math.sqrt((avg_c**7) / (avg_c**7 + 25**7))) if avg_c else 0
    a1p, a2p = (1 + g) * a1, (1 + g) * a2
    c1p, c2p = math.hypot(a1p, b1), math.hypot(a2p, b2)

    def hp(a: float, b: float) -> float:
        if a == 0 and b == 0:
            return 0
        return _wrap_hue(math.degrees(math.atan2(b, a)))

    h1p, h2p = hp(a1p, b1), hp(a2p, b2)
    dlp = L2 - L1
    dcp = c2p - c1p
    if c1p * c2p == 0:
        dhp = 0
    else:
        diff = h2p - h1p
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360
        dhp = diff
    dhp_term = 2 * math.sqrt(c1p * c2p) * math.sin(math.radians(dhp / 2))
    avg_l = (L1 + L2) / 2
    avg_cp = (c1p + c2p) / 2
    if c1p * c2p == 0:
        avg_hp = h1p + h2p
    elif abs(h1p - h2p) > 180:
        avg_hp = (h1p + h2p + 360) / 2 if h1p + h2p < 360 else (h1p + h2p - 360) / 2
    else:
        avg_hp = (h1p + h2p) / 2
    t = (
        1
        - 0.17 * math.cos(math.radians(avg_hp - 30))
        + 0.24 * math.cos(math.radians(2 * avg_hp))
        + 0.32 * math.cos(math.radians(3 * avg_hp + 6))
        - 0.20 * math.cos(math.radians(4 * avg_hp - 63))
    )
    d_ro = 30 * math.exp(-(((avg_hp - 275) / 25) ** 2))
    rc = 2 * math.sqrt((avg_cp**7) / (avg_cp**7 + 25**7)) if avg_cp else 0
    sl = 1 + (0.015 * ((avg_l - 50) ** 2)) / math.sqrt(20 + ((avg_l - 50) ** 2))
    sc = 1 + 0.045 * avg_cp
    sh = 1 + 0.015 * avg_cp * t
    rt = -math.sin(math.radians(2 * d_ro)) * rc
    return math.sqrt(
        (dlp / sl) ** 2
        + (dcp / sc) ** 2
        + (dhp_term / sh) ** 2
        + rt * (dcp / sc) * (dhp_term / sh)
    )


def tone(value: str) -> float:
    return hex_to_oklch(value)[0] * 100


def _hue_span(hexes: list[str]) -> float:
    hues = [hex_to_oklch(h)[2] for h in hexes]
    if len(hues) < 2:
        return 0
    if max(hues) - min(hues) < 0.001:
        return 0
    hues = sorted(hues)
    gaps = [(hues[(i + 1) % len(hues)] - hues[i]) % 360 for i in range(len(hues))]
    return 360 - max(gaps)


def _in_zone(hue: float, lo: float, hi: float) -> bool:
    return lo <= hue <= hi


def _is_flag_role(value: str, zone: tuple[float, float]) -> bool:
    L, C, h = hex_to_oklch(value)
    return _in_zone(h, *zone) and L < 0.65 and C > 0.13


def evaluate(roles: dict[str, str], tile_fill: str, template_id: str = "") -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    is_house = bool(template_id and template_id not in TEMPLATES and template_id != "USER")
    is_vivid = str(template_id).upper().startswith("V")
    detail_tone = tone(roles["detail"])
    bright_deltas = {role: round(tone(roles[role]) - detail_tone, 1) for role in BRIGHT_ROLES}
    checks.append({
        "id": "F1",
        "pass": (
            all(v >= 30 for v in bright_deltas.values())
            if is_vivid
            else all(v >= 37.5 for v in bright_deltas.values()) and bright_deltas["primary"] >= 49
        ),
        "detail": f"bright-detail tone deltas {bright_deltas}",
    })

    tile_tone = tone(tile_fill)
    subject_tile_delta = max(abs(tone(roles[role]) - tile_tone) for role in ROLE_ORDER)
    checks.append({
        "id": "F2",
        "pass": subject_tile_delta >= 30,
        "detail": f"max subject role vs tile tone delta {subject_tile_delta:.1f}",
    })

    tile_white_delta = abs(100 - tile_tone)
    checks.append({
        "id": "F3",
        "pass": 8 <= tile_white_delta <= 82 if is_vivid else 2 <= tile_white_delta <= 12,
        "detail": f"tile-white tone delta {tile_white_delta:.1f}",
    })

    pair_failures = []
    for i, left in enumerate(BRIGHT_ROLES):
        for right in BRIGHT_ROLES[i + 1 :]:
            de = delta_e00(roles[left], roles[right])
            L1, _, h1 = hex_to_oklch(roles[left])
            L2, _, h2 = hex_to_oklch(roles[right])
            hue_delta = abs((h1 - h2 + 180) % 360 - 180)
            if de < 9 or (hue_delta < 20 and abs(L1 - L2) < 0.03):
                pair_failures.append(f"{left}/{right} dE={de:.1f} dh={hue_delta:.1f} dL={abs(L1-L2):.2f}")
    checks.append({"id": "F4", "pass": not pair_failures, "detail": "; ".join(pair_failures) or "bright pairs separated"})

    span = _hue_span([roles[r] for r in ("primary", "secondary", "tertiary")])
    checks.append({
        "id": "F5",
        "pass": template_id == "PORCELAIN" or (is_house and span >= 20) or span >= 55,
        "detail": f"bright hue span {span:.1f}",
    })

    chroma_failures = []
    for role in ROLE_ORDER:
        L, C, _ = hex_to_oklch(roles[role])
        bands = VIVID_ROLE_BANDS if is_vivid else ROLE_BANDS
        (lmin, lmax), (cmin, cmax) = bands[role]
        if template_id == "PORCELAIN" and role == "secondary":
            cmin = 0.0
        if is_house and not is_vivid and role in ("primary", "secondary"):
            cmin = min(cmin, 0.02)
        if not (lmin - 0.04 <= L <= lmax + 0.04) or not (cmin - 0.04 <= C <= cmax + 0.04):
            chroma_failures.append(f"{role} L={L:.2f} C={C:.2f}")
        max_c = 0.33 if is_vivid else 0.20
        if C > max_c or (role in ("primary", "secondary", "tertiary") and C < cmin - 0.04):
            chroma_failures.append(f"{role} hard C={C:.2f}")
    checks.append({"id": "F6", "pass": not chroma_failures, "detail": "; ".join(chroma_failures) or "roles inside chroma windows"})

    zones = {
        "red": (15, 40),
        "green": (130, 155),
        "blue": (240, 270),
    }
    hit_zones = set()
    for role in ("primary", "secondary", "tertiary"):
        for name, zone in zones.items():
            if _is_flag_role(roles[role], zone):
                hit_zones.add(name)
    checks.append({
        "id": "F7",
        "pass": len(hit_zones) < 3,
        "detail": f"flag zones hit {sorted(hit_zones)}",
    })

    mud = []
    for role in BRIGHT_ROLES:
        L, _, _ = hex_to_oklch(roles[role])
        if L < 0.55:
            mud.append(f"{role} L={L:.2f}")
    for role in ("primary", "secondary", "tertiary", "accent"):
        L, _, _ = hex_to_oklch(roles[role])
        if L < 0.50:
            mud.append(f"{role} illegal dark L={L:.2f}")
    checks.append({"id": "F8", "pass": not mud, "detail": "; ".join(mud) or "no muddy bright roles"})

    levels = sorted((hex_to_oklch(value)[0], role) for role, value in roles.items())
    checks.append({
        "id": "F9",
        "pass": levels[0][1] == "detail" and (levels[1][0] - levels[0][0]) >= 0.25,
        "detail": f"L order {[(role, round(level, 2)) for level, role in levels]}",
    })
    return checks


def _all_pass(checks: list[dict[str, Any]]) -> bool:
    return all(bool(check["pass"]) for check in checks)


def _tile_from_primary(primary_hex: str, mode: str = "pale-primary-tint") -> str:
    L, C, h = hex_to_oklch(primary_hex)
    if mode == "saturated-sibling":
        return oklch_to_hex((0.78, _clamp(max(C * 0.70, 0.10), 0.10, 0.16), h + 32))
    if mode == "dark-anchor":
        return oklch_to_hex((0.26, _clamp(max(C * 0.38, 0.05), 0.05, 0.10), h))
    return oklch_to_hex((0.96, min(0.035, max(0.018, C * 0.30)), h))


def _signature_offsets(n: int) -> list[float]:
    if n <= 1:
        return [0]
    span = min(SET_PALETTE_CONTRACT["family_arc_deg"], (n - 1) * SET_PALETTE_CONTRACT["member_spacing_max_deg"])
    step = span / (n - 1)
    if step < SET_PALETTE_CONTRACT["member_spacing_min_deg"]:
        step = SET_PALETTE_CONTRACT["member_spacing_min_deg"]
        span = step * (n - 1)
    start = -span / 2
    return [start + step * i for i in range(n)]


def _palette_from_primary_hue(primary_hue: float, template_id: str, accent_hue: float,
                              seed: str = "", index: int = 0) -> dict[str, str]:
    if template_id not in TEMPLATES:
        template_id = "EMBER"
    template = TEMPLATES[template_id]
    primary_L, primary_C = 0.70, 0.15
    roles = {
        "primary": oklch_to_hex((primary_L, primary_C, primary_hue)),
        "secondary": oklch_to_hex((0.68, 0.12, primary_hue + template["offsets"]["secondary"])),
        "tertiary": oklch_to_hex((0.74, 0.14, primary_hue + template["offsets"]["tertiary"])),
        "accent": oklch_to_hex((0.86, 0.10, accent_hue)),
        "detail": oklch_to_hex((0.31, 0.075, primary_hue - 12)),
    }
    return {role: roles[role] for role in ROLE_ORDER}


def build_set_palette(anchor_hue: float, n: int, template_id: str,
                      mode: str = "signature-family", seed: str = "") -> list[PaletteResult]:
    mode = mode if mode in SET_PALETTE_CONTRACT["modes"] else "signature-family"
    n = max(1, int(n))
    if mode == "spectrum-sweep":
        span = 240 if n >= 6 else 150
        step = span / max(1, n - 1)
        offsets = [(-span / 2) + step * i for i in range(n)]
    else:
        offsets = _signature_offsets(n)

    accent_choices = SET_PALETTE_CONTRACT["accent_offset_deg"]
    accent_hue = _wrap_hue(anchor_hue + accent_choices[_stable_int(str(seed), "set-accent") % len(accent_choices)])
    palettes: list[PaletteResult] = []
    for index, offset in enumerate(offsets):
        jitter = 0
        if seed and mode == "spectrum-sweep":
            jitter = ((_stable_int(str(seed), f"set-jitter:{index}") % 9) - 4) * 0.5
        primary_hue = _wrap_hue(anchor_hue + offset + jitter)
        roles = _palette_from_primary_hue(primary_hue, template_id, accent_hue, seed, index)
        tile_mode = "dark-anchor" if mode == "spectrum-sweep" else "pale-primary-tint"
        tile = {"fill": _tile_from_primary(roles["primary"], tile_mode), "shape": "squircle", "mode": tile_mode}
        checks = evaluate(roles, tile["fill"], template_id)
        palettes.append(PaletteResult(roles, {**AREAS, "accent": min(AREAS["accent"], SET_PALETTE_CONTRACT["accent_area_max_pct"])}, tile, {
            "mode": "set",
            "set_palette_mode": mode,
            "seed": seed,
            "template_id": template_id,
            "set_index": index,
            "set_count": n,
            "anchor_hue": round(anchor_hue % 360, 1),
            "primary_hue": round(primary_hue, 1),
            "accent_hue": round(accent_hue, 1),
            "floor_checks": checks,
            "warnings": [],
        }))
    return palettes


def evaluate_set(palettes: list[PaletteResult], mode: str = "signature-family") -> list[dict[str, Any]]:
    mode = mode if mode in SET_PALETTE_CONTRACT["modes"] else "signature-family"
    primary_hues = [hex_to_oklch(p.roles["primary"])[2] for p in palettes]
    accent_hues = [hex_to_oklch(p.roles["accent"])[2] for p in palettes]
    accent_areas = [int(p.areas.get("accent", 0)) for p in palettes]
    checks: list[dict[str, Any]] = []

    span = _hue_span([p.roles["primary"] for p in palettes])
    if mode == "spectrum-sweep":
        checks.append({"id": "F-SET-SPECTRUM", "pass": span >= 210, "detail": f"primary hue span {span:.1f}"})
        return checks

    checks.append({
        "id": "F-SET-1",
        "pass": span <= SET_PALETTE_CONTRACT["family_arc_deg"] + 1.0,
        "detail": f"primary hue span {span:.1f}",
    })

    accent_span = _hue_span([p.roles["accent"] for p in palettes])
    checks.append({
        "id": "F-SET-2",
        "pass": accent_span <= 6 and all(area <= SET_PALETTE_CONTRACT["accent_area_max_pct"] for area in accent_areas),
        "detail": f"accent span {accent_span:.1f}; areas {accent_areas}",
    })

    sorted_hues = sorted(primary_hues)
    gaps = [sorted_hues[i + 1] - sorted_hues[i] for i in range(len(sorted_hues) - 1)]
    if len(sorted_hues) <= 1:
        spacing_pass = True
    else:
        spacing_pass = all(
            SET_PALETTE_CONTRACT["member_spacing_min_deg"] - 1.0 <= gap <= SET_PALETTE_CONTRACT["member_spacing_max_deg"] + 1.0
            for gap in gaps
        )
    checks.append({
        "id": "F-SET-3",
        "pass": spacing_pass,
        "detail": f"member spacing {[round(g, 1) for g in gaps]}",
    })

    chromas = [hex_to_oklch(p.roles["primary"])[1] for p in palettes]
    checks.append({
        "id": "F-SET-4",
        "pass": (max(chromas) - min(chromas)) <= 0.08 if chromas else True,
        "detail": f"primary chroma range {min(chromas):.3f}-{max(chromas):.3f}" if chromas else "no palettes",
    })
    return checks


def _seed_from_brief(brief: dict[str, Any]) -> str:
    explicit = brief.get("seed")
    pal = brief.get("color_palette")
    if isinstance(pal, dict):
        explicit = pal.get("seed") or explicit
    if explicit:
        return str(explicit)
    key = f"{brief.get('icon_subject','')}|{brief.get('project_name','')}|{brief.get('date','2026-07-03')}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:8]


def _palette_family_from_brief(brief: dict[str, Any]) -> str:
    pal = brief.get("color_palette")
    family = None
    if isinstance(pal, dict):
        family = pal.get("palette_family") or pal.get("family")
    family = brief.get("palette_family") or family or "soft"
    family = str(family).strip().lower()
    if family not in {"soft", "vivid"}:
        family = "soft"
    return family


def _load_house_palettes(family: str = "soft") -> list[dict[str, Any]]:
    if yaml is None:
        raise RuntimeError("PyYAML is required to load house palettes")
    path = HOUSE_PALETTES_VIVID_PATH if family == "vivid" else HOUSE_PALETTES_PATH
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data.get("palettes", [])


def house_palette_names(family: str | None = None) -> list[str]:
    families = [family] if family in {"soft", "vivid"} else ["soft", "vivid"]
    return [p["name"] for fam in families for p in _load_house_palettes(fam)]


def _find_house_palette(name: str, family: str = "soft") -> dict[str, Any] | None:
    slug = str(name).strip().lower().replace("_", "-").replace(" ", "-")
    families = [family, "vivid" if family == "soft" else "soft"]
    seen = set()
    for fam in families:
        if fam in seen:
            continue
        seen.add(fam)
        for pal in _load_house_palettes(fam):
            candidates = {pal["id"].lower(), pal["name"].lower(), pal["name"].lower().replace(" ", "-")}
            if slug in candidates or str(name).strip().lower() in candidates:
                out = dict(pal)
                out["_family"] = fam
                return out
    return None


def _roles_from_house(name: str, family: str = "soft") -> tuple[dict[str, str], dict[str, int], str, dict[str, Any]]:
    pal = _find_house_palette(name, family)
    if not pal:
        raise ValueError(f"unknown house palette: {name}")
    roles = {role: normalize_hex(pal["roles"][role]["hex"]) for role in ROLE_ORDER}
    areas = {role: int(pal["roles"][role]["area_pct"]) for role in ROLE_ORDER}
    return roles, areas, pal["id"].upper().replace("-", "_"), pal


def _parse_role_mapping(value: Any) -> tuple[dict[str, str], bool]:
    if not value:
        return {}, False
    if isinstance(value, dict):
        source = value.get("roles") if isinstance(value.get("roles"), (dict, list, str)) else value
        if isinstance(source, dict):
            roles = {}
            for key, raw in source.items():
                role = ROLE_ALIASES.get(str(key).strip().lower()) or ROLE_ALIASES.get(str(key).strip())
                if role and isinstance(raw, str) and HEX_RE.search(raw):
                    roles[role] = normalize_hex(raw)
            return roles, bool(roles)
        value = source
    if isinstance(value, list):
        roles = {}
        for role, raw in zip(ROLE_ORDER, value):
            if isinstance(raw, str) and HEX_RE.search(raw):
                roles[role] = normalize_hex(raw)
        return roles, bool(roles)
    if isinstance(value, str):
        labeled = {}
        tokens = re.findall(r"(Primary|Secondary|Tertiary|Accent|Detail|主色|辅色|第三色|点缀|深色锚)\s*[:：]?\s*(#[0-9a-fA-F]{6})", value)
        for label, raw in tokens:
            role = ROLE_ALIASES[label.lower()] if label.lower() in ROLE_ALIASES else ROLE_ALIASES[label]
            labeled[role] = normalize_hex(raw)
        if labeled:
            return labeled, True
        hexes = HEX_RE.findall(value)
        if hexes:
            return {role: normalize_hex(raw) for role, raw in zip(ROLE_ORDER, hexes)}, True
    return {}, False


def _derive_missing_roles(roles: dict[str, str], warnings: list[str]) -> dict[str, str]:
    roles = dict(roles)
    if "primary" not in roles:
        first = next(iter(roles.values()), "#BDF4A7")
        roles["primary"] = first
        warnings.append("primary role derived from first supplied color")
    if "secondary" not in roles:
        L, C, h = hex_to_oklch(roles["primary"])
        roles["secondary"] = oklch_to_hex((_clamp(L - 0.08, 0.72, 0.88), _clamp(C * 0.85, 0.08, 0.15), h + 32))
        warnings.append("secondary role derived from primary")
    if "tertiary" not in roles:
        hp = hex_to_oklch(roles["primary"])[2]
        hs = hex_to_oklch(roles["secondary"])[2]
        mid = hp + (((hs - hp + 180) % 360 - 180) / 2)
        roles["tertiary"] = oklch_to_hex((0.76, 0.14, mid + 120))
        warnings.append("tertiary role derived from primary/secondary midpoint")
    if "accent" not in roles:
        highest = max((hex_to_oklch(v)[0], v) for v in roles.values())[1]
        L, C, h = hex_to_oklch(highest)
        roles["accent"] = oklch_to_hex((_clamp(L + 0.06, 0.88, 0.96), _clamp(C - 0.03, 0.05, 0.09), h))
        warnings.append("accent role derived from highest-lightness color")
    if "detail" not in roles:
        darkest = min((hex_to_oklch(v)[0], v) for v in roles.values())[1]
        _, C, h = hex_to_oklch(darkest)
        if not (10 <= h <= 65):
            h = _wrap_hue(h + _choice([30, 45, 60], darkest, "detail-warm-shift"))
        roles["detail"] = oklch_to_hex((0.35, _clamp(C, 0.06, 0.10), h))
        warnings.append("detail role derived as saturated dark anchor")
    return {role: roles[role] for role in ROLE_ORDER}


def _validate_user_roles(roles: dict[str, str], warnings: list[str]) -> None:
    for role, value in roles.items():
        if value in {"#000000", "#FFFFFF"}:
            warnings.append(f"{role} uses {value}; white/black are not preferred palette roles")


def _path_a(brief: dict[str, Any], seed: str) -> PaletteResult | None:
    pal = brief.get("color_palette")
    family = _palette_family_from_brief(brief)
    if not pal:
        return None
    house_name = None
    if isinstance(pal, dict):
        house_name = pal.get("house_palette") or pal.get("house") or pal.get("palette_name")
    if house_name:
        roles, areas, template_id, house = _roles_from_house(str(house_name), family)
        resolved_family = str(house.get("_family") or family)
        mode = str(house.get("ground_mode") or ("saturated-sibling" if resolved_family == "vivid" else "pale-primary-tint"))
        tile = {"fill": _tile_from_primary(roles["primary"], mode), "shape": "squircle", "mode": mode}
        checks = evaluate(roles, tile["fill"], template_id)
        return PaletteResult(roles, areas, tile, {
            "mode": "house",
            "palette_family": resolved_family,
            "seed": seed,
            "template_id": template_id,
            "rotation_deg": None,
            "jitter_vector": {},
            "floor_checks": checks,
            "repairs": [],
            "warnings": [],
        })
    parsed, found = _parse_role_mapping(pal)
    if not found:
        return None
    warnings: list[str] = []
    roles = _derive_missing_roles(parsed, warnings)
    _validate_user_roles(roles, warnings)
    tile = {"fill": _tile_from_primary(roles["primary"]), "shape": "squircle", "mode": "pale-primary-tint"}
    checks = evaluate(roles, tile["fill"], "USER")
    if not _all_pass(checks):
        failed = ", ".join(check["id"] for check in checks if not check["pass"])
        warnings.append(f"user palette kept with unresolved floor warnings: {failed}")
    return PaletteResult(roles, AREAS.copy(), tile, {
        "mode": "user",
        "palette_family": family,
        "seed": seed,
        "template_id": "USER",
        "rotation_deg": None,
        "jitter_vector": {},
        "floor_checks": checks,
        "repairs": [],
        "warnings": warnings,
    })


def _band_value(role: str, seed: str, salt: str, steps: int, index_shift: int = 0) -> tuple[float, float]:
    (lmin, lmax), (cmin, cmax) = ROLE_BANDS[role]
    li = (_stable_int(seed, f"{salt}:L:{role}") + index_shift) % steps
    ci = (_stable_int(seed, f"{salt}:C:{role}") + index_shift) % 3
    L = lmin + (lmax - lmin) * (li / max(1, steps - 1))
    C = cmin + (cmax - cmin) * (ci / 2)
    return L, C


def _generate_candidate(seed: str, mood: str = "", attempt: int = 0) -> tuple[dict[str, str], str, float, dict[str, Any]]:
    templates = list(TEMPLATES)
    if mood:
        filtered = [name for name, meta in TEMPLATES.items() if mood.lower() in meta["tags"]]
        if filtered:
            templates = filtered
    template_id = _choice(templates, seed, f"template:{attempt}")
    template = TEMPLATES[template_id]
    rotation = (_stable_int(seed, f"rotation:{attempt}") % 120) * 3
    roles: dict[str, str] = {}
    jitter: dict[str, Any] = {"attempt": attempt}
    for role in ("primary", "secondary", "tertiary", "accent"):
        steps = 5 if role in ("primary", "secondary") else 3
        L, C = _band_value(role, seed, f"{template_id}:{attempt}", steps, attempt)
        offset = template["offsets"][role]
        hue_jitter = (_stable_int(seed, f"hue-jitter:{attempt}:{role}") % 19) - 9
        h = _wrap_hue(rotation + offset + hue_jitter)
        if template_id == "PORCELAIN" and role == "secondary":
            C = min(C, 0.03)
        if 240 <= h <= 280 and role in ("primary", "secondary", "tertiary"):
            C = min(C, 0.12)
        roles[role] = oklch_to_hex((L, C, h))
        jitter[role] = {"L": round(L, 3), "C": round(C, 3), "h": round(h, 1)}
    detail_h = _choice([
        _wrap_hue(hex_to_oklch(roles["primary"])[2] - 15),
        _wrap_hue(hex_to_oklch(roles["primary"])[2] + 15),
        float(_choice([25, 35, 45, 55, 65], seed, f"detail-zone:{attempt}")),
    ], seed, f"detail-hue:{attempt}")
    detail_l = 0.34 + ((_stable_int(seed, f"detail-L:{attempt}") % 3) * 0.02)
    detail_c = 0.07 + ((_stable_int(seed, f"detail-C:{attempt}") % 3) * 0.015)
    roles["detail"] = oklch_to_hex((detail_l, min(detail_c, 0.10), detail_h))
    jitter["detail"] = {"L": round(detail_l, 3), "C": round(min(detail_c, 0.10), 3), "h": round(detail_h, 1)}
    return {role: roles[role] for role in ROLE_ORDER}, template_id, rotation, jitter


def _repair_roles(roles: dict[str, str], tile: dict[str, str], template_id: str) -> tuple[dict[str, str], dict[str, str], list[str], list[dict[str, Any]]]:
    roles = dict(roles)
    tile = dict(tile)
    repairs: list[str] = []
    checks: list[dict[str, Any]] = []
    for round_index in range(3):
        checks = evaluate(roles, tile["fill"], template_id)
        if _all_pass(checks):
            return roles, tile, repairs, checks
        failed = {check["id"] for check in checks if not check["pass"]}
        if failed & {"F1", "F9"}:
            _, C, h = hex_to_oklch(roles["detail"])
            roles["detail"] = oklch_to_hex((0.31, _clamp(C, 0.06, 0.10), h))
            repairs.append(f"round {round_index+1}: lowered Detail anchor")
        if "F4" in failed:
            role = "accent"
            L, C, h = hex_to_oklch(roles[role])
            roles[role] = oklch_to_hex((_clamp(L + 0.04, *ROLE_BANDS[role][0]), C, h + 9))
            repairs.append(f"round {round_index+1}: separated accent pair")
        if failed & {"F6", "F7", "F8"}:
            for role in ROLE_ORDER:
                L, C, h = hex_to_oklch(roles[role])
                (lmin, lmax), (cmin, cmax) = ROLE_BANDS[role]
                if template_id == "PORCELAIN" and role == "secondary":
                    cmin = 0.0
                roles[role] = oklch_to_hex((_clamp(L, lmin, lmax), _clamp(C, cmin, min(cmax, 0.18)), h + (11 if role == "tertiary" else 0)))
            repairs.append(f"round {round_index+1}: re-toned and de-chromed roles")
        if failed & {"F2", "F3"}:
            tile["fill"] = _tile_from_primary(roles["primary"])
            repairs.append(f"round {round_index+1}: reset quiet tile fill")
    checks = evaluate(roles, tile["fill"], template_id)
    return roles, tile, repairs, checks


def _path_b(brief: dict[str, Any], seed: str) -> PaletteResult:
    family = _palette_family_from_brief(brief)
    if family == "vivid":
        vivid = _load_house_palettes("vivid")
        house = vivid[_stable_int(seed, "vivid-house") % len(vivid)]
        roles, areas, template_id, house = _roles_from_house(house["id"], "vivid")
        set_count = int(brief.get("set_count") or brief.get("batch_count") or 1)
        set_index = int(brief.get("set_index") or brief.get("batch_index") or 0)
        rotation = 0
        if set_count > 1:
            base_step = 360 / max(1, set_count)
            jitter = (_stable_int(seed, f"vivid-jitter:{set_index}") % 17) - 8
            rotation = round((base_step * set_index) + jitter, 2)
            roles = {
                role: oklch_to_hex((lambda lch: (lch[0], lch[1], lch[2] + rotation))(hex_to_oklch(value)))
                for role, value in roles.items()
            }
        mode = str(house.get("ground_mode") or "saturated-sibling")
        tile = {"fill": _tile_from_primary(roles["primary"], mode), "shape": "squircle", "mode": mode}
        checks = evaluate(roles, tile["fill"], template_id)
        return PaletteResult(roles, areas, tile, {
            "mode": "auto",
            "palette_family": "vivid",
            "seed": seed,
            "template_id": template_id,
            "rotation_deg": rotation,
            "jitter_vector": {"set_count": set_count, "set_index": set_index},
            "floor_checks": checks,
            "repairs": [],
            "warnings": [],
        })
    pal = brief.get("color_palette")
    mood = ""
    if isinstance(pal, dict):
        mood = str(pal.get("mood") or "")
    mood = str(brief.get("mood") or mood or "")
    for attempt in range(20):
        attempt_seed = seed if attempt == 0 else f"{seed}+{attempt}"
        roles, template_id, rotation, jitter = _generate_candidate(attempt_seed, mood, attempt)
        tile = {"fill": _tile_from_primary(roles["primary"]), "shape": "squircle", "mode": "pale-primary-tint"}
        roles, tile, repairs, checks = _repair_roles(roles, tile, template_id)
        if _all_pass(checks):
            return PaletteResult(roles, AREAS.copy(), tile, {
                "mode": "auto",
                "seed": seed,
                "template_id": template_id,
                "rotation_deg": rotation,
                "jitter_vector": jitter,
                "floor_checks": checks,
                "repairs": repairs,
                "warnings": [],
            })
    return PaletteResult(roles, AREAS.copy(), tile, {
        "mode": "auto",
        "seed": seed,
        "template_id": template_id,
        "rotation_deg": rotation,
        "jitter_vector": jitter,
        "floor_checks": checks,
        "repairs": repairs,
        "warnings": ["palette emitted after repair budget; human review required"],
    })


def generate(brief: dict[str, Any]) -> PaletteResult:
    seed = _seed_from_brief(brief)
    user = _path_a(brief, seed)
    if user:
        return user
    return _path_b(brief, seed)
