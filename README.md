# NotionMCP - Comprehensive Notion Knowledge Orchestrator

[![FastMCP Version](https://img.shields.io/badge/FastMCP-3.1.0-blue?style=flat-square&logo=python&logoColor=white)](https://github.com/sandraschi/fastmcp) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![Linted with Biome](https://img.shields.io/badge/Linted_with-Biome-60a5fa?style=flat-square&logo=biome&logoColor=white)](https://biomejs.dev/) [![Built with Just](https://img.shields.io/badge/Built_with-Just-000000?style=flat-square&logo=gnu-bash&logoColor=white)](https://github.com/casey/just)

**FastMCP 3.1.0 Implementation with Austrian Efficiency **

**Status: Production-Ready (SOTA 2026)** - High-performance RAG and Semantic Search  
**Version: 1.1.0-RAG** - Latest: FastMCP 3.1.0 migration, LanceDB core, and functional Dashboard

NotionMCP is a powerful MCP (Model Context Protocol) server and web application for comprehensive Notion workspace management and semantic knowledge retrieval. Built with Austrian efficiency for academic research, project organization, and RAG-powered intelligence.

> [!IMPORTANT]
> **FastMCP 3.1.0 Alignment**: This repository is fully compliant with the February 2026 Fleet Standard.

##  Overview

NotionMCP provides 21 comprehensive tools for managing Notion workspaces and performing semantic discovery. It features a local RAG pipeline using LanceDB for private, high-performance knowledge retrieval.

###  Key SOTA Features

- ** Neural Intelligence (RAG)**: Built-in LanceDB vector core for semantic search and context-aware chat
- ** SOTA Dashboard**: Functional web interface with real-time Notion telemetry and LLM "Glom On" discovery
- ** complete Page Management**: Create, update, search, and organize pages with German/Japanese character support
- ** Semantic Search**: Discover knowledge using meaning and intent across your entire workspace
- ** Austrian Reliability**: Zero first-time failures, strict rate limit awareness, and Europe/Vienna context

##  Quick Start (5 Minutes)

### Prerequisites

- Python 3.11+
- Notion account with integration token
- Claude Desktop Pro with MCP support (or Cursor with MCP)
- FastMCP 3.1.0+

##  Installation

### Prerequisites
- [uv](https://docs.astral.sh/uv/) installed (RECOMMENDED)
- Python 3.12+

###  Quick Start
Run immediately via `uvx`:
```bash
uvx notion-mcp
```

###  Claude Desktop Integration
Add to your `claude_desktop_config.json`:
```json
"mcpServers": {
  "notion-mcp": {
    "command": "uv",
    "args": ["--directory", "D:/Dev/repos/notion-mcp", "run", "notion-mcp"]
  }
}
```
### Get Your Notion Token

1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Name it "NotionMCP" and copy the token
4. Add the integration to your workspaces
5. Paste token in `.env` file

##  Tool Reference (18 Tools)

###  Page Management (5 tools)

| Tool | Description | Example Use |
|------|-------------|-------------|
| `create_page` | Create pages with content and properties | Research notes, project docs |
| `update_page` | Update existing page content/properties | Status updates, content revisions |
| `get_page_content` | Retrieve complete page with blocks | Content analysis, backup |
| `search_pages` | Natural language search across workspace | Find research by topic |
| `archive_page` | Safely archive or delete pages | Project cleanup, organization |

###  Database Operations (6 tools)

| Tool | Description | Example Use |
|------|-------------|-------------|
| `create_database` | Create databases with custom schemas | Anime tracker, research DB |
| `query_database` | Complex filtering and sorting | Find incomplete tasks |
| `create_database_entry` | Add entries with all property types | Add new anime, research paper |
| `update_database_entry` | Update existing entries | Mark complete, update rating |
| `get_database_schema` | Analyze database structure | Schema planning, validation |
| `bulk_import_data` | Import CSV/JSON data efficiently | Research data migration |

###  Collaboration (3 tools)

| Tool | Description | Example Use |
|------|-------------|-------------|
| `add_comment` | Add comments to pages/blocks | Academic feedback, discussions |
| `get_comments` | Retrieve comment threads | Review feedback, conversations |
| `get_workspace_users` | List workspace users and permissions | Team management, access control |

###  Neural Discovery (RAG) (3 tools) [NEW]

| Tool | Description | Example Use |
|------|-------------|-------------|
| `sync_rag_index` | Synchronize Notion workspace with local LanceDB vector store | Initialization of RAG core |
| `search_notion_knowledge` | Semantic search across indexed Notion pages using embeddings | Context-aware research discovery |
| `clear_rag_index` | Safely wipe the local vector database | Security cleanup, re-indexing |

###  Advanced Features (4 tools)

| Tool | Description | Example Use |
|------|-------------|-------------|
| `setup_automation` | Create workflow automations | Auto-notifications, triggers |
| `sync_external_data` | Sync from external sources | GitHub repos, research APIs |
| `generate_ai_summary` | AI-powered content analysis | Research summaries, insights |
| `export_workspace_data` | Backup and export functionality | Data backup, migration |

##  Austrian Efficiency Features

### Direct Communication

- **No gaslighting**: Clear error messages about what actually failed
- **Honest limitations**: Explicit about Notion API constraints
- **Actionable feedback**: Specific next steps when operations fail

### Budget Awareness (~100/month)

- **Efficient API usage**: Intelligent batching and caching
- **Rate limit respect**: Smart request patterns to avoid costs
- **Usage monitoring**: Track API calls and optimize performance

### Vienna Context

- **Timezone**: Proper Europe/Vienna date/time handling
- **German support**: Full UTF-8 for , , ,  in content
- **Date format**: DD.MM.YYYY Austrian standard
- **Academic workflows**: Optimized for research and knowledge management

### Weeb-Friendly 

- **Japanese support**: Full Unicode for  content
- **Anime tracking**: Pre-built database templates for anime/manga
- **Language learning**: Vocabulary and progress tracking tools

##  Configuration

### Environment Variables

```bash
# Required
NOTION_TOKEN=secret_your_token_here

# Austrian Context (Optional)
TIMEZONE=Europe/Vienna
DATE_FORMAT=DD.MM.YYYY
LANGUAGE=de

# Performance (Optional)
MAX_RESULTS_PER_PAGE=100
CACHE_DURATION=300
ENABLE_CACHING=true
```

### Academic Templates

Pre-configured database templates for:

- **Research papers**: Authors, citations, status tracking
- **Project management**: Tasks, deadlines, progress
- **Bibliography**: Citation management with multiple formats
- **Note organization**: Hierarchical knowledge structure

### Weeb Templates

Ready-to-use databases for:

- **Anime tracking**: Status, rating, episodes, genres
- **Manga collection**: Reading progress, series management  
- **Japanese learning**: Vocabulary, JLPT levels, practice
- **Character databases**: Favorites, stats, series connections

##  Usage Examples

### Academic Research Workflow

```python
# Create research database
await create_database(
    title="Machine Learning Research",
    parent_id="page_id",
    properties_schema={
        "Title": "title",
        "Authors": "multi_select", 
        "Year": "number",
        "Status": {"type": "select", "options": ["Reading", "Read", "Cited"]},
        "Rating": "number",
        "Notes": "rich_text"
    }
)

# Add research paper
await create_database_entry(
    database_id="db_id",
    properties={
        "Title": "Attention Is All You Need",
        "Authors": ["Vaswani", "Shazeer", "Parmar"],
        "Year": 2017,
        "Status": "Read",
        "Rating": 5
    },
    content=" transformer architecture paper..."
)

# Query by status
results = await query_database(
    database_id="db_id",
    filter={"Status": {"select": {"equals": "Reading"}}},
    sorts=[{"property": "Year", "direction": "descending"}]
)
```

### Anime Tracking

```python
# Create anime database
await create_database(
    title="Anime Collection ",
    parent_id="page_id", 
    properties_schema={
        "Title": "title",
        "Status": {"type": "select", "options": ["Watching", "Completed", "Plan to Watch", "Dropped"]},
        "Rating": "number",
        "Episodes": "number",
        "Genre": "multi_select",
        "Studio": "rich_text"
    },
    icon=""
)

# Add anime entry
await create_database_entry(
    database_id="anime_db_id",
    properties={
        "Title": "Attack on Titan",
        "Status": "Completed",
        "Rating": 9,
        "Episodes": 75,
        "Genre": ["Action", "Drama", "Fantasy"],
        "Studio": "MAPPA"
    }
)
```

### AI-Powered Analysis

```python
# Generate research summary
summary = await generate_ai_summary(
    page_id="research_page_id",
    summary_type="comprehensive", 
    length="medium",
    focus_areas=["methodology", "results", "implications"]
)

# Export workspace for backup
backup = await export_workspace_data(
    scope="workspace",
    format="json",
    include_metadata=True,
    compression=True
)
```

##  Testing

```bash
# Run all tests
make test
# or
pytest tests/ -v

# Run unit tests only
make test-unit
# or
pytest tests/ -v -m "not integration and not slow"

# Run integration tests only
make test-integration
# or
pytest tests/ -v -m integration

# Test with coverage
make test-coverage
# or
pytest tests/ --cov=notion --cov-report=html

# Austrian efficiency: Fast unit tests only
pytest tests/test_api.py -v
```

##  Development

### Austrian Efficiency Guidelines

1. **Direct communication**: No euphemisms, clear error messages
2. **Budget awareness**: Optimize for ~100/month AI tools budget
3. **Real implementation**: No stubs, everything fully functional
4. **Vienna context**: Proper timezone and character encoding
5. **Academic focus**: Research and knowledge management optimization

### Development Commands

```bash
# Install development dependencies
make install-dev

# Run linting
make lint
# or
ruff check server.py notion/ tests/

# Format code
make format
# or
ruff format server.py notion/ tests/

# Type checking
make type-check
# or
mypy server.py notion/ --ignore-missing-imports

# Run all checks
make check
```

### Project Structure

```
notionmcp/
 config/           # YAML configurations
 docs/             # Documentation
 notion/           # Core Notion modules
    client.py     # API client
    pages.py      # Page operations
    databases.py  # Database operations
    collaboration.py # Comments & users
    automations.py   # AI & automation
 tests/            # Test suite
    test_api.py  # Unit tests
    integration_tests.py  # Integration tests
 server.py         # FastMCP 3.1.0 entry point
```

##  Documentation

- **[API Reference](docs/API.md)**: Complete tool documentation
- **[Configuration Guide](docs/Configuration.md)**: Setup and customization
- **[Troubleshooting](docs/Troubleshooting.md)**: Common issues and solutions

##  Security

- **Token security**: Never commit tokens to git
- **Minimal permissions**: Grant only necessary access scopes
- **Rate limiting**: Respect Notion API limits
- **Budget monitoring**: Track usage to avoid unexpected costs

##  Troubleshooting

### Common Issues

**Server Won't Start in Cursor**

```
Issue: Server fails to start in Cursor IDE
Solution: 
1. Ensure NOTION_TOKEN is set in Cursor MCP settings
2. Check that cwd points to the notion-mcp directory
3. Verify Python 3.11+ is in PATH
4. See CURSOR_FIX.md for detailed setup instructions
```

**Authentication Error**

```
Error: Notion API token is invalid or expired
Solution: Check your NOTION_TOKEN in .env file or Cursor MCP settings
```

**Permission Denied**

```
Error: The requested page/database was not found
Solution: Add your integration to the workspace containing the content
```

**Rate Limited**

```
Error: Rate limit exceeded
Solution: Wait 60 seconds and retry, check your usage patterns
```

**Import Errors**

```
Error: ModuleNotFoundError or import failures
Solution: 
1. Install dependencies: uv pip install -r requirements.txt
2. Check PYTHONPATH includes notion-mcp directory
3. Verify all dependencies are installed: pip list
```

##  Tips for Austrian Efficiency

1. **Use templates**: Pre-configured academic and weeb databases
2. **Batch operations**: Use bulk_import_data for large datasets
3. **Smart caching**: Enable caching to reduce API calls
4. **Vienna timezone**: All dates automatically in European format
5. **German characters**: Full support for , , ,  in content
6. **Budget monitoring**: Track API usage to stay within limits


## 🛡️ Industrial Quality Stack

This project adheres to **SOTA 14.1** industrial standards for high-fidelity agentic orchestration:

- **Python (Core)**: [Ruff](https://astral.sh/ruff) for linting and formatting. Zero-tolerance for `print` statements in core handlers (`T201`).
- **Webapp (UI)**: [Biome](https://biomejs.dev/) for sub-millisecond linting. Strict `noConsoleLog` enforcement.
- **Protocol Compliance**: Hardened `stdout/stderr` isolation to ensure crash-resistant JSON-RPC communication.
- **Automation**: [Justfile](./justfile) recipes for all fleet operations (`just lint`, `just fix`, `just dev`).
- **Security**: Automated audits via `bandit` and `safety`.

##  License

MIT License with Austrian context - see LICENSE file for details.

---

**Built with Austrian efficiency in Vienna **  
*Sin temor y sin esperanza* - practical Notion management without hype.

** for:** Academic research  Project management  Anime tracking  Knowledge organization  Vienna workflows


##  Webapp Dashboard (SOTA 2026)

This MCP server includes a premium, functional web interface for monitoring and control.
By default, the web dashboard runs on port **10810**.
*(Assigned ports: **10810** (Frontend), **10811** (FastAPI Backend))*

- **Real-time Telemetry**: Live Notion workspace stats
- **RAG Chat**: Context-aware chat with Citations
- **Semantic Discovery**: Visual search results from LanceDB
- **LLM Discovery**: Automated hardware detection (Ollama/LM Studio)

To start the webapp:
1. Navigate to the `web_sota` directory.
2. Run `start.bat` (Windows) or `./start.ps1` (PowerShell).
3. Open `http://localhost:10810` in your browser.
