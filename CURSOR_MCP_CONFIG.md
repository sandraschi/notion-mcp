# Cursor MCP Configuration for Notion MCP

## Configuration

Add this to your Cursor MCP settings (usually in `.cursor/mcp.json` or Cursor Settings):

```json
{
  "mcpServers": {
    "notion-mcp": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "${workspaceFolder}/notion-mcp",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/notion-mcp",
        "PYTHONUNBUFFERED": "1",
        "NOTION_TOKEN": "your_notion_token_here"
      }
    }
  }
}
```

## Alternative: Using Module Format

If the above doesn't work, try using the module format:

```json
{
  "mcpServers": {
    "notion-mcp": {
      "command": "python",
      "args": ["-m", "server"],
      "cwd": "${workspaceFolder}/notion-mcp",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/notion-mcp",
        "PYTHONUNBUFFERED": "1",
        "NOTION_TOKEN": "your_notion_token_here"
      }
    }
  }
}
```

## Troubleshooting

1. **Make sure dependencies are installed:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Test server startup manually:**
   ```bash
   cd D:\Dev\repos\notion-mcp
   python server.py
   ```

3. **Check Python path:**
   - Ensure Python is in your PATH
   - Verify the correct Python version (3.11+)

4. **Verify NOTION_TOKEN:**
   - Set the NOTION_TOKEN environment variable
   - Or add it to the env section in Cursor config

5. **Check Cursor logs:**
   - Open Cursor Developer Tools (Help > Toggle Developer Tools)
   - Check Console for MCP server errors

## Notes

- The `cwd` parameter ensures the server runs from the correct directory
- `PYTHONPATH` must include the notion-mcp directory for imports to work
- `PYTHONUNBUFFERED=1` ensures real-time log output
