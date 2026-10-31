import path from "node:path";

import type { Page, TestInfo } from "@playwright/test";

import { expect, test, type TestUsers } from "./fixtures/users";

// TC-278 (US-122 AC1-AC2, FR-114): no horizontal scroll and no clipped control at each project width.
// /dashboard is behind AuthGuard (IMP-109), so its check signs in a confirmed local test user first
// (e2e/fixtures/users.ts; needs the local stack's keys in the environment). The / check needs none.

// UPDATE_SCREENSHOTS=1 refreshes the evidence screenshots of the IMP-104 part record.
const SCREENSHOT_DIR = path.resolve(__dirname, "../../../docs/progress/parts");
const SCREENSHOT_WIDTHS = [360, 1280];

async function expectFitsViewport(
  page: Page,
  pagePath: string,
  heading: RegExp,
  testInfo: TestInfo,
) {
  await page.goto(pagePath);
  await expect(
    page.getByRole("heading", { level: 1, name: heading }),
  ).toBeVisible();

  const { scrollWidth, innerWidth } = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    innerWidth: window.innerWidth,
  }));
  expect(scrollWidth).toBeLessThanOrEqual(innerWidth);

  // A control is clipped when it extends past the viewport or its own content overflows it.
  const clipped = await page.evaluate(() => {
    const controls = document.querySelectorAll<HTMLElement>(
      "a, button, input, [role='button']",
    );
    return Array.from(controls)
      .filter((el) => el.getClientRects().length > 0 && !el.closest(".sr-only"))
      .filter((el) => {
        const box = el.getBoundingClientRect();
        const outside = box.left < 0 || box.right > window.innerWidth + 0.5;
        const overflowing =
          el.clientWidth > 0 && el.scrollWidth > el.clientWidth + 1;
        return outside || overflowing;
      })
      .map(
        (el) =>
          el.textContent?.trim() || el.getAttribute("aria-label") || el.tagName,
      );
  });
  expect(clipped).toEqual([]);

  const width = page.viewportSize()?.width ?? 0;
  if (
    process.env.UPDATE_SCREENSHOTS === "1" &&
    pagePath === "/" &&
    SCREENSHOT_WIDTHS.includes(width)
  ) {
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, `IMP-104-whole-task-${width}.png`),
      fullPage: true,
    });
    testInfo.annotations.push({
      type: "screenshot",
      description: `IMP-104-whole-task-${width}.png`,
    });
  }
}

async function signInAsNewUser(page: Page, users: TestUsers) {
  const user = await users.create("smoke");
  await page.goto("/sign-in?next=%2Fdashboard");
  await page.getByLabel("Email").fill(user.email);
  await page.getByLabel("Password", { exact: true }).fill(user.password);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
}

test("smoke: / fits the viewport without horizontal scroll", async ({
  page,
}, testInfo) => {
  await expectFitsViewport(page, "/", /day-by-day plan/i, testInfo);
});

test("smoke: /dashboard fits the viewport without horizontal scroll", async ({
  page,
  users,
}, testInfo) => {
  await signInAsNewUser(page, users);
  await expectFitsViewport(page, "/dashboard", /your trips/i, testInfo);
});

test("smoke: a signed-out visit to /dashboard lands on /sign-in", async ({
  page,
}) => {
  await page.goto("/dashboard");
  await expect(page).toHaveURL(/\/sign-in\?next=%2Fdashboard$/);
  await expect(
    page.getByRole("heading", { level: 1, name: "Sign in" }),
  ).toBeVisible();
});
