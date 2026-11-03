"use client";

import { ArrowLeft, ArrowRight, Loader2 } from "lucide-react";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";

import {
  ErrorState,
  type ErrorStateError,
} from "@/components/states/ErrorState";
import { LoadingSkeleton } from "@/components/states/LoadingSkeleton";
import { PlacesStep } from "@/components/trips/PlacesStep";
import { effectsOf, PreferenceForm } from "@/components/trips/PreferenceForm";
import { ReviewStep } from "@/components/trips/ReviewStep";
import { TripDetailsStep } from "@/components/trips/TripDetailsStep";
import { TripStepper } from "@/components/trips/TripStepper";
import { Button } from "@/components/ui/button";
import { ApiError, type ErrorDetail } from "@/lib/api/client";
import {
  useCreateTrip,
  usePreferences,
  useSavePreferences,
} from "@/lib/api/queries";
import type { components } from "@/lib/api/schema";
import {
  toTripIn,
  type PreferencesValues,
  type TripDetailsValues,
} from "@/lib/validation/trip";

type Schemas = components["schemas"];

const STEPS = [
  {
    name: "Details",
    title: "Trip details",
    description: "Where you are going, when, and who is coming.",
  },
  {
    name: "Preferences",
    title: "Your preferences",
    description: "Tell us how you like to travel.",
  },
  {
    name: "Must-visit places",
    title: "Must-visit places",
    description: `Add up to 10 places you do not want to miss.`,
  },
  {
    name: "Review",
    title: "Review your trip",
    description: "Check everything before your itinerary is built.",
  },
] as const;
const FORM_IDS = ["trip-details", "trip-preferences", "trip-places"] as const;
const REVIEW = 3;

const OFFLINE: ErrorStateError = {
  message:
    "The server could not be reached. Check your connection and try again; your input is kept.",
};

/** The API-14 body: a full replacement, so every field is sent each time. */
function preferencesIn(
  values: PreferencesValues,
  placeIds: string[],
): Schemas["PreferencesIn"] {
  return {
    ...values,
    notes: values.notes.trim() === "" ? null : values.notes,
    must_visit_place_ids: placeIds,
  };
}

/**
 * /trips/new (§7.5.4; FR-007 to FR-009): details, preferences, must-visit places and review. Each
 * step is saved before the next one opens: Details creates the draft trip (API-07); Preferences
 * and Must-visit places save with API-14, and the field effects are read back from API-15.
 */
export function TripWizard() {
  const [step, setStep] = useState(0);
  const [trip, setTrip] = useState<Schemas["TripOut"]>();
  const [saveError, setSaveError] = useState<ErrorStateError | null>(null);
  const createTrip = useCreateTrip();
  const savePreferences = useSavePreferences(trip?.id ?? "");
  const preferences = usePreferences(trip?.id);
  const heading = useRef<HTMLHeadingElement>(null);
  const firstRender = useRef(true);
  const saving = createTrip.isPending || savePreferences.isPending;

  // Focus moves to the new step's heading, so screen readers announce it (§7.9).
  useEffect(() => {
    if (firstRender.current) {
      firstRender.current = false;
      return;
    }
    heading.current?.focus();
  }, [step]);

  function goTo(next: number) {
    setSaveError(null);
    setStep(next);
  }

  /** Runs one save; returns the 422 field details for the form, or none. */
  async function save(action: () => Promise<void>): Promise<ErrorDetail[]> {
    setSaveError(null);
    try {
      await action();
      return [];
    } catch (error) {
      if (!(error instanceof ApiError)) {
        setSaveError(OFFLINE);
        return [];
      }
      if (error.code === "VALIDATION_ERROR" && error.details.length > 0) {
        return error.details;
      }
      setSaveError(error);
      return [];
    }
  }

  const saveDetails = (values: TripDetailsValues) =>
    save(async () => {
      if (!trip) setTrip(await createTrip.mutateAsync(toTripIn(values)));
      setStep(1);
    });

  const savePreferenceFields = (values: PreferencesValues) =>
    save(async () => {
      const current = preferences.data?.must_visit_place_ids ?? [];
      await savePreferences.mutateAsync(preferencesIn(values, current));
      setStep(2);
    });

  const savePlaces = (placeIds: string[]) =>
    save(async () => {
      if (!preferences.data) return;
      const { interests, pace, budget_priority, transport_pref } =
        preferences.data;
      const { accommodation_type, step_free_required, notes } =
        preferences.data;
      await savePreferences.mutateAsync(
        preferencesIn(
          {
            interests,
            pace,
            budget_priority,
            transport_pref,
            accommodation_type,
            step_free_required,
            notes: notes ?? "",
          },
          placeIds,
        ),
      );
      setStep(REVIEW);
    });

  const current = STEPS[step];
  const loadingPreferences = (
    <LoadingSkeleton shape="text" count={4} label="Loading your preferences" />
  );

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6">
      <h1 className="font-heading text-2xl font-semibold">Plan a new trip</h1>
      <div className="rounded-xl border bg-card p-4 text-card-foreground md:p-8">
        <TripStepper steps={STEPS.map((item) => item.name)} current={step} />

        <div className="mt-8">
          <h2
            ref={heading}
            tabIndex={-1}
            className="text-xl font-semibold tracking-tight outline-none"
          >
            {current.title}
          </h2>
          <p className="mt-2 text-sm text-muted-foreground">
            {current.description}
          </p>
        </div>

        <div className="mt-8">
          <div hidden={step !== 0}>
            <TripDetailsStep
              formId={FORM_IDS[0]}
              locked={trip !== undefined}
              onSave={saveDetails}
            />
          </div>
          <div hidden={step !== 1}>
            {step >= 1 &&
              (preferences.data ? (
                <PreferenceForm
                  formId={FORM_IDS[1]}
                  preferences={preferences.data}
                  onSave={savePreferenceFields}
                />
              ) : (
                loadingPreferences
              ))}
          </div>
          <div hidden={step !== 2}>
            {step >= 2 &&
              trip &&
              (preferences.data ? (
                <PlacesStep
                  formId={FORM_IDS[2]}
                  destinationId={trip.destination_id}
                  initial={preferences.data.must_visit_places}
                  effect={effectsOf(preferences.data).must_visit_place_ids}
                  onSave={savePlaces}
                />
              ) : (
                loadingPreferences
              ))}
          </div>
          <div hidden={step !== REVIEW}>
            {step === REVIEW && trip && preferences.data && (
              <ReviewStep
                trip={trip}
                preferences={preferences.data}
                onEdit={goTo}
              />
            )}
          </div>
        </div>

        {(saveError ?? preferences.error) && (
          <div className="mt-6">
            <ErrorState
              title="Your changes could not be saved"
              error={saveError ?? (preferences.error as ApiError)}
            />
          </div>
        )}

        <div className="sticky bottom-16 z-10 -mx-4 mt-8 flex items-center justify-between gap-3 border-t bg-card px-4 py-3 md:static md:mx-0 md:mt-10 md:border-0 md:p-0">
          <Button
            type="button"
            variant="outline"
            size="lg"
            onClick={() => goTo(step - 1)}
            disabled={step === 0 || saving}
          >
            <ArrowLeft aria-hidden="true" />
            Back
          </Button>
          {step === REVIEW && trip ? (
            <Button asChild size="lg">
              <Link href={`/trips/${trip.id}/generate`}>
                Generate itinerary
              </Link>
            </Button>
          ) : (
            <Button
              type="submit"
              form={FORM_IDS[step]}
              size="lg"
              disabled={saving}
            >
              {saving ? (
                <>
                  <Loader2
                    aria-hidden="true"
                    className="motion-safe:animate-spin"
                  />
                  Saving…
                </>
              ) : (
                <>
                  Next
                  <ArrowRight aria-hidden="true" />
                </>
              )}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
