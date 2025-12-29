"""
NotionMCP - Database Management Operations
Austrian Efficiency Implementation for Academic and Project Organization

Features:
- Complete database CRUD operations
- Complex query building and filtering
- Bulk import/export operations
- Schema management and validation
- Perfect for research databases and project tracking
"""

import logging
import json
import csv
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from io import StringIO

logger = logging.getLogger("notionmcp.databases")

class DatabaseManager:
    """
    Comprehensive database management with Austrian efficiency.
    Perfect for academic research, anime tracking, project management.
    """
    
    def __init__(self, notion_client):
        """Initialize with NotionClient instance."""
        self.client = notion_client
    
    def _build_property_schema(self, properties_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build Notion database property schema with Austrian efficiency.
        
        Supported property types:
        - title: Page title
        - rich_text: Text content
        - number: Numbers
        - select: Single selection
        - multi_select: Multiple selections
        - date: Dates and times
        - checkbox: Boolean values
        - url: URLs
        - email: Email addresses
        - phone_number: Phone numbers
        - relation: Relations to other databases
        - formula: Calculated fields
        - rollup: Aggregated values from relations
        """
        notion_properties = {}
        
        for prop_name, prop_config in properties_schema.items():
            if isinstance(prop_config, str):
                # Simple string type specification
                prop_type = prop_config.lower()
                if prop_type == "text":
                    notion_properties[prop_name] = {"rich_text": {}}
                elif prop_type == "number":
                    notion_properties[prop_name] = {"number": {"format": "number"}}
                elif prop_type == "date":
                    notion_properties[prop_name] = {"date": {}}
                elif prop_type == "checkbox":
                    notion_properties[prop_name] = {"checkbox": {}}
                elif prop_type == "url":
                    notion_properties[prop_name] = {"url": {}}
                elif prop_type == "email":
                    notion_properties[prop_name] = {"email": {}}
                elif prop_type == "phone":
                    notion_properties[prop_name] = {"phone_number": {}}
                else:
                    # Default to rich_text
                    notion_properties[prop_name] = {"rich_text": {}}
            
            elif isinstance(prop_config, dict):
                # Detailed property configuration
                prop_type = prop_config.get("type", "rich_text")
                
                if prop_type == "select":
                    options = prop_config.get("options", [])
                    notion_properties[prop_name] = {
                        "select": {
                            "options": [{"name": opt, "color": "default"} for opt in options]
                        }
                    }
                elif prop_type == "multi_select":
                    options = prop_config.get("options", [])
                    notion_properties[prop_name] = {
                        "multi_select": {
                            "options": [{"name": opt, "color": "default"} for opt in options]
                        }
                    }
                elif prop_type == "relation":
                    database_id = prop_config.get("database_id")
                    if database_id:
                        notion_properties[prop_name] = {
                            "relation": {"database_id": database_id}
                        }
                elif prop_type == "formula":
                    expression = prop_config.get("expression", "")
                    if expression:
                        notion_properties[prop_name] = {
                            "formula": {"expression": expression}
                        }
                elif prop_type == "rollup":
                    relation_property = prop_config.get("relation_property")
                    rollup_property = prop_config.get("rollup_property")
                    function = prop_config.get("function", "count")
                    if relation_property and rollup_property:
                        notion_properties[prop_name] = {
                            "rollup": {
                                "relation_property_name": relation_property,
                                "rollup_property_name": rollup_property,
                                "function": function
                            }
                        }
                else:
                    # Standard property types
                    notion_properties[prop_name] = {prop_type: prop_config.get("config", {})}
        
        return notion_properties
    
    def _build_database_filter(self, filter_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build complex Notion database filters with Austrian efficiency.
        
        Supports:
        - Simple property filters: {"property": "Status", "select": {"equals": "In Progress"}}
        - Compound filters: {"and": [...], "or": [...]}
        - Complex conditions: contains, does_not_contain, is_empty, is_not_empty
        """
        if not filter_config:
            return {}
        
        # If it's already a proper Notion filter, return as-is
        if any(key in filter_config for key in ["and", "or", "property"]):
            return filter_config
        
        # Convert simple key-value filters
        filters = []
        for prop_name, condition in filter_config.items():
            if isinstance(condition, dict):
                # Detailed condition
                filters.append({
                    "property": prop_name,
                    **condition
                })
            else:
                # Simple equality check
                filters.append({
                    "property": prop_name,
                    "rich_text": {"contains": str(condition)}
                })
        
        if len(filters) == 1:
            return filters[0]
        elif len(filters) > 1:
            return {"and": filters}
        
        return {}
    
    def _build_database_sorts(self, sorts_config: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Build Notion database sort configuration with Austrian efficiency.
        """
        if not sorts_config:
            return []
        
        notion_sorts = []
        for sort_item in sorts_config:
            if isinstance(sort_item, str):
                # Simple property name
                notion_sorts.append({
                    "property": sort_item,
                    "direction": "ascending"
                })
            elif isinstance(sort_item, dict):
                if "property" in sort_item:
                    notion_sorts.append(sort_item)
                else:
                    # Convert key-value to proper format
                    for prop, direction in sort_item.items():
                        notion_sorts.append({
                            "property": prop,
                            "direction": direction if direction in ["ascending", "descending"] else "ascending"
                        })
        
        return notion_sorts
    
    async def create_database(
        self,
        title: str,
        parent_id: str,
        properties_schema: Dict[str, Any],
        icon: Optional[str] = None,
        cover: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create database with custom property schema and Austrian efficiency.
        
        Args:
            title: Database title
            parent_id: Parent page ID
            properties_schema: Property definitions
            icon: Database icon (emoji or external URL)
            cover: Database cover image URL
        
        Returns:
            Created database information
        """
        try:
            # Build database properties
            properties = self._build_property_schema(properties_schema)
            
            # Ensure title property exists
            if "title" not in properties and "Title" not in properties:
                properties["Title"] = {"title": {}}
            
            # Build database data
            database_data = {
                "parent": {"page_id": parent_id},
                "title": [{"type": "text", "text": {"content": title}}],
                "properties": properties
            }
            
            # Add icon if provided
            if icon:
                if icon.startswith("http"):
                    database_data["icon"] = {"type": "external", "external": {"url": icon}}
                else:
                    database_data["icon"] = {"type": "emoji", "emoji": icon}
            
            # Add cover if provided
            if cover and cover.startswith("http"):
                database_data["cover"] = {"type": "external", "external": {"url": cover}}
            
            # Create the database
            database = await self.client.create_database(**database_data)
            
            logger.info(f"Database created successfully: {title} ({database['id']})")
            return database
            
        except Exception as e:
            logger.error(f"Failed to create database '{title}': {e}")
            raise
    
    async def query_database(
        self,
        database_id: str,
        filter: Optional[Dict[str, Any]] = None,
        sorts: Optional[List[Dict[str, Any]]] = None,
        limit: int = 100,
        cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query database with complex filters and sorts - Austrian efficiency.
        Perfect for academic research and project tracking.
        """
        try:
            # Build query parameters
            query_params = {}
            
            if filter:
                query_params["filter"] = self._build_database_filter(filter)
            
            if sorts:
                query_params["sorts"] = self._build_database_sorts(sorts)
            
            if cursor:
                query_params["start_cursor"] = cursor
            
            query_params["page_size"] = min(limit, 100)  # Respect API limits
            
            # Execute query
            response = await self.client.query_database(
                database_id=database_id,
                **query_params
            )
            
            logger.info(f"Database query completed: {database_id} ({len(response.get('results', []))} results)")
            return response
            
        except Exception as e:
            logger.error(f"Database query failed {database_id}: {e}")
            raise
    
    async def create_database_entry(
        self,
        database_id: str,
        properties: Dict[str, Any],
        content: str = "",
        children: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Create database entry with all property types and Austrian efficiency.
        """
        try:
            # Get database schema to validate properties
            database = await self.client.get_database(database_id)
            db_properties = database.get("properties", {})
            
            # Build entry properties
            entry_properties = self._build_entry_properties(properties, db_properties)
            
            # Create the page in the database
            page_data = {
                "parent": {"database_id": database_id},
                "properties": entry_properties
            }
            
            page = await self.client.create_page(**page_data)
            
            # Add content if provided
            if content or children:
                from .pages import PageManager
                page_manager = PageManager(self.client)
                
                if children:
                    await self.client.append_block_children(
                        block_id=page["id"],
                        children=children
                    )
                elif content:
                    blocks = page_manager._build_content_blocks(content)
                    if blocks:
                        await self.client.append_block_children(
                            block_id=page["id"],
                            children=blocks
                        )
            
            logger.info(f"Database entry created: {database_id} -> {page['id']}")
            return page
            
        except Exception as e:
            logger.error(f"Failed to create database entry in {database_id}: {e}")
            raise
    
    def _build_entry_properties(
        self, 
        properties: Dict[str, Any], 
        db_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build entry properties based on database schema with Austrian efficiency.
        """
        entry_properties = {}
        
        for prop_name, value in properties.items():
            if prop_name not in db_schema:
                logger.warning(f"Property '{prop_name}' not found in database schema")
                continue
            
            prop_config = db_schema[prop_name]
            prop_type = prop_config.get("type")
            
            if value is None:
                continue
            
            if prop_type == "title":
                entry_properties[prop_name] = {
                    "title": [{"type": "text", "text": {"content": str(value)}}]
                }
            elif prop_type == "rich_text":
                entry_properties[prop_name] = {
                    "rich_text": [{"type": "text", "text": {"content": str(value)}}]
                }
            elif prop_type == "number":
                if isinstance(value, (int, float)):
                    entry_properties[prop_name] = {"number": value}
            elif prop_type == "select":
                entry_properties[prop_name] = {"select": {"name": str(value)}}
            elif prop_type == "multi_select":
                if isinstance(value, list):
                    entry_properties[prop_name] = {
                        "multi_select": [{"name": str(item)} for item in value]
                    }
                else:
                    entry_properties[prop_name] = {
                        "multi_select": [{"name": str(value)}]
                    }
            elif prop_type == "date":
                if isinstance(value, (datetime, date)):
                    entry_properties[prop_name] = {
                        "date": {"start": value.isoformat()}
                    }
                elif isinstance(value, str):
                    entry_properties[prop_name] = {
                        "date": {"start": value}
                    }
            elif prop_type == "checkbox":
                entry_properties[prop_name] = {"checkbox": bool(value)}
            elif prop_type == "url":
                entry_properties[prop_name] = {"url": str(value)}
            elif prop_type == "email":
                entry_properties[prop_name] = {"email": str(value)}
            elif prop_type == "phone_number":
                entry_properties[prop_name] = {"phone_number": str(value)}
            elif prop_type == "relation":
                if isinstance(value, list):
                    entry_properties[prop_name] = {
                        "relation": [{"id": str(item)} for item in value]
                    }
                else:
                    entry_properties[prop_name] = {
                        "relation": [{"id": str(value)}]
                    }
        
        return entry_properties
    
    async def update_database_entry(
        self,
        page_id: str,
        properties: Dict[str, Any],
        content: Optional[str] = None,
        archived: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Update database entry with Austrian efficiency.
        """
        try:
            # Get the page to determine its database
            page = await self.client.get_page(page_id)
            parent = page.get("parent", {})
            
            if parent.get("type") != "database_id":
                raise Exception("Page is not a database entry")
            
            database_id = parent.get("database_id")
            database = await self.client.get_database(database_id)
            db_properties = database.get("properties", {})
            
            # Build update data
            update_data = {}
            
            if properties:
                update_data["properties"] = self._build_entry_properties(properties, db_properties)
            
            if archived is not None:
                update_data["archived"] = archived
            
            # Update the page
            updated_page = await self.client.update_page(page_id=page_id, **update_data)
            
            # Update content if provided
            if content is not None:
                from .pages import PageManager
                page_manager = PageManager(self.client)
                blocks = page_manager._build_content_blocks(content)
                if blocks:
                    await self.client.append_block_children(
                        block_id=page_id,
                        children=blocks
                    )
            
            logger.info(f"Database entry updated: {page_id}")
            return updated_page
            
        except Exception as e:
            logger.error(f"Failed to update database entry {page_id}: {e}")
            raise
    
    async def get_database_schema(
        self,
        database_id: str,
        include_statistics: bool = False,
        property_details: bool = True
    ) -> Dict[str, Any]:
        """
        Get database structure and metadata with Austrian efficiency.
        """
        try:
            database = await self.client.get_database(database_id)
            
            result = {
                "database": database,
                "properties": {},
                "title": database.get("title", [{}])[0].get("plain_text", "Untitled")
            }
            
            if property_details:
                properties = database.get("properties", {})
                for prop_name, prop_config in properties.items():
                    prop_type = prop_config.get("type")
                    result["properties"][prop_name] = {
                        "type": prop_type,
                        "config": prop_config.get(prop_type, {})
                    }
                    
                    # Add options for select/multi_select
                    if prop_type in ["select", "multi_select"]:
                        options = prop_config.get(prop_type, {}).get("options", [])
                        result["properties"][prop_name]["options"] = [
                            opt.get("name") for opt in options
                        ]
            
            if include_statistics:
                # Get basic statistics
                try:
                    await self.query_database(database_id, limit=1)
                    result["statistics"] = {
                        "total_entries": "Unknown",  # Notion doesn't provide total count
                        "last_edited": database.get("last_edited_time"),
                        "created_time": database.get("created_time")
                    }
                except Exception:
                    result["statistics"] = {"error": "Could not retrieve statistics"}
            
            logger.info(f"Database schema retrieved: {database_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get database schema {database_id}: {e}")
            raise
    
    async def bulk_import_data(
        self,
        database_id: str,
        data_source: Union[str, List[Dict[str, Any]]],
        mapping: Optional[Dict[str, str]] = None,
        merge_strategy: str = "create_new"
    ) -> Dict[str, Any]:
        """
        Bulk import CSV/JSON data with Austrian efficiency.
        Perfect for academic data migration and project setup.
        """
        try:
            # Parse data source
            if isinstance(data_source, str):
                if data_source.strip().startswith('['):
                    # JSON data
                    data = json.loads(data_source)
                else:
                    # CSV data
                    csv_file = StringIO(data_source)
                    reader = csv.DictReader(csv_file)
                    data = list(reader)
            else:
                data = data_source
            
            if not data:
                raise Exception("No data provided for import")
            
            # Get database schema
            schema_info = await self.get_database_schema(database_id, property_details=True)
            db_properties = schema_info["properties"]
            
            # Apply mapping if provided
            if mapping:
                mapped_data = []
                for row in data:
                    mapped_row = {}
                    for source_field, target_field in mapping.items():
                        if source_field in row:
                            mapped_row[target_field] = row[source_field]
                    mapped_data.append(mapped_row)
                data = mapped_data
            
            # Import data with Austrian efficiency
            results = {
                "total_records": len(data),
                "successful_imports": 0,
                "failed_imports": 0,
                "errors": []
            }
            
            for i, row in enumerate(data):
                try:
                    # Filter properties that exist in the database
                    filtered_properties = {
                        k: v for k, v in row.items() 
                        if k in db_properties and v is not None and v != ""
                    }
                    
                    if filtered_properties:
                        await self.create_database_entry(
                            database_id=database_id,
                            properties=filtered_properties
                        )
                        results["successful_imports"] += 1
                    
                    # Austrian efficiency: Log progress every 10 records
                    if (i + 1) % 10 == 0:
                        logger.info(f"Import progress: {i + 1}/{len(data)} records processed")
                
                except Exception as row_error:
                    results["failed_imports"] += 1
                    results["errors"].append({
                        "row": i + 1,
                        "data": row,
                        "error": str(row_error)
                    })
                    logger.warning(f"Failed to import row {i + 1}: {row_error}")
            
            logger.info(f"Bulk import completed: {results['successful_imports']}/{results['total_records']} successful")
            return results
            
        except Exception as e:
            logger.error(f"Bulk import failed for database {database_id}: {e}")
            raise
