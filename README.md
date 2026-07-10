# Signet · 一句话生成一整套品牌图标的 AI Skill

<p align="center">
  <a href="README.md">中文</a> · <a href="README.en.md">English</a>
</p>

<p align="center"><strong>在 Codex Desktop、Claude Code 等 AI Agent 里，用一句话把同一套品牌视觉，铸印到每一个图标触点。</strong></p>

![Signet 全系统展示](assets/showcase/hero-signet.png)

<p align="center">
  <code>29 个精选样式</code> · <code>272 个 UI SVG</code> · <code>8 类平台导出</code> · <code>Apache-2.0</code>
</p>

---

## Signet 是什么

Signet **不是一个命令行工具**，而是一个装进 AI Agent 的 **图标设计 Skill**。

你用大白话说一句「给我的记账 App 做一套温润陶瓷风的图标，品牌色 `#2758D8`」，Signet 就会在你的 Agent 里自动完成整条链路：

```
你说一句话  →  推断主体 + 推荐风格  →  出 4 张小样给你挑  →
锁定风格出完整套件  →  机器预检（小尺寸/轮廓/对比度）  →  一次导出 8 类平台资产
```

图片本身由**你的 Agent 的生图能力**生成；Signet 负责**编排提示词、锁定材质与调色、质量把关、多平台导出**——让一整套图标看起来像出自同一个品牌，而不是十个不同模板拼起来的。

> 一句话总结：**你负责说想要什么，Signet 负责让它成套、能用、能上线。**

## 支持的 Agent 平台与安装

Signet 以 clean-room 方式构建，核心是 [`skills/signet/SKILL.md`](skills/signet/SKILL.md)，可装进任何支持 skill / plugin 的 AI Agent：

| 平台 | 安装方式 |
|---|---|
| **Codex Desktop**（主要目标平台） | 本仓库自带 Codex 插件清单 [`.codex-plugin/plugin.json`](.codex-plugin/plugin.json)。将 `skills/signet/` 放入 Codex 的 skills 目录（`~/.agents/skills/signet/`），或按 Codex 插件方式加载本仓库。用 Codex 内置的图像生成能力出图。 |
| **Claude Code** | 将 `skills/signet/` 放入 `~/.claude/skills/signet/`，重启后即可在对话中触发。 |
| **其他支持 Skill 的 Agent** | 放入该平台的 skill 目录即可，核心文件是 `skills/signet/SKILL.md` 与 `skills/signet/scripts/`。 |

> 具体安装入口以各平台最新文档为准。安装后**无需记任何命令**——直接对话即可。

## 怎么用（对话式，30 秒上手）

安装好后，在你的 Agent 里直接说人话，例如：

> **「给我的 App『FlowPilot』做一套 `kiln-charm`（窑变陶瓷）风格的图标，品牌色 `#2758D8`，导出 iOS / Android / HarmonyOS。」**

Signet 会自动：

1. **出 4 张小样** — 同一个主体、四种材质世界，让你只做一次选择；
2. **定妆出完整套件** — 锁定你选的风格、材质、光照、调色盘，成套生成；
3. **预检 + 导出** — 检查小尺寸可读性，再一次性导出多平台资产目录、manifest 与预览板。

你也可以更省事，只说「给我一套 UI 界面图标，品牌色 `#0F766E`」——走 UI SVG 轨道，直接产出可换色的线性图标集。

## 29 个视觉样式

一套系统，变化只在材质。29 个样式分四类，覆盖从品牌主图标到界面线性图标的全场景。**完整可交互画廊**见 [在线 Gallery](docs/gallery.html)（仓库开启 GitHub Pages 后可直接在浏览器打开）。

### 立体门面 · 19（品牌主图标 / 功能图标 / 高辨识对象）

<table>
  <tr>
    <td align="center" width="20%"><img src="assets/showcase/styles/kiln-charm.png" width="120"><br><sub>kiln-charm 窑变瓷</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/cobalt-bleed.png" width="120"><br><sub>cobalt-bleed 青花瓷</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/celadon-goldline.png" width="120"><br><sub>celadon-goldline 青瓷金线</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/satin-porcelain.png" width="120"><br><sub>satin-porcelain 缎瓷</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/ridge-enamel.png" width="120"><br><sub>ridge-enamel 珐琅掐丝</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="assets/showcase/styles/cloison-glass.png" width="120"><br><sub>cloison-glass 硬珐琅</sub></td>
    <td align="center"><img src="assets/showcase/styles/prism-layer.png" width="120"><br><sub>prism-layer 分层玻璃</sub></td>
    <td align="center"><img src="assets/showcase/styles/lacquer-seal.png" width="120"><br><sub>lacquer-seal 漆印</sub></td>
    <td align="center"><img src="assets/showcase/styles/knit-craft.png" width="120"><br><sub>knit-craft 钩织</sub></td>
    <td align="center"><img src="assets/showcase/styles/felt-field.png" width="120"><br><sub>felt-field 毛毡</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="assets/showcase/styles/silk-fold.png" width="120"><br><sub>silk-fold 丝绸</sub></td>
    <td align="center"><img src="assets/showcase/styles/carbon-twill.png" width="120"><br><sub>carbon-twill 碳纤斜纹</sub></td>
    <td align="center"><img src="assets/showcase/styles/candy-gloss.png" width="120"><br><sub>candy-gloss 软糖亮甜</sub></td>
    <td align="center"><img src="assets/showcase/styles/soft-molded.png" width="120"><br><sub>soft-molded 哑光软塑</sub></td>
    <td align="center"><img src="assets/showcase/styles/inflate-vinyl.png" width="120"><br><sub>inflate-vinyl 充气</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="assets/showcase/styles/facet-solid.png" width="120"><br><sub>facet-solid 低多边棱面</sub></td>
    <td align="center"><img src="assets/showcase/styles/scene-block.png" width="120"><br><sub>scene-block 等距微世界</sub></td>
    <td align="center"><img src="assets/showcase/styles/layer-paper.png" width="120"><br><sub>layer-paper 层叠纸雕</sub></td>
    <td align="center"><img src="assets/showcase/styles/sumi-bold.png" width="120"><br><sub>sumi-bold 水墨</sub></td>
    <td align="center"></td>
  </tr>
</table>

### 编辑向 · 6（空状态 / 文章配图 / 功能说明 / 品牌叙事）

<table>
  <tr>
    <td align="center" width="20%"><img src="assets/showcase/styles/pomo-splash.png" width="120"><br><sub>pomo-splash 湿墨泼彩</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/brush-block.png" width="120"><br><sub>brush-block 笔刷块面</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/carve-block.png" width="120"><br><sub>carve-block 木刻</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/riso-press.png" width="120"><br><sub>riso-press 孔版印刷</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/cyan-draft.png" width="120"><br><sub>cyan-draft 蓝图白线</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="assets/showcase/styles/contour-single.png" width="120"><br><sub>contour-single 单线等高</sub></td>
    <td align="center"></td>
    <td align="center"></td>
    <td align="center"></td>
    <td align="center"></td>
  </tr>
</table>

### ◆ 旗舰 · 1　与　扁平家族 · 3

<table>
  <tr>
    <td align="center" width="20%"><img src="assets/showcase/styles/nacre-drift.png" width="120"><br><sub>◆ nacre-drift 螺钿虹光</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/gradient-flow.png" width="120"><br><sub>gradient-flow 渐变流向</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/duotone-pop.png" width="120"><br><sub>duotone-pop 双色留白</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/geo-bauhaus.png" width="120"><br><sub>geo-bauhaus 几何原色</sub></td>
    <td align="center" width="20%"></td>
  </tr>
</table>

## 272 个 UI SVG（可换色的界面图标集）

![UI SVG 代表图](assets/showcase/ui-svg-272.png)

UI 轨道包含 **250 个 themed + 22 个 Signet 原创 = 272 个 SVG**，统一为 `24×24 / 2px / round cap / round join / currentColor`，覆盖导航、操作、状态、通信、媒体、文件、商业、平台标记等常用界面场景。

这是「**高频厚库 + 按需生成**」：库里没有的图标，Agent 会用 [`skills/signet/ui/param_engine.py`](skills/signet/ui/param_engine.py) 的矢量原语**现场画一个干净的 SVG** 给你——不靠 imagegen，天然可缩放、可用 CSS `color` 一键换成你的品牌色。

## 想拿它当命令行工具用？（进阶）

Signet 的每个能力也可以脱离 Agent，直接用 Python 跑：

```bash
git clone https://github.com/dososo/blcaptain-signet.git
cd blcaptain-signet
python -m pip install pyyaml Pillow pytest

# 编译一份图标提示词
python skills/signet/scripts/build_prompt.py \
  examples/flowpilot.brief.yaml --style kiln-charm --out /tmp/prompts.md

# 对 1024×1024 母版做质量预检
python skills/signet/scripts/preflight_icon_set.py examples/sample-master.png --json

# 一次导出 8 类平台资产
python skills/signet/scripts/export_icon_assets.py examples/sample-master.png \
  --out /tmp/signet-export --name "FlowPilot" \
  --platforms web,pwa,ios,macos,android,harmonyos,tvos,social \
  --brand-primary "#2758D8" --ios-bg "#F3F0E8" --zip

# 生成品牌色 UI SVG 集
python skills/signet/ui/ui_pipeline.py --color "#0F766E"
```

<table>
  <tr>
    <td width="50%"><img src="assets/showcase/small-size-proof.png" alt="小尺寸可读性"></td>
    <td width="50%"><img src="assets/showcase/platform-exports.png" alt="真实平台导出"></td>
  </tr>
</table>

## 为什么用 Signet

| 你要解决的问题 | Signet 给出的答案 |
|---|---|
| 一组图标像来自不同模板 | 用样式配方和批次锁统一材质、机位、光照与轮廓 |
| 品牌色一换，画面就脏或失焦 | 用角色化调色盘和明度门禁保持第一眼识别 |
| 大图好看，小图不可用 | 用 64px / 32px / 16px 预检检查轮廓、边缘与对比度 |
| 一张母版要手工适配多个平台 | 一次导出 8 类平台目录、manifest、预览板与 zip |
| 产品还需要成套线性 UI 图标 | 提供 272 个 SVG + 按需矢量生成，不靠囤积 |

## Meet Juju · 角色身份锁

<table>
  <tr>
    <td width="50%"><img src="assets/showcase/juju-character.png" alt="Juju 角色身份锁"></td>
    <td width="50%"><img src="assets/examples/example-contact-sheet.png" alt="公开样例联系表"></td>
  </tr>
</table>

Juju 是系统的角色一致性压力测试：白卷比熊、黑眼鼻三角、垂耳、橙围巾。只要它在换材质后漂成普通宠物或毛绒玩具，就说明视觉系统还没锁住。

## 常见问题

<details>
<summary><strong>Signet 会自己调用图像模型吗？</strong></summary>

不会。Signet 编译提示词与视觉约束；图片由你的 Agent（Codex Desktop / Claude Code 等）自带的图像生成能力产出。UI 线性图标则完全用矢量代码生成，不经过 imagegen。
</details>

<details>
<summary><strong>不装进 Agent，能单独用吗？</strong></summary>

能。所有能力都提供 Python CLI（见上方「进阶」），可脱离 Agent 独立运行。
</details>

<details>
<summary><strong>可以只用 UI SVG，不用图片样式吗？</strong></summary>

可以。UI SVG 轨道可独立使用，全部采用 `currentColor`，适合直接内联到前端并用 CSS 换色。
</details>

<details>
<summary><strong>可以商用吗？</strong></summary>

项目代码、文档、样式配方与自有元数据采用 Apache-2.0。第三方 UI glyph 的许可与 notice 见 [`LICENSES.md`](LICENSES.md)；模型生成的图片还需遵守所用模型条款，并自行完成商标与品牌审查。
</details>

## 项目结构

```text
skills/signet/          Skill 本体（SKILL.md）、29 个样式配方、编译器、预检、导出器、UI SVG
.codex-plugin/          Codex 插件清单
assets/                 公开展示画板与样例
docs/                   在线 Gallery 与 29 样式清单
examples/               可运行 brief 与母版样例
scripts/                发布自检
tests/                  回归测试
```

## 参与贡献

提交前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 与 [CLEAN_ROOM.md](CLEAN_ROOM.md)。请勿复制第三方提示词、素材、截图、构图、命名集合或视觉身份。

## 作者

由 **爆裂队长NEXT** 创建与维护。

- GitHub：[@dososo](https://github.com/dososo)
- X：[@thinkszyg](https://x.com/thinkszyg)
- 工作邮箱：[blteam2026@outlook.com](mailto:blteam2026@outlook.com)
- 问题反馈：[dososo/blcaptain-signet Issues](https://github.com/dososo/blcaptain-signet/issues)

## 许可

Apache License 2.0。详见 [LICENSE](LICENSE)、[NOTICE.md](NOTICE.md) 与 [LICENSES.md](LICENSES.md)。
