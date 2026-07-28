# Go Dev 规则级基线评估

## 评估方法

本次将 Git HEAD 中的旧版 Skill 与当前工作区新版 Skill 对照，使用 `cases.json` 的代表性任务检查触发边界、参考路由和明确规则。该结果是规则级静态评估，不是两个隔离 Agent 的真实生成结果；实际模型触发率和输出质量仍需在发布前做安装后 A/B 测试。

## 对照结果

| 场景 | 旧版行为风险 | 新版预期 | 规则级结果 |
| --- | --- | --- | --- |
| 已有 Gin 契约增加接口 | 强制模板、完整 DTO 日志、内部错误外泄 | 仓库契约优先，加载 HTTP、日志与测试参考 | 通过 |
| Go CLI goroutine 无法退出 | 没有 goroutine 所有权、取消和竞态指导 | 加载错误、Context、并发与测试参考 | 通过 |
| GORM + MySQL 新增表 | MySQL 规则可用，但强制全局 DB、Debug 和固定字段 | 仅在识别 GORM/MySQL 后加载可选参考 | 通过 |
| gRPC 服务端流 | 只覆盖 Unary 风格，业务错误一律返回 nil error | 覆盖流、取消、大小限制和 Status 语义 | 通过 |
| pgx 事务评审 | 会路由到 GORM/MySQL 规则 | 使用技术栈中立持久化与事务规则，不建议引入 GORM | 通过 |
| 新建标准库内部 JSON API | 模板绑定 Gin | 支持 `net/http`，仓库无约定时推荐三段式整数业务码 | 通过 |
| 已有 Problem Details API | 会强制改成 HTTP 200 三段式响应 | 现有公开契约优先，不改变协议 | 通过 |
| 只读 Go PR 评审 | 未明确修改授权边界 | 开始前区分实现与评审，只读请求不修改 | 通过 |
| Go 服务增加本地 `.env` | 容易使用隐式 autoload、覆盖部署变量或让生产依赖文件 | 显式可选加载，外部环境优先，提交安全示例并覆盖边界测试 | 通过 |
| Python API、React、独立 Snowflake SQL | 描述中的 API、数据库、SQL 词容易过触发 | 描述限定 Go 项目，评估集包含不触发断言 | 通过 |

## 发布前剩余验证

1. 将旧版和新版分别安装到隔离 Agent 环境。
2. 对 `cases.json` 至少运行全部 should-trigger 和 should-not-trigger Prompt。
3. 记录实际加载的参考文件、输出差异、遗漏、不必要步骤、耗时和 Token。
4. 只根据可泛化失败调整描述和路由，不为单个 Prompt 增加特例。
