# Signet Icon System

<p align="center">
  <a href="README.md">中文</a> · <a href="README.en.md">English</a>
</p>

<p align="center"><strong>把同一套品牌视觉身份，铸印到每一个图标触点。</strong></p>

![Signet 全系统展示](assets/showcase/hero-signet.png)

<p align="center">
  <code>29 个精选样式</code> · <code>272 个 UI SVG</code> · <code>8 类平台导出</code> · <code>Apache-2.0</code>
</p>

Signet 是一套 clean-room 图标视觉身份系统。它把产品 brief 编译成可执行的视觉契约，锁定材质、轮廓、光照、构图、调色和批次一致性；母版通过质量门禁后，再导出为 Web、PWA、iOS、Android、macOS、HarmonyOS、tvOS 与社交媒体资产。

发布计数：门面 19 · 编辑 6 · 旗舰 1 · 扁平 3 · 合计 29。完整 29 样式请看 [自包含 Gallery](docs/gallery.html) 与 [STYLE_LEDGER](docs/STYLE_LEDGER.md)。

## 为什么用 Signet

| 你要解决的问题 | Signet 给出的答案 |
|---|---|
| 一组图标像来自不同模板 | 用样式配方和批次锁统一材质、相机、光照与轮廓 |
| 品牌色一换，画面就脏或失焦 | 用角色化调色盘和明度门禁保持第一眼识别 |
| 大图好看，小图不可用 | 用 64px / 32px / 16px 预检检查轮廓、边缘与对比度 |
| 一张母版要手工适配多个平台 | 一次导出 8 类平台目录、manifest、预览板与 zip |
| 产品还需要成套线性 UI 图标 | 提供 250 个 themed + 22 个 custom，共 272 个 SVG |

## 30 秒开始

```bash
git clone https://github.com/dososo/blcaptain-signet.git
cd blcaptain-signet
python -m pip install pyyaml Pillow pytest
```

使用内置 brief 编译一份图标提示词：

```bash
python skills/signet/scripts/build_prompt.py \
  examples/flowpilot.brief.yaml \
  --style kiln-charm \
  --out /tmp/flowpilot-kiln.prompts.md
```

对 1024×1024 PNG 母版做质量预检，并导出全平台资产：

```bash
python skills/signet/scripts/preflight_icon_set.py examples/sample-master.png --json

python skills/signet/scripts/export_icon_assets.py \
  examples/sample-master.png \
  --out /tmp/signet-export \
  --name "FlowPilot" \
  --platforms web,pwa,ios,macos,android,harmonyos,tvos,social \
  --brand-primary "#2758D8" \
  --ios-bg "#F3F0E8" \
  --zip
```

Signet 负责编译视觉契约、检查母版并导出资产；实际图像生成由你选择的图像模型完成。

## 公开展示

README 只放精选 proof，避免把全量样式压缩成不可判断的小图。完整 29 张参考板在 [Gallery](docs/gallery.html) 中展开。

<table>
  <tr>
    <td width="50%"><img src="assets/showcase/juju-character.png" alt="Juju 角色身份锁"></td>
    <td width="50%"><img src="assets/examples/example-contact-sheet.png" alt="当前公开样例联系表"></td>
  </tr>
</table>

## 29 个视觉样式

| 分类 | 数量 | 用途 |
|---|---:|---|
| 门面 | 19 | 品牌主图标、功能图标、高辨识度对象 |
| 编辑 | 6 | 空状态、文章配图、功能说明、品牌叙事 |
| 旗舰 | 1 | `nacre-drift`，黑漆与螺钿的高辨识工艺 |
| 扁平 | 3 | 紧凑、高对比、偏图形语言的界面场景 |

所有样式板均使用完整主体展示，不用横向裁切图证明效果。全量板见 [docs/gallery.html](docs/gallery.html)。

## 272 个 UI SVG

![UI SVG 代表 proof](assets/showcase/ui-svg-272.png)

UI 轨道包含 **250 个 themed + 22 个 custom = 272 个 SVG**，统一为 `24×24 / 2px / round cap / round join / currentColor`。覆盖导航与方向、操作与编辑、状态与反馈、通信与媒体、媒体与设备、文件与数据、商业与安全、平台与 Signet 专属工具。

这是「高频厚库 + 按需生成」：覆盖清单外的图标可在 `skills/signet/ui/param_engine.py` 中以参数化几何方式补齐。UI 线性图标不用 imagegen；前端推荐内联 SVG，以 CSS `color` 驱动 `currentColor`。

## 小尺寸与平台交付

<table>
  <tr>
    <td width="50%"><img src="assets/showcase/small-size-proof.png" alt="小尺寸可读性 proof"></td>
    <td width="50%"><img src="assets/showcase/platform-exports.png" alt="真实平台导出 proof"></td>
  </tr>
</table>

预检会检查图标轮廓、边缘安全区、透明度、对比度与小尺寸表现。导出器会生成各平台尺寸梯、适配形态、预览板、manifest 和可选 zip。

## 工作方式

```text
产品 brief
   ↓
选择 29 个样式之一 + 品牌色
   ↓
编译视觉契约与批次提示词
   ↓
图像模型生成 1024×1024 母版
   ↓
预检：轮廓 / 对比度 / 边缘 / 一致性
   ↓
导出：Web / PWA / iOS / Android / macOS / HarmonyOS / tvOS / Social
```

关键入口：

- `build_prompt.py`：单个 brief 编译。
- `build_batch_prompts.py`：同一项目的批量提示词与一致性锁。
- `preflight_icon_set.py`：母版质量检查。
- `export_icon_assets.py`：平台尺寸、变体、manifest 与 zip。
- `ui_pipeline.py`：UI SVG 合并、验证与输出。

## 验证

```bash
python -m pytest -q
python skills/signet/ui/repo_license_gate.py
python scripts/prepush_check.py --git-tree release/github-public-v1.0
```

发布门禁覆盖：Apache-2.0 与第三方 notice、pytest、公开文件 allowlist、内部过程信息、凭据、个人隐私、README 图片、Gallery 外链资源、29 项计数、Git tree、单提交公开历史以及逐文件 SHA-256。

## 公开目录

```text
assets/                 公开参考画板与示例
docs/                   Gallery 与 29 样式清单
examples/               可运行 brief 与母版样例
skills/signet/          Skill、29 个样式配方、编译器、门禁、导出器、UI SVG
scripts/prepush_check.py
tests/                  公开产品回归测试
RELEASE_MANIFEST.md     发布文件树与逐文件 SHA-256
```

## 常见问题

<details>
<summary><strong>Signet 会直接调用图像模型吗？</strong></summary>

不会。Signet 编译提示词与视觉约束；你可以把结果交给任意支持图像生成的模型。
</details>

<details>
<summary><strong>可以只用 UI SVG，不使用图片样式吗？</strong></summary>

可以。UI SVG 轨道可以独立使用，全部采用 `currentColor`，适合直接内联到前端。
</details>

<details>
<summary><strong>可以商用吗？</strong></summary>

项目代码、文档、样式配方和自有元数据采用 Apache-2.0。第三方 UI glyph 的许可和 notice 见 `LICENSES.md`；模型生成图片还需要遵守所用模型的条款，并自行完成商标与品牌审查。
</details>

## 作者

由 **爆裂队长NEXT** 创建与维护。

- GitHub：[@dososo](https://github.com/dososo)
- X：[@thinkszyg](https://x.com/thinkszyg)
- 工作邮箱：[blteam2026@outlook.com](mailto:blteam2026@outlook.com)
- 问题反馈：[dososo/blcaptain-signet Issues](https://github.com/dososo/blcaptain-signet/issues)

## 参与贡献

提交前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 与 [CLEAN_ROOM.md](CLEAN_ROOM.md)。不要复制第三方提示词、素材、截图、构图、命名集合或视觉身份。

## 许可

Apache License 2.0。详见 [LICENSE](LICENSE)、[NOTICE.md](NOTICE.md) 与 [LICENSES.md](LICENSES.md)。
