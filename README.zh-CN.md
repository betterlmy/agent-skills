# agent-skills

[![skills.sh](https://skills.sh/b/betterlmy/agent-skills)](https://skills.sh/betterlmy/agent-skills)

[English README](README.md)

`betterlmy` 维护的 agent skills 仓库。

## Skills

| Skill | 用途 |
|---|---|
| [`playwright-cli-cdp`](skills/playwright-cli-cdp/SKILL.md) | 用 `playwright-cli` 通过 CDP 控制浏览器 |
| [`skill-engineer`](skills/skill-engineer/SKILL.md) | 创建、改进、review 和评估生产可用的 agent skill |

## skill-engineer

`skill-engineer` 把简洁的 skill 写作标准、生产级 review 和评估流程结合在一起。它帮助 agent 创建新 skill、把已有 skill 改到生产可用、审查触发描述和 bundled resources，并判断一个 skill 是否需要 scripts、references、assets、metadata、打包或前向测试。

只安装这个 skill：

```bash
npx skills add betterlmy/agent-skills --skill skill-engineer
```

全局安装到 Codex：

```bash
npx skills add betterlmy/agent-skills --skill skill-engineer -a codex -g -y
```

## playwright-cli-cdp

`playwright-cli-cdp` 是一个只面向 CDP 的 agent skill，用 Chrome DevTools Protocol (CDP) 和 `playwright-cli` 控制 Chrome 系浏览器。

它给编码 agent 提供一套稳定的浏览器工作流：启动或复用本地 CDP 端点，通过 `playwright-cli attach --cdp=...` 挂载浏览器，检查页面、操作 UI、读取浏览器状态，并在需要时直接执行原始 CDP 命令，同时避免切换到 Playwright 托管浏览器启动模式。

## 适合场景

- 需要 agent 通过真实的 Chrome、Chromium 或 Edge 调试端点操作页面。
- 需要在终端环境里完成页面检查、UI 操作、问题排查和状态采集。
- 需要开箱即用的 Bash 和 PowerShell 辅助脚本，用于环境检查、Chrome remote-debug 启动和 CDP 命令执行。
- 需要按需参考 storage、网络 mock、tracing、视频录制、代码生成和原始 CDP 示例。

## 安装

只安装这个 skill：

```bash
npx skills add betterlmy/agent-skills --skill playwright-cli-cdp
```

全局安装到 Codex：

```bash
npx skills add betterlmy/agent-skills --skill playwright-cli-cdp -a codex -g -y
```

全局安装到 Claude Code：

```bash
npx skills add betterlmy/agent-skills --skill playwright-cli-cdp -a claude-code -g -y
```

## 快速开始

安装后重新开启一个 agent 会话，然后让 agent 使用这个 skill：

```text
Use playwright-cli-cdp to open https://example.com through CDP and inspect the page title.
```

这个 skill 的默认流程是：

```bash
cd skills/playwright-cli-cdp
bash scripts/check-environment.sh
bash scripts/open-chrome-remote.sh https://example.com
bash scripts/playwright-cdp.sh -s=cdp attach --cdp=http://127.0.0.1:9222
bash scripts/playwright-cdp.sh -s=cdp snapshot
```

Windows PowerShell 和 WSL2 的细节见 [`skills/playwright-cli-cdp/SKILL.md`](skills/playwright-cli-cdp/SKILL.md)。

## 功能概览

| 范围 | 能力 |
|---|---|
| 页面操作 | 导航、点击、双击、输入、填表、hover、拖拽、文件上传、复选框、下拉选择、截图、PDF 导出 |
| 浏览器输入 | 键盘事件、鼠标移动、鼠标按键、滚轮 |
| 页面检查 | Accessibility snapshot、DOM snapshot、元素属性、computed style、console 日志、网络活动 |
| 状态管理 | Cookie、localStorage、sessionStorage、IndexedDB、storage state 保存和恢复 |
| 调试排查 | 弹窗处理、请求路由、网络 mock、tracing、视频录制 |
| 自动化产物 | Playwright locator 生成、TypeScript 测试代码生成 |
| CDP 能力 | 通过 `run-code` 执行原始 Chrome DevTools Protocol 命令 |

## 使用边界

- 这是一个 CDP-only skill，设计上避免使用 `playwright-cli open`、Playwright 托管浏览器启动、Firefox/WebKit 启动、extension attach 和 Playwright test debug attach 流程。
- 默认只使用本地 CDP 端点，不会把调试端口绑定到 `0.0.0.0`，除非用户明确要求并接受风险。
- 不会因为任务结束就关闭、杀掉、重启或断开已有 CDP 浏览器会话；只有用户要求清理时才执行清理动作。
- CDP 可以暴露 cookie、storage、页面内容和网络流量。安装或运行第三方 skill 前应先审查内容。

## 依赖要求

- Git，用于下载和更新 skill。
- `playwright-cli`，需要安装在 agent 执行浏览器命令的环境里。
- Chrome 系浏览器：Chrome、Chromium 或 Microsoft Edge。
- agent 需要具备 shell 执行能力，因为这个 skill 使用 bundled scripts。

## 仓库结构

```text
skills/
  skill-engineer/
    SKILL.md
    agents/
    references/
    scripts/
  playwright-cli-cdp/
    SKILL.md
    scripts/
    references/
```

`SKILL.md` 保存 agent 侧的核心流程；`scripts/` 保存可执行辅助脚本；`references/` 保存按需读取的详细参考文档。

## 参考文档

| 文件 | 内容 |
|---|---|
| [`cdp-startup.md`](skills/playwright-cli-cdp/references/cdp-startup.md) | CDP 启动、跨平台 Chrome 启动方式、端口冲突排查 |
| [`cdp-recipes.md`](skills/playwright-cli-cdp/references/cdp-recipes.md) | 原始 CDP 协议命令：Runtime、Network、Performance、Emulation、Security、Coverage |
| [`element-attributes.md`](skills/playwright-cli-cdp/references/element-attributes.md) | 用 `eval` 检查元素的 `id`、`class`、`data-*` 及 computed style |
| [`request-mocking.md`](skills/playwright-cli-cdp/references/request-mocking.md) | route 命令及用 `run-code` 实现高级 mock 模式 |
| [`running-code.md`](skills/playwright-cli-cdp/references/running-code.md) | 地理位置、权限、媒体模拟、frames、文件下载、剪贴板等完整示例 |
| [`storage-state.md`](skills/playwright-cli-cdp/references/storage-state.md) | Cookie、localStorage、sessionStorage、IndexedDB 及 storage state 保存/恢复参考 |
| [`test-generation.md`](skills/playwright-cli-cdp/references/test-generation.md) | 收集生成的 Playwright 代码、添加断言、`toMatchAriaSnapshot` 用法 |
| [`tracing.md`](skills/playwright-cli-cdp/references/tracing.md) | Trace 输出格式、使用场景、与视频和截图的对比 |
| [`video-recording.md`](skills/playwright-cli-cdp/references/video-recording.md) | 基础录制、脚本化演示、Overlay API 用法 |

## 相关链接

- [Skills directory](https://www.skills.sh/)
- [Skills CLI](https://github.com/vercel-labs/skills)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [Claude Code Agent SDK Skills](https://code.claude.com/docs/en/agent-sdk/skills)
