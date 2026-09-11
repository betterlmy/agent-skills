# CDP 启动与故障排查指南

本 Skill 专用于纯 CDP（Chrome DevTools Protocol）操作。启动或复用 Chrome 远程调试端点后，使用 `playwright-cli attach --cdp=...` 挂载连接。

若当前环境中已存在可连通的 CDP 端点，直接复用并保持其持续运行。严禁在任务完成时擅自关闭、kill、重启或分离现有浏览器进程与调试端口，除非用户明确指示。

## 多平台支持矩阵

| 操作系统环境 | 是否支持 | 推荐启动脚本路径 |
| --- | --- | --- |
| macOS | 是 | `bash scripts/open-chrome-remote.sh` |
| Linux | 是 | `bash scripts/open-chrome-remote.sh` |
| Windows | 是 | `powershell -ExecutionPolicy Bypass -File scripts\open-chrome-remote.ps1` |
| WSL2（使用 Linux 原生 Chrome/Chromium） | 是 | 在 WSL2 内部运行 `bash scripts/open-chrome-remote.sh` |
| WSL2（连接 Windows 宿主 Chrome） | 是（注意网络路由） | 在 Windows 端用 PowerShell 启动 Chrome，再从 WSL2 挂载到宿主网络端点 |

## 环境预检（Environment Check）

在启动或挂载前先执行环境检查，除非当前任务已在正常运行的活动 CDP 会话中：

macOS, Linux 或 WSL2：

```bash
bash scripts/check-environment.sh
```

Windows PowerShell：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\check-environment.ps1
```

预检脚本不会启动 Chrome，而是负责探测 `playwright-cli` 命令可用性、端点连通性、本地 Chrome 家族浏览器安装路径、基础端口冲突、危险的 `CDP_HOST=0.0.0.0` 绑定风险以及 WSL2 网络适配提示。

## macOS, Linux 或 WSL2 内部 Linux 浏览器

使用内置 Bash 脚本启动带有独立隔离用户配置的 Chrome 远程调试模式：

```bash
bash scripts/check-environment.sh
bash scripts/open-chrome-remote.sh
bash scripts/playwright-cdp.sh -s=cdp attach --cdp=http://127.0.0.1:9222
```

Bash 脚本默认配置：
- Host 监听地址：`127.0.0.1`
- 调试端口：`9222`
- 用户配置目录：`$HOME/.cache/playwright-cli-cdp/chrome-profile`
- 初始打开页面：`about:blank`

通过环境变量覆盖默认参数：

```bash
CDP_PORT=9333 bash scripts/check-environment.sh
CDP_PORT=9333 bash scripts/open-chrome-remote.sh https://example.com
CDP_USER_DATA_DIR=/tmp/chrome-cdp-profile bash scripts/open-chrome-remote.sh
CHROME_BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" bash scripts/open-chrome-remote.sh
```

macOS 手工启动参考：

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-address=127.0.0.1 \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.cache/playwright-cli-cdp/chrome-profile" \
  --no-first-run \
  --no-default-browser-check
```

Linux 手工启动参考：

```bash
google-chrome \
  --remote-debugging-address=127.0.0.1 \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.cache/playwright-cli-cdp/chrome-profile" \
  --no-first-run \
  --no-default-browser-check
```

## Windows PowerShell

使用内置 PowerShell 脚本：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\check-environment.ps1
powershell -ExecutionPolicy Bypass -File scripts\open-chrome-remote.ps1
powershell -ExecutionPolicy Bypass -File scripts\playwright-cdp.ps1 -s=cdp attach --cdp=http://127.0.0.1:9222
```

PowerShell 脚本默认配置：
- Host：`127.0.0.1`
- Port：`9222`
- 用户配置目录：`%LOCALAPPDATA%\playwright-cli-cdp\chrome-profile`
- 初始页面：`about:blank`

通过环境变量覆盖默认配置：

```powershell
$env:CDP_PORT = "9333"
powershell -ExecutionPolicy Bypass -File scripts\open-chrome-remote.ps1 https://example.com
```

## 常见排障速查

| 故障现象 | 根因与修复操作 |
|---|---|
| 端口 `9222` 已被占用 | 使用 `lsof -iTCP:9222 -sTCP:LISTEN`（macOS/Linux）或 `netstat -ano \| findstr :9222`（Windows）排查进程。若非 CDP 进程占用，通过 `CDP_PORT=9333` 切换端口 |
| Chrome 启动后立即退出 | 检查是否已存在使用相同 `user-data-dir` 的活跃 Chrome 实例；Chrome 不允许多个进程复用同一配置目录 |
| `curl http://127.0.0.1:9222/json/version` 报错拒绝连接 | 说明远程调试模式尚未启动成功，需检查 Chrome 实际启动日志 |
| WSL2 无法访问宿主 Windows 的 `127.0.0.1:9222` | 在 WSL2 中应通过宿主机器的虚拟网卡 IP 连接，或使用 Mirrored 网络模式（`.wslconfig` 配置 `networkingMode=mirrored`） |
