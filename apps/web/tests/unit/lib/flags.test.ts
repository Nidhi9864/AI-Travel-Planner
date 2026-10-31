import { afterEach, describe, expect, it, vi } from "vitest";

import { parseDisabledFeatures } from "@/lib/flags";

describe("feature switches (IMD-11)", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.resetModules();
  });

  it("parses names separated by commas or spaces and ignores empty entries", () => {
    expect([
      ...parseDisabledFeatures(" versions, locks ,,meal_slots packing "),
    ]).toEqual(["versions", "locks", "meal_slots", "packing"]);
    expect(parseDisabledFeatures("").size).toBe(0);
    expect(parseDisabledFeatures(undefined).size).toBe(0);
  });

  it("isEnabled reads NEXT_PUBLIC_FEATURES_DISABLED", async () => {
    vi.stubEnv("NEXT_PUBLIC_FEATURES_DISABLED", "wishlist,regeneration");
    const { isEnabled } = await import("@/lib/flags");

    expect(isEnabled("wishlist")).toBe(false);
    expect(isEnabled("regeneration")).toBe(false);
    expect(isEnabled("versions")).toBe(true);
  });

  it("enables every feature when the variable is empty", async () => {
    vi.stubEnv("NEXT_PUBLIC_FEATURES_DISABLED", "");
    const { FEATURE_NAMES, isEnabled } = await import("@/lib/flags");

    expect(FEATURE_NAMES.every((name) => isEnabled(name))).toBe(true);
  });
});
