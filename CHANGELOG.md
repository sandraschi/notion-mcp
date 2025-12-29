# Changelog

All notable changes to Notion MCP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-12-29

### Fixed
- **Cursor Compatibility**: Fixed server startup issue in Cursor by implementing lazy initialization of Notion client
  - Server can now start even if `NOTION_TOKEN` isn't set (tools will return appropriate errors)
  - Prevents import-time failures that blocked Cursor from starting the server
  - Updated `glama.json` to use direct `server.py` execution

### Changed
- Improved error handling for missing `NOTION_TOKEN` with clearer error messages
- Tools now initialize Notion client on-demand instead of at import time

## [1.0.0] - 2025-12-29

### Added
- **FastMCP 2.14.1 Upgrade**: Complete migration to FastMCP 2.14.1
  - Server lifespan context manager for startup/shutdown lifecycle
  - Comprehensive `instructions` parameter for AI guidance
  - Async `run_stdio_async()` implementation
  - Synchronous `run()` function for compatibility

- **Structured Logging**: Replaced standard logging with `structlog`
  - JSON logging output to stderr only (MCP protocol uses stdout)
  - Structured logging with context for all operations
  - Better debugging and monitoring capabilities

- **Test Harness**: Enhanced testing infrastructure
  - Created `pytest.ini` with async support and test markers
  - Enhanced `Makefile` with test commands (test, test-unit, test-integration, test-coverage)
  - Test markers: unit, integration, slow, requires_notion, requires_token

- **Code Quality**: Improved code standards
  - All ruff linting issues resolved
  - Updated Makefile to use ruff instead of black/isort
  - Fixed unused variables and bare except clauses

- **Glama Configuration**: Updated `glama.json` with proper MCP server structure
  - Complete metadata (version, author, tags, categories)
  - Proper capabilities configuration
  - Timeout settings (initialize: 30000ms, message: 60000ms)

- **Documentation**: Comprehensive documentation updates
  - Updated README.md with FastMCP 2.14.1 references
  - Created UPGRADE_SUMMARY.md documenting all changes
  - Created CURSOR_FIX.md and CURSOR_MCP_CONFIG.md for Cursor setup
  - Added Beta status note

### Changed
- Updated `pyproject.toml` entry point from `app.run` to `run` for compatibility
- All tools use docstring-based documentation (FastMCP 2.12+ standard)
- Error handling uses structured logging with context

### Fixed
- Fixed unused variables in `notion/client.py`, `notion/databases.py`, `notion/pages.py`
- Fixed bare except clauses to use `Exception` explicitly
- Fixed unused mock variables in test files

## [Unreleased]

### Planned
- MCPB packaging support
- Enhanced test coverage
- Additional Notion API features

---

## Version History

- **1.0.1** (2025-12-29): Cursor compatibility fix with lazy initialization
- **1.0.0** (2025-12-29): FastMCP 2.14.1 upgrade with structured logging and test harness
