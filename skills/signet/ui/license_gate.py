#!/usr/bin/env python3
"""Gate WS-3 UI icon manifests to permissive licenses only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
MANIFEST_PATH = BASE_DIR / "manifest.json"
PERMISSIVE_LICENSES = {"ISC", "MIT", "Apache-2.0", "BSD", "BSD-2-Clause", "BSD-3-Clause"}


def validate_manifest(manifest: dict) -> list[str]:
    errors: list[str] = []
    glyphs = manifest.get("glyphs")
    if not isinstance(glyphs, list) or not glyphs:
        return ["manifest has no glyphs"]

    for index, glyph in enumerate(glyphs):
        icon_id = glyph.get("id", f"#{index}")
        license_id = glyph.get("license")
        if license_id not in PERMISSIVE_LICENSES:
            errors.append(f"{icon_id}: non-permissive or unknown license {license_id!r}")
        if not glyph.get("upstream_source_url"):
            errors.append(f"{icon_id}: missing upstream source URL")
        if not glyph.get("derivative_statement"):
            errors.append(f"{icon_id}: missing derivative statement")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate WS-3 UI glyph licenses.")
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    args = parser.parse_args(argv)

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    errors = validate_manifest(manifest)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"PASS: {len(manifest['glyphs'])} glyph licenses are permissive and Apache-2.0 compatible")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

