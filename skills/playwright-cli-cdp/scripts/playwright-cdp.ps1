$OriginalOutputDir = $env:PLAYWRIGHT_MCP_OUTPUT_DIR
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

# Separate artifacts and their cleanup budgets for explicitly named sessions.
$Session = 'default'
foreach ($Argument in $args) {
  if ($Argument -match '^(?:-s|--session)=(.*)$') { $Session = $Matches[1] }
}
if ($Session -cnotmatch '^[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}$') {
  throw 'Invalid session name; use 1-80 ASCII letters, digits, underscores or hyphens.'
}
if (-not $env:PLAYWRIGHT_MCP_OUTPUT_DIR) {
  $env:PLAYWRIGHT_MCP_OUTPUT_DIR = Join-Path $env:TEMP "playwright-cli-cdp\$Session"
}
if (-not $env:PLAYWRIGHT_MCP_OUTPUT_MAX_SIZE) {
  $env:PLAYWRIGHT_MCP_OUTPUT_MAX_SIZE = '52428800'  # 50 MiB
}
New-Item -ItemType Directory -Force -Path $env:PLAYWRIGHT_MCP_OUTPUT_DIR | Out-Null

try {
  $PlaywrightCli = Get-Command playwright-cli -ErrorAction SilentlyContinue
  if ($PlaywrightCli) {
    & playwright-cli @args
    $ExitCode = $LASTEXITCODE
  } elseif (Get-Command npx -ErrorAction SilentlyContinue) {
    & npx --no-install playwright-cli @args
    $ExitCode = $LASTEXITCODE
  } else {
    Write-Error "playwright-cli was not found. Install @playwright/cli globally or in the current project."
    $ExitCode = 127
  }
} finally {
  # Repeated calls in one PowerShell process must not inherit another session's path.
  $env:PLAYWRIGHT_MCP_OUTPUT_DIR = $OriginalOutputDir
}
exit $ExitCode
