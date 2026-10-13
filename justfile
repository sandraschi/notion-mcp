set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]
import 'scripts/just/fleet.just'

# Open the interactive recipe dashboard in the browser
default:
    @just --list

# --- Quality ---

# Execute Ruff SOTA linting
lint:
    Set-Location '{{justfile_directory()}}'; uv run ruff check .

# Execute Ruff auto-fix and formatting
fix:
    Set-Location '{{justfile_directory()}}'; uv run ruff check . --fix --unsafe-fixes; uv run ruff format .

# Check formatting (CI gate, no writes) - code only, never vendored docs
fmt:
    Set-Location '{{justfile_directory()}}'; uv run ruff format --check server.py run_server.py notion_mcp/ scripts/ tests/ mcpb/ web_sota/backend/

# Run test suite
test:
    Set-Location '{{justfile_directory()}}'; uv run pytest tests/ -q

# Pack the MCPB bundle: fleet recipe (scripts/mcpb-pack.ps1 shim, never bare
# `mcpb pack`) comes from the scripts/just/fleet.just import above. Do NOT
# redefine mcpb-pack/cua-* here - just errors on duplicate recipes.

# Playwright e2e (backend + frontend webServers, chromium headless shell)
e2e:
    Set-Location '{{justfile_directory()}}\web_sota'; bun run test:e2e

# Biome lint frontend
lint-web:
    Set-Location '{{justfile_directory()}}\web_sota'; bunx @biomejs/biome ci .

# Biome auto-fix frontend
fix-web:
    Set-Location '{{justfile_directory()}}\web_sota'; bunx @biomejs/biome check --write .

# --- Hardening ---

# Execute Bandit security audit
check-sec:
    Set-Location '{{justfile_directory()}}'; uv run bandit -r notion_mcp/

# --- Install  serve ---

# Install Python + frontend deps (run after git clone)
bootstrap:
    Set-Location '{{justfile_directory()}}'; uv sync --extra dev; if (Test-Path '{{justfile_directory()}}\web_sota') { Push-Location '{{justfile_directory()}}\web_sota'; bun install; Pop-Location }; if (Get-Command pre-commit -ErrorAction SilentlyContinue) { pre-commit install } else { Write-Host 'pre-commit not on PATH, skipping hook install' }; Write-Host "Bootstrap complete. Run: just dev or start.bat" -ForegroundColor Green

# Start backend only (HTTP mode)
serve:
    Set-Location '{{justfile_directory()}}'; uv run python server.py --http --port 10811

# Start full stack via web_sota/start.ps1
dev:
    Set-Location '{{justfile_directory()}}\web_sota'; .\start.ps1

# Alias for dashboard launch
web: dev


# Bootstrap: install dev deps + pre-commit hook
