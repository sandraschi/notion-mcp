"""
NotionMCP - Page Management Operations
Austrian Efficiency Implementation for Academic and Weeb Content

Features:
- Complete page CRUD operations
- German and Japanese character support
- Academic workflow optimization
- Efficient content handling
- Vienna timezone integration
"""

import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

logger = logging.getLogger("notionmcp.pages")

class PageManager:
    """
    Comprehensive page management with Austrian efficiency.
    Perfect for academic research, project documentation, and weeb content organization.
    """
    
    def __init__(self, notion_client):
        """Initialize with NotionClient instance."""
        self.client = notion_client
        
    def _build_content_blocks(self, content: str) -> List[Dict[str, Any]]:
        """
        Convert plain text or markdown to Notion blocks with Austrian efficiency.
        Supports German and Japanese characters.
        """
        if not content:
            return []
        
        # Simple text to blocks conversion
        # For now, treat as paragraph blocks - can be enhanced later
        paragraphs = content.split('\n\n')
        blocks = []
        
        for paragraph in paragraphs:
            if paragraph.strip():
                # Handle basic markdown-style formatting
                if paragraph.startswith('# '):
                    # Heading 1
                    blocks.append({
                        "object": "block",
                        "type": "heading_1",
                        "heading_1": {
                            "rich_text": [{"type": "text", "text": {"content": paragraph[2:].strip()}}]
                        }
                    })
                elif paragraph.startswith('## '):
                    # Heading 2
                    blocks.append({
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {
                            "rich_text": [{"type": "text", "text": {"content": paragraph[3:].strip()}}]
                        }
                    })
                elif paragraph.startswith('### '):
                    # Heading 3
                    blocks.append({
                        "object": "block",
                        "type": "heading_3",
                        "heading_3": {
                            "rich_text": [{"type": "text", "text": {"content": paragraph[4:].strip()}}]
                        }
                    })
                elif paragraph.startswith('- ') or paragraph.startswith('* '):
                    # Bullet list (simple implementation)
                    blocks.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"type": "text", "text": {"content": paragraph[2:].strip()}}]
                        }
                    })
                else:
                    # Regular paragraph
                    blocks.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": paragraph.strip()}}]
                        }
                    })
        
        return blocks
    
    def _build_page_properties(self, properties: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build page properties for database entries with Austrian efficiency.
        """
        if not properties:
            return {}
        
        notion_properties = {}
        
        for key, value in properties.items():
            if value is None:
                continue
                
            if isinstance(value, str):
                # Text property
                notion_properties[key] = {
                    "rich_text": [{"type": "text", "text": {"content": value}}]
                }
            elif isinstance(value, (int, float)):
                # Number property
                notion_properties[key] = {"number": value}
            elif isinstance(value, bool):
                # Checkbox property
                notion_properties[key] = {"checkbox": value}
            elif isinstance(value, datetime):
                # Date property
                notion_properties[key] = {
                    "date": {"start": value.isoformat()}
                }
            elif isinstance(value, list):
                # Multi-select or select property
                if all(isinstance(item, str) for item in value):
                    notion_properties[key] = {
                        "multi_select": [{"name": item} for item in value]
                    }
            elif isinstance(value, dict) and "type" in value:
                # Direct Notion property format
                notion_properties[key] = value
        
        return notion_properties
    
    async def create_page(
        self,
        title: str,
        content: str = "",
        parent_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        children: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Create a new Notion page with Austrian efficiency.
        
        Args:
            title: Page title (supports German/Japanese characters)
            content: Page content (plain text or simple markdown)
            parent_id: Parent page/database ID
            properties: Page properties (for database pages)
            children: Custom child blocks
        
        Returns:
            Created page information
        """
        try:
            # Build the page data
            page_data = {
                "properties": {
                    "title": {
                        "title": [{"type": "text", "text": {"content": title}}]
                    }
                }
            }
            
            # Add parent
            if parent_id:
                try:
                    # Check if parent is a database or page
                    parent = await self.client.get_page(parent_id)
                    page_data["parent"] = {"page_id": parent_id}
                except:
                    try:
                        parent = await self.client.get_database(parent_id)
                        page_data["parent"] = {"database_id": parent_id}
                        
                        # Add properties for database pages
                        if properties:
                            db_properties = self._build_page_properties(properties)
                            page_data["properties"].update(db_properties)
                    except:
                        raise Exception(f"Parent ID {parent_id} is not a valid page or database")
            else:
                # Create in workspace root
                page_data["parent"] = {"type": "workspace", "workspace": True}
            
            # Create the page
            page = await self.client.create_page(**page_data)
            
            # Add content blocks if provided
            if content or children:
                blocks_to_add = children or self._build_content_blocks(content)
                if blocks_to_add:
                    await self.client.append_block_children(
                        block_id=page["id"],
                        children=blocks_to_add
                    )
            
            logger.info(f"Page created successfully: {title} ({page['id']})")
            return page
            
        except Exception as e:
            logger.error(f"Failed to create page '{title}': {e}")
            raise
    
    async def update_page(
        self,
        page_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        archived: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Update existing page with Austrian efficiency.
        """
        try:
            # Build update data
            update_data = {}
            
            if title is not None:
                update_data["properties"] = {
                    "title": {
                        "title": [{"type": "text", "text": {"content": title}}]
                    }
                }
            
            if properties is not None:
                if "properties" not in update_data:
                    update_data["properties"] = {}
                db_properties = self._build_page_properties(properties)
                update_data["properties"].update(db_properties)
            
            if archived is not None:
                update_data["archived"] = archived
            
            # Update the page
            page = await self.client.update_page(page_id=page_id, **update_data)
            
            # Update content if provided
            if content is not None:
                # For simplicity, append new content blocks
                # In a more sophisticated implementation, we'd replace existing content
                blocks = self._build_content_blocks(content)
                if blocks:
                    await self.client.append_block_children(
                        block_id=page_id,
                        children=blocks
                    )
            
            logger.info(f"Page updated successfully: {page_id}")
            return page
            
        except Exception as e:
            logger.error(f"Failed to update page {page_id}: {e}")
            raise
    
    async def get_page_content(
        self,
        page_id: str,
        include_children: bool = True,
        block_depth: int = 10
    ) -> Dict[str, Any]:
        """
        Retrieve complete page content with Austrian efficiency.
        Budget-aware with intelligent depth limiting.
        """
        try:
            # Get the page metadata
            page = await self.client.get_page(page_id)
            
            result = {
                "page": page,
                "blocks": [],
                "children_count": 0
            }
            
            if include_children and block_depth > 0:
                # Get page content blocks
                blocks = await self._get_all_blocks(page_id, max_depth=block_depth)
                result["blocks"] = blocks
                result["children_count"] = len(blocks)
            
            logger.info(f"Page content retrieved: {page_id} ({result['children_count']} blocks)")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get page content {page_id}: {e}")
            raise
    
    async def _get_all_blocks(self, block_id: str, max_depth: int = 10, current_depth: int = 0) -> List[Dict[str, Any]]:
        """
        Recursively get all blocks with depth limiting for budget efficiency.
        """
        if current_depth >= max_depth:
            return []
        
        all_blocks = []
        start_cursor = None
        
        while True:
            response = await self.client.get_block_children(
                block_id=block_id,
                start_cursor=start_cursor
            )
            
            blocks = response.get("results", [])
            all_blocks.extend(blocks)
            
            # Recursively get children for blocks that can have children
            for block in blocks:
                if block.get("has_children", False):
                    children = await self._get_all_blocks(
                        block["id"],
                        max_depth=max_depth,
                        current_depth=current_depth + 1
                    )
                    block["children"] = children
            
            if not response.get("has_more", False):
                break
            
            start_cursor = response.get("next_cursor")
        
        return all_blocks
    
    async def search_pages(
        self,
        query: str,
        filter_by_type: Optional[str] = None,
        sort_by: str = "last_edited_time",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search pages with natural language queries and Austrian efficiency.
        """
        try:
            # Build search parameters
            search_filter = None
            if filter_by_type:
                search_filter = {
                    "property": "object",
                    "value": filter_by_type
                }
            
            search_sort = {
                "direction": "descending",
                "timestamp": sort_by
            }
            
            # Perform search
            response = await self.client.search(
                query=query,
                filter=search_filter,
                sort=search_sort,
                page_size=limit
            )
            
            results = response.get("results", [])
            logger.info(f"Search completed: '{query}' returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}")
            raise
    
    async def archive_page(
        self,
        page_id: str,
        permanent_delete: bool = False,
        backup_first: bool = True
    ) -> Dict[str, Any]:
        """
        Archive or delete page with Austrian efficiency safety measures.
        """
        try:
            result = {"page_id": page_id, "backup_created": False}
            
            # Create backup if requested
            if backup_first:
                try:
                    backup_content = await self.get_page_content(page_id)
                    result["backup_content"] = backup_content
                    result["backup_created"] = True
                    result["backup_time"] = self.client.format_austrian_date(
                        self.client.get_vienna_time()
                    )
                except Exception as backup_error:
                    logger.warning(f"Backup creation failed: {backup_error}")
            
            if permanent_delete:
                # Notion API doesn't support permanent deletion
                # We archive instead and note the intention
                page = await self.client.update_page(
                    page_id=page_id,
                    archived=True
                )
                result["action"] = "archived"
                result["note"] = "Notion API doesn't support permanent deletion - page archived instead"
            else:
                # Archive the page
                page = await self.client.update_page(
                    page_id=page_id,
                    archived=True
                )
                result["action"] = "archived"
            
            result["page"] = page
            logger.info(f"Page {result['action']}: {page_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to archive page {page_id}: {e}")
            raise
    
    async def get_page_tree(self, page_id: str, max_depth: int = 3) -> Dict[str, Any]:
        """
        Get page hierarchy tree for navigation and organization.
        Austrian efficiency with depth limiting.
        """
        try:
            page = await self.client.get_page(page_id)
            
            result = {
                "page": page,
                "children": [],
                "depth": 0
            }
            
            if max_depth > 0:
                # Get child pages (not all blocks, just pages)
                blocks = await self._get_all_blocks(page_id, max_depth=1)
                child_pages = [
                    block for block in blocks 
                    if block.get("type") == "child_page"
                ]
                
                for child_page in child_pages:
                    child_tree = await self.get_page_tree(
                        child_page["id"],
                        max_depth=max_depth - 1
                    )
                    child_tree["depth"] = 1
                    result["children"].append(child_tree)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get page tree {page_id}: {e}")
            raise
