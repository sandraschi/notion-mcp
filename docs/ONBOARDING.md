# notion-mcp — Onboarding

First-timer path: install → token → verify. ~5 minutes.

## 1. Install & launch

```powershell
git clone https://github.com/sandraschi/notion-mcp
cd notion-mcp
just bootstrap
just dev
```

Open the dashboard: http://127.0.0.1:10810 (backend :10811).

## 2. Connect Notion (required)

Online account needed: a Notion account with permission to create integrations.

1. Go to https://www.notion.so/my-integrations → **New integration**,
   name it (e.g. `NotionMCP`), copy the **Internal Integration Token**.
2. In the dashboard open **Settings** (or the Connect screen) and paste the
   token — no `.env` editing needed. It is stored in the gitignored
   `exports/notion_token.txt`.
3. Alternatively set `NOTION_TOKEN` (or `NOTION_PAT`) in a root `.env`.
4. Share at least one page/database with the integration inside Notion
   (otherwise search returns nothing — this is the #1 first-run pitfall).

Verify: Status page shows Notion connected, or
`GET http://127.0.0.1:10811/api/status` → `"authenticated": true`.

## 3. Optional: local LLM

Start Ollama (`:11434`) or LM Studio (`:1234`) for RAG chat + summaries.
The Settings page auto-detects providers; without one, chat endpoints return
RAG context with `declared_fallback: true` (still useful).

## 4. Try it

- Dashboard → Explorer → search your workspace.
- Dashboard → AI Chat → ask about your content.
- MCP: `search_notion_knowledge(query="...", mode="hybrid")`.

## Sanity check

- Backend dot green + `/api/health` → `{"status":"ok"}`.
- `just test` green; `GET /api/capabilities` lists 40 tools.

## Money / cost

Notion API: free for integrations. Local LLM via Ollama: free.
No paid account required for anything in this repo.
