"""Smoke tests for the export + scoring pipeline. Run: pytest -q"""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "signet" / "scripts"

def _master(p):
    im = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([160,160,864,864], radius=180, fill=(20,160,150,255))
    d.ellipse([420,300,604,484], fill=(255,255,255,255))
    im.save(p)

def _opaque_master(p):
    im = Image.new("RGBA", (1024, 1024), (238, 241, 232, 255))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([170, 170, 854, 854], radius=190, fill=(20, 160, 150, 255))
    d.ellipse([420, 320, 604, 504], fill=(45, 30, 75, 255))
    im.save(p)

def _alpha_bbox_size(path):
    alpha = Image.open(path).convert("RGBA").getchannel("A")
    bbox = alpha.getbbox()
    assert bbox is not None
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def _has_true_alpha(path):
    im = Image.open(path).convert("RGBA")
    return im.getchannel("A").getextrema()[0] < 255

def _content_bbox_size_rgb(path):
    im = Image.open(path).convert("RGB")
    bg = im.getpixel((0, 0))
    diff = Image.new("L", im.size, 0)
    src = im.load()
    dst = diff.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            px = src[x, y]
            if max(abs(px[i] - bg[i]) for i in range(3)) > 3:
                dst[x, y] = 255
    bbox = diff.getbbox()
    assert bbox is not None
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def test_export_produces_all_platforms(tmp_path):
    m = tmp_path / "m.png"; _master(m)
    out = tmp_path / "dist"
    r = subprocess.run([sys.executable, str(SCRIPTS/"export_icon_assets.py"), str(m),
        "--out", str(out), "--name", "T", "--platforms",
        "web,pwa,ios,macos,android,watchos,windows,social", "--ios-bg", "#0E1116",
        "--brand-primary", "#EA5B89", "--tile-mode", "saturated-sibling",
        "--brand-tile-platforms", "--seed", "test-seed"], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    base = out / "T"
    manifest = json.loads((base/"export-manifest.json").read_text())
    assert manifest["source_master"].endswith("m.png")
    assert manifest["seed"] == "test-seed"
    assert manifest["tile"]["corner_radius_pct"] == 0.2237
    assert manifest["tile"]["corner_smoothing"] == 0.60
    assert manifest["tile"]["superellipse_n"] == 5
    assert manifest["tile"]["guards"]["tile_chroma_lt_subject"] is True
    assert manifest["tile"]["guards"]["tile_hue_outside_primary_12deg"] is True
    assert manifest["tile"]["guards"]["wcag_contrast"] >= 3
    assert manifest["tile"]["guards"]["apca_lc"] >= 60

    tile = Image.open(base/"tile"/"tile-1024.png")
    assert tile.size == (1024, 1024)
    assert tile.mode == "RGBA"
    assert tile.getpixel((0, 0))[3] == 0
    assert tile.getpixel((512, 512))[3] == 255
    assert (base/"variants"/"pure-white-1024.png").exists()
    assert (base/"variants"/"alpha-mask-1024.png").exists()
    assert (base/"variants"/"monochrome-1024.png").exists()

    assert (base/"web"/"favicon.ico").exists()
    assert (base/"web"/"apple-touch-icon.png").exists()
    assert (base/"pwa"/"manifest.json").exists()
    pwa_manifest = json.loads((base/"pwa"/"manifest.json").read_text())
    purposes = {icon.get("purpose", "any") for icon in pwa_manifest["icons"]}
    assert {"any", "maskable", "monochrome"}.issubset(purposes)
    maskable = Image.open(base/"pwa"/"maskable-512.png")
    assert maskable.size == (512, 512)
    assert maskable.mode == "RGB"
    assert (base/"pwa"/"monochrome-512.png").exists()

    assert (base/"ios"/"AppIcon.appiconset"/"Contents.json").exists()
    assert (base/"android"/"mipmap-anydpi-v26"/"ic_launcher.xml").exists()
    xml = (base/"android"/"mipmap-anydpi-v26"/"ic_launcher.xml").read_text()
    assert "ic_launcher_monochrome" in xml
    assert Image.open(base/"android"/"mipmap-mdpi"/"ic_launcher_foreground.png").size == (108, 108)
    assert max(_alpha_bbox_size(base/"android"/"mipmap-mdpi"/"ic_launcher_foreground.png")) == 66
    assert (base/"android"/"mipmap-mdpi"/"ic_launcher_monochrome.png").exists()
    assert (base/"android"/"play-store"/"icon-512.png").exists()
    assert (base/"macos"/"boxed"/"boxed-1024.png").exists()
    assert (base/"macos"/"T.iconset"/"icon_512x512@2x.png").exists()
    assert not (base/"macos"/"T.iconset"/"icon_1024x1024.png").exists()
    assert (base/"watchos"/"icon-172.png").exists()
    assert (base/"windows"/"AppList.targetsize-256_altform-unplated.png").exists()
    assert (base/"windows"/"AppList.targetsize-256_altform-lightunplated.png").exists()
    # Apple icon MUST be opaque
    assert Image.open(base/"ios"/"AppIcon.appiconset"/"AppIcon-1024.png").mode == "RGB"
    assert not _has_true_alpha(base/"android"/"play-store"/"icon-512.png")
    assert max(_content_bbox_size_rgb(base/"pwa"/"maskable-512.png")) <= round(512 * 0.80)

def test_export_legacy_cli_still_runs(tmp_path):
    m = tmp_path / "m.png"; _master(m)
    out = tmp_path / "dist"
    r = subprocess.run([sys.executable, str(SCRIPTS/"export_icon_assets.py"), str(m),
        "--out", str(out), "--name", "Legacy", "--platforms",
        "web,pwa,ios,macos,android,social", "--ios-bg", "#0E1116"], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    base = out / "Legacy"
    assert (base/"preview.png").exists()
    assert (base/"export-manifest.json").exists()

def test_preflight(tmp_path):
    m = tmp_path / "m.png"; _master(m)
    r = subprocess.run([sys.executable, str(SCRIPTS/"preflight_icon_set.py"), str(m),
        "--want-transparent", "--json"], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert data["icons"][0]["auto_prescreen"] >= 70
    assert data["preflight_status"] in {"AUTO_PREFLIGHT_OK","AUTO_PREFLIGHT_REVIEW","BLOCKING_EXPORT_ISSUE"}
    assert data["human_review_required"] is True

def _run_export(master, out, platforms="web"):
    return subprocess.run(
        [sys.executable, str(SCRIPTS/"export_icon_assets.py"), str(master),
         "--out", str(out), "--name", "T", "--platforms", platforms],
        capture_output=True,
        text=True,
    )

def test_master_contract_accepts_valid_opaque_master(tmp_path):
    m = tmp_path / "valid.png"
    _opaque_master(m)
    out = tmp_path / "dist"
    r = _run_export(m, out, "web")
    assert r.returncode == 0, r.stderr
    assert (out / "T" / "web" / "icon-1024.png").exists()

def test_master_contract_rejects_non_square_before_writing(tmp_path):
    m = tmp_path / "non-square.png"
    Image.new("RGBA", (1024, 900), (238, 241, 232, 255)).save(m)
    out = tmp_path / "dist"
    r = _run_export(m, out, "web")
    assert r.returncode != 0
    assert "MASTER_CONTRACT_FAILED" in r.stderr
    assert not (out / "T").exists()

def test_master_contract_rejects_black_bar_before_writing(tmp_path):
    m = tmp_path / "black-bar.png"
    im = Image.new("RGBA", (1024, 1024), (238, 241, 232, 255))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([220, 220, 804, 804], radius=160, fill=(20, 160, 150, 255))
    d.rectangle([900, 0, 1023, 1023], fill=(0, 0, 0, 255))
    im.save(m)
    out = tmp_path / "dist"
    r = _run_export(m, out, "web")
    assert r.returncode != 0
    assert "black bar" in r.stderr
    assert not (out / "T").exists()

def test_master_contract_rejects_white_frame_before_writing(tmp_path):
    m = tmp_path / "white-frame.png"
    im = Image.new("RGBA", (1024, 1024), (40, 120, 160, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 1023, 60], fill=(255, 255, 255, 255))
    d.rectangle([0, 963, 1023, 1023], fill=(255, 255, 255, 255))
    d.rectangle([0, 0, 60, 1023], fill=(255, 255, 255, 255))
    d.rectangle([963, 0, 1023, 1023], fill=(255, 255, 255, 255))
    im.save(m)
    out = tmp_path / "dist"
    r = _run_export(m, out, "web")
    assert r.returncode != 0
    assert "white frame" in r.stderr
    assert not (out / "T").exists()

def test_master_contract_rejects_transparent_master_without_explicit_flatten(tmp_path):
    m = tmp_path / "transparent.png"
    _master(m)
    out = tmp_path / "dist"
    r = _run_export(m, out, "ios")
    assert r.returncode != 0
    assert "transparent master targets opaque app platforms" in r.stderr
    assert not (out / "T").exists()
