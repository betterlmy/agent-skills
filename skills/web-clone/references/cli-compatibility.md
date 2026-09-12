# CLI 兼容性

<!-- cli-compatibility-contract:v1 -->

| 字段 | 值 |
| --- | --- |
| 工具 | Node.js 运行时、系统 Chrome/Edge/Chromium（CDP）；GitHub CLI（`gh`）为按需 |
| 分发标识 | `node`（系统安装）、`msedge.exe` / `chrome.exe` / `chromium`（系统浏览器）、`gh`（GitHub CLI） |
| 本机验证版本 | Node.js `v24.21.0`（Windows 10/11，`C:\Program Files\nodejs\node.exe`）；系统 Chrome 已跑通内嵌 CDP 控制层的最小验证（启动 → 导航 → 求值 → 截图 → 关闭）；`gh`、`jq`、`wget` 均**未安装**；各 `scripts/*.mjs` 的实际抓站流程**未**验证 |
| 验证日期 | `2026-09-12` |
| 版本策略 | 记录已探测版本，以能力探测决定其他版本能否继续 |

本契约只记录上表日期在本机实际探测到的状态，不代表跨版本测试结论；不要仅凭版本号推断兼容。

## 关键能力

1. **Node.js**：`node --version` 可读取。脚本均为零第三方依赖的 `.mjs`，仅需能运行 ES module；不支持 Node 14 以下。
2. **系统浏览器**：预检脚本（如 `recon-site.mjs` 开头的预检输出）应报告至少一个可用的 Chrome、Edge 或 Chromium；也可用环境变量 `WEB_CLONE_BROWSER_PATH` 显式指定可执行文件。本机已用该控制层跑通最小链路（启动/导航/`evaluate`/截图/关闭），但未跑过任何 `scripts/*.mjs` 抓站流程。
3. **GitHub CLI**：`gh --version` 与 `gh api --help` 可用，且需支持 `--jq`（Step 1 与许可校验用它代替外部 `jq`）。`gh` 未认证或参数不兼容时降级（见下）。

## 按需 CLI（未安装不影响主流程）

上表日期在本机的探测结果：`git`、`curl`、`unzip` 在 Git Bash 中可用；`zip` 在 Git Bash 外用需自备 PATH；`gh`、`jq`、`wget` **均未安装**。

- `gh`：Step 1 源码检索与许可核查用。缺失时降级为 GitHub 网页搜索，或 `curl https://api.github.com/search/repositories?q=<关键词>`（匿名限流更严，需声明新鲜度边界）。
- `jq`：**不是必需依赖**。文中命令已改用 `gh api --jq`；若需要处理其他 JSON，用 `node -e` 解析（`node` 是硬依赖，始终可用）。
- `wget`：仅 Step 3 的“静态 HTML 镜像”路径用。缺失时改用 `scripts/mirror-site.mjs` 或 `curl` 逐页抓取。

## 版本不一致时

- **Node 版本不同**：先跑一次轻量脚本验证 ES module 语法可用；脚本失败时报告实际版本，不要自动升级用户环境。
- **浏览器缺失**：直接说明缺少系统浏览器，或让用户通过 `WEB_CLONE_BROWSER_PATH` 指定路径；**禁止**在项目内执行 `npm install playwright` 或下载 Chromium。
- **`gh` 缺失或未认证**：退回 GitHub 网页搜索，或改用 `curl https://api.github.com/search/repositories?q=<关键词>`（匿名限流更严格，需声明结果新鲜度边界）。
- **沙箱阻止浏览器子进程**：脚本自带的 CDP 控制层会自行拉起系统浏览器子进程；被沙箱阻止时如实报告失败并停止重试，不要改用安装 Playwright 或下载 Chromium 绕过。若机器上已存在可解析的 `playwright` / `playwright-core` 包，脚本会复用该运行时，但它不是前置条件。

## 安装（仅在用户明确授权时）

```text
# GitHub CLI
winget install GitHub.cli
```

升级或安装必须获得用户同意。
