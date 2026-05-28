# agent-skills

[![skills.sh](https://skills.sh/b/betterlmy/agent-skills)](https://skills.sh/betterlmy/agent-skills)

[中文文档](README.zh-CN.md)

Agent skills maintained by `betterlmy`.

## Available Skills

| Skill | Purpose | Install |
|---|---|---|
| [`skill-engineer`](skills/skill-engineer/SKILL.md) | Create, improve, review, and evaluate production-ready agent skills | `npx skills add betterlmy/agent-skills --skill skill-engineer` |
| [`playwright-cli-cdp`](skills/playwright-cli-cdp/SKILL.md) | Control Chrome-family browsers through CDP with `playwright-cli` | `npx skills add betterlmy/agent-skills --skill playwright-cli-cdp` |

Install a skill globally for Codex:

```bash
npx skills add betterlmy/agent-skills --skill <skill-name> -a codex -g -y
```

Install a skill globally for Claude Code:

```bash
npx skills add betterlmy/agent-skills --skill <skill-name> -a claude-code -g -y
```

## skill-engineer

`skill-engineer` is a production-oriented skill for creating and reviewing agent skills.

Use it when you want an agent to:

- Create a new skill with a clear name, trigger description, and resource layout.
- Review an existing skill for production risks, over-triggering, hidden assumptions, and missing validation.
- Improve a draft skill by deciding what belongs in `SKILL.md`, `references/`, `scripts/`, `assets/`, or `agents/openai.yaml`.
- Evaluate an important skill with realistic prompts, baseline comparison, and trigger checks.

What it includes:

| File | Contents |
|---|---|
| [`SKILL.md`](skills/skill-engineer/SKILL.md) | Main workflow for creating, reviewing, improving, and evaluating production-ready skills |
| [`review-rubric.md`](skills/skill-engineer/references/review-rubric.md) | Severity model and review checklist for existing skills |
| [`eval-workflow.md`](skills/skill-engineer/references/eval-workflow.md) | Lightweight-to-full evaluation workflow for skill behavior and triggering |
| [`audit_skill.py`](skills/skill-engineer/scripts/audit_skill.py) | Static audit script for basic production-readiness checks |

Example prompt:

```text
Use skill-engineer to review this skill and tell me whether it is production-ready: /path/to/my-skill
```

## playwright-cli-cdp

`playwright-cli-cdp` is a CDP-only agent skill for controlling Chrome-family browsers through Chrome DevTools Protocol (CDP) with `playwright-cli`.

It gives coding agents a repeatable browser workflow: start or reuse a local CDP endpoint, attach with `playwright-cli attach --cdp=...`, inspect pages, interact with UI, capture browser state, and run raw CDP commands without switching to Playwright-managed browser launches.

Use it when you want an agent to:

- Operate a real Chrome, Chromium, or Edge debugging endpoint.
- Inspect pages and troubleshoot UI state from a terminal session.
- Capture browser storage, console logs, network activity, screenshots, video, or traces.
- Generate Playwright locators or TypeScript test code from a real browser session.
- Execute raw Chrome DevTools Protocol commands when high-level automation is not enough.

Guardrails:

- CDP-only: avoids `playwright-cli open`, Playwright-managed browser launches, Firefox/WebKit launches, extension attach, and Playwright test debug attach workflows.
- Keeps CDP local by default and does not bind the debugging endpoint to `0.0.0.0` unless explicitly requested.
- Does not close, kill, restart, or detach an existing CDP browser session unless the user asks for cleanup.
- CDP can expose cookies, storage, page content, and network traffic. Review third-party skills before installing or running them.

Quick start:

```text
Use playwright-cli-cdp to open https://example.com through CDP and inspect the page title.
```

Default flow:

```bash
cd skills/playwright-cli-cdp
bash scripts/check-environment.sh
bash scripts/open-chrome-remote.sh https://example.com
bash scripts/playwright-cdp.sh -s=cdp attach --cdp=http://127.0.0.1:9222
bash scripts/playwright-cdp.sh -s=cdp snapshot
```

Reference guides:

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

## Repository Layout

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

`SKILL.md` contains the agent-facing workflow. `scripts/` contains executable helpers. `references/` contains detailed guides that the agent loads only when needed.

## Related Links

- [Skills directory](https://www.skills.sh/)
- [Skills CLI](https://github.com/vercel-labs/skills)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [Claude Code Agent SDK Skills](https://code.claude.com/docs/en/agent-sdk/skills)
