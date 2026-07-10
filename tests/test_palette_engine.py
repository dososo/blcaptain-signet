"""Palette engine determinism and quality floors."""
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "signet" / "scripts"))

from palette_engine import (  # noqa: E402
    evaluate,
    generate,
    house_palette_names,
)


def floor_passes(result):
    return all(check["pass"] for check in result.report["floor_checks"])


def test_palette_engine_is_deterministic_for_same_seed():
    brief = {"project_name": "PaletteTest", "icon_subject": "friendly archive box", "seed": "abc123"}
    assert generate(brief) == generate(brief)


def test_palette_engine_changes_with_seed():
    brief = {"project_name": "PaletteTest", "icon_subject": "friendly archive box", "seed": "abc123"}
    other = {**brief, "seed": "abc124"}
    assert generate(brief).roles != generate(other).roles


def test_path_a_parses_labeled_cn_aliases_and_derives_missing_roles():
    result = generate({
        "project_name": "PaletteTest",
        "icon_subject": "paper guide",
        "color_palette": "辅色 #B8E6B3 主色 #FFC9D6 点缀 #FFF6DC",
        "seed": "cn-alias",
    })
    assert result.roles["primary"] == "#FFC9D6"
    assert result.roles["secondary"] == "#B8E6B3"
    assert result.roles["accent"] == "#FFF6DC"
    assert result.roles["tertiary"].startswith("#")
    assert result.roles["detail"].startswith("#")
    assert any("derived" in warning for warning in result.report["warnings"])


def test_path_a_unlabeled_list_maps_in_order_and_keeps_user_hexes():
    result = generate({
        "project_name": "PaletteTest",
        "icon_subject": "legacy dark brand palette",
        "color_palette": ["#1D1D1F", "#F7F4EA", "#FF8A00"],
        "seed": "ordered",
    })
    assert result.roles["primary"] == "#1D1D1F"
    assert result.roles["secondary"] == "#F7F4EA"
    assert result.roles["tertiary"] == "#FF8A00"
    assert any("user palette kept" in warning for warning in result.report["warnings"])


def test_path_b_samples_1000_seeded_palettes_through_floors():
    for i in range(1000):
        result = generate({"project_name": "PaletteTest", "icon_subject": f"object {i}", "seed": str(i)})
        assert floor_passes(result), result.report


def test_house_palettes_all_pass_quality_floors():
    for name in house_palette_names():
        result = generate({
            "project_name": "PaletteTest",
            "icon_subject": "house palette sample",
            "color_palette": {"house_palette": name},
            "seed": name,
        })
        assert floor_passes(result), (name, result.report)


def test_vivid_house_palette_can_be_selected_by_id_and_reports_colored_ground():
    result = generate({
        "project_name": "PaletteTest",
        "icon_subject": "vivid camera",
        "color_palette": {"house_palette": "V1", "palette_family": "vivid"},
        "seed": "vivid-v1",
    })
    assert result.report["template_id"] == "V1"
    assert result.report["palette_family"] == "vivid"
    assert result.tile["mode"] == "saturated-sibling"
    assert result.roles["primary"] == "#FF8A2B"
    assert floor_passes(result), result.report


def test_vivid_palette_family_auto_selects_v_palettes():
    result = generate({
        "project_name": "PaletteTest",
        "icon_subject": "vivid padlock",
        "palette_family": "vivid",
        "seed": "vivid-auto",
    })
    assert result.report["template_id"] in {"V1", "V2", "V3", "V4"}
    assert result.report["palette_family"] == "vivid"
    assert result.tile["mode"] in {"saturated-sibling", "dark-anchor"}
    assert floor_passes(result), result.report


def test_vivid_set_hue_rotation_changes_roles_by_index():
    base = {
        "project_name": "PaletteTest",
        "icon_subject": "vivid set item",
        "palette_family": "vivid",
        "seed": "vivid-set",
        "set_count": 8,
    }
    first = generate({**base, "set_index": 0})
    fourth = generate({**base, "set_index": 3})
    assert first.report["template_id"] == fourth.report["template_id"]
    assert first.report["rotation_deg"] != fourth.report["rotation_deg"]
    assert first.roles["primary"] != fourth.roles["primary"]


def test_f7_rejects_phase6a_machine_triad():
    roles = {
        "primary": "#E03131",
        "secondary": "#1864AB",
        "tertiary": "#2B8A3E",
        "accent": "#FFF2A6",
        "detail": "#5A2A16",
    }
    checks = {check["id"]: check for check in evaluate(roles, "#F8F4EA")}
    assert checks["F7"]["pass"] is False
    assert "red" in checks["F7"]["detail"]
    assert "green" in checks["F7"]["detail"]
    assert "blue" in checks["F7"]["detail"]


def test_reference_quality_palette_passes_quality_floors():
    result = generate({
        "project_name": "PaletteTest",
        "icon_subject": "reference-quality sample",
        "color_palette": {
            "roles": {
                "primary": "#BDF4A7",
                "secondary": "#5ED6D8",
                "tertiary": "#FF9A3D",
                "accent": "#FFF2A6",
                "detail": "#5A2A16",
            }
        },
        "seed": "quality-floor",
    })
    checks = {check["id"]: check for check in result.report["floor_checks"]}
    assert checks["F7"]["pass"] is True
    assert checks["F8"]["pass"] is True
