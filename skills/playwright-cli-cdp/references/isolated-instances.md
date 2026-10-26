# 独立 CDP 实例

## 分配与复用契约

默认每个任务首次调用启动器时生成 `agent-<UUID>`，新建 Profile，启动 Chrome `--remote-debugging-port=0`。系统分配端口后，启动器读取该 Profile 的 `DevToolsActivePort`，检查端口、浏览器路径及 `/json/version` 的 WebSocket 身份，成功才输出单个 JSON 对象：

```json
{"session":"agent-<UUID>","endpoint":"http://127.0.0.1:<assigned-port>","profile":"<absolute-profile-path>"}
```

- 保存返回信息到本任务记录；后续复用同一个实例，不再次启动。不同任务不能使用相同 session。
- 不扫描“空闲端口”，不复用默认 9222，不复用旧 Profile，不复制用户认证数据。
- 用户明确给出端点时，直接 attach，另生成唯一 session；这是共享连接，不保证 Profile 隔离。
- `session` 是 CLI 状态命名，不是 CDP 协议的 sessionId；端口、Profile、CLI session 三者都要独立。
- 所有显式会话名使用 `-s=<name>` / `--session=<name>`；wrapper 据此隔离日志与预算。显式输出目录由调用方负责隔离。
- 启动或挂载失败：停止对应流程，报告已创建的资源。不抢占其他实例、不自动重试创建大量浏览器。

## 平台与参数

Bash 启动器在 WSL 中自动调用同包 PowerShell 脚本，使用 Windows Chrome。原生 Linux/macOS 使用本机浏览器，需要 Python 3 生成 JSON、UUID 和验证端点。Windows 启动器兼容 Windows PowerShell 5.1。

| 含义 | Bash 环境变量 | PowerShell 参数 |
| --- | --- | --- |
| 初始页面 | 第一个位置参数 | `-StartUrl` |
| 会话名 | `CDP_SESSION` | `-Session` |
| 端口，默认 0 | `CDP_PORT` | `-Port` |
| 新 Profile 路径 | `CDP_USER_DATA_DIR` | `-UserDataDir` |
| 浏览器可执行文件 | `CHROME_BIN` | `-ChromeBin` |
| 启动等待秒数，默认 15 | `CDP_TIMEOUT_SECONDS` | `-TimeoutSeconds` |

Profile 默认父目录：Windows `%LOCALAPPDATA%\playwright-cli-cdp\profiles`；Linux/macOS `$HOME/.cache/playwright-cli-cdp/profiles`。WSL 传入自定义 Profile/Chrome 路径时必须使用 Windows 路径。指定 Profile 必须尚不存在，即使旧实例已停止也不隐式复用。

固定端口只用于用户明确指定的用途。启动器先检查是否被占用，但检查和实际绑定间存在竞争窗口；并发分配必须使用 0。启动器只允许 `127.0.0.1`，不开放公网接口。已有远程端点只能通过显式 attach 使用。

## WSL 网络边界

Windows 启动成功不代表 WSL 可访问。启动后在 WSL 对返回的 endpoint 执行健康检查；失败就报告宿主可达性问题，不回退到其他任务的 9222、不重启浏览器、不自动改变监听地址、防火墙或系统网络配置。Windows loopback 可达性依赖既有网络设置，不能把宿主虚拟网卡 IP 当作 loopback 的等价替代。

## 生命周期与验证

任务完成保留 Chrome、CDP 和 CLI 连接，直到用户明确要求关闭或分离。Profile 不自动删除；超时也不擅自终止启动中的进程。独立 Profile 需要分别登录，不能承诺同一账号的后端数据独立。

本包回归检查（从 Skill 根目录执行）：

```bash
python3 -m unittest discover -s tests -v
bash -n scripts/open-chrome-remote.sh scripts/playwright-cdp.sh
# Windows PowerShell：
# powershell -NoProfile -ExecutionPolicy Bypass -File tests/test-launcher.ps1
```

真实 Windows Chrome 前向测试（先将两次并发启动返回的 JSON 保存为 a.json / b.json）：

```bash
python3 tests/forward-isolation.py a.json b.json
# 仅当接受焦点模拟且不验收真实桌面焦点时：
python3 tests/forward-isolation.py a.json b.json --simulate-focus
```

该测试会操作这两个专用测试实例，写入合成 Cookie/localStorage；不得传入用户日常浏览器。测试不关闭实例；临时 HTTP 服务退出后页面不可继续刷新。

真实前向测试应同时启动两个实例，断言端口、Profile、session 均不同，再分别通过 wrapper attach。使用本地临时测试页面验证并发导航与表单操作互不覆盖、同源 localStorage/Cookie 不共享、输出目录不同；最后检查测试前已有端点仍为原来的浏览器。不要用真实业务数据或认证 Cookie 做隔离测试。测试产生的浏览器也遵守保留规则。
