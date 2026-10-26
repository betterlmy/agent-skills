[CmdletBinding()]
param(
  [string]$StartUrl = "about:blank",
  [string]$HostName = "",
  [ValidateRange(-1, 65535)][int]$Port = -1,
  [string]$Session = "",
  [string]$UserDataDir = "",
  [string]$ChromeBin = "",
  [int]$TimeoutSeconds = 0
)

$ErrorActionPreference = "Stop"

if (-not $HostName) {
  $HostName = if ($env:CDP_HOST) { $env:CDP_HOST } else { "127.0.0.1" }
}

if ($HostName -ne "127.0.0.1") {
  throw "Only loopback 127.0.0.1 is supported by this launcher."
}
if ($Port -eq -1) {
  $Port = if ($env:CDP_PORT) { [int]$env:CDP_PORT } else { 0 }
}
if ($Port -lt 0 -or $Port -gt 65535) { throw "Invalid CDP port: $Port" }
if (-not $Session) { $Session = "agent-" + [guid]::NewGuid().ToString("N") }
if ($Session -cnotmatch '^[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}$') {
  throw "Session must contain 1-80 ASCII letters, digits, underscores or hyphens."
}
if (-not $UserDataDir) {
  $UserDataDir = if ($env:CDP_USER_DATA_DIR) {
    $env:CDP_USER_DATA_DIR
  } else {
    Join-Path $env:LOCALAPPDATA "playwright-cli-cdp\profiles\$Session"
  }
}

if (-not $ChromeBin) {
  $ChromeBin = $env:CHROME_BIN
}

if (-not $TimeoutSeconds) {
  $TimeoutSeconds = 15
  if ($env:CDP_TIMEOUT_SECONDS) {
    [int]::TryParse($env:CDP_TIMEOUT_SECONDS, [ref]$TimeoutSeconds) | Out-Null
  }
}

if ($TimeoutSeconds -lt 1) {
  $TimeoutSeconds = 15
}

function Find-Chrome {
  if ($ChromeBin -and (Test-Path $ChromeBin)) {
    return $ChromeBin
  }

  $candidates = @(
    "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe",
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
    "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
    "$env:LOCALAPPDATA\Microsoft\Edge\Application\msedge.exe",
    "$env:ProgramFiles\Chromium\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Chromium\Application\chrome.exe"
  )

  foreach ($candidate in $candidates) {
    if ($candidate -and (Test-Path $candidate)) {
      return $candidate
    }
  }

  return $null
}

$ChromePath = Find-Chrome
if (-not $ChromePath) {
  throw @"
Could not find Chrome, Chromium, or Edge.
Set CHROME_BIN to the browser executable path and retry, for example:
  `$env:CHROME_BIN = "C:\Program Files\Google\Chrome\Application\chrome.exe"
  powershell -ExecutionPolicy Bypass -File scripts\open-chrome-remote.ps1
"@
}

if ($Port -ne 0) {
  $Probe = New-Object System.Net.Sockets.TcpListener ([System.Net.IPAddress]::Loopback), $Port
  try { $Probe.Start() } catch { throw "Requested CDP port is occupied or unavailable: $Port" } finally { $Probe.Stop() }
}

# Never launch against an existing profile (including stale DevToolsActivePort).
# Exclusive directory creation also rejects two launches using the same session.
$UserDataDir = [IO.Path]::GetFullPath($UserDataDir)
if (Test-Path -LiteralPath $UserDataDir) { throw "Profile already exists: $UserDataDir" }
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $UserDataDir) | Out-Null
New-Item -ItemType Directory -Path $UserDataDir -ErrorAction Stop | Out-Null

$Args = @(
  "--remote-debugging-address=$HostName",
  "--remote-debugging-port=$Port",
  "--user-data-dir=`"$UserDataDir`"",
  "--no-first-run",
  "--no-default-browser-check",
  "--ignore-certificate-errors",
  $StartUrl
)

Start-Process -FilePath $ChromePath -ArgumentList $Args | Out-Null

$PortFile = Join-Path $UserDataDir "DevToolsActivePort"
$Deadline = (Get-Date).AddSeconds($TimeoutSeconds)
while ((Get-Date) -lt $Deadline) {
  try {
    # Chrome writes this file for port=0; wait for both lines to be complete.
    if ($Port -eq 0) {
      $Lines = @(Get-Content -LiteralPath $PortFile -ErrorAction Stop)
      $ActualPort = 0
      if ($Lines.Count -lt 2 -or
          -not [int]::TryParse($Lines[0], [ref]$ActualPort) -or
          $ActualPort -lt 1 -or $ActualPort -gt 65535 -or
          $Lines[1] -notmatch '^/devtools/browser/.+') {
        throw "Incomplete DevToolsActivePort"
      }
    } else {
      $ActualPort = $Port
    }
    $Endpoint = "http://${HostName}:$ActualPort"
    $Version = Invoke-RestMethod -Uri "$Endpoint/json/version" -TimeoutSec 1
    if (-not $Version.webSocketDebuggerUrl) { throw "Not a browser CDP endpoint" }
    if ($Port -eq 0 -and -not $Version.webSocketDebuggerUrl.EndsWith($Lines[1])) {
      throw "CDP browser identity mismatch"
    }
    [ordered]@{
      session = $Session
      endpoint = $Endpoint
      profile = $UserDataDir
    } | ConvertTo-Json -Compress
    exit 0
  } catch {
    Start-Sleep -Milliseconds 200
  }
}

throw "CDP startup timed out after ${TimeoutSeconds}s. Session=$Session Profile=$UserDataDir RequestedPort=$Port. Resources were retained; do not kill other browsers."
