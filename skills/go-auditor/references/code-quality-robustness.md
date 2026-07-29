# 核心代码质量与健壮性（第二步·上）

本文件覆盖复杂度、重复逻辑、错误处理、边界防御和资源释放。所有命令必须限制在用户范围；文件和 diff 审计可以读取所属函数、package 与测试作为上下文，但只统计正式范围内的问题。文本或阈值命中都只是候选。

## 复杂度与可读性

- 巨型函数：圈复杂度高、嵌套深。检测：

  ```bash
  find . -name '*.go' -not -path '*/vendor/*' -exec wc -l {} + | sort -rn | head
  rg -n '^\s*(if|for|switch|select)\b' --type go -c | sort -t: -k2 -rn | head
  ```

  函数行数和嵌套层数用于排序候选，不设跨仓库通用的自动失败阈值。确认职责混杂、分支难以推理或测试困难后再提出拆分建议。

- 重复代码：用 `dupl` 或人工阅读发现候选。只有语义稳定且抽象不会引入错误耦合时才建议提炼；相似但独立演化的业务规则可以保留重复。

## 错误处理

- 异常吞没（忽略错误）：

  ```bash
  rg -n '_\s*=\s*err|,\s*_\s*:?=.*\(' --type go
  rg -n 'defer\s+\w+\.Close\(\)\s*$' --type go    # Close 错误被忽略
  ```

  DB 写、RPC、事务提交或文件写入吞错可能达到阻断级，但必须结合调用可达性、补偿机制和实际影响定级。只读关闭错误通常优先级较低，写入完成或事务错误需要重点确认。

- 错误上下文：直接返回 `err` 只有在跨越抽象边界且调用方无法判断失败步骤时才属于上下文缺失。避免每层机械包装；需要包装时使用 `%w` 保留错误链。

- 字符串比对错误（脆弱）：`if err.Error() == "xxx"` 或 `strings.Contains(err.Error(), ...)`。应改 `errors.Is`/`errors.As`。检测：

  ```bash
  rg -n 'err\.Error\(\)|strings\.Contains\(.*err' --type go
  ```

- 错误契约：检查调用方是否需要 `errors.Is`/`errors.As` 判定，以及 sentinel 或类型化错误是否稳定。错误定义分散本身不等于缺陷。

## 边界防御

- 空指针/nil：解引用前未判空；interface 持 nil（`var x Interface = nil` 陷阱，`x == nil` 为 false）。
- 切片/map 越界：外部输入直接索引未校验长度。
- 数值溢出：`int32`/`uint32` 转换、时间戳乘法未防溢出。
- 输入校验：负数、超长字符串、零值、分页参数未校验直接进查询。

## 资源释放

- `Rows`/`Body`/`File`/`Closer` 必须 `defer Close()`。检测遗漏：

  ```bash
  rg -n '\.Body\b|\.Rows\b|os\.Open|os\.Create' --type go
  ```

  对照附近是否有 `defer ...Close()`。

- `defer` 误用：循环内 defer（资源滞后到函数结束才释放）、锁内 `defer Unlock`（持锁时间被拉长）、`defer` 在大循环里累积。
- 事务：`Begin` 后是否保证 `Rollback`/`Commit` 都有路径；`Commit` 错误是否被忽略。

## panic 与 recover

- 业务代码里的 `panic`：检查它是否符合不可恢复不变量或仓库约定；可恢复输入和外部失败通常应返回 error。检测 `rg -n 'panic\(' --type go -g '!*_test.go'`。
- panic 边界：确认服务入口和自行启动的长驻 goroutine 是否符合仓库的崩溃与恢复策略。入口中间件无法恢复其他 goroutine 的 panic；不要把无条件 `recover` 当作通用修复。

## 产出

- 巨型函数与深嵌套清单（附行号与圈复杂度估计）。
- 错误处理问题分类：吞没 / 上下文丢失 / 字符串比对 / 错误契约不稳定。
- 边界防御缺口与资源释放遗漏点。
- panic 误用与 recover 缺口。
