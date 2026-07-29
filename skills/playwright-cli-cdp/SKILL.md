---
name: playwright-cli-cdp
description: CDP-only browser control with playwright-cli. Use for launching Chrome in remote debugging mode, attaching exclusively through --cdp endpoints, driving attached pages, inspecting console/network/storage, and sending raw Chrome DevTools Protocol commands. Do not use playwright-cli open, non-CDP browser launches, extension attach, or Playwright test debug attach workflows from this skill.
allowed-tools: Bash(playwright-cli:*) Bash(npx:*) Bash(npm:*) Bash(bash:*) Bash(curl:*) Bash(lsof:*) Bash(pgrep:*) Bash(mkdir:*) Bash(pwsh:*) Bash(powershell:*) Bash(powershell.exe:*)
---

# playwright-cli CDP

## Default behavior

This skill is CDP-only. All browser work must happen through a Chrome DevTools Protocol endpoint and `playwright-cli attach --cdp=...`.

Do not use `playwright-cli open`, `--browser=...`, Firefox/WebKit launches, extension attach, or Playwright test debug attach workflows in this skill. If a CDP endpoint is already reachable, reuse it as-is. If no CDP endpoint exists, start Chrome remote debugging on `127.0.0.1:9222`, attach `playwright-cli` to that endpoint, and use the session name `cdp`.

Keep CDP local. Do not bind the debugging endpoint to `0.0.0.0` or a public interface unless the user explicitly requests it and accepts the security risk.

Never close, kill, restart, detach, or otherwise clean up an existing CDP endpoint or browser just because the task is done. Leave Chrome and the debugging port running unless the user explicitly asks to close it. If the user asks to clean up, prefer `bash scripts/playwright-cdp.sh -s=<session> detach` first; only terminate browser processes when the user explicitly asks to close/kill Chrome.

Use a 15 second page/navigation timeout by default. Run `playwright-cli` through the bundled wrapper so every command inherits `PLAYWRIGHT_MCP_TIMEOUT_NAVIGATION=15000` for URL opens, `goto`, tab navigation, reloads, and other navigation waits:

- Bash/macOS/Linux/WSL2: `bash scripts/playwright-cdp.sh ...`
- Windows PowerShell: `powershell -ExecutionPolicy Bypass -File scripts\playwright-cdp.ps1 ...`

Override the page/navigation timeout only when needed with `PLAYWRIGHT_CLI_CDP_PAGE_TIMEOUT_MS=<milliseconds>`. If navigation times out, report the timeout and inspect the current page state through the existing CDP session; do not close or restart the endpoint unless the user asks.

The wrapper redirects playwright-cli output (console logs `console-*.log`, page snapshots `page-*.yml`) to a dedicated temp directory (`$TMPDIR/playwright-cli-cdp` on macOS/Linux/WSL2, `%TEMP%\playwright-cli-cdp` on Windows) so the working directory stays clean. playwright-cli always writes snapshot/console output to files in skill mode and only returns a link, so `read` that linked path when the page snapshot content is needed. A built-in size budget (`PLAYWRIGHT_MCP_OUTPUT_MAX_SIZE`, default 50 MiB) automatically reclaims the oldest files across runs; files written by the current command are never deleted. Override either with `PLAYWRIGHT_MCP_OUTPUT_DIR` or `PLAYWRIGHT_MCP_OUTPUT_MAX_SIZE`.

## Quick start

Resolve bundled scripts relative to this skill directory before running them.

macOS, Linux, or WSL2 with a Linux browser:

```bash
bash scripts/check-environment.sh
bash scripts/open-chrome-remote.sh
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\check-environment.ps1
powershell -ExecutionPolicy Bypass -File scripts\open-chrome-remote.ps1
```

WSL2 with Windows Chrome:

```bash
win_script="$(wslpath -w scripts/open-chrome-remote.ps1)"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$win_script"
```

When the PowerShell script is stored in the WSL filesystem, do not guess a `C:\Users\...` path. Prefer `wslpath -w`; if you must pass a literal `\\wsl.localhost\...` path, wrap the PowerShell command in Bash single quotes so Bash does not consume the UNC backslashes.

Attach and drive the CDP session:

```bash
bash scripts/playwright-cdp.sh -s=cdp attach --cdp=http://127.0.0.1:9222
bash scripts/playwright-cdp.sh -s=cdp goto https://example.com
bash scripts/playwright-cdp.sh -s=cdp snapshot
bash scripts/playwright-cdp.sh -s=cdp click e15
bash scripts/playwright-cdp.sh -s=cdp eval "document.title"
```

Windows PowerShell equivalent:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\playwright-cdp.ps1 -s=cdp attach --cdp=http://127.0.0.1:9222
powershell -ExecutionPolicy Bypass -File scripts\playwright-cdp.ps1 -s=cdp goto https://example.com
powershell -ExecutionPolicy Bypass -File scripts\playwright-cdp.ps1 -s=cdp snapshot
```

Start at a URL when useful:

macOS, Linux, or WSL2 with a Linux browser:

```bash
bash scripts/check-environment.sh
bash scripts/open-chrome-remote.sh https://example.com
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\check-environment.ps1
powershell -ExecutionPolicy Bypass -File scripts\open-chrome-remote.ps1 https://example.com
```

WSL2 with Windows Chrome:

```bash
win_script="$(wslpath -w scripts/open-chrome-remote.ps1)"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$win_script" https://example.com
```

Then attach:

```bash
bash scripts/playwright-cdp.sh -s=cdp attach --cdp=http://127.0.0.1:9222
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts\playwright-cdp.ps1 -s=cdp attach --cdp=http://127.0.0.1:9222
```

If the user gives an endpoint, use it directly and do not launch another browser:

```bash
bash scripts/playwright-cdp.sh -s=cdp attach --cdp=http://127.0.0.1:9223
bash scripts/playwright-cdp.sh -s=prod attach --cdp=https://debug.example.internal
```

## Endpoint checks

Run the environment check before starting or attaching unless the task is already in a known-good active CDP session:

```bash
bash scripts/check-environment.sh
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts\check-environment.ps1
```

Before attaching, verify the endpoint when possible:

```bash
curl -fsS http://127.0.0.1:9222/json/version
curl -fsS http://127.0.0.1:9222/json/list
```

If the endpoint is down, start Chrome remote mode with the bundled Bash or PowerShell script for the current platform. If the port is already used by a non-CDP process, inspect it and choose another port via `CDP_PORT`.

macOS, Linux, or WSL2 with a Linux browser:

```bash
lsof -iTCP:9222 -sTCP:LISTEN
CDP_PORT=9333 bash scripts/open-chrome-remote.sh
```

Windows PowerShell:

```powershell
netstat -ano | findstr :9222
$env:CDP_PORT = "9333"
powershell -ExecutionPolicy Bypass -File scripts\open-chrome-remote.ps1
```

Then attach:

```bash
bash scripts/playwright-cdp.sh -s=cdp attach --cdp=http://127.0.0.1:9333
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts\playwright-cdp.ps1 -s=cdp attach --cdp=http://127.0.0.1:9333
```

## Core commands after attach

Use snapshot refs for normal page interaction.

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

Use selectors or Playwright locators when refs are not stable:

```bash
bash scripts/playwright-cdp.sh -s=cdp click "#main > button.submit"
bash scripts/playwright-cdp.sh -s=cdp click "getByRole('button', { name: 'Submit' })"
bash scripts/playwright-cdp.sh -s=cdp click "getByTestId('submit-button')"
```

## Tabs and navigation

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

## Console, network, and storage

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

Use `--raw` for machine-readable pipelines:

```bash
bash scripts/playwright-cdp.sh -s=cdp --raw eval "document.title"
bash scripts/playwright-cdp.sh -s=cdp --raw snapshot > page.yml
bash scripts/playwright-cdp.sh -s=cdp --raw cookie-get session_id
TOKEN=$(bash scripts/playwright-cdp.sh -s=cdp --raw cookie-get session_id)
```

Use `--json` for structured JSON output:

```bash
bash scripts/playwright-cdp.sh -s=cdp list --json
```

## Keyboard and mouse

```bash
bash scripts/playwright-cdp.sh -s=cdp keydown Shift
bash scripts/playwright-cdp.sh -s=cdp keyup Shift
bash scripts/playwright-cdp.sh -s=cdp mousemove 150 300
bash scripts/playwright-cdp.sh -s=cdp mousedown
bash scripts/playwright-cdp.sh -s=cdp mousedown right
bash scripts/playwright-cdp.sh -s=cdp mouseup
bash scripts/playwright-cdp.sh -s=cdp mousewheel 0 100
```

## Dialog handling

```bash
bash scripts/playwright-cdp.sh -s=cdp dialog-accept
bash scripts/playwright-cdp.sh -s=cdp dialog-accept "confirmation text"
bash scripts/playwright-cdp.sh -s=cdp dialog-dismiss
```

## Request routing

```bash
bash scripts/playwright-cdp.sh -s=cdp route "**/*.jpg" --status=404
bash scripts/playwright-cdp.sh -s=cdp route "**/api/users" --body='[{"id":1}]' --content-type=application/json
bash scripts/playwright-cdp.sh -s=cdp route-list
bash scripts/playwright-cdp.sh -s=cdp unroute "**/*.jpg"
bash scripts/playwright-cdp.sh -s=cdp unroute
```

See [references/request-mocking.md](references/request-mocking.md) for advanced mocking with `run-code`.

## Tracing and video

```bash
bash scripts/playwright-cdp.sh -s=cdp tracing-start
bash scripts/playwright-cdp.sh -s=cdp tracing-stop

bash scripts/playwright-cdp.sh -s=cdp video-start recording.webm
bash scripts/playwright-cdp.sh -s=cdp video-chapter "Chapter Title" --description="Details" --duration=2000
bash scripts/playwright-cdp.sh -s=cdp video-stop
```

See [references/tracing.md](references/tracing.md) and [references/video-recording.md](references/video-recording.md) for detail.

## Debug tools

```bash
bash scripts/playwright-cdp.sh -s=cdp highlight e5
bash scripts/playwright-cdp.sh -s=cdp highlight e5 --style="outline: 3px dashed red"
bash scripts/playwright-cdp.sh -s=cdp highlight e5 --hide
bash scripts/playwright-cdp.sh -s=cdp highlight --hide
bash scripts/playwright-cdp.sh -s=cdp generate-locator e5 --raw
bash scripts/playwright-cdp.sh -s=cdp show --annotate
```

## Raw CDP commands

Use `run-code` when the task requires a Chrome DevTools Protocol domain or command that the CLI does not expose directly. Create a CDP session from the active page, enable the needed domain, send commands, and return serializable data.

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

CDP command and parameter names are case-sensitive. Use protocol commands for browser internals, performance metrics, emulation, coverage, security state, and low-level network diagnostics. After the session is attached through `--cdp`, use `playwright-cli` page commands for interaction.

## Session lifecycle

For CDP-attached browsers, leave the external Chrome and CDP port running after the requested task. Do not run `detach`, `close`, `close-all`, `kill-all`, or process-kill commands as normal cleanup.

Only detach or close when the user explicitly asks. If cleanup is requested, prefer `bash scripts/playwright-cdp.sh -s=<session> detach` because it leaves the browser and CDP endpoint running.

When multiple CDP endpoints are in use, name sessions by endpoint or purpose:

```bash
bash scripts/playwright-cdp.sh -s=local attach --cdp=http://127.0.0.1:9222
bash scripts/playwright-cdp.sh -s=staging attach --cdp=http://127.0.0.1:9333
```

## Installation fallback

If the global command is unavailable, try a local version first:

```bash
npx --no-install playwright-cli --version
bash scripts/playwright-cdp.sh -s=cdp attach --cdp=http://127.0.0.1:9222
```

The wrapper automatically falls back to `npx --no-install playwright-cli` when a global `playwright-cli` binary is unavailable.

If no local version exists, install the CLI:

```bash
npm install -g @playwright/cli@latest
```

## References

- CDP startup and troubleshooting: [references/cdp-startup.md](references/cdp-startup.md)
- CDP protocol recipes: [references/cdp-recipes.md](references/cdp-recipes.md)
- Element attribute inspection: [references/element-attributes.md](references/element-attributes.md)
- Request mocking: [references/request-mocking.md](references/request-mocking.md)
- Custom Playwright code: [references/running-code.md](references/running-code.md)
- Storage management: [references/storage-state.md](references/storage-state.md)
- Test code generation: [references/test-generation.md](references/test-generation.md)
- Tracing: [references/tracing.md](references/tracing.md)
- Video recording: [references/video-recording.md](references/video-recording.md)
