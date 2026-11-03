import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { TripWizard } from "@/components/trips/TripWizard";
import type { components } from "@/lib/api/schema";
import {
  mustVisitSchema,
  preferencesSchema,
  toTripIn,
  tripDetailsSchema,
} from "@/lib/validation/trip";

// TC-068, TC-076 (FR-007 to FR-009): the wizard against a fake API. No Supabase and no network: the
// browser client is faked and fetch answers from the in-memory SAMPLE server below.
vi.mock("@/lib/auth/supabase", () => ({
  getSupabase: () => ({
    auth: {
      getSession: async () => ({ data: { session: { access_token: "t" } } }),
    },
  }),
}));
vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://api.test/api/v1");

type Schemas = components["schemas"];

const DESTINATION_ID = "00000000-0000-4000-8000-000000000001";
const TRIP_ID = "00000000-0000-4000-8000-000000000002";
const PLACE = {
  id: "00000000-0000-4000-8000-000000000003",
  name: "Old Mill Museum (sample)",
};
const EFFECTS: Schemas["PreferenceEffect"][] = [
  { field: "interests", effect: "rank" },
  { field: "pace", effect: "rank" },
  { field: "budget_priority", effect: "rank" },
  { field: "transport_pref", effect: "note" },
  { field: "accommodation_type", effect: "note" },
  { field: "step_free_required", effect: "filter" },
  { field: "notes", effect: "note" },
  { field: "must_visit_place_ids", effect: "filter" },
];

type Call = { method: string; path: string; body: unknown };

/** The SAMPLE API: answers API-06, 07, 14, 15 and 16; `fail` overrides one route's answer. */
function fakeApi() {
  const calls: Call[] = [];
  const fail: Record<string, () => Response> = {};
  let preferences: Schemas["PreferencesOut"] = {
    interests: [],
    pace: "balanced",
    budget_priority: "balanced",
    transport_pref: "walking",
    accommodation_type: "any",
    step_free_required: false,
    notes: null,
    must_visit_place_ids: [],
    must_visit_places: [],
    effects: EFFECTS,
    saved: false,
  };
  const json = (body: unknown, status = 200) =>
    new Response(JSON.stringify(body), {
      status,
      headers: { "Content-Type": "application/json" },
    });

  async function handle(request: Request): Promise<Response> {
    const url = new URL(request.url);
    const key = `${request.method} ${url.pathname}`;
    const body = request.method === "GET" ? null : await request.json();
    calls.push({ method: request.method, path: url.pathname, body });
    if (fail[key]) return fail[key]();

    if (key === "GET /api/v1/destinations") {
      return json([
        {
          id: DESTINATION_ID,
          slug: "sampleton",
          name: "Sampleton",
          region: null,
          country_code: "GB",
          timezone: "Europe/London",
          currency: "GBP",
          is_sample: true,
          center: { lat: 51.5, lon: -0.1 },
          bbox: { min_lat: 51, min_lon: -1, max_lat: 52, max_lon: 1 },
        },
      ]);
    }
    if (key === "POST /api/v1/trips") {
      const trip = body as Schemas["TripIn"];
      return json(
        {
          ...trip,
          id: TRIP_ID,
          num_days: 3,
          adults: trip.adults ?? 1,
          children: trip.children ?? 0,
          group_needs: trip.group_needs ?? [],
          budget: trip.budget
            ? { amount: "1500.00", currency: trip.budget.currency }
            : null,
          status: "draft",
          plan_revision: 0,
          plan_stale: false,
          has_itinerary: false,
          destination: {
            id: DESTINATION_ID,
            name: "Sampleton",
            timezone: "Europe/London",
            currency: "GBP",
            is_sample: true,
          },
          created_at: "2026-11-03T10:00:00Z",
          updated_at: "2026-11-03T10:00:00Z",
        },
        201,
      );
    }
    if (url.pathname === `/api/v1/trips/${TRIP_ID}/preferences`) {
      if (request.method === "PUT") {
        const saved = body as Schemas["PreferencesIn"];
        const ids = saved.must_visit_place_ids ?? [];
        preferences = {
          ...preferences,
          ...saved,
          notes: saved.notes ?? null,
          must_visit_place_ids: ids,
          must_visit_places: ids.includes(PLACE.id) ? [PLACE] : [],
          saved: true,
        } as Schemas["PreferencesOut"];
      }
      return json(preferences);
    }
    if (key === "GET /api/v1/places") {
      return json({
        items: [
          {
            ...PLACE,
            category: "museum",
            tags: [],
            lat: 51.5,
            lon: -0.1,
            typical_duration_min: 60,
            price: null,
            price_label: "estimate",
            hours_label: "estimate",
            verification_status: "unverified",
            suitability: {},
          },
        ],
        total: 1,
        limit: 20,
        offset: 0,
      });
    }
    return json({ error: { code: "NOT_FOUND", message: "Not found." } }, 404);
  }

  return { calls, fail, handle, json };
}

let server: ReturnType<typeof fakeApi>;

beforeEach(() => {
  server = fakeApi();
  vi.stubGlobal("fetch", (request: Request) => server.handle(request));
});

function renderWizard() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  render(
    <QueryClientProvider client={client}>
      <TripWizard />
    </QueryClientProvider>,
  );
  return userEvent.setup();
}

async function fillDetails(
  user: ReturnType<typeof userEvent.setup>,
  { end = "2026-12-06" } = {},
) {
  await user.selectOptions(
    await screen.findByLabelText("Destination"),
    "Sampleton",
  );
  await user.type(screen.getByLabelText("Trip title"), "Weekend in Sampleton");
  await user.type(screen.getByLabelText("Start date"), "2026-12-04");
  await user.type(screen.getByLabelText("End date"), end);
  await user.clear(screen.getByLabelText("Adults"));
  await user.type(screen.getByLabelText("Adults"), "2");
  await user.type(screen.getByLabelText("Budget (optional)"), "1500");
}

const next = () => screen.getByRole("button", { name: /Next/ });
const posts = () => server.calls.filter((call) => call.method !== "GET");

describe("TripWizard (FR-007 to FR-009)", () => {
  it("TC-068: saves each step and links the review to the generate page", async () => {
    const user = renderWizard();
    await fillDetails(user);
    await user.click(screen.getByRole("button", { name: "Children" }));
    await user.click(next());

    // Step 1 created the draft trip with API-07, budget in the destination's currency.
    expect(
      await screen.findByRole("heading", { name: "Your preferences" }),
    ).toHaveFocus();
    expect(posts()[0]).toEqual({
      method: "POST",
      path: "/api/v1/trips",
      body: {
        destination_id: DESTINATION_ID,
        title: "Weekend in Sampleton",
        start_date: "2026-12-04",
        end_date: "2026-12-06",
        adults: 2,
        children: 0,
        group_needs: ["children"],
        budget: { amount: "1500", currency: "GBP" },
      },
    });

    // Step 2 saves the preferences with API-14 before step 3 opens.
    await user.click(screen.getByRole("button", { name: "Museums" }));
    await user.click(screen.getByRole("radio", { name: "Relaxed" }));
    await user.type(screen.getByLabelText("Notes"), "Quiet mornings.");
    await user.click(next());
    expect(
      await screen.findByRole("heading", { name: "Must-visit places" }),
    ).toHaveFocus();
    expect(posts()[1]).toMatchObject({
      method: "PUT",
      body: {
        interests: ["museum"],
        pace: "relaxed",
        notes: "Quiet mornings.",
        must_visit_place_ids: [],
      },
    });

    // Step 3 searches API-16 and saves the chosen place with the same preferences.
    await user.type(screen.getByLabelText("Search places"), "mill");
    await user.click(
      await screen.findByRole("button", { name: `Add ${PLACE.name}` }),
    );
    await user.click(next());
    await screen.findByRole("heading", { name: "Review your trip" });
    expect(posts()[2]).toMatchObject({
      method: "PUT",
      body: {
        interests: ["museum"],
        pace: "relaxed",
        must_visit_place_ids: [PLACE.id],
      },
    });
    expect(
      server.calls.some(
        (call) => call.path === "/api/v1/places" && call.method === "GET",
      ),
    ).toBe(true);

    // The review shows what the API returned and links to the generate page.
    const review = screen.getByRole("region", { name: "Trip details" });
    expect(within(review).getByText("1500.00 GBP")).toBeInTheDocument();
    expect(within(review).getByText("2026-12-04 to 2026-12-06 (3 days)"));
    expect(
      screen.getByRole("link", { name: "Generate itinerary" }),
    ).toHaveAttribute("href", `/trips/${TRIP_ID}/generate`);
  });

  it("TC-076: after a save, each field shows its effect as read back from API-15", async () => {
    const user = renderWizard();
    await fillDetails(user);
    await user.click(next());
    await screen.findByRole("heading", { name: "Your preferences" });
    // Nothing saved yet: no effect is shown.
    expect(screen.queryByText("Ranks")).not.toBeInTheDocument();

    await user.click(next());
    await screen.findByRole("heading", { name: "Must-visit places" });
    const reads = server.calls.filter(
      (call) => call.method === "GET" && call.path.endsWith("/preferences"),
    );
    expect(reads.length).toBeGreaterThanOrEqual(2); // before and after the save
    // The must-visit field filters.
    const places = screen.getByRole("form", { name: "Must-visit places" });
    expect(within(places).getByText("Filters")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /Back/ }));
    const form = screen.getByRole("form", { name: "Preferences" });
    const interests = within(form).getByRole("group", { name: /Interests/ });
    expect(within(interests).getByText("Ranks")).toBeInTheDocument();
    const notes = within(form).getByText("Notes").parentElement;
    expect(notes).toHaveTextContent("Note only");
    expect(
      within(form).getByText("I need step-free access").parentElement,
    ).toHaveTextContent("Filters");
  });

  it("FR-008 AC1: an end date before the start date is shown on the field and nothing is sent", async () => {
    const user = renderWizard();
    await fillDetails(user, { end: "2026-12-01" });
    await user.click(next());

    const end = screen.getByLabelText("End date");
    expect(end).toHaveAttribute("aria-invalid", "true");
    expect(end).toHaveAccessibleDescription(
      "Trips can be 1 to 14 days long. End date must be on or after start date.",
    );
    expect(posts()).toEqual([]);
  });

  it("FR-008 AC1: the server's 422 is mapped onto the same field and the input is kept", async () => {
    server.fail["POST /api/v1/trips"] = () =>
      server.json(
        {
          error: {
            code: "VALIDATION_ERROR",
            message: "Some fields need attention.",
            request_id: "req-422",
            details: [
              {
                field: "end_date",
                message: "A trip can be at most 3 days long.",
              },
              {
                field: "budget.currency",
                message: "Budget currency must be GBP.",
              },
            ],
            retry_after_s: null,
          },
        },
        422,
      );
    const user = renderWizard();
    await fillDetails(user);
    await user.click(next());

    const end = screen.getByLabelText("End date");
    await waitFor(() =>
      expect(end).toHaveAccessibleDescription(
        "Trips can be 1 to 14 days long. A trip can be at most 3 days long.",
      ),
    );
    expect(screen.getByLabelText("Currency")).toHaveAccessibleDescription(
      "The currency of the destination. Budget currency must be GBP.",
    );
    expect(screen.getByLabelText("Trip title")).toHaveValue(
      "Weekend in Sampleton",
    );
    expect(screen.getByRole("heading", { name: "Trip details" })).toBeVisible();
  });

  it("a 5xx shows ErrorState with the request ID and keeps the input", async () => {
    server.fail["POST /api/v1/trips"] = () =>
      server.json(
        {
          error: {
            code: "INTERNAL",
            message: "Something went wrong on our side.",
            request_id: "req-500",
            details: [],
            retry_after_s: null,
          },
        },
        500,
      );
    const user = renderWizard();
    await fillDetails(user);
    await user.click(next());

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("Something went wrong on our side.");
    expect(alert).toHaveTextContent("Request ID: req-500");
    expect(screen.getByLabelText("Trip title")).toHaveValue(
      "Weekend in Sampleton",
    );
  });

  it("is operable by keyboard: Tab reaches every control in order and Enter saves the step", async () => {
    const user = renderWizard();
    await screen.findByLabelText("Destination");

    await user.tab();
    expect(screen.getByLabelText("Destination")).toHaveFocus();
    await user.selectOptions(screen.getByLabelText("Destination"), "Sampleton");
    await user.tab();
    expect(screen.getByLabelText("Trip title")).toHaveFocus();
    await user.keyboard("Weekend in Sampleton");
    await user.tab();
    expect(screen.getByLabelText("Start date")).toHaveFocus();
    await user.keyboard("2026-12-04");
    await user.tab();
    expect(screen.getByLabelText("End date")).toHaveFocus();
    await user.keyboard("2026-12-06");
    await user.tab();
    expect(screen.getByLabelText("Adults")).toHaveFocus();
    await user.tab();
    expect(screen.getByLabelText("Children")).toHaveFocus();
    for (const need of ["Children", "Older adults", "Reduced mobility"]) {
      await user.tab();
      expect(screen.getByRole("button", { name: need })).toHaveFocus();
    }
    await user.keyboard(" "); // toggles the chip
    expect(
      screen.getByRole("button", { name: "Reduced mobility" }),
    ).toHaveAttribute("aria-pressed", "true");
    await user.tab();
    expect(screen.getByLabelText("Budget (optional)")).toHaveFocus();
    await user.tab();
    expect(screen.getByLabelText("Currency")).toHaveFocus();
    await user.tab();
    expect(next()).toHaveFocus(); // Back is disabled on the first step
    await user.keyboard("{Enter}");

    expect(
      await screen.findByRole("heading", { name: "Your preferences" }),
    ).toHaveFocus();
    expect(posts()[0]).toMatchObject({
      body: { group_needs: ["reduced_mobility"], budget: null },
    });
  });
});

describe("trip.ts rules mirror the server (§6.5, §7.3)", () => {
  const details = {
    destination_id: DESTINATION_ID,
    title: "Trip",
    start_date: "2026-12-01",
    end_date: "2026-12-14",
    adults: 1,
    children: 0,
    group_needs: [],
    budget: { amount: "", currency: "" },
  };
  const messages = (values: unknown) => {
    const result = tripDetailsSchema.safeParse(values);
    return result.success
      ? {}
      : Object.fromEntries(
          result.error.issues.map((issue) => [
            issue.path.join("."),
            issue.message,
          ]),
        );
  };

  it("accepts 14 days and no budget; rejects 15 days", () => {
    expect(messages(details)).toEqual({});
    expect(messages({ ...details, end_date: "2026-12-15" })).toEqual({
      end_date: "A trip can be at most 14 days long.",
    });
  });

  it("limits travellers to 1-20 adults and 0-20 children", () => {
    expect(messages({ ...details, adults: 0, children: 21 })).toEqual({
      adults: "Adults must be between 1 and 20.",
      children: "Children must be between 0 and 20.",
    });
    expect(messages({ ...details, adults: 20, children: 20 })).toEqual({});
  });

  it("needs a budget greater than 0 with a currency, or no budget at all", () => {
    expect(
      messages({ ...details, budget: { amount: "0", currency: "GBP" } }),
    ).toEqual({
      "budget.amount":
        "Budget must be greater than 0, with at most 2 decimal places.",
    });
    expect(
      messages({ ...details, budget: { amount: "10.50", currency: "" } }),
    ).toEqual({ "budget.currency": "Choose the currency of the budget." });
    expect(
      toTripIn({ ...details, budget: { amount: "", currency: "GBP" } }).budget,
    ).toBeNull();
  });

  it("limits notes to 1,000 characters and must-visit places to 10", () => {
    const preferences = {
      interests: [],
      pace: "balanced",
      budget_priority: "balanced",
      transport_pref: "walking",
      accommodation_type: "any",
      step_free_required: false,
      notes: "x".repeat(1001),
    };
    expect(
      preferencesSchema.safeParse(preferences).error?.issues[0].message,
    ).toBe("Keep notes to 1000 characters or fewer.");
    const ids = Array.from(
      { length: 11 },
      (_, i) => `00000000-0000-4000-8000-${String(i).padStart(12, "0")}`,
    );
    expect(mustVisitSchema.safeParse(ids.slice(0, 10)).success).toBe(true);
    expect(mustVisitSchema.safeParse(ids).error?.issues[0].message).toBe(
      "You can choose up to 10 places.",
    );
  });
});
