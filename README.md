# notion-mcp

A bridge between your Notion workspace and the world of AI tools. Browse pages, search databases, chat with your content, and automate workflows — all through a local MCP server or web dashboard.

## What is this?

notion-mcp is a Python server that connects to your Notion workspace and exposes 32 MCP tools for managing pages, databases, comments, and content. It comes with a web dashboard for browsing and searching your workspace visually.

```
Just installed? Start here:
  1. just bootstrap    -- install dependencies
  2. just dev          -- launch dashboard
  3. Open http://127.0.0.1:10810
  4. Paste your Notion token on the Connect screen
```

### Get a Notion Token

1. Go to https://www.notion.so/my-integrations
2. Click "New integration", name it "NotionMCP", copy the token
3. Paste it in the web dashboard (or set `NOTION_TOKEN` in `.env`)

## What can I do with it?

| You want to... | Use this |
|----------------|----------|
| See your pages and databases | [Web Dashboard](http://127.0.0.1:10810) -> Explorer |
| Search across your workspace | Dashboard -> Semantic Search or Explorer |
| Chat with an AI about your content | Dashboard -> AI Chat |
| Create/update pages from code | MCP tools like `create_page`, `update_page` |
| Search programmatically | `search_pages`, `query_database` MCP tools |
| Sync content for offline RAG | `sync_rag_index` + `search_notion_knowledge` |
| Automate workflows | `setup_automation`, `sync_external_data` |

## Quick Start

```powershell
git clone https://github.com/sandraschi/notion-mcp
cd notion-mcp
just bootstrap
just dev
```

Ports: **10810** (web dashboard), **10811** (backend API)

### Claude Desktop / Cursor

Add to your MCP config:

```json
{
  "mcpServers": {
    "notion-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "path/to/notion-mcp", "notion-mcp"]
    }
  }
}
```

## Tools at a Glance

- **Pages**: create, update, get content, search, archive
- **Databases**: create, query, CRUD entries, schema, bulk import
- **Collaboration**: comments, workspace users
- **RAG**: sync vector index, semantic search
- **Automations**: webhooks, AI summaries, export/import, sync external data
- **Workers**: deploy, list, logs, scaffold (ntn CLI)

## Web Dashboard

React 19 webapp with dark theme. Pages: Dashboard (recent content), Explorer (search + inline page viewer), AI Chat (personalities, speech input/output), Settings (token config), Status (server KPIs), Logging (ring buffer), Help.

## REST API

The backend exposes REST endpoints at `http://127.0.0.1:10811` for the webapp and direct integration. Key ones: `GET /api/health`, `GET /api/recent`, `GET /api/page/{id}`, `GET /api/logs`, `POST /api/chat`, `POST /api/search`, `POST /api/configure/token`.

## Environment

| Variable | Needed for | Default |
|----------|-----------|---------|
| `NOTION_TOKEN` | Notion API access (internal integration) | -- |
| `NOTION_PAT` | Notion API access (personal token) | -- |
| `LLM_API_URL` | AI summaries + chat | -- |
| `NTN_BIN` | Notion Workers CLI | ntn |

One of `NOTION_TOKEN` or `NOTION_PAT` is required. Can also be set via the web dashboard Settings page.

## Project Structure

```
server.py              -- FastMCP + FastAPI entry point
notion_mcp/            -- Python modules (client, pages, databases, etc.)
  skills/              -- FastMCP skill definitions
  rag/                 -- LanceDB vector pipeline
web_sota/              -- React web dashboard
native/                -- Tauri 2.0 desktop wrapper (NSIS build)
docs/                  -- Additional documentation
```

## Learn More

- [About Notion](docs/about-notion.md) — history, community, usage stats
- [Note Apps Comparison](docs/note-apps-comparison.md) — Notion vs Obsidian vs others
- [llms-full.txt](llms-full.txt) — full technical reference
- [INSTALL.md](INSTALL.md) — detailed setup guide

## License

MIT
