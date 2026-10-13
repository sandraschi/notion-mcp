#Requires -Version 5.1
# Fleet pre-commit biome gate: run `biome ci` in each configured web root.
# Skips roots without biome.json (nothing to enforce there).
$repo = Split-Path -Parent $PSScriptRoot
$roots = @('web_sota', 'webapp', 'webapp/frontend', 'web')
$checked = 0
foreach ($r in $roots) {
  $dir = Join-Path $repo $r
  if ((Test-Path -LiteralPath $dir) -and (Test-Path -LiteralPath (Join-Path $dir 'biome.json'))) {
    $checked += 1
    Push-Location $dir
    & npx '@biomejs/biome' ci .
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
