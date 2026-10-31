import path from "node:path";

import { expect, test } from "@playwright/test";

// TC-278 (US-122 AC1-AC2, FR-114): no horizontal scroll and no clipped control at each project width.
const PAGES = [
  { path: "/", heading: /day-by-day plan/i },
  { path: "/dashboard", heading: /your trips/i },
] as const;

// UPDATE_SCREENSHOTS=1 refreshes the evidence screenshots of the IMP-104 part record.
const SCREENSHOT_DIR = path.resolve(__dirname, "../../../docs/progress/parts");
const SCREENSHOT_WIDTHS = [360, 1280];

for (const { path: pagePath, heading } of PAGES) {
  test(`smoke: ${pagePath} fits the viewport without horizontal scroll`, async ({
    page,
  }, testInfo) => {
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
        .filter(
          (el) => el.getClientRects().length > 0 && !el.closest(".sr-only"),
        )
        .filter((el) => {
          const box = el.getBoundingClientRect();
          const outside = box.left < 0 || box.right > window.innerWidth + 0.5;
          const overflowing =
            el.clientWidth > 0 && el.scrollWidth > el.clientWidth + 1;
          return outside || overflowing;
        })
        .map(
          (el) =>
            el.textContent?.trim() ||
            el.getAttribute("aria-label") ||
            el.tagName,
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
  });
}
