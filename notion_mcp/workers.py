"""
NotionMCP - Notion Workers Management via ntn CLI
Austrian Efficiency Implementation for Worker Deployment and Management
"""

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any

logger = logging.getLogger("notionmcp.workers")


def _ntn_binary() -> str:
    """Return the path to the ntn CLI binary."""
    return os.getenv("NTN_BIN", "ntn")


def _run_ntn(args: list[str], timeout: int = 60) -> dict:
    """Run an ntn CLI command and return parsed result."""
    try:
        result = subprocess.run(
            [_ntn_binary(), *args],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip()
            return {"success": False, "error": stderr or "ntn command failed"}
        output = result.stdout.strip()
        # Try parsing JSON output
        try:
            data = json.loads(output)
            return {"success": True, "data": data}
        except json.JSONDecodeError:
            return {"success": True, "output": output}
    except FileNotFoundError:
        return {
            "success": False,
            "error": ("ntn CLI not found. Install it: curl -fsSL https://ntn.dev | bash"),
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"ntn command timed out after {timeout}s"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def deploy_worker(project_dir: str | None = None) -> dict[str, Any]:
    """
    Deploy a Notion Worker from a local project directory.
    Runs `ntn workers deploy` in the specified directory.
    """
    cwd = project_dir or os.getcwd()
    result = _run_ntn(["workers", "deploy"], timeout=120)
    if result.get("success"):
        logger.info(f"Worker deployed from {cwd}")
    else:
        logger.error(f"Worker deploy failed from {cwd}: {result.get('error')}")
    return result


async def list_workers() -> dict[str, Any]:
    """List deployed Notion Workers."""
    return _run_ntn(["workers", "list"])


async def scaffold_worker(project_dir: str) -> dict[str, Any]:
    """
    Scaffold a new Notion Worker project.
    Runs `ntn workers new` in the specified directory.
    """
    path = Path(project_dir)
    path.mkdir(parents=True, exist_ok=True)
    result = _run_ntn(["workers", "new"], timeout=60)
    if result.get("success"):
        logger.info(f"Worker scaffolded at {project_dir}")
    return result


async def worker_logs(worker_name: str | None = None, tail: int = 50) -> dict[str, Any]:
    """Fetch logs for a deployed Worker."""
    args = ["workers", "logs"]
    if worker_name:
        args.extend(["--name", worker_name])
    args.extend(["--tail", str(tail)])
    return _run_ntn(args)


async def check_ntn_version() -> dict[str, Any]:
    """Check if ntn CLI is installed and return its version."""
    try:
        result = subprocess.run(
            [_ntn_binary(), "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return {"success": True, "version": result.stdout.strip()}
        return {"success": False, "error": result.stderr.strip()}
    except FileNotFoundError:
        return {
            "success": False,
            "error": "ntn CLI not found. Install: curl -fsSL https://ntn.dev | bash",
        }
