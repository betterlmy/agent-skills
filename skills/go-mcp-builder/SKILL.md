---
metadata:
  external-cli: "true"
  cli-compatibility: "references/cli-compatibility.md"
name: go-mcp-builder
description: 依据官方最新 Model Context Protocol（MCP）规范与官方 Go SDK 构建、扩展、审查或调试 Go MCP 服务器。Use when 任务需要为现有 Go 服务添加 MCP Tool、Resource、Prompt、Streamable HTTP 或 stdio 传输通道、MCP 认证鉴权、协议版本兼容性处理、官方一致性测试或接入 MCP 端点；不用于与 MCP 协议契约无关的常规 Go HTTP API 开发。
---

# Go MCP Server Builder

## 目标与原则

在完全贴合宿主代码仓库的前提下，构建最小、最安全的 MCP 暴露面。宿主仓库的指令规范与已有架构具有最高权威；MCP 官方协议细节与 SDK 用法则属于版本强敏感事实，在具体编码实施前必须先核对官方最新来源。

## 入门指引

1. 仔细检查宿主仓库的开发规范、Go 版本基线、模块边界、已有 HTTP 技术栈、认证鉴权体系、日志规范、现有测试及实际业务用例。
2. 阅读 [protocol-and-sdk.md](references/protocol-and-sdk.md)，核对当前带日期的官方最新 MCP 规范版本及官方 Go SDK 发行版，并在任务中显式锁定所选版本。严禁盲目复制陈旧示例中的过期 SDK 代码。
3. 参考 [server-design.md](references/server-design.md) 对所需能力进行严谨分类：明确区分为 Tool、Resource、Prompt 或不暴露为 MCP 能力。切勿机械地将现有 REST 接口全盘照搬暴露。
4. 凡涉及 Streamable HTTP、认证鉴权、读取外部未知内容或处理敏感数据，编码前必须先阅读 [security-and-auth.md](references/security-and-auth.md)。
5. 若需要运行一致性校验工具，先阅读包内 [CLI 兼容性契约](references/cli-compatibility.md)。在当前环境下安装或下载外部工具必须取得任务的明确授权。

## 实施标准工作流

1. **先定义公开契约**：明确服务器标识（Identity）、支持的协议版本、传输方式、能力名称、JSON Schemas、结构化返回对象、权限校验要求、错误语义以及版本兼容窗口。
2. **通过轻量适配器解耦**：仅通过适配器层复用现有应用服务逻辑。MCP 协议解码、鉴权上下文传递和结果对象映射严禁侵入核心领域业务逻辑。
3. **优先选用官方 SDK**：优先使用官方 `github.com/modelcontextprotocol/go-sdk`。若当前仓库已锁定了第三方 SDK，先核验该 SDK 对当前协议的支持完备度，再决定是否将迁移纳入任务范围。
4. **强类型 Tool 声明**：通过 `mcp.AddTool` 配合强类型输入输出结构体；当反射推断无法表达边界限制或严格禁止未知字段时，提供显式的 JSON Schema。若需要兼容较旧的客户端，同时返回结构化内容与等价的纯文本块。
5. **严谨传递 Request Context**：在调用数据库、网络请求和下游 Provider 时全程透传 `context.Context`。对请求 Body 大小、计算量、并发度、输出体积和耗时设置显式硬上限。
6. **清晰区分三类错误**：严格区分网络传输错误（Transport errors）、JSON-RPC 协议层错误（Protocol errors）与业务执行可恢复错误（Tool execution errors）。向外返回的公开错误信息必须稳定且经过脱敏。
7. **遵循最小日志原则**：仅记录白名单元数据（如 Request ID、方法名、Tool 名称、执行状态和耗时）。严禁在日志中输出完整参数体、结果明细、请求头、Prompt 原文、凭据密钥或抓取的外部内容。
8. **同步更新接口文档与路由**：当添加网络端点时，同步更新公开文档与部署路由配置。除非仓库有既定约定，否则 OpenAPI 文档不用于描述 MCP JSON-RPC 端点。

## 传输协议默认配置

- 新增远程服务器统一使用 Streamable HTTP 协议并挂载于 `/mcp` 端点；新增本地子进程工具，当更符合客户端生命周期管理时采用 stdio 传输。
- 针对 MCP `2026-07-28` 规范，采用无状态的 Streamable HTTP Handler。严禁添加已被规范废弃的独立 GET 流、协议级长会话或 `Last-Event-ID` 路径。
- 强制启用请求取消传播、Origin 校验保护、DNS 重绑定（DNS-rebinding）防护以及显式的 Body 体积上限。本地示例端点严格绑定到回环地址（Loopback）。
- 仅在明确存在特定老旧客户端需求时才保留旧版协议，且必须对各版本协议分别进行独立验证。

## 验证与验收

1. 编写充分的单元与集成测试，覆盖 Schema 校验、结构化输出、业务错误映射、上下文取消、认证与鉴权边界、Body 体积限制、Origin/Host 校验，以及所有声明支持的协议版本。
2. 使用官方 SDK Client 运行端到端能力发现、功能枚举与接口调用测试。切勿将“编译通过”等同于“协议验证通过”。
3. 运行宿主仓库既有的格式化、单元测试、竞态检测（race detector）、代码检查（vet/lint）、构建和契约校验命令。
4. 针对可复用模板，执行 `bash scripts/verify-templates.sh`；该脚本会在下载依赖或构建前将模板复制到临时隔离目录中安全执行。
5. 当官方一致性测试套件的场景与当前产品服务匹配时，可作为辅助验证手段；对服务未声明支持的可选能力，应记录为“超出范围（Out of scope）”，而非标记为“测试通过”。

## 配套资源索引

- [protocol-and-sdk.md](references/protocol-and-sdk.md)：官方规范源核验与协议版本协商工作流。
- [server-design.md](references/server-design.md)：能力分类、Schema 定义、结果封装、错误体系、传输与集成设计。
- [security-and-auth.md](references/security-and-auth.md)：HTTP 认证授权、跨域防护、日志脱敏、频控限流与非可信内容边界。
- `templates/`：基于官方 SDK 的极简回环地址服务器参考模板。
- `evals/prompts.md`：触发场景与前向评估测试用例。

本 Skill 不替代仓库专属的 Go 编码、安全策略、部署规范或产品业务规则，亦不适用于无 MCP 契约的常规 Go HTTP 任务。
