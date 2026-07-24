# agent-skills

[![skills.sh](https://skills.sh/b/betterlmy/agent-skills)](https://skills.sh/betterlmy/agent-skills)

[English README](README.md)

`betterlmy` 维护的 agent skills 集合，覆盖仓库协作规范、代码工程、图表、前端开发、浏览器自动化、RAG 和 Skill 开发。

## 可用 Skills

| Skill | 用途 | 安装 |
| --- | --- | --- |
| [`agents-md-expert`](skills/agents-md-expert/SKILL.md) | 创建、审查和改进项目级 `AGENTS.md` 协作指令 | `npx skills add betterlmy/agent-skills --skill agents-md-expert` |
| [`code-review-skill`](skills/code-review-skill/SKILL.md) | 跨主流技术栈审查架构、安全、性能、代码质量和常见缺陷 | `npx skills add betterlmy/agent-skills --skill code-review-skill` |
| [`codegraph`](skills/codegraph/SKILL.md) | 索引本地代码库并分析符号、调用关系、改动影响和受影响测试 | `npx skills add betterlmy/agent-skills --skill codegraph` |
| [`drawio-skill`](skills/drawio-skill/SKILL.md) | 创建、编辑、审查、验证和导出 Draw.io 图表 | `npx skills add betterlmy/agent-skills --skill drawio-skill` |
| [`find-skills`](skills/find-skills/SKILL.md) | 从开放的 agent skills 生态中发现并安装 Skill | `npx skills add betterlmy/agent-skills --skill find-skills` |
| [`go-dev`](skills/go-dev/SKILL.md) | 按仓库约束和实际技术栈规范 Go 开发、评审、API、并发、持久化与测试 | `npx skills add betterlmy/agent-skills --skill go-dev` |
| [`go-mcp-builder`](skills/go-mcp-builder/SKILL.md) | 使用 `mcp-go` 和 Streamable HTTP 构建 Go MCP Server | `npx skills add betterlmy/agent-skills --skill go-mcp-builder` |
| [`mermaid-diagrams`](skills/mermaid-diagrams/SKILL.md) | 使用 Mermaid 创建流程图、时序图、ER 图和 C4 模型等软件图表 | `npx skills add betterlmy/agent-skills --skill mermaid-diagrams` |
| [`playwright-cli-cdp`](skills/playwright-cli-cdp/SKILL.md) | 使用 `playwright-cli` 通过 CDP 控制 Chrome 系浏览器 | `npx skills add betterlmy/agent-skills --skill playwright-cli-cdp` |
| [`rag-agent-builder`](skills/rag-agent-builder/SKILL.md) | 使用嵌入、向量数据库、检索和评估能力构建 RAG 应用 | `npx skills add betterlmy/agent-skills --skill rag-agent-builder` |
| [`skill-engineer`](skills/skill-engineer/SKILL.md) | 创建、改进、审查和评估生产可用的 agent skills | `npx skills add betterlmy/agent-skills --skill skill-engineer` |

## 安装

全局安装到 Codex：

```bash
npx skills add betterlmy/agent-skills --skill <skill-name> -a codex -g -y
```

全局安装到 Claude Code：

```bash
npx skills add betterlmy/agent-skills --skill <skill-name> -a claude-code -g -y
```

省略 `--skill <skill-name>` 可使用 Skills CLI 提供的交互式选择。

## Skill 分类

### 仓库与代码工程

- `agents-md-expert` 用于维护真实、作用域清晰、可执行且可验证的仓库协作指令。
- `code-review-skill` 提供跨语言的架构、安全、性能、质量和正确性审查指南。
- `codegraph` 封装代码库索引、符号定位、调用分析和改动影响分析工作流。
- `go-dev` 先识别仓库约束和实际技术栈，再提供 Go 编码、错误、Context、日志、HTTP/gRPC、持久化、并发和测试规范；统一响应等偏好只在仓库无相反约定时作为推荐默认值。
- `go-mcp-builder` 提供基于 `mark3labs/mcp-go` 与 Streamable HTTP 的 Go MCP Server 完整开发流程。

### 设计与图表

- `drawio-skill` 支持 Draw.io 架构图、流程图、ER/UML/时序图、视觉检查及 Office 安全导出。
- `mermaid-diagrams` 覆盖使用 Mermaid 语法维护可版本控制的软件图表。

### 自动化与内容

- `playwright-cli-cdp` 启动或复用本地 Chrome 调试端点，并仅通过 CDP 操作已连接的浏览器。
- `rag-agent-builder` 提供文档问答、知识库、企业搜索、检索与评估相关示例和工具。

### Skill 开发

- `find-skills` 帮助为目标能力查找可安装的 Skill。
- `skill-engineer` 支持面向生产的 Skill 创建、审查、打包、验证和真实场景评估。

## 仓库结构

```text
skills/
  <skill-name>/
    SKILL.md
    agents/       # 可选：Agent 元数据
    assets/       # 可选：可复用资源
    evals/        # 可选：评估用例和结果
    examples/     # 可选：示例
    references/   # 可选：详细参考资料
    scripts/      # 可选：可执行辅助脚本
    templates/    # 可选：模板
    tests/        # 可选：测试
```

每个 Skill 都以 `SKILL.md` 作为入口。只有在工作流需要时才会附带支持资源，因此各 Skill 目录使用的可选子目录可能不同。

## 相关链接

- [Skills 使用指南](SKILLS-GUID.md)
- [Skills directory](https://skills.sh/)
- [Skills CLI](https://github.com/vercel-labs/skills)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [Claude Code Agent SDK Skills](https://code.claude.com/docs/en/agent-sdk/skills)
