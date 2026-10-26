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

# Separate artifacts and their cleanup budgets for explicitly named sessions.
session=default
for arg in "$@"; do
  case "$arg" in -s=*|--session=*) session="${arg#*=}" ;; esac
done
if [[ ! "$session" =~ ^[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}$ ]]; then
  echo 'Invalid session name; use 1-80 ASCII letters, digits, underscores or hyphens.' >&2
  exit 2
fi
: "${PLAYWRIGHT_MCP_OUTPUT_DIR:=${TMPDIR:-/tmp}/playwright-cli-cdp/$session}"
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
