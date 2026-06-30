"""
NotionMCP - Notion API Integration Package
FastMCP 2.0 Implementation with Austrian Efficiency

Core modules for comprehensive Notion workspace management:
- client: Core Notion API client with Austrian efficiency
- pages: Page management operations (CRUD, search)
- databases: Database operations (schema, queries, bulk)
- collaboration: Comments, users, permissions
- automations: Webhooks, AI integration, export

Author: Sandra (Vienna, Austria) 🇦🇹
Date: July 22, 2025
Context: Academic knowledge management + weeb organization
"""

__version__ = "1.0.0"
__author__ = "Sandra (Vienna, Austria)"
__description__ = "Notion MCP Server with Austrian Efficiency"

# Core imports for easy access
from .automations import AutomationManager
from .client import NotionClient
from .collaboration import CollaborationManager
from .databases import DatabaseManager
from .pages import PageManager

__all__ = ["AutomationManager", "CollaborationManager", "DatabaseManager", "NotionClient", "PageManager"]
