"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Controller, useForm, useWatch } from "react-hook-form";

import { ChipMultiSelect } from "@/components/trips/ChipMultiSelect";
import {
  CONTROL_CLASS,
  EffectBadge,
  Field,
  FieldSet,
} from "@/components/trips/Field";
import { SegmentedChoice } from "@/components/trips/SegmentedChoice";
import type { ErrorDetail } from "@/lib/api/client";
import type { components } from "@/lib/api/schema";
import { cn } from "@/lib/utils";
import {
  ACCOMMODATION_LABELS,
  BUDGET_PRIORITY_LABELS,
  type Effect,
  fieldErrors,
  INTEREST_LABELS,
  NOTES_MAX_CHARS,
  PACE_LABELS,
  preferencesSchema,
  type PreferencesValues,
  TRANSPORT_LABELS,
} from "@/lib/validation/trip";

type PreferencesOut = components["schemas"]["PreferencesOut"];

const FIELDS = [
  "interests",
  "pace",
  "budget_priority",
  "transport_pref",
  "accommodation_type",
  "step_free_required",
  "notes",
] as const;

/** Each field's effect from API-15, shown only once the preferences have been saved (FR-009). */
export function effectsOf(preferences: PreferencesOut): Record<string, Effect> {
  if (!preferences.saved) return {};
  return Object.fromEntries(
    preferences.effects.map(({ field, effect }) => [field, effect]),
  );
}

/**
 * Step 2 (§7.5.4, §7.3 preferences): interests, pace, budget priority, transport, accommodation
 * type, step-free access and notes. The form starts from API-15, which gives the defaults before
 * anything is saved.
 */
export function PreferenceForm({
  formId,
  preferences,
  onSave,
}: {
  formId: string;
  preferences: PreferencesOut;
  onSave: (values: PreferencesValues) => Promise<ErrorDetail[]>;
}) {
  const {
    register,
    control,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<PreferencesValues>({
    resolver: zodResolver(preferencesSchema),
    defaultValues: {
      interests: preferences.interests,
      pace: preferences.pace,
      budget_priority: preferences.budget_priority,
      transport_pref: preferences.transport_pref,
      accommodation_type: preferences.accommodation_type,
      step_free_required: preferences.step_free_required,
      notes: preferences.notes ?? "",
    },
  });
  const effects = effectsOf(preferences);
  const notesLength = useWatch({ control, name: "notes" }).length;

  async function submit(values: PreferencesValues) {
    for (const { field, message } of fieldErrors(
      await onSave(values),
      FIELDS,
    )) {
      setError(field, { message });
    }
  }

  return (
    <form
      id={formId}
      noValidate
      onSubmit={handleSubmit(submit)}
      aria-label="Preferences"
      className="grid gap-8"
    >
      {errors.root && (
        <p role="alert" className="text-sm font-medium text-destructive">
          {errors.root.message}
        </p>
      )}
      <FieldSet
        id="interests"
        legend="Interests"
        hint="Pick everything that sounds good."
        effect={effects.interests}
        error={errors.interests?.message}
      >
        <Controller
          control={control}
          name="interests"
          render={({ field }) => (
            <ChipMultiSelect
              labels={INTEREST_LABELS}
              value={field.value}
              onChange={field.onChange}
            />
          )}
        />
      </FieldSet>

      <FieldSet id="pace" legend="Pace" effect={effects.pace}>
        <Controller
          control={control}
          name="pace"
          render={({ field }) => (
            <SegmentedChoice
              name="pace"
              labels={PACE_LABELS}
              value={field.value}
              onChange={field.onChange}
            />
          )}
        />
      </FieldSet>

      <FieldSet
        id="budget-priority"
        legend="Budget priority"
        effect={effects.budget_priority}
      >
        <Controller
          control={control}
          name="budget_priority"
          render={({ field }) => (
            <SegmentedChoice
              name="budget_priority"
              labels={BUDGET_PRIORITY_LABELS}
              value={field.value}
              onChange={field.onChange}
            />
          )}
        />
      </FieldSet>

      <FieldSet
        id="transport"
        legend="Getting around"
        effect={effects.transport_pref}
      >
        <Controller
          control={control}
          name="transport_pref"
          render={({ field }) => (
            <SegmentedChoice
              name="transport_pref"
              labels={TRANSPORT_LABELS}
              value={field.value}
              onChange={field.onChange}
            />
          )}
        />
      </FieldSet>

      <Field
        id="accommodation-type"
        label="Accommodation type"
        effect={effects.accommodation_type}
        error={errors.accommodation_type?.message}
      >
        {(describedBy) => (
          <select
            id="accommodation-type"
            className={CONTROL_CLASS}
            aria-describedby={describedBy}
            {...register("accommodation_type")}
          >
            {Object.entries(ACCOMMODATION_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        )}
      </Field>

      <div className="flex min-h-touch items-center gap-3">
        <input
          id="step-free"
          type="checkbox"
          className="size-5 accent-primary"
          {...register("step_free_required")}
        />
        <label
          htmlFor="step-free"
          className="flex-1 cursor-pointer py-3 text-sm font-medium"
        >
          I need step-free access
        </label>
        {effects.step_free_required && (
          <EffectBadge effect={effects.step_free_required} />
        )}
      </div>

      <Field
        id="notes"
        label="Notes"
        hint="Do not enter personal details."
        effect={effects.notes}
        error={errors.notes?.message}
        aside={
          <span
            className={cn(
              "text-sm tabular-nums",
              notesLength > NOTES_MAX_CHARS
                ? "font-medium text-destructive"
                : "text-muted-foreground",
            )}
          >
            {notesLength}/{NOTES_MAX_CHARS}
          </span>
        }
      >
        {(describedBy) => (
          <textarea
            id="notes"
            rows={4}
            className={CONTROL_CLASS}
            aria-describedby={describedBy}
            aria-invalid={errors.notes ? true : undefined}
            {...register("notes")}
          />
        )}
      </Field>
    </form>
  );
}
