#!/usr/bin/env python3
"""
build_prompt.py — compile ONE product brief + a style YAML into a model-agnostic
image-generation prompt bundle (prompts.md).

Model-agnostic on purpose: the output is plain prompt text usable in Codex, Claude
Code, Midjourney, Recraft, the OpenAI Image API, or any other generator. No API is
called here.

Usage:
  python scripts/build_prompt.py examples/flowpilot.brief.yaml --style prism-gel --out /tmp/flowpilot-prompts.md
  (if --style is omitted, the brief's style_family / style_mix.primary is used)
"""
from __future__ import annotations
import argparse, re, sys
import warnings
from pathlib import Path
try:
    import yaml
except ImportError:
    sys.exit("pip install pyyaml")
from palette_engine import PaletteResult, generate as generate_palette

STYLES_DIR = Path(__file__).resolve().parents[1] / "styles"

LIGHT_MODEL_ENUM = {
    "none-flat",
    "fully-diffuse",
    "recessed-shadow",
    "anisotropic-grain-streak",
    "inter-layer-cast-shadow",
    "occlusion-elevation",
    "discrete-facet-steps",
    "metal-ridge-glint",
    "controlled-specular",
    "layer-refraction",
}
# Historical name kept for downstream imports/tests. Phase B1 relaxes the old
# "glass-only" firewall: these light models are no longer globally forbidden
# outside two whitelist styles. A style must instead justify any shine/glow via
# its own material tell and anti-drift rules.
GLASS_ONLY: set[str] = set()
BANNED_TOKENS = (
    "3d render, octane render, octane, unreal engine, ray-traced, ray tracing, "
    "global illumination, HDRI, cinematic, 8k, hyper-detailed, hyperrealistic, "
    "generic glossy plastic, stock 3D icon, uncontrolled bloom, random glow, "
    "unmotivated chrome, plastic sheen, wet-look everything, dreamy bokeh"
)
GLASS_SAFE_NEG = (
    "uncontrolled bloom, neon glow spill, random rim light, lens flare, "
    "octane, octane render, 3d render, unreal engine, 8k, hyperrealistic, generic AI glossy plastic"
)
ALLOWED_GLASS_STYLE_IDS: set[str] = set()
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
GROUND_MODES = {"white_canvas", "pale_primary_tint", "cream_neutral"}
TRANSPARENT_ALLOWED_ASSET_TYPES = {"sticker", "overlay"}
APP_ICON_NO_ALPHA_ASSET_TYPES = {"app_icon", "app_icon_boxed", "favicon", "thumbnail"}
IMPACT_RUBRIC_KEYS = {
    "R1_palette_roles",
    "R2_dark_anchor",
    "R3_silhouette_weight",
    "R4_quiet_ground",
    "R5_first_glance_read",
}
STAGING_BY_ASSET_TYPE = {
    "app_icon": [
        "Asset staging: app_icon master is a pure white high-key canvas; no alpha; no saturated full-bleed ground.",
        "Subject scale: primary silhouette occupies 82-88% optical live area with even 6-9% margins.",
        "Presentation note: downstream gallery may composite the master onto a quiet pale squircle tile; the model should not render the tile.",
        "Figure-ground pairing: readable dark Detail anchor against high-key subject and quiet tile, never a saturated ground carrying the palette.",
        "Reduction guard: one focal symbol, black-silhouette readable, minimum stroke at least tile/32.",
    ],
    "app_icon_boxed": [
        "Asset staging: boxed app icon uses a white high-key master plus quiet tile presentation downstream; no alpha.",
        "Subject scale: primary silhouette occupies 78-84% optical live area after keyline compensation.",
        "Figure-ground pairing: dark Detail anchor must carry edges, seams, eyes, and tiny marks.",
        "Reduction guard: one focal symbol, black-silhouette readable, minimum stroke at least tile/32.",
    ],
    "sticker": [
        "Asset staging: sticker mode may use transparency; subject scale 40-60%; keep one bold focal subject.",
        "Reduction guard: outline or silhouette must remain readable at 48px.",
    ],
    "overlay": [
        "Asset staging: overlay mode may use transparency; subject scale 40-60%; keep one bold focal subject.",
        "Reduction guard: outline or silhouette must remain readable at 48px.",
    ],
    "favicon": [
        "Asset staging: favicon uses quiet white or pale tile presentation, subject scale 74-84%, and one focal symbol.",
        "Reduction guard: must remain readable at 48px and simplify before downscaling below that.",
    ],
    "thumbnail": [
        "Asset staging: thumbnail uses quiet white or pale tile presentation, subject scale 74-84%, and one focal symbol.",
        "Reduction guard: must remain readable at 48px and simplify before downscaling below that.",
    ],
    "expression_sheet": [
        "Asset staging: expression_sheet is a character system sheet, not an app icon.",
        "Grid: use a consistent 3x4 or 4x3 expression grid with equal cells, identical head scale, and no UI chrome.",
        "Juju liveliness: big eyes at least one quarter of head height, paired catchlights, blush, orange scarf, and varied expressions.",
        "Character lock: only expression and small squash/stretch vary; Bichon silhouette, drooping ears, eye-nose triangle, and scarf stay invariant.",
        "Ground: colored halo or soft tile may sit behind each head; keep the master readable on white and avoid dense props.",
    ],
}

def load_style(style_id: str, _seen: list[str] | None = None) -> dict:
    _seen = _seen or []
    if style_id in _seen:
        sys.exit(f"Style redirect loop detected: {' -> '.join([*_seen, style_id])}")
    _seen.append(style_id)
    p = STYLES_DIR / f"{style_id}.yaml"
    if not p.exists():
        have = ", ".join(sorted(s.stem for s in STYLES_DIR.glob("*.yaml") if not s.name.startswith("_")))
        sys.exit(f"Unknown style '{style_id}'.\nAvailable styles:\n  {have}")
    style = yaml.safe_load(p.read_text(encoding="utf-8"))
    target_id = style.get("redirect_to")
    if not target_id:
        if style.get("deprecated"):
            note = str(style.get("deprecation_note") or "Deprecated style; kept for backward-compatible compilation.")
            if style.get("retired_stub"):
                print(f"style '{style_id}' is deprecated retired-stub; no redirect: {note}", file=sys.stderr)
            else:
                print(f"style '{style_id}' is deprecated; no redirect: {note}", file=sys.stderr)
        return style
    target = load_style(str(target_id), _seen)
    if target.get("redirect_to"):
        sys.exit(f"Style '{style_id}' redirects to deprecated style '{target_id}'")
    if target.get("deprecated"):
        if target.get("retired_stub") and v3(target):
            print(f"style '{style_id}' is deprecated -> using retired stub '{target_id}'", file=sys.stderr)
            return target
        sys.exit(f"Style '{style_id}' redirects to deprecated style '{target_id}'")
    if not v3(target):
        sys.exit(f"Style '{style_id}' redirects to non-v3 style '{target_id}'")
    print(f"style '{style_id}' is deprecated -> using '{target_id}'", file=sys.stderr)
    return target

def load_all_styles(styles_dir: Path = STYLES_DIR) -> list[dict]:
    styles = []
    for p in sorted(styles_dir.glob("*.yaml")):
        if p.name.startswith("_"):
            continue
        styles.append(yaml.safe_load(p.read_text(encoding="utf-8")))
    return styles

def req(brief: dict, key: str):
    if key not in brief or brief[key] in (None, ""):
        sys.exit(f"Brief is missing required field: '{key}'")
    return brief[key]

def palette_line(pal) -> str:
    if isinstance(pal, dict):
        return ", ".join(f"{k}={v}" for k, v in pal.items() if v)
    if isinstance(pal, list):
        return ", ".join(str(c) for c in pal)
    return str(pal)

# Model-agnostic clause that goes INSIDE the image prompt (no tool-specific notes here).
def bg_clause(bg: str) -> str:
    bg = (bg or "tile").lower()
    if bg == "tile":
        return (
            "solid pure white background, isolated subject, no floor, no cast shadow, "
            "no reflection; rounded tile presentation is composed downstream"
        )
    if bg == "transparent":
        return "fully transparent PNG background; the subject floats with a clean anti-aliased edge"
    if bg == "gradient":
        return "a very simple 2-stop gradient background derived from the brand palette; no scenery"
    return "a solid opaque background filling the whole square"

# Guidance for section 7 only — model-specific caveats live here, not in the prompt text.
def bg_note(bg: str) -> str:
    bg = (bg or "tile").lower()
    if bg == "tile":
        return (
            "Tile mode: generate a 1024x1024 opaque white master. Gallery/export tooling may "
            "place it on a quiet squircle tile later; do not ask the image model to render that tile."
        )
    if bg == "transparent":
        return ("Transparent output: request PNG with alpha. Caveat: gpt-image-2 does not support "
                "transparent backgrounds — use gpt-image-1.5/1 (or another tool) when transparency "
                "is required.")
    if bg == "solid":
        return "Opaque, full-bleed background is required for iOS/Android launcher icons."
    return "Simple gradient background; keep it flat enough to stay legible when downscaled."

# Shared constraints injected once by the compiler, so style YAMLs stay pure DNA.
SHARED_CONSTRAINT = ("Single centered subject with generous edge padding, no text and no logo, "
                     "readable as a clear silhouette at 24-32px.")
EDITORIAL_SCENE_CONSTRAINT = (
    "Editorial explanation scene, not an app icon: centered Juju action, small paper props, "
    "semantic handwritten title or labels as physical paper objects only, generous whitespace, "
    "no logo, no UI screenshot, no dense paragraph text."
)
APP_ICON_CONSTRAINT = (
    "Single centered bold subject on a pure white high-key master, no text and no logo, "
    "one focal symbol, readable as a clear silhouette at 48px."
)

CONCEPT_RULES = [
    ("ai_assistant", ("ai", "assistant", "agent", "autopilot", "copilot"),
     "helper device", "generic AI orb, brain logo, random neural swirl"),
    ("workflow", ("workflow", "flow", "pipeline", "automation", "task", "route"),
     "route capsule", "dashboard screenshot, complex flowchart, tiny UI"),
    ("finance", ("finance", "ledger", "billing", "wallet", "money", "vault"),
     "coin talisman", "bank logo, currency mark, excessive gold"),
    ("search", ("search", "find", "query", "explorer", "radar"),
     "lens token", "search box screenshot, generic magnifier only"),
    ("security", ("security", "permission", "auth", "lock", "privacy", "zero-trust"),
     "lock charm", "hacker skull, real lock brand, fear visuals"),
    ("developer_tool", ("api", "deploy", "code", "dev", "monitor", "terminal", "runtime"),
     "blueprint tile", "code screenshot, dense circuit board, fake labels"),
]

def detect_concept(subject: str) -> tuple[str, str, str]:
    text = subject.lower()
    for concept, keys, fallback, avoid in CONCEPT_RULES:
        if any(k in text for k in keys):
            return concept, fallback, avoid
    return "general_product", "single tangible product object", "abstract logo, generic orb, UI screenshot"

def as_list(value) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(v) for v in value if v]
    return [str(value)]

def v2(style: dict) -> bool:
    return isinstance(style.get("visual_recipe"), dict)

def v3(style: dict) -> bool:
    return str(style.get("schema_version", "")).strip() == "3"

def is_glass(style: dict) -> bool:
    return (style.get("material_exclusivity") or {}).get("allows_glass") is True

def recipe(style: dict, *keys, default="") -> str:
    cur = style
    for key in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    if isinstance(cur, list):
        return ", ".join(str(v) for v in cur if v)
    return str(cur) if cur not in (None, "") else default

def _style_id(style: dict) -> str:
    return str(style.get("id") or "<unknown>")

def _fail(style: dict, message: str) -> None:
    sys.exit(f"{message} [{_style_id(style)}]")

def _mapping(style: dict, key: str) -> dict:
    value = style.get(key)
    if not isinstance(value, dict):
        _fail(style, f"{key} must be a mapping")
    return value

def _require_keys(style: dict, block: dict, block_name: str, keys: set[str]) -> None:
    missing = sorted(k for k in keys if k not in block or block[k] in (None, ""))
    if missing:
        _fail(style, f"{block_name} missing required keys: {', '.join(missing)}")

def _format_list(value) -> str:
    return ", ".join(as_list(value))

def _unique(items: list[str]) -> list[str]:
    seen = set()
    out = []
    for item in items:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out

def _is_hex(value) -> bool:
    return isinstance(value, str) and bool(HEX_RE.match(value))

def _require_hex(style: dict, value, field: str) -> None:
    if not _is_hex(value):
        _fail(style, f"{field} must be a #RRGGBB hex color")

def lint_glass_budget(all_styles: list[dict]) -> None:
    for style in all_styles:
        if not v3(style):
            continue
        me = style.get("material_exclusivity") or {}
        if me.get("allows_glass") is True and not str(me.get("exclusive_material", "")).strip():
            _fail(style, "MATERIAL TELL MISSING: allows_glass requires material_exclusivity.exclusive_material")

def lint_light_model(style: dict) -> None:
    if not v3(style):
        return
    me = style.get("material_exclusivity") or {}
    lm = me.get("light_model_enum")
    if lm not in LIGHT_MODEL_ENUM:
        _fail(style, f"LIGHT_MODEL REJECT: '{lm}' not in closed enum {sorted(LIGHT_MODEL_ENUM)}")
    rig = ((style.get("style_recipe") or {}).get("lighting_rig") or {}).get("model_enum")
    if rig is not None and rig != lm:
        _fail(
            style,
            "LIGHT_MODEL DESYNC: "
            f"lighting_rig.model_enum='{rig}' != material_exclusivity.light_model_enum='{lm}'",
        )

def lint_legacy_fields(style: dict) -> None:
    if not v3(style):
        return
    for key in ("id", "english_name", "chinese_name", "summary", "prompt_fragment", "negative_fragment"):
        if style.get(key) in (None, ""):
            _fail(style, f"LEGACY FIELD MISSING: {key}")
    color = style.get("color_behavior")
    if not isinstance(color, dict) or color.get("palette") in (None, ""):
        _fail(style, "LEGACY FIELD MISSING: color_behavior.palette")

def lint_style_recipe(style: dict) -> None:
    if not v3(style):
        return
    sr = _mapping(style, "style_recipe")
    _require_keys(
        style,
        sr,
        "style_recipe",
        {"material_stack", "lighting_rig", "camera", "color_system", "detail_budget", "keyline_block"},
    )
    color = sr.get("color_system") or {}
    max_colors = color.get("max_colors")
    if type(max_colors) is not int or max_colors > 6:
        _fail(style, "style_recipe.color_system.max_colors must be an integer <= 6")
    lint_color_impact(style, color)
    detail = sr.get("detail_budget") or {}
    if "legibility_floor_px" not in detail:
        _fail(style, "style_recipe.detail_budget.legibility_floor_px is required")
    keyline = sr.get("keyline_block") or {}
    _require_keys(style, keyline, "style_recipe.keyline_block", {"canvas_px", "live_area_px", "padding_px", "pixel_snap"})
    for key in ("canvas_px", "live_area_px", "padding_px"):
        if type(keyline.get(key)) is not int:
            _fail(style, f"style_recipe.keyline_block.{key} must be an integer")
    if keyline["live_area_px"] + 2 * keyline["padding_px"] != keyline["canvas_px"]:
        _fail(style, "style_recipe.keyline_block geometry mismatch: live_area_px + 2*padding_px must equal canvas_px")
    if type(keyline.get("pixel_snap")) is not bool:
        _fail(style, "style_recipe.keyline_block.pixel_snap must be boolean")
    camera = sr.get("camera") or {}
    safe_area = camera.get("safe_area_pct")
    if not isinstance(safe_area, (int, float)) or not 78 <= safe_area <= 90:
        _fail(style, "style_recipe.camera.safe_area_pct must be in [78, 90]")
    rig = sr.get("lighting_rig") or {}
    me = style.get("material_exclusivity") or {}
    if rig.get("model_enum") is not None and rig.get("model_enum") != me.get("light_model_enum"):
        _fail(style, "style_recipe.lighting_rig.model_enum must equal material_exclusivity.light_model_enum")

def lint_color_impact(style: dict, color: dict) -> None:
    if not v3(style):
        return
    fixed_6a_keys = {"hero", "supports", "branded_ground", "accent", "require_saturated_colors"}
    present = sorted(fixed_6a_keys & set(color))
    if present:
        _fail(style, f"PHASE 7A COLOR MODEL REJECT: remove fixed 6a color keys: {', '.join(present)}")
    dumped = yaml.safe_dump(color, allow_unicode=True)
    hexes = HEX_RE.findall(dumped)
    if hexes:
        _fail(style, f"PHASE 7A COLOR MODEL REJECT: style color_system must not contain fixed hex roles: {', '.join(hexes)}")
    chroma_min = color.get("chroma_min")
    if chroma_min is not None and (type(chroma_min) is not int or chroma_min < 0):
        _fail(style, "style_recipe.color_system.chroma_min must be a non-negative integer when present")

def lint_character_dna(style: dict) -> None:
    if not v3(style):
        return
    cd = _mapping(style, "character_dna")
    fit = cd.get("character_fit")
    if fit not in {"native", "capable", "object-only"}:
        _fail(style, "character_dna.character_fit must be native, capable, or object-only")
    if not cd.get("ref"):
        _fail(style, "character_dna.ref is required")
    if not isinstance(cd.get("silhouette_invariants"), list) or not cd["silhouette_invariants"]:
        _fail(style, "character_dna.silhouette_invariants must be a non-empty list")
    if not isinstance(cd.get("forbidden_drift"), list) or not cd["forbidden_drift"]:
        _fail(style, "character_dna.forbidden_drift must be a non-empty list")
    face = cd.get("face_geometry") or {}
    if not (cd.get("eye_nose_triangle") or face.get("eye_nose_triangle")):
        _fail(style, "character_dna.face_geometry.eye_nose_triangle is required")

def lint_anti_drift(style: dict) -> None:
    if not v3(style):
        return
    drift = _mapping(style, "anti_style_drift")
    if not as_list(drift.get("per_style_negatives")):
        _fail(style, "anti_style_drift.per_style_negatives is required")
    is_vs = drift.get("is_vs_is_not")
    if not isinstance(is_vs, dict) or not is_vs.get("is") or not is_vs.get("is_not"):
        _fail(style, "anti_style_drift.is_vs_is_not requires is and is_not")
    if not drift.get("default_gloss_guard"):
        _fail(style, "anti_style_drift.default_gloss_guard is required")

def lint_thumbnail(style: dict) -> None:
    if not v3(style):
        return
    t = _mapping(style, "thumbnail_first_rules")
    min_size = t.get("min_size_px")
    survives = t.get("detail_survives_downscale_to")
    if type(min_size) is not int:
        _fail(style, "thumbnail_first_rules.min_size_px must be an integer")
    if type(t.get("contact_sheet_64px_pass")) is not bool:
        _fail(style, "thumbnail_first_rules.contact_sheet_64px_pass must be boolean")
    if survives is not None:
        if type(survives) is not int:
            _fail(style, "thumbnail_first_rules.detail_survives_downscale_to must be an integer")
        if survives > min_size:
            warnings.warn(
                f"thumbnail_first_rules.detail_survives_downscale_to > min_size_px [{_style_id(style)}]",
                RuntimeWarning,
            )

def lint_batch_lock(style: dict) -> None:
    if not v3(style):
        return
    lock = _mapping(style, "batch_consistency_lock")
    _require_keys(style, lock, "batch_consistency_lock", {"camera", "lighting", "material", "palette", "safe_area"})

def lint_reference_policy(style: dict) -> None:
    if not v3(style):
        return
    rp = _mapping(style, "reference_policy")
    if not rp.get("clean_room_boundary"):
        _fail(style, "reference_policy.clean_room_boundary is required")
    if rp.get("no_third_party_names") is not True:
        _fail(style, "reference_policy.no_third_party_names must be true")
    if rp.get("no_copied_prompts_or_images") is not True:
        _fail(style, "reference_policy.no_copied_prompts_or_images must be true")

def lint_impact_rubric(style: dict) -> None:
    if not v3(style):
        return
    rubric = _mapping(style, "human_review_rubric")
    missing = sorted(k for k in IMPACT_RUBRIC_KEYS if not str(rubric.get(k, "")).strip())
    if missing:
        _fail(style, f"human_review_rubric missing Phase 7a R1-R5 keys: {', '.join(missing)}")
    required_phrases = {
        "R1_palette_roles": ["3 roles", "55-70"],
        "R2_dark_anchor": ["40", "50"],
        "R3_silhouette_weight": ["tile/32", "82-88"],
        "R4_quiet_ground": ["white", "no alpha"],
        "R5_first_glance_read": ["48px"],
    }
    for key, phrases in required_phrases.items():
        text = str(rubric.get(key, ""))
        for phrase in phrases:
            if phrase not in text:
                _fail(style, f"human_review_rubric.{key} must mention {phrase}")

def lint_compiler_style(style: dict) -> None:
    if not v3(style):
        return
    lint_legacy_fields(style)
    lint_light_model(style)
    lint_style_recipe(style)
    lint_character_dna(style)
    lint_anti_drift(style)
    lint_thumbnail(style)
    lint_batch_lock(style)
    lint_reference_policy(style)
    lint_impact_rubric(style)

def object_decision(subject: str, style: dict) -> dict:
    concept, fallback, avoid = detect_concept(subject)
    oa = style.get("object_archetype") or {}
    chosen = oa.get("default") if isinstance(oa, dict) else None
    forbidden = ", ".join(as_list(oa.get("forbidden"))) if isinstance(oa, dict) else ""
    preferred = ", ".join(as_list(oa.get("preferred"))) if isinstance(oa, dict) else ""
    return {
        "concept": concept,
        "chosen": chosen or fallback,
        "preferred": preferred or fallback,
        "avoid": forbidden or avoid,
        "why": f"'{subject}' should read as a named physical object before any style effect.",
    }

def material_lock(style: dict) -> str:
    if v3(style):
        ms = (style.get("style_recipe") or {}).get("material_stack") or {}
        me = style.get("material_exclusivity") or {}
        parts = [
            f"base: {ms.get('base') or recipe(style, 'visual_recipe', 'material_stack', 'base')}",
            f"edge: {ms.get('edge') or recipe(style, 'visual_recipe', 'material_stack', 'edge')}",
            f"inner: {ms.get('inner_detail') or recipe(style, 'visual_recipe', 'material_stack', 'inner_detail')}",
            f"finish: {ms.get('finish') or recipe(style, 'visual_recipe', 'material_stack', 'finish')}",
        ]
        if me.get("exclusive_material"):
            parts.append(f"exclusive material: {me['exclusive_material']}")
        if me.get("imperfection_injection"):
            parts.append(f"imperfection: {me['imperfection_injection']}")
        return "; ".join(p for p in parts if p and not p.endswith(": "))
    if v2(style):
        return "; ".join([
            f"base: {recipe(style, 'visual_recipe', 'material_stack', 'base')}",
            f"edge: {recipe(style, 'visual_recipe', 'material_stack', 'edge')}",
            f"inner: {recipe(style, 'visual_recipe', 'material_stack', 'inner_detail')}",
            f"finish: {recipe(style, 'visual_recipe', 'material_stack', 'finish')}",
        ])
    return f"primary: {style['material']['primary']}; secondary: {style['material'].get('secondary', '')}"

def lighting_lock(style: dict) -> str:
    if v3(style):
        rig = (style.get("style_recipe") or {}).get("lighting_rig") or {}
        me = style.get("material_exclusivity") or {}
        parts = [
            f"light-model: {me.get('light_model_enum', '')}",
            f"key: {rig.get('key') or recipe(style, 'visual_recipe', 'lighting_rig', 'key')}",
            f"rim: {rig.get('rim') or recipe(style, 'visual_recipe', 'lighting_rig', 'rim')}",
            f"shadow: {rig.get('shadow') or recipe(style, 'visual_recipe', 'lighting_rig', 'shadow')}",
        ]
        return "; ".join(p for p in parts if p and not p.endswith(": "))
    if v2(style):
        return "; ".join([
            f"key: {recipe(style, 'visual_recipe', 'lighting_rig', 'key')}",
            f"rim: {recipe(style, 'visual_recipe', 'lighting_rig', 'rim')}",
            f"shadow: {recipe(style, 'visual_recipe', 'lighting_rig', 'shadow')}",
        ])
    return f"key: {style['lighting']['key']}; accent: {style['lighting'].get('accent', '')}; shadow: {style['lighting'].get('shadow', '')}"

def camera_lock(style: dict) -> str:
    if v3(style):
        camera = (style.get("style_recipe") or {}).get("camera") or {}
        parts = [
            f"angle: {camera.get('angle') or recipe(style, 'visual_recipe', 'camera', 'angle')}",
            f"projection: {camera.get('projection') or recipe(style, 'visual_recipe', 'camera', 'projection')}",
            f"crop: {camera.get('crop') or recipe(style, 'visual_recipe', 'camera', 'crop')}",
        ]
        if camera.get("safe_area_pct") not in (None, ""):
            parts.append(f"safe-area: {camera['safe_area_pct']}%")
        return "; ".join(p for p in parts if p and not p.endswith(": "))
    if v2(style):
        return "; ".join([
            f"angle: {recipe(style, 'visual_recipe', 'camera', 'angle')}",
            f"projection: {recipe(style, 'visual_recipe', 'camera', 'projection')}",
            f"crop: {recipe(style, 'visual_recipe', 'camera', 'crop')}",
        ])
    return "identical camera angle across the set; centered product-style render"

def composition_lock(style: dict) -> str:
    if v3(style):
        sr = style.get("style_recipe") or {}
        sep = style.get("style_separation_lock") or {}
        camera = sr.get("camera") or {}
        edge = sr.get("edge_quality") or {}
        parts = [
            sep.get("silhouette_rule") or style.get("silhouette_rule"),
            f"safe-area {camera.get('safe_area_pct')}%" if camera.get("safe_area_pct") not in (None, "") else "",
            edge.get("outline") or recipe(style, "visual_recipe", "edge_quality", "outline"),
        ]
        return "; ".join(p for p in parts if p)
    safe_area = recipe(style, "batch_lock", "safe_area") if v2(style) else style["composition"]["safe_area"]
    parts = [style.get("silhouette_rule") or style["composition"]["framing"], safe_area]
    if v2(style):
        parts.append(recipe(style, "visual_recipe", "edge_quality", "outline"))
    return "; ".join(p for p in parts if p)

def detail_budget_lines(style: dict) -> list[str]:
    if v3(style):
        detail = ((style.get("style_recipe") or {}).get("detail_budget") or {})
        lines = [
            f"- Macro: {detail.get('macro', 'one dominant silhouette')}",
            f"- Mid: {detail.get('mid', 'one readable secondary cue')}",
            f"- Micro: {detail.get('micro', 'remove inner detail before it clutters at 24px')}",
        ]
        if detail.get("legibility_floor_px") not in (None, ""):
            lines.append(f"- Legibility floor: {detail['legibility_floor_px']}px")
        return lines
    if v2(style):
        return [
            f"- Macro: {recipe(style, 'visual_recipe', 'detail_budget', 'macro')}",
            f"- Mid: {recipe(style, 'visual_recipe', 'detail_budget', 'mid')}",
            f"- Micro: {recipe(style, 'visual_recipe', 'detail_budget', 'micro')}",
        ]
    return [
        f"- Macro: one dominant silhouette",
        f"- Mid: {style['composition']['detail_level']}",
        "- Micro: remove inner detail before it clutters at 24px.",
    ]

def thumbnail_lines(style: dict) -> list[str]:
    if v3(style):
        t = style.get("thumbnail_first_rules") or {}
        return [
            f"- Minimum size: {t.get('min_size_px', 24)}px",
            f"- Grayscale test: {t.get('grayscale_test', 'subject remains readable without brand color')}",
            f"- Silhouette test: {t.get('silhouette_test', 'one dominant silhouette is nameable')}",
            f"- 64px contact-sheet: {'must pass separability' if t.get('contact_sheet_64px_pass') else 'n/a'}",
            f"- Detail survives downscale to: {t.get('detail_survives_downscale_to', 24)}px",
        ]
    tr = style.get("thumbnail_rules") if isinstance(style.get("thumbnail_rules"), dict) else {}
    return [
        f"- Minimum size: {tr.get('min_size', '24-32px')}",
        f"- Grayscale test: {tr.get('grayscale_test', 'subject remains readable without brand color')}",
        f"- Silhouette test: {tr.get('silhouette_test', 'one dominant silhouette is nameable')}",
    ]

def negative_prompt(style: dict, avoid: list[str]) -> str:
    patterns = as_list(style.get("anti_taste_patterns"))
    if v3(style) and not patterns:
        patterns = as_list((style.get("anti_style_drift") or {}).get("anti_taste_patterns"))
    neg = style["negative_fragment"].strip()
    editorial = style.get("_asset_type") == "editorial_scene"
    if editorial:
        for phrase in (
            "text, letters, numbers, readable handwriting, ",
            "text, letters, numbers, ",
            "readable handwriting, ",
        ):
            neg = neg.replace(phrase, "")
    if patterns:
        neg += " Avoid these taste failures: " + ", ".join(patterns) + "."
    if v3(style):
        neg += " Shared generic-AI-look negative anchors: " + BANNED_TOKENS + "."
        if is_glass(style):
            neg += " Even for authorized shine, forbid: " + GLASS_SAFE_NEG + "."
        per_style = as_list((style.get("anti_style_drift") or {}).get("per_style_negatives"))
        if editorial:
            per_style = [item for item in per_style if item != "no readable handwritten words"]
        if per_style:
            neg += " Per-style negatives: " + ", ".join(per_style) + "."
        forbidden = _unique(
            as_list((style.get("material_exclusivity") or {}).get("forbidden_finish"))
            + as_list(((style.get("style_recipe") or {}).get("lighting_rig") or {}).get("forbidden_lighting"))
        )
        if forbidden:
            neg += " Material and lighting forbidden tokens: " + ", ".join(forbidden) + "."
        drift = as_list((style.get("character_dna") or {}).get("forbidden_drift"))
        if drift:
            neg += " Character drift to avoid: " + ", ".join(drift) + "."
        if editorial:
            rules = (style.get("character_dna") or {}).get("annotation_rules") or {}
            forbidden_annotations = as_list(rules.get("forbid") if isinstance(rules, dict) else [])
            scarf_rule = (style.get("character_dna") or {}).get("scarf_text_rule")
            extra = forbidden_annotations
            if scarf_rule:
                extra.append(f"scarf text drift: {scarf_rule}")
            if extra:
                neg += " Editorial annotation drift to avoid: " + ", ".join(extra) + "."
    if avoid:
        neg += " Also avoid: " + ", ".join(avoid) + "."
    return neg

def batch_lock_lines(style: dict, palette: PaletteResult | None = None) -> list[str]:
    if v3(style):
        lock = style.get("batch_consistency_lock") or {}
        if isinstance(lock, dict):
            lines = [f"- {k}: {v}" for k, v in lock.items()]
        else:
            lines = [f"- {r}" for r in as_list(lock)]
        if palette:
            role_text = ", ".join(f"{role}={palette.roles[role]}" for role in ("primary", "secondary", "tertiary", "accent", "detail"))
            lines.append(f"- palette_engine_roles: {role_text}")
            lines.append(f"- palette_seed: {palette.report.get('seed')}")
        return lines
    lock = style.get("batch_lock")
    if isinstance(lock, dict):
        return [f"- {k}: {v}" for k, v in lock.items()]
    return [f"- {r}" for r in style.get("batch_consistency_lock", [])]

def regeneration_lines(style: dict) -> list[str]:
    reg = style.get("regeneration_strategy")
    if isinstance(reg, dict):
        return [f"- {k}: {v}" for k, v in reg.items()]
    return [f"- {t}" for t in style.get("regeneration_tips", [])]

def keyline_lines(style: dict) -> list[str]:
    if not v3(style):
        return []
    keyline = ((style.get("style_recipe") or {}).get("keyline_block") or {})
    labels = [
        ("canvas_px", "Canvas"),
        ("live_area_px", "Live area"),
        ("padding_px", "Padding"),
        ("stroke_px", "Stroke"),
        ("corner_radius_px", "Corner radius"),
        ("min_gap_px", "Minimum gap"),
        ("pixel_snap", "Pixel snap"),
    ]
    return [f"- {label}: {keyline[key]}" for key, label in labels if key in keyline]

def color_impact_lines(style: dict, palette: PaletteResult | None = None) -> list[str]:
    if not (v3(style) and palette):
        return []
    roles = palette.roles
    areas = palette.areas
    checks = ", ".join(f"{c['id']}={'PASS' if c.get('pass') else 'REVIEW'}" for c in palette.report.get("floor_checks", []))
    repairs = "; ".join(palette.report.get("repairs") or [])
    warnings_text = "; ".join(palette.report.get("warnings") or [])
    tile = palette.tile
    ground_label = "quiet ground"
    if str(palette.report.get("palette_family", "")).lower() == "vivid":
        ground_label = "colored presentation ground"
    return [
        f"- Role palette: primary {roles['primary']}, secondary {roles['secondary']}, tertiary {roles['tertiary']}, accent {roles['accent']}, detail {roles['detail']}.",
        f"- Area hierarchy: primary {areas['primary']}% / secondary {areas['secondary']}% / tertiary {areas['tertiary']}% / accent {areas['accent']}% / detail {areas['detail']}%; color lives on the subject and at least 3 roles must be visible.",
        f"- {ground_label}: generation canvas is pure white; presentation tile may use {tile.get('fill')} as {tile.get('mode', 'presentation')} downstream; tile color must stay secondary to the subject.",
        "- High-key light language: soft wraparound brightness, no floor shadow, no contact shadow, no cast shadow; depth comes from material self-shading and part overlap only.",
        "- Detail anchor: the darkest marks are the generated detail role only, used for seams, eyes, stitches, linework, and small structural edges.",
        "- Contrast repair rule: if readability fails, deepen the Detail anchor or enlarge tertiary structure; never pour saturation into the ground.",
        f"- Palette report: seed {palette.report.get('seed')}; template {palette.report.get('template_id')}; floor checks {checks}.",
        *([f"- Palette repairs: {repairs}."] if repairs else []),
        *([f"- Palette warnings: {warnings_text}."] if warnings_text else []),
    ]

def staging_lines(style: dict, brief: dict) -> list[str]:
    if not v3(style):
        return []
    atype = brief.get("asset_type", "app_icon")
    return STAGING_BY_ASSET_TYPE.get(str(atype), [])

def color_impact_prompt_clause(lines: list[str]) -> str:
    if not lines:
        return ""
    cleaned = [line[2:] if line.startswith("- ") else line for line in lines]
    return "Color-impact lock: " + " ".join(cleaned)

def staging_prompt_clause(lines: list[str]) -> str:
    if not lines:
        return ""
    cleaned = [line[2:] if line.startswith("- ") else line for line in lines]
    return "Staging lock: " + " ".join(cleaned)

def effective_background(style: dict, asset_type: str, bg: str) -> str:
    if not v3(style):
        return bg
    atype = str(asset_type or "app_icon")
    if atype in APP_ICON_NO_ALPHA_ASSET_TYPES:
        return "tile"
    if atype in TRANSPARENT_ALLOWED_ASSET_TYPES:
        return bg
    return bg

def palette_for_prompt(pal, bg: str):
    if isinstance(pal, dict):
        out = dict(pal)
        out["background"] = bg
        return out
    return pal

def character_block(style: dict, brief: dict) -> str:
    if not (v3(style) and brief.get("render_character")):
        return ""
    cd = style.get("character_dna") or {}
    invariants = _format_list(cd.get("silhouette_invariants"))
    face = cd.get("face_geometry") or {}
    marks = _format_list(cd.get("identity_marks"))
    free = _format_list(cd.get("free_variables"))
    block = (
        f"Character DNA lock: render {cd.get('ref', 'the character')} as {cd.get('species', 'the mascot')}; "
        f"role: {cd.get('role', 'guide')}; character-fit: {cd.get('character_fit', 'capable')}; "
        f"silhouette invariants: {invariants}; face geometry: {face.get('eye_nose_triangle', 'eye-nose triangle must remain readable')}; "
        f"identity marks: {marks}; allowed free variables: {free}."
    )
    if brief.get("asset_type") == "editorial_scene":
        annotation = cd.get("annotation_rules") or {}
        if isinstance(annotation, dict):
            text_objects = _format_list(annotation.get("text_as_object"))
            forbid = _format_list(annotation.get("forbid"))
            semantic = annotation.get("semantic_rule") or annotation.get("semantic_not_decorative")
            if semantic or text_objects or forbid:
                block += (
                    f" Annotation rules: {semantic or 'semantic annotations only'}; "
                    f"text as objects: {text_objects}; forbid: {forbid}."
                )
        if cd.get("scarf_text_rule"):
            block += f" Scarf text rule: {cd['scarf_text_rule']}."
        if cd.get("variation_rule"):
            block += f" Variation rule: {cd['variation_rule']}."
        anchors = _format_list(cd.get("composition_anchors"))
        if anchors:
            block += f" Composition anchors allowed: {anchors}."
    if brief.get("asset_type") == "expression_sheet" or cd.get("liveliness_spec"):
        if cd.get("home_material"):
            block += f" Home material: {cd['home_material']}."
        live = cd.get("liveliness_spec") or {}
        if isinstance(live, dict):
            eyes = live.get("eyes") or {}
            expressions = _format_list(live.get("expression_set"))
            poses = _format_list(live.get("dynamic_pose_library"))
            white = live.get("white_body_coloring")
            ground = live.get("colored_halo_ground")
            if eyes:
                block += " Liveliness eyes: " + ", ".join(f"{k}={v}" for k, v in eyes.items()) + "."
            if expressions:
                block += f" Expression set: {expressions}."
            if poses:
                block += f" Dynamic pose library: {poses}."
            if white:
                block += f" White-body coloring rule: {white}."
            if ground:
                block += f" Colored halo ground: {ground}."
    return block

def editorial_scene_lines(style: dict, brief: dict) -> list[str]:
    if not (v3(style) and brief.get("asset_type") == "editorial_scene"):
        return []
    cd = style.get("character_dna") or {}
    anchors = _format_list(cd.get("composition_anchors")) or "center, thirds, diagonal, frame"
    ratio = brief.get("aspect_ratio", "3:4 or 16:9")
    return [
        "- Scene mode: editorial_scene, not app_icon.",
        f"- Canvas ratio: {ratio}.",
        "- Center action: anchor Juju as the main actor doing one clear explaining gesture.",
        "- Props: add small paper notes, tags, cards, or arrows only when they clarify the idea.",
        "- Semantic annotations: green, blue, or orange bubbles and arrows must point to real scene objects; they are not decorative noise.",
        "- Text objects: short handwritten title, sticky note, paper label, or arrow callout may appear as physical objects.",
        "- Whitespace: keep generous paper-world breathing room around the action.",
        "- Optional off-canvas guide: one partial hand, pencil, or arrow may guide attention from outside the frame.",
        "- Material baseline: use draft-line paper-world character DNA for Juju unless a brief explicitly overrides material.",
        f"- Composition anchors: {anchors}.",
    ]

def editorial_scene_prompt_clause(lines: list[str]) -> str:
    if not lines:
        return ""
    cleaned = [line[2:] if line.startswith("- ") else line for line in lines]
    return "Editorial scene composition lock: " + " ".join(cleaned)

def separation_block(style: dict) -> list[str]:
    if not v3(style):
        return []
    sep = style.get("style_separation_lock") or {}
    lines = []
    if sep.get("namable_archetype"):
        lines.append(f"- Archetype: {sep['namable_archetype']}")
    if sep.get("orthogonality_axis"):
        lines.append(f"- Orthogonality axis: {sep['orthogonality_axis']}")
    if sep.get("silhouette_rule"):
        lines.append(f"- Separation silhouette: {sep['silhouette_rule']}")
    return lines

def review_block(style: dict) -> list[str]:
    if not v3(style):
        return []
    lines = []
    rubric = style.get("human_review_rubric") or {}
    for key, value in rubric.items():
        lines.append(f"- {key}: {value}")
    sep = style.get("style_separation_lock") or {}
    for neighbor in as_list(sep.get("must_differ_from")):
        lines.append(f"- Must differ: {neighbor}")
    return lines

def reference_policy_line(style: dict) -> str | None:
    if not v3(style):
        return None
    rp = style.get("reference_policy") or {}
    line = "- Clean-room: " + str(
        rp.get("clean_room_boundary", "learn public principles only; no third-party names/prompts/images; original naming")
    )
    if rp.get("no_third_party_names"):
        line += " [names original]"
    return line

def compile_prompt(brief: dict, style: dict) -> str:
    if v3(style):
        lint_compiler_style(style)
    subj   = req(brief, "icon_subject")
    proj   = brief.get("project_name", "the product")
    words  = ", ".join(brief.get("brand_words", [])) or "clear, modern"
    pal    = brief.get("color_palette", {})
    avoid  = brief.get("avoid", [])
    mix    = brief.get("style_mix")
    atype  = brief.get("asset_type", "app_icon")
    palette_brief = dict(brief)
    if v3(style):
        color_system = ((style.get("style_recipe") or {}).get("color_system") or {})
        family = color_system.get("palette_family")
        if family:
            pal_source = palette_brief.get("color_palette")
            if isinstance(pal_source, dict):
                pal_source = dict(pal_source)
                pal_source.setdefault("palette_family", family)
                palette_brief["color_palette"] = pal_source
            else:
                palette_brief["palette_family"] = family
    palette_result = generate_palette(palette_brief) if v3(style) else None
    default_bg = "tile" if v3(style) and str(atype or "app_icon") in APP_ICON_NO_ALPHA_ASSET_TYPES else "transparent"
    bg     = (pal.get("background") if isinstance(pal, dict) else None) or brief.get("background", default_bg)
    bg     = effective_background(style, atype, bg)
    prompt_pal = palette_result.prompt_palette(bg) if palette_result else palette_for_prompt(pal, bg)
    decision = object_decision(subj, style)
    editorial_lines = editorial_scene_lines(style, brief)
    impact_lines = color_impact_lines(style, palette_result)
    staging = staging_lines(style, brief)
    if editorial_lines:
        shared_constraint = EDITORIAL_SCENE_CONSTRAINT
    elif v3(style) and atype == "app_icon":
        shared_constraint = APP_ICON_CONSTRAINT
    else:
        shared_constraint = SHARED_CONSTRAINT
    palette_label = "the generated role palette" if v3(style) else "the brand palette"

    mix_note = ""
    if mix and mix.get("secondary") and mix.get("secondary") != style["id"]:
        sec = load_style(mix["secondary"])
        ratio = mix.get("ratio", "80/20")
        mix_note = (f"\nStyle mix ({ratio}): keep **{style['english_name']}** as the dominant "
                    f"material/surface; borrow only the *composition/motif* cues of "
                    f"**{sec['english_name']}** ({', '.join(sec.get('visual_dna', [])[:2])}). "
                    f"Do not blend the two materials — one surface wins.")

    prompt = (
        f"A single {atype.replace('_',' ')} for {proj}, representing '{subj}' as {decision['chosen']}. "
        f"Mood: {words}. Style — {style['english_name']} ({style['chinese_name']}"
        f"{' / ' + style.get('recipe_alias') if style.get('recipe_alias') else ''}): "
        f"{style['prompt_fragment'].strip()} Material lock: {material_lock(style)}. "
        f"Composition lock: {composition_lock(style)}. Lighting lock: {lighting_lock(style)}. "
        f"Camera lock: {camera_lock(style)}. Use only {palette_label} ({palette_line(prompt_pal)}); "
        f"{style['color_behavior']['palette']}. Background: {bg_clause(bg)}. {shared_constraint}"
    )
    color_clause = color_impact_prompt_clause(impact_lines)
    if color_clause:
        prompt += " " + color_clause
    staging_clause = staging_prompt_clause(staging)
    if staging_clause:
        prompt += " " + staging_clause
    editorial_clause = editorial_scene_prompt_clause(editorial_lines)
    if editorial_clause:
        prompt += " " + editorial_clause
    char = character_block(style, brief)
    if char:
        prompt += " " + char

    negative_style = dict(style)
    if editorial_lines:
        negative_style["_asset_type"] = "editorial_scene"
    neg = negative_prompt(negative_style, avoid)
    keyline = keyline_lines(style)
    ref_line = reference_policy_line(style)
    review_basics = [
        "- recognizable at 24-32px  ·  no text/letters  ·  no fake logo  ·  no trademark lookalike",
        "- named object before style effect  ·  credible material  ·  controlled lighting  ·  not over-detailed",
        "- no watermark  ·  no UI screenshot  ·  centered silhouette  ·  on-brand palette  ·  not a stock icon",
    ]
    if editorial_lines:
        review_basics = [
            "- editorial scene reads clearly at target aspect ratio  ·  no fake logo  ·  no trademark lookalike",
            "- handwritten title or labels must be physical paper objects, not UI text or large subtitles",
            "- no watermark  ·  no UI screenshot  ·  clear Juju action  ·  semantic annotations point to real objects",
        ]

    lines = [
        f"# Prompt bundle — {proj}",
        "",
        "## 1. Project summary",
        f"- Subject: {subj}",
        f"- Asset type: {atype}",
        f"- Audience: {brief.get('audience','(unspecified)')}",
        f"- Platforms: {', '.join(brief.get('platforms', [])) or '(unspecified)'}",
        f"- Brand words: {words}",
        "",
        "## 2. Selected style",
        f"- **{style['english_name']} / {style['chinese_name']}** (`{style['id']}`)",
        f"- Why: {style['summary'].strip()}",
        *separation_block(style),
        f"- Best for: {', '.join(style.get('best_for', []))}",
        f"- Not for: {', '.join(style.get('not_for', []))}" + mix_note,
        "",
        "## 3. Object archetype decision",
        f"- Concept: {decision['concept']}",
        f"- Chosen object: {decision['chosen']}",
        f"- Preferred objects: {decision['preferred']}",
        f"- Why: {decision['why']}",
        f"- Avoid: {decision['avoid']}",
        "",
        "## 4. Creative direction brief",
        f"- Positioning: {recipe(style, 'positioning', 'one_liner', default=style['summary'].strip())}",
        f"- Material lock: {material_lock(style)}",
        f"- Composition lock: {composition_lock(style)}",
        f"- Lighting lock: {lighting_lock(style)}",
        f"- Camera lock: {camera_lock(style)}",
        "",
        *(["## 4b. Editorial scene composition", "", *editorial_lines, ""] if editorial_lines else []),
        *(
            [
                f"## 4c. Palette (engine-generated, seed {palette_result.report.get('seed')})",
                "",
                *impact_lines,
                *staging,
                "",
            ]
            if (palette_result and (impact_lines or staging))
            else []
        ),
        "## 5. Image generation prompt",
        "",
        prompt,
        "",
        "## 6. Anti-taste negative prompt",
        "",
        neg,
        "",
        "## 7. Brand consistency rules",
        *[f"- {r}" for r in style.get("brand_adaptation_rules", [])],
        "",
        "## 8. Detail budget",
        *detail_budget_lines(style),
        "",
        *(["## 8b. Keyline / pixel grid", "", *keyline, ""] if keyline else []),
        "## 9. Thumbnail-first rules",
        *thumbnail_lines(style),
        "",
        "## 10. Background notes",
        f"- {bg_note(bg)}",
        "",
        "## 11. Batch consistency lock (reuse verbatim across a set)",
        *batch_lock_lines(style, palette_result),
        "",
        "## 12. Regeneration strategy (if it fails review)",
        *regeneration_lines(style),
        "",
        "## 13. Human review checklist",
        *review_basics,
        *review_block(style),
        *([ref_line] if ref_line else []),
        "",
        "## 14. Platform notes",
        "- Generate a 1024×1024 master, then run export_icon_assets.py for all sizes.",
        "- iOS/Android launcher icons must be opaque & full-bleed; favicon/web/Android-foreground can be transparent.",
        f"- Example subjects in this style: {', '.join(style.get('example_subjects', []))}",
    ]
    return "\n".join(lines) + "\n"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brief")
    ap.add_argument("--style", help="style id (overrides brief.style_family)")
    ap.add_argument("--out")
    a = ap.parse_args()
    brief = yaml.safe_load(Path(a.brief).read_text(encoding="utf-8"))
    style_id = a.style or brief.get("style_family") or (brief.get("style_mix") or {}).get("primary")
    if not style_id:
        sys.exit("No style given: pass --style or set style_family/style_mix.primary in the brief")
    style = load_style(style_id)
    lint_glass_budget(load_all_styles())
    text = compile_prompt(brief, style)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8"); print(f"wrote {a.out}")
    else:
        print(text)

if __name__ == "__main__":
    main()
