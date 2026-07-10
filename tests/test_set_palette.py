"""Set-level palette contract tests."""
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "signet" / "scripts"))

from palette_engine import PaletteResult, build_set_palette, evaluate_set, hex_to_oklch  # noqa: E402


def _all_pass(checks):
    return all(check["pass"] for check in checks)


def test_signature_family_set_passes_contract():
    palettes = build_set_palette(55, 6, "EMBER", "signature-family", seed="sig")
    checks = evaluate_set(palettes, "signature-family")
    assert _all_pass(checks), checks
    hues = [hex_to_oklch(p.roles["primary"])[2] for p in palettes]
    assert max(hues) - min(hues) <= 61
    accent_hues = {round(hex_to_oklch(p.roles["accent"])[2]) for p in palettes}
    assert len(accent_hues) == 1


def test_signature_family_rejects_hue_jumping_set():
    palettes = []
    for i, hue in enumerate([0, 60, 120, 180]):
        roles = {
            "primary": f"#{int(80+i):02X}6688",
            "secondary": "#77AACC",
            "tertiary": "#DDBB66",
            "accent": "#FFDFA8",
            "detail": "#2A1B18",
        }
        # Force primary to the desired hue without depending on RGB literals.
        from palette_engine import oklch_to_hex
        roles["primary"] = oklch_to_hex((0.70, 0.15, hue))
        palettes.append(PaletteResult(roles, {"primary": 60, "secondary": 22, "tertiary": 9, "accent": 4, "detail": 5}, {"fill": "#F6F1E9"}, {}))
    checks = {check["id"]: check for check in evaluate_set(palettes, "signature-family")}
    assert checks["F-SET-1"]["pass"] is False


def test_spectrum_sweep_keeps_v4_mode_available():
    palettes = build_set_palette(55, 8, "EMBER", "spectrum-sweep", seed="sweep")
    checks = evaluate_set(palettes, "spectrum-sweep")
    assert _all_pass(checks), checks
    assert checks[0]["id"] == "F-SET-SPECTRUM"
