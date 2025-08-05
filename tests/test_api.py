"""
NotionMCP - Unit Tests with Comprehensive Mocking
Austrian Efficiency Testing - No Stubs, Real Validation

Tests all 18 tools with proper mocking and error scenarios.
Author: Sandra (Vienna, Austria) 🇦🇹
Date: July 22, 2025
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from datetime import datetime
import json

# Import the modules to test
from notion.client import NotionClient
from notion.pages import PageManager
from notion.databases import DatabaseManager
from notion.collaboration import CollaborationManager
from notion.automations import AutomationManager


class TestNotionClient:
    """Test the core Notion API client with Austrian efficiency."""
    
    @pytest.fixture
    def mock_notion_client(self):
        """Create mocked NotionClient for testing."""
        with patch('notion.client.AsyncClient') as mock_async_client:
            # Mock the async client instance
            mock_instance = AsyncMock()
            mock_async_client.return_value = mock_instance
            
            # Create NotionClient with mocked dependency
            client = NotionClient(
                token="test_token_12345",
                version="2022-06-28",
                timeout=30,
                timezone_str="Europe/Vienna"
            )
            
            # Attach the mock for assertions
            client._mock_async_client = mock_instance
            return client
    
    @pytest.mark.asyncio
    async def test_client_initialization(self, mock_notion_client):
        """Test client initializes with Austrian settings."""
        client = mock_notion_client
        
        assert client.timeout == 30
        assert str(client.timezone) == "Europe/Vienna"
        assert client.version == "2022-06-28"
        assert client.request_count == 0
    
    @pytest.mark.asyncio
    async def test_vienna_time_handling(self, mock_notion_client):
        """Test Vienna timezone handling for Austrian efficiency."""
        client = mock_notion_client
        
        vienna_time = client.get_vienna_time()
        assert vienna_time.tzinfo is not None
        
        formatted = client.format_austrian_date(vienna_time)
        assert "." in formatted  # DD.MM.YYYY format
        assert len(formatted.split()[0].split(".")) == 3  # DD.MM.YYYY
    
    @pytest.mark.asyncio
    async def test_page_id_validation(self, mock_notion_client):
        """Test page ID validation and formatting."""
        client = mock_notion_client
        
        # Valid ID without hyphens
        clean_id = "12345678901234567890123456789012"
        formatted = client.validate_page_id(clean_id)
        assert len(formatted) == 36  # With hyphens
        assert formatted.count("-") == 4
        
        # Invalid ID length
        with pytest.raises(ValueError, match="Invalid page ID format"):
            client.validate_page_id("too_short")
        
        # Empty ID
        with pytest.raises(ValueError, match="Page ID cannot be empty"):
            client.validate_page_id("")
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self, mock_notion_client):
        """Test successful connection test."""
        client = mock_notion_client
        
        # Mock successful user response
        mock_user = {
            "id": "user_123",
            "name": "Test User",
            "type": "person"
        }
        client._mock_async_client.users.me = AsyncMock(return_value=mock_user)
        
        result = await client.test_connection()
        
        assert result["success"] is True
        assert result["user"] == mock_user
        assert "Austria" in result["timezone"] or "Vienna" in result["timezone"]
        assert result["requests_made"] == 1
    
    @pytest.mark.asyncio
    async def test_test_connection_failure(self, mock_notion_client):
        """Test connection failure handling."""
        client = mock_notion_client
        
        # Mock API error
        from notion_client.errors import APIResponseError, APIErrorCode
        client._mock_async_client.users.me = AsyncMock(
            side_effect=APIResponseError(
                response=Mock(status_code=401),
                message="Unauthorized",
                code=APIErrorCode.Unauthorized
            )
        )
        
        result = await client.test_connection()
        
        assert result["success"] is False
        assert "token is invalid" in result["error"]
    
    @pytest.mark.asyncio
    async def test_german_character_support(self, mock_notion_client):
        """Test German character handling for Austrian content."""
        client = mock_notion_client
        
        german_text = "Österreich, München, Straße"
        cleaned = client.clean_german_text(german_text)
        
        # Should preserve UTF-8 characters
        assert "Ö" in cleaned
        assert "ü" in cleaned
        assert "ß" in cleaned


class TestPageManager:
    """Test page management operations with Austrian efficiency."""
    
    @pytest.fixture
    def mock_page_manager(self):
        """Create mocked PageManager for testing."""
        mock_client = AsyncMock()
        manager = PageManager(mock_client)
        manager.client = mock_client
        return manager
    
    @pytest.mark.asyncio
    async def test_create_page_success(self, mock_page_manager):
        """Test successful page creation."""
        manager = mock_page_manager
        
        # Mock page creation response
        mock_response = {
            "id": "page_123",
            "object": "page",
            "url": "https://notion.so/page_123"
        }
        manager.client.create_page = AsyncMock(return_value=mock_response)
        
        result = await manager.create_page(
            title="Test Research Paper",
            content="# Abstract\nThis is a test paper.",
            parent_id="parent_123"
        )
        
        assert result["id"] == "page_123"
        assert result["object"] == "page"
        manager.client.create_page.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_page_with_german_content(self, mock_page_manager):
        """Test page creation with German content."""
        manager = mock_page_manager
        
        mock_response = {"id": "page_456", "object": "page"}
        manager.client.create_page = AsyncMock(return_value=mock_response)
        
        result = await manager.create_page(
            title="Österreichische Forschung",
            content="Straße, Größe, Weiß"
        )
        
        # Should handle German characters without issues
        assert result["id"] == "page_456"
        call_args = manager.client.create_page.call_args[1]
        assert "Österreichische" in str(call_args)
    
    @pytest.mark.asyncio
    async def test_search_pages(self, mock_page_manager):
        """Test page search functionality."""
        manager = mock_page_manager
        
        mock_search_results = {
            "results": [
                {"id": "page_1", "object": "page"},
                {"id": "page_2", "object": "page"}
            ]
        }
        manager.client.search = AsyncMock(return_value=mock_search_results)
        
        results = await manager.search_pages(
            query="machine learning research",
            limit=10
        )
        
        assert len(results) == 2
        assert results[0]["id"] == "page_1"
        manager.client.search.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_archive_page_with_backup(self, mock_page_manager):
        """Test page archiving with backup creation."""
        manager = mock_page_manager
        
        # Mock page content for backup
        mock_page_content = {
            "page": {"id": "page_123"},
            "blocks": [{"type": "paragraph"}],
            "children_count": 1
        }
        manager.get_page_content = AsyncMock(return_value=mock_page_content)
        
        # Mock update response
        mock_update_response = {"id": "page_123", "archived": True}
        manager.client.update_page = AsyncMock(return_value=mock_update_response)
        
        # Mock Vienna time
        manager.client.format_austrian_date = Mock(return_value="22.07.2025 18:30")
        manager.client.get_vienna_time = Mock(return_value=datetime.now())
        
        result = await manager.archive_page(
            page_id="page_123",
            backup_first=True
        )
        
        assert result["backup_created"] is True
        assert "22.07.2025" in result["backup_time"]
        assert result["action"] == "archived"


class TestDatabaseManager:
    """Test database operations with Austrian efficiency."""
    
    @pytest.fixture
    def mock_db_manager(self):
        """Create mocked DatabaseManager for testing."""
        mock_client = AsyncMock()
        manager = DatabaseManager(mock_client)
        manager.client = mock_client
        return manager
    
    @pytest.mark.asyncio
    async def test_create_database_with_schema(self, mock_db_manager):
        """Test database creation with property schema."""
        manager = mock_db_manager
        
        mock_response = {
            "id": "db_123",
            "object": "database",
            "properties": {
                "Title": {"title": {}},
                "Status": {"select": {"options": []}}
            }
        }
        manager.client.create_database = AsyncMock(return_value=mock_response)
        
        properties_schema = {
            "Title": "title",
            "Status": {"type": "select", "options": ["Reading", "Completed"]},
            "Rating": "number"
        }
        
        result = await manager.create_database(
            title="Anime Collection",
            parent_id="page_123",
            properties_schema=properties_schema,
            icon="🎌"
        )
        
        assert result["id"] == "db_123"
        manager.client.create_database.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_query_database_with_filters(self, mock_db_manager):
        """Test database querying with complex filters."""
        manager = mock_db_manager
        
        mock_query_response = {
            "results": [
                {"id": "entry_1", "properties": {}},
                {"id": "entry_2", "properties": {}}
            ],
            "has_more": False
        }
        manager.client.query_database = AsyncMock(return_value=mock_query_response)
        
        result = await manager.query_database(
            database_id="db_123",
            filter={"Status": {"select": {"equals": "Reading"}}},
            limit=50
        )
        
        assert len(result["results"]) == 2
        assert result["has_more"] is False
        manager.client.query_database.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_bulk_import_csv_data(self, mock_db_manager):
        """Test bulk CSV import functionality."""
        manager = mock_db_manager
        
        # Mock schema info
        mock_schema = {
            "properties": {
                "Title": {"type": "title"},
                "Rating": {"type": "number"},
                "Status": {"type": "select"}
            }
        }
        manager.get_database_schema = AsyncMock(return_value=mock_schema)
        
        # Mock entry creation
        manager.create_database_entry = AsyncMock(
            return_value={"id": "entry_new"}
        )
        
        # CSV data
        csv_data = "Title,Rating,Status\nAttack on Titan,9,Completed\nNaruto,8,Watching"
        
        result = await manager.bulk_import_data(
            database_id="db_123",
            data_source=csv_data
        )
        
        assert result["total_records"] == 2
        assert result["successful_imports"] == 2
        assert result["failed_imports"] == 0


class TestCollaborationManager:
    """Test collaboration features with Austrian efficiency."""
    
    @pytest.fixture
    def mock_collab_manager(self):
        """Create mocked CollaborationManager for testing."""
        mock_client = AsyncMock()
        manager = CollaborationManager(mock_client)
        manager.client = mock_client
        return manager
    
    @pytest.mark.asyncio
    async def test_add_comment(self, mock_collab_manager):
        """Test comment addition functionality."""
        manager = mock_collab_manager
        
        # Mock Vienna time formatting
        manager.client.format_austrian_date = Mock(return_value="22.07.2025 18:30")
        manager.client.get_vienna_time = Mock(return_value=datetime.now())
        
        # Mock block append
        manager.client.append_block_children = AsyncMock()
        
        result = await manager.add_comment(
            page_id="page_123",
            content="Great research! Needs more references."
        )
        
        assert result["type"] == "comment"
        assert result["content"] == "Great research! Needs more references."
        assert "22.07.2025" in result["created_time"]
        manager.client.append_block_children.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_workspace_users(self, mock_collab_manager):
        """Test workspace user retrieval."""
        manager = mock_collab_manager
        
        mock_users_response = {
            "results": [
                {
                    "id": "user_1",
                    "name": "Sandra",
                    "type": "person",
                    "email": "sandra@example.com"
                },
                {
                    "id": "user_2", 
                    "name": "Bot User",
                    "type": "bot"
                }
            ],
            "has_more": False
        }
        manager.client.get_users = AsyncMock(return_value=mock_users_response)
        
        users = await manager.get_workspace_users(
            include_inactive=False,
            sort_by="name"
        )
        
        assert len(users) == 2
        assert users[0]["name"] == "Sandra"
        assert users[0]["type"] == "person"


class TestAutomationManager:
    """Test automation and AI features with Austrian efficiency."""
    
    @pytest.fixture
    def mock_automation_manager(self):
        """Create mocked AutomationManager for testing."""
        mock_client = AsyncMock()
        manager = AutomationManager(mock_client)
        manager.client = mock_client
        return manager
    
    @pytest.mark.asyncio
    async def test_setup_automation(self, mock_automation_manager):
        """Test automation setup with webhook."""
        manager = mock_automation_manager
        
        # Mock Vienna time
        manager.client.format_austrian_date = Mock(return_value="22.07.2025 18:30")
        manager.client.get_vienna_time = Mock(return_value=datetime.now())
        
        result = await manager.setup_automation(
            trigger_type="page_created",
            conditions={"parent_id": "db_123"},
            actions=[{"type": "notify", "webhook": "https://example.com/hook"}],
            webhook_url="https://example.com/webhook"
        )
        
        assert result["success"] is True
        assert "automation_" in result["automation_id"]
        assert result["config"]["trigger_type"] == "page_created"
    
    @pytest.mark.asyncio
    async def test_generate_ai_summary(self, mock_automation_manager):
        """Test AI summary generation."""
        manager = mock_automation_manager
        
        # Mock page content
        mock_page_content = {
            "blocks": [
                {
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"plain_text": "This is research about machine learning."}
                        ]
                    }
                }
            ]
        }
        
        # Mock PageManager
        with patch('notion.automations.PageManager') as mock_page_manager:
            mock_pm_instance = AsyncMock()
            mock_pm_instance.get_page_content = AsyncMock(return_value=mock_page_content)
            mock_page_manager.return_value = mock_pm_instance
            
            # Mock Vienna time
            manager.client.format_austrian_date = Mock(return_value="22.07.2025 18:30")
            
            result = await manager.generate_ai_summary(
                page_id="page_123",
                summary_type="comprehensive"
            )
        
        assert result["success"] is True
        assert "ai_summary" in result
        assert result["ai_summary"]["word_count"] > 0
    
    @pytest.mark.asyncio
    async def test_export_workspace_data(self, mock_automation_manager):
        """Test workspace export functionality."""
        manager = mock_automation_manager
        
        # Mock Vienna time
        manager.client.format_austrian_date = Mock(return_value="22.07.2025 18:30")
        manager.client.get_vienna_time = Mock(return_value=datetime.now())
        manager.client.timezone = "Europe/Vienna"
        
        result = await manager.export_workspace_data(
            scope="workspace",
            format="json",
            include_metadata=True
        )
        
        assert result["success"] is True
        assert result["export_config"]["scope"] == "workspace"
        assert "22.07.2025" in result["export_data"]["export_timestamp"]


class TestErrorHandling:
    """Test error handling with Austrian efficiency - no gaslighting."""
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """Test proper API error handling without gaslighting."""
        from notion_client.errors import APIResponseError, APIErrorCode
        
        mock_client = AsyncMock()
        mock_client.pages.retrieve = AsyncMock(
            side_effect=APIResponseError(
                response=Mock(status_code=404),
                message="Object not found",
                code=APIErrorCode.ObjectNotFound
            )
        )
        
        client = NotionClient("test_token")
        client.client = mock_client
        
        with pytest.raises(Exception, match="not found"):
            await client.get_page("invalid_page_id")
    
    @pytest.mark.asyncio
    async def test_rate_limit_handling(self):
        """Test rate limit error handling."""
        from notion_client.errors import APIResponseError, APIErrorCode
        
        mock_client = AsyncMock()
        mock_client.pages.retrieve = AsyncMock(
            side_effect=APIResponseError(
                response=Mock(status_code=429),
                message="Rate limited",
                code=APIErrorCode.RateLimited
            )
        )
        
        client = NotionClient("test_token")
        client.client = mock_client
        
        with pytest.raises(Exception, match="Rate limit exceeded"):
            await client.get_page("page_id")


# Test configuration
pytest_plugins = []

if __name__ == "__main__":
    pytest.main(["-v", __file__])
