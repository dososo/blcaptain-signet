#!/usr/bin/env python3
"""Theme a vendored Lucide subset into Signet UI SVG tokens."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

try:
    from icon_subset import (
        FEATHER_DERIVED_ALIASES,
        LUCIDE_REPOSITORY,
        LUCIDE_STATIC_BASE_URL,
        LUCIDE_STATIC_VERSION,
        UI_ICON_SUBSET,
    )
except ImportError:  # pragma: no cover
    from .icon_subset import (  # type: ignore
        FEATHER_DERIVED_ALIASES,
        LUCIDE_REPOSITORY,
        LUCIDE_STATIC_BASE_URL,
        LUCIDE_STATIC_VERSION,
        UI_ICON_SUBSET,
    )


BASE_DIR = Path(__file__).resolve().parent
UPSTREAM_DIR = BASE_DIR / "upstream" / "lucide"
THEMED_DIR = BASE_DIR / "themed"
MANIFEST_PATH = BASE_DIR / "manifest.json"
SVG_NS = "http://www.w3.org/2000/svg"
GEOMETRY_TAGS = {"path", "circle", "rect", "line", "polyline", "polygon", "ellipse"}
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
TOKEN_SCHEMA = {
    "grid": "24x24",
    "viewBox": "0 0 24 24",
    "stroke": "currentColor",
    "fill": "none",
    "stroke-width": "2",
    "stroke-linecap": "round",
    "stroke-linejoin": "round",
    "corner-policy": "round cap and round join; upstream geometry preserved",
    "palette-policy": "currentColor driven by CSS color or --signet-ui-color",
}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_feather_derived(license_text: str) -> set[str]:
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


def is_feather_derived(icon_id: str, feather_derived: set[str]) -> bool:
    canonical_id = FEATHER_DERIVED_ALIASES.get(icon_id, icon_id)
    return icon_id in feather_derived or canonical_id in feather_derived


def validate_hex_color(color: str | None) -> str | None:
    if color is None:
        return None
    if not HEX_RE.fullmatch(color):
        raise ValueError("--color must be a 6-digit hex value like #0F766E")
    return color.upper()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(BASE_DIR))
    except ValueError:
        return str(path)


def normalize_svg(svg_text: str, icon_id: str, color: str | None = None) -> str:
    ET.register_namespace("", SVG_NS)
    root = ET.fromstring(svg_text)
    if local_name(root.tag) != "svg":
        raise ValueError(f"{icon_id}: upstream file is not an SVG")

    root.attrib.clear()
    root.set("width", "24")
    root.set("height", "24")
    root.set("viewBox", TOKEN_SCHEMA["viewBox"])
    root.set("fill", TOKEN_SCHEMA["fill"])
    root.set("stroke", TOKEN_SCHEMA["stroke"])
    root.set("stroke-width", TOKEN_SCHEMA["stroke-width"])
    root.set("stroke-linecap", TOKEN_SCHEMA["stroke-linecap"])
    root.set("stroke-linejoin", TOKEN_SCHEMA["stroke-linejoin"])
    root.set("class", f"signet-ui-glyph signet-ui-glyph--{icon_id}")
    root.set("role", "img")
    root.set("aria-label", f"Signet themed {icon_id}")
    # 品牌色只进入 manifest / 预览 CSS；SVG 本体必须保持纯 currentColor。

    for element in root.iter():
        if element is root:
            continue
        if local_name(element.tag) not in GEOMETRY_TAGS:
            continue
        for attr in ("class", "style", "color"):
            element.attrib.pop(attr, None)
        element.set("fill", TOKEN_SCHEMA["fill"])
        element.set("stroke", TOKEN_SCHEMA["stroke"])
        element.set("stroke-width", TOKEN_SCHEMA["stroke-width"])
        element.set("stroke-linecap", TOKEN_SCHEMA["stroke-linecap"])
        element.set("stroke-linejoin", TOKEN_SCHEMA["stroke-linejoin"])

    return ET.tostring(root, encoding="unicode", short_empty_elements=True) + "\n"


def build_theme(
    upstream_dir: Path = UPSTREAM_DIR,
    output_dir: Path = THEMED_DIR,
    manifest_path: Path = MANIFEST_PATH,
    color: str | None = None,
) -> dict:
    color = validate_hex_color(color)
    icons_dir = upstream_dir / "icons"
    license_path = upstream_dir / "LICENSE"
    package_path = upstream_dir / "package.json"
    if not license_path.exists():
        raise FileNotFoundError(f"missing upstream LICENSE: {license_path}")
    if not package_path.exists():
        raise FileNotFoundError(f"missing upstream package metadata: {package_path}")

    license_text = license_path.read_text(encoding="utf-8")
    package = json.loads(package_path.read_text(encoding="utf-8"))
    if package.get("version") != LUCIDE_STATIC_VERSION:
        raise ValueError(
            f"lucide-static version mismatch: expected {LUCIDE_STATIC_VERSION}, got {package.get('version')!r}"
        )
    feather_derived = parse_feather_derived(license_text)
    output_dir.mkdir(parents=True, exist_ok=True)

    glyphs = []
    for icon_id in UI_ICON_SUBSET:
        upstream_file = icons_dir / f"{icon_id}.svg"
        if not upstream_file.exists():
            raise FileNotFoundError(f"missing upstream SVG: {upstream_file}")
        themed_svg = normalize_svg(upstream_file.read_text(encoding="utf-8"), icon_id, color=color)
        output_file = output_dir / f"{icon_id}.svg"
        output_file.write_text(themed_svg, encoding="utf-8")
        is_feather = is_feather_derived(icon_id, feather_derived)
        glyphs.append(
            {
                "id": icon_id,
                "upstream_source_url": f"{LUCIDE_STATIC_BASE_URL}/icons/{icon_id}.svg",
                "upstream_file": display_path(upstream_file),
                "themed_file": display_path(output_file),
                "license": "MIT" if is_feather else "ISC",
                "license_notice": (
                    "Feather-derived icon; MIT notice retained in upstream Lucide LICENSE"
                    if is_feather
                    else "Lucide icon; ISC notice retained in upstream Lucide LICENSE"
                ),
                "derivative_statement": "Normalized stroke/color tokens only; upstream geometry preserved; attributed upstream; not original artwork.",
            }
        )

    manifest = {
        "generated_at": dt.date.today().isoformat(),
        "generated_by": "skills/signet/ui/theme_ui.py",
        "upstream": {
            "name": package.get("name", "lucide-static"),
            "version": package.get("version", LUCIDE_STATIC_VERSION),
            "package_url": f"{LUCIDE_STATIC_BASE_URL}/package.json",
            "license_url": f"{LUCIDE_STATIC_BASE_URL}/LICENSE",
            "repository": LUCIDE_REPOSITORY,
            "vendored_license": str(license_path.relative_to(BASE_DIR)),
        },
        "token_schema": TOKEN_SCHEMA,
        "count": len(glyphs),
        "color_demo": color,
        "apache_2_compatibility": "ISC and MIT notices are permissive and compatible with Apache-2.0 redistribution when retained.",
        "glyphs": glyphs,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Theme vendored Lucide SVGs into Signet UI tokens.")
    parser.add_argument("--upstream", type=Path, default=UPSTREAM_DIR)
    parser.add_argument("--out", type=Path, default=THEMED_DIR)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--color", help="Optional 6-digit hex fallback for CSS-var driven currentColor demos.")
    args = parser.parse_args(argv)

    manifest = build_theme(args.upstream, args.out, args.manifest, args.color)
    print(f"themed={len(manifest['glyphs'])} out={args.out} manifest={args.manifest}")
    if manifest["color_demo"]:
        print(f"color_demo={manifest['color_demo']} via currentColor + --signet-ui-color")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
