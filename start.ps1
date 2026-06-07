param(
    [switch]$Headless,
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$NoBrowser
)

$webStart = Join-Path $PSScriptRoot "web_sota\start.ps1"
if (-not (Test-Path -LiteralPath $webStart)) {
    Write-Host "ERROR: web_sota\start.ps1 not found." -ForegroundColor Red
    exit 1
}
& $webStart `
    -Headless:$Headless `
    -BackendOnly:$BackendOnly `
    -FrontendOnly:$FrontendOnly `
    -NoBrowser:$NoBrowser
exit $LASTEXITCODE
