---
name: go-dev
description: 面向通用 Go 项目的开发与评审规范，先识别仓库约束和实际技术栈，再指导命名、错误处理、Context、日志、HTTP/gRPC、持久化、并发与测试。Use when working in a Go repository to write, review, refactor, or debug Go code, services, APIs, database access, migrations, concurrency, tests, or project conventions; load framework-specific guidance only when the repository actually uses that stack.
---

# Go Dev

## 规则优先级

按以下顺序处理冲突，低优先级规则不得覆盖高优先级事实：

1. 用户明确要求。
2. 仓库中的 `AGENTS.md`、`CONTRIBUTING.md`、设计文档和公开契约。
3. 仓库已有架构、依赖、封装、生成流程和测试方式。
4. Go 官方惯例、依赖的对应版本文档和本 Skill 的必须规则。
5. 本 Skill 的推荐风格。

不要为套用示例而引入第二套路由、日志、配置、错误码、ORM、DAO 或测试体系。仓库规则缺失时才使用推荐风格；发现冲突时说明冲突并沿用仓库选择。

## 开始前

1. 检查工作区状态并保留已有改动。
2. 阅读适用的仓库指令，再检查 `go.mod`、`go.work`、Makefile、生成配置和相关测试。
3. 确认任务属于实现、评审、排障还是设计；没有修改授权时只给结论和证据。
4. 根据实际任务读取最小参考，不因关键词加载所有文件。

## 参考路由

- 命名、包设计、配置和依赖：读 `references/core-go.md`。
- 错误、Context、资源和并发：读 `references/errors-context.md`。
- 日志、敏感信息和可观测性：读 `references/logging-security.md`。
- `net/http`、Gin、Echo、Chi 等 HTTP API：读 `references/http-api.md`。
- gRPC、Protobuf 或拦截器：读 `references/grpc.md`。
- `database/sql`、pgx、sqlc、GORM、迁移或 SQL：读 `references/persistence.md`；仓库实际使用 GORM 时再读 `references/gorm-database.md`，编写 SQL 时再读 `references/sql-standards.md`。
- 测试、静态检查和生成物：读 `references/testing.md`。
- 只有需要起始模板时才读取 `examples/`；示例中的包路径和组件必须替换为当前仓库已有实现。

## 必须规则

- 代码必须通过 `gofmt`；命名遵循 Go 惯例，缩写使用 `ID`、`URL`、`HTTP` 等一致形式。
- I/O、RPC、数据库和外部 API 调用接收并传播 `context.Context`；不得用 `context.Background()` 绕过已有取消链。
- 错误使用 `%w` 包装并用 `errors.Is`、`errors.As` 分类；不得依赖错误字符串做业务分支。
- 文件、响应体、Rows、Ticker、事务和 goroutine 必须有明确的关闭、回收或退出路径。
- 禁止无界读取、无界并发、goroutine 泄漏、数据竞争，以及忽略关键写入、提交或关闭错误。
- 不记录或返回凭据、完整敏感请求、内部堆栈、SQL 参数、未受控远端正文或原始内部错误。
- 不凭空假设框架、中间件、数据库、日志包、配置库和响应协议；版本敏感行为以仓库锁定版本及官方资料为准。
- 修改共享契约、生成输入、数据库 Schema 或并发状态时，必须检查调用方并补最接近行为边界的测试。

## 推荐风格

仓库没有相反约定时，默认采用以下风格：

- 对话、Markdown 文档和变更说明使用中文；代码标识符、外部协议和依赖名称沿用其英文约定。
- Handler 只做输入、认证上下文、用例调用和响应映射；业务规则放在 service/application/domain 层。
- 使用窄接口和构造函数注入依赖，避免包级可变全局变量。
- 错误码和公开消息集中定义，内部错误只用于日志和诊断，不直接暴露给调用方。
- 新建普通 JSON 业务 API 时，优先采用 `{code,message,data}`；成功和业务失败可统一使用 HTTP 200，但必须记录协议决定，并为重定向、下载、流式响应、探针和纯 HTTP 协议错误保留真实状态语义。
- List 数据初始化为空切片，公开 JSON 返回 `[]` 而不是 `null`，除非契约明确要求可空。
- 在统一中间件或拦截器记录入口、出口、耗时和关联 ID；业务日志记录事件与白名单字段，不打印完整请求或响应。
- DTO、领域对象和持久化模型分离；转换函数保持显式、可测试，避免传输或 ORM 标签污染领域层。
- 导出标识符写以名称开头的有意义注释；复杂决策解释原因和约束，不复述代码。

## 完成前

1. 运行仓库真实存在且与改动匹配的格式化、测试、静态检查、竞态检查和生成检查。
2. 检查实际差异、未跟踪文件、生成物漂移和是否需要同步文档。
3. 区分已通过检查、条件跳过项、未运行的外部环境验证和剩余风险。
4. 不把“已编写”“静态检查通过”或“等待 CI”表述成真实环境验证成功。
