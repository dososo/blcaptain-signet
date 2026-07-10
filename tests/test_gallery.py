"""Premium gallery renderer tests."""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "signet" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from gallery import GALLERY_TOKENS, render_contact_sheet, safe_gallery_ground  # noqa: E402
from palette_engine import hex_to_oklch  # noqa: E402
from taste_laws import mud_box_hex  # noqa: E402


def _icon(color):
    im = Image.new("RGBA", (256, 256), (255, 255, 255, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([42, 42, 214, 214], radius=42, fill=color)
    return im


def _master(path: Path):
    im = Image.new("RGBA", (1024, 1024), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([160, 160, 864, 864], radius=180, fill=(40, 120, 220, 255))
    im.save(path)


def test_gallery_tokens_are_self_consistent():
    assert 3 <= len(GALLERY_TOKENS["shadow"]["layers"]) <= 5
    assert 16 <= GALLERY_TOKENS["grid"]["tile_gap"] <= 24
    assert 16 <= GALLERY_TOKENS["grid"]["tile_radius"] <= 24
    _, C, _ = hex_to_oklch(GALLERY_TOKENS["ground"]["dark"])
    assert C <= 0.06
    assert not mud_box_hex(GALLERY_TOKENS["ground"]["dark"])


def test_render_contact_sheet_uses_premium_ground(tmp_path):
    out = tmp_path / "sheet.png"
    render_contact_sheet([("one", _icon((220, 80, 60, 255))), ("two", _icon((60, 160, 220, 255))), ("three", _icon((80, 190, 120, 255)))], out, cols=3)
    im = Image.open(out).convert("RGB")
    assert im.size[0] > 0 and im.size[1] > 0
    assert im.getpixel((4, 4)) != (245, 245, 247)
    assert im.getpixel((4, 4)) != (255, 255, 255)


def test_gallery_ground_guardrail_rejects_warm_muddy_dark():
    assert safe_gallery_ground("#6B4A2A", "dark") == GALLERY_TOKENS["ground"]["dark_cool"]


def test_exporter_still_writes_preview_png(tmp_path):
    master = tmp_path / "m.png"
    _master(master)
    out = tmp_path / "dist"
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "export_icon_assets.py"), str(master), "--out", str(out), "--name", "T"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (out / "T" / "preview.png").exists()
