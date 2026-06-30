"""PyInstaller entrypoint for notion-mcp HTTP sidecar."""

from __future__ import annotations

import _strptime  # noqa: F401 -- PyInstaller must bundle this eagerly
import os
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    base = Path(sys._MEIPASS)
else:
    base = Path(__file__).resolve().parent
if str(base) not in sys.path:
    sys.path.insert(0, str(base))

os.environ.setdefault("MCP_TRANSPORT", "http")

if __name__ == "__main__":
    from notion_mcp.server import app

    host = os.environ.get("NOTION_HOST", "127.0.0.1")
    port = int(os.environ.get("NOTION_PORT", os.environ.get("MCP_PORT", "10811")))
    log_level = os.environ.get("NOTION_LOG_LEVEL", "info")
    uvicorn.run(app, host=host, port=port, log_level=log_level)
