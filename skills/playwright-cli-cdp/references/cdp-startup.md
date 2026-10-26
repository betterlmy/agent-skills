# CDP 启动与故障排查

默认创建独立实例；详细契约和参数见 [独立实例](isolated-instances.md)。只有用户明确提供端点时才连接已有浏览器。任务完成不得擅自关闭、kill、重启或 detach。

## 启动

先按 SKILL.md 的快速上手解析同包脚本的绝对路径。macOS / Linux / WSL2：

```bash
bash scripts/open-chrome-remote.sh
```

WSL2 自动调用 Windows PowerShell；无需猜测 Windows 用户路径。原生 Linux/macOS 需要 Python 3 与可用 Chrome/Chromium/Edge，使用 `CHROME_BIN` 可指定可执行文件。

Windows PowerShell：

```powershell
& .\scripts\open-chrome-remote.ps1
```

默认端口为 0；返回 JSON 包含 `session`、实际 `endpoint` 和独立 `profile`。保存它们用于后续挂载和复用；不要从其他任务获取端口。

## 环境检查与挂载

```bash
CDP_ENDPOINT="$endpoint" bash scripts/check-environment.sh
bash scripts/playwright-cdp.sh -s="$session" attach --cdp="$endpoint"
```

环境检查不启动浏览器；未传端点时只探测旧固定地址 9222，结果不是创建独立实例的必要条件。WSL 没有 Linux Chrome 时，应在 Windows 启动成功后传入实际端点检查。

## 排障

| 现象 | 动作 |
| --- | --- |
| 已存在 Profile | 使用新 session/Profile；不要删除、复用或杀死原实例 |
| 动态端口启动超时 | 检查报错中的 Profile、DevToolsActivePort 和浏览器状态；保留资源并报告 |
| 固定端口占用 | 不接管；通常改回动态端口 0 |
| Windows 成功、WSL 健康检查失败 | 报告 loopback 网络可达性；不自动修改防火墙、监听地址或 WSL 配置 |
| 会话已存在 | 核查是否本任务原实例；是则复用，否则使用唯一会话名 |
| 页面导航超时 | 检查当前页面与网络，不能重启端点掩盖失败 |

Windows 启动参数保留本地既有的 `--ignore-certificate-errors` 行为；独立 Profile 不因此构成证书安全边界，不应用于敏感生产浏览。
