#Requires -Version 5.1
# Fleet pre-commit biome gate: run the repo's own `biome:ci` script in each
# configured web root (uses the local node_modules binary via npm, never npx).
$repo = Split-Path -Parent $PSScriptRoot
$roots = @('web_sota', 'webapp', 'webapp/frontend', 'web')
$checked = 0
foreach ($r in $roots) {
  $dir = Join-Path $repo $r
  $pkg = Join-Path $dir 'package.json'
  if ((Test-Path -LiteralPath $dir) -and (Test-Path -LiteralPath $pkg)) {
    $checked += 1
    Push-Location $dir
    npm run biome:ci
    $code = $LASTEXITCODE
    Pop-Location
    if ($code -ne 0) {
      Write-Host "[biome] FAIL in $r (exit $code)" -ForegroundColor Red
      exit $code
    }
    Write-Host "[biome] PASS in $r" -ForegroundColor Green
  }
}
if ($checked -eq 0) { Write-Host '[biome] no configured web root, skipping.' }
exit 0
