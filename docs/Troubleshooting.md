# NotionMCP Troubleshooting Guide

**Austrian efficiency diagnostics and problem solving**

## 🚨 Quick Diagnosis (30 seconds)

Run this command for instant health check:

```powershell
python -c "
import os, asyncio
from server import test_connection
if not os.getenv('NOTION_TOKEN'):
    print('❌ NOTION_TOKEN missing in .env')
else:
    try:
        result = asyncio.run(test_connection())
        print('✅ Connection successful' if result.get('connection', {}).get('success') else '❌ Connection failed')
    except Exception as e:
        print(f'❌ Error: {e}')
"
```

## 🔧 Common Issues & Fixes

### 1. Authentication Errors

**Error:** `"Notion API token is invalid or expired"`

**Austrian Direct Solutions:**

1. **Check token format:** Should start with `secret_`
2. **Regenerate token:** Go to notion.so/my-integrations
3. **Workspace access:** Add integration to workspace
4. **Environment loading:** Verify `.env` file location

```powershell
# Check if token is loaded
python -c "import os; print('Token found:', bool(os.getenv('NOTION_TOKEN')))"

# Test token format
python -c "
import os
token = os.getenv('NOTION_TOKEN', '')
print(f'Length: {len(token)}')
print(f'Starts with secret_: {token.startswith(\"secret_\")}')
"
```

### 2. Permission Denied Errors

**Error:** `"The requested page/database was not found"`

**Root Causes & Fixes:**

1. **Integration not connected:** Add to specific pages
2. **Wrong workspace:** Check integration workspace
3. **Invalid ID:** Verify page/database IDs

```powershell
# Test page access
python -c "
import asyncio, os
from notion.client import NotionClient

async def test_page(page_id):
    client = NotionClient(token=os.getenv('NOTION_TOKEN'))
    try:
        page = await client.get_page(page_id)
        print('✅ Page accessible')
    except Exception as e:
        print(f'❌ Page error: {e}')

# Replace with your page ID
asyncio.run(test_page('your-page-id-here'))
"
```

### 3. Rate Limiting Issues

**Error:** `"Rate limit exceeded"`

**Austrian Efficiency Solutions:**

1. **Enable caching:** `ENABLE_CACHING=true`
2. **Reduce batch size:** `MAX_RESULTS_PER_PAGE=50`
3. **Add delays:** Wait 60 seconds between requests
4. **Monitor usage:** Track daily API calls

```powershell
# Check current usage
python -c "
import asyncio
from server import notion_client

async def check_stats():
    stats = await notion_client.get_stats()
    print(f'Requests today: {stats[\"total_requests\"]}')
    print(f'Error rate: {stats[\"total_errors\"]}/{stats[\"total_requests\"]}')

asyncio.run(check_stats())
"
```

### 4. Character Encoding Problems

**Issue:** German/Japanese characters display incorrectly

**Fixes:**

1. **Set encoding:** `LANGUAGE=de` or `LANGUAGE=ja`
2. **Terminal UTF-8:** `chcp 65001` in PowerShell
3. **File encoding:** Save files as UTF-8

```powershell
# Test character support
python -c "
print('German: ä ö ü ß')
print('Japanese: 日本語')
print('Austrian: Österreich 🇦🇹')
"
```

### 5. Import/Dependency Issues

**Error:** `"ModuleNotFoundError: No module named 'fastmcp'"`

**Solutions:**

1. **Install dependencies:** `pip install -r requirements.txt`
2. **Virtual environment:** Create isolated environment
3. **Python version:** Ensure Python 3.8+

```powershell
# Check Python version
python --version

# Check installed packages
pip list | findstr "fastmcp\|notion-client\|pydantic"

# Reinstall if needed
pip install --upgrade -r requirements.txt
```

### 6. Claude Desktop Integration Issues

**Problem:** NotionMCP not appearing in Claude

**Debugging Steps:**

1. **Check config syntax:** Valid JSON format
2. **Restart Claude:** Complete restart required
3. **Path verification:** Correct server.py path
4. **Log checking:** Check Claude Desktop logs

```json
// Correct MCP configuration
{
  "mcpServers": {
    "notionmcp": {
      "command": "python",
      "args": ["D:\\Dev\\repos\\notionmcp\\server.py"],
      "env": {
        "NOTION_TOKEN": "secret_your_token_here"
      }
    }
  }
}
```

### 7. Database Schema Errors

**Error:** `"Property 'X' not found in database schema"`

**Solutions:**

1. **Check property names:** Case-sensitive matching
2. **Update schema:** Use `get_database_schema` tool
3. **Property types:** Verify correct types

```powershell
# Check database schema
python -c "
import asyncio
from server import db_manager

async def check_schema(db_id):
    schema = await db_manager.get_database_schema(db_id)
    print('Properties:', list(schema['properties'].keys()))

# Replace with your database ID
asyncio.run(check_schema('your-database-id'))
"
```

## 🇦🇹 Austrian Efficiency Diagnostics

### Performance Check

```powershell
# Complete system check
python -c "
import asyncio, os, time
from server import notion_client

async def full_check():
    print('🇦🇹 NotionMCP Diagnostic Report')
    print('=' * 40)
    
    # 1. Environment check
    print(f'Token present: {bool(os.getenv(\"NOTION_TOKEN\"))}')
    print(f'Timezone: {os.getenv(\"TIMEZONE\", \"Not set\")}')
    print(f'Language: {os.getenv(\"LANGUAGE\", \"Not set\")}')
    
    # 2. Connection test
    start = time.time()
    try:
        result = await notion_client.test_connection()
        print(f'Connection: ✅ ({time.time()-start:.2f}s)')
        print(f'User: {result.get(\"user\", {}).get(\"name\", \"Unknown\")}')
    except Exception as e:
        print(f'Connection: ❌ {e}')
    
    # 3. Performance stats
    stats = await notion_client.get_stats()
    print(f'API requests: {stats[\"total_requests\"]}')
    print(f'Success rate: {stats[\"success_rate\"]:.1f}%')
    
    print('=' * 40)
    print('✅ Diagnostic complete')

asyncio.run(full_check())
"
```

### Budget Monitoring

```powershell
# Check API usage costs
python -c "
import asyncio
from server import notion_client

async def budget_check():
    stats = await notion_client.get_stats()
    requests = stats['total_requests']
    
    # Estimate costs (rough calculation)
    estimated_cost = requests * 0.001  # €0.001 per request estimate
    monthly_budget = 100  # €100/month
    
    print(f'📊 Budget Analysis')
    print(f'Requests today: {requests}')
    print(f'Estimated cost: €{estimated_cost:.2f}')
    print(f'Monthly budget: €{monthly_budget}')
    print(f'Budget usage: {(estimated_cost/monthly_budget)*100:.1f}%')
    
    if estimated_cost > monthly_budget * 0.8:
        print('⚠️  Approaching budget limit!')
    else:
        print('✅ Budget healthy')

asyncio.run(budget_check())
"
```

## 🔍 Debug Mode

Enable detailed logging for troubleshooting:

```bash
# In .env file
DEBUG_MODE=true
LOG_LEVEL=DEBUG
LOG_API_CALLS=true
```

```powershell
# Run with verbose logging
python server.py --debug
```

## 📞 Getting Help

### 1. Check Logs

- **Server logs:** Look for error messages in console
- **Claude Desktop logs:** Check application logs
- **System logs:** Windows Event Viewer if needed

### 2. Minimal Test Case

Create simple test to isolate issue:

```python
# minimal_test.py
import asyncio
import os
from notion.client import NotionClient

async def minimal_test():
    client = NotionClient(token=os.getenv('NOTION_TOKEN'))
    result = await client.test_connection()
    print(result)

if __name__ == "__main__":
    asyncio.run(minimal_test())
```

### 3. Environment Information

Gather system info:

```powershell
# System information
python --version
pip --version
echo $env:NOTION_TOKEN.Substring(0,10)  # First 10 chars only
Get-Location
```

### 4. Austrian Direct Communication

When reporting issues:

- **Be specific:** Exact error message
- **Be honest:** What you were trying to do
- **Be efficient:** Include relevant logs only
- **No gaslighting:** Don't blame yourself if API fails

## 🛠️ Advanced Troubleshooting

### Network Issues

```powershell
# Test Notion API connectivity
curl -H "Authorization: Bearer %NOTION_TOKEN%" https://api.notion.com/v1/users/me
```

### Database Connectivity

```powershell
# Test specific database access
python -c "
import asyncio
from server import db_manager

async def test_db(db_id):
    try:
        schema = await db_manager.get_database_schema(db_id)
        print('✅ Database accessible')
        print('Properties:', list(schema['properties'].keys()))
    except Exception as e:
        print(f'❌ Database error: {e}')

asyncio.run(test_db('your-database-id'))
"
```

### Memory Usage

```powershell
# Check memory usage
python -c "
import psutil
import os

process = psutil.Process(os.getpid())
memory = process.memory_info().rss / 1024 / 1024
print(f'Memory usage: {memory:.1f} MB')
"
```

## ✅ Prevention Tips

1. **Regular testing:** Run health checks weekly
2. **Token rotation:** Update tokens quarterly
3. **Backup configs:** Keep working configurations
4. **Monitor usage:** Track API calls daily
5. **Update dependencies:** Keep packages current

## 🇦🇹 Austrian Efficiency Summary

**Most common issues (80% of problems):**

1. **Missing token:** Check `.env` file
2. **Integration not added:** Connect to workspace
3. **Wrong page ID:** Verify IDs are correct
4. **Rate limiting:** Enable caching, reduce requests

**Quick fixes that solve 90% of issues:**

1. Restart Claude Desktop
2. Regenerate Notion token
3. Check workspace permissions
4. Verify environment variables

---

**Austrian Efficiency: Fix problems directly, no dancing around issues! 🇦🇹**

*Practical troubleshooting without euphemisms or gaslighting.*
