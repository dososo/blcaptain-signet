# Brand Kit Schema

Fill a Brand Kit once per product, then LOCK the palette/material/lighting so every
icon in the set is consistent. Store as `brand.yaml` (or JSON). Only `primary_color`,
`mood_words`, and `background_mode` are required; the rest have safe defaults.

```yaml
brand:
  name: FlowPilot
  primary_color:   "#3B6FF5"
  secondary_color: "#0E1116"
  accent_color:    "#7B61FF"
  neutral_colors:  ["#F5F7FF", "#9AA3B2", "#0E1116"]
  forbidden_colors: ["#FF0000"]        # colors that clash with brand/accessibility
  mood_words:      [calm, precise, intelligent]
  typography_reference: "Geometric sans (for marketing only — icons are text-free)"
  identity_goal: "warm, calm, and distinct at product-icon scale"
  visual_metaphor: "a steady hand guiding flow"
  cultural_constraints: "avoid red/white funeral connotations in CN market"
  accessibility:
    min_contrast_ratio: 3.0            # icon vs its background
    color_blind_safe: true             # don't encode meaning in hue alone
  modes:
    light_mode_bg:  "#FFFFFF"
    dark_mode_bg:   "#0E1116"
    monochrome_fallback: "#0E1116"     # single-color version must still read
  constraints:
    app_store_safe_area: 0.90          # keep content within central 90%
    small_size_target_px: 24           # must be legible here
    no_text: true
    no_trademark_lookalike: true
locks:                                 # copied verbatim into every prompt in the set
  style_family: luminous-paper
  material: "soft matte paper with subtle edge light"
  lighting: "single soft top-left key light, gentle ambient fill"
  perspective: "front-on, slight 8-degree top-down tilt"
  background: transparent
```

## Locking rules
- Once a set starts, **never change** `locks.*` mid-set — regenerate the whole set instead.
- Provide BOTH light and dark background test renders; an icon that only works on one
  background fails preflight.
- A **monochrome fallback** must remain recognizable (used in favicons, notifications,
  print). If the metaphor dies in one color, simplify it.
- `no_text` and `no_trademark_lookalike` are non-negotiable (see legal-clean-room.md).
