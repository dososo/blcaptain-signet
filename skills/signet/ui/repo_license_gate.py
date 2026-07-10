#!/usr/bin/env python3
"""Repo-level license gate for WS-3 UI vendored assets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from icon_subset import FEATHER_DERIVED_ALIASES, LUCIDE_STATIC_VERSION
except ImportError:  # pragma: no cover
    from .icon_subset import FEATHER_DERIVED_ALIASES, LUCIDE_STATIC_VERSION  # type: ignore


UI_ROOT = Path(__file__).resolve().parent
REPO_ROOT = UI_ROOT.parents[2]
UPSTREAM_ROOT = UI_ROOT / "upstream"
THEMED_MANIFEST = UI_ROOT / "manifest.json"
CUSTOM_MANIFEST = UI_ROOT / "custom_manifest.json"

PERMISSIVE_LICENSES = {"ISC", "MIT", "BSD", "BSD-2-Clause", "BSD-3-Clause", "Apache-2.0", "CC0"}
RESTRICTED_TOKENS = ("A" + "GPL", "G" + "PL-", "G" + "PLv")
TEXT_SUFFIXES = {".cfg", ".css", ".html", ".ini", ".json", ".md", ".py", ".rst", ".toml", ".txt", ".yaml", ".yml"}
SKIP_SCAN_PARTS = {".git", ".pytest_cache", "__pycache__", "upstream"}
ALLOWED_RESTRICTED_CONTEXTS = (
    "排除",
    "对比",
    "未引入",
    "禁",
    "只研究",
    "fixture",
    "test",
    "exclusion",
    "exclude",
    "comparison",
    "not introduced",
    "not include",
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def has_apache_2_claim(text: str) -> bool:
    return "Apache-2.0" in text or ("Apache License" in text and "Version 2.0" in text)


def parse_feather_notice(license_text: str) -> set[str]:
    marker = "The following Lucide icons are derived from the Feather project:"
    end_marker = "The MIT License (MIT)"
    if marker not in license_text or end_marker not in license_text:
        raise ValueError("Lucide LICENSE is missing the Feather-derived MIT notice markers")
    block = license_text.split(marker, 1)[1].split(end_marker, 1)[0]
    icons = {
        icon.strip().strip(".")
        for icon in block.replace("\n", " ").split(",")
        if icon.strip()
    }
    if not icons:
        raise ValueError("Lucide LICENSE Feather-derived MIT notice contains no glyph ids")
    return icons


def expected_lucide_license(icon_id: str, feather_derived: set[str]) -> str:
    canonical_id = FEATHER_DERIVED_ALIASES.get(icon_id, icon_id)
    return "MIT" if icon_id in feather_derived or canonical_id in feather_derived else "ISC"


def validate_root_license(root: Path) -> list[str]:
    errors: list[str] = []
    license_path = root / "LICENSE"
    if not license_path.exists():
        return ["missing root LICENSE"]
    if not has_apache_2_claim(license_path.read_text(encoding="utf-8")):
        errors.append("root LICENSE is not Apache-2.0")

    required_claims = [
        root / "NOTICE.md",
        root / "LICENSES.md",
        root / "skills" / "signet" / "SKILL.md",
    ]
    for path in required_claims:
        if not path.exists():
            errors.append(f"{path.relative_to(root)} missing")
            continue
        if not has_apache_2_claim(path.read_text(encoding="utf-8")):
            errors.append(f"{path.relative_to(root)} does not claim Apache-2.0")
    return errors


def validate_upstream_dirs(upstream_root: Path, root: Path) -> list[str]:
    if not upstream_root.exists():
        return [f"{upstream_root.relative_to(root)} missing"]

    errors: list[str] = []
    vendored_dirs = [path for path in sorted(upstream_root.iterdir()) if path.is_dir()]
    if not vendored_dirs:
        return [f"{upstream_root.relative_to(root)} has no vendored directories"]

    for path in vendored_dirs:
        if not (path / "LICENSE").exists():
            errors.append(f"{path.relative_to(root)} missing LICENSE")
    return errors


def validate_themed_manifest(manifest_path: Path, ui_root: Path, root: Path) -> tuple[list[str], int]:
    manifest = load_json(manifest_path)
    glyphs = manifest.get("glyphs")
    if not isinstance(glyphs, list) or not glyphs:
        return [f"{manifest_path.relative_to(root)} has no glyphs"], 0

    errors: list[str] = []
    package_path = ui_root / "upstream" / "lucide" / "package.json"
    if package_path.exists():
        try:
            package_version = load_json(package_path).get("version")
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"{package_path.relative_to(root)} unreadable: {exc}")
        else:
            if package_version != LUCIDE_STATIC_VERSION:
                errors.append(
                    f"lucide-static version mismatch: expected {LUCIDE_STATIC_VERSION}, got {package_version!r}"
                )
    else:
        errors.append(f"{package_path.relative_to(root)} missing")

    manifest_version = manifest.get("upstream", {}).get("version")
    if manifest_version != LUCIDE_STATIC_VERSION:
        errors.append(
            f"manifest lucide-static version mismatch: expected {LUCIDE_STATIC_VERSION}, got {manifest_version!r}"
        )

    feather_derived: set[str] | None = None
    license_path = ui_root / "upstream" / "lucide" / "LICENSE"
    if license_path.exists():
        try:
            feather_derived = parse_feather_notice(license_path.read_text(encoding="utf-8"))
        except ValueError as exc:
            errors.append(str(exc))
    else:
        errors.append(f"{license_path.relative_to(root)} missing")

    for index, glyph in enumerate(glyphs):
        icon_id = glyph.get("id") or f"#{index}"
        license_id = glyph.get("license")
        if license_id not in PERMISSIVE_LICENSES:
            errors.append(f"{icon_id}: non-permissive or unknown license {license_id!r}")
        for key in ("upstream_source_url", "upstream_file", "license_notice", "derivative_statement"):
            if not glyph.get(key):
                errors.append(f"{icon_id}: missing {key}")
        upstream_file = glyph.get("upstream_file")
        if upstream_file and not (ui_root / upstream_file).exists():
            errors.append(f"{icon_id}: upstream file missing at {upstream_file}")
        if license_id == "MIT" and "Feather-derived" not in glyph.get("license_notice", ""):
            errors.append(f"{icon_id}: MIT glyph missing Feather-derived notice")
        if feather_derived is not None:
            expected_license = expected_lucide_license(icon_id, feather_derived)
            if license_id != expected_license:
                errors.append(f"{icon_id}: expected {expected_license} from vendored Lucide LICENSE, got {license_id!r}")
    return errors, len(glyphs)


def validate_custom_manifest(manifest_path: Path, ui_root: Path, root: Path) -> tuple[list[str], int]:
    manifest = load_json(manifest_path)
    glyphs = manifest.get("glyphs")
    if not isinstance(glyphs, list) or not glyphs:
        return [f"{manifest_path.relative_to(root)} has no glyphs"], 0

    errors: list[str] = []
    if manifest.get("license") != "Apache-2.0":
        errors.append(f"{manifest_path.relative_to(root)} top-level license is not Apache-2.0")

    for index, glyph in enumerate(glyphs):
        icon_id = glyph.get("id") or f"#{index}"
        license_id = glyph.get("license")
        if license_id not in PERMISSIVE_LICENSES:
            errors.append(f"{icon_id}: non-permissive or unknown license {license_id!r}")
        if license_id != "Apache-2.0":
            errors.append(f"{icon_id}: custom glyph license is not Apache-2.0")
        if not glyph.get("original_statement"):
            errors.append(f"{icon_id}: missing original_statement")
        output_file = glyph.get("output_file")
        if output_file and not (ui_root / output_file).exists():
            errors.append(f"{icon_id}: custom output file missing at {output_file}")
    return errors, len(glyphs)


def scan_restricted_claims(root: Path) -> list[str]:
    errors: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if set(relative.parts) & SKIP_SCAN_PARTS:
            continue
        if path.suffix and path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(lines, start=1):
            lower_line = line.lower()
            if not any(token.lower() in lower_line for token in RESTRICTED_TOKENS):
                continue
            if any(marker.lower() in lower_line for marker in ALLOWED_RESTRICTED_CONTEXTS):
                continue
            errors.append(f"{relative}:{line_number}: restricted license token outside exclusion/comparison context")
    return errors


def validate_repo(root: Path = REPO_ROOT) -> tuple[list[str], dict[str, int]]:
    root = root.resolve()
    ui_root = root / "skills" / "signet" / "ui"
    upstream_root = ui_root / "upstream"
    themed_manifest = ui_root / "manifest.json"
    custom_manifest = ui_root / "custom_manifest.json"

    errors: list[str] = []
    errors.extend(validate_root_license(root))
    errors.extend(validate_upstream_dirs(upstream_root, root))

    themed_errors, themed_count = validate_themed_manifest(themed_manifest, ui_root, root)
    custom_errors, custom_count = validate_custom_manifest(custom_manifest, ui_root, root)
    errors.extend(themed_errors)
    errors.extend(custom_errors)
    errors.extend(scan_restricted_claims(root))

    vendored_count = len([path for path in upstream_root.iterdir() if path.is_dir()]) if upstream_root.exists() else 0
    summary = {"vendored": vendored_count, "themed": themed_count, "custom": custom_count, "total": themed_count + custom_count}
    return errors, summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Signet repo license and WS-3 UI attribution gates.")
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    errors, summary = validate_repo(args.root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(
        "PASS: "
        f"vendored={summary['vendored']} "
        f"themed={summary['themed']} "
        f"custom={summary['custom']} "
        f"permissive={summary['total']} "
        "restricted=0 "
        "apache=ok"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
