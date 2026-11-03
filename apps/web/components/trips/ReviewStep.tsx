import { Pencil } from "lucide-react";
import type { ReactNode } from "react";

import { effectsOf } from "@/components/trips/PreferenceForm";
import { EffectBadge } from "@/components/trips/Field";
import { Button } from "@/components/ui/button";
import type { components } from "@/lib/api/schema";
import {
  ACCOMMODATION_LABELS,
  BUDGET_PRIORITY_LABELS,
  type Effect,
  GROUP_NEED_LABELS,
  INTEREST_LABELS,
  PACE_LABELS,
  TRANSPORT_LABELS,
} from "@/lib/validation/trip";

type Schemas = components["schemas"];

function Section({
  id,
  title,
  onEdit,
  children,
}: {
  id: string;
  title: string;
  onEdit?: () => void;
  children: ReactNode;
}) {
  return (
    <section aria-labelledby={id} className="grid gap-4 rounded-lg border p-5">
      <div className="flex items-center justify-between gap-3">
        <h3 id={id} className="text-base font-semibold">
          {title}
        </h3>
        {onEdit && (
          <Button
            type="button"
            variant="ghost"
            onClick={onEdit}
            aria-label={`Edit ${title.toLowerCase()}`}
          >
            <Pencil aria-hidden="true" />
            Edit
          </Button>
        )}
      </div>
      {children}
    </section>
  );
}

function Detail({
  label,
  effect,
  wide,
  children,
}: {
  label: string;
  effect?: Effect;
  wide?: boolean;
  children: ReactNode;
}) {
  return (
    <div className={wide ? "grid gap-1 sm:col-span-2" : "grid gap-1"}>
      <dt className="flex items-center gap-2 text-sm text-muted-foreground">
        {label}
        {effect && <EffectBadge effect={effect} />}
      </dt>
      <dd className="text-sm font-medium whitespace-pre-line">{children}</dd>
    </div>
  );
}

function list(values: readonly string[], labels: Record<string, string>) {
  return values.length > 0
    ? values.map((value) => labels[value] ?? value).join(", ")
    : "None selected";
}

/** Step 4: the saved trip and preferences as the API returned them, with Edit links (§7.5.4). */
export function ReviewStep({
  trip,
  preferences,
  onEdit,
}: {
  trip: Schemas["TripOut"];
  preferences: Schemas["PreferencesOut"];
  onEdit: (step: number) => void;
}) {
  const effects = effectsOf(preferences);

  return (
    <div className="grid gap-4">
      <Section id="review-details" title="Trip details">
        <dl className="grid gap-4 sm:grid-cols-2">
          <Detail label="Destination">{trip.destination.name}</Detail>
          <Detail label="Trip title">{trip.title}</Detail>
          <Detail label="Dates">
            {trip.start_date} to {trip.end_date} ({trip.num_days}{" "}
            {trip.num_days === 1 ? "day" : "days"})
          </Detail>
          <Detail label="Travellers">
            {trip.adults} {trip.adults === 1 ? "adult" : "adults"},{" "}
            {trip.children} {trip.children === 1 ? "child" : "children"}
          </Detail>
          <Detail label="Budget (whole group)">
            {trip.budget
              ? `${trip.budget.amount} ${trip.budget.currency}`
              : "No budget"}
          </Detail>
          <Detail label="Group needs">
            {list(trip.group_needs, GROUP_NEED_LABELS)}
          </Detail>
        </dl>
      </Section>

      <Section
        id="review-preferences"
        title="Preferences"
        onEdit={() => onEdit(1)}
      >
        <dl className="grid gap-4 sm:grid-cols-2">
          <Detail label="Interests" effect={effects.interests}>
            {list(preferences.interests, INTEREST_LABELS)}
          </Detail>
          <Detail label="Pace" effect={effects.pace}>
            {PACE_LABELS[preferences.pace]}
          </Detail>
          <Detail label="Budget priority" effect={effects.budget_priority}>
            {BUDGET_PRIORITY_LABELS[preferences.budget_priority]}
          </Detail>
          <Detail label="Getting around" effect={effects.transport_pref}>
            {TRANSPORT_LABELS[preferences.transport_pref]}
          </Detail>
          <Detail
            label="Accommodation type"
            effect={effects.accommodation_type}
          >
            {ACCOMMODATION_LABELS[preferences.accommodation_type]}
          </Detail>
          <Detail label="Step-free access" effect={effects.step_free_required}>
            {preferences.step_free_required ? "Needed" : "Not needed"}
          </Detail>
          <Detail label="Notes" effect={effects.notes} wide>
            {preferences.notes?.trim() || "No notes"}
          </Detail>
        </dl>
      </Section>

      <Section
        id="review-places"
        title="Must-visit places"
        onEdit={() => onEdit(2)}
      >
        {effects.must_visit_place_ids && (
          <p>
            <EffectBadge effect={effects.must_visit_place_ids} />
          </p>
        )}
        {preferences.must_visit_places.length === 0 ? (
          <p className="text-sm text-muted-foreground">No places added.</p>
        ) : (
          <ul className="flex flex-wrap gap-2">
            {preferences.must_visit_places.map((place) => (
              <li
                key={place.id}
                className="rounded-full bg-secondary px-3 py-1 text-sm text-secondary-foreground"
              >
                {place.name}
              </li>
            ))}
          </ul>
        )}
      </Section>
    </div>
  );
}
