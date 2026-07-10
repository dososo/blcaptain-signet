"""Signet 公开发布门禁测试。"""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "prepush_check.py"


def load_module():
    assert MODULE_PATH.exists(), "scripts/prepush_check.py 尚未实现"
    spec = importlib.util.spec_from_file_location("prepush_check", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_release_policy_excludes_internal_and_generated_intermediates():
    module = load_module()

    assert module.is_release_path(Path("README.md"))
    assert module.is_release_path(Path("README.en.md"))
    assert module.is_release_path(Path("LICENSE"))
    assert module.is_release_path(Path("assets/showcase/hero-signet.png"))
    assert module.is_release_path(Path("assets/examples/example-contact-sheet.png"))
    assert not module.is_release_path(Path("README.zh-CN.md"))
    assert not module.is_release_path(Path("generated-assets/launch/showcase/board__juju.png"))
    assert not module.is_release_path(Path("generated-assets/real-samples/contact-sheet.png"))
    assert not module.is_release_path(Path("generated-assets/curation-v1/CURATION.md"))
    assert not module.is_release_path(Path("docs/prd-v1.2.md"))
    assert not module.is_release_path(Path("docs/private-analysis.md"))
    assert not module.is_release_path(Path("examples/phase-b1/riso-press.prompt.md"))
    assert not module.is_release_path(Path("tests/fixtures/phase0-baseline/manifest.json"))
    assert not module.is_release_path(Path("skills/signet/ui/dist/ui-20260710/index.html"))
    assert not module.is_release_path(Path("tasks/todo.md"))
    assert not module.is_release_path(Path("audit/private.md"))
    assert not module.is_release_path(Path(".codex/state.json"))


def test_internal_leak_scan_checks_paths_and_text(tmp_path):
    module = load_module()
    safe = tmp_path / "README.md"
    safe.write_text("public product document\n", encoding="utf-8")
    leaking = tmp_path / "docs" / "guide.md"
    leaking.parent.mkdir()
    leaking.write_text("selected from " + "P" + "9x " + "sur" + "vivors\n", encoding="utf-8")

    leaks = module.find_internal_leaks(tmp_path, [safe, leaking])

    assert len(leaks) == 1
    assert "docs/guide.md" in leaks[0]


def test_secret_scan_detects_credentials_but_not_design_tokens(tmp_path):
    module = load_module()
    safe = tmp_path / "safe.md"
    safe.write_text("Use currentColor and palette token values.\n", encoding="utf-8")
    leaking = tmp_path / "config.py"
    key_name = "api_" + "key"
    key_value = "sk-" + "1234567890abcdefghijklmnopqrstuv"
    leaking.write_text(f"{key_name} = '{key_value}'\n", encoding="utf-8")

    leaks = module.find_secret_leaks(tmp_path, [safe, leaking])

    assert len(leaks) == 1
    assert "config.py" in leaks[0]


def test_secret_scan_detects_bearer_credential(tmp_path):
    module = load_module()
    header = tmp_path / "headers.txt"
    credential = "Bearer" + " abcdefghijklmnopqrstuvwxyz0123456789"
    header.write_text(f"Authorization: {credential}\n", encoding="utf-8")

    leaks = module.find_secret_leaks(tmp_path, [header])

    assert len(leaks) == 1
    assert "headers.txt" in leaks[0]


def test_internal_leak_scan_includes_svg_text(tmp_path):
    module = load_module()
    svg = tmp_path / "icon.svg"
    internal_marker = "P" + "9x " + "sur" + "vivor"
    svg.write_text(f"<svg><metadata>{internal_marker}</metadata></svg>\n", encoding="utf-8")

    leaks = module.find_internal_leaks(tmp_path, [svg])

    assert len(leaks) == 1
    assert "icon.svg" in leaks[0]


def test_gallery_and_readme_resource_checks(tmp_path):
    module = load_module()
    docs = tmp_path / "docs"
    images = tmp_path / "images"
    docs.mkdir()
    images.mkdir()
    (images / "hero.png").write_bytes(b"png")
    gallery = docs / "gallery.html"
    gallery.write_text('<img src="../images/hero.png"><a href="../README.md">README</a>\n', encoding="utf-8")
    readme = tmp_path / "README.md"
    readme.write_text("![Hero](images/hero.png)\n", encoding="utf-8")

    assert module.validate_gallery(gallery, tmp_path) == []
    assert module.validate_readme_images(readme, tmp_path) == []

    gallery.write_text('<img src="https://example.com/hero.png">\n', encoding="utf-8")
    assert any("http" in error for error in module.validate_gallery(gallery, tmp_path))


def test_launch_counts_are_consistent_in_public_surfaces(tmp_path):
    module = load_module()
    docs = tmp_path / "docs"
    docs.mkdir()
    summary = "门面 19 · 编辑 6 · 旗舰 1 · 扁平 3 · 合计 29"
    (tmp_path / "README.md").write_text(summary, encoding="utf-8")
    (tmp_path / "README.en.md").write_text(summary, encoding="utf-8")
    (docs / "gallery.html").write_text(summary, encoding="utf-8")
    (docs / "STYLE_LEDGER.md").write_text(summary, encoding="utf-8")

    assert module.validate_launch_counts(tmp_path) == []

    (tmp_path / "README.md").write_text("门面 18 · 编辑 6 · 旗舰 1 · 扁平 3 · 合计 28", encoding="utf-8")
    assert any("README.md" in error for error in module.validate_launch_counts(tmp_path))


def test_ci_workflow_rejects_pip_cache_without_dependency_file(tmp_path):
    module = load_module()
    workflow = tmp_path / ".github" / "workflows" / "ci.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text(
        "steps:\n"
        "  - uses: actions/setup-python@v5\n"
        "    with:\n"
        "      python-version: '3.10'\n"
        "      cache: pip\n",
        encoding="utf-8",
    )

    errors = module.validate_ci_workflow(tmp_path)

    assert any("cache: pip" in error for error in errors)

    (tmp_path / "requirements.txt").write_text("pytest\n", encoding="utf-8")
    assert module.validate_ci_workflow(tmp_path) == []


def test_showcase_gate_rejects_wide_black_bands(tmp_path):
    module = load_module()
    showcase = tmp_path / "assets" / "showcase"
    showcase.mkdir(parents=True)
    image_path = showcase / "bad.png"

    image = Image.new("RGB", (400, 240), "#f3f0e8")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 80, 400, 120), fill="#050505")
    image.save(image_path)

    errors = module.validate_showcase_assets(tmp_path)

    assert any("黑色横条" in error for error in errors)


def test_readme_showcase_strategy_avoids_full_style_board_table(tmp_path):
    module = load_module()
    (tmp_path / "README.md").write_text("![Hero](assets/showcase/hero-signet.png)\n", encoding="utf-8")
    (tmp_path / "README.en.md").write_text("![Hero](assets/showcase/hero-signet.png)\n", encoding="utf-8")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "gallery.html").write_text("assets/showcase/styles/kiln-charm.png\n", encoding="utf-8")

    assert module.validate_readme_showcase_strategy(tmp_path) == []

    (tmp_path / "README.md").write_text('<img src="assets/showcase/styles/kiln-charm.png">\n', encoding="utf-8")
    assert any("README.md" in error for error in module.validate_readme_showcase_strategy(tmp_path))


def test_manifest_hashes_every_payload_file_except_itself(tmp_path):
    module = load_module()
    (tmp_path / "README.md").write_text("hello\n", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("Apache-2.0\n", encoding="utf-8")
    manifest = tmp_path / "RELEASE_MANIFEST.md"

    module.write_manifest(
        tmp_path,
        [tmp_path / "README.md", tmp_path / "LICENSE", manifest],
        {"vendored": 1, "themed": 250, "custom": 22, "total": 272},
    )

    text = manifest.read_text(encoding="utf-8")
    assert "README.md" in text
    assert "LICENSE" in text
    assert "RELEASE_MANIFEST.md" in text
    assert "清单自身不参与自哈希" in text
    assert module.verify_manifest(tmp_path, [tmp_path / "README.md", tmp_path / "LICENSE", manifest]) == []


def test_git_tree_must_match_release_files_and_content(tmp_path):
    module = load_module()
    (tmp_path / "README.md").write_text("release\n", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("Apache-2.0\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "README.md", "LICENSE"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "release"],
        cwd=tmp_path,
        check=True,
    )
    files = [tmp_path / "README.md", tmp_path / "LICENSE"]

    assert module.validate_git_tree(tmp_path, "HEAD", files) == []

    (tmp_path / "README.md").write_text("changed after commit\n", encoding="utf-8")
    assert any("内容不一致" in error for error in module.validate_git_tree(tmp_path, "HEAD", files))


def test_privacy_scan_keeps_public_author_and_rejects_private_identity(tmp_path):
    module = load_module()
    public = tmp_path / "README.md"
    public.write_text(
        "作者：爆裂队长NEXT\nX: @thinkszyg\n邮箱：blteam2026@outlook.com\n",
        encoding="utf-8",
    )
    private = tmp_path / "notes.md"
    private_mail = "someone@" + "gmail.com"
    private_path = "/" + "Users/example/Desktop/private.txt"
    private.write_text(
        f"联系 {private_mail}，文件位于 {private_path}\n",
        encoding="utf-8",
    )

    assert module.find_privacy_leaks(tmp_path, [public]) == []
    leaks = module.find_privacy_leaks(tmp_path, [public, private])
    assert any("notes.md" in leak for leak in leaks)


def test_public_commit_is_single_root_commit_with_confirmed_author(tmp_path):
    module = load_module()
    (tmp_path / "README.md").write_text("release\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=爆裂队长NEXT",
            "-c",
            "user.email=blteam2026@outlook.com",
            "commit",
            "-qm",
            "release",
        ],
        cwd=tmp_path,
        check=True,
    )

    assert module.validate_public_history(tmp_path, "HEAD") == []

    subprocess.run(
        [
            "git",
            "-c",
            "user.name=爆裂队长NEXT",
            "-c",
            "user.email=blteam2026@outlook.com",
            "commit",
            "--allow-empty",
            "-qm",
            "second",
        ],
        cwd=tmp_path,
        check=True,
    )
    assert any("仅允许 1 个" in error for error in module.validate_public_history(tmp_path, "HEAD"))


def test_public_showcase_has_all_29_style_boards():
    style_ids = []
    ledger = (ROOT / "docs" / "STYLE_LEDGER.md").read_text(encoding="utf-8")
    for line in ledger.splitlines():
        if line.startswith("- `"):
            style_ids.append(line.split("`")[1])

    boards = ROOT / "assets" / "showcase" / "styles"
    assert len(style_ids) == 29
    assert {path.stem for path in boards.glob("*.png")} == set(style_ids)


def test_public_readme_does_not_embed_all_style_boards():
    for relative in ("README.md", "README.en.md"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "assets/showcase/styles/" not in text


def test_open_source_metadata_and_author_contract():
    metadata = __import__("json").loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert metadata["version"] == "1.0.0"
    assert metadata["license"] == "Apache-2.0"
    assert metadata["styleCount"] == 29
    assert metadata["uiSvgCount"] == 272

    for relative in ("README.md", "README.en.md"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "dososo/blcaptain-signet" in text
        assert "爆裂队长NEXT" in text
        assert "@thinkszyg" in text
        assert "blteam2026@outlook.com" in text


def test_current_product_snapshot_meets_release_contract():
    module = load_module()
    files = module.collect_release_files(ROOT)
    relative = {path.relative_to(ROOT).as_posix() for path in files}

    assert "README.md" in relative
    assert "README.en.md" in relative
    assert "README.zh-CN.md" not in relative
    assert "LICENSE" in relative
    assert "docs/gallery.html" in relative
    assert "docs/STYLE_LEDGER.md" in relative
    assert not any(path.startswith("generated-assets/") for path in relative)
    assert module.find_internal_leaks(ROOT, files) == []
    assert module.find_secret_leaks(ROOT, files) == []
    assert module.find_privacy_leaks(ROOT, files) == []
    assert module.validate_gallery(ROOT / "docs" / "gallery.html", ROOT) == []
    assert module.validate_readme_images(ROOT / "README.md", ROOT) == []
    assert module.validate_readme_images(ROOT / "README.en.md", ROOT) == []
    assert module.validate_launch_counts(ROOT) == []
