# NotionMCP - Comprehensive Notion Workspace Management

**FastMCP 2.0 Implementation with Austrian Efficiency 🇦🇹**

A powerful MCP (Model Context Protocol) server for comprehensive Notion workspace management, built with Austrian efficiency for academic research, project organization, and weeb content management.

## 🎯 Overview

NotionMCP provides 18 comprehensive tools for managing Notion workspaces through Claude Desktop Pro. Perfect for Sandra's academic work, research organization, anime tracking, and Vienna-based workflow optimization.

### ✨ Key Features

- **🗃️ Complete Page Management**: Create, update, search, and organize pages with German/Japanese character support
- **📊 Database Operations**: Complex queries, bulk import/export, schema management
- **💬 Collaboration Tools**: Comments, user management, workspace permissions
- **🤖 AI Integration**: Content analysis, automated summaries, research assistance
- **⚡ Automation**: Webhooks, external data sync, workflow automation
- **🇦🇹 Austrian Context**: Vienna timezone, German characters, budget awareness (~€100/month)
- **🎌 Weeb Support**: Japanese characters, anime/manga databases, language learning tools

## 🚀 Quick Start (5 Minutes)

### Prerequisites

- Python 3.8+
- Notion account with integration token
- Claude Desktop Pro with MCP support

### Installation

```bash
# Clone and setup
git clone <repository-url>
cd notionmcp

# Install dependencies (Austrian efficiency)
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your NOTION_TOKEN

# Test connection
python server.py
```

### Get Your Notion Token

1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Name it "NotionMCP" and copy the token
4. Add the integration to your workspaces
5. Paste token in `.env` file

## 🛠️ Tool Reference (18 Tools)

### 📄 Page Management (5 tools)

| Tool | Description | Example Use |
|------|-------------|-------------|
| `create_page` | Create pages with content and properties | Research notes, project docs |
| `update_page` | Update existing page content/properties | Status updates, content revisions |
| `get_page_content` | Retrieve complete page with blocks | Content analysis, backup |
| `search_pages` | Natural language search across workspace | Find research by topic |
| `archive_page` | Safely archive or delete pages | Project cleanup, organization |

### 🗄️ Database Operations (6 tools)

| Tool | Description | Example Use |
|------|-------------|-------------|
| `create_database` | Create databases with custom schemas | Anime tracker, research DB |
| `query_database` | Complex filtering and sorting | Find incomplete tasks |
| `create_database_entry` | Add entries with all property types | Add new anime, research paper |
| `update_database_entry` | Update existing entries | Mark complete, update rating |
| `get_database_schema` | Analyze database structure | Schema planning, validation |
| `bulk_import_data` | Import CSV/JSON data efficiently | Research data migration |

### 💬 Collaboration (3 tools)

| Tool | Description | Example Use |
|------|-------------|-------------|
| `add_comment` | Add comments to pages/blocks | Academic feedback, discussions |
| `get_comments` | Retrieve comment threads | Review feedback, conversations |
| `get_workspace_users` | List workspace users and permissions | Team management, access control |

### 🔍 Advanced Features (4 tools)

| Tool | Description | Example Use |
|------|-------------|-------------|
| `setup_automation` | Create workflow automations | Auto-notifications, triggers |
| `sync_external_data` | Sync from external sources | GitHub repos, research APIs |
| `generate_ai_summary` | AI-powered content analysis | Research summaries, insights |
| `export_workspace_data` | Backup and export functionality | Data backup, migration |

## 🇦🇹 Austrian Efficiency Features

### Direct Communication

- **No gaslighting**: Clear error messages about what actually failed
- **Honest limitations**: Explicit about Notion API constraints
- **Actionable feedback**: Specific next steps when operations fail

### Budget Awareness (~€100/month)

- **Efficient API usage**: Intelligent batching and caching
- **Rate limit respect**: Smart request patterns to avoid costs
- **Usage monitoring**: Track API calls and optimize performance

### Vienna Context

- **Timezone**: Proper Europe/Vienna date/time handling
- **German support**: Full UTF-8 for ä, ö, ü, ß in content
- **Date format**: DD.MM.YYYY Austrian standard
- **Academic workflows**: Optimized for research and knowledge management

### Weeb-Friendly 🎌

- **Japanese support**: Full Unicode for 日本語 content
- **Anime tracking**: Pre-built database templates for anime/manga
- **Language learning**: Vocabulary and progress tracking tools

## 🔧 Configuration

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

## 📚 Usage Examples

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
    content="Revolutionary transformer architecture paper..."
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
    title="Anime Collection 🎌",
    parent_id="page_id", 
    properties_schema={
        "Title": "title",
        "Status": {"type": "select", "options": ["Watching", "Completed", "Plan to Watch", "Dropped"]},
        "Rating": "number",
        "Episodes": "number",
        "Genre": "multi_select",
        "Studio": "rich_text"
    },
    icon="🎌"
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

## 🧪 Testing

```bash
# Run all tests
pytest

# Test with coverage
pytest --cov=notion --cov-report=html

# Integration tests (requires real Notion workspace)
pytest tests/integration_tests.py -v

# Austrian efficiency: Fast unit tests only
pytest tests/test_api.py -v
```

## 🤝 Development

### Austrian Efficiency Guidelines

1. **Direct communication**: No euphemisms, clear error messages
2. **Budget awareness**: Optimize for ~€100/month AI tools budget
3. **Real implementation**: No stubs, everything fully functional
4. **Vienna context**: Proper timezone and character encoding
5. **Academic focus**: Research and knowledge management optimization

### Project Structure

```
notionmcp/
├── config/           # YAML configurations
├── docs/             # Documentation
├── notion/           # Core Notion modules
│   ├── client.py     # API client
│   ├── pages.py      # Page operations
│   ├── databases.py  # Database operations
│   ├── collaboration.py # Comments & users
│   └── automations.py   # AI & automation
├── tests/            # Test suite
└── server.py         # FastMCP 2.0 entry point
```

## 📖 Documentation

- **[API Reference](docs/API.md)**: Complete tool documentation
- **[Configuration Guide](docs/Configuration.md)**: Setup and customization
- **[Troubleshooting](docs/Troubleshooting.md)**: Common issues and solutions

## 🔒 Security

- **Token security**: Never commit tokens to git
- **Minimal permissions**: Grant only necessary access scopes
- **Rate limiting**: Respect Notion API limits
- **Budget monitoring**: Track usage to avoid unexpected costs

## 🐛 Troubleshooting

### Common Issues

**Authentication Error**

```
Error: Notion API token is invalid or expired
Solution: Check your NOTION_TOKEN in .env file
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

## 💡 Tips for Austrian Efficiency

1. **Use templates**: Pre-configured academic and weeb databases
2. **Batch operations**: Use bulk_import_data for large datasets
3. **Smart caching**: Enable caching to reduce API calls
4. **Vienna timezone**: All dates automatically in European format
5. **German characters**: Full support for ä, ö, ü, ß in content
6. **Budget monitoring**: Track API usage to stay within limits

## 📄 License

MIT License with Austrian context - see LICENSE file for details.

---

**Built with Austrian efficiency in Vienna 🇦🇹**  
*Sin temor y sin esperanza* - practical Notion management without hype.

**Perfect for:** Academic research • Project management • Anime tracking • Knowledge organization • Vienna workflows
