# MCP 服务器设计规范

## 能力类型选型指南

| 业务诉求 | 对应的 MCP 暴露形态 |
| --- | --- |
| 模型自主决策何时发起查询、计算或数据变更 | Tool（工具） |
| 应用或用户挑选具备寻址能力的只读上下文 | Resource 或 Resource Template（资源 / 资源模板） |
| 用户选择可复用的消息工作流或提示词模板 | Prompt（提示词） |
| 长时间异步运行的任务需要持久化句柄跟踪状态 | Task extension（仅在客户端明确支持该扩展时使用） |

始终坚持最小暴露面原则。一个包含二十个操作的 REST API 绝不需要机械地映射为二十个 MCP Tool。在能够完整保持业务鉴权语义和产品边界的前提下，优先提供面向完整任务的组合式 Tool，而非死板地按网络接口逐个封装。

## Tool 设计与实现

- **稳定唯一的命名**：长度 1–128 字符，仅允许 ASCII 字母、数字、下划线、短横线与点号（`.`）。
- **面向模型的清晰描述**：详细阐明 Tool 的功能定位、前置上下文、副作用影响以及重要边界条件，以便模型准确决策调用。
- **强类型出入参定义**：优先通过 `mcp.AddTool` 配合 Go 结构体定义；当涉及数值边界、枚举、严格禁止未知字段（`additionalProperties: false`）或特定兼容需求时，覆盖自动推断出的 Schema。
- **声明输出结构体**：定义清晰的输出 Schema 并返回结构化数据。若需兼容较旧版本的客户端，可将同样的 JSON 内容序列化后一并放入 `TextContent` 中返回。
- **敏感数据边界**：切勿在 `x-mcp-header` 中存放密钥、个人隐私、敏感查询参数或自由文本内容，这类数据在网络中间代理中是完全明文可见的。

## 错误分类与处理体系

- **协议级错误（Protocol errors）**：格式错误的 JSON-RPC 请求、不支持的调用方法、无效的协议元数据以及非预期的服务端内部崩溃。
- **Tool 业务执行错误（Tool results with `isError=true`）**：领域参数不合规、资源冲突、下游依赖暂不可用等 LLM 具备理解并可自我修正的错误，统一在 Tool 返回结果中将 `isError` 置为 `true`。
- **认证与鉴权错误**：在 Streamable HTTP 模式下，直接归属于 HTTP 认证边界（返回 401/403）。
- **错误脱敏与稳定性**：向客户端输出的错误文案必须稳定且经过严格脱敏。底层的原始堆栈与详细错误原因仅限在受控的服务端日志中记录。

## HTTP 架构集成

`mcp.NewStreamableHTTPHandler` 本身是一个标准的 `http.Handler`。在现有 Go Web 服务中，直接将其挂载到外层的 `http.ServeMux` 或主流框架的原生 Handler 适配器下。注意保持 MCP 响应独立，严禁将其包裹进业务统一的 RESTful 响应封套中；同时确保全局的 Panic 恢复中间件不会向连接同时写入两套互不兼容的协议数据。

针对 `2026-07-28` 版本的推荐配置：

```go
&mcp.StreamableHTTPOptions{
    Stateless:                    true,
    JSONResponse:                 true, // 当无需流式进度/SSE 时启用
    MaxRequestBodyBytes:          1 << 20,
    PropagateRequestCancellation: true,
}
```

在 MCP Handler 外层包裹 `http.NewCrossOriginProtection().Handler(handler)`。保持 SDK 内置的本地回环保护始终开启。仅对已知的浏览器客户端配置显式信任的跨域 Origin 白名单。

针对需要身份鉴权的响应结果，将 MCP 缓存作用域标记为私有（private），避免被共享的中间 HTTP 缓存误存。对于仅暴露固定 Tool 的无状态服务器，切勿添加资源订阅（Resource Subscriptions）或 EventStore 状态管理。

## 验证与测试矩阵

核心测试覆盖范围：

- 服务的发现逻辑与协议版本协商流程；
- 功能列表输出的确定性（幂等、无随机漂移）；
- 严格的输入校验与输出 Schema 结构匹配；
- 成功调用、业务可恢复错误以及内部异常的三类路径；
- 契约要求空列表时返回 `[]` 而非 `null`；
- 上下文取消（Cancellation）与超时截止时间（Deadlines）的正常传递；
- 认证与各项权限 Scope 分支的覆盖；
- 协议 Header、Content-Type、Accept、Body 体积硬限制、请求 Method、Origin 及 Host 校验；
- 敏感凭据在日志与返回错误中的绝对脱敏。
