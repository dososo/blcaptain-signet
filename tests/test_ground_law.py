"""Executable ground taste-law tests."""
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "signet" / "scripts"))

from export_icon_assets import derive_tile_color  # noqa: E402
from palette_engine import hex_to_oklch  # noqa: E402
from taste_laws import mud_box, premium_ground  # noqa: E402


def test_mud_box_boundaries():
    assert mud_box(0.35, 0.06, 90) is True
    assert mud_box(0.14, 0.01, 90) is False
    assert mud_box(0.32, 0.12, 235) is False


def test_premium_ground_near_black_passes_gates():
    ground, report = premium_ground("#E8853A", family_hue=55, tier="near-black")
    L, C, H = hex_to_oklch(ground)
    assert not mud_box(L, C, H)
    assert report["gates"]["chroma_gap"] is True
    assert report["gates"]["value_gap"] is True


def test_premium_ground_deep_jewel_uses_family_hue_when_clean():
    ground, report = premium_ground("#BFC8D6", family_hue=235, tier="deep-jewel")
    L, C, H = hex_to_oklch(ground)
    assert not mud_box(L, C, H)
    assert 0.25 <= L <= 0.45
    assert C >= 0.10
    assert abs((H - 235 + 180) % 360 - 180) <= 30
    assert report["resolved_species"] == "deep-jewel"


def test_dark_anchor_no_longer_falls_into_mud_box():
    tile, report = derive_tile_color("#EE7A43", "dark-anchor", "#E8853A")
    assert report["guards"]["not_mud_box"] is True
    assert not mud_box(*hex_to_oklch(tile))


def test_all_tile_modes_and_ground_tiers_avoid_mud_box():
    for mode in ("saturated-sibling", "dark-anchor", "cream-tint", "jewel-ground", "near-black-ground"):
        tile, _ = derive_tile_color("#EE7A43", mode, "#E8853A")
        assert not mud_box(*hex_to_oklch(tile)), mode
    for tier in ("near-black", "deep-jewel", "pale-tint"):
        ground, _ = premium_ground("#E8853A", family_hue=55, tier=tier)
        assert not mud_box(*hex_to_oklch(ground)), tier
