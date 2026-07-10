# Signet 风格宇宙目录

本目录按 v2/v3 设计契约重生成。当前可编译的新宇宙为 **22 个 v3 风格**：12 个 flagship + 10 个 support。另有 5 个 roadmap 仅命名，尚未落 YAML。旧 24 个 id 保留为 deprecated alias，调用旧 id 会重定向到目标 v3 风格并输出弃用提示。

硬约束：

- 玻璃预算恰好 2 个：`cloison-glass` 与 `prism-layer`。
- 其余风格均为非玻璃材质，不在正向材质中使用 glow / gel / crystal / chrome / translucent / specular 等泛光泽词。
- 所有命名与配方为 Signet 原创；只使用公共工艺和材质原则，不复制第三方命名集、prompt、图片、构图或资产。
- 预筛与 lint 只做机器检查，不声称自动法律清关、商标安全或审美保证；仍需要人工审查。

## 12 个 Flagship

| # | id | 中文名 | 排他材质 | light_model | character_fit | 迁移吸收 |
|---:|---|---|---|---|---|---|
| 1 | `draft-line` | 手绘草线 | 石墨/墨线在无涂层纸上，零填充 | `none-flat` | native | `vector-signal`, `mono-emblem` |
| 2 | `press-relief` | 压印浮雕 | 棉纸深压凹/盲压 | `recessed-shadow` | capable | `letterpress-badge` |
| 3 | `ridge-enamel` | 软珐琅 | 金属凸线 + 哑光珐琅色区 | `metal-ridge-glint` | capable | `brass-inlay` |
| 4 | `cloison-glass` | 硬珐琅琉璃 | 抛平硬珐琅 + 金属细胞线 | `controlled-specular` | capable | `jade-lens` |
| 5 | `prism-layer` | 分层琉璃 | 2-4 层分离液态玻璃深度 | `layer-refraction` | object-only | `aurora-gradient`, `hologram-plate` |
| 6 | `felt-field` | 羊毛毡 | 针毡羊毛，完全不透明、漫反射 | `fully-diffuse` | native | `foam-object` |
| 7 | `carve-block` | 木刻版画 | 纸上凸版哑光油墨，两色高反差 | `none-flat` | native | `ink-seal` 部分吸收 |
| 8 | `facet-solid` | 低多边形 | 不透明多面体，每个面单一平色 | `discrete-facet-steps` | capable | `prism-gel`, `data-crystal`, `folded-signal` |
| 9 | `cyan-draft` | 蓝图 | 普鲁士蓝底上的白/负形工程线 | `none-flat` | object-only | `blueprint-grid` |
| 10 | `riso-grain` | 孔版印刷 | 半不透明专色油墨吸收进哑光纸 | `none-flat` | native | `mosaic-tile` |
| 11 | `carbon-twill` | 碳纤斜纹 | 哑光 2/2 碳纤维斜纹编织 | `anisotropic-grain-streak` | object-only | `carbon-core` |
| 12 | `lacquer-seal` | 漆印 | 不透明深色漆面 + 印章式刻凹 | `recessed-shadow` | capable | `ink-seal` |

## 10 个 Support

| id | 中文名 | 排他材质 | light_model | character_fit | 迁移吸收 |
|---|---|---|---|---|---|
| `brushed-alloy` | 拉丝金属 | 阳极氧化铝，单向拉丝纹 | `anisotropic-grain-streak` | object-only | `liquid-metal-mark` |
| `matte-clay` | 黏土 | 不透明粉彩黏土，膨胀圆胖、哑光 | `fully-diffuse` | native | `soft-capsule`, `rubber-toy` |
| `layer-paper` | 层叠纸雕 | 哑光卡纸切片堆叠 | `inter-layer-cast-shadow` | native | `luminous-paper` |
| `satin-porcelain` | 柔瓷 | 不透明陶瓷体上的柔釉积色 | `fully-diffuse` | capable | `bio-sprout` |
| `pixel-grid` | 像素格 | 粗网格不透明方形像素单元 | `none-flat` | capable | `pixel-charm` |
| `contour-map` | 等高线 | 平面底上的等距嵌套等高线 | `none-flat` | object-only | `topographic-flow` |
| `silk-fold` | 绸缎褶 | 编织绸缎布料与褶向柔光 | `anisotropic-grain-streak` | capable | `silk-ribbon` |
| `scene-block` | 场景块 | 不透明哑光等距实体块 | `occlusion-elevation` | capable | `isometric-miniworld` |
| `ink-wash` | 水墨 | 吸水纸上的水性墨洗、湿晕与枯笔 | `none-flat` | native | 新增 |
| `celadon-goldline` | 青绿描金 | 米白宣纸上的青绿/靛蓝平涂色域 + 哑光描金细线 | `none-flat` | capable | 作者自有文化风格 |

## 母题库

`references/motif-library.md` 是 clean-room 母题 resolver，可作为 `celadon-goldline`、`lacquer-seal`、`carve-block` 的 object_archetype 来源。它只记录原创措辞的母题名称、公开寓意、配色和图标化提炼建议；未 bundle 任何 CC BY-NC 图片、数据集文案或派生素材。`wenyang.net` 仅作为外部可选资源。

## 5 个 Roadmap

这些 id 已命名但未落 YAML，不能作为当前 `--style` 使用。

| id | 中文名 | 规划定位 |
|---|---|---|
| `chrome-knot` | 镜面铬结 | 真实镜面铬材质，暂缓以避免光泽预算失控 |
| `chalk-board` | 黑板粉笔 | 深底浅色粉笔粉尘线条，是 line family 的深底语境工具 |
| `rubber-matte` | 哑胶 | 去光泽 soft-touch 哑光橡胶，后续可承接旧 rubber-toy 的一部分需求 |
| `wire-frame` | 线框网格 | 透明网格边线，仅拓扑边线，不承载玻璃材质 |
| `grid-mosaic` | 马赛克 | 哑光 tesserae + grout 缝隙，与 pixel-grid 的干净方格区分 |

## Deprecated / 迁移别名

旧 id 仍可传给 `--style`，但会输出弃用提示并使用目标 v3 风格编译。

| 旧 id | 目标 v3 id | 迁移类型 |
|---|---|---|
| `aurora-gradient` | `prism-layer` | retire |
| `prism-gel` | `facet-solid` | retire |
| `data-crystal` | `facet-solid` | retire |
| `hologram-plate` | `prism-layer` | retire |
| `carbon-core` | `carbon-twill` | retire |
| `brass-inlay` | `ridge-enamel` | rebuild |
| `bio-sprout` | `satin-porcelain` | rebuild |
| `luminous-paper` | `layer-paper` | rebuild |
| `soft-capsule` | `matte-clay` | rebuild |
| `rubber-toy` | `matte-clay` | rebuild |
| `mosaic-tile` | `riso-grain` | rebuild |
| `liquid-metal-mark` | `brushed-alloy` | rebuild |
| `jade-lens` | `cloison-glass` | downgrade |
| `foam-object` | `felt-field` | merge |
| `mono-emblem` | `draft-line` | merge |
| `vector-signal` | `draft-line` | merge |
| `blueprint-grid` | `cyan-draft` | upgrade |
| `folded-signal` | `facet-solid` | upgrade |
| `ink-seal` | `lacquer-seal` | upgrade |
| `isometric-miniworld` | `scene-block` | upgrade |
| `letterpress-badge` | `press-relief` | upgrade |
| `pixel-charm` | `pixel-grid` | upgrade |
| `topographic-flow` | `contour-map` | upgrade |
| `silk-ribbon` | `silk-fold` | upgrade |

## 选型提示

- Juju / 角色原生：优先 `draft-line`，其次按材质选择 `felt-field`、`matte-clay`、`riso-grain`、`ink-wash`。
- 技术、开发者、系统工具：`cyan-draft`、`brushed-alloy`、`carbon-twill`、`scene-block`。
- 纸张、出版、知识工具：`draft-line`、`press-relief`、`layer-paper`、`riso-grain`、`ink-wash`。
- 高级徽章/工艺：`ridge-enamel`、`lacquer-seal`、`satin-porcelain`、`cloison-glass`、`celadon-goldline`。
- 玻璃/系统层级：只用 `cloison-glass` 或 `prism-layer`，不得新增第三个玻璃风格。
- 像素/地图/平面语法：`pixel-grid`、`contour-map`、`cyan-draft`。
- 传统母题/文化解释：`celadon-goldline`，母题来源走 `references/motif-library.md`，不得复制具体文物或外部纹样素材。
