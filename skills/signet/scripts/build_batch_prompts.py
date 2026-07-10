#!/usr/bin/env python3
"""
build_batch_prompts.py — compile a batch brief (many icons, one style) into a set of
per-icon prompts that share one global lock (style/palette/lighting/material/perspective).

Consistency comes from reusing the SAME lock block byte-for-byte in every prompt; that
is where hand-written sets drift.

Usage:
  python scripts/build_batch_prompts.py examples/devpulse.batch.yaml --style blueprint-grid --out /tmp/devpulse-batch-prompts.md
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path
try:
    import yaml
except ImportError:
    sys.exit("pip install pyyaml")

from build_prompt import (
    batch_lock_lines,
    camera_lock,
    character_block,
    composition_lock,
    detail_budget_lines,
    effective_background,
    keyline_lines,
    lint_compiler_style,
    lint_glass_budget,
    load_all_styles,
    load_style,
    lighting_lock,
    material_lock,
    negative_prompt,
    object_decision,
    reference_policy_line,
    regeneration_lines,
    review_block,
    thumbnail_lines,
    v3,
)
from palette_engine import generate as generate_palette

def palette_line(pal):
    if isinstance(pal, dict):
        return ", ".join(f"{k}={v}" for k, v in pal.items() if v)
    if isinstance(pal, list):
        return ", ".join(map(str, pal))
    return str(pal)

def bg_instr(bg):
    bg = (bg or "tile").lower()
    return ("solid pure white master background; quiet squircle tile is composed downstream" if bg == "tile"
            else "fully transparent PNG background" if bg == "transparent"
            else "solid opaque background filling the square" if bg == "solid"
            else "a very simple 2-stop brand gradient background")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brief")
    ap.add_argument("--style")
    ap.add_argument("--out")
    a = ap.parse_args()
    b = yaml.safe_load(Path(a.brief).read_text(encoding="utf-8"))
    sid = a.style or b.get("style_family")
    if not sid:
        sys.exit("No style: pass --style or set style_family in the brief")
    if "icons" not in b or not b["icons"]:
        sys.exit("Batch brief needs a non-empty 'icons:' list")
    style = load_style(sid)
    lint_glass_budget(load_all_styles())
    lint_compiler_style(style)

    proj = b.get("project_name", "the product")
    words = ", ".join(b.get("brand_words", [])) or "clear, modern"
    pal = b.get("color_palette", {})
    palette_result = generate_palette(b) if v3(style) else None
    default_bg = "tile" if v3(style) else "transparent"
    bg = (pal.get("background") if isinstance(pal, dict) else None) or b.get("background", default_bg)
    bg = effective_background(style, "app_icon", bg)
    prompt_pal = palette_result.prompt_palette(bg) if palette_result else pal
    avoid = b.get("avoid", [])
    palette_label = "generated role palette" if v3(style) else "palette"

    lock = (f"STYLE: {style['english_name']} ({style['id']}"
            f"{' / ' + style.get('recipe_alias') if style.get('recipe_alias') else ''}) — "
            f"{style['prompt_fragment'].strip()} "
            f"MATERIAL: {material_lock(style)}. "
            f"LIGHTING: {lighting_lock(style)}. "
            f"CAMERA: {camera_lock(style)}. "
            f"PALETTE: only {palette_label} {palette_line(prompt_pal)}; {style['color_behavior']['palette']}. "
            f"BACKGROUND: {bg_instr(bg)} (same for all). "
            f"COMPOSITION: {composition_lock(style)}.")
    character_note = character_block(style, b)
    if character_note:
        lock += " " + character_note
    neg = negative_prompt(style, avoid)
    keyline = keyline_lines(style)
    ref_line = reference_policy_line(style)
    decisions = [(subj, object_decision(str(subj), style)) for subj in b["icons"]]

    out = [f"# Batch prompt set — {proj}", "",
           f"Style: **{style['english_name']} / {style['chinese_name']}** (`{style['id']}`)  ·  "
           f"{len(b['icons'])} icons  ·  mood: {words}", "",
           "## Global locks (global style lock / palette lock / lighting-material-perspective-composition lock)", "",
           f"> {lock}", "",
           "### Set-level lock details", "",
           f"- Material lock: {material_lock(style)}",
           f"- Composition lock: {composition_lock(style)}",
           f"- Lighting lock: {lighting_lock(style)}",
           f"- Camera lock: {camera_lock(style)}",
           *batch_lock_lines(style, palette_result),
           "",
           "## Object archetype decisions", "",
           "| Subject | Concept | Object archetype | Avoid |",
           "|---|---|---|---|"]
    for subj, dec in decisions:
        out.append(f"| {subj} | {dec['concept']} | {dec['chosen']} | {dec['avoid']} |")
    out += ["",
           "## Global negative (identical in every prompt)", "",
           f"> {neg}", "",
           "## Detail budget", "",
           *detail_budget_lines(style),
           "",
           *(["## Keyline / pixel grid", "", *keyline, ""] if keyline else []),
           "## Thumbnail-first rules", "",
           *thumbnail_lines(style),
           ""]
    for i, (subj, dec) in enumerate(decisions, 1):
        p = (f"A single feature icon representing '{subj}' as {dec['chosen']} for {proj}. Mood: {words}. {lock} "
             f"It must belong to the same set as its siblings (same material, light, palette, camera).")
        out += [f"### {i}. {subj}", "",
                f"Object archetype decision: {dec['concept']} -> {dec['chosen']}. Avoid: {dec['avoid']}.", "",
                "**Prompt**", "", p, "",
                "**Negative prompt**", "", neg, "", "---", ""]
    out += ["## Consistency repair prompt (for outliers)", "",
            "Regenerate ONLY the mismatched icon, pasting the Global locks above verbatim and adding: "
            "\"match the exact material finish, key-light direction, palette and camera of the other "
            "icons in this set; do not introduce new colors or a new light direction.\"", "",
            "## Regeneration strategy", "",
            *regeneration_lines(style),
            "",
            "## Set-level human review checklist", "",
            "- all icons read at 24-32px  ·  same material & light across the set  ·  one shared palette",
            "- each subject has a named object archetype  ·  no generic orb/logo/dashboard screenshot",
            "- no text/logo/watermark/UI in any icon  ·  each subject is unmistakable  ·  no outlier style",
            *review_block(style),
            *([ref_line] if ref_line else [])]
    text = "\n".join(out) + "\n"
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8"); print(f"wrote {a.out} ({len(b['icons'])} icons)")
    else:
        print(text)

if __name__ == "__main__":
    main()
