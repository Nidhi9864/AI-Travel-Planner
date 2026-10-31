import { defineConfig, devices } from "@playwright/test";

// BASE_URL runs the specs against a deployment (make e2e BASE_URL=...); otherwise the dev server.
const baseURL = process.env.BASE_URL ?? "http://localhost:3000";

// The widths of US-122 and §7.9: phone, tablet, laptop and wide desktop.
const WIDTHS = [360, 768, 1280, 1920] as const;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [["list"], ["html", { open: "never" }]] : "list",
  use: {
    baseURL,
    trace: "on-first-retry",
  },
  projects: WIDTHS.map((width) => ({
    name: `chromium-${width}`,
    use: {
      ...devices["Desktop Chrome"],
      viewport: { width, height: width < 768 ? 800 : 900 },
    },
  })),
  webServer: process.env.BASE_URL
    ? undefined
    : {
        command: "npm run dev",
        url: baseURL,
        reuseExistingServer: !process.env.CI,
        timeout: 120_000,
      },
});
