#!/usr/bin/env python3
"""Build a merged Signet UI SVG set from themed Lucide and custom glyphs."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import shutil
from pathlib import Path

try:
    import param_engine
    import theme_ui
except ImportError:  # pragma: no cover
    from . import param_engine, theme_ui  # type: ignore


BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def validate_hex(value: str) -> str:
    if not HEX_RE.fullmatch(value):
        raise ValueError(f"expected 6-digit hex color, got {value!r}")
    return value.upper()


def parse_palette(palette_json: str | None, color: str | None) -> dict[str, str]:
    if palette_json:
        palette = json.loads(palette_json)
        if not isinstance(palette, dict):
            raise ValueError("--palette must be a JSON object")
        normalized = {str(role): validate_hex(str(value)) for role, value in palette.items()}
        if not normalized:
            raise ValueError("--palette must not be empty")
        return normalized
    return {"primary": validate_hex(color or "#17130F")}


def run_id_now() -> str:
    return "ui-" + dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def copy_svg(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def inline_svg(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip().replace("<svg ", '<svg aria-hidden="true" ')


def build_index(run_dir: Path, manifest: dict, index_path: Path) -> None:
    cards = []
    for glyph in manifest["glyphs"]:
        svg = inline_svg(run_dir / glyph["file"])
        cards.append(
            f"""
      <article class="glyph-card" data-source="{html.escape(glyph['source'])}">
        <div class="glyph-meta">
          <span>{html.escape(glyph['id'])}</span>
          <code>{html.escape(glyph['source'])} · {html.escape(glyph['license'])}</code>
        </div>
        <div class="glyph-row">
          <div class="glyph-24">{svg}</div>
          <div class="glyph-16">{svg}</div>
        </div>
      </article>"""
        )

    primary = manifest["palette"]["primary"]
    index = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Signet UI SVG 轨道预览</title>
  <style>
    :root {{
      --bg: #f7f4ee;
      --panel: #fffdfa;
      --ink: #17130f;
      --muted: #6b6258;
      --line: #d8d0c5;
      --glyph-color: {primary};
      --signet-ui-color: var(--glyph-color);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); }}
    main {{ width: min(1180px, calc(100vw - 32px)); margin: 0 auto; padding: 32px 0 40px; }}
    header {{ display: flex; justify-content: space-between; gap: 24px; align-items: end; border-bottom: 1px solid var(--line); padding-bottom: 18px; margin-bottom: 20px; }}
    h1 {{ margin: 0 0 8px; font-size: 24px; line-height: 1.15; font-weight: 720; letter-spacing: 0; }}
    p {{ margin: 0; max-width: 760px; color: var(--muted); line-height: 1.55; font-size: 14px; }}
    .palette {{ display: flex; gap: 8px; align-items: center; flex-wrap: wrap; justify-content: flex-end; min-width: 220px; }}
    .swatch {{ width: 34px; height: 34px; border-radius: 50%; border: 1px solid var(--line); cursor: pointer; box-shadow: inset 0 0 0 3px var(--panel); }}
    .grid {{ display: grid; grid-template-columns: repeat(8, minmax(0, 1fr)); gap: 10px; color: var(--glyph-color); }}
    .glyph-card {{ min-height: 108px; border: 1px solid var(--line); border-radius: 8px; background: var(--panel); padding: 10px; display: flex; flex-direction: column; justify-content: space-between; gap: 12px; }}
    .glyph-meta {{ display: flex; flex-direction: column; gap: 4px; color: var(--ink); font-size: 12px; line-height: 1.25; min-width: 0; }}
    .glyph-meta span, code {{ overflow-wrap: anywhere; }}
    code {{ color: var(--muted); font-size: 10px; }}
    .glyph-row {{ display: flex; align-items: center; justify-content: space-between; min-height: 42px; }}
    .glyph-24, .glyph-16 {{ display: grid; place-items: center; width: 42px; height: 42px; border-radius: 8px; background: #f1ece4; }}
    .glyph-24 svg {{ width: 24px; height: 24px; display: block; }}
    .glyph-16 svg {{ width: 16px; height: 16px; display: block; }}
    .glyph-card svg * {{ vector-effect: non-scaling-stroke; }}
    @media (max-width: 1100px) {{ .grid {{ grid-template-columns: repeat(5, minmax(0, 1fr)); }} }}
    @media (max-width: 720px) {{ header {{ align-items: start; flex-direction: column; }} .palette {{ justify-content: flex-start; min-width: 0; }} .grid {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }} }}
    @media (max-width: 460px) {{ main {{ width: min(100vw - 20px, 420px); }} .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>Signet UI SVG 轨道</h1>
        <p>合并集包含 {manifest['counts']['themed']} 个 Lucide themed SVG 和 {manifest['counts']['custom']} 个 Signet custom glyph，共 {manifest['counts']['total']} 个；高频厚库之外的缺口由 param_engine 现场按需生成，不是原创 500 图标大库。</p>
      </div>
      <nav class="palette" aria-label="调色">
        <button class="swatch" type="button" style="background:{primary}" data-color="{primary}" aria-label="主色"></button>
        <button class="swatch" type="button" style="background:#0F766E" data-color="#0F766E" aria-label="青绿"></button>
        <button class="swatch" type="button" style="background:#9A3430" data-color="#9A3430" aria-label="赤陶"></button>
      </nav>
    </header>
    <section class="grid" aria-label="合并 UI glyph 预览">
{''.join(cards)}
    </section>
  </main>
  <script>
    const root = document.documentElement;
    document.querySelectorAll("[data-color]").forEach((button) => {{
      button.addEventListener("click", () => {{
        root.style.setProperty("--glyph-color", button.dataset.color);
        root.style.setProperty("--signet-ui-color", button.dataset.color);
      }});
    }});
  </script>
</body>
</html>
"""
    index_path.write_text(index, encoding="utf-8")


def build_ui_set(
    output_root: Path = DIST_DIR,
    run_id: str | None = None,
    intent: str = "成套 UI 界面图标",
    brand_words: str = "",
    color: str | None = None,
    palette_json: str | None = None,
) -> dict:
    palette = parse_palette(palette_json, color)
    run = run_id or run_id_now()
    run_dir = output_root / run
    themed_dir = run_dir / "themed"
    custom_dir = run_dir / "custom"
    icons_dir = run_dir / "icons"

    theme_manifest_path = run_dir / "theme_manifest.json"
    custom_manifest_path = run_dir / "custom_manifest.json"
    custom_preview_path = run_dir / "custom_preview.html"
    combined_manifest_path = run_dir / "manifest.json"
    index_path = run_dir / "index.html"

    theme_manifest = theme_ui.build_theme(
        output_dir=themed_dir,
        manifest_path=theme_manifest_path,
        color=palette["primary"],
    )
    custom_manifest = param_engine.build_custom(
        output_dir=custom_dir,
        manifest_path=custom_manifest_path,
        preview_path=custom_preview_path,
    )

    glyphs = []
    seen: set[str] = set()
    for glyph in theme_manifest["glyphs"]:
        icon_id = glyph["id"]
        if icon_id in seen:
            raise ValueError(f"duplicate glyph id: {icon_id}")
        seen.add(icon_id)
        source_svg = themed_dir / f"{icon_id}.svg"
        dest_svg = icons_dir / f"{icon_id}.svg"
        copy_svg(source_svg, dest_svg)
        glyphs.append(
            {
                "id": icon_id,
                "source": "lucide-themed",
                "file": str(dest_svg.relative_to(run_dir)),
                "license": glyph["license"],
                "license_notice": glyph["license_notice"],
                "upstream_source_url": glyph["upstream_source_url"],
                "derivative_statement": glyph["derivative_statement"],
            }
        )

    for glyph in custom_manifest["glyphs"]:
        icon_id = glyph["id"]
        if icon_id in seen:
            raise ValueError(f"duplicate glyph id: {icon_id}")
        seen.add(icon_id)
        source_svg = custom_dir / f"{icon_id}.svg"
        dest_svg = icons_dir / f"{icon_id}.svg"
        copy_svg(source_svg, dest_svg)
        glyphs.append(
            {
                "id": icon_id,
                "source": "signet-custom",
                "file": str(dest_svg.relative_to(run_dir)),
                "license": "Apache-2.0",
                "purpose": glyph["purpose"],
                "original_statement": glyph["original_statement"],
            }
        )

    combined = {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "generated_by": "skills/signet/ui/ui_pipeline.py",
        "intent": intent,
        "brand_words": brand_words,
        "palette": palette,
        "token_schema": theme_manifest["token_schema"],
        "counts": {
            "themed": len(theme_manifest["glyphs"]),
            "custom": len(custom_manifest["glyphs"]),
            "total": len(glyphs),
        },
        "license_summary": {
            "lucide": "ISC with Feather-derived MIT notices retained per glyph",
            "signet_custom": "Apache-2.0 self-authored procedural SVG",
        },
        "honest_scope": "固定 permissive Lucide 高频厚库 + Signet 自制参数 glyph；缺口由 param_engine 现场按需生成，不是原创 500 图标大库。",
        "glyphs": glyphs,
    }
    combined_manifest_path.write_text(json.dumps(combined, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    build_index(run_dir, combined, index_path)
    return {
        "run_dir": str(run_dir),
        "manifest": str(combined_manifest_path),
        "index": str(index_path),
        "icons_dir": str(icons_dir),
        "counts": combined["counts"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a merged Signet UI SVG set.")
    parser.add_argument("--intent", default="成套 UI 界面图标")
    parser.add_argument("--brand", default="")
    parser.add_argument("--color", default="#17130F")
    parser.add_argument("--palette", help="Optional JSON object with 5-role hex colors; primary drives SVG color.")
    parser.add_argument("--out", type=Path, default=DIST_DIR)
    parser.add_argument("--run-id")
    args = parser.parse_args(argv)

    result = build_ui_set(
        output_root=args.out,
        run_id=args.run_id,
        intent=args.intent,
        brand_words=args.brand,
        color=args.color,
        palette_json=args.palette,
    )
    counts = result["counts"]
    print(
        f"run={result['run_dir']} themed={counts['themed']} custom={counts['custom']} "
        f"total={counts['total']} manifest={result['manifest']} index={result['index']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
