# Signet Clean-Room Motif Library

用途：这是一个传统母题 resolver，用于把用户输入的文化母题转成 Signet 风格的 icon object_archetype。它服务于 `celadon-goldline`、`lacquer-seal`、`carve-block`，也可给 `draft-line` 做解释性草图。

边界：

- 本表只使用公共领域中的母题名称与通用寓意，不复制任何具体文物、纹样数据集、图片、提示词、构图或说明文案。
- 作者可参考自有资料；`wenyang.net` 仅作为外部可选资源，不 bundle 其 CC BY-NC 4.0 图片、文本或派生素材。
- 生成时必须抽象为“单一母题姿态”，避免复刻具体纹样、器物、碑帖、馆藏或当代设计作品。

| CN 母题 | EN Resolver | 公开寓意 | 典型传统配色 | 24px icon 化提炼建议 | 适配风格 |
|---|---|---|---|---|---|
| 缠枝莲 | lotus-scroll | 连绵、生长、清雅 | 青绿、靛蓝、米白、描金 | 保留一条 S 形藤蔓和一朵侧向莲，不做连续满铺 | celadon-goldline, carve-block |
| 回纹 | key-fret | 秩序、回环、边界 | 靛蓝、米白、描金、墨 | 抽成单个折返角或方形回环，不画长边框 | celadon-goldline, lacquer-seal |
| 祥云 | auspicious-cloud | 祥瑞、流动、上升 | 青绿、朱砂、米白、描金 | 用三段卷云叠成一个清晰云头，去掉小尾巴 | celadon-goldline, ink-wash |
| 如意 | ruyi-head | 顺遂、祝愿、护持 | 朱砂、青绿、米白、描金 | 只保留一个如意头和短柄弧线 | celadon-goldline, lacquer-seal |
| 牡丹 | peony | 富贵、盛放、繁荣 | 朱砂、青绿、米白、墨 | 只画三层花瓣的正面团花，不画枝叶群 | celadon-goldline, riso-grain |
| 龙 | dragon | 权能、守护、变化 | 靛蓝、朱砂、描金、米白 | 抽成一枚龙首侧影或一段龙身弧，不画整条复杂龙 | celadon-goldline, lacquer-seal |
| 饕餮 | taotie-mask | 威严、守门、警示 | 墨、靛蓝、描金、米白 | 保留双眼、鼻梁、对称角形，压成一个面具符号 | lacquer-seal, carve-block |
| 寿字 | longevity-mark | 长寿、祝福、延展 | 朱砂、墨、米白、描金 | 只取抽象寿字结构，不生成可读文字或书法复制 | lacquer-seal, draft-line |
| 卷草 | acanthus-scroll | 生长、延续、柔韧 | 青绿、米白、描金 | 用一片卷叶和一条弧藤表达，不做连续花边 | celadon-goldline, ink-wash |
| 宝相花 | baoxiang-flower | 圆满、庄重、护佑 | 青绿、靛蓝、朱砂、描金 | 抽成四瓣或八瓣对称花心，避免复杂满地纹 | celadon-goldline, press-relief |
| 海水江崖 | wave-cliff | 根基、气势、永续 | 靛蓝、米白、墨、描金 | 取一块斜崖和两道波峰，不做整幅山海纹 | celadon-goldline, contour-map |
| 鱼 | fish | 丰足、灵动、连年有余 | 青绿、朱砂、米白、描金 | 用单条侧身鱼和一枚尾鳍，不画鱼群 | celadon-goldline, riso-grain |
| 蝙蝠 | bat | 福气、到来、护佑 | 朱砂、靛蓝、米白、描金 | 抽成对称翼形和小头，避免写实动物细节 | lacquer-seal, celadon-goldline |
| 葫芦 | gourd | 收纳、平安、医护 | 青绿、米白、朱砂、墨 | 保留上下双圆和短藤，不画复杂挂饰 | celadon-goldline, draft-line |
| 梅 | plum-blossom | 坚韧、清寒、初春 | 墨、朱砂、米白、青绿 | 三到五瓣花 + 一段折枝，去掉枝条网 | ink-wash, celadon-goldline |
| 兰 | orchid | 清雅、君子、幽香 | 青绿、墨、米白 | 三片长叶和一朵简花，保持留白 | ink-wash, draft-line |
| 竹 | bamboo | 正直、节制、成长 | 青绿、墨、米白 | 两节竹竿和三片叶，避免竹林 | ink-wash, carve-block |
| 菊 | chrysanthemum | 高洁、晚香、从容 | 朱砂、青绿、米白、描金 | 一枚放射花盘，花瓣数量控制在 8-12 片 | celadon-goldline, riso-grain |
| 松 | pine | 长青、坚守、庇护 | 靛蓝、青绿、米白、墨 | 一段弯枝和三簇针叶，不画整棵树 | ink-wash, lacquer-seal |
| 鹤 | crane | 长寿、清远、升举 | 米白、墨、朱砂、青绿 | 侧身鹤颈 + 一片翅形，去掉羽毛细节 | celadon-goldline, draft-line |
| 鹿 | deer | 祥和、俸禄、山林 | 青绿、米白、朱砂、墨 | 侧面鹿首和一对简角，不画全身纹理 | celadon-goldline, felt-field |
| 石榴 | pomegranate | 多子、丰收、团圆 | 朱砂、青绿、米白、描金 | 半开果形和三粒籽，避免复杂果实剖面 | celadon-goldline, riso-grain |
| 铜钱 | coin-ring | 流通、守财、交换 | 米白、墨、描金、朱砂 | 方孔圆钱抽象化，禁止真实货币符号 | ridge-enamel, celadon-goldline |
| 双鱼 | paired-fish | 和合、循环、丰足 | 青绿、朱砂、米白、描金 | 两条鱼首尾成环，中间留白，不画水草 | celadon-goldline, lacquer-seal |
| 山形 | mountain-form | 稳固、远行、格局 | 靛蓝、青绿、米白、墨 | 三层山脊剪影或一枚峰形，不画写实山水 | contour-map, celadon-goldline |
| 星宿 | star-lodge | 方位、时间、秩序 | 靛蓝、米白、描金 | 三到五个点和一条短连线，避免天文图复制 | cyan-draft, celadon-goldline |

## Resolver 使用规则

- 如果用户给出具体母题名，优先匹配 `CN 母题` 或 `EN Resolver`。
- 如果用户给出抽象寓意，先匹配“公开寓意”，再选一个最简姿态。
- `celadon-goldline` 中每张图只允许一个母题，置于圆形开光内；不要生成连续纹样、墙纸、边框满铺。
- `lacquer-seal` 中优先把母题转成阴刻/阳刻的单色印形；不要生成可读文字。
- `carve-block` 中优先保留刀刻边、黑白块面和少量断墨；不要使用描金。
