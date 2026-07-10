# Contributing To Signet

Signet is a clean-room visual identity system. Contributions should make the system more ownable, more verifiable, or easier to ship without weakening the locked design contract.

## Clean-Room Rules

- Do not copy third-party prompts, screenshots, compositions, style names, or reference boards.
- Do not submit lookalikes of an existing product, brand, icon pack, font, or visual system.
- New style names must be original kebab-case IDs.
- Reference material can describe a craft process or material behavior, but it must not reproduce a third-party visual identity.

## Adding A Style YAML

Add styles under:

```text
skills/signet/styles/<style-id>.yaml
```

The public schema source of truth is:

```text
skills/signet/references/style-schema.md
```

Required authoring blocks include `positioning`, `character_dna`, `style_recipe`, `style_separation_lock`, `material_exclusivity`, `anti_style_drift`, `thumbnail_first_rules`, `batch_consistency_lock`, `human_review_rubric`, `reference_policy`, `regeneration_strategy`, `prompt_fragment`, and `negative_fragment`.

Every style must state what it is made of, not just how it feels. The material tell must survive at 64px.

## Machine Gates

Before opening a PR, run:

```bash
python -m pytest -q
python skills/signet/ui/repo_license_gate.py
python skills/signet/scripts/preflight_icon_set.py path/to/generated/*.png --json
```

`taste_laws.py` is currently an imported gate module, not a standalone CLI. Its checks are exercised by `tests/test_ground_law.py`, `tests/test_set_palette.py`, and by exports that derive tile or platform grounds through `export_icon_assets.py`.

The required gates are:

- Silhouette remains readable at 64px, with 32px and 16px contact-sheet evidence.
- The material tell is visible without relying on the style name.
- Figure-ground contrast passes WCAG >= 3 or APCA >= 60 where measured.
- The output does not collapse into generic glossy plastic.
- GROUND LAW passes for presentation grounds.
- MUD_BOX is a hard reject; muddy warm middle-value grounds must not ship.
- Human review still checks metaphor accuracy, no fake logos or wordmarks, trademark risk, embedded text, brand palette match, and style fidelity.

## PR Requirements

Each style PR must include:

- The new or changed YAML file.
- A 64px / 32px / 16px contact sheet.
- The command output from `preflight_icon_set.py`.
- Evidence that taste laws ran, either targeted pytest output or an export manifest showing derived ground guards.
- At least one full-resolution sample so reviewers can inspect first-eye quality.
- A short note explaining how the style differs from its nearest neighbors on material, edge behavior, and texture signature.

## License

Signet is licensed under Apache-2.0. Contributions submitted to this repository are accepted under Apache-2.0 unless a separate written agreement says otherwise.

Launch-facing PRs should not describe the license as undecided or split by content type.

## Development Notes

- Use `python`, not `python3`, if your local `python3` does not have `pyyaml` and `Pillow`.
- Do not change compiler contracts, gate scripts, or the public style schema in a style PR unless the PR is explicitly scoped as a contract change.
- Keep docs honest: Signet compiles prompts and exports assets; image generation still happens in the user's model.
