"""Platform completeness tests for HarmonyOS and tvOS export targets."""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "signet" / "scripts"


def _master(path: Path):
    im = Image.new("RGBA", (1024, 1024), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([170, 170, 854, 854], radius=190, fill=(238, 120, 58, 255))
    d.ellipse([390, 330, 634, 574], fill=(45, 30, 75, 255))
    im.save(path)


def _run_export(master: Path, out: Path, platforms: str):
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "export_icon_assets.py"),
            str(master),
            "--out",
            str(out),
            "--name",
            "T",
            "--platforms",
            platforms,
            "--brand-primary",
            "#EE7A43",
            "--ground-tier",
            "near-black",
            "--brand-tile-platforms",
        ],
        capture_output=True,
        text=True,
    )


def _alpha_bbox_size(path: Path) -> tuple[int, int]:
    alpha = Image.open(path).convert("RGBA").getchannel("A")
    bbox = alpha.getbbox()
    assert bbox is not None
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def test_harmonyos_exports_layered_icon_contract(tmp_path):
    master = tmp_path / "m.png"
    _master(master)
    out = tmp_path / "dist"
    result = _run_export(master, out, "harmonyos")
    assert result.returncode == 0, result.stderr

    base = out / "T" / "harmonyos"
    fg = Image.open(base / "foreground.png")
    bg = Image.open(base / "background.png")
    assert fg.size == (1024, 1024)
    assert fg.mode == "RGBA"
    assert fg.getchannel("A").getextrema()[0] < 255
    assert max(_alpha_bbox_size(base / "foreground.png")) in range(448, 453)
    assert bg.size == (1024, 1024)
    assert bg.mode == "RGB"
    data = json.loads((base / "layered_image.json").read_text())
    assert data["layered-image"]["background"] == "$media:background"
    assert data["layered-image"]["foreground"] == "$media:foreground"
    assert (base / "README_HARMONYOS.txt").exists()


def test_tvos_exports_parallax_layers_and_store_icon(tmp_path):
    master = tmp_path / "m.png"
    _master(master)
    out = tmp_path / "dist"
    result = _run_export(master, out, "tvos")
    assert result.returncode == 0, result.stderr

    base = out / "T" / "tvos"
    layer_files = list(base.glob("*x/layer*.png"))
    assert len(layer_files) >= 2
    assert Image.open(base / "1x" / "layer0_back.png").size == (400, 240)
    assert Image.open(base / "2x" / "layer1_graphic.png").size == (800, 480)
    assert Image.open(base / "AppStore-1280x768.png").size == (1280, 768)
    assert Image.open(base / "TopShelf-1920x720.png").size == (1920, 720)
    assert Image.open(base / "TopShelfWide-2320x720.png").size == (2320, 720)
    assert (base / "README_TVOS.txt").exists()


def test_default_platforms_do_not_emit_new_targets(tmp_path):
    master = tmp_path / "m.png"
    _master(master)
    out = tmp_path / "dist"
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "export_icon_assets.py"), str(master), "--out", str(out), "--name", "T"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    base = out / "T"
    for platform in ("web", "pwa", "ios", "macos", "android", "social"):
        assert (base / platform).exists()
    assert not (base / "harmonyos").exists()
    assert not (base / "tvos").exists()
