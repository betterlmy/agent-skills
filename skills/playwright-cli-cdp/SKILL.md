---
metadata:
  external-cli: "true"
  cli-compatibility: "references/cli-compatibility.md"
name: playwright-cli-cdp
description: 纯 CDP（Chrome DevTools Protocol）浏览器控制，基于 playwright-cli，支持多 Agent 独立 Profile、动态端口和唯一会话。Use when 需要以远程调试模式启动 Chrome、仅通过 --cdp 端点挂载、驱动已挂载的页面、检查控制台/网络/存储，或发送原生 Chrome DevTools Protocol 协议指令；不得用于普通 playwright-cli open、非 CDP 浏览器启动、浏览器插件调试或 Playwright test debug 挂载工作流。
allowed-tools: Bash(python3:*) Bash(playwright-cli:*) Bash(npx:*) Bash(npm:*) Bash(bash:*) Bash(curl:*) Bash(lsof:*) Bash(pgrep:*) Bash(mkdir:*) Bash(pwsh:*) Bash(powershell:*) Bash(powershell.exe:*)
---

# playwright-cli CDP

## 默认行为与硬性约束

本 Skill 专为**纯 CDP 模式**设计。所有浏览器自动化操作必须通过 Chrome DevTools Protocol 调试端点以及 `playwright-cli attach --cdp=...` 进行连接。

严禁使用 `playwright-cli open`、`--browser=...`、直接启动 Firefox/WebKit、安装插件，或使用 Playwright test debug 调试工作流。

- 用户明确提供端点 -> 连接该端点，使用本任务唯一 CLI 会话，不新建浏览器；共享端点不代表状态隔离。
- 当前任务已有专属实例 -> 复用已记录的 `session`、`endpoint`、`profile`；不要每条命令重新启动。
- 否则 -> 使用启动脚本创建新 Profile，以 `--remote-debugging-port=0` 让系统分配端口，并读取 `DevToolsActivePort`。不得因为发现可用的 `9222` 就接管其他任务浏览器。
- 启动成功仅输出 JSON `{session, endpoint, profile}`；在任务记录中保存这三项，不保存 Cookie 或凭据。所有命令固定使用返回的 session。详情见 [独立实例与并发测试](references/isolated-instances.md)。

保持 CDP 端点仅限本地。严禁将调试端口绑定到 `0.0.0.0` 或任何公网接口，除非用户明确要求且知晓安全风险。

**严禁在任务完成时擅自关闭、kill、重启、分离或清理已存在的 CDP 端点或浏览器进程。** 始终保持 Chrome 及其调试端口持续运行，除非用户明确要求关闭。若用户主动要求清理，优先使用 `bash scripts/playwright-cdp.sh -s=<session> detach` 断开挂载；仅在用户明确指示关闭/杀死 Chrome 时才终止浏览器进程。

默认页面导航与操作超时设置为 15 秒。始终通过包内包装脚本运行 `playwright-cli`，以确保所有命令继承 `PLAYWRIGHT_MCP_TIMEOUT_NAVIGATION=15000`（覆盖 URL 打开、`goto`、标签页切换、页面重载等导航等待）：

- Bash / macOS / Linux / WSL2：`bash scripts/playwright-cdp.sh ...`
- Windows PowerShell：`powershell -ExecutionPolicy Bypass -File scripts\playwright-cdp.ps1 ...`

仅在必要时通过环境变量覆盖超时时长：`PLAYWRIGHT_CLI_CDP_PAGE_TIMEOUT_MS=<毫秒数>`。若页面导航超时，直接汇报超时详情并通过现有 CDP 会话检查当前页面状态，切勿擅自重启端点。

包装脚本把日志和快照写入临时目录的 `playwright-cli-cdp/<session>`，容量预算默认每会话 50 MiB，避免跨任务清理。使用 `-s=<session>` 或 `--session=<session>` 的等号形式；会话名限 1–80 位 ASCII 字母、数字、下划线、连字符。显式 `PLAYWRIGHT_MCP_OUTPUT_DIR` 会覆盖隔离目录。需要查看快照时用 `read` 读取返回文件。

## 快速上手

运行内置脚本前，先基于本 Skill 目录解析脚本的相对路径。
先阅读 [CLI 兼容性契约](references/cli-compatibility.md)；环境检查脚本会排查命令可用性并报告潜在版本漂移。

macOS / Linux / WSL2（WSL 自动调用宿主 Windows PowerShell；原生 Linux/macOS 需要 Python 3）：

```bash
instance="$(bash scripts/open-chrome-remote.sh)" || exit 1
session="$(printf '%s' "$instance" | python3 -c 'import json,sys; print(json.load(sys.stdin)["session"])')"
endpoint="$(printf '%s' "$instance" | python3 -c 'import json,sys; print(json.load(sys.stdin)["endpoint"])')"
CDP_ENDPOINT="$endpoint" bash scripts/check-environment.sh
bash scripts/playwright-cdp.sh -s="$session" attach --cdp="$endpoint"
bash scripts/playwright-cdp.sh -s="$session" goto https://example.com
bash scripts/playwright-cdp.sh -s="$session" snapshot
```

Windows PowerShell：

```powershell
$instance = & .\scripts\open-chrome-remote.ps1 | ConvertFrom-Json
if (-not $instance.endpoint) { throw 'CDP startup failed' }
& .\scripts\check-environment.ps1 -Endpoint $instance.endpoint
& .\scripts\playwright-cdp.ps1 "-s=$($instance.session)" attach "--cdp=$($instance.endpoint)"
```

启动脚本也接受初始 URL。启动失败时停止，不使用其他浏览器兜底；保存报错中的 session/profile 以供排查。WSL 若找不到 `powershell.exe`，脚本会尝试系统标准挂载路径；不猜测用户目录。

用户指定端点时跳过启动，生成唯一会话后 attach。以下命令速查中的 `-s=cdp` **仅是占位示例**，执行时必须替换为本任务 session，不是共享默认名。

## 端点健康检查

已有本任务活动会话可跳过重复检查。用户指定端点时先检查；新建实例时启动后传入实际 endpoint 检查（默认 9222 不可达不应阻止独立实例启动）：

```bash
CDP_ENDPOINT="$endpoint" bash scripts/check-environment.sh
```

检查当前任务返回的端点，而不是固定探测 9222：

```bash
curl -fsS --max-time 3 "$endpoint/json/version"
curl -fsS --max-time 3 "$endpoint/json/list"
```

动态端口无需预扫描。只有用户明确需要固定端口时才使用 `CDP_PORT`（PowerShell `-Port`）；固定端口的空闲预检查不是原子保留，不适用于并发分配。启动器不复用任何已有 Profile 或已占用端口。

## 挂载后的核心交互命令

常规页面交互推荐使用基于快照的元素引用编号（Snapshot refs，如 `e3`、`e15`）：

```bash
bash scripts/playwright-cdp.sh -s=cdp snapshot
bash scripts/playwright-cdp.sh -s=cdp snapshot --boxes
bash scripts/playwright-cdp.sh -s=cdp snapshot --depth=4
bash scripts/playwright-cdp.sh -s=cdp snapshot e34
bash scripts/playwright-cdp.sh -s=cdp snapshot --filename=after-click.yaml
bash scripts/playwright-cdp.sh -s=cdp goto https://playwright.dev
bash scripts/playwright-cdp.sh -s=cdp click e3
bash scripts/playwright-cdp.sh -s=cdp dblclick e7
bash scripts/playwright-cdp.sh -s=cdp fill e5 "user@example.com" --submit
bash scripts/playwright-cdp.sh -s=cdp type "search query"
bash scripts/playwright-cdp.sh -s=cdp press Enter
bash scripts/playwright-cdp.sh -s=cdp hover e4
bash scripts/playwright-cdp.sh -s=cdp select e9 "option-value"
bash scripts/playwright-cdp.sh -s=cdp upload ./document.pdf
bash scripts/playwright-cdp.sh -s=cdp drop e4 --path=./image.png
bash scripts/playwright-cdp.sh -s=cdp drop e4 --data="text/plain=hello world"
bash scripts/playwright-cdp.sh -s=cdp check e12
bash scripts/playwright-cdp.sh -s=cdp uncheck e12
bash scripts/playwright-cdp.sh -s=cdp screenshot --filename=page.png
```

当引用编号不稳定时，使用 CSS 选择器或 Playwright Locators：

```bash
bash scripts/playwright-cdp.sh -s=cdp click "#main > button.submit"
bash scripts/playwright-cdp.sh -s=cdp click "getByRole('button', { name: 'Submit' })"
bash scripts/playwright-cdp.sh -s=cdp click "getByTestId('submit-button')"
```

若普通 `click` 持续等待可见元素，或组合框/弹窗等复合组件键盘行为不一致，参阅 [交互失败排查与验收边界](references/interaction-troubleshooting.md) 检查活动页面、点击命中区、动效与替代路径。完整 UI 验收还须执行其中的长数据、低高度桌面、嵌套 Escape 与真实服务／Fixture 证据清单；默认短数据点击通过不能替代这些边界。切勿通过直接操作 DOM 或直接发起 API 请求掩盖指针交互失败。

将已挂载浏览器交给用户手动验收前，按该参考的“文件选择窗口被自动化拦截”步骤，在所有挂载同一页面的 CLI 会话中释放文件选择拦截；保持 Chrome 和 CDP 连接运行。页面上传点击触发 `File chooser` 而系统窗口不出现时，先排查这一工具状态。

## 标签页管理与导航控制

```bash
bash scripts/playwright-cdp.sh -s=cdp tab-list
bash scripts/playwright-cdp.sh -s=cdp tab-new https://example.com/page
bash scripts/playwright-cdp.sh -s=cdp tab-select 0
bash scripts/playwright-cdp.sh -s=cdp tab-close 1
bash scripts/playwright-cdp.sh -s=cdp go-back
bash scripts/playwright-cdp.sh -s=cdp go-forward
bash scripts/playwright-cdp.sh -s=cdp reload
bash scripts/playwright-cdp.sh -s=cdp resize 1440 1000
bash scripts/playwright-cdp.sh -s=cdp pdf --filename=page.pdf
```

## 控制台、网络与存储管理

```bash
bash scripts/playwright-cdp.sh -s=cdp console
bash scripts/playwright-cdp.sh -s=cdp console error
bash scripts/playwright-cdp.sh -s=cdp requests
bash scripts/playwright-cdp.sh -s=cdp request 3

bash scripts/playwright-cdp.sh -s=cdp cookie-list
bash scripts/playwright-cdp.sh -s=cdp cookie-get session_id
bash scripts/playwright-cdp.sh -s=cdp cookie-set session_id abc123 --domain=example.com --httpOnly --secure
bash scripts/playwright-cdp.sh -s=cdp localstorage-list
bash scripts/playwright-cdp.sh -s=cdp localstorage-get token
bash scripts/playwright-cdp.sh -s=cdp sessionstorage-list

bash scripts/playwright-cdp.sh -s=cdp state-save auth.json
bash scripts/playwright-cdp.sh -s=cdp state-load auth.json
```

在自动化管道中使用 `--raw` 获取纯净数据流：

```bash
bash scripts/playwright-cdp.sh -s=cdp --raw eval "document.title"
bash scripts/playwright-cdp.sh -s=cdp --raw snapshot > page.yml
TOKEN=$(bash scripts/playwright-cdp.sh -s=cdp --raw cookie-get session_id)
```

使用 `--json` 获取结构化 JSON 格式数据：

```bash
bash scripts/playwright-cdp.sh -s=cdp list --json
```

## 键盘与鼠标底层操作

```bash
bash scripts/playwright-cdp.sh -s=cdp keydown Shift
bash scripts/playwright-cdp.sh -s=cdp keyup Shift
bash scripts/playwright-cdp.sh -s=cdp mousemove 150 300
bash scripts/playwright-cdp.sh -s=cdp mousedown
bash scripts/playwright-cdp.sh -s=cdp mousedown right
bash scripts/playwright-cdp.sh -s=cdp mouseup
bash scripts/playwright-cdp.sh -s=cdp mousewheel 0 100
```

## 原生对话框（Dialog）处理

```bash
bash scripts/playwright-cdp.sh -s=cdp dialog-accept
bash scripts/playwright-cdp.sh -s=cdp dialog-accept "确认文本"
bash scripts/playwright-cdp.sh -s=cdp dialog-dismiss
```

## 网络请求拦截与 Mock

```bash
bash scripts/playwright-cdp.sh -s=cdp route "**/*.jpg" --status=404
bash scripts/playwright-cdp.sh -s=cdp route "**/api/users" --body='[{"id":1}]' --content-type=application/json
bash scripts/playwright-cdp.sh -s=cdp route-list
bash scripts/playwright-cdp.sh -s=cdp unroute "**/*.jpg"
bash scripts/playwright-cdp.sh -s=cdp unroute
```

高级请求 Mock 方案参阅 [references/request-mocking.md](references/request-mocking.md)。

## 链路追踪与视频录制

```bash
bash scripts/playwright-cdp.sh -s=cdp tracing-start
bash scripts/playwright-cdp.sh -s=cdp tracing-stop

bash scripts/playwright-cdp.sh -s=cdp video-start recording.webm
bash scripts/playwright-cdp.sh -s=cdp video-chapter "章节标题" --description="详细说明" --duration=2000
bash scripts/playwright-cdp.sh -s=cdp video-stop
```

详细信息参阅 [references/tracing.md](references/tracing.md) 与 [references/video-recording.md](references/video-recording.md)。

## 界面调试工具

```bash
bash scripts/playwright-cdp.sh -s=cdp highlight e5
bash scripts/playwright-cdp.sh -s=cdp highlight e5 --style="outline: 3px dashed red"
bash scripts/playwright-cdp.sh -s=cdp highlight e5 --hide
bash scripts/playwright-cdp.sh -s=cdp highlight --hide
bash scripts/playwright-cdp.sh -s=cdp generate-locator e5 --raw
bash scripts/playwright-cdp.sh -s=cdp show --annotate
```

## 原生 CDP 协议指令执行

当任务需要调用 CLI 尚未直接封装的原生 Chrome DevTools Protocol 域或指令时，使用 `run-code`。从活动页面建立 CDP 会话，启用对应域并发送协议请求：

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  const cdp = await page.context().newCDPSession(page);
  return await cdp.send('Browser.getVersion');
}"
```

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send('Network.enable');
  return await cdp.send('Runtime.evaluate', {
    expression: 'navigator.userAgent',
    returnByValue: true
  });
}"
```

CDP 命令与参数严格区分大小写。主要用于探测浏览器底层机制、性能指标、设备模拟、测试覆盖率、安全状态和底层网络诊断。通过 `--cdp` 挂载成功后，常规交互依然优先使用 `playwright-cli` 的页面命令。

## 会话生命周期规则

针对通过 CDP 连接的外部浏览器，任务执行完毕后**必须保持 Chrome 进程和 CDP 端口处于运行状态**。严禁将 `detach`、`close`、`close-all`、`kill-all` 或强杀进程命令作为常规收尾清理动作。

仅在用户明确发出指令时才断开连接或关闭浏览器。若用户要求清理，优先选用 `bash scripts/playwright-cdp.sh -s=<session> detach`，以确保外部浏览器和调试端口不受影响。

多个 Agent 使用各自返回的 session/endpoint/profile，禁止接管其他任务实例。不同 Profile 不共享登录状态；同一业务账号的服务端数据仍可能互相影响。保留实例会消耗资源，关闭浏览器和删除 Profile 必须另获用户授权。

## 安装与降级策略

若全局 CLI 命令不可用，先尝试本地免安装方式：

```bash
npx --no-install playwright-cli --version
bash scripts/playwright-cdp.sh -s="$session" attach --cdp="$endpoint"
```

当全局 `playwright-cli` 二进制缺失时，包装脚本会自动无缝降级到 `npx --no-install playwright-cli`。

若本地环境均不存在该工具，经用户授权后进行安装：

```bash
npm install -g @playwright/cli@0.1.17
```

`0.1.17` 为本机验证基线版本。在尝试其他版本前必须执行环境与能力检查；安装成功不代表本 Skill 的所有命令均受支持。

## 配套参考文档

- CDP 启动与排错指南：[references/cdp-startup.md](references/cdp-startup.md)
- CLI 版本与能力契约：[references/cli-compatibility.md](references/cli-compatibility.md)
- CDP 原生协议用法配方：[references/cdp-recipes.md](references/cdp-recipes.md)
- 页面元素属性检查：[references/element-attributes.md](references/element-attributes.md)
- 交互失败排查与验收边界：[references/interaction-troubleshooting.md](references/interaction-troubleshooting.md)
- 网络请求 Mock：[references/request-mocking.md](references/request-mocking.md)
- 执行自定义 Playwright 代码：[references/running-code.md](references/running-code.md)
- 状态与存储管理：[references/storage-state.md](references/storage-state.md)
- 自动化测试代码生成：[references/test-generation.md](references/test-generation.md)
- 链路追踪（Tracing）：[references/tracing.md](references/tracing.md)
- 视频录制指南：[references/video-recording.md](references/video-recording.md)
