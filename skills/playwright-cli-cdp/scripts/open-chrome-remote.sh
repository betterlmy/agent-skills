#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# WSL uses the established Windows host browser, not a second Linux browser.
if grep -qi microsoft /proc/version 2>/dev/null; then
  powershell_bin="$(command -v powershell.exe || true)"
  powershell_bin="${powershell_bin:-/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe}"
  [[ -x "$powershell_bin" ]] || { echo 'Windows PowerShell is unavailable.' >&2; exit 1; }
  params=(-NoProfile -ExecutionPolicy Bypass -File "$(wslpath -w "$script_dir/open-chrome-remote.ps1")" -StartUrl "${1:-about:blank}")
  [[ -z "${CDP_SESSION:-}" ]] || params+=(-Session "$CDP_SESSION")
  [[ -z "${CDP_PORT:-}" ]] || params+=(-Port "$CDP_PORT")
  [[ -z "${CDP_HOST:-}" ]] || params+=(-HostName "$CDP_HOST")
  [[ -z "${CDP_USER_DATA_DIR:-}" ]] || params+=(-UserDataDir "$CDP_USER_DATA_DIR")
  [[ -z "${CHROME_BIN:-}" ]] || params+=(-ChromeBin "$CHROME_BIN")
  [[ -z "${CDP_TIMEOUT_SECONDS:-}" ]] || params+=(-TimeoutSeconds "$CDP_TIMEOUT_SECONDS")
  exec "$powershell_bin" "${params[@]}"
fi

HOST="${CDP_HOST:-127.0.0.1}"
PORT="${CDP_PORT:-0}"
TIMEOUT_SECONDS="${CDP_TIMEOUT_SECONDS:-15}"
[[ "$HOST" == 127.0.0.1 ]] || { echo 'Only loopback 127.0.0.1 is supported.' >&2; exit 1; }
[[ "$PORT" =~ ^[0-9]{1,5}$ ]] && (( 10#$PORT <= 65535 )) || { echo 'Invalid CDP_PORT.' >&2; exit 1; }
[[ "$TIMEOUT_SECONDS" =~ ^[0-9]+$ ]] && (( TIMEOUT_SECONDS > 0 )) || { echo 'Invalid CDP_TIMEOUT_SECONDS.' >&2; exit 1; }
command -v python3 >/dev/null || { echo 'python3 is required for endpoint JSON validation.' >&2; exit 1; }
SESSION="${CDP_SESSION:-agent-$(python3 -c 'import uuid; print(uuid.uuid4().hex)')}"
[[ "$SESSION" =~ ^[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}$ ]] || { echo 'Invalid CDP_SESSION.' >&2; exit 1; }
USER_DATA_DIR="${CDP_USER_DATA_DIR:-$HOME/.cache/playwright-cli-cdp/profiles/$SESSION}"
LOG_FILE="${CDP_LOG_FILE:-${TMPDIR:-/tmp}/playwright-cli-cdp-$SESSION.log}"

find_chrome() {
  if [[ -n "${CHROME_BIN:-}" ]]; then
    [[ -x "$CHROME_BIN" ]] && printf '%s\n' "$CHROME_BIN"
    return
  fi
  local candidate
  for candidate in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" "/Applications/Chromium.app/Contents/MacOS/Chromium" "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" google-chrome google-chrome-stable chromium chromium-browser microsoft-edge microsoft-edge-stable; do
    if [[ "$candidate" == */* && -x "$candidate" ]]; then
      printf '%s\n' "$candidate"; return
    elif command -v "$candidate" >/dev/null 2>&1; then
      command -v "$candidate"; return
    fi
  done
  return 1
}
chrome_bin="$(find_chrome)" || { echo 'Chrome not found; set CHROME_BIN.' >&2; exit 1; }
# Reject an occupied fixed port rather than silently adopting someone else's browser.
if (( 10#$PORT != 0 )); then
  python3 - "$PORT" <<'PY'
import socket, sys
with socket.socket() as sock:
    sock.bind(('127.0.0.1', int(sys.argv[1])))
PY
fi
mkdir -p "$(dirname "$USER_DATA_DIR")"
mkdir "$USER_DATA_DIR" # exclusive: never reuse a profile or a stale port file
USER_DATA_DIR="$(cd "$USER_DATA_DIR" && pwd)"
args=("--remote-debugging-address=$HOST" "--remote-debugging-port=$PORT" "--user-data-dir=$USER_DATA_DIR" --no-first-run --no-default-browser-check "${1:-about:blank}")
if [[ "$(uname -s)" == Darwin && "$chrome_bin" == *.app/Contents/MacOS/* ]]; then
  /usr/bin/open -n -a "${chrome_bin%%.app/*}.app" --args "${args[@]}" >>"$LOG_FILE" 2>&1
elif command -v setsid >/dev/null 2>&1; then
  setsid "$chrome_bin" "${args[@]}" >"$LOG_FILE" 2>&1 </dev/null &
else
  nohup "$chrome_bin" "${args[@]}" >"$LOG_FILE" 2>&1 </dev/null &
fi

# Validate both the dynamic port file and the browser identity at that endpoint.
python3 - "$USER_DATA_DIR" "$PORT" "$SESSION" "$TIMEOUT_SECONDS" <<'PY'
import json, pathlib, sys, time, urllib.request
profile, requested, session, timeout = sys.argv[1:]
deadline = time.monotonic() + int(timeout)
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
while time.monotonic() < deadline:
    try:
        browser_path = None
        port = int(requested)
        if port == 0:
            lines = (pathlib.Path(profile) / 'DevToolsActivePort').read_text().splitlines()
            port, browser_path = int(lines[0]), lines[1]
            if not 1 <= port <= 65535 or not browser_path.startswith('/devtools/browser/'):
                raise ValueError('Incomplete port file')
        endpoint = f'http://127.0.0.1:{port}'
        with opener.open(endpoint + '/json/version', timeout=1) as response:
            version = json.load(response)
        websocket = version['webSocketDebuggerUrl']
        if browser_path and not websocket.endswith(browser_path):
            raise ValueError('CDP browser identity mismatch')
        print(json.dumps(dict(session=session, endpoint=endpoint, profile=profile)))
        break
    except (OSError, ValueError, KeyError, IndexError):
        time.sleep(.2)
else:
    sys.exit(f'CDP startup timed out. Session={session} Profile={profile}; resources retained.')
PY
