#!/usr/bin/env bash
set -uo pipefail

HOST="${CDP_HOST:-127.0.0.1}"
PORT="${CDP_PORT:-9222}"
ENDPOINT="${CDP_ENDPOINT:-http://${HOST}:${PORT}}"
TIMEOUT_SECONDS="${CDP_TIMEOUT_SECONDS:-15}"
VERIFIED_PLAYWRIGHT_CLI_VERSION="0.1.17"

failures=0
warnings=0

case "$TIMEOUT_SECONDS" in
  ''|*[!0-9]*) TIMEOUT_SECONDS=15 ;;
esac
if (( TIMEOUT_SECONDS < 1 )); then
  TIMEOUT_SECONDS=15
fi

ok() {
  printf '[OK] %s\n' "$1"
}

warn() {
  warnings=$((warnings + 1))
  printf '[WARN] %s\n' "$1"
}

fail() {
  failures=$((failures + 1))
  printf '[FAIL] %s\n' "$1"
}

find_chrome() {
  if [[ -n "${CHROME_BIN:-}" ]]; then
    if [[ -x "$CHROME_BIN" ]]; then
      printf '%s\n' "$CHROME_BIN"
      return 0
    fi
    return 1
  fi

  local candidates=(
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary"
    "/Applications/Chromium.app/Contents/MacOS/Chromium"
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
    "google-chrome"
    "google-chrome-stable"
    "chromium"
    "chromium-browser"
    "microsoft-edge"
    "microsoft-edge-stable"
  )

  local candidate
  for candidate in "${candidates[@]}"; do
    if [[ "$candidate" == */* && -x "$candidate" ]]; then
      printf '%s\n' "$candidate"
      return 0
    fi
    if [[ "$candidate" != */* ]] && command -v "$candidate" >/dev/null 2>&1; then
      command -v "$candidate"
      return 0
    fi
  done

  return 1
}

printf 'playwright-cli-cdp environment check\n'
printf 'Endpoint: %s\n\n' "$ENDPOINT"
printf 'Timeout: %ss\n\n' "$TIMEOUT_SECONDS"

case "$(uname -s 2>/dev/null || printf unknown)" in
  Darwin) ok "platform: macOS" ;;
  Linux)
    if grep -qi microsoft /proc/version 2>/dev/null; then
      ok "platform: WSL2/Linux"
    else
      ok "platform: Linux"
    fi
    ;;
  *) warn "platform could not be identified; continue if Chrome-family CDP is reachable" ;;
esac

playwright_command=()
if command -v playwright-cli >/dev/null 2>&1; then
  playwright_command=(playwright-cli)
elif command -v npx >/dev/null 2>&1 && npx --no-install playwright-cli --version >/dev/null 2>&1; then
  playwright_command=(npx --no-install playwright-cli)
else
  fail "playwright-cli is not available; install it or provide a local package usable with npx --no-install"
fi

if [[ "${#playwright_command[@]}" -gt 0 ]]; then
  version="$("${playwright_command[@]}" --version 2>/dev/null | head -n 1 || true)"
  ok "playwright-cli is available${version:+: $version}"
  if [[ -z "$version" ]]; then
    fail "playwright-cli 未返回版本"
  elif [[ "${version#v}" != "$VERIFIED_PLAYWRIGHT_CLI_VERSION" ]]; then
    warn "playwright-cli 当前版本 $version 与本机验证版本 $VERIFIED_PLAYWRIGHT_CLI_VERSION 不同；以能力检查结果为准"
  fi

  cli_help="$("${playwright_command[@]}" --help 2>/dev/null || true)"
  for capability in attach snapshot run-code tracing-start video-start; do
    if ! grep -Eq "^[[:space:]]+${capability}([[:space:]]|$)" <<<"$cli_help"; then
      fail "playwright-cli 缺少必需能力: $capability"
    fi
  done
fi

if command -v curl >/dev/null 2>&1; then
  ok "curl is available"
else
  fail "curl is required by the Bash startup and endpoint checks"
fi

endpoint_ready=false
if command -v curl >/dev/null 2>&1 && curl -fsS --max-time "$TIMEOUT_SECONDS" "${ENDPOINT}/json/version" >/dev/null 2>&1; then
  endpoint_ready=true
  ok "CDP endpoint is reachable: ${ENDPOINT}"
else
  warn "CDP endpoint is not reachable yet: ${ENDPOINT}"
fi

chrome_path="$(find_chrome || true)"
if [[ -n "$chrome_path" ]]; then
  ok "Chrome-family browser found: ${chrome_path}"
elif [[ "$endpoint_ready" == true ]]; then
  warn "Chrome-family browser was not found locally, but an existing CDP endpoint is reachable"
else
  fail "Chrome, Chromium, or Edge was not found; set CHROME_BIN or provide an existing CDP endpoint"
fi

if [[ "$HOST" == "0.0.0.0" ]]; then
  warn "CDP_HOST=0.0.0.0 can expose browser data to the network; prefer 127.0.0.1 when possible"
fi

if [[ "$endpoint_ready" != true ]]; then
  if [[ -n "${CDP_ENDPOINT:-}" ]]; then
    warn "CDP_ENDPOINT is set; skipped local port ${PORT} conflict check"
  elif command -v lsof >/dev/null 2>&1; then
    if lsof -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
      warn "port ${PORT} is in use but does not look like a reachable CDP endpoint"
    else
      ok "port ${PORT} is available"
    fi
  else
    warn "lsof is not available; skipped port conflict check"
  fi
fi

if grep -qi microsoft /proc/version 2>/dev/null && [[ "$endpoint_ready" != true && -z "$chrome_path" ]]; then
  warn "WSL2 note: if Chrome is only installed on Windows, run: win_script=\"\$(wslpath -w scripts/open-chrome-remote.ps1)\"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"\$win_script\""
fi

printf '\nSummary: %d failure(s), %d warning(s)\n' "$failures" "$warnings"
if [[ "$failures" -gt 0 ]]; then
  exit 1
fi
