# Skills 使用指南

本文档用于快速判断本仓库中的 Skill 是否适合当前任务。实际可用能力、触发描述和执行要求以当前会话暴露的 Skill 列表及对应 `SKILL.md` 为准。

## 使用原则

- 用户明确点名某个 Skill 时，优先读取并遵循该 Skill。
- 只选择覆盖任务所需的最小 Skill 组合；不要因为关键词相似就加载无关 Skill。
- 选定 Skill 后完整读取它的 `SKILL.md`，再按其中的渐进披露规则读取必要资源。
- 只读排查或普通问答仅在 Skill 会改变执行路径、产物格式或验证方式时加载。

## 快速路由

| 用户意图 | 优先使用 | 关键边界 |
| --- | --- | --- |
| 创建、审查或改进项目级 `AGENTS.md` | `agents-md-expert` | 只处理 Agent 协作指令，不用于普通 README 或完整架构文档 |
| 扫描一个或多个仓库的过度工程、代码膨胀、无必要抽象或可删除内容 | `audit-overengineering` | 默认只输出证据报告；不用于单次 diff、通用正确性、安全或性能审查，也不直接实施重构 |
| 跨语言审查代码、PR、架构、安全、性能或常见缺陷 | `code-review-skill` | Go 专项且需要 package、范围或影响上下文时优先使用 `go-auditor` |
| 生成、优化或检查中文 commit message，或执行本地提交 | `commit` | 可按明确范围执行 `git add` 和 `git commit`；仅在用户明确要求且满足全局 push 策略（禁止 force、禁止 master/main 分支）时推送 |
| 探索代码结构、定位符号、分析调用关系或改动影响 | `codegraph` | 精确字符串、配置和非代码文本优先使用 `rg` |
| 创建、编辑、审查或导出 Draw.io 图表 | `drawio-skill` | 需要 Mermaid 文本时使用 `mermaid-diagrams`；需要品牌化 HTML/SVG/PNG 重绘时使用 `diagram-design` |
| 创建品牌化 HTML/SVG/PNG 编辑式图表，或将 Draw.io/Mermaid 重绘为可交付视觉稿 | `diagram-design` | 只需要可版本控制的 Mermaid 文本时使用 `mermaid-diagrams`；只需要编辑 Draw.io 源文件时使用 `drawio-skill` |
| 查找或安装外部 Skill | `find-skills` | 已经指定要修改某个现有 Skill 时不需要先搜索 |
| 为产品生成简洁可爱的拟人化 IP 角色 Logo，或批量提出候选方向供确认 | `ip-as-logo` | 需要可编辑 SVG/矢量 Logo 时使用 `svg-logo-designer`；本 Skill 以方形角色构图和批量候选为主 |
| 编写、审查、重构或排查 Go 代码、服务、API、并发和持久化 | `go-dev` | 先遵循仓库约束并识别实际技术栈；Go MCP Server 任务还必须组合 `go-mcp-builder` |
| 审计 Go 仓库、模块、package、目录、文件集、高风险域或 diff | `go-auditor` | 输出证据报告但不直接修改代码；落实修复用 `go-dev` |
| 使用 `mcp-go` 开发、修改或调试 Go MCP Server | `go-mcp-builder` | 仅讨论通用 Go 编码规范时使用 `go-dev` 即可 |
| 使用 Mermaid 创建可维护的文本图 | `mermaid-diagrams` | 需要品牌化 HTML/SVG/PNG 重绘时使用 `diagram-design`；需要 `.drawio` 文件或 Draw.io 专项导出时使用 `drawio-skill` |
| 通过 CDP 启动或控制 Chrome、检查页面状态 | `playwright-cli-cdp` | 只允许 CDP 工作流，不使用普通 `playwright-cli open` |
| 构建文档问答、知识库、企业搜索或其他 RAG 应用 | `rag-agent-builder` | 普通数据库查询或不涉及检索增强的搜索不触发 |
| 创建、改进、审查或生产化 Agent Skill | `skill-engineer` | 单纯发现现有 Skill 时优先使用 `find-skills` |
| 根据需求编写软件设计文档，或根据代码、配置、Schema 和测试逆向现状设计 | `software-designer` | 只画单张图、只做代码审查、只写需求或直接实现功能时不使用 |
| 从品牌简报设计或迭代字标、字母标、图形标、组合标及 SVG Logo 变体 | `svg-logo-designer` | 普通 UI 图标、图表、格式转换、完整品牌战略或商标法律审查不使用 |

## 推荐组合

- Go MCP Server：先用 `go-mcp-builder` 确定 MCP 结构、传输和安全边界，再用 `go-dev` 按仓库技术栈落实 Go 编码、错误、Context、日志和测试规范。
- 代码变更评审：跨语言或通用 PR 反馈使用 `code-review-skill`；Go diff 需要 package 语义、工作区或 revision 范围审计时使用 `go-auditor`；需要定位调用方或评估影响面时再叠加 `codegraph`。
- Go 质量审计：用 `go-auditor` 审计整仓或局部范围，也可检查工作区、暂存区和 revision range；需定位调用方或评估影响面时叠加 `codegraph`，落实修复时参考 `go-dev`。
- 软件图表：品牌化 HTML/SVG/PNG 编辑式交付或 Draw.io/Mermaid 重绘使用 `diagram-design`；Markdown 内联和文本维护使用 `mermaid-diagrams`；需要可编辑 Draw.io 文件或 Draw.io 专项视觉检查时使用 `drawio-skill`。
- 软件设计文档：使用 `software-designer` 完成正向设计、代码逆向或增量维护；代码逆向需要调用关系和影响分析时可组合 `codegraph`，只需要单张图时使用对应图表能力。
- Skill 维护：查找外部能力使用 `find-skills`；创建、修改、审查或验证 Skill 使用 `skill-engineer`。
