import { defineConfig, devices } from "@playwright/test";

// Serves BOTH backend (FastAPI :10811) and frontend (Vite :10810):
// specs navigate the SPA, so a backend-only webServer would fail.
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  retries: 0,
  reporter: "list",
  use: {
    baseURL: "http://127.0.0.1:10810",
    trace: "retain-on-failure",
  },
  webServer: [
    {
      command: "uv run python server.py --http --port 10811",
      cwd: "..",
      url: "http://127.0.0.1:10811/api/health",
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000,
    },
    {
      command: "npm run dev -- --port 10810 --host 127.0.0.1",
      url: "http://127.0.0.1:10810",
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000,
    },
  ],
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
