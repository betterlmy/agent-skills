# 协议与 SDK 版本选型

MCP 协议规范与对应的编程语言 SDK 属于独立演进关系。在确定 API 设计或底层网络交互行为前，必须对两者分别进行核实。

## 官方核验来源

按以下顺序依次参考官方权威源：

1. 当前带日期的官方规范：<https://modelcontextprotocol.io/specification>
2. 规范仓库与变更日志：<https://github.com/modelcontextprotocol/modelcontextprotocol>
3. 官方 Go SDK 发布列表：<https://github.com/modelcontextprotocol/go-sdk/releases>
4. 官方 Go SDK 兼容性矩阵与文档：<https://github.com/modelcontextprotocol/go-sdk>
5. 选定版本 Tag 对应的 GoDoc API：<https://pkg.go.dev/github.com/modelcontextprotocol/go-sdk>

在具体实施任务中，明确记录核验日期、具体协议修订版本号、具体 SDK Tag 标签、支持的 Go 语言版本以及业务所需的能力集。优先选用明确声明完全支持目标协议版本的最新稳定版 SDK。切勿仅因版本号更大就选用预发布版本（pre-release）。

## 已验证基线

以下为已通过完整可复现验证的基线版本（不代表永久的“最新”声明）：

| 项目 | 已验证取值 |
| --- | --- |
| 验证日期 | 2026-09-04 |
| 带日期 MCP 修订版本 | `2026-07-28` |
| 官方 Go SDK | `github.com/modelcontextprotocol/go-sdk v1.7.0` |
| SDK Go 版本指令 | Go 1.25 |
| 向前兼容修订版本 | `2025-11-25` |

在具体编码前，重新核验上述官方来源。若已有更新的稳定版 SDK 发行，在调整版本依赖前必须完整阅读其 Release Notes 与能力支持矩阵。

## `2026-07-28` 生命周期规范

- **纯无状态协议**：移除了 `initialize` 与 `notifications/initialized` 握手阶段。
- **服务发现机制**：在执行常规请求前，通过 `server/discover` 接口向客户端声明服务器标识、可用能力及所支持的版本。
- **请求级元数据**：每个请求通过 `_meta.io.modelcontextprotocol/*` 字段携带客户端的协议版本与能力声明。
- **Streamable HTTP 交互**：每个请求对应一次独立的 POST 调用。返回内容为结构化 JSON 或请求生命周期内的 SSE 流。
- **移除历史特性**：独立的 GET 流、协议级长会话、`Mcp-Session-Id` 会话头以及基于 `Last-Event-ID` 的断点续传机制均不属于此版本规范。
- **服务器主动调用**：服务器主动发起的调用采用多轮往返结果机制。Roots、Sampling 和 MCP Logging 已被标记为废弃（Deprecated）；若无明确的旧客户端兼容需求，新服务中不得引入。

对于该版本规范，官方 Go SDK 强制要求设置 `StreamableHTTPOptions.Stateless=true`，并由 SDK 内置接管 `server/discover`、请求元数据解析、Header/Body 校验以及协议版本协商。

版本 Tag 注意事项：`v1.7.0` 尚未暴露主分支上的 `ServerOptions.SupportedProtocolVersions` 字段，其默认声明 SDK 内置的版本矩阵。若业务服务必须收敛对外声明或接收的版本集合，需要在应用层引入协议守卫中间件并配合单元测试。锁版本为 `v1.7.0` 时，严禁在业务代码中直接调用尚未发布的字段。

## 兼容性策略与原则

- 若所选 SDK Tag 提供了版本暴露控制，仅声明并接受真实客户端所必需的协议版本；否则必须增加经过测试的应用层守卫，或在文档中清晰说明 SDK 的实际暴露矩阵。
- 对声明支持的每一个历史版本，使用其专属生命周期流程进行独立测试。最新版本测试通过绝不能证明旧版本握手依然正常。
- 新建服务严禁回退采用已被废弃的 HTTP+SSE 传输通道。
- 严禁将 `MCPGODEBUG` 等 SDK 兼容性开关写入持久化生产配置中，除非复现出的特定第三方依赖要求进行阶段性平滑过渡。
