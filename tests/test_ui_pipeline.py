"""WS-3 merged UI SVG pipeline contract tests."""

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UI_ROOT = ROOT / "skills" / "signet" / "ui"
sys.path.insert(0, str(UI_ROOT))

import param_engine  # noqa: E402
import ui_pipeline  # noqa: E402


REMOVED_WEAK_GLYPHS = {"juju-mark", "brush-mark", "kiln-mark", "knit-mark"}
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


def test_custom_curation_removes_weak_organic_marks(tmp_path):
    out_dir = tmp_path / "custom"
    manifest = param_engine.build_custom(out_dir, tmp_path / "custom_manifest.json", tmp_path / "custom_preview.html")
    ids = {glyph["id"] for glyph in manifest["glyphs"]}
    assert not (ids & REMOVED_WEAK_GLYPHS)
    assert not {path.stem for path in out_dir.glob("*.svg")} & REMOVED_WEAK_GLYPHS
    assert len(ids) == 22
    assert ON_DEMAND_SAMPLE_IDS <= ids


def test_ui_pipeline_builds_merged_set_manifest_and_preview(tmp_path):
    result = ui_pipeline.build_ui_set(
        output_root=tmp_path / "dist",
        run_id="test-run",
        intent="成套 UI 界面图标",
        brand_words="warm, trustworthy",
        color="#0F766E",
    )
    run_dir = Path(result["run_dir"])
    manifest = json.loads(Path(result["manifest"]).read_text(encoding="utf-8"))
    icon_files = sorted((run_dir / "icons").glob("*.svg"))

    assert result["counts"] == {"themed": 250, "custom": 22, "total": 272}
    assert len(icon_files) == 272
    assert len(manifest["glyphs"]) == 272
    assert {glyph["license"] for glyph in manifest["glyphs"]} <= {"ISC", "MIT", "Apache-2.0"}
    assert "按需生成" in manifest["honest_scope"]
    assert "不是原创 500 图标大库" in manifest["honest_scope"]
    assert not ({glyph["id"] for glyph in manifest["glyphs"]} & REMOVED_WEAK_GLYPHS)

    index = Path(result["index"]).read_text(encoding="utf-8")
    assert index.count("<article class=\"glyph-card\"") == 272
    assert "250 个 Lucide themed" in index
    assert "22 个 Signet custom" in index
    assert "按需生成" in index
    assert "--signet-ui-color" in index
    assert "src=\"http" not in index
    assert "href=\"http" not in index


def test_ui_pipeline_accepts_five_role_palette(tmp_path):
    palette = '{"primary":"#0F766E","secondary":"#1F2937","tertiary":"#EAB308","accent":"#F97316","detail":"#111827"}'
    result = ui_pipeline.build_ui_set(output_root=tmp_path / "dist", run_id="palette-run", palette_json=palette)
    manifest = json.loads(Path(result["manifest"]).read_text(encoding="utf-8"))
    assert manifest["palette"]["primary"] == "#0F766E"
    assert set(manifest["palette"]) == {"primary", "secondary", "tertiary", "accent", "detail"}
