import { z } from "zod";

import type { ErrorDetail } from "@/lib/api/client";
import type { components } from "@/lib/api/schema";

/**
 * Trip details, preferences and must-visit places (§7.3; FR-007, FR-008, FR-009). The rules mirror
 * the server's (§6.5 TripIn and PreferencesIn, apps/api/app/trips/domain.py) so most mistakes are
 * shown before anything is sent; the server stays the authority and its 422 details are mapped
 * onto the same field names (`fieldErrors`).
 */

type Schemas = components["schemas"];
export type GroupNeed = Schemas["GroupNeed"];
export type Interest = Schemas["OfferedCategory"];
export type Pace = Schemas["Pace"];
export type BudgetPriority = Schemas["BudgetPriority"];
export type TransportPref = Schemas["TransportPref"];
export type AccommodationType = Schemas["AccommodationType"];
export type Effect = Schemas["Effect"];

export const TITLE_MAX_CHARS = 120;
export const MAX_TRIP_DAYS = 14;
export const ADULTS_MIN = 1;
export const ADULTS_MAX = 20;
export const CHILDREN_MIN = 0;
export const CHILDREN_MAX = 20;
export const NOTES_MAX_CHARS = 1000;
export const MAX_MUST_VISIT = 10;

// Display labels for the API's fixed vocabularies. Each record is typed by the generated enum, so a
// value added to or removed from the contract fails the type check here.
export const GROUP_NEED_LABELS: Record<GroupNeed, string> = {
  children: "Children",
  older_adults: "Older adults",
  reduced_mobility: "Reduced mobility",
};
export const INTEREST_LABELS: Record<Interest, string> = {
  sight: "Sights",
  museum: "Museums",
  nature: "Nature",
  food: "Food",
  shopping: "Shopping",
  entertainment: "Entertainment",
  religious: "Religious sites",
  activity: "Activities",
};
export const PACE_LABELS: Record<Pace, string> = {
  relaxed: "Relaxed",
  balanced: "Balanced",
  busy: "Busy",
};
export const BUDGET_PRIORITY_LABELS: Record<BudgetPriority, string> = {
  saving: "Saving",
  balanced: "Balanced",
  comfort: "Comfort",
};
export const TRANSPORT_LABELS: Record<TransportPref, string> = {
  walking: "Walking",
  local_transport: "Local transport",
  car: "Car",
};
export const ACCOMMODATION_LABELS: Record<AccommodationType, string> = {
  budget: "Budget",
  mid_range: "Mid-range",
  premium: "Premium",
  any: "No preference",
};
/** FR-009 AC3: what a preference field does in planning, as API-15 reports it. */
export const EFFECT_LABELS: Record<Effect, string> = {
  filter: "Filters",
  rank: "Ranks",
  note: "Note only",
};

function keysOf<K extends string>(labels: Record<K, string>) {
  return Object.keys(labels) as [K, ...K[]];
}

const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/;
const CURRENCY = /^[A-Z]{3}$/;
// numeric(12,2) on the server: at most 10 digits before the point and 2 after (IMD-05).
const AMOUNT = /^\d{1,10}(\.\d{1,2})?$/;

/** Days from start to end inclusive, as the server's num_days; for validation only. */
function tripDays(start: string, end: string): number {
  const utc = (iso: string) => {
    const [year, month, day] = iso.split("-").map(Number);
    return Date.UTC(year, month - 1, day);
  };
  return Math.round((utc(end) - utc(start)) / 86_400_000) + 1;
}

const count = (label: string, min: number, max: number) =>
  z
    .number({ error: `Enter the number of ${label}, from ${min} to ${max}.` })
    .int({ error: "Use a whole number." })
    .min(min, {
      error: `${capitalise(label)} must be between ${min} and ${max}.`,
    })
    .max(max, {
      error: `${capitalise(label)} must be between ${min} and ${max}.`,
    });

function capitalise(text: string) {
  return text.charAt(0).toUpperCase() + text.slice(1);
}

export const tripDetailsSchema = z
  .object({
    destination_id: z.string().min(1, { error: "Choose a destination." }),
    title: z
      .string()
      .trim()
      .min(1, {
        error: `Enter a trip name of 1 to ${TITLE_MAX_CHARS} characters.`,
      })
      .max(TITLE_MAX_CHARS, {
        error: `Enter a trip name of 1 to ${TITLE_MAX_CHARS} characters.`,
      }),
    start_date: z.string().regex(ISO_DATE, { error: "Choose a start date." }),
    end_date: z.string().regex(ISO_DATE, { error: "Choose an end date." }),
    adults: count("adults", ADULTS_MIN, ADULTS_MAX),
    children: count("children", CHILDREN_MIN, CHILDREN_MAX),
    group_needs: z.array(z.enum(keysOf(GROUP_NEED_LABELS))),
    // The budget is optional; amount and currency are sent together or not at all (§7.3).
    budget: z.object({
      amount: z.string().trim(),
      currency: z.string(),
    }),
  })
  .superRefine((trip, ctx) => {
    if (ISO_DATE.test(trip.start_date) && ISO_DATE.test(trip.end_date)) {
      if (trip.end_date < trip.start_date) {
        ctx.addIssue({
          code: "custom",
          path: ["end_date"],
          message: "End date must be on or after start date.",
        });
      } else if (tripDays(trip.start_date, trip.end_date) > MAX_TRIP_DAYS) {
        ctx.addIssue({
          code: "custom",
          path: ["end_date"],
          message: `A trip can be at most ${MAX_TRIP_DAYS} days long.`,
        });
      }
    }
    const { amount, currency } = trip.budget;
    if (amount === "") return;
    if (!AMOUNT.test(amount) || Number(amount) <= 0) {
      ctx.addIssue({
        code: "custom",
        path: ["budget", "amount"],
        message:
          "Budget must be greater than 0, with at most 2 decimal places.",
      });
    }
    if (!CURRENCY.test(currency)) {
      ctx.addIssue({
        code: "custom",
        path: ["budget", "currency"],
        message: "Choose the currency of the budget.",
      });
    }
  });

export type TripDetailsValues = z.infer<typeof tripDetailsSchema>;

/** The API-07 body for valid form values. */
export function toTripIn(values: TripDetailsValues): Schemas["TripIn"] {
  const { budget, ...rest } = values;
  return {
    ...rest,
    budget: budget.amount === "" ? null : budget,
  };
}

export const preferencesSchema = z.object({
  interests: z.array(z.enum(keysOf(INTEREST_LABELS))),
  pace: z.enum(keysOf(PACE_LABELS)),
  budget_priority: z.enum(keysOf(BUDGET_PRIORITY_LABELS)),
  transport_pref: z.enum(keysOf(TRANSPORT_LABELS)),
  accommodation_type: z.enum(keysOf(ACCOMMODATION_LABELS)),
  step_free_required: z.boolean(),
  notes: z.string().max(NOTES_MAX_CHARS, {
    error: `Keep notes to ${NOTES_MAX_CHARS} characters or fewer.`,
  }),
});

export type PreferencesValues = z.infer<typeof preferencesSchema>;

export const mustVisitSchema = z.array(z.uuid()).max(MAX_MUST_VISIT, {
  error: `You can choose up to ${MAX_MUST_VISIT} places.`,
});

/**
 * Server 422 details for a form: each detail whose field (or its first part, for "interests.0")
 * is one of `fields` is returned under that name; the rest are returned under "root".
 */
export function fieldErrors<F extends string>(
  details: ErrorDetail[],
  fields: readonly F[],
): { field: F | "root"; message: string }[] {
  return details.map(({ field, message }) => {
    const known = fields.find(
      (name) => field === name || field.startsWith(`${name}.`),
    );
    return { field: known ?? "root", message };
  });
}
