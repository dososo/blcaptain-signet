# Style YAML Schema

Every style is one file: `styles/<id>.yaml`. The prompt compiler loads it by `id`.
This keeps styles machine-readable, contributable (1 PR = 1 file), and drift-free
(the catalog in `style-system.md` is auto-generated from these).

Required fields:
```yaml
id:                 # kebab-case, matches filename
english_name:
chinese_name:
summary:            # one sentence
visual_dna:         # 3-4 defining visual traits
material:           # {primary, secondary}
shape_language:     # list
lighting:           # {key, accent, shadow}
color_behavior:     # {palette (how brand colors map), background}
composition:        # {framing, safe_area, detail_level}
best_for:           # list of industries/use-cases
not_for:            # list
prompt_fragment:    # reusable positive clause (the heart of the style)
negative_fragment:  # reusable negative clause
batch_consistency_lock:   # invariants reused verbatim across a set
brand_adaptation_rules:   # how to map a Brand Kit onto this style
regeneration_tips:        # what to do when a result fails review
example_subjects:         # 2-3 sample subjects
```
A CI test (`tests/test_style_schema.py`) asserts all 24 files parse and contain every
required field. To add a style: copy an existing YAML, keep the field set, give it an
original name (see `legal-clean-room.md`), and open a PR with DCO sign-off.
