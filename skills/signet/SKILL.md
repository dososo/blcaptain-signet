---
name: signet
description: >-
  开源、clean-room 的图标视觉系统 skill。用于把用户一句自然语意图编排成同一材质世界里的 app icon、
  app_icon_boxed、sticker、overlay、favicon、thumbnail、expression_sheet 或 editorial_scene prompt，
  并在确认后导出多平台资产。feature_icon、hero_object、empty_state、marketing_visual 等只作为通用
  prompt fallback 处理，不是当前编译器的专用 asset_type 分支。不用于带字 logo/wordmark、照片编辑、
  或模仿现有品牌身份。
license: Apache-2.0
---

# Signet · 图标视觉系统

Signet 是 clean-room、开源的图标视觉系统：用户用一句自然语说明想做什么，skill 负责推断主体、推荐材质世界、编译 prompt、组织预览、跑预检，并在确认后导出平台资产。

本文件的职责是编排流程，不改写 style YAML、Python 脚本或平台契约。

## 何时触发

- 用户要做 app icon、favicon、贴纸、表情包、编辑插画场景或一组同风格图标。
- 用户说“给我的产品做一套图标视觉”“用某个 Signet 风格生成 prompt”“导出到 iOS / Android / HarmonyOS / PWA / macOS”等。
- 用户给出一批功能项，并要求同一材质、同一光照、同一调色盘。

## 何时不要触发

- 带文字的 logo、wordmark、商标字标。
- 用户要求编辑真人照片、复刻某品牌图标、模仿第三方视觉身份。
- 用户只想要普通矢量 icon 字体或现成 SVG 包。

## 公开样式目录

Signet 1.0.0 提供 29 个可执行样式配方：19 个门面、6 个编辑、1 个旗舰与 3 个扁平样式。完整 ID 和分类以 `docs/STYLE_LEDGER.md` 为准。

- 门面用于品牌主图标、功能图标与高辨识度对象。
- 编辑用于空状态、文章插画、功能说明与品牌叙事。
- `nacre-drift` 旗舰适合珍宝、器物、漆面、扇面和簪饰等窄题材。
- 扁平组用于紧凑、高对比、偏图形语言的界面场景。

执行时必须读取本地 `skills/signet/styles/<id>.yaml` 的 `positioning`、材质约束、原生题材域和禁区。不得脱离本地配方硬编 prompt。

## Juju 角色锁

Juju 的身份锁固定为：白卷比熊、黑眼鼻三角、垂耳、橙围巾。

Juju 的默认 home 是 `knit-craft`，官方备选是 `felt-field`。角色相关请求优先走这两个织物方向；不要把其它旧方向写成 launch home。

## 输入原则

首轮预览前不要强制用户先选 style 或 platform。用户一句话足够开始：

- 从自然语推断产品类型、hero 主体、气质词、资产范围和候选风格池。
- 只有硬约束确实不可知时才停下问，例如必须包含某个监管符号但用户没给范围。
- 高级控制延后到第二阶段或导出确认 gate：平台、尺寸、seed、zip、背景色、是否全平台。

支持的专用 `asset_type` 只按编译器真实分支宣传：

`app_icon` / `app_icon_boxed` / `sticker` / `overlay` / `favicon` / `thumbnail` / `expression_sheet` / `editorial_scene`

其它常见产品面，例如 `feature_icon`、`feature_icon_set`、`hero_object`、`empty_state`、`marketing_visual`、`social_visual`，可以作为通用 prompt fallback 或 batch 用途描述，但不能宣称有专用编译器分支。

## 两段式漏斗

### Stage 1：风格小样板

目标：便宜、快、零追问，让用户只做一个选择。

- [ ] 解析用户自然语意图；首轮预览前零追问（除非硬约束不可知）
- [ ] 推断 hero 主体 + 候选风格池（读各 YAML positioning 匹配，别硬编）
- [ ] 选 4 个候选风格，标 1 个「推荐」/ recommended
- [ ] 同一主体生成 4 张小样 -> 2×2 board / 2x2 board，大白话标签（如「窑变瓷·温润」，不要写技术黑话）
- [ ] 用户只挑 1 个风格（pick one）

执行要求：

- 4 张小样必须使用同一 hero 主体，只换材质世界。
- 候选标签用用户能理解的话，不用内部参数名堆砌。
- 推荐项要说明一句理由，例如“更符合温暖可信”或“更适合小尺寸识别”。
- 用户不满意时，可以重选 4 个候选；不要直接全平台导出多个风格。

### Stage 2：定妆全量

目标：只对用户选中的一个风格做完整套件。

- [ ] 锁定该风格 + palette（5-role，可自选色值）-> 生成完整套件（只用该风格原生题材）
- [ ] 跑 preflight；失败项有限重掷 <=2 / 重掷 ≤2；仍不过标人工，绝不静默交废图
- [ ] 【确认 gate】高成本全平台导出前停一次问
- [ ] 移动端默认平台含 iOS + Android + HarmonyOS

执行要求：

- 锁定后不要混入其它材质世界。
- 一组图标必须复用同一个风格、材质、光向、调色盘、镜头和背景策略。
- preflight 是机器预筛，不是最终审美或法律保证；失败后可按同 prompt 换 seed 有限重掷，最多 2 次。
- 仍不过的图必须标为人工检查，不得混进交付包。

### UI SVG 轨道：成套界面图标

当用户意图是**成套 UI 界面图标**（设置页、导航、工具栏、状态、文件操作等），而不是品牌材质 app icon、Juju 场景或营销插画时，走 **UI SVG 轨道**。UI 线性图标不用 imagegen；它们必须由现有 Lucide 矢量或 `param_engine.py` 的代码原语生成。

定位：库不求囤满。先用固定 Lucide 高频厚库覆盖通用语义；范围外的 glyph 由 Codex 现场新增 `draw_*` 函数、注册 `CustomGlyph`，再运行 `param_engine.py` 按需生成。禁止粘贴第三方 SVG path 后冒充原创。

视觉说明：UI 图标是单色 `currentColor` 描边，统一为 24×24、2px、round cap / join。品牌色由前端 CSS `color` 驱动，不把 hex 写死进 SVG。

当前覆盖清单：250 个 Lucide themed + 22 个 Signet custom = 272 个 SVG。覆盖导航与方向、操作与编辑、状态与反馈、通信与媒体、媒体与设备、文件与数据、商业与安全、平台导出和 Signet 专属工具；清单外语义按需补齐。

#### UI SVG 按需执行 checklist

- [ ] 识别意图：确认这是 UI 线性图标集，而不是材质 app icon / 插画轨道。
- [ ] 说明形式：先告诉用户“本轨道输出单色 `currentColor` 描边 SVG，可随 CSS 换色，不调用 imagegen”。
- [ ] 主动问品牌色：只问 1 个品牌主色 hex，推荐话术为“请给我一个品牌主色 hex，例如 `#0F766E`”；只有明确需要 hover / active 多态时，才追加询问 palette JSON。
- [ ] 确认图标范围：列出用户所需 glyph，并对照上面的覆盖清单；已有项走 Lucide themed，缺失项现场用 `param_engine.py` 手写矢量原语并注册。
- [ ] 生成与校验：运行 `param_engine.py` 重建 custom SVG / manifest，再运行 `ui_pipeline.py` 输出合并 SVG 集、逐 glyph manifest 和自包含预览；核对 themed / custom / total 与实际文件数一致。
- [ ] 许可证门禁：Lucide/Feather 逐 glyph 保留 source、ISC/MIT、notice 与 derivative statement；Signet custom 逐 glyph 标 Apache-2.0 和原创声明。
- [ ] 交付说明：推荐前端内联 SVG，通过 CSS `color` + `currentColor` 换色；同时给出合并 manifest 与本地 `index.html` 预览路径。

诚实边界：这是**固定 permissive Lucide 高频厚库 + Signet 自制参数 glyph + 按需补齐**，不是“原创 500 大库”。合并输出由 `skills/signet/ui/ui_pipeline.py` 生成 manifest 和自包含预览：

```bash
python skills/signet/ui/ui_pipeline.py --color "#0F766E"
```

## 脚本边界

以下 4 个脚本是可直接运行的 CLI。命令从工程根目录执行。

### 单个 prompt

```bash
python skills/signet/scripts/build_prompt.py <brief.yaml> --style <id> --out prompts.md
```

用途：把一个 brief 与一个 style YAML 编译成 prompt bundle。

### 批量 prompt

```bash
python skills/signet/scripts/build_batch_prompts.py <batch.yaml> --style <id> --out batch.md
```

用途：为一组图标生成共享 lock 的 batch prompt。不要手写每个图标的独立风格 prompt。

### 预检

```bash
python skills/signet/scripts/preflight_icon_set.py *.png [--want-transparent] [--json]
```

用途：检查机器可筛的问题，例如小尺寸可读性、居中、安全区、背景和调色盘。它返回预检状态，但仍需要人工检查隐喻、商标风险、文字、风格忠实度和审美质量。

### 多平台导出

```bash
python skills/signet/scripts/export_icon_assets.py MASTER.png --out dist --name "<Project>" --platforms web,pwa,ios,macos,android,harmonyos,tvos,social --ios-bg "<hex>" --brand-primary "<hex>" --seed "<seed>" --zip
```

用途：从 master PNG 导出平台资产。全平台导出前必须经过确认 gate。移动 app 默认平台至少包含 `ios,android,harmonyos`；tvOS 只在 TV/大屏意图明确时默认加入。

`palette_engine.py`、`taste_laws.py`、`gallery.py` 是被脚本或测试调用的库能力，不是用户 CLI。不要把它们写成让用户直接运行的命令。

## 硬规则

- 图标不包含文字、字母、wordmark、假 logo、水印或 UI 截图；`editorial_scene` 只能把短标签当作纸张等实体道具处理。
- 不做商标近似；可能暗示品牌的主体必须抽象化。
- clean-room only；不复制第三方 prompt、图、构图或品牌身份。
- 单焦点、居中、24-32px 可读；宁可删细节，不堆复杂度。
- 每个风格只用自己的原生题材域，不跨材质乱混。
- 不声称自动法律清关，也不声称机器预检等于审美保证。

## 真实限制

- 图像模型输出的是 raster 图，不是原生 SVG。
- 透明、尺寸、平台输出能力取决于图像模型与本地 exporter；不能把平台导出说成原生矢量生成。
- iOS Liquid Glass 分层 `.icon` 不是当前 exporter 能力；可导出扁平 fallback。
- MASTER 画布与平台规格是否完全合规，要按现有 gate 和人工复核判断；失败不得静默交付。

## 目录提示

- `skills/signet/styles/*.yaml`：风格配方、定位、材质锁、负向约束。
- `skills/signet/references/`：style system、schema、prompt compiler、brand kit、QA、输出规范、clean-room。
- `skills/signet/scripts/`：4 个 CLI + 3 个库模块。
- `examples/`：brief、batch 和 sample master 示例。
