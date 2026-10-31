import path from "node:path";

import type { Page } from "@playwright/test";

import { MESSAGES } from "../components/auth/messages";
import { expect, randomPassword, test, uniqueEmail } from "./fixtures/users";

// E2E-01 (auth part): sign-up, sign-in, reload, sign-out and Back against the local Supabase stack.
// Each test signs in or up at most once, which keeps a full run (four widths) well inside the
// local stack's limit of 30 sign-ins and sign-ups per 5 minutes (supabase/config.toml).

// UPDATE_SCREENSHOTS=1 refreshes the evidence screenshot of the IMP-109 part record.
const SCREENSHOT = path.resolve(
  __dirname,
  "../../../docs/progress/parts/IMP-109-whole-task-signup-errors-360.png",
);

async function expectNoHorizontalScroll(page: Page) {
  const { scrollWidth, innerWidth } = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    innerWidth: window.innerWidth,
  }));
  expect(scrollWidth).toBeLessThanOrEqual(innerWidth);
}

async function signIn(page: Page, email: string, password: string) {
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password", { exact: true }).fill(password);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
}

async function signUp(page: Page, email: string, password: string) {
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password", { exact: true }).fill(password);
  await page.getByRole("button", { name: "Create account" }).click();
}

// Next.js keeps its own role="alert" route announcer outside <main>, so messages are looked up in
// the main landmark.
const inMain = (page: Page) => page.getByRole("main");

const dashboardHeading = (page: Page) =>
  page.getByRole("heading", { level: 1, name: "Your trips" });

test("auth: sign-up rejects empty and weak input per field (TC-053)", async ({
  page,
}) => {
  const signUpCalls: string[] = [];
  page.on("request", (request) => {
    if (request.url().includes("/auth/v1/signup"))
      signUpCalls.push(request.url());
  });
  await page.goto("/sign-up");

  await page.getByRole("button", { name: "Create account" }).click();
  const email = page.getByLabel("Email");
  const password = page.getByLabel("Password", { exact: true });
  await expect(email).toHaveAttribute("aria-invalid", "true");
  await expect(email).toHaveAccessibleDescription("Enter your email address");
  await expect(password).toHaveAccessibleDescription(/Enter a password/);

  await email.fill("not-an-email");
  await password.fill("short");
  await page.getByRole("button", { name: "Create account" }).click();
  await expect(email).toHaveAccessibleDescription(
    "Enter a valid email address, like name@example.com",
  );
  await expect(password).toHaveAccessibleDescription(
    /Use at least 8 characters/,
  );
  await expectNoHorizontalScroll(page);
  expect(signUpCalls).toEqual([]);

  // §7.9: the show or hide toggle is reachable by keyboard and is a 44 px target.
  const toggle = page.getByRole("button", { name: "Show password" });
  await password.focus();
  await page.keyboard.press("Tab");
  await expect(toggle).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(password).toHaveAttribute("type", "text");
  const box = await toggle.boundingBox();
  expect(box?.width).toBeGreaterThanOrEqual(44);
  expect(box?.height).toBeGreaterThanOrEqual(44);
  await page.keyboard.press("Enter");

  if (
    process.env.UPDATE_SCREENSHOTS === "1" &&
    page.viewportSize()?.width === 360
  ) {
    await page.screenshot({ path: SCREENSHOT, fullPage: true });
  }
});

test("auth: a valid sign-up creates one account and signs in or asks for confirmation (TC-051)", async ({
  page,
  users,
}) => {
  const email = uniqueEmail("signup");
  users.track(email);
  await page.goto("/sign-up");
  await expectNoHorizontalScroll(page);
  await signUp(page, email, randomPassword());

  // The local stack has email confirmation off, so the account is signed in at once; with
  // confirmation on, the neutral notice is shown instead.
  await expect(
    dashboardHeading(page).or(page.getByText(MESSAGES.signUpNotice)),
  ).toBeVisible();
  expect(await users.countByEmail(email)).toBe(1);
});

test("auth: sign-up with an existing email shows the neutral notice and creates no second account (TC-052)", async ({
  page,
  users,
}) => {
  const existing = await users.create("duplicate");
  await page.goto("/sign-up");
  await signUp(page, existing.email, randomPassword());

  await expect(inMain(page).getByRole("status")).toHaveText(
    MESSAGES.signUpNotice,
  );
  await expect(inMain(page).getByRole("alert")).toHaveCount(0);
  expect(await users.countByEmail(existing.email)).toBe(1);

  // Nothing was signed in: the dashboard still sends the visitor to sign-in.
  await page.goto("/dashboard");
  await expect(page).toHaveURL(/\/sign-in\?next=%2Fdashboard$/);
});

test("auth: wrong credentials say only that the email or password is incorrect", async ({
  page,
  users,
}) => {
  const user = await users.create("wrong-password");
  await page.goto("/sign-in");
  await signIn(page, user.email, `${user.password}-wrong`);

  await expect(inMain(page).getByRole("alert")).toHaveText(
    MESSAGES.signInFailed,
  );
  await expect(page).toHaveURL(/\/sign-in$/);
});

test("auth: sign-in opens the dashboard, survives reload, and Back after sign-out shows no private data (TC-054, TC-056)", async ({
  page,
  users,
}) => {
  const user = await users.create("journey");

  // A signed-out visitor of an (app) page goes to /sign-in, which remembers the page.
  await page.goto("/dashboard");
  await expect(page).toHaveURL(/\/sign-in\?next=%2Fdashboard$/);
  await expectNoHorizontalScroll(page);
  await signIn(page, user.email, user.password);
  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(dashboardHeading(page)).toBeVisible();
  await expectNoHorizontalScroll(page);

  // The session survives a reload.
  await page.reload();
  await expect(dashboardHeading(page)).toBeVisible();

  // A signed-in user who opens /sign-in is sent to the dashboard (§7.2).
  await page.goto("/sign-in");
  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(dashboardHeading(page)).toBeVisible();

  // Sign out from the account menu, which names the signed-in user.
  await page.getByRole("button", { name: "Account menu" }).click();
  await expect(page.getByRole("menu")).toContainText(user.email);
  await page.getByRole("menuitem", { name: "Sign out" }).click();
  await expect(page).toHaveURL(/\/sign-in$/);

  // Back returns to an earlier dashboard entry: it must show nothing private and go to sign-in.
  await page.goBack();
  await expect(page).toHaveURL(/\/sign-in/);
  await expect(page.getByRole("heading", { name: "Sign in" })).toBeVisible();
  await expect(dashboardHeading(page)).toHaveCount(0);
  await expect(page.getByText(user.email)).toHaveCount(0);
});
