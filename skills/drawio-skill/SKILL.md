---
name: drawio-skill
version: 1.6.0
description: 创建、编辑、审查、校验和导出可编辑的 Draw.io 图表。Use when 主要交付物为 `.drawio` XML、`.drawio.png` 或 `.drawio.svg`，需要对 Draw.io 图表进行视觉质检、透明背景导出，或生成字体稳定的 PowerPoint/Office 安全矢量图；不用于仅需要纯 Mermaid 源码或独立品牌化 HTML/SVG/PNG 重绘的场景。
license: MIT
homepage: https://github.com/Agents365-ai/drawio-skill
compatibility: 本地渲染需要 Draw.io Desktop；PPT 安全 SVG 需额外依赖 Poppler pdftocairo。视觉模型（Vision）可用于视觉质检。
external-cli: true
cli-compatibility: references/cli-compatibility.md
platforms: [macos, linux, windows]
metadata: {"openclaw":{"requires":{"anyBins":["draw.io","drawio"]},"emoji":"📐","os":["darwin","linux","win32"],"install":[{"id":"brew-drawio","kind":"brew","formula":"drawio","bins":["draw.io"],"label":"Install draw.io via Homebrew","os":["darwin"]}]},"hermes":{"tags":["drawio","diagram","flowchart","architecture","visualization","uml"],"category":"design","requires_tools":["draw.io"],"related_skills":["mermaid","excalidraw","plantuml"]},"author":"Agents365-ai","version":"1.6.0"}
---

# Draw.io 图表

优先生成可编辑的 `.drawio` 源文件，再按需导出并质检目标产物。在修改过程中保留图表已有的样式微调，始终将“源文件可编辑性”与“终端展示兼容性”解耦处理。

## 资源精准路由

仅在满足特定条件时读取对应参考资源：

| 参考资源 | 何时读取 |
|---|---|
| `references/workflow.md` | 创建新图表、进行全局布局调整或执行视觉审查时 |
| `references/xml-authoring.md` | 编写或编辑 Draw.io XML、容器、连线、布局或透明填充时 |
| `references/diagram-types.md` | 涉及 ERD、UML 类图、时序图、系统架构图、ML/DL 流水线或流程图结构时 |
| `references/style-presets.md` | 应用、学习、列出、重命名、删除或设置预设样式时 |
| `references/style-extraction.md` | 从现有 Draw.io XML 或参考图片中提取样式规范时 |
| `references/export.md` | 导出 PNG/SVG/PDF/JPG，或权衡“保留可编辑性”与“Office/PPT 安全输出”时 |
| `references/troubleshooting.md` | 遇到渲染崩溃、CLI 报错、布局错位、字体或背景透明度异常时 |
| `references/cli-compatibility.md` | 查看 CLI 依赖版本、必需导出功能或版本漂移处理方案时 |

包内确定性辅助脚本：

| 脚本工具 | 用途说明 |
|---|---|
| `scripts/validate_drawio.py` | 验证根单元（root cell）、元素 ID 唯一性、父子嵌套、连线几何属性及引用有效性 |
| `scripts/repair_png.py` | 修复内嵌 XML 导出 PNG 时已知的末尾 IEND 块截断问题 |
| `scripts/export_ppt_svg.py` | 生成适用于 Office/PPT 的透明 SVG，将所有字体轮廓化为矢量路径以防缺字错位 |
| `scripts/encode_drawio_url.py` | 在本地 Desktop CLI 不可用时，生成前端可直接打开编辑的 diagrams.net 链接 |

## 标准工作流程

1. **明确范围**：优先从用户 Prompt、附件或已有源文件中提取信息；仅在图表的核心目标、必须包含的实体、交付格式或保真度目标存在重大分歧且无法推断时才提问。
2. **确定样式**：优先匹配明确指定的样式预设；未指定时采用用户标记为默认的单一套预设；再次降级到内置规范。组件名称不可当作样式名称。
3. **构思规划**：在分配具体坐标前，先梳理节点清单、容器分层、连线拓扑、文本标签、流向方向、网格对齐和布线通道。
4. **生成或编辑**：严格遵循 `xml-authoring.md`。针对已有文件，执行精准局部编辑并保留原有 ID 与坐标；除非用户要求全量重构，否则不整体重绘。
5. **静态校验**：在渲染前必须运行 `python3 <this-skill-dir>/scripts/validate_drawio.py <file.drawio>`。
6. **预览与质检**：导出一份不带 `-e` 参数的干净 PNG，在支持 Vision 的环境中进行视觉检查，自动修复轮次不得超过两轮。
7. **用户反馈迭代**：在现有 XML 基础上应用用户修改意见，并覆盖原有预览文件。若迭代超过 5 轮，建议用户在桌面客户端中进行微调。
8. **最终交付**：根据 `export.md` 选择适配的导出模式，完整保留 `.drawio` 源文件，并在交付总结中清晰报告校验结果、跳过的质检项及环境潜在风险。

## 源码硬性约束（不可妥协）

- 每个页面必须包含 `0` 和 `1` 两个根级 `mxCell`；页面内所有元素 ID 必须唯一。
- XML 属性必须合法转义，文本换行统一使用 `&#xa;`。
- 保持可编辑标签的 `html=1` 属性；不得为了兼容 PowerPoint 而强行修改源文本模式。
- 每条连线必须包含 `<mxGeometry relative="1" as="geometry" />` 子元素。
- 分组内容必须使用真正的父子容器嵌套关系（parent 指定），而非单纯在视觉上叠放。
- XML 注释中严禁连续出现 `--`。
- 需要透明背景时，设置 `fillColor=none`，且不得添加覆盖全画布的底色矩形。
- 严格保留用户在范围外的不相关修改，严禁覆盖用户指定范围外的源文件。

## 导出决策原则

- **预览图**：不带 `-e` 参数；生成纯净 PNG 供视觉检查与用户确认。
- **最终可编辑交付**：使用 `-e` 参数；文件命名使用双扩展名（如 `.drawio.png` 或 `.drawio.svg`）以标明包含内嵌 XML。
- **嵌入式 PNG**：每次导出后必须运行 `scripts/repair_png.py` 修复文件末尾数据。
- **PowerPoint/Office 或固定字体需求**：使用 `scripts/export_ppt_svg.py`；必须同时单独交付 `.drawio` 源文件（因为轮廓化后的矢量 SVG 文本无法再次直接编辑）。
- **SVG 严格渲染报错（如 `text is not svg`）**：切勿临时手动剥离标签；应直接转用 PPT 安全导出方案，并参阅 `troubleshooting.md`。

## 质检与交付核对

在正式交付前必须完成：

- 对 `.drawio` 源文件执行结构有效性校验；
- 检查内容完整性、层级结构、元素重叠、边缘截断、文本对齐、连线交叉、对比度及画布边界；
- 验证最终产物的文件格式有效性；
- 确保 PPT 安全 SVG 中不再包含 `<text>` 或 `foreignObject` 标签；
- 同时清晰输出源文件路径与导出产物路径；
- 明确区分已完成的静态校验、视觉质检、条件性跳过项以及尚未在目标运行环境中测试的潜在行为。

若 Draw.io Desktop 在沙箱隔离环境中不可用或崩溃，切勿在同一环境下盲目重试。使用 `scripts/encode_drawio_url.py` 或直接交付合法的 `.drawio` XML 源文件，并向用户说明哪些导出格式仍需宿主环境支持。
