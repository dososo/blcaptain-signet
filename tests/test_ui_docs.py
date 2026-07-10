"""UI SVG 按需生成引导与覆盖清单契约测试。"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_skill_documents_on_demand_ui_svg_checklist():
    skill = (ROOT / "skills" / "signet" / "SKILL.md").read_text(encoding="utf-8")
    for phrase in (
        "识别意图",
        "单色 `currentColor` 描边",
        "品牌主色 hex",
        "hover / active",
        "palette JSON",
        "覆盖清单",
        "param_engine.py",
        "UI 线性图标不用 imagegen",
        "前端内联",
        "CSS `color`",
    ):
        assert phrase in skill


def test_readmes_publish_aligned_ui_coverage_counts():
    for relative in ("README.md", "README.en.md"):
        readme = (ROOT / relative).read_text(encoding="utf-8")
        for phrase in ("250", "22", "272"):
            assert phrase in readme

    chinese = (ROOT / "README.md").read_text(encoding="utf-8")
    for phrase in ("按需生成", "导航与方向", "状态与反馈", "媒体与设备", "文件与数据"):
        assert phrase in chinese

    english = (ROOT / "README.en.md").read_text(encoding="utf-8")
    for phrase in ("generated on demand", "navigation", "status", "media", "files"):
        assert phrase in english.lower()


def test_license_summary_matches_manifest_counts():
    licenses = (ROOT / "LICENSES.md").read_text(encoding="utf-8")
    for phrase in ("MIT glyph 共 96 个", "其余 154 个", "22 个几何", "当前 UI SVG 总量为 272"):
        assert phrase in licenses
