## Summary

- What changed:
- Why it is needed:

## Style Evidence

- Style ID:
- Contact sheet at 64px / 32px / 16px:
- Full-resolution samples:
- Nearest neighboring styles and how this differs:

## Gate Evidence

Paste command output or link artifacts:

```text
python -m pytest -q
python skills/signet/ui/repo_license_gate.py
python skills/signet/scripts/preflight_icon_set.py path/to/generated/*.png --json
```

Checklist:

- [ ] 64px silhouette is readable.
- [ ] Material tell is visible without reading the style name.
- [ ] Figure-ground contrast is WCAG >= 3 or APCA >= 60 where measured.
- [ ] Output avoids generic glossy plastic.
- [ ] GROUND LAW passed.
- [ ] MUD_BOX did not appear in presentation grounds.
- [ ] No fake logo, wordmark, embedded text, or trademark lookalike.

## Clean-Room Statement

- [ ] This PR does not copy third-party prompts, images, screenshots, style names, or compositions.
- [ ] All naming, recipes, prompts, and references are original to this contribution.

## License Note

- [ ] I understand that accepted contributions are provided under Apache-2.0.
