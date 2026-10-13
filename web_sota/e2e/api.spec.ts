import { expect, test } from "@playwright/test";

// Backend contract: the endpoints the dashboard depends on.
test("health reports ok", async ({ request }) => {
  const res = await request.get("http://127.0.0.1:10811/api/health");
  expect(res.ok()).toBeTruthy();
  const body = await res.json();
  expect(body.status).toBe("ok");
});

test("capabilities list 41 tools", async ({ request }) => {
  const res = await request.get("http://127.0.0.1:10811/api/capabilities");
  expect(res.ok()).toBeTruthy();
  const body = await res.json();
  expect(body.server).toBe("notion-mcp");
  expect(body.tool_count).toBe(41);
  expect(body.tools).toContain("search_notion_knowledge");
});

test("skills endpoint returns registry", async ({ request }) => {
  const res = await request.get("http://127.0.0.1:10811/api/skills");
  expect(res.ok()).toBeTruthy();
  const body = await res.json();
  expect(Array.isArray(body.skills)).toBeTruthy();
});

test("llm onboarding reports token need", async ({ request }) => {
  const res = await request.get("http://127.0.0.1:10811/api/llm/onboarding");
  expect(res.ok()).toBeTruthy();
  const body = await res.json();
  expect(typeof body.needs_token).toBe("boolean");
});
