import type { ReactNode } from "react";

import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";
import { EFFECT_LABELS, type Effect } from "@/lib/validation/trip";

/** Classes of a native select or textarea, matching the Input of components/ui. */
export const CONTROL_CLASS =
  "min-h-touch w-full min-w-0 rounded-lg border border-input bg-background px-3 py-2 text-base outline-none transition-colors focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:cursor-not-allowed disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-3 aria-invalid:ring-destructive/20 md:text-sm";

type Frame = {
  id: string;
  error?: string;
  hint?: string;
  /** What the field does in planning, shown once API-15 reports it (FR-009). */
  effect?: Effect;
  aside?: ReactNode;
};

/** The ids a control's aria-describedby lists: its hint and, when shown, its error. */
export function describedBy({ id, error, hint }: Frame): string | undefined {
  const ids = [hint && `${id}-hint`, error && `${id}-error`].filter(Boolean);
  return ids.length > 0 ? ids.join(" ") : undefined;
}

export function EffectBadge({ effect }: { effect: Effect }) {
  return (
    <span className="inline-flex items-center rounded-full bg-secondary px-2 py-0.5 text-xs font-medium text-secondary-foreground">
      {EFFECT_LABELS[effect]}
    </span>
  );
}

function Messages({ id, error, hint }: Frame) {
  return (
    <>
      {hint && (
        <p id={`${id}-hint`} className="text-sm text-muted-foreground">
          {hint}
        </p>
      )}
      <p
        id={`${id}-error`}
        aria-live="polite"
        className="text-sm font-medium text-destructive empty:hidden"
      >
        {error}
      </p>
    </>
  );
}

/** One labelled control; render-prop children receive the aria-describedby value. */
export function Field({
  label,
  className,
  children,
  ...frame
}: Frame & {
  label: string;
  className?: string;
  children: (describedBy: string | undefined) => ReactNode;
}) {
  return (
    <div className={cn("flex flex-col gap-2", className)}>
      <div className="flex min-h-6 flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Label htmlFor={frame.id}>{label}</Label>
          {frame.effect && <EffectBadge effect={frame.effect} />}
        </div>
        {frame.aside}
      </div>
      {children(describedBy(frame))}
      <Messages {...frame} />
    </div>
  );
}

/** A group of controls (chips, segmented choices) under one legend. */
export function FieldSet({
  legend,
  className,
  children,
  ...frame
}: Frame & { legend: string; className?: string; children: ReactNode }) {
  return (
    <fieldset
      className={cn("flex flex-col gap-2", className)}
      aria-describedby={describedBy(frame)}
    >
      <legend className="mb-2 flex items-center gap-2 text-sm font-medium">
        {legend}
        {frame.effect && <EffectBadge effect={frame.effect} />}
      </legend>
      {children}
      <Messages {...frame} />
    </fieldset>
  );
}
