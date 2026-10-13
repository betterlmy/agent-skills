# 死代码工具链实战

目的：把“静态线索”升级为“消费者地图”所需的工具选择、已知盲区和删除顺序。只覆盖工具层；契约证明与删减边界仍按 [调查手册](investigation.md) 执行。

## 工具选择

| 栈 | 首选 | 补充 | 说明 |
| --- | --- | --- | --- |
| Go | `deadcode ./...`（`golang.org/x/tools/cmd/deadcode`） | `golangci-lint run --no-config --enable-only=unused` | `unused` 只报包内私有符号，常为 0；导出层可达性靠 `deadcode` |
| TS/JS | `knip --no-progress --reporter compact` | `tsc --noUnusedLocals --noUnusedParameters` | `tsc` 只管局部，管不到未使用的导出 |
| 文档 | 仓库自带链接校验（如 `verify-docs`） | `rg` 已删路径 | 代码删除后文档链接最先失效 |

- golangci-lint v2 已无 `--disable-all`，改用 `--enable-only=<linter>`；仓内 v1 配置在 v2 下可能报错，用 `--no-config`。
- 工具装到仓库之外（如 `/tmp/<tool>`），不改被审仓的 `package.json`/`go.mod`；先读用户级企业源规则，npm 与 Go 均走企业源。
- `go install` 与 `npm install` 属于改环境，先说明再装；用户已授权后不重复确认。

## 已知盲区（必须交叉验证）

- `deadcode` 只分析 main 依赖图。**完全孤立的包不会被完整报告**（例如整个包无人 import，却只报出少数函数）。补一轮：`go list -deps ./cmd/...` 与 `go list ./...` 求差集，得到不被 main 依赖的包。
- `deadcode -test` 把“测试里可达”算可达。两轮都跑：不含 `-test` 得到生产不可达全集，含 `-test` 得到连测试都不用的子集。清理以生产不可达为准，测试使用只说明还有测试依赖，不说明有生产价值。
- 调用图类工具的 `callers` 对同名方法不区分接收者类型：core 层 `Service.Turn` 与 handler `Handler.Turn` 会混在一起。用 `rg` 按接收者和调用点复核，别只信 callers 数。
- Go 的 HTTP handler 报不可达时，先查路由注册文件是否真的引用该方法（`router.go` 的 `handlers.X.Method`），而不是只看 handler 包内。
- knip 的 `Unused exports` 不含“被同文件使用的导出”：这类只需去掉 `export`，不需要删函数。

## “未接线”不等于“可删”

按证据强度分三档处理：

| 证据 | 处理 |
| --- | --- |
| 源码里有明确废弃标记（如 `Historical route retired`、`@deprecated` 且无消费者）、或整包全仓零 import | 可删 |
| 仅未接线，无废弃标记，有完整实现和测试 | 视为待接入能力，**默认保留**，向用户确认后才动 |
| 仅测试基础设施引用（如 `testsupport` fake） | 视为待接入能力，保留 |

- 用户明确说“能力还没接入，暂不删”后，把该子系统整体记为保留，后续扫描不再重复提议。
- 顶层包只有 `doc.go` 的“孤儿包”没有代码可删，直接忽略。

## 删除顺序（Go 后端）

1. 先删整包孤儿（零装配改动，风险最低）。
2. 再删“被构造但无路由使用”的包：同步清理 `router` 的字段与 nil 校验、`bootstrap` 的 import/构造/配置调用/注入，以及因此变孤儿的局部变量。
3. 再删包内未接线的方法和文件，随后清理只服务它们的响应类型与转换函数。
4. 最后删失去消费者的共享 helper。每步后都跑 `go build ./...` 与 `go vet ./...`，`vet` 会暴露测试文件里的残留引用。

- 生成物（swagger、proto、sqlc）与源码同步：删 handler 后跑仓库的生成命令与 `*-check`，同一变更提交。
- 删函数后检查 import 是否变孤儿；删含 `sort`/`strings` 的测试函数前先数这些包在文件内的其他使用。
- 契约测试里断言“某 DTO 定义存在”的用例，随被删 DTO 一起删，不要为让它通过而保留死 DTO。

## 删除顺序（TS 前端）

1. 先 `rg` 统计符号在定义文件内、`src`、`tests`、`scripts` 的出现次数，分三种处理：
   - 定义文件内出现 1 次、别处 0 次：只有定义，整段删除。
   - 定义文件内出现多次、别处 0 次：同文件仍在用，**只去掉 `export`**，不删代码。knip 的 `Unused exports` 大多是这一类。
   - 别处有引用：保留。
2. 删函数后跑 `tsc --noEmit`：`noUnusedLocals` 会暴露因此变孤儿的 import 和类型，逐个清掉；清掉一个又可能暴露下一个，循环到 typecheck 通过。
3. 再复扫 knip：每轮删除会暴露新的孤儿类型，直到收敛。
4. 只被自身测试使用的 API 模块（测试是它唯一消费者）连同测试一起删，测试数下降属预期，核对差值等于被删测试的用例数。
5. 导出的类型可能只服务于已删的类型（如 `DeliveryStatus` 只被 `AgentSendResult` 引用），按 2 的循环自然清掉。
- knip 的 `Unused files` 先查 `SKILL.md`、测试、`src` 入口、`package.json` scripts、Dockerfile/CI、文档对它的引用；有任何一处引用就不算死。无人引用但属于需手动传参的集成检查脚本，无法从代码判断是否废弃，列出来问用户，不直接删。
- `Unused dependencies` 的删除会改锁文件，单独确认。
- knip 报 `Unlisted binaries`、`Unresolved imports`（如 `cc`、`go`、原生 `.node` 产物）是配置噪声，不是删除线索。

## 文档与周边

- 代码删除后立刻跑文档链接校验；历史证据表格里的失效链接改为纯文本并注明“已随历史 API 删除”，不要删掉论证行。
- 用户已有的未提交改动与清理改动混在同一工作区：按路径分别统计，汇报时点明哪些是本次改动，提交时需分开。
- 未跟踪且被忽略的历史产物（任务记录、venv）删除不可从 Git 恢复，先说明恢复边界；root 属主残留需要提权，只对已授权的精确路径执行。

## 验证与汇报

- 每步用“构建 → 静态检查 → 测试 → 生成物校验”递进；全仓测试只在收尾跑一次。
- 汇报只给：删除量（代码与生成物分开）、关键废弃证据、验证结果、保留项及原因。不重复列选项让用户反复选择；用户说“能删就删”时，只对证据足够的项直接执行。
