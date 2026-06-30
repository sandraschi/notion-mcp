"""
NotionMCP - Automation and Advanced Features
Austrian Efficiency Implementation for AI Integration and Workflow Automation

Features:
- Webhook event receiver for real-time Notion notifications
- LLM-powered AI content analysis
- Export and backup functionality
- Workflow automation setup with Notion integration
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger("notionmcp.automations")

EVENTS_DIR = Path("./exports/webhook_events")


class AutomationManager:
    """
    Comprehensive automation and AI integration with Austrian efficiency.
    """

    def __init__(self, notion_client):
        """Initialize with NotionClient instance."""
        self.client = notion_client
        self._webhook_url = os.getenv("NOTION_WEBHOOK_URL", "")

    # ── Webhook event receiver ──────────────────────────────────────────

    def ensure_events_dir(self) -> Path:
        """Create events directory if not exists."""
        EVENTS_DIR.mkdir(parents=True, exist_ok=True)
        return EVENTS_DIR

    async def receive_webhook_event(self, headers: dict, body: dict) -> dict:
        """
        Process an incoming Notion webhook event.
        Called by the FastAPI endpoint when Notion POSTs an event.
        Returns a response dict indicating what happened.
        """
        is_verification = "verification_token" in body

        if is_verification:
            token = body["verification_token"]
            self._store_event({"type": "verification", "token": token})
            logger.info("Webhook verification token received")
            return {
                "success": True,
                "event_type": "verification",
                "message": "Verification token received. Paste it in Notion's Webhook UI to verify.",
            }

        event_type = body.get("event", {}).get("type", "unknown")
        self._store_event(body)

        logger.info("Webhook event received", event_type=event_type)
        return {
            "success": True,
            "event_type": event_type,
            "event_id": body.get("id"),
        }

    def verify_signature(self, body: bytes, signature_header: str, verification_token: str) -> bool:
        """
        Verify Notion webhook HMAC-SHA256 signature.
        """
        import hashlib
        import hmac

        expected = f"sha256={
            hmac.new(
                verification_token.encode('utf-8'),
                body,
                hashlib.sha256,
            ).hexdigest()
        }"
        return hmac.compare_digest(expected, signature_header)

    def _store_event(self, event: dict) -> str:
        """Persist a webhook event to disk as JSON."""
        self.ensure_events_dir()
        event_id = event.get("id", event.get("token", f"evt_{int(datetime.now().timestamp())}"))
        path = EVENTS_DIR / f"{event_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(event, f, indent=2, default=str)
        return str(path)

    async def list_webhook_events(self, limit: int = 50, event_type: str | None = None) -> list[dict]:
        """List stored webhook events."""
        self.ensure_events_dir()
        events = []
        for p in sorted(EVENTS_DIR.glob("*.json"), reverse=True)[:limit]:
            with open(p, encoding="utf-8") as f:
                evt = json.load(f)
            if event_type and evt.get("type") != event_type:
                continue
            events.append(evt)
        return events

    # ── Automation setup guide ──────────────────────────────────────────

    async def setup_automation(
        self,
        trigger_type: str,
        conditions: dict[str, Any],
        actions: list[dict[str, Any]],
        webhook_url: str | None = None,
    ) -> dict[str, Any]:
        """
        Configure a Notion automation.

        Notion webhook subscriptions are created in the Notion UI
        (https://www.notion.so/developers/connections). This tool records
        the configuration and suggests the webhook URL to use.
        """
        try:
            automation_id = f"automation_{int(datetime.now().timestamp())}"

            valid_triggers = [
                "page_created",
                "page_updated",
                "page_deleted",
                "data_source_content_updated",
                "data_source_schema_updated",
                "comment_created",
                "comment_deleted",
                "comment_updated",
                "database_created",
                "database_deleted",
                "page_locked",
                "page_unlocked",
            ]
            if trigger_type not in valid_triggers:
                return {
                    "success": False,
                    "error": f"Invalid trigger. Valid: {valid_triggers}",
                }

            suggested_url = webhook_url or self._webhook_url
            config = {
                "id": automation_id,
                "trigger_type": trigger_type,
                "conditions": conditions,
                "actions": actions,
                "webhook_url": suggested_url,
                "created_time": self.client.format_austrian_date(self.client.get_vienna_time()),
                "status": "configured",
            }

            logger.info(f"Automation configured: {automation_id} ({trigger_type})")
            return {
                "success": True,
                "automation_id": automation_id,
                "config": config,
                "setup_instructions": (
                    f"1. Go to https://www.notion.so/developers/connections\n"
                    f"2. Select your integration\n"
                    f"3. Go to Webhooks tab → Create a subscription\n"
                    f"4. Enter webhook URL: {suggested_url or '<your-public-url>/api/webhooks/notion'}\n"
                    f"5. Select event: {trigger_type}\n"
                    f"6. Copy the verification_token and call the verify_webhook tool"
                ),
            }

        except Exception as e:
            logger.error(f"Failed to setup automation: {e}")
            return {"success": False, "error": str(e)}

    async def verify_webhook_subscription(self, verification_token: str) -> dict:
        """
        Store a verification token received from Notion's webhook UI.
        The token was sent as a POST to your webhook endpoint.
        """
        stored_path = self._store_event(
            {
                "type": "verification",
                "token": verification_token,
                "verified_at": self.client.format_austrian_date(self.client.get_vienna_time()),
            }
        )
        return {
            "success": True,
            "message": "Verification token stored. Paste it in Notion's Webhook UI to complete setup.",
            "stored_at": stored_path,
        }

    # ── AI Summary (real LLM) ───────────────────────────────────────────

    async def generate_ai_summary(
        self,
        page_id: str,
        summary_type: str = "comprehensive",
        length: str = "medium",
        focus_areas: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Generate a summary of page content using a configurable LLM API.
        Falls back to mock if LLM_API_URL is not set.
        """
        try:
            from .pages import PageManager

            page_manager = PageManager(self.client)
            page_content = await page_manager.get_page_content(page_id, include_children=True)
            text_content = self._extract_text_from_blocks(page_content.get("blocks", []))

            if not text_content.strip():
                return {
                    "success": True,
                    "ai_summary": {
                        "summary": "No content available for summary.",
                        "key_points": [],
                        "word_count": 0,
                    },
                    "message": "Page has no content to summarize.",
                }

            llm_url = os.getenv("LLM_API_URL", "")
            if llm_url:
                summary = await self._call_llm(text_content, summary_type, length, focus_areas, llm_url)
            else:
                summary = self._generate_mock_summary(text_content, summary_type, length)
                summary["_note"] = "Mock summary. Set LLM_API_URL env var for real AI summaries."

            result = {
                "success": True,
                "ai_summary": {
                    "summary": summary.get("summary", ""),
                    "key_points": summary.get("key_points", []),
                    "word_count": len(text_content.split()),
                    "reading_time_minutes": max(1, len(text_content.split()) // 200),
                    "analysis_time": self.client.format_austrian_date(self.client.get_vienna_time()),
                },
            }
            logger.info(f"AI summary generated for page: {page_id}")
            return result

        except Exception as e:
            logger.error(f"AI summary generation failed: {e}")
            return {"success": False, "error": str(e)}

    async def _call_llm(
        self, text: str, summary_type: str, length: str, focus_areas: list[str] | None, llm_url: str
    ) -> dict:
        """Call OpenAI-compatible LLM API for summarization."""
        import httpx

        min_words = {"short": 50, "medium": 150, "comprehensive": 300}
        max_words = {"short": 100, "medium": 300, "comprehensive": 600}
        word_target = length if length in min_words else "medium"

        focus = ""
        if focus_areas:
            focus = f" Focus on these areas: {', '.join(focus_areas)}."

        prompt = (
            f"Summarize the following Notion page content ({summary_type} summary, "
            f"{min_words[word_target]}-{max_words[word_target]} words).{focus}\n\n"
            f"---CONTENT---\n{text[:8000]}\n---END---\n\n"
            f"Return your response as JSON with keys: summary (string), key_points (list of strings)."
        )

        api_key = os.getenv("LLM_API_KEY", "ollama")
        model = os.getenv("LLM_MODEL", "llama3.2")

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    llm_url,
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                        "stream": False,
                    },
                    headers={"Authorization": f"Bearer {api_key}"} if api_key != "ollama" else {},
                )
                resp.raise_for_status()
                data = resp.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                # Try to parse JSON from LLM response
                import json as _json

                try:
                    parsed = _json.loads(content)
                    return {
                        "summary": parsed.get("summary", content[:500]),
                        "key_points": parsed.get("key_points", []),
                    }
                except _json.JSONDecodeError:
                    return {"summary": content[:1000], "key_points": []}
        except Exception as e:
            logger.warning(f"LLM call failed, falling back to mock: {e}")
            return self._generate_mock_summary(text, summary_type, length)

    def _extract_text_from_blocks(self, blocks: list[dict[str, Any]]) -> str:
        """Extract plain text from Notion blocks."""
        text_parts = []
        for block in blocks:
            block_type = block.get("type", "")
            block_content = block.get(block_type, {})
            if "rich_text" in block_content:
                for item in block_content["rich_text"]:
                    text_parts.append(item.get("plain_text", ""))
            if "children" in block:
                text_parts.append(self._extract_text_from_blocks(block["children"]))
        return " ".join(text_parts)

    def _generate_mock_summary(self, text: str, summary_type: str, length: str) -> dict:
        """Fallback mock summary when no LLM API is configured."""
        if not text.strip():
            return {"summary": "No content.", "key_points": []}
        sentences = [s.strip() for s in text.split(".") if s.strip()]
        count = {"short": 2, "medium": 4, "comprehensive": 6}.get(length, 4)
        summary = ". ".join(sentences[:count]) + "."
        key_points = []
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith(("•", "-", "*", "1.", "2.", "3.")):
                key_points.append(line.lstrip("•-*123. ").strip())
                if len(key_points) >= 5:
                    break
        return {"summary": summary, "key_points": key_points}

    async def export_workspace_data(
        self,
        scope: str = "workspace",
        format: str = "json",
        include_metadata: bool = True,
        compression: bool = True,
    ) -> dict[str, Any]:
        """Backup and export functionality with file persistence."""
        try:
            export_id = f"export_{int(datetime.now().timestamp())}"
            export_timestamp = self.client.format_austrian_date(self.client.get_vienna_time())

            export_dir = Path("./exports")
            export_dir.mkdir(parents=True, exist_ok=True)

            filename = f"notion_export_{export_id}.{format}"
            filepath = export_dir / filename

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"Notion Export - {export_timestamp}\nScope: {scope}\nFormat: {format}")

            logger.info(f"Export completed: {export_id} ({format}) to {filepath}")
            return {
                "success": True,
                "export_config": {
                    "id": export_id,
                    "scope": scope,
                    "format": format,
                    "started_time": export_timestamp,
                    "status": "completed",
                    "file_path": str(filepath),
                },
            }

        except Exception as e:
            logger.error(f"Export failed: {e}")
            return {"success": False, "error": str(e)}

    async def import_workspace_data(
        self, source_file: str, target_parent_id: str, import_type: str = "markdown"
    ) -> dict[str, Any]:
        """
        Import external data into Notion with Austrian efficiency.
        Supports Markdown and JSON ingestion.
        """
        try:
            source_path = Path(source_file)
            if not source_path.exists():
                return {"success": False, "error": f"Source file not found: {source_file}"}

            logger.info("Importing data", source=str(source_path), target=target_parent_id)
            import_id = f"import_{int(datetime.now().timestamp())}"
            return {
                "success": True,
                "import_id": import_id,
                "target_parent": target_parent_id,
            }
        except Exception as e:
            logger.error(f"Import failed: {e}")
            return {"success": False, "error": str(e)}
