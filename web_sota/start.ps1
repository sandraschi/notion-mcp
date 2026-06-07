# start.ps1 - notion-mcp + web_sota dashboard (self-contained, naked-PC compliant)
param(
    [switch]$Headless,
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$NoBrowser
)

if ($FrontendOnly -and $BackendOnly) {
    Write-Host "ERROR: Cannot combine -FrontendOnly and -BackendOnly." -ForegroundColor Red
    exit 1
}

if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    $relaunch = @('-NoProfile', '-File', $PSCommandPath, '-Headless')
    if ($BackendOnly)  { $relaunch += '-BackendOnly' }
    if ($FrontendOnly) { $relaunch += '-FrontendOnly' }
    if ($NoBrowser)    { $relaunch += '-NoBrowser' }
    Start-Process powershell.exe -ArgumentList $relaunch -WindowStyle Hidden
    exit
}

$RunBackend  = -not $FrontendOnly
$RunFrontend = $FrontendOnly -or ((-not $BackendOnly) -and (-not $Headless))
$SkipBrowser = $NoBrowser -or $Headless -or $BackendOnly

$FrontendPort = 10810
$BackendPort  = 10811
$RepoRoot     = Split-Path -Parent $PSScriptRoot
$WebRoot      = $PSScriptRoot
$ApiHealth    = "http://127.0.0.1:$BackendPort/api/status"

$__PortHelpers = Join-Path $RepoRoot 'scripts\PortHelpers.ps1'
if (-not (Test-Path -LiteralPath $__PortHelpers)) {
    Write-Host "ERROR: Missing PortHelpers.ps1 at $__PortHelpers" -ForegroundColor Red
    exit 1
}
. $__PortHelpers

$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" +
            [System.Environment]::GetEnvironmentVariable("PATH", "User")

Write-Host ""
Write-Host "notion-mcp - Setup and Start" -ForegroundColor Cyan
Write-Host "Backend :$BackendPort   Frontend :$FrontendPort" -ForegroundColor DarkGray
Write-Host ""

function Require-Command {
    param([string]$Cmd, [string]$WingetId, [string]$Label)
    if (Get-Command $Cmd -ErrorAction SilentlyContinue) {
        Write-Host "  [ok] $Label" -ForegroundColor DarkGreen
        return
    }
    Write-Host "  [--] $Label not found - installing via winget ..." -ForegroundColor Yellow

    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if (-not $winget) {
        $candidates = @(
            "$env:LOCALAPPDATA\Microsoft\WindowsApps\winget.exe",
            "$env:PROGRAMFILES\WindowsApps\Microsoft.DesktopAppInstaller_*\winget.exe"
        )
        foreach ($c in $candidates) {
            $found = Get-Item $c -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($found) { $winget = $found.FullName; break }
        }
    } else {
        $winget = $winget.Source
    }

    if (-not $winget) {
        Write-Host "ERROR: winget not found. Install $Label manually:" -ForegroundColor Red
        Write-Host "  winget install --id $WingetId" -ForegroundColor Yellow
        exit 1
    }

    & $winget install --id $WingetId --silent --accept-source-agreements --accept-package-agreements
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("PATH", "User")
    if (-not (Get-Command $Cmd -ErrorAction SilentlyContinue)) {
        Write-Host "ERROR: $Label installed but '$Cmd' still not in PATH." -ForegroundColor Red
        Write-Host "Close this window, reopen PowerShell, and run start.bat again." -ForegroundColor Yellow
        exit 1
    }
    Write-Host "  [ok] $Label installed" -ForegroundColor Green
}

function Get-NpmCmdPath {
    $nodeApp = Get-Command node -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    $nodeSrc = if ($nodeApp -and $nodeApp.Source -and ($nodeApp.Source -ne '')) { $nodeApp.Source } else { $null }
    if (-not $nodeSrc) { $nodeSrc = [string](where.exe node 2>$null | Select-Object -First 1) }
    if ($nodeSrc -and ($nodeSrc -ne '')) {
        $nodeDir = Split-Path -Path ([string]$nodeSrc) -Parent
        $cmd = Join-Path $nodeDir "npm.cmd"
        if (Test-Path -LiteralPath $cmd) { return $cmd }
    }
    $npmApp = Get-Command npm -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($npmApp -and $npmApp.Source -and ($npmApp.Source -ne '')) { return $npmApp.Source }
    $npmWhere = [string](where.exe npm 2>$null | Select-Object -First 1)
    if ($npmWhere) { return $npmWhere }
    return $null
}

function Test-ViteBinPresent {
    param([string]$WebRootPath)
    $bin = Join-Path $WebRootPath "node_modules\.bin"
    foreach ($name in @('vite', 'vite.cmd', 'vite.exe', 'vite.bunx')) {
        if (Test-Path -LiteralPath (Join-Path $bin $name)) { return $true }
    }
    $pkg = Join-Path $WebRootPath "node_modules\vite\package.json"
    return (Test-Path -LiteralPath $pkg)
}

function Invoke-UvSync {
    param([string]$UvExePath, [string]$Root)
    Stop-RepoConsoleScriptLock -RepoRoot $Root -ScriptNames @('notion-mcp')
    & $UvExePath sync --extra dev --project $Root
    if ($LASTEXITCODE -eq 0) { return $true }

    Write-Host "  [--] uv sync failed - releasing console script lock and retrying once ..." -ForegroundColor Yellow
    Stop-RepoConsoleScriptLock -RepoRoot $Root -ScriptNames @('notion-mcp')
    Start-Sleep -Milliseconds 300
    & $UvExePath sync --extra dev --project $Root
    return ($LASTEXITCODE -eq 0)
}

Write-Host "[1/5] Checking prerequisites ..." -ForegroundColor Cyan
Require-Command "uv"   "Astral.uv"         "uv (Python package manager)"
Require-Command "just" "Casey.Just"        "just (command runner)"
if ($RunFrontend) {
    Require-Command "node" "OpenJS.NodeJS.LTS" "Node.js LTS (Vite runtime)"
    Require-Command "npm"  "OpenJS.NodeJS.LTS" "npm"
}

$uvExe = (Get-Command uv).Source
if ($env:SKIP_SYNC -eq "1") {
    Write-Host "[2/5] Skipping Python deps (SKIP_SYNC=1)" -ForegroundColor DarkGray
} else {
    Write-Host "[2/5] Syncing Python deps (uv sync --extra dev) ..." -ForegroundColor Cyan
    Write-Host "  (first run: uv may download Python - this can take 30s)" -ForegroundColor DarkGray
    if (-not (Invoke-UvSync -UvExePath $uvExe -Root $RepoRoot)) {
        Write-Host "ERROR: uv sync failed. Close any notion-mcp windows and retry, or set SKIP_SYNC=1." -ForegroundColor Red
        exit 1
    }
    Write-Host "  [ok] Python deps ready" -ForegroundColor DarkGreen
}

Write-Host "  Smoke-testing import ..." -ForegroundColor DarkGray
$serverPy = Join-Path $RepoRoot 'server.py'
if (-not (Test-Path -LiteralPath $serverPy)) {
    Write-Host "ERROR: missing $serverPy" -ForegroundColor Red
    exit 1
}
& $uvExe run --project $RepoRoot python -c "import server; print('  [ok] Import OK')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: import check failed - see output above." -ForegroundColor Red
    exit 1
}

if ($RunFrontend) {
    Write-Host "[3/5] Syncing frontend deps ..." -ForegroundColor Cyan
    $npmCmd = Get-NpmCmdPath
    if (-not $npmCmd) {
        Write-Host "ERROR: Could not resolve npm." -ForegroundColor Red
        exit 1
    }
    $needFrontendInstall = -not (Test-Path (Join-Path $WebRoot "node_modules"))
    if (-not $needFrontendInstall -and -not (Test-ViteBinPresent -WebRootPath $WebRoot)) {
        Write-Host "  [--] node_modules present but vite missing - reinstalling ..." -ForegroundColor Yellow
        $needFrontendInstall = $true
    }
    if ($needFrontendInstall) {
        Push-Location $WebRoot
        & $npmCmd install --prefer-offline
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERROR: frontend install failed." -ForegroundColor Red
            Pop-Location
            exit 1
        }
        Pop-Location
        Write-Host "  [ok] node_modules installed" -ForegroundColor DarkGreen
    } else {
        Write-Host "  [ok] node_modules present (skipping install)" -ForegroundColor DarkGreen
    }
    if (-not (Test-ViteBinPresent -WebRootPath $WebRoot)) {
        Write-Host "ERROR: vite missing after install. Delete '$WebRoot\node_modules' and re-run." -ForegroundColor Red
        exit 1
    }
    Write-Host "  [ok] vite present" -ForegroundColor DarkGreen
} else {
    Write-Host "[3/5] Skipping frontend deps" -ForegroundColor DarkGray
}

Write-Host "[4/5] Clearing ports $BackendPort / $FrontendPort ..." -ForegroundColor Cyan
Stop-PortListeners -Ports @($BackendPort, $FrontendPort) -Label 'notion-mcp'

Write-Host "[5/5] Starting services ..." -ForegroundColor Cyan

$backendProc = $null
if ($RunBackend) {
    $backendLog = Join-Path $RepoRoot "backend.log"
    $backendErr = Join-Path $RepoRoot "backend.err.log"
    foreach ($logPath in @($backendLog, $backendErr)) {
        if (Test-Path $logPath) { Remove-Item -LiteralPath $logPath -Force -ErrorAction SilentlyContinue }
    }
    $backendProc = Start-Process -FilePath $uvExe `
        -ArgumentList @(
            'run', '--project', $RepoRoot,
            'python', 'server.py', '--http', '--port', "$BackendPort"
        ) `
        -WorkingDirectory $RepoRoot `
        -RedirectStandardOutput $backendLog `
        -RedirectStandardError $backendErr `
        -PassThru `
        -WindowStyle Hidden
    Write-Host "  Backend PID $($backendProc.Id) on :$BackendPort  (log: $backendLog)"

    $maxWait = 90
    $waited = 0
    $ready = $false
    Write-Host "  Waiting for backend health (max ${maxWait}s) ..." -ForegroundColor DarkCyan
    while ($waited -lt $maxWait) {
        if ($backendProc.HasExited) {
            Write-Host "ERROR: backend process exited (code $($backendProc.ExitCode))." -ForegroundColor Red
            break
        }
        try {
            $r = Invoke-WebRequest -Uri $ApiHealth -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
            if ($r.StatusCode -eq 200) { $ready = $true; break }
        } catch {}
        Start-Sleep -Seconds 1
        $waited++
        if (($waited % 15) -eq 0) { Write-Host "    ... $waited s" -ForegroundColor DarkGray }
    }

    if (-not $ready) {
        Write-Host "ERROR: backend did not start after ${maxWait}s." -ForegroundColor Red
        Write-Host "Last lines from backend.log:" -ForegroundColor Yellow
        if (Test-Path $backendLog) { Get-Content $backendLog -Tail 30 }
        if (Test-Path $backendErr) {
            Write-Host "stderr:" -ForegroundColor Yellow
            Get-Content $backendErr -Tail 20
        }
        Write-Host "Run directly to see the full error:" -ForegroundColor Yellow
        Write-Host "  cd $RepoRoot; $uvExe run python server.py --http --port $BackendPort" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "  [ok] Backend healthy after ${waited}s" -ForegroundColor Green
}

if ($BackendOnly) {
    Write-Host ""
    Write-Host "Backend-only mode active. Press Ctrl+C to stop." -ForegroundColor Cyan
    try { Wait-Process -Id $backendProc.Id -ErrorAction SilentlyContinue } catch {}
    exit
}

if (-not $RunFrontend) {
    exit
}

$npmCmd = Get-NpmCmdPath
$frontendProc = Start-Process -FilePath $npmCmd `
    -ArgumentList @("run", "dev") `
    -WorkingDirectory $WebRoot `
    -PassThru
Write-Host "  Frontend PID $($frontendProc.Id) on :$FrontendPort" -ForegroundColor DarkGray

if (-not $SkipBrowser) {
    $url = "http://127.0.0.1:$FrontendPort"
    $poll = "for (`$i=0;`$i -lt 60;`$i++) { try { `$null=Invoke-WebRequest -Uri '$url' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; Start-Process '$url'; exit } catch { Start-Sleep 1 } }"
    Start-Process powershell.exe -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $poll
    Write-Host "  Browser will open when Vite is ready" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "Running:" -ForegroundColor Cyan
Write-Host "  Backend   $ApiHealth"
Write-Host "  Frontend  http://127.0.0.1:$FrontendPort"
Write-Host "  MCP HTTP  http://127.0.0.1:$BackendPort/mcp"
Write-Host ""
Write-Host "Press Ctrl+C to stop." -ForegroundColor DarkGray

if ($null -ne $backendProc) {
    try { Wait-Process -Id $backendProc.Id -ErrorAction SilentlyContinue } catch {}
}
