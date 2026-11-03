import { Check } from "lucide-react";

import { cn } from "@/lib/utils";

/** Progress through the wizard: "Step 2 of 4" on phones, the named steps from 768 px (§7.5.4). */
export function TripStepper({
  steps,
  current,
}: {
  steps: readonly string[];
  current: number;
}) {
  return (
    <>
      <p className="text-sm font-medium text-muted-foreground md:hidden">
        Step {current + 1} of {steps.length}
      </p>
      <ol aria-label="Progress" className="hidden items-center md:flex">
        {steps.map((name, index) => {
          const complete = index < current;
          const active = index === current;
          return (
            <li
              key={name}
              aria-current={active ? "step" : undefined}
              className={cn(
                "flex items-center",
                index < steps.length - 1 && "flex-1",
              )}
            >
              <span className="flex items-center gap-3">
                <span
                  className={cn(
                    "flex size-8 shrink-0 items-center justify-center rounded-full border text-sm font-semibold",
                    complete &&
                      "border-primary bg-primary text-primary-foreground",
                    active &&
                      "border-primary bg-background text-foreground ring-4 ring-muted",
                    !complete &&
                      !active &&
                      "border-input bg-background text-muted-foreground",
                  )}
                >
                  {complete ? (
                    <Check aria-label="Completed" className="size-4" />
                  ) : (
                    index + 1
                  )}
                </span>
                <span
                  className={cn(
                    "text-sm whitespace-nowrap",
                    active
                      ? "font-semibold text-foreground"
                      : "font-medium text-muted-foreground",
                  )}
                >
                  {name}
                </span>
              </span>
              {index < steps.length - 1 && (
                <span
                  aria-hidden="true"
                  className="mx-4 h-px flex-1 bg-border"
                />
              )}
            </li>
          );
        })}
      </ol>
    </>
  );
}
