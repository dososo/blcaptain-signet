# Signet · 让一整套图标，一眼就是「你」

<p align="center"><strong>中文</strong> · <a href="README.en.md">English</a></p>

> 不是又一个图标库，也不是又一个 AI 图标生成器。Signet 是**图标的品牌身份系统**——你说一句话，它让你从 App 图标到界面线性图标的一整套图标，都像出自同一个品牌，而不是十个不同模板拼起来的。

![Signet 全系统展示](assets/showcase/hero-signet.png)

<p align="center">
  <img src="https://img.shields.io/badge/样式-29_套-c8553d.svg" />
  <img src="https://img.shields.io/badge/UI_SVG-272_个-2f5ea7.svg" />
  <img src="https://img.shields.io/badge/导出平台-8_类-2b2622.svg" />
  <img src="https://img.shields.io/badge/Agent-Skill-d98e3a.svg" />
  <img src="https://img.shields.io/badge/License-Apache--2.0-4c8a5b.svg" />
</p>

> **安装**：对你的 Agent（Codex Desktop / Claude Code…）说 ——「帮我安装这个 Skill：`github.com/dososo/blcaptain-signet`」

---

## 为什么要做它

一个 App 从 0 做到上线，图标是最容易「露馅」的地方：主图标找了个设计师画，功能图标外包了一批，空状态插画随手 AI 生了几张，界面里的小图标又抓了套开源线性图标——**单看每个都行，放一起就像来自十个不同的团队。**

再往下还有三个坑：

- **换个品牌色，画面就脏。** 大多数图标经不起换色，一改主色就失焦、发灰、撞色。
- **大图好看，小图糊成一团。** 32px 一缩，轮廓塌了、细节糊了、认不出了。
- **一张图要手工适配 8 个平台。** iOS 圆角、Android 自适应、HarmonyOS、手表、社交预览……一个个导出到手酸。

问题的根子是：**大多数工具解决的是「画一个图标」，而真正难的是「让一整套图标始终是同一个你」。** 前者是绘图问题，后者是**身份问题**——和 logo、VI、品牌手册是同一件事。

Signet 把「身份」这件事，变成 AI 能稳定复用的能力：把材质、轮廓、光照、镜头、调色、批次一致性，全部固化成**配方与常量**。AI 不自由发挥，只在被验证过的「材质世界」里填你的内容，所以出来的一整套，稳定地是同一个品牌。

> 底气一句话：**好看不是玄学，是可以写进代码的常量。** 字号差多少、留白留多少、明度不够就打回、64px 认不出就不算过——都是硬门禁，不靠运气。

## 不是又一个 X

| 它**不是** | 它**是** |
|---|---|
| ❌ 又一个图标素材库（下载完还是拼凑） | ✅ 一套让你所有图标**共享同一身份**的系统 |
| ❌ 又一个「输入文字出图」的生成器 | ✅ 编排提示词 + 锁材质 + 质检 + 多平台导出的**中间层** |
| ❌ 一套滤镜套所有内容 | ✅ 29 个各有灵魂的**材质世界**，每个都是一种物理，不是换皮 |
| ❌ 自己偷偷调模型生图 | ✅ 图由**你的 Agent 生图能力**产出，Signet 只负责让它成套、能用、能上线 |

## 它能给你什么（效果）

| 维度 | 内容 |
|---|---|
| **材质样式** | **29 套经过验证的视觉样式**（立体门面 19 / 编辑向 6 / 旗舰 1 / 扁平 3），每套都是一种材质物理，不是滤镜 |
| **调色** | 每次请求**独立生成 5-role 调色盘**（primary/secondary/tertiary/accent/detail），换品牌色也不脏、不失焦 |
| **UI 图标** | **272 个界面 SVG**（250 themed + 22 原创）+ **按需矢量生成**：库里没有的现场画一个干净 SVG，不靠囤积 |
| **角色一致性** | Juju 角色身份锁——换材质不能漂成别的宠物，这是系统的**压力测试** |
| **小尺寸** | 64px / 32px / 16px 预检，轮廓塌了、糊了就打回，不放行 |
| **多平台** | 一张母版一次导出 **Web / PWA / iOS / Android / macOS / HarmonyOS / tvOS / Social**，带 manifest、预览板、zip |

## 独家优势

别的图标工具大多是「一套模板套所有」，结果满屏一个味。这套不一样：

1. **29 个材质世界，各有物理** —— 窑变瓷的开片、钩织的线脚、珐琅的掐丝、纸雕的层影……不是给图标换个颜色，是给它**换一种材料**。同一个主体换材质，气质完全不同，但都是「一套系统」。
2. **换品牌色不脏的秘密** —— 颜色不是随便填的 hex，而是被分成 5 个角色（主体色、暗部锚点、点睛色…），每个角色有固定职责 + 明度门禁。所以你换主色，画面只会换气质，不会变脏。
3. **Juju 身份锁** —— 一只白卷比熊，换 29 种材质都必须还是它（黑眼鼻三角、垂耳、橙围巾）。**只要它漂成普通宠物，就说明视觉系统还没锁住。** 这是别人没有的一致性标尺。
4. **UI 图标「按需生成」而非「囤积」** —— 不追求囤满 1500 个。库里没有的，Agent 用矢量原语**现场画一个**给你，天然可缩放、可换色，和主题化的 250 个无缝一致。
5. **每次都稳定** —— 明度阈值、64px 可读、批次锁、边缘安全区，全是代码门禁。不过就打回，不靠模型今天心情好。
6. **Clean-room 干净出身** —— 不复制任何第三方的名字、提示词、图、构图、命名集合。主仓 Apache-2.0，第三方 glyph 逐个署名。

## 29 个视觉样式

一套系统，变化只在材质。**完整可交互画廊** 👉 [在线 Gallery](https://dososo.github.io/blcaptain-signet/docs/gallery.html)（浏览器直接打开，可交互查看全部 29 套）。

### 立体门面 · 19（品牌主图标 / 功能图标 / 高辨识对象）

<table>
  <tr>
    <td align="center" width="20%"><img src="assets/showcase/styles/kiln-charm.png" width="118"><br><sub>kiln-charm 窑变瓷</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/cobalt-bleed.png" width="118"><br><sub>cobalt-bleed 青花瓷</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/celadon-goldline.png" width="118"><br><sub>celadon-goldline 青瓷金线</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/satin-porcelain.png" width="118"><br><sub>satin-porcelain 缎瓷</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/ridge-enamel.png" width="118"><br><sub>ridge-enamel 珐琅掐丝</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="assets/showcase/styles/cloison-glass.png" width="118"><br><sub>cloison-glass 硬珐琅</sub></td>
    <td align="center"><img src="assets/showcase/styles/prism-layer.png" width="118"><br><sub>prism-layer 分层玻璃</sub></td>
    <td align="center"><img src="assets/showcase/styles/lacquer-seal.png" width="118"><br><sub>lacquer-seal 漆印</sub></td>
    <td align="center"><img src="assets/showcase/styles/knit-craft.png" width="118"><br><sub>knit-craft 钩织</sub></td>
    <td align="center"><img src="assets/showcase/styles/felt-field.png" width="118"><br><sub>felt-field 毛毡</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="assets/showcase/styles/silk-fold.png" width="118"><br><sub>silk-fold 丝绸</sub></td>
    <td align="center"><img src="assets/showcase/styles/carbon-twill.png" width="118"><br><sub>carbon-twill 碳纤斜纹</sub></td>
    <td align="center"><img src="assets/showcase/styles/candy-gloss.png" width="118"><br><sub>candy-gloss 软糖亮甜</sub></td>
    <td align="center"><img src="assets/showcase/styles/soft-molded.png" width="118"><br><sub>soft-molded 哑光软塑</sub></td>
    <td align="center"><img src="assets/showcase/styles/inflate-vinyl.png" width="118"><br><sub>inflate-vinyl 充气</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="assets/showcase/styles/facet-solid.png" width="118"><br><sub>facet-solid 低多边棱面</sub></td>
    <td align="center"><img src="assets/showcase/styles/scene-block.png" width="118"><br><sub>scene-block 等距微世界</sub></td>
    <td align="center"><img src="assets/showcase/styles/layer-paper.png" width="118"><br><sub>layer-paper 层叠纸雕</sub></td>
    <td align="center"><img src="assets/showcase/styles/sumi-bold.png" width="118"><br><sub>sumi-bold 水墨</sub></td>
    <td align="center"></td>
  </tr>
</table>

### 编辑向 · 6（空状态 / 文章配图 / 功能说明 / 品牌叙事）

<table>
  <tr>
    <td align="center" width="20%"><img src="assets/showcase/styles/pomo-splash.png" width="118"><br><sub>pomo-splash 湿墨泼彩</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/brush-block.png" width="118"><br><sub>brush-block 笔刷块面</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/carve-block.png" width="118"><br><sub>carve-block 木刻</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/riso-press.png" width="118"><br><sub>riso-press 孔版印刷</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/cyan-draft.png" width="118"><br><sub>cyan-draft 蓝图白线</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="assets/showcase/styles/contour-single.png" width="118"><br><sub>contour-single 单线等高</sub></td>
    <td align="center"></td><td align="center"></td><td align="center"></td><td align="center"></td>
  </tr>
</table>

### ◆ 旗舰 · 1　与　扁平家族 · 3

<table>
  <tr>
    <td align="center" width="20%"><img src="assets/showcase/styles/nacre-drift.png" width="118"><br><sub>◆ nacre-drift 螺钿虹光</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/gradient-flow.png" width="118"><br><sub>gradient-flow 渐变流向</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/duotone-pop.png" width="118"><br><sub>duotone-pop 双色留白</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/geo-bauhaus.png" width="118"><br><sub>geo-bauhaus 几何原色</sub></td>
    <td align="center" width="20%"></td>
  </tr>
</table>

## 272 个 UI SVG（可换色的界面图标集）

![UI SVG 代表图](assets/showcase/ui-svg-272.png)

**250 themed + 22 Signet 原创 = 272 个 SVG**，统一 `24×24 / 2px / round / currentColor`，覆盖导航、操作、状态、通信、媒体、文件、商业、平台标记。库里没有的图标，Agent 用 [`param_engine.py`](skills/signet/ui/param_engine.py) 的矢量原语**现场画一个**——不靠 imagegen，天然可缩放，CSS `color` 一键换品牌色。

## Juju · 角色身份锁

<table>
  <tr>
    <td width="50%"><img src="assets/showcase/juju-character.png" alt="Juju 角色身份锁"></td>
    <td width="50%"><img src="assets/examples/example-contact-sheet.png" alt="公开样例联系表"></td>
  </tr>
</table>

白卷比熊、黑眼鼻三角、垂耳、橙围巾。它是系统的**一致性压力测试**：只要它换一种材质就漂成普通宠物、毛绒玩具或随机小动物，说明这套视觉系统还没锁住。锁住了，它换 29 种材料都还是它。

## 适合 / 不适合

**适合**：品牌 App 主图标 · 成套功能图标 · 空状态与引导插画 · 产品视觉身份 · 成套界面线性图标 · 多平台图标导出 · 需要长期保持一致的图标体系。

**不适合**（会直说、劝你换工具）：带文字的 logo / wordmark / 商标字标 · 编辑真人照片 / 磨皮换脸 · 复刻某个现有品牌的图标 · 没有一致性诉求的单张随手图。**一个什么都能做的工具，通常什么都做不好。**

## 内容 → 材质（怎么挑样式）

| 你的产品气质 | 建议材质 |
|---|---|
| 温润、手作、生活方式、文化 | 陶瓷之家（kiln-charm / cobalt-bleed / celadon）· 织物之家（knit / felt / silk） |
| 精致、高端、珠宝 / 工艺感 | 珍宝阁（ridge-enamel / cloison-glass / prism-layer / ◆nacre-drift） |
| 亲和、玩趣、消费级 App | 软触感（candy-gloss / soft-molded / inflate-vinyl） |
| 科技、工具、效率产品 | 几何之家（facet-solid / scene-block / cyan-draft） |
| 编辑、内容、叙事场景 | 墨与纸（sumi-bold / pomo-splash / brush-block / carve-block） |
| 现代、扁平、界面图形语言 | 扁平家族（gradient-flow / duotone-pop / geo-bauhaus） |
| 只要成套线性 UI 图标 | UI SVG 轨道，一句话出品牌色图标集 |

## 哪些 Agent 能用

不绑定某一个 Agent。**只要你的 Agent 支持 Skill（能读取本地 skill 目录），就能用：**

| Agent | 支持方式 |
|---|---|
| **Codex Desktop**（主要目标平台） | 自带 [`.codex-plugin/plugin.json`](.codex-plugin/plugin.json)，用其内置生图出图 |
| **Claude Code** | 放入 `~/.claude/skills/` |
| Cursor / Gemini CLI / 其他支持 Skill 的 Agent | 通用方式 |

> 图片由你的 Agent 生图能力产出；UI 线性图标是矢量代码生成，不需要生图。

## 安装

```bash
# 通用方式（推荐）：让 Agent 帮你装
npx skills add dososo/blcaptain-signet -g

# 或手动克隆到你 Agent 的 skills 目录
git clone https://github.com/dososo/blcaptain-signet.git
# Codex Desktop：  cp -R blcaptain-signet ~/.agents/skills/
# Claude Code：    cp -R blcaptain-signet ~/.claude/skills/

# 想脱离 Agent 单独用 CLI，装一次依赖
python -m pip install pyyaml Pillow pytest
```

## 怎么用（对话式，30 秒上手）

安装好后，在你的 Agent 里直接说人话：

> **「给我的 App『FlowPilot』做一套 `kiln-charm`（窑变陶瓷）风格的图标，品牌色 `#2758D8`，导出 iOS / Android / HarmonyOS。」**

Signet 会：**出 4 张小样让你挑 → 锁定风格出完整套件 → 小尺寸预检 → 一次导出多平台**。

不满意随时改：直接说「换个材质 / 颜色太闷 / 这个太复杂 / 图标再大点」。

## 工作流：选材质 → 出图 → 上线

```text
一句话说你要什么
   ↓ 推断主体 + 推荐 4 个候选材质
挑 1 个材质 + 品牌色
   ↓ 编译视觉契约 + 批次一致性锁
你的 Agent 生成 1024×1024 母版
   ↓ 预检：轮廓 / 对比度 / 边缘 / 64px 可读
一次导出 Web / PWA / iOS / Android / macOS / HarmonyOS / tvOS / Social
```

想当命令行工具用（脱离 Agent）：`build_prompt.py`（编译提示词）· `preflight_icon_set.py`（母版预检）· `export_icon_assets.py`（多平台导出）· `ui_pipeline.py`（UI SVG 出品牌色集）。

## 设计原则

- **单焦点、居中、64px 可读** —— 宁可删细节，不堆复杂度。看不清就不算过。
- **材质圣经** —— 每个样式只用自己的原生材质与物理，不跨材质乱混。
- **约束即工艺** —— 材质痕迹（切边、air gap、掐丝）由结构生成，不是表面滤镜。
- **留白限色** —— 主体集中，背景安静，颜色受限；给无限选择只会更容易做丑。
- **明度门禁** —— 暗部锚点唯一、亮部够亮，换色不塌。
- **Clean-room** —— 只学公开工艺原理，不复制任何第三方素材、命名与身份。

## 后续计划（Roadmap）

- **UI 图标扩容** —— themed 高频集持续扩，评估接入 Phosphor 等 permissive 集。
- **建造中样式转正** —— `press-relief`（活版压印）等 spike 冲小尺寸可读性，达标即并入。
- **导出增强** —— 跟进平台新规范（如 iOS 分层 `.icon`），补齐更多适配形态。
- **更多材质世界** —— 在保持「一套系统」的前提下，谨慎扩充有辨识度的新材质。

## FAQ

<details>
<summary><strong>Signet 会自己调用图像模型吗？</strong></summary>

不会。Signet 编译提示词与视觉约束；图片由你的 Agent 生图能力产出。UI 线性图标完全用矢量代码生成，不经过 imagegen。
</details>

<details>
<summary><strong>它和「找个图标库下载」有什么区别？</strong></summary>

图标库给你一堆现成图标，拼起来还是拼起来。Signet 给你的是「身份」——同一套材质、调色、光照规则贯穿你所有图标，换品牌色、换尺寸、换平台，都还是同一个你。
</details>

<details>
<summary><strong>可以只用 UI SVG，不用图片样式吗？</strong></summary>

可以。UI SVG 轨道独立可用，全部 `currentColor`，适合直接内联前端 + CSS 换色。
</details>

<details>
<summary><strong>可以商用吗？</strong></summary>

代码、文档、样式配方与自有元数据采用 Apache-2.0。第三方 UI glyph 许可见 [`LICENSES.md`](LICENSES.md)；模型生成的图片还需遵守所用模型条款，并自行完成商标与品牌审查。
</details>

## 关于作者

由 **爆裂队长NEXT** 创建与维护。

- GitHub：[@dososo](https://github.com/dososo) · X：[@thinkszyg](https://x.com/thinkszyg)
- 工作邮箱：[blteam2026@outlook.com](mailto:blteam2026@outlook.com)
- 反馈：[Issues](https://github.com/dososo/blcaptain-signet/issues)

## License

Apache License 2.0。详见 [LICENSE](LICENSE)、[NOTICE.md](NOTICE.md) 与 [LICENSES.md](LICENSES.md)。
