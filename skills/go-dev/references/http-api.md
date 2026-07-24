# HTTP API 规范

## 先确认契约

- 先确认仓库使用标准库 `net/http`、Gin、Echo、Chi、Fiber 或其他框架，并沿用已有 Router、中间件和绑定方式。
- 先读取当前 OpenAPI/Swagger、客户端契约和相邻 Handler；不要根据本 Skill 擅自改变状态码、字段名、认证来源或错误格式。
- Handler 只处理协议适配：解析与验证输入、建立认证上下文、调用用例、映射输出。业务规则放在可独立测试的层中。
- Request/Response DTO、领域对象和持久化模型保持分离；公开 DTO 的 JSON 字段、可空性和集合语义必须稳定。

## 输入边界

- 限制请求体大小，再进行解码；验证 `Content-Type`、Path、Query、Header 和 Body 的允许集合。
- JSON API 根据契约决定是否拒绝未知字段、重复字段、尾随内容和重复 Query；安全敏感接口应采用严格解析。
- 区分“缺失”“空值”和“零值”。只靠 `binding:"required"` 可能无法表达所有语义，必要时增加显式验证。
- Path 和 Query 解码要考虑编码斜杠、重复键、非法转义、规范化和重定向行为。
- 使用 `c.Request.Context()` 或 `r.Context()` 传播取消，不用新建根 Context 覆盖它。

## 输出边界

- 一个请求只由一个明确出口写 Header 和 Body；避免在中间件、`defer` 和 Handler 中重复写响应。
- 写响应前确定状态、Content-Type、缓存策略和安全 Header；流式响应在首次 Flush 后不能再切换普通 JSON 错误。
- List 字段默认初始化为空切片，避免无意返回 `null`。
- 不直接返回内部错误、堆栈、SQL、远端响应和凭据；通过集中映射产生稳定错误码与公开消息。

## 推荐的普通 JSON 契约

仓库没有既有约定、且正在创建普通 JSON 业务 API 时，优先采用：

```go
type Response[T any] struct {
    Code    uint32 `json:"code"`
    Message string `json:"message"`
    Data    T      `json:"data"`
}
```

- `code == 0` 表示成功，其他整数码由集中定义维护；调用方不要依赖消息文本做业务分支。
- 可以让成功和预期业务失败统一返回 HTTP 200，但必须在 OpenAPI 和项目文档中明确，并确保认证、代理、监控和客户端理解该约定。
- OAuth 跳转、文件下载、SSE/WebSocket、静态资源、健康探针、缓存协商、限流和纯 HTTP 协议错误保留真实 HTTP 语义。
- 已有仓库使用 REST 状态码、Problem Details、GraphQL 或其他协议时，沿用现有契约，不改成三段式响应。

## 中间件

按实际风险和仓库约定考虑：

- Request ID、Trace Context、访问日志、Recovery、Deadline、Body Limit、认证、授权、CSRF、CORS 和安全 Header。
- 中间件顺序必须有测试；Recovery、日志和关联字段应覆盖后续中间件与 Handler。
- 认证和授权是不同边界。不要因为复用 Handler 就放宽 JWT、Session、mTLS、API Key 等凭据来源。
- 不信任 `X-Forwarded-*`、Client IP 和 Host，除非部署拓扑及受信代理已明确配置。

## 文档与测试

- 修改 DTO、路由、状态码、安全定义或错误码时同步更新 OpenAPI/Swagger 和生成客户端。
- 测试精确 method/path、Content-Type、空集合、非法输入、认证来源、超时、Panic、重复写入和协议特例。
- 框架行为与版本有关时，读取 `go.mod` 锁定版本的官方文档或源码，并用最小测试确认。
