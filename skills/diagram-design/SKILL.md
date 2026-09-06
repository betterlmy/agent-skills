---
name: diagram-design
description: Create branded editorial diagrams as standalone HTML/SVG/PNG. Use when the user wants a polished diagram or visual redraw; do not use for plain Mermaid source, editable Draw.io XML, or information clearer in prose.
metadata:
  external-cli: "true"
  cli-compatibility: "references/cli-compatibility.md"
  version: "2.4"
license: MIT
---

# diagram-design

## 范围与执行

产物按用户指定的 HTML/SVG/PNG 交付；默认生成静态、自包含 HTML。先复用项目明确的配色和版式；无品牌要求时使用默认主题并说明，不为选择样式重复暂停。只在品牌选择实质改变结果且上下文无法确定时提问。

- 用户当前要求、项目硬约束和已有授权优先；参考中的视觉禁令、数值预算和示例是匹配目标后的选择，不是额外产品需求。
- 先查看相关页面、品牌资料与构建文件，以一句话说明设计方向和验收目标；已能可靠确定的事项直接推进。
- 只改变需求范围内的视觉与交互；不因素材、安装表或预检清单而擅自安装新库、上传数据、发布站点或调用额外付费服务。
- 仅加载下表当前任务命中的章节；选中的章节完整读取，不把全部词库加载作为每次任务前置条件。
- 参考节号与原指南一致；涉及第三方版本时查对应官方文档，示例安装命令不是已验证的当前环境命令。

## 按需参考索引

重设计读取对应 redesign 章节；动效仅在需要时读取 motion；主题仅在需要时读取 theme/dark；导入与导出只在对应交付时读取。绘图必须读所选类型的参考，技术验证不能由审美偏好替代。

| 任务对应章节 | 参考 |
| --- | --- |
| 0. First-time setup — style guide gate | [guide-00.md](references/guide-00.md) |
| 1. Philosophy | [guide-01.md](references/guide-01.md) |
| 2. When to Use | [guide-02.md](references/guide-02.md) |
| 3. Selection: semantic pattern, then visual type | [guide-03.md](references/guide-03.md) |
| 4. Universal Anti-patterns | [guide-04.md](references/guide-04.md) |
| 5. Design System | [guide-05.md](references/guide-05.md) |
| 6. Core SVG Primitives | [guide-06.md](references/guide-06.md) |
| 7. Layout & Spacing | [guide-07.md](references/guide-07.md) |
| 8. Summary Card Pattern | [guide-08.md](references/guide-08.md) |
| 9. Pre-Output Checklist (Taste Gate) | [guide-09.md](references/guide-09.md) |
| 10. Templates & Variants | [guide-10.md](references/guide-10.md) |
| 11. Importing an Existing Diagram (draw.io) and Mermaid | [guide-11.md](references/guide-11.md) |
| 12. Output | [guide-12.md](references/guide-12.md) |

## 验证与交付

- 先确认内容、关系和关键交互正确，再检查遮挡、溢出、键盘、可访问性和约定视口；沿用宿主已选择的浏览器。
- 运行项目已有且与修改相关的检查；相同输入通过后不重复，未运行的浏览器/导出检查明确说明。
- 不编造真实数据、来源、图片或已执行测试；交付请求的产物和简短说明，不自动增加多套主题或格式。
- 首次调用导出工具前读 [CLI 兼容性](references/cli-compatibility.md)；使用包内 scripts/self_check.py 检查可访问 SVG、自包含结构和实际选择的动效。
