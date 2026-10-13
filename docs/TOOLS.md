# notion-mcp — Tools

40 MCP tools (stdio) + REST mirror at `http://127.0.0.1:10811`.
Full inventory: `GET /api/tools`, `GET /api/capabilities`, or the
`server_help` tool. Per-tool docs: `notion_mcp/skills/notion-expert/SKILL.md`.

## Portmanteau (consolidated entry points)

| Tool | Operation values |
|------|------------------|
| `manage_notion_data` | `create/retrieve/update/archive/restore` × `page/data_source/block` |
| `query_data_source` | filtered/sorted/paginated structured queries |
| `orchestrate_automation` | `setup/sync_external/report/export` |
| `orchestrate_workers` | `deploy/list/scaffold/logs/check` |
| `server_help` | inventory + pointers |
| `shutdown_server` | graceful self-termination (DESTRUCTIVE) |

## Single-purpose

- **Pages (5):** `create_page`, `update_page`, `get_page_content`,
  `search_pages`, `archive_page`
- **Databases (6):** `create_database`, `query_database`,
  `create_database_entry`, `update_database_entry`, `get_database_schema`,
  `bulk_import_data`
- **Collaboration (3):** `add_comment`, `get_comments`, `get_workspace_users`
- **RAG (2):** `sync_rag_index`, `search_notion_knowledge`
  (`semantic/keyword/hybrid`)
- **Automations (4):** `setup_automation`, `sync_external_data`,
  `generate_ai_summary`, `export_workspace_data`, plus `import_workspace_data`
- **Webhooks (2):** `verify_webhook`, `list_webhook_events`
  (inbound: `POST /api/webhooks/notion`, list: `GET /api/webhooks/events`)
- **Workers (6, need `ntn` CLI):** `deploy_worker`, `list_workers`,
  `scaffold_worker`, `worker_logs`, `check_ntn`
- **Blocks/Markdown (6):** `append_blocks`, `update_block`, `delete_block`,
  `get_page_markdown`, `update_page_markdown`, `update_database_schema`

## REST (webapp + direct integration)

`GET /api/health` (+ `/health` alias), `GET /api/status`,
`GET /api/capabilities`, `GET /api/v1/diagnostics`, `GET /api/recent`,
`GET /api/page/{id}`, `/api/page/{id}/markdown`, `/api/page/{id}/blocks`,
`PATCH /api/database/{id}/schema`, `POST /api/search`, `POST /api/chat`,
`POST /api/llm/chat` (+ `GET /api/llm/models`, `/api/llm/discovery`,
`/api/llm/providers`, `/api/llm/onboarding`), `GET /api/skills`,
`GET /api/logs` (+ export, DELETE), `GET /api/plugins`,
`POST /api/plugins/install/{id}` (declared simulation),
`POST /api/configure/token`, `GET /api/export`, `POST /api/import`,
`POST /api/shutdown`, `/mcp` (streamable HTTP).

## Declared fallbacks (not mocks)

- `POST /api/chat` / `/api/llm/chat` without a reachable LLM return RAG
  context + stub reply with `declared_fallback: true`.
- Plugin install writes a stub module and reports `simulated: true`.
