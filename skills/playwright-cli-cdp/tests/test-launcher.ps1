# Windows PowerShell 5.1 regressions; never starts a browser.
$ErrorActionPreference = 'Stop'
$Scripts = Join-Path (Split-Path -Parent $PSScriptRoot) 'scripts'
foreach ($File in Get-ChildItem -LiteralPath $Scripts -Filter '*.ps1') {
  $Tokens = $null
  $Errors = $null
  [System.Management.Automation.Language.Parser]::ParseFile($File.FullName, [ref]$Tokens, [ref]$Errors) | Out-Null
  if ($Errors.Count) { throw ($Errors | Out-String) }
}
$Launcher = Join-Path $Scripts 'open-chrome-remote.ps1'
$Wrapper = Join-Path $Scripts 'playwright-cdp.ps1'
function Expect-Failure {
  param([scriptblock]$Action, [string]$Pattern)
  $Failed = $false
  try { & $Action | Out-Null } catch {
    $Failed = $true
    if ($_ -notmatch $Pattern) { throw "Unexpected failure: $_" }
  }
  if (-not $Failed) { throw 'Expected failure did not occur' }
}
Expect-Failure { & $Launcher -HostName '0.0.0.0' } 'loopback'
Expect-Failure { & $Launcher -Session '../unsafe' } 'Session must'
Expect-Failure { & $Launcher -UserDataDir $env:TEMP } 'Profile already exists'
$Listener = New-Object System.Net.Sockets.TcpListener ([System.Net.IPAddress]::Loopback), 0
try {
  $Listener.Start()
  $Port = $Listener.LocalEndpoint.Port
  Expect-Failure { & $Launcher -Port $Port } 'port is occupied'
} finally { $Listener.Stop() }

# Stub the CLI, not the wrapper: assert arguments and environment per call.
function playwright-cli {
  $global:LASTEXITCODE = 0
  $env:PLAYWRIGHT_MCP_OUTPUT_DIR
}
$Before = $env:PLAYWRIGHT_MCP_OUTPUT_DIR
try {
  $env:PLAYWRIGHT_MCP_OUTPUT_DIR = $null
  $A = & $Wrapper '-s=task-a' snapshot
  $B = & $Wrapper '-s=task-b' snapshot
  if (-not $A.EndsWith('task-a') -or -not $B.EndsWith('task-b') -or $A -eq $B) {
    throw "Output directory isolation failed: $A / $B"
  }
  if ($env:PLAYWRIGHT_MCP_OUTPUT_DIR) { throw 'Wrapper leaked output directory into caller' }
  Expect-Failure { & $Wrapper '-s=../unsafe' snapshot } 'Invalid session'
} finally { $env:PLAYWRIGHT_MCP_OUTPUT_DIR = $Before }
Write-Output 'PASS: PowerShell syntax, unsafe inputs, existing profile, occupied port, output isolation, caller environment restoration.'
