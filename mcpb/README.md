# notion-mcp (MCPB Bundle)

FastMCP 3.1.0 server for comprehensive Notion workspace management and RAG

## Usage

Add to \claude_desktop_config.json\:
\\\json
{
  "mcpServers": {
    "notion-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "\D:\Dev\repos", "python", "-m", "notion_mcp"],
      "env": { "PYTHONPATH": "\D:\Dev\repos/src" }
    }
  }
}
\\\

## Tools

- **notion-mcp**: FastMCP 3.1.0 server for comprehensive Notion workspace management and RAG

## Requirements

- Python 3.12+
- uv
