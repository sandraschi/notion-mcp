# Fix for Notion MCP Not Starting in Cursor

## Issue
The server was trying to initialize the Notion client at import time, which could prevent Cursor from starting it if dependencies weren't installed or NOTION_TOKEN wasn't set.

## Solution Applied

1. **Lazy Initialization**: Changed Notion client initialization to happen lazily when tools are called, not at import time
2. **Updated glama.json**: Changed command args to use `server.py` directly
3. **Better Error Handling**: Tools now initialize the client and return clear error messages if NOTION_TOKEN is missing

## Cursor Configuration

Add this to your Cursor MCP settings (Cursor Settings > MCP Servers):

```json
{
  "mcpServers": {
    "notion-mcp": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "D:\\Dev\\repos\\notion-mcp",
      "env": {
        "PYTHONPATH": "D:\\Dev\\repos\\notion-mcp",
        "PYTHONUNBUFFERED": "1",
        "NOTION_TOKEN": "your_notion_token_here"
      }
    }
  }
}
```

## Testing

1. **Test server startup:**
   ```bash
   cd D:\Dev\repos\notion-mcp
   python server.py
   ```
   The server should start without errors (it will wait for MCP protocol on stdin)

2. **Test in Cursor:**
   - Open Cursor Settings
   - Go to MCP Servers
   - Add the configuration above
   - Restart Cursor
   - Check MCP server status in Cursor

## Troubleshooting

If the server still doesn't start:

1. **Check Python path:**
   - Ensure Python 3.11+ is in your PATH
   - Verify: `python --version`

2. **Check dependencies:**
   ```bash
   cd D:\Dev\repos\notion-mcp
   pip install -r requirements.txt
   ```

3. **Check NOTION_TOKEN:**
   - Set the environment variable in Cursor config
   - Or set it in your system environment variables

4. **Check Cursor logs:**
   - Open Cursor Developer Tools (Help > Toggle Developer Tools)
   - Check Console for MCP server errors

5. **Verify server.py location:**
   - Make sure `server.py` is in `D:\Dev\repos\notion-mcp\`
   - The `cwd` in Cursor config should point to this directory

## Changes Made

- ✅ Lazy initialization of Notion client (no import-time failures)
- ✅ Updated glama.json command format
- ✅ Better error messages for missing NOTION_TOKEN
- ✅ Server can start even if token isn't set (tools will return errors)
