import {
  useMutation,
  useQuery,
  useQueryClient,
  keepPreviousData,
} from "@tanstack/react-query";

import { api, unwrap } from "@/lib/api/client";
import type { components } from "@/lib/api/schema";

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
  destinations: () => ["destinations"] as const,
  preferences: (tripId: string) => ["preferences", tripId] as const,
  places: (destinationId: string, filters?: QueryFilters) =>
    filters === undefined
      ? (["places", destinationId] as const)
      : (["places", destinationId, filters] as const),
  itinerary: (tripId: string, versionId?: string) =>
    versionId === undefined
      ? (["itinerary", tripId] as const)
      : (["itinerary", tripId, versionId] as const),
  costs: (tripId: string) => ["costs", tripId] as const,
  generation: (generationId: string) => ["generation", generationId] as const,
} as const;

/** The version segment of the itinerary key for the plan currently in use. */
export const CURRENT_VERSION = "current";

type Schemas = components["schemas"];

/** API-06: the active destinations, for the wizard's destination list. */
export function useDestinations() {
  return useQuery({
    queryKey: queryKeys.destinations(),
    queryFn: async () => unwrap(await api().GET("/api/v1/destinations")),
  });
}

/** API-15: the trip's preferences, with what each field does (FR-009). */
export function usePreferences(tripId: string | undefined) {
  return useQuery({
    queryKey: queryKeys.preferences(tripId ?? ""),
    queryFn: async () =>
      unwrap(
        await api().GET("/api/v1/trips/{trip_id}/preferences", {
          params: { path: { trip_id: tripId ?? "" } },
        }),
      ),
    enabled: tripId !== undefined,
  });
}

/** API-16 basic search: places of one destination whose name matches `q`. */
export function usePlaceSearch(destinationId: string | undefined, q: string) {
  return useQuery({
    queryKey: queryKeys.places(destinationId ?? "", { q }),
    queryFn: async () =>
      unwrap(
        await api().GET("/api/v1/places", {
          params: { query: { destination_id: destinationId ?? "", q } },
        }),
      ),
    enabled: destinationId !== undefined && q !== "",
    placeholderData: keepPreviousData,
  });
}

/** API-07: create a draft trip (§7.4: invalidate `trips`). */
export function useCreateTrip() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (body: Schemas["TripIn"]) =>
      unwrap(await api().POST("/api/v1/trips", { body })),
    onSuccess: async (trip) => {
      queryClient.setQueryData(queryKeys.trip(trip.id), trip);
      await queryClient.invalidateQueries({ queryKey: queryKeys.trips() });
    },
  });
}

/** API-14: replace the trip's preferences (§7.4: invalidate `preferences` and `trip`). */
export function useSavePreferences(tripId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (body: Schemas["PreferencesIn"]) =>
      unwrap(
        await api().PUT("/api/v1/trips/{trip_id}/preferences", {
          params: { path: { trip_id: tripId } },
          body,
        }),
      ),
    onSuccess: async (saved) => {
      queryClient.setQueryData(queryKeys.preferences(tripId), saved);
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: queryKeys.preferences(tripId),
        }),
        queryClient.invalidateQueries({ queryKey: queryKeys.trip(tripId) }),
      ]);
    },
  });
}
