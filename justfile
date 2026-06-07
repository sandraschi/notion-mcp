set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]

# Open the interactive recipe dashboard in the browser
default:
    @just --list

# ── Quality ───────────────────────────────────────────────────────────────────

# Execute Ruff SOTA linting
lint:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check .

# Execute Ruff auto-fix and formatting
fix:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check . --fix --unsafe-fixes
    uv run ruff format .

# Biome lint frontend
lint-web:
    Set-Location '{{justfile_directory()}}\web_sota'
    npx @biomejs/biome ci .

# Biome auto-fix frontend
fix-web:
    Set-Location '{{justfile_directory()}}\web_sota'
    npx @biomejs/biome check --write .

# ── Hardening ─────────────────────────────────────────────────────────────────

# Execute Bandit security audit
check-sec:
    Set-Location '{{justfile_directory()}}'
    uv run bandit -r notion_mcp/

# ── Install / serve ───────────────────────────────────────────────────────────

# Install Python + frontend deps (run after git clone)
bootstrap:
    Set-Location '{{justfile_directory()}}'
    uv sync --extra dev
    if (Test-Path '{{justfile_directory()}}\web_sota') { Push-Location '{{justfile_directory()}}\web_sota'; npm install; Pop-Location }
    Write-Host "Bootstrap complete. Run: just dev or start.bat" -ForegroundColor Green

# Start backend only (HTTP mode)
serve:
    Set-Location '{{justfile_directory()}}'
    uv run python server.py --http --port 10811

# Start full stack via web_sota/start.ps1
dev:
    Set-Location '{{justfile_directory()}}\web_sota'
    .\start.ps1

# Alias for dashboard launch
web: dev
