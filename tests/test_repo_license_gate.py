"""Repo-level WS-3 license gate tests."""

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UI_ROOT = ROOT / "skills" / "signet" / "ui"
sys.path.insert(0, str(UI_ROOT))

import repo_license_gate  # noqa: E402


def write_minimal_repo(tmp_path: Path, themed_license: str = "ISC", include_upstream_license: bool = True) -> Path:
    root = tmp_path / "repo"
    ui_root = root / "skills" / "signet" / "ui"
    upstream_icons = ui_root / "upstream" / "lucide" / "icons"
    custom_dir = ui_root / "custom"
    upstream_icons.mkdir(parents=True)
    custom_dir.mkdir(parents=True)

    (root / "LICENSE").write_text("Apache License\nVersion 2.0\n", encoding="utf-8")
    (root / "NOTICE.md").write_text("This project is licensed under Apache-2.0.\n", encoding="utf-8")
    (root / "LICENSES.md").write_text("Apache-2.0\nLucide ISC\nFeather MIT\n", encoding="utf-8")
    (root / "skills" / "signet").mkdir(parents=True, exist_ok=True)
    (root / "skills" / "signet" / "SKILL.md").write_text("license: Apache-2.0\n", encoding="utf-8")

    if include_upstream_license:
        (ui_root / "upstream" / "lucide" / "LICENSE").write_text(
            "ISC License\n"
            "The following Lucide icons are derived from the Feather project:\n"
            "minus-circle\n"
            "The MIT License (MIT)\n",
            encoding="utf-8",
        )
    (ui_root / "upstream" / "lucide" / "package.json").write_text(
        json.dumps({"name": "lucide-static", "version": "1.23.0"}),
        encoding="utf-8",
    )
    (upstream_icons / "check.svg").write_text("<svg viewBox=\"0 0 24 24\" />\n", encoding="utf-8")
    (custom_dir / "signet-seal.svg").write_text("<svg viewBox=\"0 0 24 24\" />\n", encoding="utf-8")

    themed_manifest = {
        "upstream": {"version": "1.23.0"},
        "glyphs": [
            {
                "id": "check",
                "upstream_source_url": "https://unpkg.com/lucide-static@1.23.0/icons/check.svg",
                "upstream_file": "upstream/lucide/icons/check.svg",
                "themed_file": "themed/check.svg",
                "license": themed_license,
                "license_notice": "Lucide icon; ISC notice retained in upstream Lucide LICENSE",
                "derivative_statement": "Normalized stroke/color tokens only; attributed upstream; not original artwork.",
            }
        ]
    }
    custom_manifest = {
        "license": "Apache-2.0",
        "glyphs": [
            {
                "id": "signet-seal",
                "output_file": "custom/signet-seal.svg",
                "license": "Apache-2.0",
                "original_statement": "Signet self-authored procedural SVG glyph; no upstream glyph geometry.",
            }
        ],
    }
    (ui_root / "manifest.json").write_text(json.dumps(themed_manifest), encoding="utf-8")
    (ui_root / "custom_manifest.json").write_text(json.dumps(custom_manifest), encoding="utf-8")
    return root


def test_repo_license_gate_passes_current_repo():
    errors, summary = repo_license_gate.validate_repo(ROOT)
    assert errors == []
    assert summary == {"vendored": 1, "themed": 250, "custom": 22, "total": 272}


def test_repo_license_gate_rejects_gpl_manifest_record(tmp_path):
    root = write_minimal_repo(tmp_path, themed_license="G" + "PL-3.0")

    errors, _ = repo_license_gate.validate_repo(root)

    assert any("check" in error and "license" in error for error in errors)
    assert repo_license_gate.main(["--root", str(root)]) == 1


def test_repo_license_gate_rejects_missing_vendored_license(tmp_path):
    root = write_minimal_repo(tmp_path, include_upstream_license=False)

    errors, _ = repo_license_gate.validate_repo(root)

    assert any("missing LICENSE" in error for error in errors)
    assert repo_license_gate.main(["--root", str(root)]) == 1


def test_repo_license_gate_rejects_feather_alias_misclassified_as_isc(tmp_path):
    root = write_minimal_repo(tmp_path)
    manifest_path = root / "skills" / "signet" / "ui" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["glyphs"][0]["id"] = "circle-minus"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    errors, _ = repo_license_gate.validate_repo(root)

    assert any("circle-minus" in error and "MIT" in error for error in errors)


def test_repo_license_gate_rejects_unparseable_feather_notice(tmp_path):
    root = write_minimal_repo(tmp_path)
    license_path = root / "skills" / "signet" / "ui" / "upstream" / "lucide" / "LICENSE"
    license_path.write_text("ISC License only\n", encoding="utf-8")

    errors, _ = repo_license_gate.validate_repo(root)

    assert any("Feather" in error for error in errors)


def test_repo_license_gate_rejects_mismatched_upstream_version(tmp_path):
    root = write_minimal_repo(tmp_path)
    package_path = root / "skills" / "signet" / "ui" / "upstream" / "lucide" / "package.json"
    package_path.write_text(json.dumps({"name": "lucide-static", "version": "0.0.0"}), encoding="utf-8")

    errors, _ = repo_license_gate.validate_repo(root)

    assert any("version" in error for error in errors)
