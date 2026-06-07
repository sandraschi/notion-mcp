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
