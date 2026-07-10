"""Executable taste laws for Signet export and gallery layers."""
from __future__ import annotations

from typing import Any

from palette_engine import hex_to_oklch, normalize_hex, oklch_to_hex


GROUND_SPECIES = {
    "near-black": {"L_max": 0.20, "C_max": 0.03, "ref": "#121316"},
    "deep-jewel": {"L_min": 0.25, "L_max": 0.45, "C_min": 0.10, "ref": "#0B1B3A"},
    "pale-tint": {"L_min": 0.90, "C_max": 0.05, "ref": "#F6F1E9"},
}
GROUND_TIERS = ("auto", "near-black", "deep-jewel", "pale-tint")
MUD_HUE_MIN = 70.0
MUD_HUE_MAX = 140.0


def hue_delta(a: float, b: float) -> float:
    return abs((a - b + 180) % 360 - 180)


def mud_box(L: float, C: float, H: float) -> bool:
    return 0.20 < L < 0.70 and 0.03 < C < 0.10 and MUD_HUE_MIN <= (H % 360) <= MUD_HUE_MAX


def mud_box_hex(value: str) -> bool:
    return mud_box(*hex_to_oklch(normalize_hex(value)))


def _near_black(family_hue: float) -> tuple[float, float, float]:
    return 0.14, 0.012, family_hue


def _deep_jewel_hue(family_hue: float, seed: str = "") -> float:
    family_hue = family_hue % 360
    if MUD_HUE_MIN <= family_hue <= MUD_HUE_MAX:
        return (family_hue + 180) % 360
    if 210 <= family_hue <= 250:
        return (family_hue + 20) % 360
    return family_hue


def _candidate_lch(tier: str, family_hue: float, seed: str = "") -> tuple[float, float, float]:
    if tier == "deep-jewel":
        return 0.34, 0.14, _deep_jewel_hue(family_hue, seed)
    if tier == "pale-tint":
        return 0.965, 0.022, 82
    return _near_black(family_hue)


def premium_ground(subject_hex: str, family_hue: float, tier: str, seed: str = "") -> tuple[str, dict[str, Any]]:
    """Return a curated premium ground and its guard report.

    The function never darkens/desaturates the subject color. It places the
    ground into one of the three clean species and falls back to near-black
    when the requested species fails the executable taste gates.
    """
    tier = tier if tier in GROUND_SPECIES else "near-black"
    subject_hex = normalize_hex(subject_hex)
    subject_L, subject_C, _ = hex_to_oklch(subject_hex)
    requested_lch = _candidate_lch(tier, family_hue, seed)
    ground_hex = oklch_to_hex(requested_lch)
    ground_L, ground_C, ground_H = hex_to_oklch(ground_hex)

    gates = {
        "not_mud_box": not mud_box(ground_L, ground_C, ground_H),
        "chroma_gap": abs(subject_C - ground_C) >= 0.08,
        "value_gap": abs(subject_L - ground_L) >= 0.35,
    }
    fallback_used = False
    if not all(gates.values()):
        fallback_used = True
        ground_hex = oklch_to_hex(_near_black(family_hue))
        ground_L, ground_C, ground_H = hex_to_oklch(ground_hex)
        gates = {
            "not_mud_box": not mud_box(ground_L, ground_C, ground_H),
            "chroma_gap": abs(subject_C - ground_C) >= 0.08,
            "value_gap": abs(subject_L - ground_L) >= 0.35,
        }

    report = {
        "tier": tier,
        "resolved_species": "near-black" if fallback_used else tier,
        "fallback_used": fallback_used,
        "subject": subject_hex,
        "family_hue": round(family_hue % 360, 1),
        "ground_lch": {"L": round(ground_L, 3), "C": round(ground_C, 3), "H": round(ground_H, 1)},
        "gates": gates,
    }
    return ground_hex, report
