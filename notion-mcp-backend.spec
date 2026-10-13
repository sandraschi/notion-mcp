# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for notion-mcp backend sidecar."""

from PyInstaller.utils.hooks import copy_metadata

pkg_name = "notion_mcp"

datas = [("notion_mcp", "notion_mcp")]
for pkg in (
    "fastmcp",
    "fastapi",
    "uvicorn",
    "pydantic",
    "starlette",
    "httpx",
):
    datas += copy_metadata(pkg)

hiddenimports = [
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.asyncio",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.httptools_impl",
    "uvicorn.protocols.http.h11_impl",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    "notion_mcp",
    "notion_mcp.__main__",
    "notion_mcp.client",
    "notion_mcp.pages",
    "notion_mcp.databases",
    "notion_mcp.collaboration",
    "notion_mcp.automations",
    "notion_mcp.workers",
    "notion_mcp.plugins",
    "notion_mcp.transport",
    "notion_mcp.ai",
    "notion_mcp.auth",
    "notion_mcp.web",
    "notion_mcp.rag",
    "notion_mcp.rag.orchestrator",
    "notion_mcp.rag.vector_db",
]

a = Analysis(
    ["run_server.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # NOTE (2026-10-13): "torch" was listed here and broke the frozen exe
    # (sentence_transformers imports it unconditionally). Only exclude GUI
    # toolkits that are provably unimported.
    # NOTE (2026-10-13): "torch" and "scipy" were listed here and broke the
    # frozen exe (sentence_transformers imports torch unconditionally;
    # sklearn, pulled by sentence_transformers.util.similarity, needs scipy).
    # Only exclude GUI toolkits that are provably unimported.
    excludes=["tkinter", "matplotlib", "pandas", "tensorflow"],
    noarchive=True,
    optimize=0,
)
# NOTE (2026-10-13): an earlier revision stripped ALL .dist-info except a
# _keep_dist allowlist. That broke the frozen exe three times over (opentelemetry
# entry_points -> StopIteration; lancedb/tqdm metadata -> PackageNotFoundError),
# because modern deps query importlib.metadata at import time. The allowlist is
# unmaintainable whack-a-mole (transformers alone can demand dozens). Keep ALL
# metadata: correctness beats a few MB of bundle size. The list below documents
# the known-sensitive packages for reviewers; it no longer gates anything.
_keep_dist = ['fastmcp-', 'mcp-', 'prefab-ui-', 'prefab_ui-', 'opentelemetry-', 'opentelemetry_', 'email-validator-', 'email_validator-', 'lancedb-', 'lancedb_']
def _dist_name(path):
    return str(path).replace('_', '-').lower()
# _saved intentionally unused now (kept for audit trail of the allowlist era).
_saved = [e for e in a.datas if isinstance(e, tuple) and any(k in _dist_name(e[0]) for k in _keep_dist) and '.dist-info' in str(e[0])]
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="notion-mcp-backend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
