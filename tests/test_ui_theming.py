"""WS-3 UI theming contract tests."""

import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest


ROOT = Path(__file__).resolve().parents[1]
UI_ROOT = ROOT / "skills" / "signet" / "ui"
sys.path.insert(0, str(UI_ROOT))

import license_gate  # noqa: E402
import theme_ui  # noqa: E402
from icon_subset import UI_ICON_SUBSET  # noqa: E402


GEOMETRY_TAGS = {"path", "circle", "rect", "line", "polyline", "polygon", "ellipse"}
COLOR_RE = re.compile(r"(#[0-9a-fA-F]{3,8}|rgb\(|hsl\()", re.IGNORECASE)


def local_name(tag):
    return tag.rsplit("}", 1)[-1]


def themed_tmp(tmp_path):
    out_dir = tmp_path / "themed"
    manifest_path = tmp_path / "manifest.json"
    manifest = theme_ui.build_theme(output_dir=out_dir, manifest_path=manifest_path, color="#0F766E")
    return out_dir, manifest_path, manifest


def test_theme_outputs_valid_tokenized_svgs(tmp_path):
    out_dir, _, manifest = themed_tmp(tmp_path)
    assert manifest["count"] == len(manifest["glyphs"]) == 250

    for glyph in manifest["glyphs"]:
        svg_path = out_dir / f"{glyph['id']}.svg"
        text = svg_path.read_text(encoding="utf-8")
        root = ET.fromstring(text)
        assert local_name(root.tag) == "svg"
        assert root.get("viewBox") == "0 0 24 24"
        assert root.get("fill") == "none"
        assert root.get("stroke") == "currentColor"
        assert root.get("stroke-width") == "2"
        assert root.get("stroke-linecap") == "round"
        assert root.get("stroke-linejoin") == "round"
        assert root.get("style") is None
        assert not COLOR_RE.search(text.replace("currentColor", ""))

        geometry_count = 0
        for element in root.iter():
            if local_name(element.tag) not in GEOMETRY_TAGS:
                continue
            geometry_count += 1
            assert element.get("fill") == "none"
            assert element.get("stroke") == "currentColor"
            assert element.get("stroke-width") == "2"
            assert element.get("stroke-linecap") == "round"
            assert element.get("stroke-linejoin") == "round"
            scrubbed = element.get("stroke", "").replace("currentColor", "")
            assert not COLOR_RE.search(scrubbed)
        assert geometry_count > 0


def test_manifest_covers_all_subset_glyphs(tmp_path):
    _, _, manifest = themed_tmp(tmp_path)
    ids = {glyph["id"] for glyph in manifest["glyphs"]}
    assert ids == set(UI_ICON_SUBSET)
    assert all(glyph["upstream_source_url"].startswith("https://unpkg.com/lucide-static@1.23.0/icons/") for glyph in manifest["glyphs"])
    assert all(glyph["derivative_statement"] for glyph in manifest["glyphs"])


def test_vendored_source_index_matches_expanded_subset():
    sources_path = UI_ROOT / "upstream" / "lucide" / "sources.json"
    sources = json.loads(sources_path.read_text(encoding="utf-8"))
    assert sources["count"] == len(sources["icons"]) == len(UI_ICON_SUBSET) == 250
    assert set(sources["icons"]) == set(UI_ICON_SUBSET)


def test_feather_derived_icons_are_marked_mit(tmp_path):
    _, _, manifest = themed_tmp(tmp_path)
    by_id = {glyph["id"]: glyph for glyph in manifest["glyphs"]}
    for icon_id in ("arrow-right", "check", "search", "trash"):
        assert by_id[icon_id]["license"] == "MIT"
        assert "Feather-derived" in by_id[icon_id]["license_notice"]
    assert by_id["home"]["license"] == "ISC"


def test_feather_geometry_aliases_are_marked_mit(tmp_path):
    _, _, manifest = themed_tmp(tmp_path)
    by_id = {glyph["id"]: glyph for glyph in manifest["glyphs"]}
    for icon_id in ("circle-minus", "circle-plus", "circle-x", "octagon-alert"):
        assert by_id[icon_id]["license"] == "MIT"
        assert "Feather-derived" in by_id[icon_id]["license_notice"]


def test_feather_license_parser_fails_closed_without_markers():
    with pytest.raises(ValueError, match="Feather"):
        theme_ui.parse_feather_derived("ISC License only")


def test_theme_rejects_mismatched_upstream_version(tmp_path):
    upstream = tmp_path / "lucide"
    (upstream / "icons").mkdir(parents=True)
    (upstream / "LICENSE").write_text(
        (theme_ui.UPSTREAM_DIR / "LICENSE").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (upstream / "package.json").write_text(json.dumps({"name": "lucide-static", "version": "0.0.0"}), encoding="utf-8")

    with pytest.raises(ValueError, match="version"):
        theme_ui.build_theme(upstream_dir=upstream, output_dir=tmp_path / "out", manifest_path=tmp_path / "manifest.json")


def test_license_gate_passes_permissive_manifest(tmp_path):
    _, manifest_path, _ = themed_tmp(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert license_gate.validate_manifest(manifest) == []
    assert license_gate.main(["--manifest", str(manifest_path)]) == 0


def test_license_gate_rejects_non_permissive_record(tmp_path):
    _, manifest_path, manifest = themed_tmp(tmp_path)
    manifest["glyphs"].append(
        {
            "id": "bad-license",
            "upstream_source_url": "https://example.invalid/bad.svg",
            "license": "G" + "PL-3.0",
            "derivative_statement": "test fixture",
        }
    )
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    errors = license_gate.validate_manifest(manifest)
    assert any("bad-license" in error for error in errors)
    assert license_gate.main(["--manifest", str(manifest_path)]) == 1


def test_committed_themed_artifacts_and_licenses_match_vendored_source():
    manifest = json.loads(theme_ui.MANIFEST_PATH.read_text(encoding="utf-8"))
    glyphs = manifest["glyphs"]
    ids = [glyph["id"] for glyph in glyphs]
    upstream_ids = {path.stem for path in (theme_ui.UPSTREAM_DIR / "icons").glob("*.svg")}
    themed_ids = {path.stem for path in theme_ui.THEMED_DIR.glob("*.svg")}
    assert manifest["count"] == len(ids) == len(set(ids)) == 250
    assert set(ids) == set(UI_ICON_SUBSET) == upstream_ids == themed_ids

    license_text = (theme_ui.UPSTREAM_DIR / "LICENSE").read_text(encoding="utf-8")
    feather_derived = theme_ui.parse_feather_derived(license_text)
    feather_aliases = {"circle-minus", "circle-plus", "circle-x", "octagon-alert"}
    for glyph in glyphs:
        expected = "MIT" if glyph["id"] in feather_derived | feather_aliases else "ISC"
        assert glyph["license"] == expected
        assert (UI_ROOT / glyph["upstream_file"]).exists()
        assert (UI_ROOT / glyph["themed_file"]).exists()
