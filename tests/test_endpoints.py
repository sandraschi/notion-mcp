"""Endpoint tests for the Phase 2/3 REST surface.

No Notion token required: health/capabilities/skills/LLM-discovery paths
work unauthenticated; LLM chat paths exercise the declared fallback.
`POST /api/shutdown` and the `shutdown_server` tool are deliberately NEVER
tested here (they terminate the test process).
"""

from fastapi.testclient import TestClient

import server

client = TestClient(server.app, raise_server_exceptions=False)


class TestHealth:
    def test_root_health_alias(self):
        r = client.get("/health")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ok"
        assert body["server"] == "notion-mcp"
        assert isinstance(body["uptime_seconds"], int)

    def test_api_health(self):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


class TestCapabilities:
    def test_tool_count(self):
        r = client.get("/api/capabilities")
        assert r.status_code == 200
        body = r.json()
        assert body["tool_count"] == 41
        assert "search_notion_knowledge" in body["tools"]
        assert "server_help" in body["tools"]
        assert "shutdown_server" in body["tools"]

    def test_diagnostics(self):
        r = client.get("/api/v1/diagnostics")
        assert r.status_code == 200
        assert r.json()["tool_count"] == 41


class TestSkills:
    def test_registry(self):
        r = client.get("/api/skills")
        assert r.status_code == 200
        names = [s["name"] for s in r.json()["skills"]]
        assert "notion-expert" in names


class TestLlm:
    def test_onboarding_shape(self):
        r = client.get("/api/llm/onboarding")
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body["needs_token"], bool)
        assert len(body["steps"]) >= 1

    def test_models_shape(self):
        r = client.get("/api/llm/models", params={"provider": "ollama"})
        assert r.status_code == 200
        body = r.json()
        assert body["provider"] == "ollama"
        assert isinstance(body["models"], list)
        assert isinstance(body["live"], bool)

    def test_chat_declared_fallback(self):
        r = client.post("/api/llm/chat", json={"messages": [{"role": "user", "content": "hi"}]})
        assert r.status_code == 200
        body = r.json()
        assert body["declared_fallback"] is True
        assert isinstance(body["reply"], str)

    def test_chat_stream_contract(self):
        r = client.post("/api/llm/chat/stream", json={"messages": [{"role": "user", "content": "hi"}]})
        assert r.status_code == 200
        assert "text/event-stream" in r.headers["content-type"]
        assert r.text.strip().endswith("data: [DONE]")
        assert "declared_fallback" in r.text


class TestDocs:
    def test_bundled_doc(self):
        r = client.get("/api/docs/API")
        assert r.status_code == 200
        assert len(r.json()["content"]) > 100
