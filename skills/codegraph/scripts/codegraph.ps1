#requires -Version 5.1

Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"
$CliArgs = @($args)

function Show-Usage {
    @"
CodeGraph CLI wrapper

用法:
  codegraph.ps1 check
  codegraph.ps1 raw <codegraph-args...>
  codegraph.ps1 init <project> [--verbose]
  codegraph.ps1 uninit <project> [--force]
  codegraph.ps1 index <project> [--force] [--quiet] [--verbose]
  codegraph.ps1 sync <project> [--quiet]
  codegraph.ps1 status <project> [--no-json]
  codegraph.ps1 explore <project> <query...> [--max-files N]
  codegraph.ps1 node <project> [name] [--file FILE] [--offset N] [--limit N] [--symbols-only]
  codegraph.ps1 query <project> <search> [--limit N] [--kind KIND] [--no-json]
  codegraph.ps1 files <project> [options] [--no-json]
  codegraph.ps1 callers|callees <project> <symbol> [--limit N] [--no-json]
  codegraph.ps1 impact <project> <symbol> [--depth N] [--no-json]
  codegraph.ps1 affected <project> [files...] [options] [--no-json]
  codegraph.ps1 unlock <project>
  codegraph.ps1 upgrade [version] [--check] [--force]

环境变量:
  CODEGRAPH_BIN  指定 codegraph 可执行文件，默认从 PATH 查找。
"@
}

function Fail([string] $Message) {
    [Console]::Error.WriteLine("错误: $Message")
    exit 1
}

function Get-Tail([object[]] $Values, [int] $Start) {
    if ($Values.Count -le $Start) {
        return @()
    }
    return @($Values[$Start..($Values.Count - 1)])
}

function Require-Value([object[]] $Values, [int] $Index, [string] $Name) {
    if ($Values.Count -le $Index -or [string]::IsNullOrWhiteSpace([string] $Values[$Index])) {
        Fail "缺少 $Name 参数。"
    }
    return [string] $Values[$Index]
}

function Get-CodeGraphBin {
    if (-not [string]::IsNullOrWhiteSpace($env:CODEGRAPH_BIN)) {
        return $env:CODEGRAPH_BIN
    }
    $Command = Get-Command codegraph -ErrorAction SilentlyContinue
    if ($null -eq $Command) {
        Fail "找不到 codegraph。请先获得用户同意后安装 CLI，或设置 CODEGRAPH_BIN。"
    }
    return $Command.Source
}

function Invoke-CodeGraph([string[]] $ToolArgs) {
    & $script:CodeGraphBin @ToolArgs
    exit $LASTEXITCODE
}

function Ensure-IndexIgnored([string] $Project) {
    if ($null -eq (Get-Command git -ErrorAction SilentlyContinue)) {
        return
    }

    & git -C $Project rev-parse --is-inside-work-tree *> $null
    if ($LASTEXITCODE -ne 0) {
        return
    }

    $ProjectPath = (Resolve-Path -LiteralPath $Project).Path
    $Probe = Join-Path $ProjectPath ".codegraph/.ignore-check"
    & git -C $Project check-ignore -q --no-index -- $Probe
    if ($LASTEXITCODE -ne 0) {
        Fail "项目未忽略 .codegraph/。请先获得用户同意并在适用的 .gitignore 中加入 .codegraph/ 或 **/.codegraph/。"
    }
}

$CommandName = if ($CliArgs.Count -gt 0) { $CliArgs[0] } else { "help" }
if ($CommandName -in @("help", "-h", "--help")) {
    Show-Usage
    exit 0
}

$Rest = @(Get-Tail $CliArgs 1)
$script:CodeGraphBin = Get-CodeGraphBin

switch ($CommandName) {
    "check" {
        Invoke-CodeGraph @("--version")
    }
    "raw" {
        if ($Rest.Count -eq 0) { Fail "raw 需要传入 codegraph 原生命令参数。" }
        Invoke-CodeGraph $Rest
    }
    "init" {
        $Project = Require-Value $Rest 0 "project"
        Ensure-IndexIgnored $Project
        $Forward = @(Get-Tail $Rest 1)
        Invoke-CodeGraph (@("init") + $Forward + @($Project))
    }
    { $_ -in @("uninit", "index", "sync") } {
        $Project = Require-Value $Rest 0 "project"
        $Forward = @(Get-Tail $Rest 1)
        Invoke-CodeGraph (@($CommandName) + $Forward + @($Project))
    }
    "status" {
        $Project = Require-Value $Rest 0 "project"
        $Forward = @(Get-Tail $Rest 1)
        $NoJson = $Forward -contains "--no-json"
        $Forward = @($Forward | Where-Object { $_ -ne "--no-json" })
        if (-not $NoJson) { $Forward += "--json" }
        Invoke-CodeGraph (@("status") + $Forward + @($Project))
    }
    "explore" {
        $Project = Require-Value $Rest 0 "project"
        $Forward = @(Get-Tail $Rest 1)
        if ($Forward.Count -eq 0) { Fail "explore 缺少 query 参数。" }
        Invoke-CodeGraph (@("explore", "--path", $Project) + $Forward)
    }
    "node" {
        $Project = Require-Value $Rest 0 "project"
        $Forward = @(Get-Tail $Rest 1)
        if ($Forward.Count -eq 0) { Fail "node 需要 symbol、file 或其他查询参数。" }
        Invoke-CodeGraph (@("node", "--path", $Project) + $Forward)
    }
    "query" {
        $Project = Require-Value $Rest 0 "project"
        $Search = Require-Value $Rest 1 "search"
        $Forward = @(Get-Tail $Rest 2)
        $NoJson = $Forward -contains "--no-json"
        $Forward = @($Forward | Where-Object { $_ -ne "--no-json" })
        if (-not $NoJson) { $Forward += "--json" }
        Invoke-CodeGraph (@("query", "--path", $Project) + $Forward + @($Search))
    }
    "files" {
        $Project = Require-Value $Rest 0 "project"
        $Forward = @(Get-Tail $Rest 1)
        $NoJson = $Forward -contains "--no-json"
        $Forward = @($Forward | Where-Object { $_ -ne "--no-json" })
        if (-not $NoJson) { $Forward += "--json" }
        Invoke-CodeGraph (@("files", "--path", $Project) + $Forward)
    }
    { $_ -in @("callers", "callees") } {
        $Project = Require-Value $Rest 0 "project"
        $Symbol = Require-Value $Rest 1 "symbol"
        $Forward = @(Get-Tail $Rest 2)
        $NoJson = $Forward -contains "--no-json"
        $Forward = @($Forward | Where-Object { $_ -ne "--no-json" })
        if (-not $NoJson) { $Forward += "--json" }
        Invoke-CodeGraph (@($CommandName, "--path", $Project) + $Forward + @($Symbol))
    }
    "impact" {
        $Project = Require-Value $Rest 0 "project"
        $Symbol = Require-Value $Rest 1 "symbol"
        $Forward = @(Get-Tail $Rest 2)
        $NoJson = $Forward -contains "--no-json"
        $Forward = @($Forward | Where-Object { $_ -ne "--no-json" })
        if (-not $NoJson) { $Forward += "--json" }
        Invoke-CodeGraph (@("impact", "--path", $Project) + $Forward + @($Symbol))
    }
    "affected" {
        $Project = Require-Value $Rest 0 "project"
        $Forward = @(Get-Tail $Rest 1)
        $NoJson = $Forward -contains "--no-json"
        $Forward = @($Forward | Where-Object { $_ -ne "--no-json" })
        if (-not $NoJson) { $Forward += "--json" }
        Invoke-CodeGraph (@("affected", "--path", $Project) + $Forward)
    }
    "unlock" {
        $Project = Require-Value $Rest 0 "project"
        if ($Rest.Count -ne 1) { Fail "unlock 不接受额外参数。" }
        Invoke-CodeGraph @("unlock", $Project)
    }
    "upgrade" {
        & $script:CodeGraphBin upgrade --help *> $null
        if ($LASTEXITCODE -eq 0) {
            Invoke-CodeGraph (@("upgrade") + $Rest)
        }

        if ($null -eq (Get-Command npm -ErrorAction SilentlyContinue)) {
            Fail "当前 CodeGraph 不支持原生 upgrade，且找不到 npm；请按官方安装方式重新安装。"
        }

        $Check = $Rest -contains "--check"
        $Unsupported = @($Rest | Where-Object { $_ -like "-*" -and $_ -notin @("--check", "--force") })
        if ($Unsupported.Count -gt 0) { Fail "upgrade fallback 不支持参数: $($Unsupported[0])" }
        $Version = @($Rest | Where-Object { -not $_.StartsWith("-") } | Select-Object -Last 1)

        if ($Check) {
            $Current = (& $script:CodeGraphBin --version 2>$null | Select-Object -First 1)
            if ([string]::IsNullOrWhiteSpace($Current)) { $Current = "unknown" }
            $Latest = (& npm view @colbymchenry/codegraph version | Select-Object -First 1)
            Write-Output "current=$Current"
            Write-Output "latest=$Latest"
            if ($Current -eq $Latest) { Write-Output "status=up-to-date" }
            else { Write-Output "status=update-available" }
            exit 0
        }

        if ($Version.Count -gt 0) {
            & npm i -g "@colbymchenry/codegraph@$($Version[0])"
            exit $LASTEXITCODE
        }
        & npm i -g @colbymchenry/codegraph
        exit $LASTEXITCODE
    }
    default {
        [Console]::Error.WriteLine((Show-Usage))
        Fail "未知命令: $CommandName"
    }
}
