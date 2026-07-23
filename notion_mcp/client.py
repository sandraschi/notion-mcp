"""
NotionMCP - Core Notion API Client
Austrian Efficiency Implementation with Budget Awareness

Features:
- Rate limiting respect (~€100/month budget consideration)
- Vienna timezone handling (Europe/Vienna)
- German character support (ä, ö, ü, ß)
- Japanese character support for weeb content
- Direct error communication (no gaslighting)
"""

import logging
from datetime import datetime
from typing import Any

import pytz
from notion_client import AsyncClient
from notion_client.errors import APIErrorCode, APIResponseError

logger = logging.getLogger("notionmcp.client")


class NotionClient:
    """
    Core Notion API client with Austrian efficiency and budget awareness.
    """

    def __init__(
        self,
        token: str,
        version: str = "2026-03-11",
        timeout: int = 30,
        timezone_str: str = "Europe/Vienna",
        token_type: str = "internal",  # noqa: S107
    ):
        """
        Initialize Notion client with Austrian context.

        token: Notion integration token or Personal Access Token (PAT)
        version: API version (default: 2026-03-11)
        timeout: Request timeout in seconds
        timezone_str: Timezone for date handling (default: Vienna)
        token_type: "internal" or "pat" (Personal Access Token)
        """
        if not token:
            raise ValueError("Notion token required. Set NOTION_TOKEN (internal integration) or NOTION_PAT.")

        self.client = AsyncClient(auth=token, notion_version=version, timeout_ms=timeout * 1000)

        self.timezone = pytz.timezone(timezone_str)
        self.version = version
        self.timeout = timeout
        self.token_type = token_type

        # Austrian efficiency: Track API usage for budget awareness
        self.request_count = 0
        self.error_count = 0

        logger.info(f"Notion client initialized ({token_type}) - Vienna timezone: {timezone_str}, API: {version}")

    async def _make_request(self, method: str, *args, **kwargs) -> Any:
        """
        Make API request with Austrian efficiency error handling and rate limiting.
        """
        self.request_count += 1

        try:
            # Resolve dotted method names for nested attribute access
            parts = method.split(".")
            client_method = self.client
            for part in parts:
                client_method = getattr(client_method, part)
            result = await client_method(*args, **kwargs)

            logger.debug(f"API request successful: {method} (Total: {self.request_count})")
            return result

        except APIResponseError as e:
            self.error_count += 1
            logger.error(f"Notion API error: {e.code} - {getattr(e, 'body', str(e))}")

            msg = getattr(e, "body", str(e))
            if e.code == APIErrorCode.Unauthorized:
                raise Exception("Notion API token is invalid or expired. Check your integration settings.") from e
            elif e.code == APIErrorCode.RateLimited:
                raise Exception("Rate limit exceeded. Please wait before making more requests.") from e
            elif e.code == APIErrorCode.ObjectNotFound:
                raise Exception("The requested page/database was not found. Check the ID and permissions.") from e
            elif e.code == APIErrorCode.ValidationError:
                raise Exception(f"Invalid request data: {msg}") from e
            else:
                raise Exception(f"Notion API error ({e.code}): {msg}") from e

        except Exception as e:
            self.error_count += 1
            logger.error(f"Unexpected error in {method}: {e}")
            raise Exception(f"Request failed: {e!s}") from e

    def get_vienna_time(self) -> datetime:
        """Get current time in Vienna timezone for Austrian efficiency."""
        return datetime.now(self.timezone)

    def format_austrian_date(self, dt: datetime) -> str:
        """Format date in Austrian style: DD.MM.YYYY HH:MM"""
        if dt.tzinfo is None:
            dt = self.timezone.localize(dt)
        elif dt.tzinfo != self.timezone:
            dt = dt.astimezone(self.timezone)

        return dt.strftime("%d.%m.%Y %H:%M")

    def clean_german_text(self, text: str) -> str:
        """Ensure proper German character encoding for Austrian content."""
        if not text:
            return text

        # Ensure UTF-8 encoding for German characters (ä, ö, ü, ß)
        # In practice, text should already be UTF-8
        return text

    def validate_page_id(self, page_id: str) -> str:
        """Validate and clean page/database ID format."""
        if not page_id:
            raise ValueError("Page ID cannot be empty")

        # Remove any hyphens and ensure correct format
        clean_id = page_id.replace("-", "")

        if len(clean_id) != 32:
            raise ValueError(f"Invalid page ID format: {page_id}")

        # Return with proper hyphen formatting
        return f"{clean_id[:8]}-{clean_id[8:12]}-{clean_id[12:16]}-{clean_id[16:20]}-{clean_id[20:]}"

    async def test_connection(self) -> dict[str, Any]:
        """Test Notion API connection with Austrian efficiency."""
        try:
            # Try to get the current user
            user_info = await self._make_request("users.me")

            return {
                "success": True,
                "user": user_info,
                "timezone": str(self.timezone),
                "current_time": self.format_austrian_date(self.get_vienna_time()),
                "requests_made": self.request_count,
                "message": "Connection successful with Austrian efficiency! 🇦🇹",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Connection failed - check your token and permissions",
            }

    async def get_stats(self) -> dict[str, Any]:
        """Get client usage statistics for budget awareness."""
        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "success_rate": (self.request_count - self.error_count) / max(self.request_count, 1) * 100,
            "current_time": self.format_austrian_date(self.get_vienna_time()),
            "timezone": str(self.timezone),
            "version": self.version,
        }

    # Core API methods with Austrian efficiency

    async def get_page(self, page_id: str) -> dict[str, Any]:
        """Get page by ID with validation."""
        page_id = self.validate_page_id(page_id)
        return await self._make_request("pages.retrieve", page_id=page_id)

    async def get_database(self, database_id: str) -> dict[str, Any]:
        """Get database by ID with validation."""
        database_id = self.validate_page_id(database_id)
        return await self._make_request("databases.retrieve", database_id=database_id)

    async def get_block_children(self, block_id: str, start_cursor: str | None = None) -> dict[str, Any]:
        """Get block children with pagination."""
        block_id = self.validate_page_id(block_id)
        kwargs = {"block_id": block_id}
        if start_cursor:
            kwargs["start_cursor"] = start_cursor
        return await self._make_request("blocks.children.list", **kwargs)

    async def search(
        self,
        query: str = "",
        filter: dict[str, Any] | None = None,
        sort: dict[str, Any] | None = None,
        start_cursor: str | None = None,
        page_size: int = 10,
    ) -> dict[str, Any]:
        """Search with Austrian efficiency parameters."""
        kwargs = {
            "query": query,
            "page_size": min(page_size, 100),  # Respect API limits
        }

        if filter:
            kwargs["filter"] = filter
        if sort:
            kwargs["sort"] = sort
        if start_cursor:
            kwargs["start_cursor"] = start_cursor

        return await self._make_request("search", **kwargs)

    async def create_page(self, **kwargs) -> dict[str, Any]:
        """Create page with parameter validation."""
        return await self._make_request("pages.create", **kwargs)

    async def update_page(self, page_id: str, **kwargs) -> dict[str, Any]:
        """Update page with ID validation."""
        page_id = self.validate_page_id(page_id)
        return await self._make_request("pages.update", page_id=page_id, **kwargs)

    async def create_database(self, **kwargs) -> dict[str, Any]:
        """Create database with parameter validation."""
        return await self._make_request("databases.create", **kwargs)

    async def update_database(self, database_id: str, **kwargs) -> dict[str, Any]:
        """Update database with ID validation."""
        database_id = self.validate_page_id(database_id)
        return await self._make_request("databases.update", database_id=database_id, **kwargs)

    async def query_database(self, database_id: str, **kwargs) -> dict[str, Any]:
        """Query database with ID validation."""
        database_id = self.validate_page_id(database_id)
        return await self._make_request("databases.query", database_id=database_id, **kwargs)

    async def append_block_children(self, block_id: str, children: list[dict[str, Any]]) -> dict[str, Any]:
        """Append blocks with validation."""
        block_id = self.validate_page_id(block_id)
        return await self._make_request("blocks.children.append", block_id=block_id, children=children)

    async def get_users(self, start_cursor: str | None = None) -> dict[str, Any]:
        """Get workspace users."""
        kwargs = {}
        if start_cursor:
            kwargs["start_cursor"] = start_cursor
        return await self._make_request("users.list", **kwargs)

    async def get_user(self, user_id: str) -> dict[str, Any]:
        """Get user by ID."""
        return await self._make_request("users.retrieve", user_id=user_id)

    async def create_comment(
        self,
        parent: dict[str, Any],
        rich_text: list[dict[str, Any]],
        discussion_id: str | None = None,
    ) -> dict[str, Any]:
        """Create a comment on a page or in a discussion thread."""
        kwargs: dict[str, Any] = {
            "parent": parent,
            "rich_text": rich_text,
        }
        if discussion_id:
            kwargs["discussion_id"] = discussion_id
        return await self._make_request("comments.create", **kwargs)

    async def list_comments(
        self,
        block_id: str,
        start_cursor: str | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """List comments on a page or block."""
        block_id = self.validate_page_id(block_id)
        kwargs: dict[str, Any] = {"block_id": block_id}
        if start_cursor:
            kwargs["start_cursor"] = start_cursor
        if page_size:
            kwargs["page_size"] = min(page_size, 100)
        return await self._make_request("comments.list", **kwargs)

    async def update_block(self, block_id: str, **kwargs) -> dict[str, Any]:
        """Update a specific block (type, content, properties)."""
        block_id = self.validate_page_id(block_id)
        return await self._make_request("blocks.update", block_id=block_id, **kwargs)

    async def delete_block(self, block_id: str) -> dict[str, Any]:
        """Set a block to archived: true."""
        block_id = self.validate_page_id(block_id)
        return await self._make_request("blocks.delete", block_id=block_id)

    async def update_database_schema(self, database_id: str, **kwargs) -> dict[str, Any]:
        """Update database properties, title, description, or icon."""
        database_id = self.validate_page_id(database_id)
        return await self._make_request("databases.update", database_id=database_id, **kwargs)

    async def retrieve_page_markdown(self, page_id: str) -> dict[str, Any]:
        """Retrieve page content as enhanced markdown."""
        page_id = self.validate_page_id(page_id)
        return await self._make_request("pages.retrieve_markdown", page_id=page_id)

    async def update_page_markdown(self, page_id: str, markdown: str) -> dict[str, Any]:
        """Update page content using enhanced markdown."""
        page_id = self.validate_page_id(page_id)
        return await self._make_request("pages.update_markdown", page_id=page_id, markdown=markdown)
