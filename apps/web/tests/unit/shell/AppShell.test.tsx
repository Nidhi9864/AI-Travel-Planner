import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { AppShell } from "@/components/shell/AppShell";

const navigation = vi.hoisted(() => ({
  pathname: "/dashboard",
  params: {} as Record<string, string>,
}));

vi.mock("next/navigation", () => ({
  usePathname: () => navigation.pathname,
  useParams: () => navigation.params,
}));

function renderShell(variant?: "app" | "public") {
  return render(
    <AppShell variant={variant}>
      <h1>Page content</h1>
      <button type="button">First control in the page</button>
    </AppShell>,
  );
}

// jsdom applies no CSS, so both the header and the bottom navigation are in the tree here;
// in a browser only one is displayed at a time (md:block / md:hidden).
function firstNav() {
  return screen.getAllByRole("navigation", { name: "Main" })[0];
}

describe("AppShell (TC-278)", () => {
  beforeEach(() => {
    navigation.pathname = "/dashboard";
    navigation.params = {};
  });

  it("exposes header, navigation and main landmarks", () => {
    renderShell();

    const header = screen.getByRole("banner");
    expect(
      within(header).getByRole("link", { name: "AI Travel Planner" }),
    ).toHaveAttribute("href", "/dashboard");
    expect(
      screen.getAllByRole("navigation", { name: "Main" }).length,
    ).toBeGreaterThan(0);
    const main = screen.getByRole("main");
    expect(
      within(main).getByRole("heading", { name: "Page content" }),
    ).toBeInTheDocument();
    expect(
      within(header).getByRole("button", { name: "Account menu" }),
    ).toBeInTheDocument();
  });

  it("links Trips and Profile and marks the current page", () => {
    renderShell();

    const nav = firstNav();
    const trips = within(nav).getByRole("link", { name: /Trips/ });
    expect(trips).toHaveAttribute("href", "/dashboard");
    expect(trips).toHaveAttribute("aria-current", "page");
    const profile = within(nav).getByRole("link", { name: /Profile/ });
    expect(profile).toHaveAttribute("href", "/profile");
    expect(profile).not.toHaveAttribute("aria-current");
  });

  it("offers Itinerary and Costs only when a trip is open", () => {
    const { unmount } = renderShell();
    let nav = firstNav();
    expect(
      within(nav).queryByRole("link", { name: /Itinerary/ }),
    ).not.toBeInTheDocument();
    expect(
      within(nav).getByText("Itinerary").closest("[aria-disabled='true']"),
    ).not.toBeNull();
    expect(
      within(nav).getByText("Costs").closest("[aria-disabled='true']"),
    ).not.toBeNull();
    unmount();

    navigation.pathname = "/trips/trip-1/itinerary";
    navigation.params = { tripId: "trip-1" };
    renderShell();
    nav = firstNav();
    const itinerary = within(nav).getByRole("link", { name: /Itinerary/ });
    expect(itinerary).toHaveAttribute("href", "/trips/trip-1/itinerary");
    expect(itinerary).toHaveAttribute("aria-current", "page");
    expect(within(nav).getByRole("link", { name: /Costs/ })).toHaveAttribute(
      "href",
      "/trips/trip-1/costs",
    );
  });

  it("has a skip link as the first focusable element that moves focus to main", async () => {
    const user = userEvent.setup();
    renderShell();

    await user.tab();
    const skip = screen.getByRole("link", { name: "Skip to content" });
    expect(skip).toHaveFocus();
    expect(skip).toHaveAttribute("href", "#main-content");

    await user.keyboard("{Enter}");
    const main = screen.getByRole("main");
    expect(main).toHaveFocus();
    expect(main).toHaveAttribute("id", "main-content");

    await user.tab();
    expect(
      screen.getByRole("button", { name: "First control in the page" }),
    ).toHaveFocus();
  });

  it("public variant keeps header, main and skip link without the signed-in navigation", () => {
    renderShell("public");

    expect(screen.getByRole("banner")).toBeInTheDocument();
    expect(screen.getByRole("main")).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: "Skip to content" }),
    ).toBeInTheDocument();
    expect(screen.queryByRole("navigation")).not.toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: "AI Travel Planner" }),
    ).toHaveAttribute("href", "/");
    expect(screen.getByRole("link", { name: "Sign in" })).toHaveAttribute(
      "href",
      "/sign-in",
    );
  });
});
