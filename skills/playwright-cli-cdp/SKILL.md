---
metadata:
  external-cli: "true"
  cli-compatibility: "references/cli-compatibility.md"
name: playwright-cli-cdp
description: 纯 CDP（Chrome DevTools Protocol）方式的浏览器控制工具，基于 playwright-cli。Use when 需要以远程调试模式启动 Chrome、仅通过 --cdp 端点挂载、驱动已挂载的页面、检查控制台/网络/存储，或发送原生 Chrome DevTools Protocol 协议指令；不得用于普通 playwright-cli open、非 CDP 浏览器启动、浏览器插件调试或 Playwright test debug 挂载工作流。
allowed-tools: Bash(playwright-cli:*) Bash(npx:*) Bash(npm:*) Bash(bash:*) Bash(curl:*) Bash(lsof:*) Bash(pgrep:*) Bash(mkdir:*) Bash(pwsh:*) Bash(powershell:*) Bash(powershell.exe:*)
---

# playwright-cli CDP

## 默认行为与硬性约束

本 Skill 专为**纯 CDP 模式**设计。所有浏览器自动化操作必须通过 Chrome DevTools Protocol 调试端点以及 `playwright-cli attach --cdp=...` 进行连接。

严禁使用 `playwright-cli open`、`--browser=...`、直接启动 Firefox/WebKit、安装插件，或使用 Playwright test debug 调试工作流。若当前已存在可连通的 CDP 端点，直接复用该端点；若无可用端点，则在本地 `127.0.0.1:9222` 启动 Chrome 远程调试模式，并使用 `cdp` 作为默认会话名称挂载 `playwright-cli`。

保持 CDP 端点仅限本地。严禁将调试端口绑定到 `0.0.0.0` 或任何公网接口，除非用户明确要求且知晓安全风险。

**严禁在任务完成时擅自关闭、kill、重启、分离或清理已存在的 CDP 端点或浏览器进程。** 始终保持 Chrome 及其调试端口持续运行，除非用户明确要求关闭。若用户主动要求清理，优先使用 `bash scripts/playwright-cdp.sh -s=<session> detach` 断开挂载；仅在用户明确指示关闭/杀死 Chrome 时才终止浏览器进程。

默认页面导航与操作超时设置为 15 秒。始终通过包内包装脚本运行 `playwright-cli`，以确保所有命令继承 `PLAYWRIGHT_MCP_TIMEOUT_NAVIGATION=15000`（覆盖 URL 打开、`goto`、标签页切换、页面重载等导航等待）：

- Bash / macOS / Linux / WSL2：`bash scripts/playwright-cdp.sh ...`
- Windows PowerShell：`powershell -ExecutionPolicy Bypass -File scripts\playwright-cdp.ps1 ...`

仅在必要时通过环境变量覆盖超时时长：`PLAYWRIGHT_CLI_CDP_PAGE_TIMEOUT_MS=<毫秒数>`。若页面导航超时，直接汇报超时详情并通过现有 CDP 会话检查当前页面状态，切勿擅自重启端点。

包装脚本会自动将 playwright-cli 的输出（控制台日志 `console-*.log`、页面快照 `page-*.yml`）重定向到专用临时目录（macOS/Linux/WSL2 为 `$TMPDIR/playwright-cli-cdp`，Windows 为 `%TEMP%\playwright-cli-cdp`），保持工作目录整洁。playwright-cli 在 skill 模式下总会将快照与日志写入临时文件并返回链接，需要查看快照时使用 `read` 读取该文件。内置存储容量上限（`PLAYWRIGHT_MCP_OUTPUT_MAX_SIZE`，默认 50 MiB）会自动清理跨会话的历史文件，但绝不会误删当前命令写入的文件。可通过环境变量自定义配置。

## 快速上手

运行内置脚本前，先基于本 Skill 目录解析脚本的相对路径。
先阅读 [CLI 兼容性契约](references/cli-compatibility.md)；环境检查脚本会排查命令可用性并报告潜在版本漂移。

macOS、Linux 或带有 Linux 浏览器的 WSL2：

```bash
bash scripts/check-environment.sh
bash scripts/open-chrome-remote.sh
```

Windows PowerShell：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\check-environment.ps1
powershell -ExecutionPolicy Bypass -File scripts\open-chrome-remote.ps1
```

WSL2 环境调用宿主 Windows Chrome：

```bash
win_script="$(wslpath -w scripts/open-chrome-remote.ps1)"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$win_script"
```

当 PowerShell 脚本存储在 WSL 文件系统内时，不要猜测 `C:\Users\...` 路径。优先使用 `wslpath -w`；若必须传递字面 `\\wsl.localhost\...` 路径，用单引号包裹 PowerShell 命令以避免转义消耗。

挂载并驱动 CDP 会话：

```bash
bash scripts/playwright-cdp.sh -s=cdp attach --cdp=http://127.0.0.1:9222
bash scripts/playwright-cdp.sh -s=cdp goto https://example.com
bash scripts/playwright-cdp.sh -s=cdp snapshot
bash scripts/playwright-cdp.sh -s=cdp click e15
bash scripts/playwright-cdp.sh -s=cdp eval "document.title"
```

Windows PowerShell 等价命令：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\playwright-cdp.ps1 -s=cdp attach --cdp=http://127.0.0.1:9222
powershell -ExecutionPolicy Bypass -File scripts\playwright-cdp.ps1 -s=cdp goto https://example.com
powershell -ExecutionPolicy Bypass -File scripts\playwright-cdp.ps1 -s=cdp snapshot
```

启动时直接打开指定目标 URL：

macOS、Linux 或 WSL2：

```bash
bash scripts/check-environment.sh
bash scripts/open-chrome-remote.sh https://example.com
```

Windows PowerShell：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\check-environment.ps1
powershell -ExecutionPolicy Bypass -File scripts\open-chrome-remote.ps1 https://example.com
```

然后执行挂载：

```bash
bash scripts/playwright-cdp.sh -s=cdp attach --cdp=http://127.0.0.1:9222
```

若用户直接给出了现成的端点地址，直接连入，切勿启动新浏览器：

```bash
bash scripts/playwright-cdp.sh -s=cdp attach --cdp=http://127.0.0.1:9223
bash scripts/playwright-cdp.sh -s=prod attach --cdp=https://debug.example.internal
```

## 端点健康检查

除非当前任务已在正常运行的活动 CDP 会话中，否则在启动或连接前先执行环境检查：

```bash
bash scripts/check-environment.sh
```

可提前验证端点健康状态：

```bash
curl -fsS http://127.0.0.1:9222/json/version
curl -fsS http://127.0.0.1:9222/json/list
```

若端点未就绪，使用内置脚本启动远程模式 Chrome。若端口已被非 CDP 进程占用，排查并指定其他 `CDP_PORT`：

```bash
lsof -iTCP:9222 -sTCP:LISTEN
CDP_PORT=9333 bash scripts/open-chrome-remote.sh
```

挂载到自定义端口：

```bash
bash scripts/playwright-cdp.sh -s=cdp attach --cdp=http://127.0.0.1:9333
```

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

若普通 `click` 持续等待可见元素，或组合框/弹窗等复合组件键盘行为不一致，参阅 [交互失败排查与验收边界](references/interaction-troubleshooting.md) 检查活动页面、点击命中区、动效与替代路径。切勿通过直接操作 DOM 或直接发起 API 请求掩盖指针交互失败。

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

使用多个 CDP 端点时，按端点或用途命名会话：

```bash
bash scripts/playwright-cdp.sh -s=local attach --cdp=http://127.0.0.1:9222
bash scripts/playwright-cdp.sh -s=staging attach --cdp=http://127.0.0.1:9333
```

## 安装与降级策略

若全局 CLI 命令不可用，先尝试本地免安装方式：

```bash
npx --no-install playwright-cli --version
bash scripts/playwright-cdp.sh -s=cdp attach --cdp=http://127.0.0.1:9222
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
