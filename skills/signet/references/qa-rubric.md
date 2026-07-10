# QA Rubric — 100 points

A pre-screen, not a guarantee. `scripts/preflight_icon_set.py` auto-checks the
machine-checkable rows and returns `AUTO_PREFLIGHT_OK` / `AUTO_PREFLIGHT_REVIEW` /
`BLOCKING_EXPORT_ISSUE`; **human review is always required** for the rest. Ship only when
the human rows below pass too. Any failed must-pass row = regenerate.

| # | Dimension | Weight | Auto? | Pass criterion | Must-pass |
|---|-----------|:-----:|:-----:|----------------|:--------:|
| 1 | Small-size legibility (24px) | 18 | ✅ heuristic | Clear silhouette at 24×24; contrast retained | ✅ |
| 2 | Visual-metaphor accuracy | 14 | ❌ | Subject is recognizable & correct | ✅ |
| 3 | Style-family fidelity | 8 | ⚠️ partial | Matches chosen family's material/light | |
| 4 | Brand consistency (palette) | 10 | ✅ | Uses only brand palette; ≤6 colors | ✅ |
| 5 | Set consistency | 8 | ✅ | Siblings share palette/light/perspective | ✅ (sets) |
| 6 | Composition centering | 6 | ✅ | Subject centered within tolerance | |
| 7 | App-icon safe area | 6 | ✅ | Content within central 80–90% | ✅ (app icons) |
| 8 | Background handling | 6 | ✅ | Transparent OR opaque exactly as required | ✅ |
| 9 | Multi-size export quality | 4 | ✅ | No artifacts/halos after downscale | |
| 10 | Accessibility (contrast, non-hue) | 4 | ⚠️ partial | ≥3:1 vs bg; meaning not hue-only | |
| 11 | No trademark lookalike | 4 | ❌ | Doesn't imitate a real logo | ✅ |
| 12 | No embedded text/wordmark | 4 | ⚠️ OCR optional | Zero letters/words in the icon | ✅ |
| 13 | No fake logo/UI/watermark | 4 | ❌ | Not a pseudo-logo, no UI chrome, no watermark | ✅ |
| 14 | Detail restraint | 2 | ⚠️ | Not over-detailed; survives shrink | |
| 15 | No wrong/broken symbols | 2 | ❌ | No malformed glyphs/artifacts | |
| | **Total** | **100** | | | |

## Automation status (what the scorer really does)
- **Fully auto (heuristic):** 1 (contrast-at-24px proxy), 4 (quantized color count),
  5 (pairwise palette distance), 6 (alpha/luma centroid), 7 (content-in-safe-area),
  8 (alpha presence vs requested), 9 (downscale sanity).
- **Partial / optional:** 3 (family fidelity — hard; treat as human), 10 (contrast
  math is auto, "meaning not hue-only" is human), 12 (add an OCR pass, e.g. Tesseract,
  to auto-flag text; still confirm by eye).
- **Human-only:** 2, 11, 13, 15 — semantic judgments a heuristic cannot make reliably.

Be honest about this in output: the auto-score screens obvious failures; it does **not**
certify metaphor correctness, taste, or trademark safety.

## Human review questions (ask these every time)
1. Would a stranger name the subject correctly in under 2 seconds?
2. At 24px on a busy home screen, does it still stand out?
3. Does it look like it belongs to the same family as its siblings?
4. Does it accidentally resemble any real company's logo?
5. Is there any letter, number, or word baked in? (There must not be.)
6. Does it read in the monochrome fallback?
7. Would a professional designer ship this, or does it look "AI-generated"?

## Low-score repair strategy
- **Fails #1 (small-size):** remove inner detail, thicken forms, increase figure/ground
  contrast, enlarge the subject within the frame. Repair prompt adds:
  *"simplify to a bold silhouette that is unmistakable at 24px; remove fine detail."*
- **Fails #4/#5 (consistency):** re-run the batch builder so the lock block is identical;
  regenerate the outliers only, reusing the exact lock.
- **Fails #2 (metaphor):** swap to a more literal object, or add one unambiguous cue.
  Repair prompt: *"make the '<subject>' reading unmistakable; prefer a single clear object."*
- **Fails #11/#12/#13 (logo/text/trademark):** regenerate with stronger negatives:
  *"no text, no letters, no wordmark, no existing brand logo, no UI, no watermark."*
- After ≥2 failed repairs on the same icon, change **style family** (some subjects don't
  survive a given material) rather than re-rolling endlessly.
