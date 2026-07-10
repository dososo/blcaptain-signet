#!/usr/bin/env python3
"""Signet product-only 发布前自检与确定性清单生成。"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import subprocess
import sys
import tarfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_NAME = "RELEASE_MANIFEST.md"
COUNT_MARKER = "门面 19 · 编辑 6 · 旗舰 1 · 扁平 3 · 合计 29"
PUBLIC_AUTHOR_NAME = "爆裂队长NEXT"
PUBLIC_AUTHOR_EMAIL = "blteam2026@outlook.com"
TEXT_SUFFIXES = {
    "",
    ".cfg",
    ".css",
    ".html",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".rst",
    ".svg",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
ROOT_RELEASE_FILES = {
    ".gitignore",
    "CLEAN_ROOM.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "LICENSE-CONTENT",
    "LICENSES.md",
    "NOTICE.md",
    "README.en.md",
    "README.md",
    "RELEASE_MANIFEST.md",
    "VERSION",
}
PUBLIC_STYLE_IDS = {
    "brush-block", "candy-gloss", "carbon-twill", "carve-block",
    "celadon-goldline", "cloison-glass", "cobalt-bleed", "contour-single",
    "cyan-draft", "duotone-pop", "facet-solid", "felt-field", "geo-bauhaus",
    "gradient-flow", "inflate-vinyl", "kiln-charm", "knit-craft",
    "lacquer-seal", "layer-paper", "nacre-drift", "pomo-splash",
    "prism-layer", "ridge-enamel", "riso-press", "satin-porcelain",
    "scene-block", "silk-fold", "soft-molded", "sumi-bold",
}
PUBLIC_DOCS = {"gallery.html", "STYLE_LEDGER.md"}
PUBLIC_EXAMPLES = {
    "devpulse.batch.yaml",
    "flowpilot.brief.yaml",
    "kidnest.brief.yaml",
    "ledgerfox.brief.yaml",
    "sample-master.png",
}
PUBLIC_TESTS = {
    "test_export.py", "test_gallery.py", "test_ground_law.py",
    "test_palette_engine.py", "test_platform_completeness.py",
    "test_prepush_check.py", "test_repo_license_gate.py", "test_set_palette.py",
    "test_ui_docs.py", "test_ui_param_engine.py", "test_ui_pipeline.py",
    "test_ui_theming.py",
}
INTERNAL_TEXT_PATTERNS = (
    re.compile(r"\bP\d+[a-z0-9_-]*\b", re.IGNORECASE),
    re.compile(r"\b" + "sur" + r"vivors?\b", re.IGNORECASE),
    re.compile(r"catalog_status\s*:\s*spike\b", re.IGNORECASE),
)


def is_release_path(relative: Path) -> bool:
    """返回路径是否属于 product-only 发布集合。"""
    parts = relative.parts
    if not parts:
        return False
    if any(part in {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"} for part in parts):
        return False
    if relative.name in {".DS_Store"} or relative.suffix in {".pyc", ".pyo", ".zip"}:
        return False
    if "dist" in parts or "build" in parts or "tmp" in parts:
        return False
    if len(parts) == 1:
        return relative.name in ROOT_RELEASE_FILES
    if parts[0] in {"assets", ".agents", ".codex-plugin"}:
        return True
    if parts[0] == ".github":
        return True
    if parts[0] == "docs":
        return len(parts) == 2 and parts[1] in PUBLIC_DOCS
    if parts[0] == "examples":
        return len(parts) == 2 and parts[1] in PUBLIC_EXAMPLES
    if parts[0] == "scripts":
        return len(parts) == 2 and parts[1] == "prepush_check.py"
    if parts[0] == "tests":
        return len(parts) == 2 and parts[1] in PUBLIC_TESTS
    if parts[:3] == ("skills", "signet", "styles"):
        return len(parts) == 4 and relative.stem in PUBLIC_STYLE_IDS
    if parts[:2] == ("skills", "signet"):
        return True
    return False


def collect_release_files(root: Path = ROOT) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(root)
        if is_release_path(relative):
            files.append(path)
    return sorted(files, key=lambda path: path.relative_to(root).as_posix())


def _read_text(path: Path) -> str | None:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return None
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def find_internal_leaks(root: Path, files: list[Path]) -> list[str]:
    leaks: list[str] = []
    policy_files = {"scripts/prepush_check.py", "tests/test_prepush_check.py"}
    for path in files:
        relative = path.relative_to(root).as_posix()
        text = _read_text(path)
        if relative in policy_files:
            continue
        if any(pattern.search(relative) or pattern.search(text or "") for pattern in INTERNAL_TEXT_PATTERNS):
            leaks.append(f"{relative}: 内部阶段或筛选过程标记泄漏")
    return leaks


def find_privacy_leaks(root: Path, files: list[Path]) -> list[str]:
    """保留已授权公开身份，拒绝其他邮箱和本机绝对用户路径。"""
    email_pattern = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z][A-Z0-9.-]*\.[A-Z]{2,}\b")
    home_pattern = re.compile(r"(?:(?:/Users|/home)/[^/\s]+|[A-Z]:\\Users\\[^\\\s]+)")
    leaks: list[str] = []
    for path in files:
        text = _read_text(path)
        if text is None:
            continue
        relative = path.relative_to(root).as_posix()
        for line_number, line in enumerate(text.splitlines(), start=1):
            emails = {match.group(0).lower() for match in email_pattern.finditer(line)}
            disallowed = {
                email for email in emails
                if email != PUBLIC_AUTHOR_EMAIL.lower()
                and not email.endswith(("@example.com", "@example.invalid"))
            }
            if disallowed:
                leaks.append(f"{relative}:{line_number}: 非公开授权邮箱")
            if home_pattern.search(line):
                leaks.append(f"{relative}:{line_number}: 本机用户绝对路径")
    return leaks


def _secret_patterns() -> tuple[re.Pattern[str], ...]:
    assignment_names = "api" + r"[_-]?key|client[_-]?secret|access[_-]?token|password|secret"
    assignment = re.compile(
        rf"(?i)\b(?:{assignment_names})\b\s*[:=]\s*['\"]?([A-Za-z0-9_./+=-]{{16,}})"
    )
    bearer = re.compile(r"(?i)\b" + "Bearer" + r"\s+[A-Za-z0-9._~+/=-]{20,}")
    key_prefix = re.compile(r"\b(?:" + "sk" + r"-[A-Za-z0-9_-]{24,}|ghp_[A-Za-z0-9]{24,})\b")
    private_key = re.compile("BEGIN " + r"(?:RSA |EC |OPENSSH |DSA )?" + "PRIVATE KEY")
    return assignment, bearer, key_prefix, private_key


def find_secret_leaks(root: Path, files: list[Path]) -> list[str]:
    patterns = _secret_patterns()
    leaks: list[str] = []
    for path in files:
        text = _read_text(path)
        if text is None:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if any(pattern.search(line) for pattern in patterns):
                leaks.append(f"{path.relative_to(root).as_posix()}:{line_number}: 疑似凭据")
    return leaks


class _ResourceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[tuple[str, str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        src = values.get("src")
        if src:
            self.references.append((tag, "src", src))
        if tag == "link" and values.get("href"):
            self.references.append((tag, "href", values["href"] or ""))
        if tag == "a" and values.get("href"):
            self.references.append((tag, "href", values["href"] or ""))


def _resolve_local_reference(source: Path, value: str) -> Path | None:
    if value.startswith(("#", "data:", "mailto:", "javascript:")):
        return None
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc:
        return None
    return (source.parent / parsed.path).resolve()


def validate_gallery(gallery: Path, root: Path) -> list[str]:
    if not gallery.exists():
        return ["docs/gallery.html 缺失"]
    parser = _ResourceParser()
    parser.feed(gallery.read_text(encoding="utf-8"))
    errors: list[str] = []
    for tag, attribute, value in parser.references:
        parsed = urlsplit(value)
        if parsed.scheme in {"http", "https"} and (attribute == "src" or tag == "link"):
            errors.append(f"gallery 外链资源: {value}")
            continue
        local = _resolve_local_reference(gallery, value)
        if local is not None and not local.exists():
            errors.append(f"gallery 本地资源缺失: {value}")
        if local is not None:
            try:
                local.relative_to(root.resolve())
            except ValueError:
                errors.append(f"gallery 引用越出产品根: {value}")
    return errors


MARKDOWN_IMAGE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")
HTML_IMAGE = re.compile(r"<img\b[^>]*\bsrc=['\"]([^'\"]+)['\"]", re.IGNORECASE)


def validate_readme_images(readme: Path, root: Path) -> list[str]:
    if not readme.exists():
        return [f"{readme.name} 缺失"]
    text = readme.read_text(encoding="utf-8")
    references = MARKDOWN_IMAGE.findall(text) + HTML_IMAGE.findall(text)
    errors: list[str] = []
    for value in references:
        parsed = urlsplit(value)
        if parsed.scheme in {"http", "https"}:
            continue
        local = _resolve_local_reference(readme, value)
        if local is None or not local.exists():
            errors.append(f"{readme.name} 图片缺失: {value}")
            continue
        try:
            local.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{readme.name} 图片越出产品根: {value}")
    return errors


def validate_launch_counts(root: Path) -> list[str]:
    errors: list[str] = []
    for relative in ("README.md", "README.en.md", "docs/gallery.html", "docs/STYLE_LEDGER.md"):
        path = root / relative
        if not path.exists():
            errors.append(f"{relative}: 缺失")
            continue
        if COUNT_MARKER not in path.read_text(encoding="utf-8"):
            errors.append(f"{relative}: 未声明 {COUNT_MARKER}")
    return errors


def validate_gitignore(root: Path) -> list[str]:
    path = root / ".gitignore"
    if not path.exists():
        return [".gitignore 缺失"]
    text = path.read_text(encoding="utf-8")
    required = (
        "**/__pycache__/",
        "*.pyc",
        "**/dist/ui-*/",
        "**/.codex/",
        "**/audit/",
        "generated-assets/",
        "private/",
        "workbench/",
    )
    return [f".gitignore 缺少规则: {rule}" for rule in required if rule not in text]


def validate_ci_workflow(root: Path) -> list[str]:
    workflow = root / ".github" / "workflows" / "ci.yml"
    if not workflow.exists():
        return [".github/workflows/ci.yml 缺失"]
    text = workflow.read_text(encoding="utf-8")
    uses_pip_cache = re.search(r"(?m)^\s*cache:\s*['\"]?pip['\"]?\s*$", text)
    has_dependency_file = any(root.glob("**/requirements.txt")) or any(root.glob("**/pyproject.toml"))
    if uses_pip_cache and not has_dependency_file:
        return ["CI 使用 cache: pip，但发布树没有 requirements.txt 或 pyproject.toml"]
    return []


def _has_wide_black_band(path: Path) -> bool:
    from PIL import Image

    image = Image.open(path).convert("L")
    image.thumbnail((520, 520))
    w, h = image.size
    if not w or not h:
        return False

    def long_run(values: list[float], limit: int) -> bool:
        run = 0
        for value in values:
            if value >= 0.74:
                run += 1
                if run >= limit:
                    return True
            else:
                run = 0
        return False

    row_ratios: list[float] = []
    pixels = image.load()
    for y in range(h):
        dark = sum(1 for x in range(w) if pixels[x, y] < 28)
        row_ratios.append(dark / w)
    if long_run(row_ratios, max(5, h // 80)):
        return True

    col_ratios: list[float] = []
    for x in range(w):
        dark = sum(1 for y in range(h) if pixels[x, y] < 28)
        col_ratios.append(dark / h)
    return long_run(col_ratios, max(5, w // 80))


def validate_showcase_assets(root: Path) -> list[str]:
    targets = [root / "assets" / "examples" / "example-contact-sheet.png"]
    targets.extend(sorted((root / "assets" / "showcase").glob("*.png")))
    targets.extend(sorted((root / "assets" / "showcase" / "styles").glob("*.png")))
    errors: list[str] = []
    for path in targets:
        if not path.exists():
            continue
        if _has_wide_black_band(path):
            errors.append(f"{path.relative_to(root).as_posix()}: 疑似黑色横条或整列黑条")
    return errors


def validate_readme_showcase_strategy(root: Path) -> list[str]:
    errors: list[str] = []
    public_surfaces = ("README.md", "README.en.md", "docs/gallery.html")
    banned_terms = (
        "generated-assets/real-samples",
        "alloyai liquid metal",
        "devpulse blueprint",
        "flowpilot prism gel",
        "inkflow ink seal",
        "ledgerfox jade lens",
    )
    for relative in public_surfaces:
        path = root / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8").lower()
        if relative.startswith("README") and "assets/showcase/styles/" in text:
            errors.append(f"{relative}: README 不应内嵌全部样式板，改链接到 Gallery")
        for term in banned_terms:
            if term in text:
                errors.append(f"{relative}: 仍引用早期废弃 proof: {term}")
    return errors


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _license_summary(root: Path) -> dict[str, int]:
    ui_root = root / "skills" / "signet" / "ui"
    themed = json.loads((ui_root / "manifest.json").read_text(encoding="utf-8"))["glyphs"]
    custom = json.loads((ui_root / "custom_manifest.json").read_text(encoding="utf-8"))["glyphs"]
    upstream = ui_root / "upstream"
    vendored = len([path for path in upstream.iterdir() if path.is_dir()])
    return {"vendored": vendored, "themed": len(themed), "custom": len(custom), "total": len(themed) + len(custom)}


def render_manifest(root: Path, files: list[Path], license_summary: dict[str, int]) -> str:
    relative_files = sorted({path.relative_to(root).as_posix() for path in files})
    if MANIFEST_NAME not in relative_files:
        relative_files.append(MANIFEST_NAME)
        relative_files.sort()
    payload = [relative for relative in relative_files if relative != MANIFEST_NAME]
    lines = [
        "# RELEASE MANIFEST",
        "",
        "发布根：`Signet_Complete_Assets_v1.0/signet-icon-system`",
        "",
        f"发布计数：{COUNT_MARKER}",
        "",
        "License 摘要：",
        "",
        f"- vendored upstream：{license_summary['vendored']}",
        f"- themed permissive glyph：{license_summary['themed']}",
        f"- custom Apache-2.0 glyph：{license_summary['custom']}",
        f"- permissive glyph 合计：{license_summary['total']}",
        "- restricted：0",
        "- project license：Apache-2.0",
        "",
        f"发布文件：{len(relative_files)}；SHA-256 payload：{len(payload)}。",
        "",
        "`RELEASE_MANIFEST.md` 列入发布树，但清单自身不参与自哈希；其 SHA-256 由 pre-push 终端输出单列。",
        "",
        "## 发布文件树",
        "",
        "```text",
        *relative_files,
        "```",
        "",
        "## SHA-256",
        "",
        "| 文件 | SHA-256 |",
        "|---|---|",
    ]
    for relative in payload:
        digest = sha256_file(root / relative)
        lines.append(f"| `{relative.replace('|', '&#124;')}` | `{digest}` |")
    lines.append("")
    return "\n".join(lines)


def write_manifest(root: Path, files: list[Path], license_summary: dict[str, int]) -> Path:
    manifest = root / MANIFEST_NAME
    manifest.write_text(render_manifest(root, files, license_summary), encoding="utf-8")
    return manifest


def verify_manifest(root: Path, files: list[Path]) -> list[str]:
    manifest = root / MANIFEST_NAME
    if not manifest.exists():
        return [f"{MANIFEST_NAME} 缺失"]
    actual = manifest.read_text(encoding="utf-8")
    try:
        license_summary = _license_summary(root)
    except FileNotFoundError:
        values: dict[str, int] = {}
        labels = {
            "vendored upstream": "vendored",
            "themed permissive glyph": "themed",
            "custom Apache-2.0 glyph": "custom",
            "permissive glyph 合计": "total",
        }
        for label, key in labels.items():
            match = re.search(rf"^- {re.escape(label)}：(\d+)$", actual, re.MULTILINE)
            if not match:
                return [f"{MANIFEST_NAME} 缺少 license 摘要: {label}"]
            values[key] = int(match.group(1))
        license_summary = values
    expected = render_manifest(root, files, license_summary)
    return [] if actual == expected else [f"{MANIFEST_NAME} 与当前发布集合或哈希不一致"]


def validate_git_tree(root: Path, treeish: str, files: list[Path]) -> list[str]:
    """验证待推 Git tree 的文件名和内容与发布集合完全一致。"""
    result = subprocess.run(
        ["git", "archive", "--format=tar", treeish],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        return [f"无法读取待推 Git tree {treeish}: {message}"]

    archived: dict[str, str] = {}
    with tarfile.open(fileobj=io.BytesIO(result.stdout), mode="r:") as archive:
        for member in archive.getmembers():
            if not member.isfile():
                continue
            handle = archive.extractfile(member)
            if handle is None:
                return [f"Git tree 文件无法读取: {member.name}"]
            archived[member.name] = hashlib.sha256(handle.read()).hexdigest()

    expected = {path.relative_to(root).as_posix(): sha256_file(path) for path in files}
    errors: list[str] = []
    missing = sorted(set(expected) - set(archived))
    extra = sorted(set(archived) - set(expected))
    if missing:
        errors.append(f"Git tree 缺少发布文件: {', '.join(missing[:10])}")
    if extra:
        errors.append(f"Git tree 含清单外文件: {', '.join(extra[:10])}")
    changed = sorted(path for path in set(expected) & set(archived) if expected[path] != archived[path])
    if changed:
        errors.append(f"Git tree 与工作区内容不一致: {', '.join(changed[:10])}")
    return errors


def validate_public_history(root: Path, treeish: str) -> list[str]:
    """验证公开分支只有一个无父提交，且作者和提交者均为公开身份。"""
    count = subprocess.run(
        ["git", "rev-list", "--count", treeish], cwd=root, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if count.returncode != 0:
        return [f"无法读取公开历史 {treeish}: {count.stderr.strip()}"]
    errors: list[str] = []
    if count.stdout.strip() != "1":
        errors.append(f"公开历史仅允许 1 个无父提交，实际为 {count.stdout.strip()}")
    metadata = subprocess.run(
        ["git", "show", "-s", "--format=%an%n%ae%n%cn%n%ce%n%P", treeish],
        cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if metadata.returncode != 0:
        return [*errors, f"无法读取公开提交元数据: {metadata.stderr.strip()}"]
    values = metadata.stdout.splitlines()
    if len(values) < 4:
        return [*errors, "公开提交元数据不完整"]
    expected = [PUBLIC_AUTHOR_NAME, PUBLIC_AUTHOR_EMAIL, PUBLIC_AUTHOR_NAME, PUBLIC_AUTHOR_EMAIL]
    if values[:4] != expected:
        errors.append("公开提交 author/committer 与已确认公开身份不一致")
    parent = values[4].strip() if len(values) > 4 else ""
    if parent:
        errors.append("公开提交必须无父提交")
    return errors


def _run(command: list[str], root: Path) -> tuple[bool, str]:
    result = subprocess.run(command, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return result.returncode == 0, result.stdout.strip()


def _report(name: str, errors: list[str], detail: str = "") -> bool:
    if errors:
        print(f"FAIL {name}")
        for error in errors:
            print(f"  - {error}")
        if detail:
            print(detail)
        return False
    suffix = f": {detail}" if detail else ""
    print(f"PASS {name}{suffix}")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="运行 Signet product-only 发布自检。")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--skip-pytest", action="store_true", help="仅供单元测试和诊断使用")
    parser.add_argument("--list-release-files", action="store_true", help="只输出发布文件相对路径")
    parser.add_argument("--git-tree", default="release/github-public-v1.0", help="待推送的本地 Git tree")
    args = parser.parse_args(argv)
    root = args.root.resolve()

    files = collect_release_files(root)
    if args.list_release_files:
        for path in files:
            print(path.relative_to(root).as_posix())
        return 0

    manifest = root / MANIFEST_NAME
    manifest_inputs = files if manifest in files else [*files, manifest]
    write_manifest(root, manifest_inputs, _license_summary(root))
    files = collect_release_files(root)

    all_passed = True
    license_ok, license_output = _run([sys.executable, "skills/signet/ui/repo_license_gate.py"], root)
    all_passed &= _report("license_gate", [] if license_ok else ["repo license gate 失败"], license_output)

    if not args.skip_pytest:
        pytest_ok, pytest_output = _run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], root)
        all_passed &= _report("pytest", [] if pytest_ok else ["pytest 失败"], pytest_output)

    checks = (
        ("gitignore", validate_gitignore(root)),
        ("ci_workflow", validate_ci_workflow(root)),
        ("showcase_assets", validate_showcase_assets(root)),
        ("readme_showcase_strategy", validate_readme_showcase_strategy(root)),
        ("internal_research_leak", find_internal_leaks(root, files)),
        ("secret_scan", find_secret_leaks(root, files)),
        ("privacy_scan", find_privacy_leaks(root, files)),
        ("gallery_self_contained", validate_gallery(root / "docs" / "gallery.html", root)),
        (
            "readme_images",
            validate_readme_images(root / "README.md", root)
            + validate_readme_images(root / "README.en.md", root),
        ),
        ("launch_counts", validate_launch_counts(root)),
        ("release_manifest", verify_manifest(root, files)),
    )
    for name, errors in checks:
        all_passed &= _report(name, errors)

    git_repo, _ = _run(["git", "rev-parse", "--git-dir"], root)
    if git_repo:
        all_passed &= _report("git_release_tree", validate_git_tree(root, args.git_tree, files), args.git_tree)
        all_passed &= _report("git_public_history", validate_public_history(root, args.git_tree), args.git_tree)
    else:
        all_passed &= _report("git_release_tree", [], "archive snapshot（无 .git）")

    print(f"RELEASE_FILES {len(files)}")
    print(f"RELEASE_MANIFEST {manifest}")
    print(f"RELEASE_MANIFEST_SHA256 {sha256_file(manifest)}")
    if args.skip_pytest:
        print("DIAGNOSTIC_ONLY pytest 已跳过，禁止据此发布")
        return 2
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
