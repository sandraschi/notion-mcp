# NotionMCP Configuration Guide

**5-minute setup with Austrian efficiency for Vienna workflows**

## 🚀 Quick Start (5 Minutes)

### Step 1: Prerequisites (1 minute)

- **Python 3.8+** installed
- **Notion account** with workspace access
- **Claude Desktop Pro** with MCP support
- **Terminal/PowerShell** access

### Step 2: Installation (2 minutes)

```powershell
# Clone the repository
git clone <repository-url>
cd notionmcp

# Install dependencies (Austrian efficiency)
pip install -r requirements.txt
```

### Step 3: Notion Integration Setup (2 minutes)

1. **Create Notion Integration:**
   - Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
   - Click "New integration"
   - Name: "NotionMCP"
   - Select workspace
   - Copy the token

2. **Set up environment:**

   ```powershell
   # Copy environment template
   Copy-Item .env.example .env
   
   # Edit .env file and add your token
   # NOTION_TOKEN=secret_your_token_here
   ```

3. **Add integration to workspace:**
   - Go to any Notion page
   - Click "..." → "Add connections"
   - Select "NotionMCP"

### Step 4: Test Connection (30 seconds)

```powershell
# Start the server
python server.py

# Should see: "Austrian efficiency activated! 🇦🇹"
```

✅ **Done!** Ready for Vienna workflows.

## 🔧 Environment Configuration

### Required Settings

```bash
# Your Notion integration token (REQUIRED)
NOTION_TOKEN=secret_your_token_here

# API version (recommended)
NOTION_VERSION=2022-06-28
```

### Austrian Context (Optional)

```bash
# Vienna timezone for proper date handling
TIMEZONE=Europe/Vienna

# Austrian date format (DD.MM.YYYY)
DATE_FORMAT=DD.MM.YYYY

# Language preference (German/English)
LANGUAGE=de

# Currency for budget tracking
CURRENCY=EUR

# Monthly budget consideration (~€100/month)
MONTHLY_BUDGET_EUR=100
```

### Performance Settings

```bash
# Request timeout (Austrian efficiency)
NOTION_TIMEOUT=30

# Maximum results per page (budget awareness)
MAX_RESULTS_PER_PAGE=100

# Enable caching for better performance
ENABLE_CACHING=true
CACHE_DURATION=300

# Maximum concurrent requests
MAX_CONCURRENT_REQUESTS=5
```

### Feature Flags

```bash
# Enable AI features (when available)
ENABLE_AI_FEATURES=true

# Enable webhook support
ENABLE_WEBHOOKS=true

# Enable bulk operations
ENABLE_BULK_OPERATIONS=true

# Enable Japanese character support (weeb features)
ENABLE_JAPANESE_SUPPORT=true

# Enable academic templates
ENABLE_ACADEMIC_MODE=true
```

## 🎯 Use Case Configurations

### Academic Research Setup

```bash
ENABLE_ACADEMIC_MODE=true
DEFAULT_CITATION_FORMAT=APA
ENABLE_BIBLIOGRAPHY=true
LANGUAGE=en
```

### Anime/Weeb Organization 🎌

```bash
ENABLE_JAPANESE_SUPPORT=true
ENABLE_ANIME_TEMPLATES=true
ENABLE_LANGUAGE_LEARNING=true
```

### Vienna Business/Project Management 🇦🇹

```bash
TIMEZONE=Europe/Vienna
DATE_FORMAT=DD.MM.YYYY
LANGUAGE=de
CURRENCY=EUR
```

## 🔗 Claude Desktop Integration

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "notionmcp": {
      "command": "python",
      "args": ["D:\\Dev\\repos\\notionmcp\\server.py"],
      "env": {
        "NOTION_TOKEN": "your_token_here",
        "TIMEZONE": "Europe/Vienna"
      }
    }
  }
}
```

**Important:** Restart Claude Desktop after configuration changes.

## 🧪 Testing Configuration

### Basic Connection Test

```python
# Quick test
python -c "
import asyncio
import os
from notion.client import NotionClient

async def test():
    client = NotionClient(token=os.getenv('NOTION_TOKEN'))
    result = await client.test_connection()
    print(f'✅ Success: {result[\"success\"]}')
    print(f'🇦🇹 Vienna time: {result.get(\"current_time\")}')

asyncio.run(test())
"
```

## 🚨 Common Issues & Solutions

### Authentication Problems

**Issue:** `"Notion API token is invalid"`

**Solutions:**

1. Check token in `.env` file
2. Regenerate token in Notion integrations
3. Ensure integration is added to workspace

### Permission Errors

**Issue:** `"Page/database not found"`

**Solutions:**

1. Add integration to specific pages/databases
2. Check workspace access
3. Use correct IDs

### Character Encoding

**Issue:** German/Japanese characters broken

**Solutions:**

1. Set correct `LANGUAGE` in `.env`
2. Ensure UTF-8 encoding
3. Check terminal settings

## 🇦🇹 Austrian Efficiency Tips

1. **Minimal config:** Only set what you need
2. **Smart defaults:** Optimized for Vienna workflows
3. **Budget awareness:** Monitor API usage
4. **Academic focus:** Enable research templates
5. **Weeb support:** Japanese character handling

## 📋 Configuration Checklist

- [ ] Python 3.8+ installed
- [ ] Notion integration created
- [ ] Token added to `.env` file
- [ ] Integration added to workspace
- [ ] Claude Desktop configured
- [ ] Connection test successful
- [ ] Austrian efficiency activated! 🇦🇹

---

**Austrian Efficiency: Configure once, work efficiently forever!**  
*Quick setup optimized for Vienna workflows, academic research, and weeb organization.*
