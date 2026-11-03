import { cn } from "@/lib/utils";

/** A single choice shown as segments: native radio inputs, so arrow keys move the choice. */
export function SegmentedChoice<T extends string>({
  name,
  labels,
  value,
  onChange,
}: {
  name: string;
  labels: Record<T, string>;
  value: T;
  onChange: (value: T) => void;
}) {
  const options = Object.entries(labels) as [T, string][];

  return (
    <div className="grid grid-cols-3 gap-1 rounded-lg border border-input bg-muted p-1">
      {options.map(([option, label]) => (
        <label
          key={option}
          className={cn(
            "flex min-h-touch cursor-pointer items-center justify-center rounded-md px-2 text-center text-sm font-medium transition-colors has-[:focus-visible]:ring-3 has-[:focus-visible]:ring-ring has-[:focus-visible]:ring-offset-1",
            option === value
              ? "bg-background text-foreground shadow-sm"
              : "text-muted-foreground hover:bg-background/70 hover:text-foreground",
          )}
        >
          <input
            type="radio"
            name={name}
            value={option}
            checked={option === value}
            onChange={() => onChange(option)}
            className="sr-only"
          />
          {label}
        </label>
      ))}
    </div>
  );
}
