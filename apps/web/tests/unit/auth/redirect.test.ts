import { describe, expect, it } from "vitest";

import { DEFAULT_AFTER_SIGN_IN, safeNextPath } from "@/lib/auth/redirect";

// The `next` parameter is never an open redirect (§7.2).
describe("safeNextPath", () => {
  it.each([
    ["/dashboard", "/dashboard"],
    ["/trips/abc/itinerary?day=2", "/trips/abc/itinerary?day=2"],
    ["/trips/abc#costs", "/trips/abc#costs"],
    ["/trips/../dashboard", "/dashboard"],
  ])("keeps the same-site path %s", (next, expected) => {
    expect(safeNextPath(next)).toBe(expected);
  });

  it.each([
    null,
    undefined,
    "",
    "dashboard",
    "//evil.example/path",
    "/\\evil.example",
    "/\\/evil.example",
    "https://evil.example/dashboard",
    "javascript:alert(1)",
    "/\tevil",
    " /dashboard",
  ])("falls back to /dashboard for %j", (next) => {
    expect(safeNextPath(next)).toBe(DEFAULT_AFTER_SIGN_IN);
  });
});
