---
name: notion-mcp
description: Notion workspace management — search, read, create, and sync pages and databases
---

# notion-mcp skill

## Session Context (notion-mcp)

You can read, search, create, and manage Notion pages, databases, and comments (40 tools).

**Before starting work:**
1. Find task-relevant pages: search_notion_knowledge(query="<topic>", mode="hybrid")
2. Check backend health: GET /api/health on :10811 (dashboard :10810)

**At end of work:**
- Export changed scope: export_workspace_data(scope="workspace", format="json")
- Leave the tree clean: commit finished work, revert the rest
