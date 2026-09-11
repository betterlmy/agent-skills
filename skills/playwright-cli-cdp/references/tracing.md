# 链路追踪（Tracing）排障指南

在 Windows PowerShell 环境中，将 `bash scripts/playwright-cdp.sh` 替换为 `powershell -ExecutionPolicy Bypass -File scripts\playwright-cdp.ps1`。

链路追踪能够录制执行过程中的全量上下文数据，包含每一步前后的 DOM 快照、截图、网络请求明细以及控制台输出，极其适合排障与复杂链路取证。

## 基础操作命令

```bash
bash scripts/playwright-cdp.sh -s=cdp tracing-start
bash scripts/playwright-cdp.sh -s=cdp goto https://example.com
bash scripts/playwright-cdp.sh -s=cdp click e1
bash scripts/playwright-cdp.sh -s=cdp fill e2 "测试数据"
bash scripts/playwright-cdp.sh -s=cdp tracing-stop
```

## 追踪产物目录说明

调用 `tracing-stop` 后，文件会自动写入 `traces/` 目录：

| 文件 / 目录 | 记录的核心内容 |
|---|---|
| `trace-{timestamp}.trace` | 动作序列、操作前后的完整 DOM 快照、截图、控制台日志、时序耗时 |
| `trace-{timestamp}.network` | 所有网络请求与响应报文、Header、Body 内容、响应耗时、资源体积 |
| `resources/` | 网页重放所需的静态资源缓存 |

## 核心应用场景

### 1. 调试偶发失败的指针或表单操作
```bash
bash scripts/playwright-cdp.sh -s=cdp tracing-start
bash scripts/playwright-cdp.sh -s=cdp goto https://app.example.com
bash scripts/playwright-cdp.sh -s=cdp click e5
bash scripts/playwright-cdp.sh -s=cdp tracing-stop
```

### 2. 页面加载性能瀑布流分析
```bash
bash scripts/playwright-cdp.sh -s=cdp tracing-start
bash scripts/playwright-cdp.sh -s=cdp goto https://slow-site.com
bash scripts/playwright-cdp.sh -s=cdp tracing-stop
```
通过 Trace Viewer 的网络瀑布流快速定位造成阻塞的长耗时静态资源或 API。

### 3. 长流程多步骤交互证据保存
```bash
bash scripts/playwright-cdp.sh -s=cdp tracing-start
bash scripts/playwright-cdp.sh -s=cdp goto https://app.example.com/checkout
bash scripts/playwright-cdp.sh -s=cdp fill e1 "4111111111111111"
bash scripts/playwright-cdp.sh -s=cdp fill e2 "12/25"
bash scripts/playwright-cdp.sh -s=cdp fill e3 "123"
bash scripts/playwright-cdp.sh -s=cdp click e4
bash scripts/playwright-cdp.sh -s=cdp tracing-stop
```

## 追踪文件清理建议

```bash
find .playwright-cli/traces -mtime +7 -delete
```
链路追踪会带来一定的运行时开销，且追踪文件体积增长较快，建议定期清理历史旧文件，或仅在关键排查环节开启。
