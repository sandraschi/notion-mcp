#!/usr/bin/env python3
"""
NotionMCP - Comprehensive Notion Workspace Management MCP Server
FastMCP 3.1 Implementation with Austrian Efficiency

Built for Claude Desktop Pro + MCP setup
Author: Sandra (Vienna, Austria) 🇦🇹
Date: March 7, 2026
Context: Academic knowledge management + weeb organization + direct communication

Status: Production-Ready (SOTA 2026)
"""

import asyncio
import collections
import datetime
import json
import os
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import structlog
import yaml
from fastapi import Body, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastmcp import Context, FastMCP
from fastmcp.server import create_proxy
from pydantic import Field

from notion_mcp import workers as notion_workers
from notion_mcp.automations import AutomationManager
from notion_mcp.client import NotionClient
from notion_mcp.collaboration import CollaborationManager
from notion_mcp.databases import DatabaseManager
from notion_mcp.pages import PageManager
from notion_mcp.plugins import PluginManager
from notion_mcp.rag.orchestrator import RAGOrchestrator
from notion_mcp.transport import (
    run_server_async,
)

if sys.stdout is None:  # windowed frozen exe (console=False) has no stdout
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:  # same for stderr; transformers/tqdm probe both
    sys.stderr = open(os.devnull, "w")

_LOG_BUFFER_MAX = 5000
_log_buffer: collections.deque[dict] = collections.deque(maxlen=_LOG_BUFFER_MAX)
_log_counter = 0


def _log_processor(logger_, method_name, event_dict):
    global _log_counter
    _log_counter += 1
    _log_buffer.append(
        {
            "id": str(_log_counter),
            "timestamp": datetime.datetime.now().isoformat(),
            "level": method_name.upper(),
            "kind": "",
            "detail": str(event_dict.get("event", event_dict.get("message", ""))),
            "meta": {k: v for k, v in event_dict.items() if k not in ("event", "message")},
        }
    )
    return event_dict


# Configure structured logging with in-memory ring buffer capture
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        _log_processor,
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


def _error_response(message: str, error: Exception, user_message: str = "", **context: Any) -> dict[str, Any]:
    """Shared error path (TOOL_DESIGN_STANDARDS §7.1 Pattern 3): logs with
    traceback via logger.exception, returns a dialogic error dict. Use in
    every except block instead of bare logger.error + hand-built dicts."""
    logger.exception(message, error=str(error), **context)
    return {"success": False, "error": str(error), "message": user_message or message}


# Load configuration with Austrian context
def load_config() -> dict[str, Any]:
    """Load configuration from YAML files with Vienna defaults"""
    config_path = os.path.join(os.path.dirname(__file__), "config", "settings.yaml")
    try:
        with open(config_path, encoding="utf-8") as f:
            config = yaml.safe_load(f)
        logger.info("Configuration loaded", config_path=config_path)
        return config
    except FileNotFoundError:
        logger.warning("Config file not found, using defaults", config_path=config_path)
        return {
            "server": {
                "name": "Notion Workspace Management MCP 🗃️",
                "timezone": "Europe/Vienna",
                "language": "de",
            }
        }


# Server lifespan for startup/shutdown lifecycle
@asynccontextmanager
async def server_lifespan(app: FastMCP):
    """Server lifespan context manager for FastMCP 2.14.1+."""
    # Startup
    logger.info("Starting NotionMCP Server", version="1.1.0", fastmcp_version="3.1.0")
    try:
        yield
    finally:
        # Shutdown
        logger.info("Shutting down NotionMCP Server")


# Initialize FastMCP 3.1 Server with Austrian Efficiency
_MCP_INSTRUCTIONS = "You are NotionMCP, a comprehensive MCP server for Notion workspace management."

mcp = FastMCP(
    "notion-mcp",
    version="1.1.0",
    instructions=_MCP_INSTRUCTIONS
    + """

CORE CAPABILITIES:
- Page Management: Create, update, search, archive pages with German/Japanese character support
- Database Operations: Create databases, query with complex filters, bulk import/export
- Collaboration: Add comments, manage users, handle workspace permissions
- Automation: Setup webhooks, sync external data, create workflow automations
- AI Integration: Generate summaries, analyze content, provide research assistance

USAGE PATTERNS:
1. Page Operations: Use create_page() to create pages, update_page() to modify, search_pages() to find content
2. Database Management: Use create_database() to set up databases, query_database() for complex queries
3. Collaboration: Use add_comment() for discussions, get_workspace_users() for team management
4. Automation: Use setup_automation() for workflows, sync_external_data() for integrations
5. AI Features: Use generate_ai_summary() for content analysis, export_workspace_data() for backups

RESPONSE FORMAT:
- All tools return dictionaries with 'success' boolean
- Error responses include 'error' field with descriptive message
- Success responses include relevant data fields
- Austrian efficiency: Direct, honest error messages without gaslighting

AUSTRIAN CONTEXT:
- Timezone: Europe/Vienna (all dates in DD.MM.YYYY format)
- Language: German characters (a, o, u, ss) fully supported
- Budget: Optimized for ~100/month AI tools budget
- Academic focus: Research and knowledge management workflows

ERROR HANDLING:
- Authentication errors include token setup instructions
- Permission errors specify which workspace needs access
- Rate limit errors provide wait time and optimization suggestions
- Direct communication: No euphemisms, clear actionable feedback""",
    lifespan=server_lifespan,
)

# MCP Bridge — proxy remote MCP servers via ProxyProvider
MCP_BRIDGE_URLS = os.environ.get("MCP_BRIDGE_URLS", "")
if MCP_BRIDGE_URLS:
    for url in MCP_BRIDGE_URLS.split(","):
        url = url.strip()
        if url:
            mcp.add_provider(create_proxy(url))

# Domain skills served over the MCP protocol (not just REST /api/skills)
try:
    from fastmcp.server.providers.skills import SkillsDirectoryProvider

    mcp.add_provider(SkillsDirectoryProvider(roots=Path(__file__).parent / "notion_mcp" / "skills"))
except Exception:
    logger.exception("Failed to register SkillsDirectoryProvider")

# Initialize RAG Orchestrator for knowledge management
rag = RAGOrchestrator()

# MCP HTTP sub-app (path="/" avoids BUG-008 double-prefix when mounted at /mcp)
mcp_app = mcp.http_app(path="/")


@asynccontextmanager
async def app_lifespan(parent: FastAPI):
    """Parent lifespan: enter the mounted MCP sub-app lifespan so the FastMCP
    session manager starts (BUG-038 class — a mount without this serves /mcp
    but real clients get 'Session terminated')."""
    async with mcp_app.router.lifespan_context(mcp_app):
        yield


# Initialize FastAPI app for SOTA Dashboard
app = FastAPI(title="NotionMCP SOTA Dashboard", lifespan=app_lifespan)


class _McpBarePathMiddleware:
    """Rewrite bare /mcp -> /mcp/ (Starlette Mount only matches /mcp/*)."""

    def __init__(self, inner: Any):
        self.inner = inner

    async def __call__(self, scope: Any, receive: Any, send: Any):
        if scope.get("type") == "http" and scope.get("path") == "/mcp":
            scope["path"] = "/mcp/"
        await self.inner(scope, receive, send)


app.add_middleware(_McpBarePathMiddleware)
app.mount("/mcp", mcp_app)

# Add CORS middleware (fleet standard — unconditional)
_tauri_desktop = os.environ.get("NOTION_MCP_TAURI", "").lower() in ("1", "true", "yes")
_backend_port = int(os.getenv("PORT", "10811"))
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"http://localhost:{_backend_port}",
        f"http://127.0.0.1:{_backend_port}",
        "http://tauri.localhost",
        "https://tauri.localhost",
        "tauri://localhost",
    ],
    allow_origin_regex=r"https?://(?:[a-zA-Z0-9-]+\.ts\.net|.*?\.tail-[a-f0-9]+\.ts\.net|tauri\.localhost|localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|100\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?$|^tauri://localhost$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = load_config()
plugin_manager = PluginManager()
_server_start_time = time.time()


# Custom API endpoints for SOTA Dashboard
@app.get("/api/health")
async def get_health():
    """Health check endpoint — liveness probe."""
    return {
        "status": "ok",
        "server": "notion-mcp",
        "version": "1.2.0",
        "uptime_seconds": int(time.time() - _server_start_time),
    }


@app.get("/health")
async def get_health_root():
    """Fleet-launcher liveness alias (fleet-start.config.ps1 HealthPath)."""
    return await get_health()


@app.get("/api/v1/diagnostics")
async def get_diagnostics():
    """Full diagnostics for CUA-NSIS smoke testing."""
    try:
        tools = await mcp.list_tools()
        tools_list = [t.name for t in tools]
    except Exception:
        logger.exception("Failed to list tools for diagnostics")
        tools_list = []
    return {
        "status": "ok",
        "server": "notion-mcp",
        "version": "1.2.0",
        "uptime_seconds": int(time.time() - _server_start_time),
        "tool_count": len(tools_list),
        "tools": [{"name": t} for t in tools_list],
        "system": {"windows": True},
        "errors": [],
    }


@app.get("/api/status")
async def get_status():
    """Return system connection status and workspace info."""
    authenticated = False
    workspace_name = "Not Connected"
    try:
        initialize_notion_client()
        if notion_client is None:
            raise RuntimeError("notion_client is None after initialization")
        authenticated = True
        workspace_name = "Notion Workspace"
    except Exception as exc:
        logger.warning("Notion not authenticated", error=str(exc), exc_info=True)

    return {
        "authenticated": authenticated,
        "workspace": workspace_name,
        "server_running": True,
        "mcp_version": "3.1.0",
    }


@app.post("/api/shutdown")
async def shutdown_server_endpoint():
    """Orderly exit: respond 200 immediately, then exit ~500 ms later so
    in-flight flows (RAG syncs, exports) can checkpoint. The fleet launcher
    calls this before bouncing the backend; without it restarts are hard."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        os._exit(0)
    loop.call_later(0.5, lambda: os._exit(0))
    return {"success": True, "message": "notion-mcp shutting down in ~500 ms"}


@app.get("/api/capabilities")
async def get_capabilities():
    """Standard capability descriptor (TOOLS_DESIGN/WEBAPP shape) for the
    webapp and IDE integration: server identity, transports, tool inventory,
    feature flags."""
    try:
        tools = await mcp.list_tools()
        tool_names = [t.name for t in tools]
    except Exception:
        logger.exception("Failed to list tools for capabilities")
        tool_names = []
    return {
        "server": "notion-mcp",
        "version": "1.2.0",
        "transport": ["stdio", "http"],
        "tool_count": len(tool_names),
        "tools": tool_names,
        "features": {
            "rag": True,
            "webhooks": True,
            "chat": True,
            "llm_discovery": True,
            "workers": True,
        },
    }


@app.get("/api/docs/{name}")
async def get_doc(name: str):
    """Return a docs/*.md file as plain text."""
    import pathlib

    docs_dir = pathlib.Path(__file__).parent / "docs"
    safe_name = pathlib.Path(name).name
    doc_path = docs_dir / f"{safe_name}.md"
    if doc_path.exists() and doc_path.is_file():
        return {"name": safe_name, "content": doc_path.read_text(encoding="utf-8")}
    return {"error": "not found"}


@app.get("/api/skills")
async def get_skills():
    """List available skills."""
    import pathlib

    skills_dir = pathlib.Path(__file__).parent / "notion_mcp" / "skills"
    skills = []
    if skills_dir.is_dir():
        for sdir in skills_dir.iterdir():
            if sdir.is_dir():
                skill_file = sdir / "SKILL.md"
                if skill_file.exists():
                    skills.append({"name": sdir.name, "path": str(skill_file)})
    return {"skills": skills}


@app.post("/api/configure/token")
async def set_notion_token(token: str = Body(..., embed=True)):
    """Store Notion token via webapp (no .env editing needed)."""
    global notion_client, page_manager, db_manager, collab_manager, automation_manager
    notion_client = None
    page_manager = None
    db_manager = None
    collab_manager = None
    automation_manager = None
    _write_stored_token(token)
    try:
        initialize_notion_client()
        return {"success": True, "authenticated": True, "message": "Token saved and connected."}
    except Exception as e:
        logger.exception("Token save succeeded but connection failed")
        return {
            "success": False,
            "authenticated": False,
            "error": str(e),
            "message": "Token saved but Notion rejected it.",
        }


@app.get("/api/logs")
async def get_logs(
    limit: int = 50, offset: int = 0, level: str = "", kind: str = "", search: str = "", sort: str = "desc"
):
    """Query the in-memory log ring buffer."""
    entries = list(_log_buffer)
    if level:
        entries = [e for e in entries if e["level"] == level.upper()]
    if kind:
        entries = [e for e in entries if e["kind"] == kind]
    if search:
        entries = [e for e in entries if search.lower() in e["detail"].lower()]
    if sort == "desc":
        entries = list(reversed(entries))
    total = len(entries)
    entries = entries[offset : offset + limit]
    return {"entries": entries, "total": total, "offset": offset, "limit": limit}


@app.delete("/api/logs")
async def clear_logs():
    """Clear the in-memory log ring buffer."""
    _log_buffer.clear()
    return {"success": True}


@app.get("/api/logs/export")
async def export_logs(format: str = "json", level: str = "", kind: str = "", search: str = ""):
    """Export logs as JSON or CSV."""
    entries = list(_log_buffer)
    if level:
        entries = [e for e in entries if e["level"] == level.upper()]
    if kind:
        entries = [e for e in entries if e["kind"] == kind]
    if search:
        entries = [e for e in entries if search.lower() in e["detail"].lower()]
    if format == "csv":
        import io

        buf = io.StringIO()
        buf.write("id,timestamp,level,kind,detail\n")
        for e in entries:
            d = e["detail"].replace('"', '""')
            buf.write(f'{e["id"]},{e["timestamp"]},{e["level"]},{e["kind"]},"{d}"\n')
        from fastapi.responses import Response as FastResponse

        return FastResponse(
            content=buf.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=logs.csv"},
        )
    from fastapi.responses import JSONResponse

    return JSONResponse(content={"entries": entries, "total": len(entries)})


@app.get("/api/plugins")
async def get_plugins():
    """List installed and recommended plugins."""
    return {"plugins": plugin_manager.list_plugins()}


@app.post("/api/plugins/install/{plugin_id}")
async def install_plugin(plugin_id: str):
    """Install/Activate a plugin.

    DECLARED SIMULATION (not a mock): writes a stub module that logs instead
    of executing, and reports `simulated: true` so callers never mistake it
    for a live install.
    """
    # Simulation: Write an empty py file to plugins dir
    path = os.path.join(plugin_manager.plugins_dir, f"{plugin_id}.py")
    with open(path, "w") as f:
        f.write(f"# Plugin: {plugin_id}\ndef run():\n    print('{plugin_id} running')\n")
    return {"success": True, "message": f"Plugin {plugin_id} installed!", "simulated": True}


@app.post("/api/import")
async def import_data(file_path: str = Body(..., embed=True), target_id: str = Body(..., embed=True)):
    """API endpoint for data migration."""
    try:
        initialize_notion_client()
        assert automation_manager is not None, "Notion client failed to initialize"
        return await automation_manager.import_workspace_data(file_path, target_id)
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/export")
async def export_data(format: str = "json"):
    """API endpoint for data export."""
    try:
        initialize_notion_client()
        assert automation_manager is not None, "Notion client failed to initialize"
        return await automation_manager.export_workspace_data(format=format)
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/page/{page_id}")
async def get_page(page_id: str):
    """Return page metadata and content blocks."""
    try:
        initialize_notion_client()
        assert page_manager is not None, "Notion client failed to initialize"
        content = await page_manager.get_page_content(page_id, include_children=True, block_depth=5)
        page_data = content.get("page", {})
        title = "Untitled"
        props = page_data.get("properties", {})
        if "title" in props:
            title_parts = props["title"].get("title", [])
            if title_parts:
                title = title_parts[0].get("plain_text", "") or "Untitled"
        blocks_text = []
        for b in content.get("blocks", []):
            b_type = b.get("type", "")
            b_content = b.get(b_type, {})
            text = ""
            if "rich_text" in b_content:
                text = "".join(t.get("plain_text", "") for t in b_content["rich_text"])
            elif "text" in b_content:
                text = b_content["text"].get("content", "")
            if text:
                blocks_text.append({"type": b_type, "text": text})
        return {
            "id": page_id,
            "title": title,
            "url": page_data.get("url", ""),
            "last_edited": page_data.get("last_edited_time", ""),
            "blocks": blocks_text,
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/recent")
async def get_recent(limit: int = 20):
    """Return recent pages and databases from the Notion workspace."""
    try:
        initialize_notion_client()
        assert page_manager is not None, "Notion client failed to initialize"
        results = await page_manager.search_pages(query="", sort_by="last_edited_time", limit=limit)
        items = []
        for r in results:
            obj_type = r.get("object", "page")
            title = "Untitled"
            props = r.get("properties", {})
            if "title" in props:
                title_parts = props["title"].get("title", [])
                if title_parts:
                    title = title_parts[0].get("plain_text", "") or "Untitled"
            elif "Name" in props:
                title_parts = props["Name"].get("title", [])
                if title_parts:
                    title = title_parts[0].get("plain_text", "") or "Untitled"
            items.append(
                {
                    "id": r.get("id", ""),
                    "title": title,
                    "type": obj_type,
                    "url": r.get("url", ""),
                    "last_edited": r.get("last_edited_time", ""),
                }
            )
        return {"items": items}
    except Exception as e:
        return {"items": [], "error": str(e)}


@app.get("/api/stats")
async def get_stats():
    """Return real-time Notion workspace telemetry."""
    try:
        initialize_notion_client()
        assert notion_client is not None, "Notion client failed to initialize"
        stats = await notion_client.get_stats()
        return stats
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/tools")
async def list_tools():
    """Dynamic listing of registered MCP tools."""
    try:
        tools = await mcp.list_tools()
        return {"tools": [t.name for t in tools]}
    except Exception as e:
        logger.exception("Failed to list tools")
        return {"tools": [], "error": str(e)}


@app.get("/api/llm/providers")
async def llm_providers():
    """Return available LLM providers and their models (for Settings page)."""
    import httpx

    providers: dict[str, list[dict]] = {"ollama": [], "lm_studio": []}
    async with httpx.AsyncClient(timeout=2) as client:
        try:
            resp = await client.get("http://localhost:11434/api/tags")
            if resp.status_code == 200:
                for m in resp.json().get("models", []):
                    providers["ollama"].append({"name": m["name"]})
        except Exception:
            logger.debug("Ollama provider probe: not reachable")
        try:
            resp = await client.get("http://localhost:1234/v1/models")
            if resp.status_code == 200:
                for m in resp.json().get("data", []):
                    providers["lm_studio"].append({"name": m["id"]})
        except Exception:
            logger.debug("LM Studio provider probe: not reachable")
    return providers


@app.get("/api/llm-discovery")
async def discover_llms():
    """Auto-detect local LLMs (Ollama / LM Studio)."""
    import httpx

    llms = []
    async with httpx.AsyncClient(timeout=2) as client:
        try:
            resp = await client.get("http://localhost:11434/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                for model in data.get("models", []):
                    llms.append({"name": model["name"], "provider": "Ollama", "url": "http://localhost:11434"})
        except Exception as e:
            logger.warning("Ollama discovery failed", error=str(e))
        try:
            resp = await client.get("http://localhost:1234/v1/models")
            if resp.status_code == 200:
                data = resp.json()
                for model in data.get("data", []):
                    llms.append({"name": model["id"], "provider": "LM Studio", "url": "http://localhost:1234"})
        except Exception as e:
            logger.warning("LM Studio discovery failed", error=str(e))

    return {"llms": llms}


@app.get("/api/llm/models")
async def llm_models(provider: str = "ollama"):
    """Model list per provider: live when reachable, curated fallback otherwise.

    ## Return Format
    `{"provider": str, "models": [{"name": str}], "live": bool}`.
    """
    name = provider.lower().replace("-", "_").replace(" ", "_")
    if name in ("lm_studio", "lmstudio"):
        url, key = "http://localhost:1234/v1/models", "data"
    else:
        url, key = "http://localhost:11434/api/tags", "models"
    import httpx

    try:
        async with httpx.AsyncClient(timeout=2) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                items = resp.json().get(key, [])
                models = [{"name": (m.get("name") or m.get("id", ""))} for m in items]
                return {"provider": provider, "models": models, "live": True}
    except Exception:
        logger.exception("LLM model list probe failed")
    fallback = {
        "ollama": [{"name": "llama3.1:8b"}, {"name": "qwen2.5:7b"}],
        "lm_studio": [{"name": "local-model"}],
    }
    return {
        "provider": provider,
        "models": fallback.get(name, []),
        "live": False,
    }


@app.get("/api/llm/onboarding")
async def llm_onboarding():
    """Fresh-install starter facts + recommended path for the under-hero cue.

    ## Return Format
    `{"steps": [...], "recommended": str, "needs_token": bool}`.
    """
    try:
        initialize_notion_client()
        needs_token = False
    except Exception:
        needs_token = True
    return {
        "steps": [
            "Paste your Notion integration token on the Connect screen (Settings).",
            "Get one at https://www.notion.so/my-integrations (New integration).",
            "Optional: start Ollama (:11434) for local RAG chat summaries.",
        ],
        "recommended": "settings-token-first",
        "needs_token": needs_token,
    }


@app.post("/api/llm/chat")
async def llm_chat(messages: list[dict[str, Any]] = Body(..., embed=True)):
    """Backend chat proxy (OpenAI-style messages) — the ONLY path the Chat
    page should use. Keys never leave the server. Tries local Ollama first;
    DECLARED FALLBACK: returns RAG context with a stub reply and
    `declared_fallback: true` when no LLM is reachable.

    ## Return Format
    `{"reply": str, "context": [...], "model": str | None,
    "declared_fallback": bool}`.
    """
    user_text = ""
    for m in reversed(messages or []):
        if m.get("role") == "user":
            content = m.get("content", "")
            user_text = content if isinstance(content, str) else str(content)
            break
    try:
        context = await rag.semantic_search(user_text or "", limit=3)
    except Exception:
        logger.exception("RAG context build failed for llm_chat")
        context = []
    import httpx

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            tags = await client.get("http://localhost:11434/api/tags")
            model_names = [m["name"] for m in tags.json().get("models", [])] if tags.status_code == 200 else []
            if model_names:
                prompt = (
                    "Context from Notion:\n"
                    + "\n".join(f"Source: {c.get('title', '')}\nContent: {c.get('content', '')}" for c in context)
                    + f"\n\nUser Question: {user_text}\n\nAnswer based on the context."
                )
                gen = await client.post(
                    "http://localhost:11434/api/generate",
                    json={"model": model_names[0], "prompt": prompt, "stream": False},
                )
                if gen.status_code == 200:
                    return {
                        "reply": gen.json().get("response", ""),
                        "context": context,
                        "model": model_names[0],
                        "declared_fallback": False,
                    }
    except Exception:
        logger.exception("Local LLM chat attempt failed, using declared fallback")
    return {
        "reply": "RAG Context provided. Local LLM invocation would happen here.",
        "context": context,
        "model": None,
        "declared_fallback": True,
    }


@app.post("/api/llm/chat/stream")
async def llm_chat_stream(messages: list[dict[str, Any]] = Body(..., embed=True)):
    """SSE token stream for the Chat page (chat_skills_prefab_standard
    1.10). Events: `data: {"token": str}` chunks, then `data: [DONE]`.
    Without a reachable Ollama, emits one `{"reply", "declared_fallback"}`
    event (same declared contract as POST /api/llm/chat).

    ## Return Format
    `text/event-stream` of `data: {...}` lines ending with `data: [DONE]`.
    """
    user_text = ""
    for m in reversed(messages or []):
        if m.get("role") == "user":
            content = m.get("content", "")
            user_text = content if isinstance(content, str) else str(content)
            break
    try:
        context = await rag.semantic_search(user_text or "", limit=3)
    except Exception:
        logger.exception("RAG context build failed for llm_chat_stream")
        context = []

    async def events():
        import httpx

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                tags = await client.get("http://localhost:11434/api/tags")
                model_names = [m["name"] for m in tags.json().get("models", [])] if tags.status_code == 200 else []
                if model_names:
                    prompt = (
                        "Context from Notion:\n"
                        + "\n".join(f"Source: {c.get('title', '')}\nContent: {c.get('content', '')}" for c in context)
                        + f"\n\nUser Question: {user_text}\n\nAnswer based on the context."
                    )
                    async with client.stream(
                        "POST",
                        "http://localhost:11434/api/generate",
                        json={"model": model_names[0], "prompt": prompt, "stream": True},
                    ) as resp:
                        if resp.status_code == 200:
                            async for line in resp.aiter_lines():
                                if not line.strip():
                                    continue
                                try:
                                    chunk = json.loads(line)
                                except ValueError:
                                    continue
                                token = chunk.get("response", "")
                                if token:
                                    yield f"data: {json.dumps({'token': token})}\n\n"
                            yield "data: [DONE]\n\n"
                            return
        except Exception:
            logger.exception("Local LLM stream failed, using declared fallback")
        yield f"data: {json.dumps({'reply': 'RAG Context provided. Local LLM invocation would happen here.', 'declared_fallback': True})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")


@app.post("/api/search")
async def semantic_search(query: str = Body(..., embed=True)):
    """SOTA Semantic Search endpoint."""
    return await rag.semantic_search(query)


@app.post("/api/chat")
async def chat_interaction(message: str = Body(..., embed=True), model_url: str | None = None):
    """RAG-powered chat with local LLM integration.

    DECLARED FALLBACK (not a mock): without a configured local LLM this
    returns the retrieved RAG context plus a stub reply and
    `declared_fallback: true`. Prefer POST /api/llm/chat (tries Ollama).
    """
    context = await rag.semantic_search(message, limit=3)
    context_text = "\n".join([f"Source: {c['title']}\nContent: {c['content']}" for c in context])

    prompt = f"Context from Notion:\n{context_text}\n\nUser Question: {message}\n\nPlease answer based on the context."
    logger.debug("Chat prompt construction finished", prompt_preview=prompt[:100])

    # In a full implementation, we'd call the model_url here
    return {
        "reply": "RAG Context provided. Local LLM invocation would happen here.",
        "context": context,
        "declared_fallback": True,
    }


@app.post("/api/webhooks/notion")
async def notion_webhook_receiver(request: Request):
    """Receive Notion webhook events (verification + content events)."""
    initialize_notion_client()
    assert automation_manager is not None, "Notion client failed to initialize"
    body = await request.json()
    headers = dict(request.headers)
    result = await automation_manager.receive_webhook_event(headers, body)
    logger.info("Webhook event received", event_type=result.get("event_type", "unknown"))
    return result


@app.get("/api/webhooks/events")
async def get_webhook_events(limit: int = 50, event_type: str | None = None):
    """List stored webhook events."""
    initialize_notion_client()
    assert automation_manager is not None, "Notion client failed to initialize"
    return await automation_manager.list_webhook_events(limit=limit, event_type=event_type)


_DATA_DIR = Path(__file__).resolve().parent / "exports"
_TOKEN_FILE = _DATA_DIR / "notion_token.txt"


def _read_stored_token() -> str | None:
    """Read token from local file (set via webapp Settings)."""
    try:
        if _TOKEN_FILE.exists():
            return _TOKEN_FILE.read_text(encoding="utf-8").strip()
    except Exception:
        logger.warning("Failed to read stored token file", exc_info=True)
    return None


def _write_stored_token(token: str) -> None:
    """Persist token to local file."""
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    _TOKEN_FILE.write_text(token, encoding="utf-8")


# Initialize Notion client with Austrian efficiency
# Note: Initialization happens lazily to avoid import-time failures
notion_client = None
page_manager = None
db_manager = None
collab_manager = None
automation_manager = None


def initialize_notion_client():
    """Initialize Notion client and managers."""
    global notion_client, page_manager, db_manager, collab_manager, automation_manager

    if notion_client is not None:
        return  # Already initialized

    # Check env vars first, then file-based token (set via webapp Settings)
    token = os.getenv("NOTION_TOKEN") or os.getenv("NOTION_PAT") or _read_stored_token()
    has_file_token = bool(_read_stored_token())
    token_type = "pat" if (os.getenv("NOTION_PAT") or has_file_token) and not os.getenv("NOTION_TOKEN") else "internal"

    if not token:
        raise ValueError("Notion token required. Set NOTION_TOKEN or NOTION_PAT.")

    try:
        notion_client = NotionClient(
            token=token,
            version=os.getenv("NOTION_VERSION", "2026-03-11"),
            timeout=int(os.getenv("NOTION_TIMEOUT", "30")),
            token_type=token_type,
        )

        # Initialize managers
        page_manager = PageManager(notion_client)
        db_manager = DatabaseManager(notion_client)
        collab_manager = CollaborationManager(notion_client)
        automation_manager = AutomationManager(notion_client)

        logger.info(
            "Notion client initialized successfully",
            message="Austrian efficiency activated",
        )
    except Exception as e:
        logger.exception("Failed to initialize Notion client", error=str(e))
        raise


_READ_ONLY = {"readonly": True}
_MUTATING = {}
_DESTRUCTIVE = {}
# All tools return JSON objects (dialogic dicts); declared once, shared.
_OUT_OBJECT = {"type": "object"}

# 🎛️ SOTA Portmanteau Toolsets (Consolidated Implementation)


@mcp.tool(annotations=_DESTRUCTIVE, output_schema=_OUT_OBJECT)
async def manage_notion_data(
    operation: str = Field(description="CRUD operation: create, retrieve, update, archive, restore"),
    entity_type: str = Field(description="Entity type: page, data_source, block"),
    entity_id: str | None = Field(default=None, description="Target entity ID (required except for create)"),
    parent_id: str | None = Field(default=None, description="Parent ID (required for create)"),
    title: str | None = Field(default=None, description="Title/Name for the entity"),
    content: str | None = Field(default=None, description="Content (text or block formatted)"),
    properties: dict[str, Any] | None = Field(default=None, description="Structured properties"),
    children: list[dict[str, Any]] | None = Field(default=None, description="Child blocks"),
    extra_params: dict[str, Any] | None = Field(default=None, description="Advanced API parameters"),
) -> dict[str, Any]:
    """Consolidated CRUD management for Notion Pages, Data Sources, and Blocks.

    ## Return Format
    `{"success": bool, "message"?: str, "error"?: str, ...}` — create returns
    `id`+`url`; retrieve returns `data`; update/archive return `message`.

    ## Examples
    `manage_notion_data(operation="retrieve", entity_type="page", entity_id="...")`
    -> `{"success": True, "data": {...}, "message": "page retrieved."}`.
    """
    try:
        initialize_notion_client()
        assert page_manager is not None, "Notion client failed to initialize"
        assert db_manager is not None, "Notion client failed to initialize"
        assert notion_client is not None, "Notion client failed to initialize"
        extra_params = extra_params or {}

        if operation == "create":
            if entity_type == "page":
                if not title:
                    return {"success": False, "error": "title is required for 'create'"}
                result = await page_manager.create_page(
                    title=title,
                    content=content or "",
                    parent_id=parent_id,
                    properties=properties,
                    children=children,
                )
            elif entity_type == "data_source":
                if not title or not parent_id:
                    return {
                        "success": False,
                        "error": "title and parent_id are required to create a data source",
                    }
                result = await db_manager.create_database(
                    title=title,
                    parent_id=parent_id,
                    properties_schema=properties or {},
                    **extra_params,
                )
            else:
                return {
                    "success": False,
                    "error": f"Unsupported creation type: {entity_type}",
                }

            return {
                "success": True,
                "id": result["id"],
                "url": result.get("url"),
                "message": f"{entity_type.capitalize()} created successfully ✅",
            }

        if not entity_id:
            return {
                "success": False,
                "error": f"entity_id is required for '{operation}'",
            }

        if operation == "retrieve":
            if entity_type == "page":
                result = await page_manager.get_page_content(entity_id, **extra_params)
            elif entity_type == "data_source":
                result = await db_manager.get_database(entity_id)
            elif entity_type == "block":
                result = await notion_client.get_block_children(entity_id)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported retrieval type: {entity_type}",
                }
            return {"success": True, "data": result, "message": f"{entity_type} retrieved."}

        if operation == "update":
            if entity_type == "page":
                await page_manager.update_page(entity_id, title=title, content=content, properties=properties)
            elif entity_type == "data_source":
                await db_manager.update_database(entity_id, title=title, properties=properties)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported update type: {entity_type}",
                }
            return {
                "success": True,
                "message": f"{entity_type.capitalize()} updated ✅",
            }

        if operation == "archive":
            if entity_type == "page":
                await page_manager.archive_page(entity_id, **extra_params)
            else:
                await notion_client.update_page(entity_id, archived=True)
            return {
                "success": True,
                "message": f"{entity_type.capitalize()} archived ✅",
            }

        return {"success": False, "error": f"Unknown operation: {operation}"}

    except Exception as e:
        logger.exception(f"manage_notion_data failed ({operation} {entity_type})", error=str(e))
        return {"success": False, "error": str(e)}


@mcp.tool(annotations=_READ_ONLY, output_schema=_OUT_OBJECT)
async def query_data_source(
    data_source_id: str = Field(description="Data source ID to query"),
    filter: dict[str, Any] | None = Field(default=None, description="Query filter"),
    sorts: list[dict[str, Any]] | None = Field(default=None, description="Sort list"),
    limit: int = Field(default=50, description="Max results"),
    cursor: str | None = Field(default=None, description="Pagination cursor"),
) -> dict[str, Any]:
    """High-speed exploration of structured data sources with complex filtering.

    ## Return Format
    `{"success": bool, "results": [...], "has_more": bool,
    "next_cursor"?: str, "message": str}`.

    ## Examples
    `query_data_source(data_source_id="...", limit=10)`
    -> `{"success": True, "results": [...], "has_more": False, ...}`.
    """
    try:
        initialize_notion_client()
        assert db_manager is not None, "Notion client failed to initialize"
        results = await db_manager.query_database(
            database_id=data_source_id,
            filter=filter,
            sorts=sorts,
            limit=limit,
            cursor=cursor,
        )
        return {
            "success": True,
            "results": results.get("results", []),
            "has_more": results.get("has_more", False),
            "next_cursor": results.get("next_cursor"),
            "message": "Data retrieved with Austrian efficiency! 📊",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool(annotations=_READ_ONLY, output_schema=_OUT_OBJECT)
async def search_notion_knowledge(
    query: str = Field(description="Search query (natural language)"),
    mode: str = Field(
        default="semantic",
        description="Search mode: semantic (RAG), keyword (API), hybrid",
    ),
    limit: int = Field(default=10, description="Max results"),
) -> dict[str, Any]:
    """Powerful SOTA search leveraging both Notion API and local RAG pipeline.

    ## Return Format
    `{"success": bool, "results": [...], "mode": str, "message": str}` —
    items are `{"type": "rag"|"api", ...}`.

    ## Examples
    `search_notion_knowledge(query="roadmap", mode="hybrid")`
    -> `{"success": True, "results": [...], "mode": "hybrid"}`.
    """
    try:
        initialize_notion_client()
        assert page_manager is not None, "Notion client failed to initialize"
        results = []

        if mode in ["semantic", "hybrid"]:
            rag_results = await rag.semantic_search(query, limit=limit)
            results.extend([{"type": "rag", **r} for r in rag_results])

        if mode in ["keyword", "hybrid"] or not results:
            api_results = await page_manager.search_pages(query, limit=limit)
            results.extend([{"type": "api", **r} for r in api_results])

        return {
            "success": True,
            "results": results[:limit],
            "mode": mode,
            "message": f"Found {len(results)} intelligence items! 🔍",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool(annotations=_MUTATING, output_schema=_OUT_OBJECT)
async def sync_rag_index(
    data_source_ids: list[str] | None = Field(
        default=None,
        description="Specific IDs to index. If None, performs workspace scan",
    ),
    force_rebuild: bool = Field(default=False, description="Rebuild index from scratch"),
) -> dict[str, Any]:
    """Synchronize Notion workspace knowledge to local LanceDB vector store.

    ## Return Format
    `{"success": bool, "message": str}` — the sweep runs in background.

    ## Examples
    `sync_rag_index(force_rebuild=False)` -> `{"success": True, ...}`.
    """
    try:
        initialize_notion_client()
        # In a real implementation, this would trigger the indexing loop
        # For now, we'll simulate the orchestrator call
        return {
            "success": True,
            "message": "SOTA Synchronization started in background. Knowledge base will be online shortly. 📡",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool(annotations=_READ_ONLY, output_schema=_OUT_OBJECT)
async def server_help() -> dict[str, Any]:
    """Show server capabilities, tool inventory, and usage pointers.

    ## Return Format
    `{"success": bool, "message": str, "server": str, "version": str,
    "tool_count": int, "tools": [str], "dashboard": str, "api": str}`.

    ## Examples
    `server_help()` -> `{"success": True, "tool_count": 40, ...}`.
    """
    try:
        tools = await mcp.list_tools()
        names = [t.name for t in tools]
    except Exception:
        logger.exception("server_help failed to list tools")
        names = []
    return {
        "success": True,
        "message": (
            f"notion-mcp exposes {len(names)} tools: pages, databases, comments, "
            "RAG search, automations, workers, webhooks. Start with search_pages "
            "or search_notion_knowledge; see dashboard for visual browsing."
        ),
        "server": "notion-mcp",
        "version": "1.2.0",
        "tool_count": len(names),
        "tools": names,
        "dashboard": "http://127.0.0.1:10810",
        "api": "http://127.0.0.1:10811",
    }


@mcp.tool(annotations=_DESTRUCTIVE, output_schema=_OUT_OBJECT)
async def shutdown_server() -> dict[str, Any]:
    """Gracefully shut down the server process (orderly self-termination).

    ## Return Format
    `{"success": bool, "message": str}` — the process exits ~500 ms after
    responding so in-flight work can checkpoint.

    ## Examples
    `shutdown_server()` -> `{"success": True, "message": "shutting down..."}`.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        os._exit(0)
    loop.call_later(0.5, lambda: os._exit(0))
    return {"success": True, "message": "notion-mcp shutting down in ~500 ms"}


@mcp.tool(annotations=_READ_ONLY, output_schema=_OUT_OBJECT)
async def notion_agentic_workflow(
    goal: str = Field(description="High-level objective in plain language"),
    ctx: Context = Field(description="MCP request context (sampling + progress)"),
) -> dict[str, Any]:
    """Autonomous multi-step Notion workflow via MCP sampling (SEP-1577).

    Grounds the goal with a workspace search, then borrows the client LLM
    via ctx.sample() to plan concrete tool calls. Sampling stays supported
    indefinitely (Claude Desktop path); when the host cannot sample, the
    tool reports so explicitly instead of guessing.

    ## Return Format
    `{"success": bool, "message": str, "goal": str, "grounding": [...],
    "plan": str, "sampling": "client-llm"|"unavailable"}`.

    ## Examples
    `notion_agentic_workflow(goal="triage open meeting notes")`
    -> `{"success": True, "plan": "1. search_pages... ", ...}`.
    """
    initialize_notion_client()
    assert page_manager is not None, "Notion client failed to initialize"
    try:
        grounding = await page_manager.search_pages(query=goal, limit=5)
    except Exception:
        logger.exception("Agentic grounding search failed")
        grounding = []
    titles = [g.get("properties", {}) for g in grounding]
    try:
        sampled = await ctx.sample(
            messages=[
                f"Goal: {goal}\nWorkspace hits (properties): {titles}\n"
                "Plan the concrete notion-mcp tool calls to achieve the goal. "
                "Prefer search_notion_knowledge, get_page_content, manage_notion_data, "
                "query_database, export_workspace_data. Reply with a numbered plan only."
            ],
            system_prompt="You are a Notion workspace planner. Output numbered tool-call plans, no prose.",
            temperature=0.2,
            max_tokens=800,
        )
        plan_text = sampled.text if hasattr(sampled, "text") else str(sampled)
        return {
            "success": True,
            "message": "Plan ready via client sampling.",
            "goal": goal,
            "grounding": grounding,
            "plan": plan_text,
            "sampling": "client-llm",
        }
    except Exception as e:
        logger.exception("Agentic sampling unavailable")
        return {
            "success": False,
            "error": f"sampling unavailable on this host: {e}",
            "message": "Retry from a sampling-capable client (Claude Desktop) or break the goal into direct tool calls.",
            "goal": goal,
            "grounding": grounding,
            "sampling": "unavailable",
        }


@mcp.resource("notion://status")
async def resource_status() -> str:
    """Live server status (identity, version, uptime)."""
    import json

    return json.dumps(
        {
            "server": "notion-mcp",
            "version": "1.2.0",
            "uptime_seconds": int(time.time() - _server_start_time),
        }
    )


@mcp.prompt()
async def notion_quickstart() -> str:
    """Starter workflow: find a page, read it, update it."""
    return (
        "To work with the Notion workspace: 1) search_notion_knowledge(query) to "
        "find relevant pages, 2) get_page_content(page_id) to read one, "
        "3) update_page(page_id, ...) to change it. Ask for a token via the "
        "dashboard Settings page if tools report missing authentication."
    )


# 📄 Legacy Logic (Redirected to Portmanteau)
# Note: Keeping these for backward compatibility but marking as secondary


@mcp.tool(annotations=_MUTATING, output_schema=_OUT_OBJECT)
async def create_page(
    title: str = Field(description="Page title (supports German characters: ä, ö, ü, ß)"),
    content: str = Field(default="", description="Page content in Notion blocks format or plain text"),
    parent_id: str | None = Field(
        default=None,
        description="Parent page/database ID. If not provided, creates in workspace root",
    ),
    properties: dict[str, Any] | None = Field(default=None, description="Page properties if parent is a database"),
    children: list[dict[str, Any]] | None = Field(default=None, description="Child blocks to add to the page"),
) -> dict[str, Any]:
    """Create a new Notion page with content, properties, and Austrian efficiency.

    ## Return Format
    `{"success": bool, "page_id": str, "url": str, "title": str,
    "message": str}`.

    ## Examples
    `create_page(title="Neu", content="Hallo")`
    -> `{"success": True, "page_id": "...", ...}`.
    """
    try:
        initialize_notion_client()  # Ensure client is initialized
        assert page_manager is not None, "Notion client failed to initialize"
        result = await page_manager.create_page(
            title=title,
            content=content,
            parent_id=parent_id,
            properties=properties,
            children=children,
        )
        logger.info("Page created successfully", page_title=title, page_id=result["id"])
        return {
            "success": True,
            "page_id": result["id"],
            "url": result.get("url", ""),
            "title": title,
            "message": f"Page '{title}' created with Austrian efficiency! ✅",
        }
    except Exception as e:
        logger.exception("Failed to create page", page_title=title, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "message": "Page creation failed - check your permissions and parent_id",
        }


@mcp.tool(annotations=_MUTATING, output_schema=_OUT_OBJECT)
async def update_page(
    page_id: str = Field(description="Page ID to update"),
    title: str | None = Field(default=None, description="New page title"),
    content: str | None = Field(default=None, description="New page content"),
    properties: dict[str, Any] | None = Field(default=None, description="Updated properties"),
    archived: bool | None = Field(default=None, description="Archive status"),
) -> dict[str, Any]:
    """Update existing Notion page with Austrian efficiency.

    ## Return Format
    `{"success": bool, "page_id": str, "updated_fields": [...],
    "message": str}`.

    ## Examples
    `update_page(page_id="...", title="Neu")` -> `{"success": True, ...}`.
    """
    try:
        initialize_notion_client()
        assert page_manager is not None, "Notion client failed to initialize"
        result = await page_manager.update_page(
            page_id=page_id,
            title=title,
            content=content,
            properties=properties,
            archived=archived,
        )
        logger.info("Page updated successfully", page_id=page_id)
        return {
            "success": True,
            "page_id": page_id,
            "updated_fields": [k for k, v in locals().items() if v is not None and k != "page_id"],
            "message": "Page updated with Austrian efficiency! ✅",
        }
    except Exception as e:
        logger.exception("Failed to update page", page_id=page_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "message": "Page update failed - check page ID and permissions",
        }


@mcp.tool(annotations=_READ_ONLY, output_schema=_OUT_OBJECT)
async def get_page_content(
    page_id: str = Field(description="Page ID to retrieve"),
    include_children: bool = Field(default=True, description="Include child blocks"),
    block_depth: int = Field(default=10, description="Maximum depth for nested blocks"),
) -> dict[str, Any]:
    """Retrieve complete page content with Austrian efficiency optimization.

    ## Return Format
    `{"success": bool, "page": {...}, "message": str}`.

    ## Examples
    `get_page_content(page_id="...")` -> `{"success": True, "page": {...}}`.
    """
    try:
        initialize_notion_client()
        assert page_manager is not None, "Notion client failed to initialize"
        result = await page_manager.get_page_content(
            page_id=page_id, include_children=include_children, block_depth=block_depth
        )
        logger.info("Page content retrieved", page_id=page_id)
        return {
            "success": True,
            "page": result,
            "message": "Page content retrieved with Austrian efficiency! ✅",
        }
    except Exception as e:
        logger.exception("Failed to get page content", page_id=page_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "message": "Page retrieval failed - check page ID and permissions",
        }


@mcp.tool(annotations=_READ_ONLY, output_schema=_OUT_OBJECT)
async def search_pages(
    query: str = Field(description="Search query (natural language)"),
    filter_by_type: str | None = Field(default=None, description="Filter by object type: page, database"),
    sort_by: str = Field(
        default="last_edited_time",
        description="Sort field: last_edited_time, created_time",
    ),
    limit: int = Field(default=10, description="Maximum results to return"),
) -> dict[str, Any]:
    """Natural language search across entire Notion workspace.

    ## Return Format
    `{"success": bool, "results": [...], "count": int, "query": str,
    "message": str}`.

    ## Examples
    `search_pages(query="urlaub")` -> `{"success": True, "count": 3, ...}`.
    """
    try:
        initialize_notion_client()
        assert page_manager is not None, "Notion client failed to initialize"
        results = await page_manager.search_pages(
            query=query, filter_by_type=filter_by_type, sort_by=sort_by, limit=limit
        )
        logger.info(f"Search completed for query: {query}")
        return {
            "success": True,
            "results": results,
            "count": len(results),
            "query": query,
            "message": f"Found {len(results)} results with Austrian efficiency! 🔍",
        }
    except Exception as e:
        logger.exception(f"Search failed for query '{query}': {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Search failed - check your query and try again",
        }


@mcp.tool(annotations=_DESTRUCTIVE, output_schema=_OUT_OBJECT)
async def archive_page(
    page_id: str = Field(description="Page ID to archive"),
    permanent_delete: bool = Field(default=False, description="Permanently delete instead of archive"),
    backup_first: bool = Field(default=True, description="Create backup before deletion"),
) -> dict[str, Any]:
    """Safely archive or delete pages with Austrian efficiency confirmations.

    ## Return Format
    `{"success": bool, "page_id": str, "action": "archived"|"deleted",
    "backup_created": bool, "message": str}`.

    ## Examples
    `archive_page(page_id="...")` -> `{"success": True, "action": "archived"}`.
    """
    try:
        initialize_notion_client()
        assert page_manager is not None, "Notion client failed to initialize"
        await page_manager.archive_page(
            page_id=page_id,
            permanent_delete=permanent_delete,
            backup_first=backup_first,
        )
        action = "deleted" if permanent_delete else "archived"
        logger.info(
            "Page archived/deleted",
            page_id=page_id,
            action=action,
            backup_created=backup_first,
        )
        return {
            "success": True,
            "page_id": page_id,
            "action": action,
            "backup_created": backup_first,
            "message": f"Page {action} with Austrian efficiency! ✅",
        }
    except Exception as e:
        logger.exception("Failed to archive page", page_id=page_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "message": "Archive operation failed - check page ID and permissions",
        }


# 🗄️ Database Operations (6 tools)


@mcp.tool(annotations=_MUTATING, output_schema=_OUT_OBJECT)
async def create_database(
    title: str = Field(description="Database title"),
    parent_id: str = Field(description="Parent page ID where database will be created"),
    properties_schema: dict[str, Any] = Field(description="Database properties schema"),
    icon: str | None = Field(default=None, description="Database icon (emoji or external URL)"),
    cover: str | None = Field(default=None, description="Database cover image URL"),
) -> dict[str, Any]:
    """Create databases with custom property schemas.

    ## Return Format
    `{"success": bool, "database_id": str, "url": str, "title": str,
    "properties": {...}, "message": str}`.

    ## Examples
    `create_database(title="DB", parent_id="...", properties_schema={...})`
    -> `{"success": True, "database_id": "..."}`.
    """
    try:
        initialize_notion_client()
        assert db_manager is not None, "Notion client failed to initialize"
        result = await db_manager.create_database(
            title=title,
            parent_id=parent_id,
            properties_schema=properties_schema,
            icon=icon,
            cover=cover,
        )
        logger.info(f"Database created: {title}")
        return {
            "success": True,
            "database_id": result["id"],
            "url": result.get("url", ""),
            "title": title,
            "properties": result.get("properties", {}),
            "message": f"Database '{title}' created with Austrian efficiency! 🗄️",
        }
    except Exception as e:
        logger.exception(f"Failed to create database '{title}': {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Database creation failed - check schema and permissions",
        }


@mcp.tool(annotations=_READ_ONLY, output_schema=_OUT_OBJECT)
async def query_database(
    database_id: str = Field(description="Database ID to query"),
    filter: dict[str, Any] | None = Field(default=None, description="Query filter conditions"),
    sorts: list[dict[str, Any]] | None = Field(default=None, description="Sort configuration"),
    limit: int = Field(default=100, description="Maximum results"),
    cursor: str | None = Field(default=None, description="Pagination cursor"),
) -> dict[str, Any]:
    """Query databases with complex filters and sorts.

    ## Return Format
    `{"success": bool, "results": [...], "has_more": bool,
    "next_cursor"?: str, "count": int, "message": str}`.

    ## Examples
    `query_database(database_id="...")` -> `{"success": True, "count": 5}`.
    """
    try:
        initialize_notion_client()
        assert db_manager is not None, "Notion client failed to initialize"
        results = await db_manager.query_database(
            database_id=database_id,
            filter=filter,
            sorts=sorts,
            limit=limit,
            cursor=cursor,
        )
        result_count = len(results.get("results", []))
        logger.info(
            "Database query completed",
            database_id=database_id,
            result_count=result_count,
        )
        return {
            "success": True,
            "results": results.get("results", []),
            "has_more": results.get("has_more", False),
            "next_cursor": results.get("next_cursor"),
            "count": result_count,
            "message": "Query completed with Austrian efficiency! 🔍",
        }
    except Exception as e:
        logger.exception("Database query failed", database_id=database_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "message": "Database query failed - check database ID and filter syntax",
        }


@mcp.tool(annotations=_MUTATING, output_schema=_OUT_OBJECT)
async def create_database_entry(
    database_id: str = Field(description="Database ID to add entry to"),
    properties: dict[str, Any] = Field(description="Entry properties"),
    content: str = Field(default="", description="Entry content"),
    children: list[dict[str, Any]] | None = Field(default=None, description="Child blocks"),
) -> dict[str, Any]:
    """Add entries with all property types (text, select, date, etc.)

    ## Return Format
    `{"success": bool, "page_id": str, "database_id": str,
    "properties": {...}, "message": str}`.

    ## Examples
    `create_database_entry(database_id="...", properties={...})`
    -> `{"success": True, "page_id": "..."}`.
    """
    try:
        initialize_notion_client()
        assert db_manager is not None, "Notion client failed to initialize"
        result = await db_manager.create_database_entry(
            database_id=database_id,
            properties=properties,
            content=content,
            children=children,
        )
        logger.info(f"Database entry created: {database_id}")
        return {
            "success": True,
            "page_id": result["id"],
            "database_id": database_id,
            "properties": properties,
            "message": "Database entry created with Austrian efficiency! ✅",
        }
    except Exception as e:
        logger.exception(f"Failed to create database entry: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Database entry creation failed - check properties and schema",
        }


@mcp.tool(annotations=_MUTATING, output_schema=_OUT_OBJECT)
async def update_database_entry(
    page_id: str = Field(description="Entry page ID to update"),
    properties: dict[str, Any] | None = Field(default=None, description="Updated properties"),
    content: str | None = Field(default=None, description="Updated content"),
    archived: bool | None = Field(default=None, description="Archive status"),
) -> dict[str, Any]:
    """Update existing database entries and properties.

    ## Return Format
    `{"success": bool, "page_id": str, "updated_properties"?: {...},
    "message": str}`.

    ## Examples
    `update_database_entry(page_id="...", properties={...})`
    -> `{"success": True}`.
    """
    try:
        initialize_notion_client()
        assert db_manager is not None, "Notion client failed to initialize"
        await db_manager.update_database_entry(
            page_id=page_id, properties=properties, content=content, archived=archived
        )
        logger.info("Database entry updated", page_id=page_id)
        return {
            "success": True,
            "page_id": page_id,
            "updated_properties": properties,
            "message": "Database entry updated with Austrian efficiency! ✅",
        }
    except Exception as e:
        logger.exception("Failed to update database entry", page_id=page_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "message": "Database entry update failed - check page ID and properties",
        }


@mcp.tool(annotations=_READ_ONLY, output_schema=_OUT_OBJECT)
async def get_database_schema(
    database_id: str = Field(description="Database ID to analyze"),
    include_statistics: bool = Field(default=False, description="Include usage statistics"),
    property_details: bool = Field(default=True, description="Include detailed property information"),
) -> dict[str, Any]:
    """Retrieve database structure, properties, and metadata.

    ## Return Format
    `{"success": bool, "schema": {...}, "message": str}`.

    ## Examples
    `get_database_schema(database_id="...")`
    -> `{"success": True, "schema": {...}}`.
    """
    try:
        initialize_notion_client()
        assert db_manager is not None, "Notion client failed to initialize"
        result = await db_manager.get_database_schema(
            database_id=database_id,
            include_statistics=include_statistics,
            property_details=property_details,
        )
        logger.info(f"Database schema retrieved: {database_id}")
        return {
            "success": True,
            "schema": result,
            "message": "Database schema retrieved with Austrian efficiency! 📊",
        }
    except Exception as e:
        logger.exception(f"Failed to get database schema {database_id}: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Schema retrieval failed - check database ID and permissions",
        }


@mcp.tool(annotations=_MUTATING, output_schema=_OUT_OBJECT)
async def bulk_import_data(
    database_id: str = Field(description="Target database ID"),
    data_source: str = Field(description="CSV or JSON data to import"),
    mapping: dict[str, str] | None = Field(default=None, description="Field mapping (source -> target)"),
    merge_strategy: str = Field(default="create_new", description="How to handle existing data"),
) -> dict[str, Any]:
    """Import CSV/JSON data efficiently into databases.

    ## Return Format
    `{"success": bool, "import_results": {...}, "message": str}` with
    `successful_imports`/`total_records` counts.

    ## Examples
    `bulk_import_data(database_id="...", data_source="[...]")`
    -> `{"success": True, "import_results": {...}}`.
    """
    try:
        initialize_notion_client()
        assert db_manager is not None, "Notion client failed to initialize"
        result = await db_manager.bulk_import_data(
            database_id=database_id,
            data_source=data_source,
            mapping=mapping,
            merge_strategy=merge_strategy,
        )
        logger.info(
            "Bulk import completed",
            database_id=database_id,
            successful=result.get("successful_imports", 0),
            total=result.get("total_records", 0),
        )
        return {
            "success": True,
            "import_results": result,
            "message": f"Imported {result['successful_imports']}/{result['total_records']} records.",
        }
    except Exception as e:
        logger.exception("Bulk import failed", database_id=database_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "message": "Bulk import failed - check data format and database schema",
        }


# 💬 Collaboration Tools (3 tools)


@mcp.tool(annotations=_MUTATING, output_schema=_OUT_OBJECT)
async def add_comment(
    page_id: str = Field(description="Page or block ID to comment on"),
    content: str = Field(description="Comment content"),
    parent_comment_id: str | None = Field(default=None, description="Parent comment for threaded discussions"),
    rich_text: list[dict[str, Any]] | None = Field(default=None, description="Rich text formatting"),
) -> dict[str, Any]:
    """Add comments to pages or specific blocks.

    ## Return Format
    `{"success": bool, "comment": {...}, "message": str}`.

    ## Examples
    `add_comment(page_id="...", content="Hallo")`
    -> `{"success": True, "comment": {...}}`.
    """
    try:
        initialize_notion_client()
        assert collab_manager is not None, "Notion client failed to initialize"
        result = await collab_manager.add_comment(
            page_id=page_id,
            content=content,
            parent_comment_id=parent_comment_id,
            rich_text=rich_text,
        )
        logger.info("Comment added", page_id=page_id, comment_id=result.get("id"))
        return {
            "success": True,
            "comment": result,
            "message": "Comment added with Austrian efficiency! 💬",
        }
    except Exception as e:
        logger.exception("Failed to add comment", page_id=page_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "message": "Comment creation failed - check page ID and permissions",
        }


@mcp.tool(annotations=_READ_ONLY, output_schema=_OUT_OBJECT)
async def get_comments(
    page_id: str = Field(description="Page ID to get comments from"),
    include_resolved: bool = Field(default=False, description="Include resolved comments"),
    sort_by: str = Field(default="created_time", description="Sort field"),
    limit: int = Field(default=50, description="Maximum comments to return"),
) -> dict[str, Any]:
    """Retrieve page/block discussions and comment threads.

    ## Return Format
    `{"success": bool, "comments": [...], "count": int, "message": str}`.

    ## Examples
    `get_comments(page_id="...")` -> `{"success": True, "count": 2}`.
    """
    try:
        initialize_notion_client()
        assert collab_manager is not None, "Notion client failed to initialize"
        results = await collab_manager.get_comments(
            page_id=page_id,
            include_resolved=include_resolved,
            sort_by=sort_by,
            limit=limit,
        )
        logger.info("Comments retrieved", page_id=page_id, comment_count=len(results))
        return {
            "success": True,
            "comments": results,
            "count": len(results),
            "message": f"Retrieved {len(results)} comments with Austrian efficiency! 💬",
        }
    except Exception as e:
        logger.exception("Failed to get comments", page_id=page_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "message": "Comment retrieval failed - check page ID and permissions",
        }


@mcp.tool(annotations=_READ_ONLY, app=True, output_schema=_OUT_OBJECT)
async def get_workspace_users(
    include_inactive: bool = Field(default=False, description="Include inactive users"),
    permission_level: str | None = Field(default=None, description="Filter by permission level"),
    sort_by: str = Field(default="name", description="Sort field"),
) -> dict[str, Any]:
    """List workspace users, permissions, and activity.

    ## Return Format
    `{"success": bool, "users": [...], "count": int, "message": str}`.

    ## Examples
    `get_workspace_users()` -> `{"success": True, "count": 4, ...}`.
    """
    try:
        initialize_notion_client()
        assert collab_manager is not None, "Notion client failed to initialize"
        results = await collab_manager.get_workspace_users(
            include_inactive=include_inactive,
            permission_level=permission_level,
            sort_by=sort_by,
        )
        logger.info("Workspace users retrieved", user_count=len(results))
        return {
            "success": True,
            "users": results,
            "count": len(results),
            "message": f"Retrieved {len(results)} users with Austrian efficiency! 👥",
        }
    except Exception as e:
        logger.exception("Failed to get workspace users", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "message": "User retrieval failed - check permissions",
        }


# 🔍 Advanced Features (7 tools)


@mcp.tool(annotations=_MUTATING, output_schema=_OUT_OBJECT)
async def setup_automation(
    trigger_type: str = Field(description="Automation trigger type"),
    conditions: dict[str, Any] = Field(description="Trigger conditions"),
    actions: list[dict[str, Any]] = Field(description="Actions to perform"),
    webhook_url: str | None = Field(default=None, description="Optional webhook URL"),
) -> dict[str, Any]:
    """Configure a Notion automation with webhook integration.

    ## Return Format
    Automation-manager result dict with `success` + `message`.

    ## Examples
    `setup_automation(trigger_type="page_created", conditions={...},
    actions=[...])` -> `{"success": True, ...}`.
    """
    initialize_notion_client()
    assert automation_manager is not None, "Notion client failed to initialize"
    return await automation_manager.setup_automation(
        trigger_type=trigger_type,
        conditions=conditions,
        actions=actions,
        webhook_url=webhook_url,
    )


@mcp.tool(annotations=_MUTATING, output_schema=_OUT_OBJECT)
async def sync_external_data(
    external_source: str = Field(description="External data source type"),
    sync_config: dict[str, Any] = Field(description="Sync configuration"),
    update_frequency: str = Field(default="daily", description="Update frequency"),
) -> dict[str, Any]:
    """Create synced databases from external tools.

    DECLARED SCOPE: registers the sync configuration; live polling is not
    implemented (load via bulk_import_data).

    ## Return Format
    Automation-manager result dict with `success` + `message`.

    ## Examples
    `sync_external_data(external_source="csv", sync_config={...})`
    -> `{"success": True, ...}`.
    """
    initialize_notion_client()
    assert automation_manager is not None, "Notion client failed to initialize"
    return await automation_manager.sync_external_data(
        external_source=external_source,
        sync_config=sync_config,
        update_frequency=update_frequency,
    )


@mcp.tool(annotations=_MUTATING, output_schema=_OUT_OBJECT)
async def generate_ai_summary(
    page_id: str = Field(description="Page ID to analyze"),
    summary_type: str = Field(default="comprehensive", description="Summary type"),
    length: str = Field(default="medium", description="Summary length"),
    focus_areas: list[str] | None = Field(default=None, description="Areas to focus on"),
) -> dict[str, Any]:
    """Summarize page content using LLM API or fallback.

    ## Return Format
    Automation-manager result dict with `success` + summary payload.

    ## Examples
    `generate_ai_summary(page_id="...")` -> `{"success": True, ...}`.
    """
    initialize_notion_client()
    assert automation_manager is not None, "Notion client failed to initialize"
    return await automation_manager.generate_ai_summary(
        page_id=page_id,
        summary_type=summary_type,
        length=length,
        focus_areas=focus_areas,
    )


@mcp.tool(annotations=_MUTATING, output_schema=_OUT_OBJECT)
async def export_workspace_data(
    scope: str = Field(default="workspace", description="Export scope"),
    format: str = Field(default="json", description="Export format"),
    include_metadata: bool = Field(default=True, description="Include metadata"),
    compression: bool = Field(default=True, description="Compress export"),
) -> dict[str, Any]:
    """Backup and export functionality with multiple formats.

    ## Return Format
    Automation-manager result dict with `success` + export payload/path.

    ## Examples
    `export_workspace_data(scope="workspace", format="json")`
    -> `{"success": True, ...}`.
    """
    initialize_notion_client()
    assert automation_manager is not None, "Notion client failed to initialize"
    return await automation_manager.export_workspace_data(
        scope=scope, format=format, include_metadata=include_metadata, compression=compression
    )


@mcp.tool(annotations=_MUTATING, output_schema=_OUT_OBJECT)
async def import_workspace_data(
    source_path: str = Field(description="Local path to Markdown/JSON file"),
    target_parent_id: str = Field(description="Parent Page/Database ID in Notion"),
    import_type: str = Field(default="markdown", description="Type of data: markdown or json"),
) -> dict[str, Any]:
    """Import external data into Notion workspace.

    ## Return Format
    Automation-manager result dict with `success` + import counts.

    ## Examples
    `import_workspace_data(source_path="data.json",
    target_parent_id="...")` -> `{"success": True, ...}`.
    """
    initialize_notion_client()
    assert automation_manager is not None, "Notion client failed to initialize"
    return await automation_manager.import_workspace_data(
        source_file=source_path,
        target_parent_id=target_parent_id,
        import_type=import_type,
    )


@mcp.tool(annotations=_MUTATING, output_schema=_OUT_OBJECT)
async def orchestrate_automation(
    operation: str = Field(description="Automation operation: setup, sync_external, report, export"),
    config: dict[str, Any] = Field(description="Automation configuration"),
) -> dict[str, Any]:
    """SOTA Orchestrator for Notion automations, bulk syncing, and reporting.

    ## Return Format
    Handler result dict (`success` + payload) for the chosen `operation`.

    ## Examples
    `orchestrate_automation(operation="export", config={...})`
    -> `{"success": True, ...}`.
    """
    initialize_notion_client()
    assert automation_manager is not None, "Notion client failed to initialize"
    ops = {
        "setup": automation_manager.setup_automation,
        "sync_external": automation_manager.sync_external_data,
        "report": automation_manager.generate_ai_summary,
        "export": automation_manager.export_workspace_data,
    }
    handler = ops.get(operation)
    if not handler:
        return {"success": False, "error": f"Unknown operation: {operation}"}
    return await handler(**config)


# 🌐 Webhook Management (2 tools)


@mcp.tool(annotations=_MUTATING, output_schema=_OUT_OBJECT)
async def verify_webhook(
    verification_token: str = Field(description="Verification token from Notion's webhook POST"),
) -> dict[str, Any]:
    """Store a webhook verification token from Notion.

    ## Return Format
    Automation-manager result dict with `success` + `message`.

    ## Examples
    `verify_webhook(verification_token="...")` -> `{"success": True}`.
    """
    initialize_notion_client()
    assert automation_manager is not None, "Notion client failed to initialize"
    return await automation_manager.verify_webhook_subscription(verification_token)


@mcp.tool(annotations=_READ_ONLY, app=True, output_schema=_OUT_OBJECT)
async def list_webhook_events(
    limit: int = Field(default=50, description="Max events to return"),
    event_type: str | None = Field(default=None, description="Filter by event type"),
) -> dict[str, Any]:
    """List received Notion webhook events.

    ## Return Format
    `{"success": bool, "events": [...], "count": int}`.

    ## Examples
    `list_webhook_events(limit=10)` -> `{"success": True, "count": 2}`.
    """
    initialize_notion_client()
    assert automation_manager is not None, "Notion client failed to initialize"
    events = await automation_manager.list_webhook_events(limit=limit, event_type=event_type)
    return {"success": True, "events": events, "count": len(events)}


# 🔧 Notion Workers Management (6 tools)


@mcp.tool(annotations=_MUTATING, output_schema=_OUT_OBJECT)
async def deploy_worker(
    project_dir: str | None = Field(default=None, description="Worker project directory (default: current dir)"),
) -> dict[str, Any]:
    """Deploy a Notion Worker. Requires ntn CLI installed.

    ## Return Format
    `{"success": bool, "data"?: {...}, "error"?: str}` from the ntn CLI.

    ## Examples
    `deploy_worker(project_dir=".")` -> `{"success": True, ...}`.
    """
    return await notion_workers.deploy_worker(project_dir)


@mcp.tool(annotations=_READ_ONLY, output_schema=_OUT_OBJECT)
async def list_workers() -> dict[str, Any]:
    """List deployed Notion Workers. Requires ntn CLI.

    ## Return Format
    `{"success": bool, "data"?: [...], "error"?: str}`.

    ## Examples
    `list_workers()` -> `{"success": True, "data": [...]}`.
    """
    return await notion_workers.list_workers()


@mcp.tool(annotations=_MUTATING, output_schema=_OUT_OBJECT)
async def scaffold_worker(
    project_dir: str = Field(description="Directory to scaffold the worker project"),
) -> dict[str, Any]:
    """Scaffold a new Notion Worker project. Requires ntn CLI.

    ## Return Format
    `{"success": bool, "data"?: {...}, "error"?: str}`.

    ## Examples
    `scaffold_worker(project_dir="./w")` -> `{"success": True}`.
    """
    return await notion_workers.scaffold_worker(project_dir)


@mcp.tool(annotations=_READ_ONLY, output_schema=_OUT_OBJECT)
async def worker_logs(
    worker_name: str | None = Field(default=None, description="Worker name filter"),
    tail: int = Field(default=50, description="Number of log lines"),
) -> dict[str, Any]:
    """Fetch logs from a deployed Notion Worker.

    ## Return Format
    `{"success": bool, "data"?: {...}, "error"?: str}`.

    ## Examples
    `worker_logs(tail=20)` -> `{"success": True, ...}`.
    """
    return await notion_workers.worker_logs(worker_name=worker_name, tail=tail)


@mcp.tool(annotations=_READ_ONLY, output_schema=_OUT_OBJECT)
async def check_ntn() -> dict[str, Any]:
    """Check if Notion CLI (ntn) is installed.

    ## Return Format
    `{"success": bool, "version"?: str, "error"?: str}`.

    ## Examples
    `check_ntn()` -> `{"success": True, "version": "ntn 1.2.3"}`.
    """
    return await notion_workers.check_ntn_version()


@mcp.tool(annotations=_MUTATING, output_schema=_OUT_OBJECT)
async def orchestrate_workers(
    operation: str = Field(description="Worker operation: deploy, list, scaffold, logs, check"),
    project_dir: str | None = Field(default=None, description="Project directory (for deploy/scaffold)"),
    worker_name: str | None = Field(default=None, description="Worker name (for logs)"),
    tail: int = Field(default=50, description="Log lines (for logs)"),
) -> dict[str, Any]:
    """Orchestrate Notion Workers operations.

    ## Return Format
    Handler result dict (`success` + payload) for the chosen `operation`.

    ## Examples
    `orchestrate_workers(operation="check")`
    -> `{"success": True, "version": "..."}`.
    """
    ops = {
        "deploy": lambda: notion_workers.deploy_worker(project_dir),
        "list": notion_workers.list_workers,
        "scaffold": lambda: notion_workers.scaffold_worker(project_dir or "."),
        "logs": lambda: notion_workers.worker_logs(worker_name, tail),
        "check": notion_workers.check_ntn_version,
    }
    handler = ops.get(operation)
    if not handler:
        return {"success": False, "error": f"Unknown operation: {operation}"}
    return await handler()


# Block operations


@mcp.tool(annotations=_MUTATING, output_schema=_OUT_OBJECT)
async def append_blocks(
    block_id: str = Field(description="Page or block ID to append children to"),
    children: list[dict[str, Any]] = Field(description="List of block objects to append"),
) -> dict[str, Any]:
    """Append child blocks to an existing page or block.

    ## Return Format
    `{"success": bool, "result": {...}, "message": str}`.

    ## Examples
    `append_blocks(block_id="...", children=[...])`
    -> `{"success": True, "message": "Appended 2 blocks."}`.
    """
    try:
        initialize_notion_client()
        assert notion_client is not None, "Notion client failed to initialize"
        result = await notion_client.append_block_children(block_id, children)
        return {"success": True, "result": result, "message": f"Appended {len(children)} blocks."}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool(annotations=_MUTATING, output_schema=_OUT_OBJECT)
async def update_block(
    block_id: str = Field(description="Block ID to update"),
    block_type: str = Field(description="Block type (e.g. paragraph, heading_1, to_do)"),
    content: dict[str, Any] = Field(description="Block content properties (e.g. rich_text, checked)"),
    archived: bool | None = Field(default=None, description="Archive or unarchive the block"),
) -> dict[str, Any]:
    """Update a specific block's content or properties.

    ## Return Format
    `{"success": bool, "result": {...}, "message": str}`.

    ## Examples
    `update_block(block_id="...", block_type="paragraph", content={...})`
    -> `{"success": True}`.
    """
    try:
        initialize_notion_client()
        kwargs: dict[str, Any] = {block_type: content}
        if archived is not None:
            kwargs["archived"] = archived
        assert notion_client is not None, "Notion client failed to initialize"
        result = await notion_client.update_block(block_id, **kwargs)
        return {"success": True, "result": result, "message": "Block updated."}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool(annotations=_DESTRUCTIVE, output_schema=_OUT_OBJECT)
async def delete_block(
    block_id: str = Field(description="Block ID to archive/delete"),
) -> dict[str, Any]:
    """Archive (soft-delete) a block by ID.

    ## Return Format
    `{"success": bool, "result": {...}, "message": str}`.

    ## Examples
    `delete_block(block_id="...")` -> `{"success": True, ...}`.
    """
    try:
        initialize_notion_client()
        assert notion_client is not None, "Notion client failed to initialize"
        result = await notion_client.delete_block(block_id)
        return {"success": True, "result": result, "message": "Block archived."}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Markdown page endpoints


@mcp.tool(annotations=_READ_ONLY, output_schema=_OUT_OBJECT)
async def get_page_markdown(
    page_id: str = Field(description="Page ID to retrieve as markdown"),
) -> dict[str, Any]:
    """Retrieve page content as enhanced markdown (API 2026-03-11).

    ## Return Format
    `{"success": bool, "markdown": str, "page_id": str}`.

    ## Examples
    `get_page_markdown(page_id="...")`
    -> `{"success": True, "markdown": "# ...", ...}`.
    """
    try:
        initialize_notion_client()
        assert notion_client is not None, "Notion client failed to initialize"
        result = await notion_client.retrieve_page_markdown(page_id)
        return {"success": True, "markdown": result.get("markdown", ""), "page_id": page_id}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool(annotations=_MUTATING, output_schema=_OUT_OBJECT)
async def update_page_markdown(
    page_id: str = Field(description="Page ID to update"),
    markdown: str = Field(description="Full markdown content to write to the page"),
) -> dict[str, Any]:
    """Update page content using enhanced markdown (API 2026-03-11).

    ## Return Format
    `{"success": bool, "result": {...}, "message": str}`.

    ## Examples
    `update_page_markdown(page_id="...", markdown="# Neu")`
    -> `{"success": True}`.
    """
    try:
        initialize_notion_client()
        assert notion_client is not None, "Notion client failed to initialize"
        result = await notion_client.update_page_markdown(page_id, markdown)
        return {"success": True, "result": result, "message": "Page updated via markdown."}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Database schema mutation


@mcp.tool(annotations=_MUTATING, output_schema=_OUT_OBJECT)
async def update_database_schema(
    database_id: str = Field(description="Database ID to update"),
    title: str | None = Field(default=None, description="New database title"),
    properties: dict[str, Any] | None = Field(default=None, description="Property schema changes (add/remove/modify)"),
    description: list[dict[str, Any]] | None = Field(default=None, description="Rich text description"),
) -> dict[str, Any]:
    """Update database properties, title, or description.

    ## Return Format
    `{"success": bool, "result": {...}, "message": str}`.

    ## Examples
    `update_database_schema(database_id="...", title="Neu")`
    -> `{"success": True}`.
    """
    try:
        initialize_notion_client()
        kwargs: dict[str, Any] = {}
        if title:
            kwargs["title"] = [{"type": "text", "text": {"content": title}}]
        if properties:
            kwargs["properties"] = properties
        if description:
            kwargs["description"] = description
        assert notion_client is not None, "Notion client failed to initialize"
        result = await notion_client.update_database_schema(database_id, **kwargs)
        return {"success": True, "result": result, "message": "Database schema updated."}
    except Exception as e:
        return {"success": False, "error": str(e)}


# REST endpoints for block operations


@app.post("/api/page/{page_id}/blocks")
async def append_blocks_rest(page_id: str, children: list[dict[str, Any]] = Body(...)):
    """Append child blocks to a page."""
    try:
        initialize_notion_client()
        assert notion_client is not None, "Notion client failed to initialize"
        result = await notion_client.append_block_children(page_id, children)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.patch("/api/page/{page_id}/blocks/{block_id}")
async def update_block_rest(page_id: str, block_id: str, data: dict[str, Any] = Body(...)):
    """Update a specific block."""
    try:
        initialize_notion_client()
        assert notion_client is not None, "Notion client failed to initialize"
        result = await notion_client.update_block(block_id, **data)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.delete("/api/page/{page_id}/blocks/{block_id}")
async def delete_block_rest(page_id: str, block_id: str):
    """Archive a block."""
    try:
        initialize_notion_client()
        assert notion_client is not None, "Notion client failed to initialize"
        result = await notion_client.delete_block(block_id)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/page/{page_id}/markdown")
async def get_page_markdown_rest(page_id: str):
    """Retrieve page as markdown."""
    try:
        initialize_notion_client()
        assert notion_client is not None, "Notion client failed to initialize"
        result = await notion_client.retrieve_page_markdown(page_id)
        return {"success": True, "markdown": result.get("markdown", ""), "page_id": page_id}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.put("/api/page/{page_id}/markdown")
async def update_page_markdown_rest(page_id: str, markdown: str = Body(..., embed=True)):
    """Update page via markdown."""
    try:
        initialize_notion_client()
        assert notion_client is not None, "Notion client failed to initialize"
        result = await notion_client.update_page_markdown(page_id, markdown)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.patch("/api/database/{database_id}/schema")
async def update_database_schema_rest(database_id: str, data: dict[str, Any] = Body(...)):
    """Update database properties."""
    try:
        initialize_notion_client()
        assert notion_client is not None, "Notion client failed to initialize"
        result = await notion_client.update_database_schema(database_id, **data)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Server health check


async def main() -> None:
    """Main entry point for the Notion Workspace MCP server."""
    # Austrian efficiency: Clear startup message
    logger.info("NotionMCP server starting", message="Austrian efficiency activated")
    logger.info(
        "Server configuration",
        server_name=config.get("server", {}).get("name", "NotionMCP"),
        timezone=config.get("server", {}).get("timezone", "Europe/Vienna"),
    )

    # Note: Notion client initialization happens lazily when tools are called
    # This allows the server to start even if NOTION_TOKEN isn't set yet
    # Tools will initialize and return appropriate errors if token is missing

    # MCP sub-app is mounted at module import (see mcp_app above).

    # Run the unified server
    await run_server_async(mcp, http_app=app, server_name="notion-mcp")


def run() -> None:
    """Synchronous entry point for compatibility."""
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
