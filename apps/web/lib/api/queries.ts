/**
 * Query keys of §7.4. TanStack Query is the only cache; every hook built on the API client
 * (IMP-214 and later) takes its key from this factory, so invalidation in one place reaches every
 * reader. Calling a key without its trailing arguments gives the prefix used to invalidate them all,
 * for example `queryKeys.trips()` matches every `['trips', filters]` entry.
 */

/** Filter values that are part of a list key, kept in the URL query string by the page. */
export type QueryFilters = Readonly<
  Record<string, string | number | boolean | null | undefined>
>;

export const queryKeys = {
  trips: (filters?: QueryFilters) =>
    filters === undefined
      ? (["trips"] as const)
      : (["trips", filters] as const),
  trip: (tripId: string) => ["trip", tripId] as const,
  itinerary: (tripId: string, versionId?: string) =>
    versionId === undefined
      ? (["itinerary", tripId] as const)
      : (["itinerary", tripId, versionId] as const),
  costs: (tripId: string) => ["costs", tripId] as const,
  generation: (generationId: string) => ["generation", generationId] as const,
} as const;

/** The version segment of the itinerary key for the plan currently in use. */
export const CURRENT_VERSION = "current";
