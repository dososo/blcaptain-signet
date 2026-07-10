# Signet License and Attribution Summary

本文件汇总 Signet 仓库本体与 WS-3 UI SVG 轨道的许可证来源。根许可证全文见 `LICENSE`，项目 NOTICE 见 `NOTICE.md`。

## 项目本体

- 范围: 材质 YAML、Python 脚本、参数化 Signet glyph、文档、showcase、测试和 supporting metadata。
- 许可证: Apache-2.0。
- 来源: Signet 原创 / clean-room 编写。
- 本地许可证文件: `LICENSE`。

## UI vendored 第三方基集

- 基集: Lucide Static `v1.23.0`。
- 上游包: https://unpkg.com/lucide-static@1.23.0/package.json
- 上游仓库: https://github.com/lucide-icons/lucide
- 上游许可证: ISC。
- 本地保留许可证: `skills/signet/ui/upstream/lucide/LICENSE`。
- 逐 glyph 来源与 license 记录: `skills/signet/ui/manifest.json`。

Lucide LICENSE 同时声明部分 Lucide icon 派生自 Feather project；这些 Feather-derived glyph 及其同几何别名使用 MIT notice。当前生产 manifest 中 MIT glyph 共 96 个：

```text
alert-circle, alert-triangle, arrow-down, arrow-down-circle, arrow-down-left, arrow-down-right, arrow-left, arrow-left-circle, arrow-right, arrow-right-circle, arrow-up, arrow-up-circle, arrow-up-left, arrow-up-right, at-sign, calendar, cast, check, chevron-down, chevron-left, chevron-right, chevron-up, chevrons-down, chevrons-left, chevrons-right, chevrons-up, circle, circle-minus, circle-plus, circle-x, clipboard, clock, code, command, compass, corner-down-left, corner-down-right, corner-left-down, corner-left-up, corner-right-down, corner-right-up, corner-up-left, corner-up-right, database, download, external-link, hash, headphones, help-circle, info, italic, key, layout, link, link-2, loader, lock, log-in, log-out, minus, monitor, moon, more-horizontal, more-vertical, move, music, navigation, navigation-2, octagon-alert, pause-circle, percent, plus, plus-circle, power, radio, rss, search, server, share, shopping-bag, sidebar, smartphone, smile, table-2, target, terminal, trash, trash-2, triangle, tv, type, upload, x, x-circle, zoom-in, zoom-out
```

其余 154 个 Lucide-themed glyph 在 `skills/signet/ui/manifest.json` 中标注为 ISC。每条 manifest 记录包含 `upstream_source_url`、本地 `upstream_file`、`license`、`license_notice` 和 `derivative_statement`。

## UI Signet custom glyph

- 范围: `skills/signet/ui/custom/*.svg` 与 `skills/signet/ui/custom_manifest.json` 中的 22 个几何 / 平台 / 工具类 glyph；其中 8 个是本轮按需生成示范。
- 许可证: Apache-2.0。
- 来源: Signet 自制参数化 SVG；不使用第三方 glyph 几何。
- 逐 glyph 记录: `skills/signet/ui/custom_manifest.json`。

当前 UI SVG 总量为 272：250 个 Lucide themed（154 ISC + 96 Feather MIT）与 22 个 Signet custom（Apache-2.0）。

## 兼容性与再分发

ISC、MIT、BSD、Apache-2.0、CC0 均为 permissive license。当前 WS-3 UI SVG 轨道只接收 permissive 来源；Lucide ISC 与 Feather MIT notice 在保留上游版权与 permission notice 的前提下，可与本仓 Apache-2.0 本体一起再分发。

Clean-room 边界: `themed/` 内 SVG 是对 Lucide / Feather 上游几何的描边 token、颜色 token、端点/拐角归一化衍生，必须署名上游，不冒充 Signet 原创；`custom/` 内 SVG 为 Signet 自制参数 glyph。

本仓未引入 AGPL/GPL 图标集；相关字样只允许出现在排除说明、对比说明或测试夹具上下文中。
