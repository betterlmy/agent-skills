# agent-skills

[![skills.sh](https://skills.sh/b/betterlmy/agent-skills)](https://skills.sh/betterlmy/agent-skills)

[中文文档](README.zh-CN.md)

Agent skills maintained by `betterlmy`.

## Skills

| Skill | Purpose |
|---|---|
| [`playwright-cli-cdp`](skills/playwright-cli-cdp/SKILL.md) | CDP-only browser control with `playwright-cli` |
| [`skill-engineer`](skills/skill-engineer/SKILL.md) | Create, improve, review, and evaluate production-ready agent skills |

## skill-engineer

`skill-engineer` combines a concise skill-writing standard with production review and evaluation workflows. It helps agents create new skills, make existing skills production-ready, audit trigger descriptions and bundled resources, and decide when a skill needs scripts, references, assets, metadata, packaging, or forward testing.

Install only this skill:

```bash
npx skills add betterlmy/agent-skills --skill skill-engineer
```

Install globally for Codex:

```bash
npx skills add betterlmy/agent-skills --skill skill-engineer -a codex -g -y
```

## playwright-cli-cdp

`playwright-cli-cdp` is a CDP-only agent skill for controlling Chrome-family browsers through Chrome DevTools Protocol (CDP) with `playwright-cli`.

It gives coding agents a repeatable browser workflow: start or reuse a local CDP endpoint, attach with `playwright-cli attach --cdp=...`, inspect pages, interact with UI, capture browser state, and run raw CDP commands without switching to Playwright-managed browser launches.

## Why use it

- Keeps browser automation tied to a real Chrome, Chromium, or Edge debugging endpoint.
- Works well for agents that need terminal-driven page inspection, UI operation, and troubleshooting.
- Provides bundled Bash and PowerShell helpers for environment checks, Chrome remote-debug startup, and CDP command execution.
- Includes focused reference guides for storage, network mocking, tracing, video recording, code generation, and raw CDP recipes.

## Install

Install only this skill:

```bash
npx skills add betterlmy/agent-skills --skill playwright-cli-cdp
```

Install globally for Codex:

```bash
npx skills add betterlmy/agent-skills --skill playwright-cli-cdp -a codex -g -y
```

Install globally for Claude Code:

```bash
npx skills add betterlmy/agent-skills --skill playwright-cli-cdp -a claude-code -g -y
```

## Quick start

After installation, start a new agent session and ask the agent to use this skill:

```text
Use playwright-cli-cdp to open https://example.com through CDP and inspect the page title.
```

The skill's default flow is:

```bash
cd skills/playwright-cli-cdp
bash scripts/check-environment.sh
bash scripts/open-chrome-remote.sh https://example.com
bash scripts/playwright-cdp.sh -s=cdp attach --cdp=http://127.0.0.1:9222
bash scripts/playwright-cdp.sh -s=cdp snapshot
```

For Windows PowerShell and WSL2 details, see [`skills/playwright-cli-cdp/SKILL.md`](skills/playwright-cli-cdp/SKILL.md).

## Capabilities

| Area | What is included |
|---|---|
| Page operation | Navigation, click, double-click, type, fill, hover, drag-and-drop, file upload, checkbox, select, screenshots, PDF export |
| Browser input | Keyboard events, mouse movement, mouse buttons, wheel scrolling |
| Inspection | Accessibility snapshots, DOM snapshots, element attributes, computed styles, console logs, network activity |
| State | Cookies, localStorage, sessionStorage, IndexedDB, storage-state save and restore |
| Debugging | Dialog handling, request routing, network mocking, tracing, video recording |
| Automation output | Playwright locator generation and TypeScript test code generation |
| CDP access | Raw Chrome DevTools Protocol commands through `run-code` |

## Guardrails

- This skill is CDP-only. It intentionally avoids `playwright-cli open`, Playwright-managed browser launches, Firefox/WebKit launches, extension attach, and Playwright test debug attach workflows.
- It keeps CDP local by default and does not bind the debugging endpoint to `0.0.0.0` unless explicitly requested.
- It does not close, kill, restart, or detach an existing CDP browser session unless the user asks for cleanup.
- CDP can expose cookies, storage, page content, and network traffic. Review third-party skills before installing or running them.

## Requirements

- Git, for downloading and updating the skill.
- `playwright-cli`, installed in the environment where the agent runs browser commands.
- A Chrome-family browser: Chrome, Chromium, or Microsoft Edge.
- Shell access for the agent, because this skill uses bundled scripts.

## Repository layout

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

`SKILL.md` contains the agent-facing workflow. `scripts/` contains executable helpers. `references/` contains detailed guides that the agent loads only when needed.

## Reference guides

| File | Contents |
|---|---|
| [`cdp-startup.md`](skills/playwright-cli-cdp/references/cdp-startup.md) | CDP startup, cross-platform Chrome launch, port conflict troubleshooting |
| [`cdp-recipes.md`](skills/playwright-cli-cdp/references/cdp-recipes.md) | Raw CDP protocol commands: Runtime, Network, Performance, Emulation, Security, Coverage |
| [`element-attributes.md`](skills/playwright-cli-cdp/references/element-attributes.md) | Inspecting `id`, `class`, `data-*`, and computed style via `eval` |
| [`request-mocking.md`](skills/playwright-cli-cdp/references/request-mocking.md) | Route commands and advanced mocking patterns with `run-code` |
| [`running-code.md`](skills/playwright-cli-cdp/references/running-code.md) | Geolocation, permissions, media emulation, frames, file download, clipboard, and more |
| [`storage-state.md`](skills/playwright-cli-cdp/references/storage-state.md) | Cookie, localStorage, sessionStorage, IndexedDB, and state save/load reference |
| [`test-generation.md`](skills/playwright-cli-cdp/references/test-generation.md) | Collecting generated Playwright code, adding assertions, `toMatchAriaSnapshot` patterns |
| [`tracing.md`](skills/playwright-cli-cdp/references/tracing.md) | Trace output format, use cases, comparison with video and screenshot |
| [`video-recording.md`](skills/playwright-cli-cdp/references/video-recording.md) | Basic recording, scripted demos, and the Overlay API |

## Related links

- [Skills directory](https://www.skills.sh/)
- [Skills CLI](https://github.com/vercel-labs/skills)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [Claude Code Agent SDK Skills](https://code.claude.com/docs/en/agent-sdk/skills)
