# notion-mcp

FastMCP MCP server for Notion workspace management. Browse, search, and manage pages and databases through MCP tools or the web dashboard.

**Version**: 1.2.0 | **Python**: 3.12+ | **Framework**: FastMCP 3.4, FastAPI | **License**: MIT

## Quick Start

```powershell
git clone https://github.com/sandraschi/notion-mcp
cd notion-mcp
just bootstrap   # install Python + frontend deps
just dev         # start backend + web dashboard
```

Open http://127.0.0.1:10810 in your browser.

### Get a Notion Token

1. Go to https://www.notion.so/my-integrations
2. Click "New integration", name it "NotionMCP", copy the token
3. Paste it in the web dashboard (Settings page or the Connect screen)
4. Share pages with the integration in Notion

## Ports

| Port | Service |
|------|---------|
| 10810 | Web dashboard (Vite dev server) |
| 10811 | Backend API (FastAPI + MCP HTTP) |

## MCP Transport

**stdio** (Claude Desktop / Cursor):
```json
{
  "mcpServers": {
    "notion-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "D:/Dev/repos/notion-mcp", "notion-mcp"]
    }
  }
}
```

**HTTP** (streamable): http://127.0.0.1:10811/mcp

## Tools (32)

### Page Management
`create_page`, `update_page`, `get_page_content`, `search_pages`, `archive_page`

### Database Operations
`create_database`, `query_database`, `create_database_entry`, `update_database_entry`, `get_database_schema`, `bulk_import_data`

### Collaboration
`add_comment`, `get_comments`, `get_workspace_users`

### RAG / Semantic Search
`sync_rag_index`, `search_notion_knowledge`, `clear_rag_index`

### Automations
`setup_automation`, `sync_external_data`, `generate_ai_summary`, `export_workspace_data`, `import_workspace_data`, `orchestrate_automation`

### Webhooks
`verify_webhook`, `list_webhook_events`

### Notion Workers (ntn CLI)
`deploy_worker`, `list_workers`, `scaffold_worker`, `worker_logs`, `check_ntn`, `orchestrate_workers`

### Consolidated
`manage_notion_data`, `query_data_source`, `search_notion_knowledge`

## Web Dashboard

React 19 + Vite 7 + TailwindCSS + Lucide + Radix UI. Permanently dark theme.

Pages: Dashboard (hero + recent content), Workspace Explorer (search + inline page viewer), AI Chat (personalities, speech), Settings (token config, LLM providers), Status (KPIs, services), Logging (ring buffer), Help.

## REST API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/health | Liveness probe |
| GET | /api/status | Auth status |
| GET | /api/recent?limit=N | Recent pages/databases |
| GET | /api/page/{id} | Page content with blocks |
| GET | /api/stats | Session request stats |
| GET | /api/tools | Registered MCP tool list |
| GET | /api/logs | Ring buffer log query |
| DELETE | /api/logs | Clear log buffer |
| GET | /api/logs/export | Export logs as JSON/CSV |
| GET | /api/llm-discovery | Probe Ollama/LM Studio |
| GET | /api/llm/providers | LLM provider list |
| GET | /api/skills | Available skills |
| GET | /api/plugins | Plugin list |
| POST | /api/plugins/install/{id} | Install plugin |
| POST | /api/configure/token | Set Notion token |
| POST | /api/search | Semantic search |
| POST | /api/chat | RAG chat completion |
| POST | /api/webhooks/notion | Webhook receiver |
| GET | /api/webhooks/events | Stored webhook events |

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| NOTION_TOKEN | Yes* | -- | Internal integration token |
| NOTION_PAT | Yes* | -- | Personal access token |
| NOTION_VERSION | No | 2026-03-11 | API version |
| LLM_API_URL | No | -- | OpenAI-compatible LLM endpoint |
| LLM_API_KEY | No | ollama | LLM API key |
| LLM_MODEL | No | llama3.2 | Model name |
| NTN_BIN | No | ntn | Notion CLI path |
| LOG_LEVEL | No | INFO | Logging level |

*One of NOTION_TOKEN or NOTION_PAT required. Can also be set via the web dashboard Settings page (stored in `exports/notion_token.txt`).

## Architecture

```
server.py (FastMCP + FastAPI)
  |-- notion_mcp/client.py        -- Notion API client
  |-- notion_mcp/pages.py         -- Page CRUD + markdown endpoints
  |-- notion_mcp/databases.py     -- Database query + schema
  |-- notion_mcp/collaboration.py -- Comments + users
  |-- notion_mcp/automations.py   -- AI summary, webhooks
  |-- notion_mcp/workers.py       -- ntn CLI wrapper
  |-- notion_mcp/plugins.py       -- Plugin management
  |-- notion_mcp/rag/             -- LanceDB vector pipeline
  |-- notion_mcp/transport.py     -- Dual stdio/HTTP transport
  |-- notion_mcp/skills/          -- FastMCP skills
  +-- web_sota/                   -- React web dashboard
```

## Testing

```bash
uv run pytest tests/ -q        # 20 tests
just lint                       # ruff check
just fix                        # ruff check --fix + format
```

## Native Desktop Build (Tauri + NSIS)

A Tauri 2.0 native wrapper is in `native/`. Build pipeline:

```powershell
just build-native    # PyInstaller backend + Tauri NSIS bundle
just cua-nsis-test   # install -> launch -> verify -> uninstall
```

Output: `native/target/release/bundle/nsis/Notion MCP_*_x64-setup.exe`

## Data Storage

- LanceDB: `data/notion_mcp/lancedb/` — RAG vector index
- Webhook events: `exports/webhook_events/`
- Token file: `exports/notion_token.txt` (set via web dashboard)
- Log ring buffer: in-memory (5000 entry cap, not persisted)

## License

MIT
