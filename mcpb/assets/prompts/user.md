# notion-mcp - User Guide

notion-mcp connects your Notion workspace to AI assistants and to a local web
dashboard. Through it you can find anything in your workspace, create and edit
pages, run databases, discuss with comments, back everything up, and automate
workflows - from chat ("find my roadmap") or from code (41 MCP tools).

## Install and launch

Clone, bootstrap, launch: `git clone
https://github.com/sandraschi/notion-mcp`, `cd notion-mcp`,
`just bootstrap`, `just dev`. Open the dashboard at
http://127.0.0.1:10810 (backend API on :10811). Backend-only mode:
`just serve` or `uv run python server.py --http --port 10811`. Claude
Desktop mode: `python -m notion_mcp` (stdio, the default transport).

Claude Desktop one-liner (after the first tagged release):
`irm https://github.com/sandraschi/notion-mcp/releases/latest/download/install.ps1 | iex`.

## Connect your Notion account (required, ~2 minutes)

1. Open https://www.notion.so/my-integrations, create a **New integration**,
   name it (e.g. `NotionMCP`), copy the Internal Integration Token.
2. In the dashboard open **Settings** (the Connect screen appears
   automatically while unauthenticated) and paste the token - nothing to edit
   by hand; it is stored in the gitignored `exports/notion_token.txt`.
   Alternative: set `NOTION_TOKEN` (or `NOTION_PAT`) in a root `.env`.
3. Inside Notion, **share at least one page or database with the
   integration** (Share -> invite the integration). This is the number-one
   first-run pitfall: with zero shared pages every search returns nothing.
4. Verify on the Status page (Notion: connected) or
   `GET http://127.0.0.1:10811/api/status` -> `"authenticated": true`.

Optional local AI: start Ollama (`:11434`) or LM Studio (`:1234`). Settings
auto-detects providers and models, remembers your choice, and chat/summaries
use it. Without any LLM, chat still works off retrieved context and says so
(`declared_fallback: true`).

## How to use each tool

Pages. `create_page`: give a title and optional text; add `parent_id` to
nest under a page or database, `properties` for database rows, `children`
for raw blocks. `update_page`: pass only what changes (`title`, `content`,
`properties`, `archived`); the reply lists `updated_fields`. `get_page_content`:
full page plus nested blocks (tune `block_depth`, default 10, for huge
trees). `search_pages`: keyword search sorted by edit/creation time; combine
with `filter_by_type` (`page`/`database`). `archive_page`: archives by
default; `permanent_delete: true` destroys (keep `backup_first: true`).
Prefer the portmanteau `manage_notion_data` when a task mixes create, read,
update, and archive across pages, data sources, and blocks - one tool, an
`operation` plus `entity_type`, fewer round trips.

Databases. `create_database`: needs a parent page ID and a property schema
mapping names to Notion types (title, rich_text, number, select,
multi_select, date, checkbox, url, email, people, relation, files).
`query_database`: filter/sort/paginate (`limit` default 100, follow
`next_cursor` while `has_more`). `create_database_entry`: one row with
typed properties. `update_database_entry`: patch properties, content, or
archive flag (properties optional). `get_database_schema`: inspect types
before writing code against a base (add `include_statistics` for usage).
`bulk_import_data`: hand it CSV/JSON text plus a source-to-target `mapping`;
check `successful_imports/total_records`, then `query_database` to verify.

Search and knowledge. `search_notion_knowledge`: `semantic` consults your
local vector index (meaning-based), `keyword` hits the Notion API (exact),
`hybrid` merges both - the default choice when unsure. `sync_rag_index`:
(open Settings aside) indexes the workspace to LanceDB; pass specific data
source IDs to limit scope, `force_rebuild: true` to start over. Search first,
read second, summarize third.

Collaboration. `add_comment` (thread with `parent_comment_id`),
`get_comments` (filter resolved, sort, limit), `get_workspace_users`
(members, types, activity).

Automations. `setup_automation`: records trigger+conditions+actions and
returns the exact Notion UI steps to create the matching webhook
subscription - triggers include page/datastore lifecycle and comment
events. `verify_webhook`: paste the token Notion shows; the handshake then
completes and `list_webhook_events` shows traffic. `sync_external_data`:
REGISTERS csv/json/github/rss syncs (persisted under `exports/`); live
polling is not implemented, so load with `bulk_import_data`.
`orchestrate_automation`: single entry for setup/sync_external/report/export.

AI and backup. `generate_ai_summary`: needs `LLM_API_URL`, else an
extractive fallback; pick `summary_type` (comprehensive/brief/bullets),
`length`, and `focus_areas`. `export_workspace_data`: scope + format +
metadata + compression knobs for backups. `import_workspace_data`: load a
local Markdown/JSON file under a Notion parent.

Workers. Install the `ntn` CLI first (`check_ntn` verifies). Then
`scaffold_worker` -> `deploy_worker` -> `worker_logs` -> `list_workers`, or
drive all five through `orchestrate_workers`.

Blocks and markdown. `append_blocks` / `update_block` / `delete_block`
(soft archive) for surgical edits; `get_page_markdown` /
`update_page_markdown` for Markdown round-trips on API 2026-03-11;
`update_database_schema` for title/properties/description changes.

Utility. `server_help`: full inventory when you wonder what's available.
`shutdown_server`: graceful self-termination (confirm first; restart after).

## Dashboard walkthrough

Explorer: recent content plus keyword search and an inline page viewer
(blocks or Markdown view, open-in-Notion links). Semantic Search: meaning
search with relevance scores. AI Chat: personalities (Research Assistant,
Expert Reviewer, Quick Summarizer, Custom), speech input/output, skill-aware
system prompts, history persisted locally (100 cap), export/clear. Tools:
live registry from the backend. Settings: token + connection status, LLM
provider/model selects (persisted), app info. Status: request/error/success
telemetry, service dots, detected LLMs. Logging: ring-buffer viewer with
level/kind/search filters and CSV/JSON export. Help: bundled guides.
Plugins: install/available registry (installs are declared simulations).

## Troubleshooting FAQ

Empty search? Share pages with the integration; check Status. Token
rejected? Regenerate at my-integrations and re-paste in Settings. Chat says
fallback? Start Ollama/LM Studio or set `LLM_API_URL`. RAG finds nothing?
Run `sync_rag_index` and wait for the sweep. Port busy? Only one backend
may own :10811 - stop the other (the launcher does not zombie-clear yet).
Dashboard blank from another machine? Use same-origin (the app proxies
`/api`); absolute 127.0.0.1 URLs only work on localhost (fixed in 1.2.0).
`ntn` tools fail? Install the CLI (`NTN_BIN` override supported). Rate
limits? Slow down, batch imports, paginate. Webhook never verifies? Create
the subscription in Notion's UI first, then `verify_webhook`.

## Advanced patterns (ten runbooks)

1. Weekly review briefing. Hybrid-search last week's topics, read the top
five pages, generate one summary per page, then create a "Weekly Review"
page with the briefs as children blocks. Archive last week's review page to
keep exactly one live.
2. Meeting-notes pipeline. Create a database with Name/Date/Attendees/Status
properties. After each meeting, create an entry, append blocks with decisions,
comment action items with mentions via rich_text, and query Status=Open
every Monday.
3. Research library. One database (Title, Authors, Year, Topics, Rating).
Bulk-import a CSV of papers, query by topic, summarize the best three, and
export the workspace monthly as backup.
4. Content migration. Export the old scope to JSON, transform field names
with `mapping`, bulk-import into the new database, query counts on both
sides, archive (don't delete) the old pages after a week.
5. Comment triage. `get_comments` per active page, resolve threads in Notion,
re-list with `include_resolved` to confirm zero open, summarize blockers to
the team page.
6. Webhook-driven log. setup_automation (page_created) -> subscription in the
UI -> verify -> poll `list_webhook_events` daily; export events weekly.
7. Worker status page. `check_ntn`, scaffold, deploy, then `worker_logs`
with tail 20 into a monitoring page; re-deploy on config change.
8. RAG hygiene. `sync_rag_index` after big imports; `force_rebuild` quarterly
or after renames; spot-check with three known queries (one per mode).
9. Multi-page refactor. Search the topic, read every hit, update titles and
properties for consistency, move stale pages under an Archive parent,
export before starting.
10. Backup drill. Monthly: `export_workspace_data` (workspace scope, JSON,
metadata on, compression on); verify the artifact opens and counts match
`query_database` totals; store off-machine.

## REST cookbook (curl against :10811)

Health: `curl localhost:10811/health`. Status:
`curl localhost:10811/api/status`. Capabilities:
`curl localhost:10811/api/capabilities`. Recent pages:
`curl "localhost:10811/api/recent?limit=5"`. Read a page:
`curl localhost:10811/api/page/<id>`. Semantic search:
`curl -X POST localhost:10811/api/search -H "Content-Type: application/json" -d '{"query":"roadmap"}'`.
Chat: `curl -X POST localhost:10811/api/chat -H "Content-Type: application/json" -d '{"message":"summarize my week"}'`.
LLM chat (OpenAI-style):
`curl -X POST localhost:10811/api/llm/chat -H "Content-Type: application/json" -d '{"messages":[{"role":"user","content":"hi"}]}'`.
Models: `curl "localhost:10811/api/llm/models?provider=ollama"`.
Onboarding facts: `curl localhost:10811/api/llm/onboarding`. Tools:
`curl localhost:10811/api/tools`. Skills:
`curl localhost:10811/api/skills`. Logs:
`curl "localhost:10811/api/logs?limit=20&level=ERROR"`. Save a token:
`curl -X POST localhost:10811/api/configure/token -H "Content-Type: application/json" -d '{"token":"ntn_..."}'`.
MCP endpoint: `http://127.0.0.1:10811/mcp` (streamable HTTP; use an MCP
client, not curl). Shutdown (restarts backend!):
`curl -X POST localhost:10811/api/shutdown`.

## Extended FAQ

Can I use this without the dashboard? Yes - stdio mode (`python -m
notion_mcp`) exposes all 40 tools to Claude Desktop; REST is only needed for
the web UI and scripts. Can two people share one server? The token is
per-integration; sharing the server shares the workspace view. Use separate
`.env` files/backends for separate workspaces. Does sync handle deletions?
Archive events flow through webhooks; RAG rebuilds pick up deletions on
`force_rebuild`. What breaks on API version bumps? Block/markdown shapes;
check `NOTION_VERSION` and the changelog. Where is my data? Notion cloud
(source of truth), LanceDB under `.lancedb/` (derived index, safe to wipe),
`exports/` (token, backups, registrations - private, gitignored). How do I
move machines? Copy `.env`/token, `just bootstrap`, `just dev`, re-share
nothing (sharing lives in Notion).

## Tool cookbook A-Z (concrete calls)

`manage_notion_data(operation="create", entity_type="page", title="Neu",
parent_id="page-0")` creates a nested page and returns its id and URL. Swap
operation to `retrieve` with `entity_id` to read, `update` with new fields
to patch, `archive` to shelve. For databases use entity_type `data_source`
with title plus parent_id. Tip: validate title/parent presence errors by
reading the returned `error` string - it names the missing field.

`query_data_source(data_source_id="ds-1", filter={"property": "Status",
"select": {"equals": "Done"}}, sorts=[{"property": "Name", "direction":
"ascending"}], limit=25)` returns matching rows; follow `next_cursor` while
`has_more` is true. Tip: build filters incrementally - one condition first,
then nest with and/or.

`search_notion_knowledge(query="Q3 roadmap", mode="hybrid", limit=8)`
merges vector and keyword hits. Use `semantic` for "documents about...",
`keyword` for exact titles you half-remember, `hybrid` as the default. Tip:
RAG answers need a prior `sync_rag_index` after big imports.

`sync_rag_index(data_source_ids=["ds-1"])` scopes the sweep; omit for a
full scan; `force_rebuild=True` wipes first. The call returns at once -
wait a minute, then search. Tip: scope sweeps while iterating, full-scan
overnight.

`server_help()` with no arguments returns the live inventory (41 tools),
URLs, and pointers. Call it whenever a new session starts so capabilities
are grounded, not guessed. Tip: paste its tool list into your notes.

`shutdown_server()` with no arguments stops the backend in ~500 ms after
replying. Confirm with the user first; restart via `just serve` or the
launcher afterwards. Tip: prefer it over killing the process.

`create_page(title="Neu", content="Hallo", parent_id="page-0")` nests a
page; omit parent for workspace root; pass `children` block objects for
rich layouts, `properties` for database rows. Tip: create the parent first
and use the returned id downstream.

`update_page(page_id="p-1", title="Neu")` patches only given fields and
reports `updated_fields`. Pass `archived=True` to shelve. Tip: read before
writing when unsure of current content.

`get_page_content(page_id="p-1", include_children=True, block_depth=10)`
dumps page plus tree. Lower depth for huge pages, then drill into children.
Tip: depth 2-3 is enough for triage.

`search_pages(query="urlaub", filter_by_type="page",
sort_by="last_edited_time", limit=10)` is the fast keyword path. Tip: sort
by `created_time` when hunting something new.

`archive_page(page_id="p-9")` shelves safely; add `permanent_delete=True`
(keep `backup_first=True`) only for real destruction. The reply states the
`action`. Tip: export first for anything irreproducible.

`create_database(title="DB", parent_id="page-0", properties_schema={"Name":
{"title": {}}})` plus optional `icon`/`cover`. Design the schema before
loading rows - types are sticky. Tip: prototype with three properties, grow
later via `update_database_schema`.

`query_database(database_id="ds-1", limit=100)` pages with cursor; filter
and sort like `query_data_source`. Tip: mirror every bulk import with a
count query afterwards.

`create_database_entry(database_id="ds-1", properties={"Name": {"title":
[{"text": {"content": "Eintrag"}}]}})` writes one typed row; `content`
adds body text. Tip: validate property names against
`get_database_schema`.

`update_database_entry(page_id="p-5", properties={...})` patches rows;
omit properties for content/archived-only edits. Tip: the reply echoes
`updated_properties` - diff it.

`get_database_schema(database_id="ds-1", include_statistics=True)` shows
types plus usage. Call before coding against an unfamiliar base. Tip:
`property_details=False` for a compact overview.

`bulk_import_data(database_id="ds-1", data_source="[...]", mapping={"Name":
"Name"})` loads CSV/JSON; check `successful_imports/total_records`. Tip:
import 5 rows first, verify, then the full file.

`add_comment(page_id="p-1", content="Hallo")`, thread with
`parent_comment_id`, format with `rich_text`. Tip: comments beat page edits
for discussion (history preserved).

`get_comments(page_id="p-1", include_resolved=False, limit=50)` lists
threads; flip `include_resolved` for audits. Tip: sort oldest-first for
follow-ups.

`get_workspace_users()` lists members; filter `permission_level`, include
inactive for offboarding reviews. Tip: re-check after team changes.

`setup_automation(trigger_type="page_created", conditions={},
actions=[{"type": "notify"}])` records the automation and returns the
Notion UI steps; add `webhook_url` to prefill. Tip: create the UI
subscription the same day or the record goes stale.

`sync_external_data(external_source="csv", sync_config={"path":
"data.csv"})` registers the sync (csv/json/github/rss); load via bulk
import - polling is not implemented. Tip: keep registrations small and
named by source.

`generate_ai_summary(page_id="p-1", summary_type="comprehensive",
length="medium", focus_areas=["Termine"])` needs `LLM_API_URL`, else an
extractive fallback. Tip: brief+short for triage, comprehensive+bullets
for handoffs.

`export_workspace_data(scope="workspace", format="json")` backs up with
metadata; tune scope/format/compression per need. Tip: monthly full
exports, off-machine copies.

`import_workspace_data(source_path="data.json",
target_parent_id="page-0", import_type="json")` loads files under a parent.
Tip: dry-run with 3 rows first.

`orchestrate_automation(operation="export", config={"scope": "workspace"})`
routes setup/sync_external/report/export through one entry. Tip: use it
from scripts to avoid tool-switching.

`verify_webhook(verification_token="tok-1")` completes the Notion handshake
after UI subscription. Tip: tokens expire - verify promptly.

`list_webhook_events(limit=50)` tails stored events; filter `event_type`
for noise. Tip: poll daily, export weekly.

`deploy_worker(project_dir=".")`, `list_workers()`,
`scaffold_worker(project_dir="./w")`, `worker_logs(tail=20)`,
`check_ntn()`, `orchestrate_workers(operation="check")` - run `check_ntn`
first; without the CLI everything else fails clearly. Tip: pin `NTN_BIN`
per machine.

`append_blocks(block_id="p-1", children=[...])` adds blocks; `update_block`
patches type/content/archived; `delete_block` soft-archives. Tip: prefer
blocks for surgery, markdown for rewrites.

`get_page_markdown(page_id="p-1")` and
`update_page_markdown(page_id="p-1", markdown="# Neu")` round-trip Markdown
(API 2026-03-11). Tip: keep a local .md copy of critical pages.

`update_database_schema(database_id="ds-1", title="Neu")` renames;
`properties` adds/removes/modifies; `description` documents. Tip: snapshot
the old schema via `get_database_schema` first.

## Power workflows (five end-to-end scripts)

A. New-hire onboarding base. Create a parent page "Team Hub", one database
("People": Name, Role, Start, Buddy), one database ("Docs": Title, Topic,
Owner). Bulk-import the roster CSV, create five starter docs, comment each
with its owner, export the scope as the golden backup. Time: 30 minutes.
Verify: two databases queryable, five docs readable, one export artifact.

B. Content audit. Hybrid-search the ten most-edited topics, read each top
hit, tag stale pages (Status=Archive), move them under an Archive parent,
update titles for consistency, export before and after. Verify: zero pages
with pre-audit titles in the active tree, two export artifacts.

C. Launch checklist tracker. Database (Task, Owner, Due, Status, Link).
Bulk-import the checklist, assign owners via people properties, comment
blockers daily, query Status!=Done every morning, summarize to leadership
weekly with `generate_ai_summary` on the tracker page. Verify: morning
query under a minute, Friday brief posted.

D. Knowledge base seeding. Gather source files (Markdown/JSON), import each
under the right parent with `import_workspace_data`, run `sync_rag_index`
scoped to the new data sources, spot-check with ten known questions (one
per topic), force-rebuild once, re-check. Verify: 10/10 spot checks hit.

E. Incident log. Database (Time, Service, Severity, Summary, Link). Append
entries as incidents happen, comment timeline updates, query Severity=High
weekly, export monthly. Verify: entries append in under a minute, weekly
query returns the right slice.

## Keyboard, accessibility, and display

Dashboard keyboard: Ctrl+Scroll zooms, Ctrl+0 resets, Ctrl+L toggles the
logger, Ctrl+H toggles help, Ctrl+K focuses search. Chat: Enter sends,
Shift+Enter newline; mic button for speech input where supported; speaker
icons read replies aloud. Status dots (green/red/gray) mirror backend, auth,
and LLM state - any red dot links to its fix (token, backend, or model).
Text meets contrast minimums (slate-300+ on dark); tiny labels are metadata
only, never body copy. The onboarding cue under the hero appears exactly
when no content is reachable (unauthenticated or unshared).

## Glossary for new users

Workspace: your Notion account content. Integration: the API credential you
create at my-integrations. Share: granting the integration access to a page
(required per page). Database (data source): a structured table. Entry: one
row. Property: a typed column. Block: a content chunk. Token: the secret
string (never share screenshots of it). RAG: meaning-based search over your
synced copy. LanceDB: the local vector store. Portmanteau: one tool with an
operation verb. Stdio: Claude Desktop pipe mode. SSE: streaming chat
updates. Prefab: rich in-chat cards.

## Migration guides (from other tools)

From Evernote. Export notebooks to ENEX, convert to Markdown (any ENEX
converter), `import_workspace_data` per notebook under a dated parent,
`sync_rag_index` scoped to the new sources, spot-check ten notes, archive
the imports only after a month of daily use. Tags become a multi-select
property via `mapping` in a second bulk pass. Verify: note counts match per
notebook, attachments listed, search hits both old titles and new text.

From Confluence. Export spaces to HTML/Word, convert to Markdown, import
per space, rebuild the page tree with `parent_id` nesting (Confluence
hierarchy maps cleanly), migrate labels to select properties, re-link
attachments manually (paths change). Verify: hierarchy depth matches, labels
present, top-20 pages spot-read.

From Obsidian. The vault is already Markdown: `import_workspace_data` per
folder, `[[wikilinks]]` need manual conversion to Notion links (note the
count first), frontmatter becomes properties via `mapping`, daily notes go
to a dated database. Verify: link count before/after, frontmatter keys as
properties, graph-central notes readable.

## Team playbook

Roles: one integration owner (token + sharing), editors (pages/entries),
viewers (comment-only). Permissions mirror in Notion sharing, not in this
server. Cadence: Monday query of open items, Wednesday comment triage,
Friday brief export. Reviews: quarterly schema review (`get_database_schema`
diffs), monthly backup drill, weekly webhook event skim. Offboarding: share
away pages, `get_workspace_users(include_inactive=True)` to confirm, rotate
the token if the owner leaves. Onboarding a teammate: share the hub,
walk Settings once, assign three starter pages, confirm their first search
hits. Escalation: red Status dot -> token/backend/model in that order;
data loss -> exports first, then ask.

## Performance tuning

Keep pages under a few hundred blocks (split mega-pages yearly). Query with
`limit` 25-50 for interactive use, 100+ for batch. RAG: scope sweeps to
changed sources; full rebuilds quarterly. Chat: short focused questions
beat wall-of-text prompts (smaller context, faster local inference).
Exports: compress, scope down, off-machine. Backend: one instance per token;
restart weekly via `/api/shutdown` + launcher. Dashboard: Explorer over
full-text only when needed; semantic search for discovery. If the UI lags,
check Status telemetry (error rate, LLM latency) before blaming content.

## Security and privacy guide

Threat model: your Notion content is the asset; the token is the key; this
server, the dashboard browser tab, and export files are the attack surface.
Rules: never paste the token anywhere except Settings/`.env`; never commit
`.env` or `exports/` (both gitignored — verify with `git status` before
every commit); never screenshot Settings with the token visible; rotate the
token the day anyone with access leaves. The backend never logs token
material; if you see one in Logging, treat it as a bug and report it with
the version. Exports contain live content — encrypt off-machine copies.
`permanent_delete` is unrecoverable by design; the server cannot undo it, so
exports precede it. Webhook endpoints accept Notion-signed traffic; do not
expose :10811 to the internet without a reverse proxy, auth, and TLS — LAN
use is the supported shape (Tailscale recommended for remote). Review
`list_webhook_events` for unexpected sources monthly.

## Automation cookbook (five recipes)

New-page notifier. `setup_automation(trigger_type="page_created",
conditions={}, actions=[{"type":"notify"}])`, create the UI subscription,
`verify_webhook`, watch events. Test by creating a scratch page, then
archive it. Comment digest. `get_comments` across five active pages nightly,
append open threads to a digest page, resolve in Notion, re-list to confirm
zero. Status rollup. `query_database` Status!=Done each morning, post counts
to the team page, `generate_ai_summary` Fridays. Backup rotation. Monthly
`export_workspace_data` full scope, verify artifact, prune quarters older
than a year (export first). Stale-hunter. Quarterly hybrid search for
"draft/TODO/WIP", read hits, archive or finish each, re-export after.

## Workers end-to-end tutorial

Goal: a nightly sync worker. 1) `check_ntn` (install CLI if absent).
2) `scaffold_worker(project_dir="./nightly-sync")`. 3) Edit the scaffold
(entrypoint + schedule per ntn docs). 4) `deploy_worker` from the dir.
5) `worker_logs(tail=30)` to confirm first run. 6) `list_workers` to see
status. 7) On config change: edit, redeploy, re-check logs. 8) To retire:
archive the project dir and remove the schedule in ntn. Drive steps 4-6 via
`orchestrate_workers` once comfortable. Troubleshoot: CLI missing (install),
auth errors (token), schedule silent (logs first, config second).

## Reference: every REST endpoint (method, path, purpose)

`GET /health` - launcher liveness alias (200 + uptime). `GET /api/health` -
same for humans and monitors. `GET /api/status` - authenticated flag,
workspace name, server liveness. `GET /api/capabilities` - identity,
transports, 40 tool names, feature flags (start integrations here).
`GET /api/v1/diagnostics` - tools, versions, system, error list (smoke
tests). `GET /api/recent?limit=N` - latest pages/databases. `GET
/api/page/{id}` - page metadata + text blocks. `GET/PUT
/api/page/{id}/markdown` - Markdown round-trip. `POST
/api/page/{id}/blocks` - append children. `PATCH
/api/page/{id}/blocks/{block_id}` - patch one block. `DELETE same` -
archive one block. `PATCH /api/database/{id}/schema` - mutate schema.
`POST /api/search` (`{"query"}`) - semantic search. `POST /api/chat`
(`{"message"}`) - RAG chat with declared fallback. `POST /api/llm/chat`
(`{"messages"}`) - OpenAI-style proxy (Ollama first, fallback flagged).
`GET /api/llm/models?provider=` - live or curated model list. `GET
/api/llm-discovery` - Ollama/LM Studio auto-detect. `GET /api/llm/providers`
- registry with detected/configured flags. `GET /api/llm/onboarding` -
starter facts for the dashboard cue. `GET /api/skills` - skill names/paths.
`GET /api/logs` (+limit/offset/level/kind/search/sort) - ring buffer.
`GET /api/logs/export?format=` - JSON/CSV download. `DELETE /api/logs` -
clear buffer. `GET /api/plugins` - registry. `POST
/api/plugins/install/{id}` - declared-simulation install. `POST
/api/configure/token` (`{"token"}`) - save credential, returns auth state.
`GET /api/export?format=` - download backup. `POST /api/import`
(`{"file_path","target_id"}`) - load file. `GET /api/docs/{name}` - bundled
markdown as text. `GET /api/stats` - workspace telemetry. `GET /api/tools`
- live MCP tool names. `POST /api/webhooks/notion` - Notion event receiver.
`GET /api/webhooks/events` - stored events. `POST /api/shutdown` - orderly
exit in ~500 ms (restarts the backend - confirm first). `/mcp` - MCP
streamable HTTP for clients. `/docs`, `/redoc`, `/openapi.json` - FastAPI
auto-docs (explore interactively).

You now know everything the bundle contains. Start with Settings (token),
verify Status, search once, and build from there.

## Dashboard pages deep-dive (eleven pages)

Dashboard: hero with tool count, quick links (Explorer/Chat/Tools),
onboarding cue when empty, recent-content grid (18 max, search/filter,
per-item open). Use it as home base; the cue is the fastest path from
install to value. Explorer: keyword search box, type filter, results list,
click-to-viewer with Blocks/Markdown toggle, open-in-Notion links,
per-page block counts. Use it for navigation and triage. Semantic Search:
concept box, relevance percentages, result cards with source snippets. Use
it for discovery ("find things about X"). AI Chat: personality select
(4 incl. Custom with its own prompt box), provider dot, skill badge,
example prompts, mic/speech, persisted history (100), export/clear. Use it
for Q&A and briefs. Tools: live registry table from `/api/tools` with
descriptions; empty state when backend is down. Use it to confirm wiring.
Settings: token card (password input, save, connection result, docs link),
LLM card (provider/model selects, persisted, auto-detected), app-info card
(version, transports, ports). Use it first after install, rarely after.
Status: KPI cards (requests, errors, success rate, LLMs found), service
rows (backend port state, Notion label), local-LLM list with endpoints. Use
it to diagnose ("why is nothing working"). Logging: level/kind/search
filters, limit/offset pager, tail toggle, clear with confirm modal, JSON/CSV
export. Use it after any failure. Help: tabbed bundled guides (docs served
by `/api/docs`). Use it before asking for help. Data: export picker
(format select, download) and import form (file path + target). Use monthly
for backups. Plugins: installed vs available lists, one-click declared
installs. Use it to extend carefully.

## Quick reference card (print this)

Ports: dashboard :10810, backend :10811. Health: `/health`. Auth:
`NOTION_TOKEN` or Settings paste + share pages. Search: hybrid default,
semantic for meaning, keyword for titles. Read: `get_page_content`, depth
10 max. Write: `create_page` (title+parent), `update_page` (patch subset).
Tables: `create_database` (schema first), `query_database` (cursor pages),
`bulk_import_data` (map, 5-row trial, count-verify). Talk: comments beat
edits for discussion. Backup: monthly full export off-machine. Automate:
record via tool, subscribe via Notion UI, verify token, watch events.
Summarize: `LLM_API_URL` or fallback. Workers: `check_ntn` first. Markdown:
round-trip critical pages locally. Delete: export, archive, wait, destroy.
Debug order: Status dots, `/api/health`, logs (ERROR filter), token,
sharing, ports, LLM. Restart: `POST /api/shutdown` + launcher (never
taskkill). Upgrade: pull, sync, test, restart, verify capabilities. Move
machines: token, bootstrap, dev, no re-share. Costs: Notion API free for
integrations; Ollama free; no paid account needed. Limits: ~3 req/s,
paginate everything, depth caps, cursors. Flags: `declared_fallback` and
`simulated` mean degraded-but-honest - relay them, never launder.

## First-week checklist (do these in order)

Day one: install, paste token, share three pages, confirm Status green, run
one hybrid search. Day two: create a scratch page, update it, comment on it,
archive it (learn the lifecycle where nothing matters). Day three: build one
real database with a proper schema, import ten rows, query them back. Day
four: run `sync_rag_index`, ask chat five known questions, note misses. Day
five: full `export_workspace_data`, verify the artifact, store it
off-machine. Weekend: set up one automation end-to-end (record, subscribe,
verify, watch one event). Following week: onboard real content, schedule the
monthly backup drill, and re-read the runbook that matches your heaviest
workflow. If any step fails, the FAQ and Status page resolve ninety percent
of cases; the rest belong in a bug report with version, tool, arguments, and
telemetry attached. Done right, the workspace starts answering questions
before you finish asking them.
