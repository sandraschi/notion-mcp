"""
NotionMCP - Collaboration Management Operations
Austrian Efficiency Implementation for Team and Academic Collaboration

Features:
- Comment management (create, retrieve, resolve)
- User and workspace management
- Permission handling
- Discussion thread organization
- Perfect for academic collaboration and project feedback
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger("notionmcp.collaboration")

class CollaborationManager:
    """
    Comprehensive collaboration management with Austrian efficiency.
    Perfect for academic discussions, project feedback, and team coordination.
    """
    
    def __init__(self, notion_client):
        """Initialize with NotionClient instance."""
        self.client = notion_client
    
    def _build_comment_content(self, content: str) -> List[Dict[str, Any]]:
        """
        Build comment rich text content with Austrian efficiency.
        Supports German and Japanese characters for international collaboration.
        """
        if not content:
            return []
        
        # Simple implementation - can be enhanced for mentions, formatting
        return [{
            "type": "text",
            "text": {"content": content},
            "plain_text": content
        }]
    
    async def add_comment(
        self,
        page_id: str,
        content: str,
        parent_comment_id: Optional[str] = None,
        rich_text: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Add comment to page or specific block with Austrian efficiency.
        
        Args:
            page_id: Page or block ID to comment on
            content: Comment content (plain text)
            parent_comment_id: ID of parent comment for threaded discussions
            rich_text: Optional rich text formatting (overrides content)
        
        Returns:
            Created comment information
        """
        try:
            # Note: As of 2024/2025, Notion API has limited comment support
            # This is a placeholder implementation that would work when/if 
            # Notion expands their comments API
            
            # Build comment data
            comment_data = {
                "parent": {"page_id": page_id},
                "rich_text": rich_text or self._build_comment_content(content)
            }
            
            if parent_comment_id:
                comment_data["parent"] = {"comment_id": parent_comment_id}
            
            # For now, we'll simulate comment creation by adding a note block
            # This is a workaround until Notion provides full comment API
            comment_block = {
                "type": "callout",
                "callout": {
                    "rich_text": comment_data["rich_text"],
                    "icon": {"emoji": "💬"},
                    "color": "gray_background"
                }
            }
            
            # Add timestamp in Austrian format
            timestamp = self.client.format_austrian_date(self.client.get_vienna_time())
            timestamp_block = {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": f"Comment added: {timestamp}"},
                        "annotations": {"italic": True, "color": "gray"}
                    }]
                }
            }
            
            # Append comment blocks to page
            await self.client.append_block_children(
                block_id=page_id,
                children=[comment_block, timestamp_block]
            )
            
            result = {
                "id": f"comment_{int(datetime.now().timestamp())}",
                "type": "comment",
                "content": content,
                "page_id": page_id,
                "created_time": timestamp,
                "parent_comment_id": parent_comment_id
            }
            
            logger.info(f"Comment added to page: {page_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to add comment to {page_id}: {e}")
            raise Exception(f"Comment creation failed: {str(e)}")
    
    async def get_comments(
        self,
        page_id: str,
        include_resolved: bool = False,
        sort_by: str = "created_time",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieve page/block discussions and comment threads with Austrian efficiency.
        
        Args:
            page_id: Page ID to get comments from
            include_resolved: Include resolved comments
            sort_by: Sort field (created_time, last_edited_time)
            limit: Maximum comments to return
        
        Returns:
            List of comments and discussions
        """
        try:
            # Note: This is a workaround implementation since Notion's comment API is limited
            # We'll look for callout blocks that represent comments
            
            # Get page blocks
            from .pages import PageManager
            page_manager = PageManager(self.client)
            page_content = await page_manager.get_page_content(page_id, include_children=True)
            
            comments = []
            blocks = page_content.get("blocks", [])
            
            for block in blocks:
                if block.get("type") == "callout":
                    callout = block.get("callout", {})
                    icon = callout.get("icon", {})
                    
                    # Check if it's a comment block (has comment emoji)
                    if icon.get("emoji") == "💬":
                        rich_text = callout.get("rich_text", [])
                        content = ""
                        if rich_text:
                            content = rich_text[0].get("plain_text", "")
                        
                        comment = {
                            "id": block.get("id"),
                            "type": "comment",
                            "content": content,
                            "page_id": page_id,
                            "created_time": block.get("created_time"),
                            "last_edited_time": block.get("last_edited_time"),
                            "resolved": False  # No way to track this in current implementation
                        }
                        
                        if include_resolved or not comment["resolved"]:
                            comments.append(comment)
            
            # Sort comments
            if sort_by == "created_time":
                comments.sort(key=lambda x: x.get("created_time", ""))
            elif sort_by == "last_edited_time":
                comments.sort(key=lambda x: x.get("last_edited_time", ""))
            
            # Apply limit
            comments = comments[:limit]
            
            logger.info(f"Retrieved {len(comments)} comments from page: {page_id}")
            return comments
            
        except Exception as e:
            logger.error(f"Failed to get comments from {page_id}: {e}")
            raise Exception(f"Comment retrieval failed: {str(e)}")
    
    async def get_workspace_users(
        self,
        include_inactive: bool = False,
        permission_level: Optional[str] = None,
        sort_by: str = "name"
    ) -> List[Dict[str, Any]]:
        """
        List workspace users, permissions, and activity with Austrian efficiency.
        
        Args:
            include_inactive: Include inactive/deactivated users
            permission_level: Filter by permission level
            sort_by: Sort field (name, email, last_active)
        
        Returns:
            List of workspace users with details
        """
        try:
            # Get all users
            all_users = []
            start_cursor = None
            
            while True:
                response = await self.client.get_users(start_cursor=start_cursor)
                users = response.get("results", [])
                all_users.extend(users)
                
                if not response.get("has_more", False):
                    break
                start_cursor = response.get("next_cursor")
            
            # Process and filter users
            processed_users = []
            for user in all_users:
                user_info = {
                    "id": user.get("id"),
                    "type": user.get("type"),
                    "name": user.get("name", ""),
                    "avatar_url": user.get("avatar_url"),
                    "email": user.get("email", ""),
                    "object": user.get("object"),
                    "last_active": "Unknown"  # Notion doesn't provide this
                }
                
                # Determine if user is active
                user_type = user.get("type", "")
                is_active = user_type == "person"  # Simple heuristic
                
                # Apply filters
                if not include_inactive and not is_active:
                    continue
                
                if permission_level:
                    # Notion doesn't provide detailed permission info via users API
                    # This would need to be enhanced with workspace permission checking
                    user_info["permission_level"] = "Unknown"
                
                processed_users.append(user_info)
            
            # Sort users
            if sort_by == "name":
                processed_users.sort(key=lambda x: x.get("name", "").lower())
            elif sort_by == "email":
                processed_users.sort(key=lambda x: x.get("email", "").lower())
            
            logger.info(f"Retrieved {len(processed_users)} workspace users")
            return processed_users
            
        except Exception as e:
            logger.error(f"Failed to get workspace users: {e}")
            raise Exception(f"User retrieval failed: {str(e)}")
    
    async def get_user_details(self, user_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific user with Austrian efficiency.
        
        Args:
            user_id: User ID to retrieve details for
        
        Returns:
            Detailed user information
        """
        try:
            user = await self.client.get_user(user_id)
            
            user_details = {
                "id": user.get("id"),
                "type": user.get("type"),
                "name": user.get("name", ""),
                "avatar_url": user.get("avatar_url"),
                "email": user.get("email", ""),
                "object": user.get("object"),
                "workspace_role": "Unknown",  # Not available via API
                "last_active": "Unknown",     # Not available via API
                "timezone": "Unknown",        # Not available via API
                "language": "Unknown"         # Not available via API
            }
            
            logger.info(f"Retrieved user details: {user_id}")
            return user_details
            
        except Exception as e:
            logger.error(f"Failed to get user details {user_id}: {e}")
            raise Exception(f"User details retrieval failed: {str(e)}")
    
    async def get_page_permissions(self, page_id: str) -> Dict[str, Any]:
        """
        Get page sharing and permission information (Austrian efficiency placeholder).
        
        Note: Notion API has limited permission querying capabilities.
        This is a placeholder for when/if expanded permission APIs become available.
        """
        try:
            # Get page to check basic properties
            page = await self.client.get_page(page_id)
            
            # Basic permission info (limited by API)
            permissions = {
                "page_id": page_id,
                "object": page.get("object"),
                "parent": page.get("parent"),
                "created_by": page.get("created_by"),
                "last_edited_by": page.get("last_edited_by"),
                "public_access": "Unknown",     # Not available via API
                "workspace_access": "Unknown",  # Not available via API
                "shared_users": "Unknown",      # Not available via API
                "permission_level": "Unknown",  # Not available via API
                "message": "Notion API has limited permission querying - check workspace settings manually"
            }
            
            logger.info(f"Retrieved basic permission info for page: {page_id}")
            return permissions
            
        except Exception as e:
            logger.error(f"Failed to get page permissions {page_id}: {e}")
            raise Exception(f"Permission retrieval failed: {str(e)}")
    
    async def get_collaboration_stats(self, page_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get collaboration statistics with Austrian efficiency.
        
        Args:
            page_id: Optional page ID for page-specific stats
        
        Returns:
            Collaboration statistics and activity summary
        """
        try:
            stats = {
                "timestamp": self.client.format_austrian_date(self.client.get_vienna_time()),
                "timezone": str(self.client.timezone)
            }
            
            if page_id:
                # Page-specific collaboration stats
                try:
                    page = await self.client.get_page(page_id)
                    comments = await self.get_comments(page_id, include_resolved=True)
                    
                    stats.update({
                        "page_id": page_id,
                        "page_title": "Unknown",  # Would need to parse title property
                        "total_comments": len(comments),
                        "active_comments": len([c for c in comments if not c.get("resolved", False)]),
                        "last_activity": page.get("last_edited_time"),
                        "created_by": page.get("created_by", {}),
                        "last_edited_by": page.get("last_edited_by", {})
                    })
                except Exception as page_error:
                    stats["page_error"] = str(page_error)
            else:
                # Workspace-wide collaboration stats
                try:
                    users = await self.get_workspace_users(include_inactive=True)
                    active_users = [u for u in users if u.get("type") == "person"]
                    
                    stats.update({
                        "scope": "workspace",
                        "total_users": len(users),
                        "active_users": len(active_users),
                        "bot_users": len([u for u in users if u.get("type") == "bot"]),
                        "api_usage": await self.client.get_stats()
                    })
                except Exception as workspace_error:
                    stats["workspace_error"] = str(workspace_error)
            
            logger.info(f"Collaboration stats generated: {stats.get('scope', 'page')}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collaboration stats: {e}")
            raise Exception(f"Stats retrieval failed: {str(e)}")
    
    async def mention_user_in_comment(
        self,
        page_id: str,
        content: str,
        mentioned_user_id: str,
        user_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create comment with user mention - Austrian efficiency implementation.
        
        Args:
            page_id: Page to comment on
            content: Comment content
            mentioned_user_id: User ID to mention
            user_name: Optional user display name
        
        Returns:
            Comment with mention information
        """
        try:
            # Get user details if name not provided
            if not user_name:
                user_details = await self.get_user_details(mentioned_user_id)
                user_name = user_details.get("name", "Unknown User")
            
            # Build rich text with mention
            rich_text = [
                {
                    "type": "mention",
                    "mention": {"user": {"id": mentioned_user_id}},
                    "plain_text": f"@{user_name}"
                },
                {
                    "type": "text",
                    "text": {"content": f" {content}"},
                    "plain_text": f" {content}"
                }
            ]
            
            # Create comment with mention
            comment = await self.add_comment(
                page_id=page_id,
                content=f"@{user_name} {content}",
                rich_text=rich_text
            )
            
            comment["mentioned_user"] = {
                "id": mentioned_user_id,
                "name": user_name
            }
            
            logger.info(f"Comment with mention created: {page_id} -> @{user_name}")
            return comment
            
        except Exception as e:
            logger.error(f"Failed to create comment with mention: {e}")
            raise Exception(f"Mention comment failed: {str(e)}")
