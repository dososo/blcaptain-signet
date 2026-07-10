"""WS-3 custom parameterized glyph contract tests."""

import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
UI_ROOT = ROOT / "skills" / "signet" / "ui"
sys.path.insert(0, str(UI_ROOT))

import param_engine  # noqa: E402
from icon_subset import UI_ICON_SUBSET  # noqa: E402


GEOMETRY_TAGS = {"path", "circle", "rect", "line", "polyline", "polygon", "ellipse"}
COLOR_RE = re.compile(r"(#[0-9a-fA-F]{3,8}|rgb\(|hsl\()", re.IGNORECASE)
FORBIDDEN_SVG_FEATURES = ("<filter", " filter=", " transform=")
ON_DEMAND_SAMPLE_IDS = {
    "battery-charging",
    "maximize",
    "minimize",
    "qr-code",
    "redo",
    "scan",
    "sliders-horizontal",
    "undo",
}


def local_name(tag):
    return tag.rsplit("}", 1)[-1]


def build_tmp(tmp_path):
    out_dir = tmp_path / "custom"
    manifest_path = tmp_path / "custom_manifest.json"
    preview_path = tmp_path / "custom_preview.html"
    manifest = param_engine.build_custom(out_dir, manifest_path, preview_path)
    return out_dir, manifest_path, preview_path, manifest


def test_custom_outputs_valid_tokenized_svgs(tmp_path):
    out_dir, _, _, manifest = build_tmp(tmp_path)
    assert manifest["count"] == len(manifest["glyphs"]) == 22

    for glyph in manifest["glyphs"]:
        svg_path = out_dir / f"{glyph['id']}.svg"
        text = svg_path.read_text(encoding="utf-8")
        assert all(feature not in text for feature in FORBIDDEN_SVG_FEATURES)
        root = ET.fromstring(text)
        assert local_name(root.tag) == "svg"
        assert root.get("viewBox") == "0 0 24 24"
        assert root.get("fill") == "none"
        assert root.get("stroke") == "currentColor"
        assert root.get("stroke-width") == "2"
        assert root.get("stroke-linecap") == "round"
        assert root.get("stroke-linejoin") == "round"

        geometry_count = 0
        scrubbed = text.replace("currentColor", "")
        assert not COLOR_RE.search(scrubbed)
        for element in root.iter():
            if local_name(element.tag) not in GEOMETRY_TAGS:
                continue
            geometry_count += 1
            assert element.get("fill") == "none"
            assert element.get("stroke") == "currentColor"
            assert element.get("stroke-width") == "2"
            assert element.get("stroke-linecap") == "round"
            assert element.get("stroke-linejoin") == "round"
        assert geometry_count > 0


def test_custom_manifest_covers_all_outputs_and_apache_license(tmp_path):
    out_dir, manifest_path, _, manifest = build_tmp(tmp_path)
    svg_ids = {path.stem for path in out_dir.glob("*.svg")}
    manifest_ids = {glyph["id"] for glyph in manifest["glyphs"]}
    assert manifest_ids == svg_ids
    assert json.loads(manifest_path.read_text(encoding="utf-8"))["glyphs"] == manifest["glyphs"]
    assert all(glyph["license"] == "Apache-2.0" for glyph in manifest["glyphs"])
    assert all("Signet self-authored" in glyph["original_statement"] for glyph in manifest["glyphs"])
    assert not (manifest_ids & set(UI_ICON_SUBSET))
    assert ON_DEMAND_SAMPLE_IDS <= manifest_ids


def test_on_demand_samples_use_registered_draw_functions():
    by_id = {glyph.id: glyph for glyph in param_engine.CUSTOM_GLYPHS}
    assert len(by_id) == len(param_engine.CUSTOM_GLYPHS) == 22
    for glyph_id in ON_DEMAND_SAMPLE_IDS:
        glyph = by_id[glyph_id]
        assert glyph.draw.__name__ == f"draw_{glyph_id.replace('-', '_')}"

    guide = param_engine.__doc__ or ""
    for phrase in ("draw_", "CustomGlyph", "build_custom", "custom_manifest.json"):
        assert phrase in guide


def test_custom_preview_is_self_contained_and_color_switchable(tmp_path):
    _, _, preview_path, manifest = build_tmp(tmp_path)
    preview = preview_path.read_text(encoding="utf-8")
    assert preview.count("<article class=\"glyph-card\"") == len(manifest["glyphs"])
    assert preview.count("data-color=") == 3
    assert "currentColor" in preview
    assert "--glyph-color" in preview
    assert "src=\"http" not in preview
    assert "href=\"http" not in preview
    assert f"{len(manifest['glyphs'])} 个 Signet 自制 SVG glyph" in preview


def test_param_engine_exposes_required_primitives():
    canvas = param_engine.GlyphCanvas("primitive-probe", "Primitive probe")
    for primitive in ("line", "polyline", "arc", "circle", "rect", "path"):
        assert hasattr(canvas, primitive)


def test_committed_custom_artifacts_match_registry():
    manifest = json.loads(param_engine.CUSTOM_MANIFEST_PATH.read_text(encoding="utf-8"))
    registry_ids = [glyph.id for glyph in param_engine.CUSTOM_GLYPHS]
    assert manifest["count"] == len(registry_ids) == 22
    assert [glyph["id"] for glyph in manifest["glyphs"]] == registry_ids
    assert {path.stem for path in param_engine.CUSTOM_DIR.glob("*.svg")} == set(registry_ids)
    for glyph in param_engine.CUSTOM_GLYPHS:
        assert (param_engine.CUSTOM_DIR / f"{glyph.id}.svg").read_text(encoding="utf-8") == param_engine.render_glyph(glyph)
