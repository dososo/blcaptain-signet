#!/usr/bin/env python3
"""
Signet — preflight_icon_set.py
Heuristic, auditable PRE-SCREEN for generated icons. This is NOT a QA pass and NOT an
aesthetic or trademark guarantee — human review is ALWAYS required. It only flags obvious,
machine-checkable problems before export.

It scores the machine-checkable subset of the QA rubric (see references/qa-rubric.md):
  - small-size legibility proxy   (contrast retained after downscale to 24px)
  - composition centering         (alpha centroid vs geometric centre)
  - safe-area compliance          (share of visible content inside central 80%)
  - background handling           (transparent vs opaque, as requested)
  - palette discipline            (distinct-colour count after quantisation)
  - set consistency               (pairwise palette distance across the batch)

Everything subjective (metaphor accuracy, "looks like a fake logo", brand fit,
trademark risk, embedded text) is DELIBERATELY out of scope and flagged for a human.
It is a pre-screen for obvious failures, never a quality/aesthetic/legal guarantee.

Usage:
  python3 preflight_icon_set.py icon1.png icon2.png ...  [--want-transparent] [--json]
"""
from __future__ import annotations
import argparse, json, sys, math
from pathlib import Path
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
try:
    from PIL import Image
except ImportError:
    sys.exit("pip install Pillow")
from build_prompt import lint_glass_budget, load_all_styles

def load(p):  return Image.open(p).convert("RGBA")

def contrast_retained(im):
    """Proxy for small-size legibility: std-dev of luminance at 24px, 0..1."""
    small = im.convert("L").resize((24, 24), Image.LANCZOS)
    px = list(small.getdata())
    n = len(px); mean = sum(px) / n
    var = sum((v - mean) ** 2 for v in px) / n
    return min(1.0, (var ** 0.5) / 80.0)  # ~80 std ≈ strong contrast

def alpha_or_luma_mask(im):
    a = im.getchannel("A")
    if a.getextrema()[0] < 255:      # real transparency -> use alpha
        return a, True
    # opaque: treat non-background pixels as content via luma deviation from corners
    g = im.convert("L"); return g, False

def centering(im):
    mask, transparent = alpha_or_luma_mask(im)
    w, h = mask.size; px = mask.load()
    tot = sx = sy = 0
    for y in range(0, h, 4):
        for x in range(0, w, 4):
            v = px[x, y] if transparent else abs(px[x, y] - px[0, 0])
            if v > 20:
                tot += v; sx += x * v; sy += y * v
    if tot == 0: return 0.0, 0.0
    cx, cy = sx / tot, sy / tot
    off = math.hypot(cx - w / 2, cy - h / 2) / (w / 2)
    return max(0.0, 1 - off), off

def safe_area(im, frac=0.8):
    mask, transparent = alpha_or_luma_mask(im)
    w, h = mask.size; px = mask.load()
    m = int(w * (1 - frac) / 2)
    inside = total = 0
    for y in range(0, h, 4):
        for x in range(0, w, 4):
            v = px[x, y] if transparent else abs(px[x, y] - px[0, 0])
            if v > 20:
                total += 1
                if m <= x <= w - m and m <= y <= h - m: inside += 1
    return (inside / total) if total else 1.0

def palette_count(im, k=16):
    q = im.convert("RGB").resize((64, 64)).quantize(colors=k)
    counts = q.convert("RGB").getcolors(64 * 64) or []
    sig = [c for n, c in sorted(counts, reverse=True) if n > 40]  # ignore stray
    return len(sig), sig[:6]

def palette_dist(a, b):
    if not a or not b: return 1.0
    def near(c, pal): return min(sum((c[i]-p[i])**2 for i in range(3)) for p in pal) ** 0.5
    d = sum(near(c, b) for c in a) / len(a)
    return min(1.0, d / 442.0)  # 442 = max rgb distance

def score_one(im, want_transparent):
    leg, _ = contrast_retained(im), None
    cen, off = centering(im)
    safe = safe_area(im)
    _, transparent = alpha_or_luma_mask(im)
    npal, pal = palette_count(im)
    bg_ok = (transparent == want_transparent)
    pal_score = 1.0 if npal <= 6 else max(0.0, 1 - (npal - 6) / 10)
    parts = {
        "legibility_24px": round(leg, 2),
        "centering": round(cen, 2),
        "safe_area_80": round(safe, 2),
        "background_ok": bg_ok,
        "palette_colors": npal,
    }
    weighted = (leg*0.30 + cen*0.20 + safe*0.20 + (1.0 if bg_ok else 0.0)*0.15 + pal_score*0.15)
    return round(weighted * 100), parts, pal

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("icons", nargs="+")
    ap.add_argument("--want-transparent", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    lint_glass_budget(load_all_styles())

    results, palettes = [], []
    for p in a.icons:
        s, parts, pal = score_one(load(p), a.want_transparent)
        palettes.append(pal); results.append((Path(p).name, s, parts))

    # set consistency: mean pairwise palette closeness
    consistency = 1.0
    if len(palettes) > 1:
        ds = [1 - palette_dist(palettes[i], palettes[j])
              for i in range(len(palettes)) for j in range(i+1, len(palettes))]
        consistency = round(sum(ds)/len(ds), 2)

    scores = [s for _, s, _ in results]
    bg_fail = any(not c["background_ok"] for _, _, c in results)
    if bg_fail or min(scores) < 40:
        status = "BLOCKING_EXPORT_ISSUE"   # wrong background, or unreadable — fix before export
    elif min(scores) < 70 or consistency < 0.6:
        status = "AUTO_PREFLIGHT_REVIEW"    # passable but needs a human look
    else:
        status = "AUTO_PREFLIGHT_OK"        # machine-checkable rows look fine; still needs human review

    out = {"icons": [{"file": f, "auto_prescreen": s, "checks": c} for f, s, c in results],
           "set_consistency": consistency,
           "preflight_status": status,
           "human_review_required": True,   # ALWAYS — this tool cannot judge taste/metaphor/trademark
           "human_review_items": [
               "visual metaphor accuracy", "no fake logo / wordmark",
               "trademark & lookalike risk", "no embedded text",
               "brand palette match", "style-family fidelity"]}
    if a.json:
        print(json.dumps(out, indent=2, ensure_ascii=False)); return
    print(f"\nSignet preflight — auto pre-screen only, human review required")
    print(f"  status: {status}   set consistency: {consistency}")
    for r in out["icons"]:
        print(f"  {r['file']:<28} pre-screen {r['auto_prescreen']:>3}/100  {r['checks']}")
    print("  A human must still verify:", ", ".join(out["human_review_items"]))

if __name__ == "__main__":
    main()
