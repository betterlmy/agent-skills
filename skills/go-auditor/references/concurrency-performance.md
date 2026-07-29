# 并发与性能安全（第二步·中）

数据竞争与 goroutine 泄漏往往延迟暴露，应结合生命周期、所有权、背压和取消路径审查。命令限制在用户范围；文件或 diff 涉及并发原语时，必须读取 goroutine 启动、停止和共享状态的完整上下文。关键词只能用于发现候选。

## goroutine 泄漏

无 `ctx`/`done` 退出的常驻 goroutine、`for-select` 无退出分支：

```bash
rg -n 'go\s+func' --type go
rg -n 'for\s*\{' --type go            # 无限循环，查是否有 return/ctx.Done 分支
```

重点看：

- `go func(){ ... }()` 内部循环或阻塞接收，外层无 cancel 机制。
- `for { select { case ...: } }` 缺少 `case <-ctx.Done(): return`。
- 启动 goroutine 后无 `WaitGroup`/channel 等待，函数返回后 goroutine 仍在跑。

## 无界并发

- `for { go ... }` 无 worker pool / semaphore 限流，输入大时 goroutine 爆炸。
- 应使用 buffered channel 或 `golang.org/x/sync/errgroup` + `SetLimit`。
- 无界读取：从外部源（MQ、channel、slice）不限量读入内存。

## 锁与共享状态

- `sync.Mutex` 范围过大（持锁做 IO/RPC），应缩小临界区或用读写锁。
- `defer Unlock` 是否拉长持锁时间取决于函数剩余工作；回读临界区后判断，不把语法形式直接视为性能问题。
- 未同步的 map 并发读写可能导致竞态或进程失败，通常属于阻断级候选。修复方式可能是所有权收敛、互斥锁或特定场景下的 `sync.Map`，不能机械替换。
- 锁拷贝：`go vet` 的 `copylocks` 能检出 `Mutex` 值拷贝。
- 死锁候选包括多锁顺序不一致和缺少生命周期退出的永久等待。`select` 没有 `default` 常常是正确的阻塞语义，不能单独视为死锁证据。

## channel

- 向已关闭 channel 发送会 panic；必须证明关闭与发送路径可能并发到达后再形成结论。
- 发送方关闭 channel：应由唯一发送方关闭，多发送方应避免关闭或用额外协调。
- nil channel 误用（nil channel 的收发永久阻塞，有时是技巧，有时是 bug）。

## Context 传播

- 请求链路里用 `context.Background()`/`TODO()` 绕过取消与超时：

  ```bash
  rg -n 'context\.Background\(\)|context\.TODO\(\)' --type go -g '!*_test.go' -g '!main.go'
  ```

  handler 或 service 层出现 `Background()` 是取消传播断链候选；若任务确有独立生命周期，应检查其专用超时、停止和回收机制。

- 下游 RPC/DB/HTTP 调用未传 ctx：`noctx`/`contextcheck` linter 可检出。
- goroutine 内未继承 ctx 导致取消不传播。

## 性能隐患

- N+1：循环内单条 DB/RPC 查询。见 `persistence-data.md`，也适用于 RPC 批量。
- 大切片未预分配：`append` 在已知长度时未 `make([]T, 0, n)`。`prealloc` linter。
- 字符串循环拼接：应用 `strings.Builder`。
- 热路径反射、`fmt.Sprintf`、正则重复编译。
- 不必要的值拷贝：大结构体按值传递/返回。

## 产出

- goroutine 泄漏点（无退出路径）与无界并发点。
- 锁/map/channel 问题清单。
- Context 传播断链点。
- 性能热点（N+1、分配、反射）。
