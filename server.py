#!/usr/bin/env python3
"""
NotionMCP - Comprehensive Notion Workspace Management MCP Server
FastMCP 2.14.1 Implementation with Austrian Efficiency

Built for Claude Desktop Pro + MCP setup
Author: Sandra (Vienna, Austria) 🇦🇹
Date: July 22, 2025
Context: Academic knowledge management + weeb organization + direct communication

Status: Beta - Actively developed, API may change
"""

import asyncio
import os
import sys
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import structlog
import yaml
from fastmcp import FastMCP
from pydantic import Field

from notion.client import NotionClient
from notion.pages import PageManager
from notion.databases import DatabaseManager
from notion.collaboration import CollaborationManager
from notion.automations import AutomationManager

# Configure structured logging (JSON to stderr only)
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
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Load configuration with Austrian context
def load_config() -> Dict[str, Any]:
    """Load configuration from YAML files with Vienna defaults"""
    config_path = os.path.join(os.path.dirname(__file__), "config", "settings.yaml")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logger.info("Configuration loaded", config_path=config_path)
        return config
    except FileNotFoundError:
        logger.warning("Config file not found, using defaults", config_path=config_path)
        return {
            "server": {
                "name": "Notion Workspace Management MCP 🗃️",
                "timezone": "Europe/Vienna",
                "language": "de"
            }
        }

# Server lifespan for startup/shutdown lifecycle
@asynccontextmanager
async def server_lifespan(app: FastMCP):
    """Server lifespan context manager for FastMCP 2.14.1+."""
    # Startup
    logger.info("Starting NotionMCP Server", version="1.0.0", fastmcp_version="2.14.1")
    try:
        yield
    finally:
        # Shutdown
        logger.info("Shutting down NotionMCP Server")

# FastMCP 2.14.1 Server Setup with comprehensive instructions
app = FastMCP(
    "Notion Workspace Management MCP 🗃️",
    instructions="""You are NotionMCP, a comprehensive MCP server for Notion workspace management with Austrian efficiency.

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
- Language: German characters (ä, ö, ü, ß) fully supported
- Budget: Optimized for ~€100/month AI tools budget
- Academic focus: Research and knowledge management workflows

ERROR HANDLING:
- Authentication errors include token setup instructions
- Permission errors specify which workspace needs access
- Rate limit errors provide wait time and optimization suggestions
- Direct communication: No euphemisms, clear actionable feedback""",
    lifespan=server_lifespan
)
config = load_config()

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
    
    # Check for NOTION_TOKEN
    token = os.getenv("NOTION_TOKEN")
    if not token:
        raise ValueError("NOTION_TOKEN environment variable is required. Get your integration token from: https://www.notion.so/my-integrations")
    
    try:
        notion_client = NotionClient(
            token=token,
            version=os.getenv("NOTION_VERSION", "2022-06-28"),
            timeout=int(os.getenv("NOTION_TIMEOUT", "30"))
        )
        
        # Initialize managers
        page_manager = PageManager(notion_client)
        db_manager = DatabaseManager(notion_client)
        collab_manager = CollaborationManager(notion_client)
        automation_manager = AutomationManager(notion_client)
        
        logger.info("Notion client initialized successfully", message="Austrian efficiency activated")
    except Exception as e:
        logger.error("Failed to initialize Notion client", error=str(e))
        raise

# 📄 Page Management Tools (5 tools)

@app.tool()
async def create_page(
    title: str = Field(description="Page title (supports German characters: ä, ö, ü, ß)"),
    content: str = Field(default="", description="Page content in Notion blocks format or plain text"),
    parent_id: Optional[str] = Field(default=None, description="Parent page/database ID. If not provided, creates in workspace root"),
    properties: Optional[Dict[str, Any]] = Field(default=None, description="Page properties if parent is a database"),
    children: Optional[List[Dict[str, Any]]] = Field(default=None, description="Child blocks to add to the page")
) -> Dict[str, Any]:
    """Create a new Notion page with content, properties, and Austrian efficiency."""
    try:
        initialize_notion_client()  # Ensure client is initialized
        result = await page_manager.create_page(
            title=title,
            content=content,
            parent_id=parent_id,
            properties=properties,
            children=children
        )
        logger.info("Page created successfully", page_title=title, page_id=result["id"])
        return {
            "success": True,
            "page_id": result["id"],
            "url": result.get("url", ""),
            "title": title,
            "message": f"Page '{title}' created with Austrian efficiency! ✅"
        }
    except Exception as e:
        logger.error("Failed to create page", page_title=title, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "message": "Page creation failed - check your permissions and parent_id"
        }

@app.tool()
async def update_page(
    page_id: str = Field(description="Page ID to update"),
    title: Optional[str] = Field(default=None, description="New page title"),
    content: Optional[str] = Field(default=None, description="New page content"),
    properties: Optional[Dict[str, Any]] = Field(default=None, description="Updated properties"),
    archived: Optional[bool] = Field(default=None, description="Archive status")
) -> Dict[str, Any]:
    """Update existing Notion page with Austrian efficiency."""
    try:
        result = await page_manager.update_page(
            page_id=page_id,
            title=title,
            content=content,
            properties=properties,
            archived=archived
        )
        logger.info("Page updated successfully", page_id=page_id)
        return {
            "success": True,
            "page_id": page_id,
            "updated_fields": [k for k, v in locals().items() if v is not None and k != "page_id"],
            "message": "Page updated with Austrian efficiency! ✅"
        }
    except Exception as e:
        logger.error("Failed to update page", page_id=page_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "message": "Page update failed - check page ID and permissions"
        }

@app.tool()
async def get_page_content(
    page_id: str = Field(description="Page ID to retrieve"),
    include_children: bool = Field(default=True, description="Include child blocks"),
    block_depth: int = Field(default=10, description="Maximum depth for nested blocks")
) -> Dict[str, Any]:
    """Retrieve complete page content with Austrian efficiency optimization."""
    try:
        result = await page_manager.get_page_content(
            page_id=page_id,
            include_children=include_children,
            block_depth=block_depth
        )
        logger.info("Page content retrieved", page_id=page_id)
        return {
            "success": True,
            "page": result,
            "message": "Page content retrieved with Austrian efficiency! ✅"
        }
    except Exception as e:
        logger.error("Failed to get page content", page_id=page_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "message": "Page retrieval failed - check page ID and permissions"
        }

@app.tool()
async def search_pages(
    query: str = Field(description="Search query (natural language)"),
    filter_by_type: Optional[str] = Field(default=None, description="Filter by object type: page, database"),
    sort_by: str = Field(default="last_edited_time", description="Sort field: last_edited_time, created_time"),
    limit: int = Field(default=10, description="Maximum results to return")
) -> Dict[str, Any]:
    """Natural language search across entire Notion workspace."""
    try:
        results = await page_manager.search_pages(
            query=query,
            filter_by_type=filter_by_type,
            sort_by=sort_by,
            limit=limit
        )
        logger.info(f"Search completed for query: {query}")
        return {
            "success": True,
            "results": results,
            "count": len(results),
            "query": query,
            "message": f"Found {len(results)} results with Austrian efficiency! 🔍"
        }
    except Exception as e:
        logger.error(f"Search failed for query '{query}': {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Search failed - check your query and try again"
        }

@app.tool()
async def archive_page(
    page_id: str = Field(description="Page ID to archive"),
    permanent_delete: bool = Field(default=False, description="Permanently delete instead of archive"),
    backup_first: bool = Field(default=True, description="Create backup before deletion")
) -> Dict[str, Any]:
    """Safely archive or delete pages with Austrian efficiency confirmations."""
    try:
        await page_manager.archive_page(
            page_id=page_id,
            permanent_delete=permanent_delete,
            backup_first=backup_first
        )
        action = "deleted" if permanent_delete else "archived"
        logger.info("Page archived/deleted", page_id=page_id, action=action, backup_created=backup_first)
        return {
            "success": True,
            "page_id": page_id,
            "action": action,
            "backup_created": backup_first,
            "message": f"Page {action} with Austrian efficiency! ✅"
        }
    except Exception as e:
        logger.error("Failed to archive page", page_id=page_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "message": "Archive operation failed - check page ID and permissions"
        }

# 🗄️ Database Operations (6 tools)

@app.tool()
async def create_database(
    title: str = Field(description="Database title"),
    parent_id: str = Field(description="Parent page ID where database will be created"),
    properties_schema: Dict[str, Any] = Field(description="Database properties schema"),
    icon: Optional[str] = Field(default=None, description="Database icon (emoji or external URL)"),
    cover: Optional[str] = Field(default=None, description="Database cover image URL")
) -> Dict[str, Any]:
    """Create databases with custom property schemas."""
    try:
        result = await db_manager.create_database(
            title=title,
            parent_id=parent_id,
            properties_schema=properties_schema,
            icon=icon,
            cover=cover
        )
        logger.info(f"Database created: {title}")
        return {
            "success": True,
            "database_id": result["id"],
            "url": result.get("url", ""),
            "title": title,
            "properties": result.get("properties", {}),
            "message": f"Database '{title}' created with Austrian efficiency! 🗄️"
        }
    except Exception as e:
        logger.error(f"Failed to create database '{title}': {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Database creation failed - check schema and permissions"
        }

@app.tool()
async def query_database(
    database_id: str = Field(description="Database ID to query"),
    filter: Optional[Dict[str, Any]] = Field(default=None, description="Query filter conditions"),
    sorts: Optional[List[Dict[str, Any]]] = Field(default=None, description="Sort configuration"),
    limit: int = Field(default=100, description="Maximum results"),
    cursor: Optional[str] = Field(default=None, description="Pagination cursor")
) -> Dict[str, Any]:
    """Query databases with complex filters and sorts."""
    try:
        results = await db_manager.query_database(
            database_id=database_id,
            filter=filter,
            sorts=sorts,
            limit=limit,
            cursor=cursor
        )
        result_count = len(results.get("results", []))
        logger.info("Database query completed", database_id=database_id, result_count=result_count)
        return {
            "success": True,
            "results": results.get("results", []),
            "has_more": results.get("has_more", False),
            "next_cursor": results.get("next_cursor"),
            "count": result_count,
            "message": "Query completed with Austrian efficiency! 🔍"
        }
    except Exception as e:
        logger.error("Database query failed", database_id=database_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "message": "Database query failed - check database ID and filter syntax"
        }

@app.tool()
async def create_database_entry(
    database_id: str = Field(description="Database ID to add entry to"),
    properties: Dict[str, Any] = Field(description="Entry properties"),
    content: str = Field(default="", description="Entry content"),
    children: Optional[List[Dict[str, Any]]] = Field(default=None, description="Child blocks")
) -> Dict[str, Any]:
    """Add entries with all property types (text, select, date, etc.)"""
    try:
        result = await db_manager.create_database_entry(
            database_id=database_id,
            properties=properties,
            content=content,
            children=children
        )
        logger.info(f"Database entry created: {database_id}")
        return {
            "success": True,
            "page_id": result["id"],
            "database_id": database_id,
            "properties": properties,
            "message": "Database entry created with Austrian efficiency! ✅"
        }
    except Exception as e:
        logger.error(f"Failed to create database entry: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Database entry creation failed - check properties and schema"
        }

@app.tool()
async def update_database_entry(
    page_id: str = Field(description="Entry page ID to update"),
    properties: Optional[Dict[str, Any]] = Field(default=None, description="Updated properties"),
    content: Optional[str] = Field(default=None, description="Updated content"),
    archived: Optional[bool] = Field(default=None, description="Archive status")
) -> Dict[str, Any]:
    """Update existing database entries and properties."""
    try:
        await db_manager.update_database_entry(
            page_id=page_id,
            properties=properties,
            content=content,
            archived=archived
        )
        logger.info("Database entry updated", page_id=page_id)
        return {
            "success": True,
            "page_id": page_id,
            "updated_properties": properties,
            "message": "Database entry updated with Austrian efficiency! ✅"
        }
    except Exception as e:
        logger.error("Failed to update database entry", page_id=page_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "message": "Database entry update failed - check page ID and properties"
        }

@app.tool()
async def get_database_schema(
    database_id: str = Field(description="Database ID to analyze"),
    include_statistics: bool = Field(default=False, description="Include usage statistics"),
    property_details: bool = Field(default=True, description="Include detailed property information")
) -> Dict[str, Any]:
    """Retrieve database structure, properties, and metadata."""
    try:
        result = await db_manager.get_database_schema(
            database_id=database_id,
            include_statistics=include_statistics,
            property_details=property_details
        )
        logger.info(f"Database schema retrieved: {database_id}")
        return {
            "success": True,
            "schema": result,
            "message": "Database schema retrieved with Austrian efficiency! 📊"
        }
    except Exception as e:
        logger.error(f"Failed to get database schema {database_id}: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Schema retrieval failed - check database ID and permissions"
        }

@app.tool()
async def bulk_import_data(
    database_id: str = Field(description="Target database ID"),
    data_source: str = Field(description="CSV or JSON data to import"),
    mapping: Optional[Dict[str, str]] = Field(default=None, description="Field mapping (source -> target)"),
    merge_strategy: str = Field(default="create_new", description="How to handle existing data")
) -> Dict[str, Any]:
    """Import CSV/JSON data efficiently into databases."""
    try:
        result = await db_manager.bulk_import_data(
            database_id=database_id,
            data_source=data_source,
            mapping=mapping,
            merge_strategy=merge_strategy
        )
        logger.info("Bulk import completed", 
                   database_id=database_id,
                   successful=result.get('successful_imports', 0),
                   total=result.get('total_records', 0))
        return {
            "success": True,
            "import_results": result,
            "message": f"Imported {result['successful_imports']}/{result['total_records']} records with Austrian efficiency! 📊"
        }
    except Exception as e:
        logger.error("Bulk import failed", database_id=database_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "message": "Bulk import failed - check data format and database schema"
        }

# 💬 Collaboration Tools (3 tools)

@app.tool()
async def add_comment(
    page_id: str = Field(description="Page or block ID to comment on"),
    content: str = Field(description="Comment content"),
    parent_comment_id: Optional[str] = Field(default=None, description="Parent comment for threaded discussions"),
    rich_text: Optional[List[Dict[str, Any]]] = Field(default=None, description="Rich text formatting")
) -> Dict[str, Any]:
    """Add comments to pages or specific blocks."""
    try:
        result = await collab_manager.add_comment(
            page_id=page_id,
            content=content,
            parent_comment_id=parent_comment_id,
            rich_text=rich_text
        )
        logger.info("Comment added", page_id=page_id, comment_id=result.get("id"))
        return {
            "success": True,
            "comment": result,
            "message": "Comment added with Austrian efficiency! 💬"
        }
    except Exception as e:
        logger.error("Failed to add comment", page_id=page_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "message": "Comment creation failed - check page ID and permissions"
        }

@app.tool()
async def get_comments(
    page_id: str = Field(description="Page ID to get comments from"),
    include_resolved: bool = Field(default=False, description="Include resolved comments"),
    sort_by: str = Field(default="created_time", description="Sort field"),
    limit: int = Field(default=50, description="Maximum comments to return")
) -> Dict[str, Any]:
    """Retrieve page/block discussions and comment threads."""
    try:
        results = await collab_manager.get_comments(
            page_id=page_id,
            include_resolved=include_resolved,
            sort_by=sort_by,
            limit=limit
        )
        logger.info("Comments retrieved", page_id=page_id, comment_count=len(results))
        return {
            "success": True,
            "comments": results,
            "count": len(results),
            "message": f"Retrieved {len(results)} comments with Austrian efficiency! 💬"
        }
    except Exception as e:
        logger.error("Failed to get comments", page_id=page_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "message": "Comment retrieval failed - check page ID and permissions"
        }

@app.tool()
async def get_workspace_users(
    include_inactive: bool = Field(default=False, description="Include inactive users"),
    permission_level: Optional[str] = Field(default=None, description="Filter by permission level"),
    sort_by: str = Field(default="name", description="Sort field")
) -> Dict[str, Any]:
    """List workspace users, permissions, and activity."""
    try:
        results = await collab_manager.get_workspace_users(
            include_inactive=include_inactive,
            permission_level=permission_level,
            sort_by=sort_by
        )
        logger.info("Workspace users retrieved", user_count=len(results))
        return {
            "success": True,
            "users": results,
            "count": len(results),
            "message": f"Retrieved {len(results)} users with Austrian efficiency! 👥"
        }
    except Exception as e:
        logger.error("Failed to get workspace users", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "message": "User retrieval failed - check permissions"
        }

# 🔍 Advanced Features (4 tools)

@app.tool()
async def setup_automation(
    trigger_type: str = Field(description="Automation trigger type"),
    conditions: Dict[str, Any] = Field(description="Trigger conditions"),
    actions: List[Dict[str, Any]] = Field(description="Actions to perform"),
    webhook_url: Optional[str] = Field(default=None, description="Optional webhook URL")
) -> Dict[str, Any]:
    """Create Notion automations with webhook integration."""
    try:
        result = await automation_manager.setup_automation(
            trigger_type=trigger_type,
            conditions=conditions,
            actions=actions,
            webhook_url=webhook_url
        )
        logger.info("Automation created", automation_id=result.get('automation_id'))
        return result
    except Exception as e:
        logger.error("Failed to setup automation", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "message": "Automation setup failed - check configuration"
        }

@app.tool()
async def sync_external_data(
    external_source: str = Field(description="External data source type"),
    sync_config: Dict[str, Any] = Field(description="Sync configuration"),
    update_frequency: str = Field(default="daily", description="Update frequency")
) -> Dict[str, Any]:
    """Create synced databases from external tools."""
    try:
        result = await automation_manager.sync_external_data(
            external_source=external_source,
            sync_config=sync_config,
            update_frequency=update_frequency
        )
        logger.info("External sync configured", sync_id=result.get('sync_id'), source=external_source)
        return result
    except Exception as e:
        logger.error("Failed to setup external sync", source=external_source, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "message": "External sync setup failed - check configuration"
        }

@app.tool()
async def generate_ai_summary(
    page_id: str = Field(description="Page ID to analyze"),
    summary_type: str = Field(default="comprehensive", description="Summary type"),
    length: str = Field(default="medium", description="Summary length"),
    focus_areas: Optional[List[str]] = Field(default=None, description="Areas to focus on")
) -> Dict[str, Any]:
    """Use Notion AI for page/database content summaries."""
    try:
        result = await automation_manager.generate_ai_summary(
            page_id=page_id,
            summary_type=summary_type,
            length=length,
            focus_areas=focus_areas
        )
        logger.info("AI summary generated", page_id=page_id, summary_type=summary_type)
        return result
    except Exception as e:
        logger.error("Failed to generate AI summary", page_id=page_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "message": "AI summary generation failed - check page ID"
        }

@app.tool()
async def export_workspace_data(
    scope: str = Field(default="workspace", description="Export scope"),
    format: str = Field(default="json", description="Export format"),
    include_metadata: bool = Field(default=True, description="Include metadata"),
    compression: bool = Field(default=True, description="Compress export")
) -> Dict[str, Any]:
    """Backup and export functionality with multiple formats."""
    try:
        result = await automation_manager.export_workspace_data(
            scope=scope,
            format=format,
            include_metadata=include_metadata,
            compression=compression
        )
        logger.info("Export completed", export_id=result.get('export_config', {}).get('id'), format=format, scope=scope)
        return result
    except Exception as e:
        logger.error("Failed to export data", scope=scope, format=format, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "message": "Export failed - check permissions and configuration"
        }

# Server health check
@app.tool()
async def test_connection() -> Dict[str, Any]:
    """Test Notion API connection and server health."""
    try:
        result = await notion_client.test_connection()
        stats = await notion_client.get_stats()
        
        return {
            "connection": result,
            "server_stats": stats,
            "message": "NotionMCP server healthy with Austrian efficiency! 🇦🇹"
        }
    except Exception as e:
        logger.error("Connection test failed", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "message": "Connection test failed - check your NOTION_TOKEN"
        }

async def main() -> None:
    """Main entry point for the MCP server."""
    # Austrian efficiency: Clear startup message
    logger.info("NotionMCP server starting", message="Austrian efficiency activated")
    logger.info("Server configuration", 
                server_name=config.get('server', {}).get('name', 'NotionMCP'),
                timezone=config.get('server', {}).get('timezone', 'Europe/Vienna'))
    
    # Note: Notion client initialization happens lazily when tools are called
    # This allows the server to start even if NOTION_TOKEN isn't set yet
    # Tools will initialize and return appropriate errors if token is missing
    
    # Run the FastMCP 2.14.1 server
    await app.run_stdio_async()


def run() -> None:
    """Synchronous entry point for compatibility."""
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
