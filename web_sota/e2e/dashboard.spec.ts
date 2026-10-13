import { expect, test } from "@playwright/test";

// Dashboard smoke: hero renders, sidebar nav walks every primary page.
// Title/testid matching (fleet CUA pattern) - no coordinate clicks.
test("dashboard hero and onboarding cue", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByTestId("dashboard")).toBeVisible({ timeout: 30000 });
  await expect(page.getByTestId("dashboard-hero")).toBeVisible();
  await expect(page.getByText("notion-mcp").first()).toBeVisible();
});

test("sidebar nav walk", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByTestId("dashboard")).toBeVisible({ timeout: 30000 });
  const routes: [string, string][] = [
    ["/explorer", "explorer-page"],
    ["/search", "search-page"],
    ["/chat", "chat-page"],
    ["/tools", "tools-page"],
    ["/skills", "skills-page"],
    ["/status", "status-page"],
    ["/settings", "settings-page"],
    ["/logging", "logging-page"],
    ["/help", "help-page"],
    ["/data", "data-page"],
    ["/plugins", "plugins-page"],
  ];
  for (const [route, testid] of routes) {
    await page.goto(route);
    await expect(page.getByTestId(testid)).toBeVisible({ timeout: 15000 });
  }
});

test("tools page lists backend registry", async ({ page }) => {
  await page.goto("/tools");
  await expect(page.getByTestId("tools-page")).toBeVisible({ timeout: 30000 });
  await expect(page.getByText("search_notion_knowledge").first()).toBeVisible({
    timeout: 15000,
  });
});
