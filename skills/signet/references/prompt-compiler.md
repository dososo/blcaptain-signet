# Prompt Compiler

Turns a structured brief + a style YAML into a model-agnostic prompt bundle.
Single icon → `scripts/build_prompt.py`. A set → `scripts/build_batch_prompts.py`
(reuses one lock so the set can't drift). Styles live in `styles/*.yaml`; the compiler
loads a style by id and injects the shared constraints, so each YAML stays pure DNA.

## Input schema (YAML) — `color_palette` is a dict (recommended)
```yaml
project_name:  FlowPilot
asset_type:    app_icon        # app_icon | feature_icon | feature_icon_set | hero_object | empty_state | marketing_visual | social_visual | editorial_scene
aspect_ratio:  "3:4"           # optional; mainly for editorial_scene, may also be "16:9"
icon_subject:  calm AI workflow autopilot     # or: icons: [a, b, c] for a set
brand_words:   [calm, precise, intelligent]
audience:      indie SaaS founders
platforms:     [web, ios, android, pwa]
style_family:  prism-gel       # any id in styles/
render_character: false        # bool; only v3 styles with character_dna emit Character DNA lock when true
style_mix:                     # EXPERIMENTAL — see note below
  primary:   prism-gel
  secondary: blueprint-grid
  ratio:     80/20
color_palette:                 # dict form is the recommended schema
  primary:    "#6D7CFF"
  secondary:  "#8BE9D4"
  accent:     "#FFD166"
  background: transparent      # transparent | solid | gradient
avoid: [text, letters, fake logo, brand lookalike, watermark, UI screenshot]
```
(A bare list `color_palette: ["#6D7CFF", "#8BE9D4"]` is also accepted, but the dict form
is preferred because it names primary/secondary/accent/background explicitly.)

## Output `prompts.md` sections
1. Project summary  2. Selected style (+ why)  3. Image generation prompt
4. Negative prompt  5. Brand consistency rules  6. Small-size legibility rules
7. Background instruction (model caveats live HERE, not in the prompt text)
8. Batch consistency lock  9. Regeneration prompt  10. Human review checklist
11. Platform notes

The compiler injects one shared constraint into ordinary icon prompts —
*"single centered subject, generous edge padding, no text, no logo, legible at 24-32px"* —
so it never has to be repeated inside each style YAML. `asset_type: editorial_scene` is the exception: it emits a v3-only scene composition block for Juju explanation scenes and allows short handwritten labels as physical paper objects, not UI text.

## editorial_scene
Use this asset type for 3:4 or 16:9 explanatory scenes rather than app icons. The compiler adds a v3-gated `## 4b. Editorial scene composition` section and an image-prompt scene lock: centered Juju action, small paper props, green/blue/orange semantic bubbles and arrows, short handwritten title or paper labels, generous whitespace, and optional off-canvas guidance. It is intended for `draft-line` with `render_character: true`.

## style_mix (EXPERIMENTAL)
Partial support. Rule: **primary controls material, lighting, and color behavior;
secondary contributes only a composition/motif cue.** Never blend two full material
systems — one surface wins. The compiler currently borrows the secondary style's top
visual-DNA cues only; treat richer blending as future work.

## Commands
```bash
python scripts/build_prompt.py examples/flowpilot.brief.yaml --style prism-gel --out prompts.md
python scripts/build_batch_prompts.py examples/devpulse.batch.yaml --style blueprint-grid --out batch.md
```

## Worked examples (all use current styles)
- **Transparent web spot icon** — `--style prism-gel`, `background: transparent`.
- **Opaque iOS app icon** — `--style jade-lens`, `background: solid` (see examples/ledgerfox.brief.yaml).
- **Friendly consumer icon** — `--style foam-object` (see examples/kidnest.brief.yaml).
- **Fintech feature set** — `build_batch_prompts.py --style blueprint-grid` over a 6-icon list
  (see examples/devpulse.batch.yaml); every icon shares the locked palette/material/lighting/camera.
