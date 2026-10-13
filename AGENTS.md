# notion-mcp - Agent Guide

## Overview

FastMCP 3.1 server for Notion workspace management and RAG.

## Entry Points

- `uv run notion-mcp` or `uv run python server.py --stdio` - stdio MCP
- `uv run python server.py --http --port 10811` - HTTP backend
- `.\start.bat` - full stack (backend + `web_sota` Vite dashboard)

## Standards

- FastMCP 3.x portmanteau tools use an `operation` enum parameter
- Responses: structured dicts with `success`, `message`, and domain fields
- Dual transport: stdio (Claude Desktop) and HTTP (`--http`)
- Ports: frontend `10810`, backend `10811`
- No mcp-central-docs dependency - use repo-local `README.md` and `INSTALL.md`

## Key Files

- `README.md` - full documentation
- `INSTALL.md` - setup and launch
- `pyproject.toml` - build config and entry points
- `justfile` - lint, bootstrap, `just dev`
- `CLAUDE.md` - Claude Code context (if present)

## Quick Ref

```powershell
uv run pytest tests/ -q
just dev
```

## HTTP Daemon + Stdio Proxy

- **Daemon port:** backend `10811` (frontend `10810`); liveness `GET /health`
  (alias of `/api/health`); orderly restart via `POST /api/shutdown`.
- **Transports:** stdio default (`python -m notion_mcp`, Claude Desktop);
  HTTP via `server.py --http --port 10811` (dashboard backend).
- **MCP mount:** `mcp.http_app(path="/")` mounted at `/mcp` on the FastAPI
  `app`; parent `app_lifespan` enters the sub-app router lifespan so the
  FastMCP session manager starts. Do not revert to bare `mcp.http_app`.
- **State:** LanceDB index under `.lancedb/` (repo root) + `web_sota/.lancedb`;
  token in gitignored `exports/notion_token.txt` (or `NOTION_TOKEN` env).
- **No NSSM service.** Known gap: `web_sota/start.ps1` does not clear zombie
  port holders before bind — restart manually if the port is held.
