$PageTimeoutMs = 15000

if ($env:PLAYWRIGHT_MCP_TIMEOUT_NAVIGATION) {
  [int]::TryParse($env:PLAYWRIGHT_MCP_TIMEOUT_NAVIGATION, [ref]$PageTimeoutMs) | Out-Null
}

if ($env:PLAYWRIGHT_CLI_CDP_PAGE_TIMEOUT_MS) {
  [int]::TryParse($env:PLAYWRIGHT_CLI_CDP_PAGE_TIMEOUT_MS, [ref]$PageTimeoutMs) | Out-Null
}

if ($PageTimeoutMs -lt 1) {
  $PageTimeoutMs = 15000
}

$env:PLAYWRIGHT_MCP_TIMEOUT_NAVIGATION = [string]$PageTimeoutMs

# Redirect playwright-cli output (console logs, page snapshots) to a dedicated
# temp directory so the working directory stays clean. A fixed subdirectory lets
# the built-in outputMaxSize budget reclaim old files across runs; the budget
# never deletes files written by the current command. Both vars stay overridable.
if (-not $env:PLAYWRIGHT_MCP_OUTPUT_DIR) {
  $env:PLAYWRIGHT_MCP_OUTPUT_DIR = Join-Path $env:TEMP 'playwright-cli-cdp'
}
if (-not $env:PLAYWRIGHT_MCP_OUTPUT_MAX_SIZE) {
  $env:PLAYWRIGHT_MCP_OUTPUT_MAX_SIZE = '52428800'  # 50 MiB
}
New-Item -ItemType Directory -Force -Path $env:PLAYWRIGHT_MCP_OUTPUT_DIR | Out-Null

$PlaywrightCli = Get-Command playwright-cli -ErrorAction SilentlyContinue
if ($PlaywrightCli) {
  & playwright-cli @args
  exit $LASTEXITCODE
}

$Npx = Get-Command npx -ErrorAction SilentlyContinue
if ($Npx) {
  & npx --no-install playwright-cli @args
  exit $LASTEXITCODE
}

Write-Error "playwright-cli was not found. Install @playwright/cli globally or in the current project."
exit 127
