import { Skeleton } from "@/components/ui/skeleton";

export type LoadingSkeletonProps = {
  /** `cards` for card grids, `list` for rows, `text` for paragraphs. */
  shape?: "cards" | "list" | "text";
  count?: number;
  /** Read by screen readers instead of the placeholder blocks. */
  label?: string;
};

/** Placeholder blocks shown while data loads (§7.6); announced once as a polite status. */
export function LoadingSkeleton({
  shape = "list",
  count = 3,
  label = "Loading",
}: LoadingSkeletonProps) {
  const blocks = Array.from({ length: count }, (_, index) => index);

  return (
    <div role="status" aria-live="polite" aria-busy="true">
      <span className="sr-only">{label}</span>
      {shape === "cards" && (
        <div
          aria-hidden="true"
          className="grid grid-cols-1 gap-4 lg:grid-cols-3"
        >
          {blocks.map((index) => (
            <Skeleton key={index} className="h-36 w-full rounded-xl" />
          ))}
        </div>
      )}
      {shape === "list" && (
        <div aria-hidden="true" className="flex flex-col gap-3">
          {blocks.map((index) => (
            <Skeleton key={index} className="h-14 w-full" />
          ))}
        </div>
      )}
      {shape === "text" && (
        <div aria-hidden="true" className="flex flex-col gap-2">
          {blocks.map((index) => (
            <Skeleton key={index} className="h-4 w-full last:w-2/3" />
          ))}
        </div>
      )}
    </div>
  );
}
