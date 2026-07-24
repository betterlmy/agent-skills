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
| 审查代码、PR、架构、安全、性能或常见缺陷 | `code-review-skill` | 适用于审查和反馈；没有修改授权时不要直接实施修复 |
| 探索代码结构、定位符号、分析调用关系或改动影响 | `codegraph` | 精确字符串、配置和非代码文本优先使用 `rg` |
| 创建、编辑、审查或导出 Draw.io 图表 | `drawio-skill` | 明确要求 Mermaid 或定量数据图表时不要使用 |
| 查找或安装外部 Skill | `find-skills` | 已经指定要修改某个现有 Skill 时不需要先搜索 |
| 编写、审查、重构或排查 Go 代码、服务、API、并发和持久化 | `go-dev` | 先遵循仓库约束并识别实际技术栈；Go MCP Server 任务还必须组合 `go-mcp-builder` |
| 使用 `mcp-go` 开发、修改或调试 Go MCP Server | `go-mcp-builder` | 仅讨论通用 Go 编码规范时使用 `go-dev` 即可 |
| 使用 Mermaid 创建可维护的文本图 | `mermaid-diagrams` | 需要 `.drawio` 文件或稳定导出时使用 `drawio-skill` |
| 通过 CDP 启动或控制 Chrome、检查页面状态 | `playwright-cli-cdp` | 只允许 CDP 工作流，不使用普通 `playwright-cli open` |
| 构建文档问答、知识库、企业搜索或其他 RAG 应用 | `rag-agent-builder` | 普通数据库查询或不涉及检索增强的搜索不触发 |
| 创建、改进、审查或生产化 Agent Skill | `skill-engineer` | 单纯发现现有 Skill 时优先使用 `find-skills` |

## 推荐组合

- Go MCP Server：先用 `go-mcp-builder` 确定 MCP 结构、传输和安全边界，再用 `go-dev` 按仓库技术栈落实 Go 编码、错误、Context、日志和测试规范。
- 代码变更评审：用 `code-review-skill` 审查正确性、质量、安全和性能；需要定位调用方或评估影响面时再叠加 `codegraph`。
- 软件图表：Markdown 内联和文本维护使用 `mermaid-diagrams`；需要可编辑 Draw.io 文件或 PNG、SVG、PDF 导出时使用 `drawio-skill`。
- Skill 维护：查找外部能力使用 `find-skills`；创建、修改、审查或验证 Skill 使用 `skill-engineer`。
