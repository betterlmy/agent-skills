#!/usr/bin/env bash
set -euo pipefail

page_timeout_ms="${PLAYWRIGHT_CLI_CDP_PAGE_TIMEOUT_MS:-${PLAYWRIGHT_MCP_TIMEOUT_NAVIGATION:-15000}}"

case "$page_timeout_ms" in
  ''|*[!0-9]*) page_timeout_ms=15000 ;;
esac
if (( page_timeout_ms < 1 )); then
  page_timeout_ms=15000
fi

export PLAYWRIGHT_MCP_TIMEOUT_NAVIGATION="$page_timeout_ms"

# Redirect playwright-cli output (console logs, page snapshots) to a dedicated
# temp directory so the working directory stays clean. A fixed subdirectory lets
# the built-in outputMaxSize budget reclaim old files across runs; the budget
# never deletes files written by the current command. Both vars stay overridable.
: "${PLAYWRIGHT_MCP_OUTPUT_DIR:=${TMPDIR:-/tmp}/playwright-cli-cdp}"
: "${PLAYWRIGHT_MCP_OUTPUT_MAX_SIZE:=52428800}"  # 50 MiB
export PLAYWRIGHT_MCP_OUTPUT_DIR PLAYWRIGHT_MCP_OUTPUT_MAX_SIZE
mkdir -p "$PLAYWRIGHT_MCP_OUTPUT_DIR"

if command -v playwright-cli >/dev/null 2>&1; then
  exec playwright-cli "$@"
fi

if command -v npx >/dev/null 2>&1; then
  exec npx --no-install playwright-cli "$@"
fi

echo "Error: playwright-cli was not found. Install @playwright/cli globally or in the current project." >&2
exit 127
