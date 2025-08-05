# NotionMCP API Reference

**Complete documentation for all 18 tools with Austrian efficiency examples**

## 📄 Page Management Tools (5 tools)

### 1. `create_page`

Create a new Notion page with content, properties, and Austrian efficiency.

**Parameters:**

- `title` (string, required): Page title (supports German characters: ä, ö, ü, ß)
- `content` (string, optional): Page content in plain text or simple markdown
- `parent_id` (string, optional): Parent page/database ID. If not provided, creates in workspace root
- `properties` (object, optional): Page properties if parent is a database
- `children` (array, optional): Custom child blocks to add to the page

**Returns:**

```json
{
  "success": true,
  "page_id": "12345678-1234-1234-1234-123456789012",
  "url": "https://notion.so/...",
  "title": "Page Title",
  "message": "Page 'Title' created with Austrian efficiency! ✅"
}
```

**Examples:**

```javascript
// Simple page creation
await create_page({
  title: "Research Notes - Machine Learning",
  content: "# Introduction\n\nThis page contains my research on ML algorithms..."
});

// Page in database with properties
await create_page({
  title: "Attack on Titan - Season 4",
  parent_id: "anime_database_id",
  properties: {
    "Status": "Completed",
    "Rating": 9,
    "Episodes": 16,
    "Genre": ["Action", "Drama"]
  },
  content: "Final season analysis and thoughts..."
});

// Academic paper with German characters
await create_page({
  title: "Künstliche Intelligenz Forschung",
  content: "## Überblick\n\nDiese Forschung beschäftigt sich mit...",
  properties: {
    "Author": "Dr. Müller",
    "University": "Universität Wien"
  }
});
```

### 2. `update_page`

Update existing Notion page content, properties, or archive status.

**Parameters:**

- `page_id` (string, required): Page ID to update
- `title` (string, optional): New page title
- `content` (string, optional): New page content
- `properties` (object, optional): Updated properties
- `archived` (boolean, optional): Archive status

**Returns:**

```json
{
  "success": true,
  "page_id": "12345678-1234-1234-1234-123456789012",
  "updated_fields": ["title", "properties"],
  "message": "Page updated with Austrian efficiency! ✅"
}
```

**Examples:**

```javascript
// Update anime status
await update_page({
  page_id: "anime_page_id",
  properties: {
    "Status": "Completed",
    "Rating": 8,
    "Completed_Date": "2025-07-22"
  }
});

// Add research findings
await update_page({
  page_id: "research_page_id",
  content: "## New Findings\n\nRecent experiments show that...",
  properties: {
    "Last_Updated": "22.07.2025",
    "Status": "In Progress"
  }
});
```

### 3. `get_page_content`

Retrieve complete page content including all blocks and metadata.

**Parameters:**

- `page_id` (string, required): Page ID to retrieve
- `include_children` (boolean, default: true): Include child blocks
- `block_depth` (number, default: 10): Maximum depth for nested blocks

**Returns:**

```json
{
  "success": true,
  "page": {
    "page": {/* page metadata */},
    "blocks": [/* all blocks */],
    "children_count": 25
  },
  "message": "Page content retrieved with Austrian efficiency! ✅"
}
```

**Examples:**

```javascript
// Get full page content
const content = await get_page_content({
  page_id: "research_page_id",
  include_children: true,
  block_depth: 5
});

// Get page metadata only
const metadata = await get_page_content({
  page_id: "page_id",
  include_children: false
});
```

### 4. `search_pages`

Natural language search across entire Notion workspace.

**Parameters:**

- `query` (string, required): Search query (natural language)
- `filter_by_type` (string, optional): Filter by object type: "page" or "database"
- `sort_by` (string, default: "last_edited_time"): Sort field
- `limit` (number, default: 10): Maximum results to return

**Returns:**

```json
{
  "success": true,
  "results": [/* search results */],
  "count": 5,
  "query": "machine learning research",
  "message": "Found 5 results with Austrian efficiency! 🔍"
}
```

**Examples:**

```javascript
// Academic research search
const research = await search_pages({
  query: "machine learning neural networks",
  filter_by_type: "page",
  limit: 20
});

// Anime search with Japanese characters
const anime = await search_pages({
  query: "進撃の巨人 Attack on Titan",
  sort_by: "created_time",
  limit: 10
});

// Project search
const projects = await search_pages({
  query: "incomplete tasks high priority",
  filter_by_type: "database"
});
```

### 5. `archive_page`

Safely archive or delete pages with Austrian efficiency confirmations.

**Parameters:**

- `page_id` (string, required): Page ID to archive
- `permanent_delete` (boolean, default: false): Permanently delete instead of archive
- `backup_first` (boolean, default: true): Create backup before deletion

**Returns:**

```json
{
  "success": true,
  "page_id": "12345678-1234-1234-1234-123456789012",
  "action": "archived",
  "backup_created": true,
  "message": "Page archived with Austrian efficiency! ✅"
}
```

**Examples:**

```javascript
// Archive with backup
await archive_page({
  page_id: "old_project_id",
  backup_first: true
});

// Archive without backup (Austrian efficiency)
await archive_page({
  page_id: "temporary_page_id", 
  backup_first: false
});
```

## 🗄️ Database Operations (6 tools)

### 6. `create_database`

Create databases with custom property schemas for academic and weeb content.

**Parameters:**

- `title` (string, required): Database title
- `parent_id` (string, required): Parent page ID where database will be created
- `properties_schema` (object, required): Database properties schema
- `icon` (string, optional): Database icon (emoji or external URL)
- `cover` (string, optional): Database cover image URL

**Returns:**

```json
{
  "success": true,
  "database_id": "12345678-1234-1234-1234-123456789012",
  "url": "https://notion.so/...",
  "title": "Database Title",
  "properties": {/* created properties */},
  "message": "Database 'Title' created with Austrian efficiency! 🗄️"
}
```

**Examples:**

```javascript
// Academic research database
await create_database({
  title: "Research Papers Database",
  parent_id: "research_page_id",
  properties_schema: {
    "Title": "title",
    "Authors": "multi_select",
    "Publication_Year": "number",
    "Status": {
      "type": "select",
      "options": ["To Read", "Reading", "Read", "Cited"]
    },
    "Rating": "number",
    "DOI": "url",
    "Notes": "rich_text",
    "Tags": "multi_select"
  },
  icon: "📚"
});

// Anime tracking database
await create_database({
  title: "Anime Collection 🎌",
  parent_id: "weeb_page_id",
  properties_schema: {
    "Title": "title",
    "Japanese_Title": "rich_text",
    "Status": {
      "type": "select", 
      "options": ["Watching", "Completed", "Plan to Watch", "Dropped", "On Hold"]
    },
    "Rating": "number",
    "Episodes_Watched": "number",
    "Total_Episodes": "number",
    "Genre": "multi_select",
    "Studio": "rich_text",
    "Season": "rich_text",
    "Year": "number",
    "MyAnimeList_Score": "number"
  },
  icon: "🎌",
  cover: "https://example.com/anime-cover.jpg"
});

// Project management database (Vienna context)
await create_database({
  title: "Projekte Wien 🇦🇹",
  parent_id: "projects_page_id",
  properties_schema: {
    "Projekt_Name": "title",
    "Status": {
      "type": "select",
      "options": ["Geplant", "In Arbeit", "Abgeschlossen", "Pausiert"]
    },
    "Priorität": {
      "type": "select", 
      "options": ["Niedrig", "Mittel", "Hoch", "Kritisch"]
    },
    "Fälligkeitsdatum": "date",
    "Verantwortlich": "person",
    "Fortschritt": "number",
    "Budget_EUR": "number"
  },
  icon: "🏗️"
});
```

### 7. `query_database`

Query databases with complex filters and sorts for academic research.

**Parameters:**

- `database_id` (string, required): Database ID to query
- `filter` (object, optional): Query filter conditions
- `sorts` (array, optional): Sort configuration
- `limit` (number, default: 100): Maximum results
- `cursor` (string, optional): Pagination cursor

**Returns:**

```json
{
  "success": true,
  "results": [/* query results */],
  "has_more": false,
  "next_cursor": null,
  "count": 15,
  "message": "Query completed with Austrian efficiency! 🔍"
}
```

**Examples:**

```javascript
// Find incomplete anime
const incomplete_anime = await query_database({
  database_id: "anime_db_id",
  filter: {
    "and": [
      {
        "property": "Status",
        "select": {
          "does_not_equal": "Completed"
        }
      },
      {
        "property": "Rating",
        "number": {
          "greater_than": 7
        }
      }
    ]
  },
  sorts: [
    {
      "property": "Rating",
      "direction": "descending"
    },
    {
      "property": "Title", 
      "direction": "ascending"
    }
  ],
  limit: 50
});

// Academic research by year
const recent_research = await query_database({
  database_id: "research_db_id",
  filter: {
    "and": [
      {
        "property": "Publication_Year",
        "number": {
          "greater_than_or_equal_to": 2020
        }
      },
      {
        "property": "Status",
        "select": {
          "equals": "Read"
        }
      }
    ]
  },
  sorts: [
    {
      "property": "Publication_Year",
      "direction": "descending"
    }
  ]
});

// High priority Vienna projects
const priority_projects = await query_database({
  database_id: "vienna_projects_db_id",
  filter: {
    "property": "Priorität",
    "select": {
      "equals": "Hoch"
    }
  },
  sorts: [
    {
      "property": "Fälligkeitsdatum",
      "direction": "ascending"
    }
  ]
});
```

### 8. `create_database_entry`

Add entries with all property types for academic and anime tracking.

**Parameters:**

- `database_id` (string, required): Database ID to add entry to
- `properties` (object, required): Entry properties
- `content` (string, optional): Entry content
- `children` (array, optional): Child blocks

**Returns:**

```json
{
  "success": true,
  "page_id": "12345678-1234-1234-1234-123456789012",
  "database_id": "database_id",
  "properties": {/* created properties */},
  "message": "Database entry created with Austrian efficiency! ✅"
}
```

**Examples:**

```javascript
// Add research paper
await create_database_entry({
  database_id: "research_db_id",
  properties: {
    "Title": "Attention Is All You Need",
    "Authors": ["Vaswani", "Shazeer", "Parmar", "Uszkoreit"],
    "Publication_Year": 2017,
    "Status": "Read",
    "Rating": 5,
    "DOI": "https://arxiv.org/abs/1706.03762",
    "Tags": ["Transformers", "Attention", "NLP", "Deep Learning"]
  },
  content: "# Summary\n\nRevolutionary paper introducing the Transformer architecture...\n\n## Key Contributions\n\n- Self-attention mechanism\n- Parallelizable architecture\n- State-of-the-art results"
});

// Add anime with Japanese title
await create_database_entry({
  database_id: "anime_db_id",
  properties: {
    "Title": "Attack on Titan",
    "Japanese_Title": "進撃の巨人 (Shingeki no Kyojin)",
    "Status": "Completed",
    "Rating": 9,
    "Episodes_Watched": 75,
    "Total_Episodes": 75,
    "Genre": ["Action", "Drama", "Fantasy", "Military"],
    "Studio": "MAPPA",
    "Season": "Final Season",
    "Year": 2023,
    "MyAnimeList_Score": 9.0
  },
  content: "# Review\n\nEpic conclusion to one of the greatest anime series...\n\n## Highlights\n- Incredible animation by MAPPA\n- Complex moral themes\n- Satisfying ending"
});

// Add Vienna project
await create_database_entry({
  database_id: "vienna_projects_db_id",
  properties: {
    "Projekt_Name": "NotionMCP Entwicklung",
    "Status": "In Arbeit",
    "Priorität": "Hoch", 
    "Fälligkeitsdatum": "2025-07-25",
    "Fortschritt": 75,
    "Budget_EUR": 0
  },
  content: "## Projektbeschreibung\n\nEntwicklung eines MCP-Servers für Notion-Workspace-Management mit österreichischer Effizienz.\n\n### Fortschritt\n- ✅ Grundstruktur implementiert\n- ✅ 18 Tools entwickelt\n- 🔄 Dokumentation und Tests\n- ⏳ Deployment vorbereiten"
});
```

### 9. `update_database_entry`

Update existing database entries and properties with Austrian efficiency.

**Parameters:**

- `page_id` (string, required): Entry page ID to update
- `properties` (object, optional): Updated properties
- `content` (string, optional): Updated content
- `archived` (boolean, optional): Archive status

**Examples:**

```javascript
// Update anime progress
await update_database_entry({
  page_id: "anime_entry_id",
  properties: {
    "Episodes_Watched": 12,
    "Status": "Watching",
    "Last_Watched": "2025-07-22"
  }
});

// Complete research paper
await update_database_entry({
  page_id: "research_entry_id", 
  properties: {
    "Status": "Cited",
    "Citation_Count": 1,
    "Notes": "Used in Chapter 3 of thesis"
  },
  content: "## Updated Analysis\n\nAfter citing this paper in my thesis..."
});
```

### 10. `get_database_schema`

Retrieve database structure, properties, and metadata for planning.

**Parameters:**

- `database_id` (string, required): Database ID to analyze
- `include_statistics` (boolean, default: false): Include usage statistics
- `property_details` (boolean, default: true): Include detailed property information

**Examples:**

```javascript
// Analyze anime database structure
const anime_schema = await get_database_schema({
  database_id: "anime_db_id",
  include_statistics: true,
  property_details: true
});

// Quick schema check
const research_schema = await get_database_schema({
  database_id: "research_db_id",
  property_details: false
});
```

### 11. `bulk_import_data`

Import CSV/JSON data efficiently for academic datasets and anime lists.

**Parameters:**

- `database_id` (string, required): Target database ID
- `data_source` (string, required): CSV or JSON data to import
- `mapping` (object, optional): Field mapping (source -> target)
- `merge_strategy` (string, default: "create_new"): How to handle existing data

**Examples:**

```javascript
// Import anime list from CSV
const anime_csv = `Title,Status,Rating,Episodes
"Death Note","Completed",9,37
"Naruto","Completed",8,720
"One Piece","Watching",9,1000+`;

await bulk_import_data({
  database_id: "anime_db_id",
  data_source: anime_csv,
  mapping: {
    "Title": "Title",
    "Status": "Status", 
    "Rating": "Rating",
    "Episodes": "Total_Episodes"
  }
});

// Import research papers from JSON
const research_json = `[
  {
    "paper_title": "BERT: Pre-training of Deep Bidirectional Transformers",
    "authors": "Devlin et al.",
    "year": 2018,
    "status": "To Read",
    "venue": "NAACL"
  },
  {
    "paper_title": "GPT-3: Language Models are Few-Shot Learners", 
    "authors": "Brown et al.",
    "year": 2020,
    "status": "Read",
    "venue": "NeurIPS"
  }
]`;

await bulk_import_data({
  database_id: "research_db_id",
  data_source: research_json,
  mapping: {
    "paper_title": "Title",
    "authors": "Authors",
    "year": "Publication_Year",
    "status": "Status",
    "venue": "Venue"
  }
});
```

## 💬 Collaboration Tools (3 tools)

### 12. `add_comment`

Add comments to pages or specific blocks for academic discussions.

**Parameters:**

- `page_id` (string, required): Page or block ID to comment on
- `content` (string, required): Comment content
- `parent_comment_id` (string, optional): Parent comment for threaded discussions
- `rich_text` (array, optional): Rich text formatting

**Examples:**

```javascript
// Academic feedback
await add_comment({
  page_id: "thesis_page_id",
  content: "The methodology section needs more detail about the data collection process. Consider adding information about sample size and selection criteria."
});

// Anime discussion
await add_comment({
  page_id: "anime_review_id",
  content: "I disagree with the rating - the animation quality in the final season was exceptional! MAPPA did an amazing job with the action sequences. 🎌"
});

// Threaded discussion
await add_comment({
  page_id: "research_page_id",
  content: "I found additional papers that support this hypothesis. Should we include them in the literature review?",
  parent_comment_id: "previous_comment_id"
});
```

### 13. `get_comments`

Retrieve page/block discussions and comment threads.

**Parameters:**

- `page_id` (string, required): Page ID to get comments from
- `include_resolved` (boolean, default: false): Include resolved comments
- `sort_by` (string, default: "created_time"): Sort field
- `limit` (number, default: 50): Maximum comments to return

**Examples:**

```javascript
// Get all active comments
const active_comments = await get_comments({
  page_id: "thesis_page_id",
  include_resolved: false,
  sort_by: "created_time",
  limit: 100
});

// Review feedback history
const all_feedback = await get_comments({
  page_id: "paper_draft_id",
  include_resolved: true,
  sort_by: "last_edited_time"
});
```

### 14. `get_workspace_users`

List workspace users, permissions, and activity for team management.

**Parameters:**

- `include_inactive` (boolean, default: false): Include inactive users
- `permission_level` (string, optional): Filter by permission level
- `sort_by` (string, default: "name"): Sort field

**Examples:**

```javascript
// Get active collaborators
const active_users = await get_workspace_users({
  include_inactive: false,
  sort_by: "name"
});

// Full user audit
const all_users = await get_workspace_users({
  include_inactive: true,
  sort_by: "last_active"
});
```

## 🔍 Advanced Features (4 tools)

### 15. `setup_automation`

Create Notion automations with webhook integration.

**Parameters:**

- `trigger_type` (string, required): Automation trigger type
- `conditions` (object, required): Trigger conditions
- `actions` (array, required): Actions to perform
- `webhook_url` (string, optional): Optional webhook URL

**Examples:**

```javascript
// Notify when research status changes
await setup_automation({
  trigger_type: "database_entry_updated",
  conditions: {
    "database_id": "research_db_id",
    "property": "Status",
    "value": "Read"
  },
  actions: [
    {
      "type": "send_notification",
      "message": "New paper read and ready for citation! 📚"
    },
    {
      "type": "update_property",
      "target_property": "Last_Activity",
      "value": "{{current_date}}"
    }
  ],
  webhook_url: "https://your-webhook.com/research-updates"
});

// Anime completion celebration
await setup_automation({
  trigger_type: "database_entry_updated",
  conditions: {
    "database_id": "anime_db_id",
    "property": "Status", 
    "value": "Completed"
  },
  actions: [
    {
      "type": "send_notification",
      "message": "Anime completed! Time to update MyAnimeList 🎌"
    },
    {
      "type": "create_page",
      "parent_id": "reviews_page_id",
      "template": "anime_review_template"
    }
  ]
});
```

### 16. `sync_external_data`

Create synced databases from external tools and APIs.

**Parameters:**

- `external_source` (string, required): External data source type
- `sync_config` (object, required): Sync configuration
- `update_frequency` (string, default: "daily"): Update frequency

**Examples:**

```javascript
// Sync GitHub repositories
await sync_external_data({
  external_source: "github",
  sync_config: {
    "username": "sandra-vienna",
    "repositories": ["notionmcp", "fastsearch", "virtualbox-mcp"],
    "include_issues": true,
    "include_prs": true,
    "target_database": "projects_db_id"
  },
  update_frequency: "daily"
});

// Sync MyAnimeList
await sync_external_data({
  external_source: "myanimelist",
  sync_config: {
    "username": "sandra_weeb",
    "list_type": "anime",
    "target_database": "anime_db_id",
    "sync_ratings": true,
    "sync_progress": true
  },
  update_frequency: "weekly"
});

// Sync academic papers from arXiv
await sync_external_data({
  external_source: "arxiv",
  sync_config: {
    "categories": ["cs.AI", "cs.LG", "cs.CL"],
    "max_papers_per_day": 10,
    "target_database": "research_db_id",
    "keywords": ["transformer", "attention", "language model"]
  },
  update_frequency: "daily"
});
```

### 17. `generate_ai_summary`

Use Notion AI for page/database content summaries and analysis.

**Parameters:**

- `page_id` (string, required): Page ID to analyze
- `summary_type` (string, default: "comprehensive"): Summary type
- `length` (string, default: "medium"): Summary length
- `focus_areas` (array, optional): Areas to focus on

**Examples:**

```javascript
// Research paper analysis
const paper_summary = await generate_ai_summary({
  page_id: "transformer_paper_id",
  summary_type: "comprehensive",
  length: "long",
  focus_areas: ["methodology", "results", "implications", "future_work"]
});

// Anime season review
const anime_summary = await generate_ai_summary({
  page_id: "aot_final_season_id",
  summary_type: "bullet_points",
  length: "medium", 
  focus_areas: ["plot", "animation", "character_development"]
});

// Project status overview
const project_summary = await generate_ai_summary({
  page_id: "notionmcp_project_id",
  summary_type: "key_insights",
  length: "short",
  focus_areas: ["progress", "challenges", "next_steps"]
});
```

### 18. `export_workspace_data`

Backup and export functionality with multiple formats and Austrian efficiency.

**Parameters:**

- `scope` (string, default: "workspace"): Export scope
- `format` (string, default: "json"): Export format
- `include_metadata` (boolean, default: true): Include metadata
- `compression` (boolean, default: true): Compress export

**Examples:**

```javascript
// Full workspace backup
const full_backup = await export_workspace_data({
  scope: "workspace",
  format: "json",
  include_metadata: true,
  compression: true
});

// Research database export for sharing
const research_export = await export_workspace_data({
  scope: "research_database_id",
  format: "csv",
  include_metadata: false,
  compression: false
});

// Academic citations export
const citations_export = await export_workspace_data({
  scope: "bibliography_database_id", 
  format: "bibtex",
  include_metadata: true,
  compression: false
});
```

## 🧪 Testing and Health Check

### `test_connection`

Test Notion API connection and server health.

**Parameters:** None

**Returns:**

```json
{
  "connection": {
    "success": true,
    "user": {/* current user info */},
    "timezone": "Europe/Vienna",
    "current_time": "22.07.2025 18:30",
    "requests_made": 42,
    "message": "Connection successful with Austrian efficiency! 🇦🇹"
  },
  "server_stats": {
    "total_requests": 42,
    "total_errors": 0,
    "success_rate": 100.0,
    "current_time": "22.07.2025 18:30",
    "timezone": "Europe/Vienna",
    "version": "2022-06-28"
  },
  "message": "NotionMCP server healthy with Austrian efficiency! 🇦🇹"
}
```

**Example:**

```javascript
// Health check
const health = await test_connection();
console.log(`Server health: ${health.connection.success ? '✅' : '❌'}`);
console.log(`API requests made: ${health.server_stats.total_requests}`);
console.log(`Success rate: ${health.server_stats.success_rate}%`);
```

## 🔧 Error Handling

All tools return consistent error responses with Austrian directness:

```json
{
  "success": false,
  "error": "Specific error description",
  "message": "User-friendly error message with next steps"
}
```

**Common Errors:**

- **Authentication**: `"Notion API token is invalid or expired. Check your integration settings."`
- **Rate Limit**: `"Rate limit exceeded. Please wait before making more requests."`
- **Not Found**: `"The requested page/database was not found. Check the ID and permissions."`
- **Validation**: `"Invalid request data: [specific validation error]"`

## 🇦🇹 Austrian Efficiency Tips

1. **Batch operations**: Use `bulk_import_data` for large datasets
2. **Smart filtering**: Use specific filters in `query_database` to reduce API calls
3. **Depth limiting**: Set appropriate `block_depth` in `get_page_content`
4. **Caching**: Enable caching for frequently accessed content
5. **Vienna timezone**: All dates automatically formatted as DD.MM.YYYY
6. **Budget monitoring**: Track `total_requests` in `test_connection` response

## 📚 Academic Templates Quick Reference

```javascript
// Research Paper Database Schema
{
  "Title": "title",
  "Authors": "multi_select", 
  "Publication_Year": "number",
  "Status": {"type": "select", "options": ["To Read", "Reading", "Read", "Cited"]},
  "Rating": "number",
  "DOI": "url", 
  "Tags": "multi_select",
  "Notes": "rich_text",
  "Citation_Count": "number"
}

// Project Management Schema
{
  "Project_Name": "title",
  "Status": {"type": "select", "options": ["Planning", "In Progress", "Completed", "On Hold"]},
  "Priority": {"type": "select", "options": ["Low", "Medium", "High", "Critical"]},
  "Due_Date": "date",
  "Assignee": "person",
  "Progress": "number",
  "Budget": "number"
}
```

## 🎌 Weeb Templates Quick Reference

```javascript
// Anime Database Schema
{
  "Title": "title",
  "Japanese_Title": "rich_text",
  "Status": {"type": "select", "options": ["Watching", "Completed", "Plan to Watch", "Dropped", "On Hold"]},
  "Rating": "number",
  "Episodes_Watched": "number", 
  "Total_Episodes": "number",
  "Genre": "multi_select",
  "Studio": "rich_text",
  "Season": "rich_text",
  "Year": "number"
}

// Japanese Learning Schema
{
  "Word": "title",
  "Hiragana": "rich_text",
  "Katakana": "rich_text",
  "Kanji": "rich_text", 
  "Meaning": "rich_text",
  "JLPT_Level": {"type": "select", "options": ["N5", "N4", "N3", "N2", "N1"]},
  "Example": "rich_text",
  "Learned": "checkbox"
}
```

---

**Built with Austrian efficiency in Vienna 🇦🇹**  
*Complete API documentation for practical Notion management without hype.*
