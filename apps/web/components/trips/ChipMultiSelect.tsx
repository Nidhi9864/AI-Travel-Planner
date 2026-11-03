import { Check } from "lucide-react";

import { cn } from "@/lib/utils";

/** Toggle chips for a multi-choice field; each chip is a 44 px button with aria-pressed. */
export function ChipMultiSelect<T extends string>({
  labels,
  value,
  onChange,
}: {
  labels: Record<T, string>;
  value: T[];
  onChange: (value: T[]) => void;
}) {
  const options = Object.entries(labels) as [T, string][];
  const toggle = (option: T) =>
    onChange(
      value.includes(option)
        ? value.filter((item) => item !== option)
        : [...value, option],
    );

  return (
    <div className="flex flex-wrap gap-2">
      {options.map(([option, label]) => {
        const selected = value.includes(option);
        return (
          <button
            key={option}
            type="button"
            aria-pressed={selected}
            onClick={() => toggle(option)}
            className={cn(
              "inline-flex min-h-touch items-center gap-2 rounded-full border px-4 text-sm font-medium transition-colors outline-none focus-visible:ring-3 focus-visible:ring-ring focus-visible:ring-offset-2",
              selected
                ? "border-primary bg-primary text-primary-foreground hover:bg-primary-hover"
                : "border-input bg-background text-foreground hover:bg-muted",
            )}
          >
            {selected && <Check aria-hidden="true" className="size-4" />}
            {label}
          </button>
        );
      })}
    </div>
  );
}
