# agent-skills

[![skills.sh](https://skills.sh/b/betterlmy/agent-skills)](https://skills.sh/betterlmy/agent-skills)

[English README](README.md)

`betterlmy` 维护的 agent skills 仓库。

## 可用 Skills

| Skill | 用途 | 安装 |
|---|---|---|
| [`skill-engineer`](skills/skill-engineer/SKILL.md) | 创建、改进、review 和评估生产可用的 agent skill | `npx skills add betterlmy/agent-skills --skill skill-engineer` |
| [`playwright-cli-cdp`](skills/playwright-cli-cdp/SKILL.md) | 用 `playwright-cli` 通过 CDP 控制 Chrome 系浏览器 | `npx skills add betterlmy/agent-skills --skill playwright-cli-cdp` |

全局安装到 Codex：

```bash
npx skills add betterlmy/agent-skills --skill <skill-name> -a codex -g -y
```

全局安装到 Claude Code：

```bash
npx skills add betterlmy/agent-skills --skill <skill-name> -a claude-code -g -y
```

## skill-engineer

`skill-engineer` 是一个面向生产可用性的 skill，用于创建和 review agent skills。

适合让 agent 完成：

- 创建新 skill，并设计清晰的名称、触发描述和资源结构。
- Review 已有 skill，检查生产风险、过度触发、隐藏假设和缺失验证。
- 改进草稿 skill，判断哪些内容应放在 `SKILL.md`、`references/`、`scripts/`、`assets/` 或 `agents/openai.yaml`。
- 用真实 prompt、baseline 对比和触发检查来评估关键 skill。

包含内容：

| 文件 | 内容 |
|---|---|
| [`SKILL.md`](skills/skill-engineer/SKILL.md) | 创建、review、改进和评估生产可用 skill 的主流程 |
| [`review-rubric.md`](skills/skill-engineer/references/review-rubric.md) | 已有 skill 的严重级别模型和 review checklist |
| [`eval-workflow.md`](skills/skill-engineer/references/eval-workflow.md) | 从轻量到完整的 skill 行为和触发评估流程 |
| [`audit_skill.py`](skills/skill-engineer/scripts/audit_skill.py) | 用于基础生产可用性检查的静态审查脚本 |

示例 prompt：

```text
Use skill-engineer to review this skill and tell me whether it is production-ready: /path/to/my-skill
```

## playwright-cli-cdp

`playwright-cli-cdp` 是一个只面向 CDP 的 agent skill，用 Chrome DevTools Protocol (CDP) 和 `playwright-cli` 控制 Chrome 系浏览器。

它给编码 agent 提供一套稳定的浏览器工作流：启动或复用本地 CDP 端点，通过 `playwright-cli attach --cdp=...` 挂载浏览器，检查页面、操作 UI、读取浏览器状态，并在需要时直接执行原始 CDP 命令，同时避免切换到 Playwright 托管浏览器启动模式。

适合让 agent 完成：

- 操作真实的 Chrome、Chromium 或 Edge 调试端点。
- 在终端会话里检查页面并排查 UI 状态。
- 采集浏览器 storage、console 日志、网络活动、截图、视频或 trace。
- 从真实浏览器会话生成 Playwright locator 或 TypeScript 测试代码。
- 在高层自动化能力不足时执行原始 Chrome DevTools Protocol 命令。

使用边界：

- CDP-only：避免 `playwright-cli open`、Playwright 托管浏览器启动、Firefox/WebKit 启动、extension attach 和 Playwright test debug attach 流程。
- 默认只使用本地 CDP 端点，不会把调试端口绑定到 `0.0.0.0`，除非用户明确要求。
- 不会因为任务结束就关闭、杀掉、重启或断开已有 CDP 浏览器会话；只有用户要求清理时才执行。
- CDP 可以暴露 cookie、storage、页面内容和网络流量。安装或运行第三方 skill 前应先审查内容。

快速开始：

```text
Use playwright-cli-cdp to open https://example.com through CDP and inspect the page title.
```

默认流程：

```bash
cd skills/playwright-cli-cdp
bash scripts/check-environment.sh
bash scripts/open-chrome-remote.sh https://example.com
bash scripts/playwright-cdp.sh -s=cdp attach --cdp=http://127.0.0.1:9222
bash scripts/playwright-cdp.sh -s=cdp snapshot
```

参考文档：

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
    references/
    scripts/
```

`SKILL.md` 保存 agent 侧的核心流程；`scripts/` 保存可执行辅助脚本；`references/` 保存按需读取的详细参考文档。

## 相关链接

- [Skills directory](https://www.skills.sh/)
- [Skills CLI](https://github.com/vercel-labs/skills)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [Claude Code Agent SDK Skills](https://code.claude.com/docs/en/agent-sdk/skills)
