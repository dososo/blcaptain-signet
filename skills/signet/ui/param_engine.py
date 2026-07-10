#!/usr/bin/env python3
"""用确定性矢量原语生成 Signet 自制 UI glyph。

按需新增一个 glyph 的唯一入口：

1. 新增一个只调用 :class:`GlyphCanvas` 原语的 ``draw_<glyph_id>()`` 函数；
2. 在 ``CUSTOM_GLYPHS`` 注册一条 ``CustomGlyph``，写清 id、label 与 purpose；
3. 运行 ``python skills/signet/ui/param_engine.py``；
4. ``build_custom()`` 会按统一 token 输出 SVG，并把 Apache-2.0 逐 glyph 记录写入
   ``custom_manifest.json``，同时重建自包含预览。

最小示例：``CustomGlyph("status-pin", "Status pin", "状态定位。", draw_status_pin)``。
禁止粘贴第三方 SVG path；draw 函数必须由 Signet 独立编写。
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable
from xml.etree import ElementTree as ET

try:
    from icon_subset import UI_ICON_SUBSET
    from theme_ui import TOKEN_SCHEMA
except ImportError:  # pragma: no cover
    from .icon_subset import UI_ICON_SUBSET  # type: ignore
    from .theme_ui import TOKEN_SCHEMA  # type: ignore


BASE_DIR = Path(__file__).resolve().parent
CUSTOM_DIR = BASE_DIR / "custom"
CUSTOM_MANIFEST_PATH = BASE_DIR / "custom_manifest.json"
CUSTOM_PREVIEW_PATH = BASE_DIR / "custom_preview.html"
SVG_NS = "http://www.w3.org/2000/svg"
GEOMETRY_ATTRS = {
    "fill": TOKEN_SCHEMA["fill"],
    "stroke": TOKEN_SCHEMA["stroke"],
    "stroke-width": TOKEN_SCHEMA["stroke-width"],
    "stroke-linecap": TOKEN_SCHEMA["stroke-linecap"],
    "stroke-linejoin": TOKEN_SCHEMA["stroke-linejoin"],
}
PATH_SPACE_RE = re.compile(r"\s+")


def fmt(value: float | int | str) -> str:
    if isinstance(value, str):
        return value
    if abs(value - round(value)) < 0.001:
        return str(int(round(value)))
    return f"{value:.2f}".rstrip("0").rstrip(".")


def normalize_path(d: str) -> str:
    return PATH_SPACE_RE.sub(" ", d.strip())


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(BASE_DIR))
    except ValueError:
        return str(path)


def points_attr(points: Iterable[tuple[float, float]]) -> str:
    return " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points)


class GlyphCanvas:
    """Small SVG canvas with Signet UI tokenized drawing primitives."""

    def __init__(self, glyph_id: str, label: str) -> None:
        ET.register_namespace("", SVG_NS)
        self.glyph_id = glyph_id
        self.root = ET.Element(
            f"{{{SVG_NS}}}svg",
            {
                "width": "24",
                "height": "24",
                "viewBox": TOKEN_SCHEMA["viewBox"],
                "fill": TOKEN_SCHEMA["fill"],
                "stroke": TOKEN_SCHEMA["stroke"],
                "stroke-width": TOKEN_SCHEMA["stroke-width"],
                "stroke-linecap": TOKEN_SCHEMA["stroke-linecap"],
                "stroke-linejoin": TOKEN_SCHEMA["stroke-linejoin"],
                "class": f"signet-ui-glyph signet-ui-glyph--{glyph_id}",
                "role": "img",
                "aria-label": f"Signet custom {label}",
            },
        )

    def _add(self, tag: str, attrs: dict[str, str]) -> None:
        ET.SubElement(self.root, f"{{{SVG_NS}}}{tag}", {**attrs, **GEOMETRY_ATTRS})

    def line(self, x1: float, y1: float, x2: float, y2: float) -> None:
        self._add("line", {"x1": fmt(x1), "y1": fmt(y1), "x2": fmt(x2), "y2": fmt(y2)})

    def polyline(self, points: Iterable[tuple[float, float]]) -> None:
        self._add("polyline", {"points": points_attr(points)})

    def circle(self, cx: float, cy: float, r: float) -> None:
        self._add("circle", {"cx": fmt(cx), "cy": fmt(cy), "r": fmt(r)})

    def rect(self, x: float, y: float, width: float, height: float, rx: float = 2) -> None:
        self._add(
            "rect",
            {
                "x": fmt(x),
                "y": fmt(y),
                "width": fmt(width),
                "height": fmt(height),
                "rx": fmt(rx),
            },
        )

    def path(self, d: str) -> None:
        self._add("path", {"d": normalize_path(d)})

    def arc(self, cx: float, cy: float, r: float, start_deg: float, end_deg: float) -> None:
        start = math.radians(start_deg)
        end = math.radians(end_deg)
        x1 = cx + r * math.cos(start)
        y1 = cy + r * math.sin(start)
        x2 = cx + r * math.cos(end)
        y2 = cy + r * math.sin(end)
        large_arc = "1" if abs(end_deg - start_deg) > 180 else "0"
        sweep = "1" if end_deg >= start_deg else "0"
        self.path(f"M {fmt(x1)} {fmt(y1)} A {fmt(r)} {fmt(r)} 0 {large_arc} {sweep} {fmt(x2)} {fmt(y2)}")

    def svg(self) -> str:
        return ET.tostring(self.root, encoding="unicode", short_empty_elements=True) + "\n"


@dataclass(frozen=True)
class CustomGlyph:
    id: str
    label: str
    purpose: str
    draw: Callable[[GlyphCanvas], None]


def draw_signet_seal(g: GlyphCanvas) -> None:
    g.circle(12, 12, 7)
    g.path("M 9 10.5 L 12 7.5 L 15 10.5 L 15 14 L 12 16.5 L 9 14 Z")
    g.line(10.5, 12, 13.5, 12)


def draw_material_swatch(g: GlyphCanvas) -> None:
    g.rect(4.5, 5.5, 12, 13, 2)
    g.line(8, 10, 13, 10)
    g.line(8, 13, 11.5, 13)
    g.line(16.5, 9, 19.5, 6)
    g.line(16.5, 15, 19.5, 18)


def draw_palette_5role(g: GlyphCanvas) -> None:
    g.circle(12, 12, 8)
    for cx, cy in ((12, 7.5), (16, 10.5), (14.5, 15.5), (9.5, 15.5), (8, 10.5)):
        g.circle(cx, cy, 1.15)
    g.line(12, 12, 12, 12)


def draw_tier_d_badge(g: GlyphCanvas) -> None:
    g.circle(12, 12, 7)
    g.path("M 12 6.5 L 15 12 L 12 17.5 L 9 12 Z")
    g.line(6.5, 12, 8.5, 12)
    g.line(15.5, 12, 17.5, 12)


def draw_tier_e_badge(g: GlyphCanvas) -> None:
    g.path("M 8 5.5 H 16 L 19 9 V 15 L 16 18.5 H 8 L 5 15 V 9 Z")
    g.line(9, 10, 15, 10)
    g.line(9, 14, 15, 14)


def draw_platform_ios(g: GlyphCanvas) -> None:
    g.rect(7, 3.5, 10, 17, 3)
    g.line(10.5, 17.5, 13.5, 17.5)
    g.circle(12, 6.5, 0.65)


def draw_platform_android(g: GlyphCanvas) -> None:
    g.arc(12, 12, 6.5, 205, 335)
    g.line(8, 7.5, 6.5, 5.5)
    g.line(16, 7.5, 17.5, 5.5)
    g.line(7, 12, 7, 17)
    g.line(17, 12, 17, 17)
    g.line(9, 18.5, 9, 20.5)
    g.line(15, 18.5, 15, 20.5)
    g.circle(9.7, 11, 0.45)
    g.circle(14.3, 11, 0.45)


def draw_platform_harmonyos(g: GlyphCanvas) -> None:
    g.arc(12, 12, 7.5, 25, 205)
    g.arc(12, 12, 4.5, 205, 385)
    g.circle(12, 12, 1.1)


def draw_platform_web(g: GlyphCanvas) -> None:
    g.rect(4, 5, 16, 13, 2)
    g.line(4, 9, 20, 9)
    g.circle(7, 7, 0.5)
    g.circle(9.5, 7, 0.5)


def draw_platform_pwa(g: GlyphCanvas) -> None:
    g.rect(5, 5, 14, 14, 3)
    g.polyline(((8, 15), (10.5, 9), (13, 15), (15.5, 9), (17, 15)))


def draw_platform_macos(g: GlyphCanvas) -> None:
    g.rect(4, 6, 16, 11, 2)
    g.line(9, 20, 15, 20)
    g.line(12, 17, 12, 20)
    g.line(8, 9, 16, 9)


def draw_platform_tvos(g: GlyphCanvas) -> None:
    g.rect(4, 7, 16, 10, 2)
    g.line(9, 19, 15, 19)
    g.line(7, 10, 11, 14)
    g.line(11, 10, 7, 14)
    g.line(13, 10, 17, 10)
    g.line(15, 10, 15, 14)


def draw_export_zip(g: GlyphCanvas) -> None:
    g.path("M 7 4 H 14 L 18 8 V 20 H 7 Z")
    g.polyline(((14, 4), (14, 8), (18, 8)))
    g.line(10, 6.5, 10, 8)
    g.line(12, 8, 12, 9.5)
    g.line(10, 9.5, 10, 11)
    g.rect(9, 13.5, 4, 3.5, 1)


def draw_squircle_tile(g: GlyphCanvas) -> None:
    g.rect(5, 5, 14, 14, 4)
    g.rect(8, 8, 8, 8, 2)
    g.line(12, 5, 12, 8)
    g.line(12, 16, 12, 19)


def draw_battery_charging(g: GlyphCanvas) -> None:
    g.rect(3, 7, 16, 10, 2)
    g.line(21, 10, 21, 14)
    g.path("M 12.5 8.5 L 8.5 13 H 11.5 L 10.5 16 L 15.5 11.5 H 12.5 Z")


def draw_qr_code(g: GlyphCanvas) -> None:
    g.rect(4, 4, 5, 5, 0.75)
    g.rect(15, 4, 5, 5, 0.75)
    g.rect(4, 15, 5, 5, 0.75)
    g.rect(12, 12, 3, 3, 0.5)
    g.line(18, 12, 20, 12)
    g.line(18, 12, 18, 15)
    g.polyline(((12, 18), (15, 18), (15, 20)))
    g.polyline(((18, 18), (20, 18), (20, 20), (18, 20)))


def draw_undo(g: GlyphCanvas) -> None:
    g.polyline(((9, 7), (5, 11), (9, 15)))
    g.path("M 6 11 H 13.5 C 17 11 19 13 19 16.5")


def draw_redo(g: GlyphCanvas) -> None:
    g.polyline(((15, 7), (19, 11), (15, 15)))
    g.path("M 18 11 H 10.5 C 7 11 5 13 5 16.5")


def draw_scan(g: GlyphCanvas) -> None:
    g.polyline(((9, 4), (4, 4), (4, 9)))
    g.polyline(((15, 4), (20, 4), (20, 9)))
    g.polyline(((4, 15), (4, 20), (9, 20)))
    g.polyline(((20, 15), (20, 20), (15, 20)))
    g.line(7, 12, 17, 12)


def draw_sliders_horizontal(g: GlyphCanvas) -> None:
    g.line(4, 6, 20, 6)
    g.circle(9, 6, 2)
    g.line(4, 12, 20, 12)
    g.circle(15, 12, 2)
    g.line(4, 18, 20, 18)
    g.circle(11, 18, 2)


def draw_maximize(g: GlyphCanvas) -> None:
    g.polyline(((9, 4), (4, 4), (4, 9)))
    g.polyline(((15, 4), (20, 4), (20, 9)))
    g.polyline(((4, 15), (4, 20), (9, 20)))
    g.polyline(((20, 15), (20, 20), (15, 20)))


def draw_minimize(g: GlyphCanvas) -> None:
    g.polyline(((4, 9), (9, 9), (9, 4)))
    g.polyline(((20, 9), (15, 9), (15, 4)))
    g.polyline(((4, 15), (9, 15), (9, 20)))
    g.polyline(((20, 15), (15, 15), (15, 20)))


CUSTOM_GLYPHS = [
    CustomGlyph("signet-seal", "Signet seal", "Brand seal for Signet-owned UI identity.", draw_signet_seal),
    CustomGlyph("material-swatch", "Material swatch", "Material sample card for style selection.", draw_material_swatch),
    CustomGlyph("palette-5role", "Palette 5-role", "Five-role palette token selector.", draw_palette_5role),
    CustomGlyph("tier-d-badge", "Tier D badge", "Decision-tier badge for D-level curation states.", draw_tier_d_badge),
    CustomGlyph("tier-e-badge", "Tier E badge", "Decision-tier badge for E-level curation states.", draw_tier_e_badge),
    CustomGlyph("platform-ios", "iOS platform mark", "Abstract iOS export target mark.", draw_platform_ios),
    CustomGlyph("platform-android", "Android platform mark", "Abstract Android export target mark.", draw_platform_android),
    CustomGlyph("platform-harmonyos", "HarmonyOS platform mark", "Abstract HarmonyOS export target mark.", draw_platform_harmonyos),
    CustomGlyph("platform-web", "Web platform mark", "Abstract web export target mark.", draw_platform_web),
    CustomGlyph("platform-pwa", "PWA platform mark", "Abstract PWA export target mark.", draw_platform_pwa),
    CustomGlyph("platform-macos", "macOS platform mark", "Abstract macOS export target mark.", draw_platform_macos),
    CustomGlyph("platform-tvos", "tvOS platform mark", "Abstract tvOS export target mark.", draw_platform_tvos),
    CustomGlyph("export-zip", "Export zip", "Packaged export artifact mark.", draw_export_zip),
    CustomGlyph("squircle-tile", "Squircle tile", "App icon tile and safe-area mark.", draw_squircle_tile),
    CustomGlyph("battery-charging", "Battery charging", "Charging and power state control.", draw_battery_charging),
    CustomGlyph("qr-code", "QR code", "QR scan and share entry point.", draw_qr_code),
    CustomGlyph("undo", "Undo", "Undo the most recent action.", draw_undo),
    CustomGlyph("redo", "Redo", "Redo the most recent reverted action.", draw_redo),
    CustomGlyph("scan", "Scan", "Camera or document scan target.", draw_scan),
    CustomGlyph("sliders-horizontal", "Horizontal sliders", "Tune filters and detailed settings.", draw_sliders_horizontal),
    CustomGlyph("maximize", "Maximize", "Expand a panel or viewport.", draw_maximize),
    CustomGlyph("minimize", "Minimize", "Contract a panel or viewport.", draw_minimize),
]


def render_glyph(glyph: CustomGlyph) -> str:
    canvas = GlyphCanvas(glyph.id, glyph.label)
    glyph.draw(canvas)
    return canvas.svg()


def build_manifest(glyphs: list[CustomGlyph], output_dir: Path) -> dict:
    return {
        "generated_at": dt.date.today().isoformat(),
        "generated_by": "skills/signet/ui/param_engine.py",
        "token_schema": TOKEN_SCHEMA,
        "count": len(glyphs),
        "license": "Apache-2.0",
        "original_statement": "Signet self-authored procedural SVG glyphs; no upstream glyph geometry; released under Apache-2.0.",
        "glyphs": [
            {
                "id": glyph.id,
                "label": glyph.label,
                "purpose": glyph.purpose,
                "output_file": display_path(output_dir / f"{glyph.id}.svg"),
                "license": "Apache-2.0",
                "original_statement": "Signet self-authored procedural SVG glyph; no upstream glyph geometry.",
            }
            for glyph in glyphs
        ],
    }


def inline_svg(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip().replace("<svg ", '<svg aria-hidden="true" ')


def build_preview(glyphs: list[CustomGlyph], output_dir: Path, preview_path: Path) -> None:
    cards = []
    for glyph in glyphs:
        svg = inline_svg(output_dir / f"{glyph.id}.svg")
        cards.append(
            f"""
      <article class="glyph-card">
        <div class="glyph-meta">
          <span>{html.escape(glyph.label)}</span>
          <code>{html.escape(glyph.id)}</code>
        </div>
        <div class="glyph-row">
          <div class="glyph-24">{svg}</div>
          <div class="glyph-16">{svg}</div>
        </div>
      </article>"""
        )

    preview = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Signet WS-3 参数化 Glyph 预览</title>
  <style>
    :root {{
      --bg: #f7f4ee;
      --panel: #fffdfa;
      --ink: #17130f;
      --muted: #6b6258;
      --line: #d8d0c5;
      --glyph-color: #17130f;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); }}
    main {{ width: min(1120px, calc(100vw - 32px)); margin: 0 auto; padding: 32px 0 40px; }}
    header {{ display: flex; justify-content: space-between; gap: 24px; align-items: end; border-bottom: 1px solid var(--line); padding-bottom: 18px; margin-bottom: 20px; }}
    h1 {{ margin: 0 0 8px; font-size: 24px; line-height: 1.15; font-weight: 720; letter-spacing: 0; }}
    p {{ margin: 0; max-width: 680px; color: var(--muted); line-height: 1.55; font-size: 14px; }}
    .palette {{ display: flex; gap: 8px; align-items: center; flex-wrap: wrap; justify-content: flex-end; min-width: 220px; }}
    .swatch {{ width: 34px; height: 34px; border-radius: 50%; border: 1px solid var(--line); cursor: pointer; box-shadow: inset 0 0 0 3px var(--panel); }}
    .grid {{ display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 12px; color: var(--glyph-color); }}
    .glyph-card {{ min-height: 116px; border: 1px solid var(--line); border-radius: 8px; background: var(--panel); padding: 12px; display: flex; flex-direction: column; justify-content: space-between; gap: 16px; }}
    .glyph-meta {{ display: flex; justify-content: space-between; gap: 12px; align-items: center; color: var(--ink); font-size: 13px; line-height: 1.25; }}
    code {{ color: var(--muted); font-size: 11px; white-space: nowrap; }}
    .glyph-row {{ display: flex; align-items: center; justify-content: space-between; min-height: 48px; }}
    .glyph-24, .glyph-16 {{ display: grid; place-items: center; width: 48px; height: 48px; border-radius: 8px; background: #f1ece4; }}
    .glyph-24 svg {{ width: 24px; height: 24px; display: block; }}
    .glyph-16 svg {{ width: 16px; height: 16px; display: block; }}
    .glyph-card svg * {{ vector-effect: non-scaling-stroke; }}
    @media (max-width: 980px) {{ .grid {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }} }}
    @media (max-width: 620px) {{ header {{ align-items: start; flex-direction: column; }} .palette {{ justify-content: flex-start; min-width: 0; }} .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>Signet 参数化 glyph 集</h1>
        <p>{len(glyphs)} 个 Signet 自制 SVG glyph，共享 24x24 网格、2px 描边、圆端点/圆拐角和 currentColor 换色。</p>
      </div>
      <nav class="palette" aria-label="调色">
        <button class="swatch" type="button" style="background:#17130f" data-color="#17130f" aria-label="墨色"></button>
        <button class="swatch" type="button" style="background:#0f766e" data-color="#0f766e" aria-label="青绿"></button>
        <button class="swatch" type="button" style="background:#9a3430" data-color="#9a3430" aria-label="赤陶"></button>
      </nav>
    </header>
    <section class="grid" aria-label="参数化 glyph 预览">
{''.join(cards)}
    </section>
  </main>
  <script>
    const root = document.documentElement;
    document.querySelectorAll("[data-color]").forEach((button) => {{
      button.addEventListener("click", () => root.style.setProperty("--glyph-color", button.dataset.color));
    }});
  </script>
</body>
</html>
"""
    preview_path.write_text(preview, encoding="utf-8")


def build_custom(
    output_dir: Path = CUSTOM_DIR,
    manifest_path: Path = CUSTOM_MANIFEST_PATH,
    preview_path: Path = CUSTOM_PREVIEW_PATH,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    glyphs = list(CUSTOM_GLYPHS)
    source_ids = set(UI_ICON_SUBSET)
    overlaps = sorted(glyph.id for glyph in glyphs if glyph.id in source_ids)
    if overlaps:
        raise ValueError(f"custom glyph ids overlap Lucide subset: {', '.join(overlaps)}")

    for glyph in glyphs:
        (output_dir / f"{glyph.id}.svg").write_text(render_glyph(glyph), encoding="utf-8")

    manifest = build_manifest(glyphs, output_dir)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    build_preview(glyphs, output_dir, preview_path)
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Signet custom UI glyphs.")
    parser.add_argument("--out", type=Path, default=CUSTOM_DIR)
    parser.add_argument("--manifest", type=Path, default=CUSTOM_MANIFEST_PATH)
    parser.add_argument("--preview", type=Path, default=CUSTOM_PREVIEW_PATH)
    args = parser.parse_args(argv)

    manifest = build_custom(args.out, args.manifest, args.preview)
    print(f"custom={len(manifest['glyphs'])} out={args.out} manifest={args.manifest} preview={args.preview}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
