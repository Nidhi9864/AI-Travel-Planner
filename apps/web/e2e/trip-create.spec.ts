import path from "node:path";

import type { Page, TestInfo } from "@playwright/test";

import { expect, test } from "./fixtures/users";

// TC-068 (FR-007 AC1, E2E-02 wizard part): sign in, create a trip with preferences and a must-visit
// place in the SAMPLE destination, and land on the generate page. Needs the local stack, the API
// with AI_PROVIDER=MOCK and `make seed` (Sampleton).

// UPDATE_SCREENSHOTS=1 refreshes the four-step screenshots of the IMP-212 part record (360 and
// 1280 px only).
const SCREENS = path.resolve(
  __dirname,
  "../../../docs/progress/parts/IMP-212-screens",
);

async function snapshot(page: Page, info: TestInfo, step: string) {
  const width = page.viewportSize()?.width;
  if (!process.env.UPDATE_SCREENSHOTS || (width !== 360 && width !== 1280)) {
    return;
  }
  await page.screenshot({
    path: path.join(SCREENS, `${step}-${width}.png`),
    fullPage: true,
  });
  info.annotations.push({
    type: "screenshot",
    description: `${step}-${width}`,
  });
}

const stepHeading = (page: Page, name: string) =>
  page.getByRole("heading", { level: 2, name });

test("trip-create: a new trip is saved step by step and opens the generate page (TC-068)", async ({
  page,
  users,
}, info) => {
  const user = await users.create("trip");
  await page.goto("/sign-in?next=%2Ftrips%2Fnew");
  await page.getByLabel("Email").fill(user.email);
  await page.getByLabel("Password", { exact: true }).fill(user.password);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(
    page.getByRole("heading", { level: 1, name: "Plan a new trip" }),
  ).toBeVisible();

  // Step 1: details. An end date before the start date is caught before anything is sent.
  await page
    .getByLabel("Destination")
    .selectOption({ label: "Sampleton (sample)" });
  await page.getByLabel("Trip title").fill("Weekend in Sampleton");
  await page.getByLabel("Start date").fill("2026-12-04");
  await page.getByLabel("End date").fill("2026-12-01");
  await page.getByLabel("Adults").fill("2");
  await page.getByLabel("Budget (optional)").fill("600");
  await page.getByRole("button", { name: "Next", exact: true }).click();
  await expect(page.getByLabel("End date")).toHaveAccessibleDescription(
    /End date must be on or after start date\./,
  );
  await page.getByLabel("End date").fill("2026-12-06");
  await snapshot(page, info, "1-details");

  const created = page.waitForResponse(
    (r) => r.url().endsWith("/api/v1/trips") && r.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Next", exact: true }).click();
  expect((await created).status()).toBe(201);
  const tripId = (await (await created).json()).id as string;

  // Step 2: preferences, saved with API-14.
  await expect(stepHeading(page, "Your preferences")).toBeFocused();
  await page.getByRole("button", { name: "Museums" }).click();
  await page.getByText("Relaxed", { exact: true }).click();
  await page.getByLabel("Notes").fill("Quiet mornings, please.");
  await snapshot(page, info, "2-preferences");
  await page.getByRole("button", { name: "Next", exact: true }).click();

  // Step 3: must-visit places found with API-16.
  await expect(stepHeading(page, "Must-visit places")).toBeFocused();
  await page.getByLabel("Search places").fill("museum");
  const results = page.getByRole("list", { name: "Search results" });
  await results.getByRole("button").first().click();
  await expect(
    page.getByRole("list", { name: "Chosen places" }).getByRole("button"),
  ).toHaveCount(1);
  await snapshot(page, info, "3-places");
  await page.getByRole("button", { name: "Next", exact: true }).click();

  // Step 4: review of what the API saved, with each preference's effect (FR-009).
  await expect(stepHeading(page, "Review your trip")).toBeFocused();
  const details = page.getByRole("region", { name: "Trip details" });
  await expect(details).toContainText("Sampleton (sample)");
  await expect(details).toContainText("2026-12-04 to 2026-12-06 (3 days)");
  const preferences = page.getByRole("region", { name: "Preferences" });
  await expect(preferences).toContainText("Museums");
  await expect(preferences).toContainText("Ranks");
  await expect(preferences).toContainText("Note only");
  await expect(
    page.getByRole("region", { name: "Must-visit places" }),
  ).toContainText("Filters");
  await snapshot(page, info, "4-review");

  await page.getByRole("link", { name: "Generate itinerary" }).click();
  await expect(page).toHaveURL(`/trips/${tripId}/generate`);
});
