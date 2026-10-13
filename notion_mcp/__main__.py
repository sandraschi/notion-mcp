"""Stdio entry point: `python -m notion_mcp` (Claude Desktop).

Transport defaults to stdio (see notion_mcp.transport); pass `--http --port N`
for HTTP mode (web dashboard backend).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import run

if __name__ == "__main__":
    run()
