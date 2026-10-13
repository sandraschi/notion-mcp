# notion-mcp — Development

## Prereqs

- Python 3.12+, `uv` (`C:\Users\sandr\.local\bin\uv.exe`)
- Node 22 + npm (web dashboard in `web_sota/`)
- `pre-commit` for hooks (`just bootstrap` installs the hook)

## Install

```powershell
uv sync --extra dev
pre-commit install
Push-Location web_sota; bun install; Pop-Location
```

Or `just bootstrap`.

Toolchain split (deliberate): bun owns `install` (`bun.lock`), lint,
build, and test (`bun run ...`); `npm run dev` serves the dashboard
(node is on PATH everywhere, bun is not - spawned servers must not assume
it). Both read the same `node_modules`.

## Run

```powershell
just serve          # backend only (HTTP :10811)
just dev            # full stack via web_sota/start.ps1
uv run python server.py --http --port 10811   # same as serve
python -m notion_mcp                          # stdio (Claude Desktop)
```

Ports: frontend `10810`, backend `10811` (registry:
`mcp-central-docs/operations/WEBAPP_PORTS.md`).

## Gates (must be green before commit)

```powershell
just lint           # ruff check .
just fmt            # ruff format --check .
uv run pytest tests/ -q
uvx pyright notion_mcp/ server.py
Push-Location web_sota; npm run biome:ci; npx tsc --noEmit; Pop-Location
```

## Layout

- `server.py` — FastMCP tools (40) + FastAPI REST app (`app`), MCP sub-app
  mounted at `/mcp` via `mcp.http_app(path="/")` with parent lifespan wiring
  (BUG-008/038 pattern — do not revert to bare `mcp.http_app`).
- `notion_mcp/` — client, pages, databases, collaboration, automations,
  workers (`ntn` CLI), plugins, rag (LanceDB), transport (stdio/HTTP dual).
- `web_sota/` — React 19 + Vite dashboard (same-origin `/api` via proxy;
  absolute URL only behind the Tauri gate in `src/lib/api.ts`).
- `native/` — Tauri 2.0 wrapper (NSIS).
- `mcpb/` — Claude Desktop bundle sources; pack with `just mcpb-pack`
  (fleet shim — never bare `mcpb pack`).

## Conventions

- Tool docstrings: one-line summary + `## Return Format` +
  `## Examples` (fleet docstring gate).
- Returns: `{success, message, ...}` dialogic dicts; declared fallbacks carry
  `declared_fallback: true` / `simulated: true` (never silent stubs).
- Logging: structlog; `logger.exception()` inside `except` blocks.
- Ruff: `T20` enforced (no `print` in server code); `S110`/`S112` NOT ignored.
- Secrets: `.env` / `exports/` are gitignored. Never commit tokens.
