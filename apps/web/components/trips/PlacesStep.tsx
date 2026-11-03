"use client";

import { Check, Plus, Search, X } from "lucide-react";
import { useEffect, useState, type FormEvent } from "react";

import { ErrorState } from "@/components/states/ErrorState";
import { LoadingSkeleton } from "@/components/states/LoadingSkeleton";
import { EffectBadge, Field } from "@/components/trips/Field";
import { Input } from "@/components/ui/input";
import type { ErrorDetail } from "@/lib/api/client";
import { usePlaceSearch } from "@/lib/api/queries";
import type { components } from "@/lib/api/schema";
import { MAX_MUST_VISIT, type Effect } from "@/lib/validation/trip";

type Place = components["schemas"]["MustVisitPlace"];

const SEARCH_DEBOUNCE_MS = 300;
const QUERY_MAX_CHARS = 80; // API-16 q

/** Step 3: pick up to 10 must-visit places of the trip's destination, found with API-16. */
export function PlacesStep({
  formId,
  destinationId,
  initial,
  effect,
  onSave,
}: {
  formId: string;
  destinationId: string;
  initial: Place[];
  effect: Effect | undefined;
  onSave: (placeIds: string[]) => Promise<ErrorDetail[]>;
}) {
  const [selected, setSelected] = useState<Place[]>(initial);
  const [query, setQuery] = useState("");
  const [q, setQ] = useState("");
  const [error, setError] = useState<string | undefined>();
  const search = usePlaceSearch(destinationId, q);

  useEffect(() => {
    const timer = setTimeout(() => setQ(query.trim()), SEARCH_DEBOUNCE_MS);
    return () => clearTimeout(timer);
  }, [query]);

  const atLimit = selected.length >= MAX_MUST_VISIT;
  const selectedIds = new Set(selected.map((place) => place.id));

  function add(place: Place) {
    if (atLimit || selectedIds.has(place.id)) return;
    setSelected([...selected, { id: place.id, name: place.name }]);
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(undefined);
    const details = await onSave(selected.map((place) => place.id));
    if (details.length > 0) setError(details.map((d) => d.message).join(" "));
  }

  return (
    <form
      id={formId}
      noValidate
      onSubmit={submit}
      aria-label="Must-visit places"
      className="grid gap-8"
    >
      <Field
        id="place-search"
        label="Search places"
        hint="Search by name, then choose a place to add it to your trip."
      >
        {(describedBy) => (
          <div className="relative">
            <Search
              aria-hidden="true"
              className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground"
            />
            <Input
              id="place-search"
              type="search"
              value={query}
              maxLength={QUERY_MAX_CHARS}
              onChange={(event) => setQuery(event.target.value)}
              autoComplete="off"
              aria-describedby={describedBy}
              className="pl-9"
            />
          </div>
        )}
      </Field>

      <div className="grid gap-3">
        {q === "" && (
          <p className="text-sm text-muted-foreground">
            Start typing to find places.
          </p>
        )}
        {q !== "" && search.isPending && (
          <LoadingSkeleton count={3} label="Searching places" />
        )}
        {q !== "" && search.isError && (
          <ErrorState
            title="Places could not be searched"
            error={search.error}
            onRetry={() => void search.refetch()}
          />
        )}
        {q !== "" && search.data && search.data.items.length === 0 && (
          <p role="status" className="text-sm text-muted-foreground">
            No places match your search.
          </p>
        )}
        {q !== "" && search.data && search.data.items.length > 0 && (
          <ul
            aria-label="Search results"
            className="divide-y divide-border rounded-lg border bg-background"
          >
            {search.data.items.map((place) => {
              const added = selectedIds.has(place.id);
              return (
                <li key={place.id}>
                  <button
                    type="button"
                    onClick={() => add(place)}
                    disabled={added || atLimit}
                    aria-label={
                      added ? `${place.name}, added` : `Add ${place.name}`
                    }
                    className="flex min-h-touch w-full items-center justify-between gap-3 px-4 py-2 text-left text-sm font-medium transition-colors outline-none hover:bg-muted focus-visible:bg-muted focus-visible:ring-3 focus-visible:ring-ring disabled:cursor-not-allowed disabled:text-muted-foreground disabled:hover:bg-transparent"
                  >
                    <span>{place.name}</span>
                    {added ? (
                      <span className="inline-flex items-center gap-1">
                        <Check aria-hidden="true" className="size-4" />
                        Added
                      </span>
                    ) : (
                      <Plus aria-hidden="true" className="size-4" />
                    )}
                  </button>
                </li>
              );
            })}
          </ul>
        )}
        <p
          aria-live="polite"
          className="text-sm font-medium text-destructive empty:hidden"
        >
          {atLimit ? `You can choose up to ${MAX_MUST_VISIT} places.` : error}
        </p>
      </div>

      <div className="grid gap-3">
        <div className="flex items-center justify-between gap-2">
          <h3 className="flex items-center gap-2 text-sm font-medium">
            Your places
            {effect && <EffectBadge effect={effect} />}
          </h3>
          <span className="text-sm text-muted-foreground tabular-nums">
            {selected.length} of {MAX_MUST_VISIT}
          </span>
        </div>
        {selected.length === 0 ? (
          <p className="text-sm text-muted-foreground">No places added yet.</p>
        ) : (
          <ul aria-label="Chosen places" className="flex flex-wrap gap-2">
            {selected.map((place) => (
              <li key={place.id}>
                <button
                  type="button"
                  onClick={() =>
                    setSelected(selected.filter((item) => item.id !== place.id))
                  }
                  aria-label={`Remove ${place.name}`}
                  className="inline-flex min-h-touch items-center gap-2 rounded-full border border-input bg-background py-2 pr-3 pl-4 text-sm font-medium transition-colors outline-none hover:border-ring focus-visible:ring-3 focus-visible:ring-ring focus-visible:ring-offset-2"
                >
                  {place.name}
                  <X aria-hidden="true" className="size-4" />
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </form>
  );
}
