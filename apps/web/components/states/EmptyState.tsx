import type { ReactNode } from "react";

export type EmptyStateProps = {
  title: string;
  description?: string;
  /** The next step, usually a Button or a Button-styled link. */
  action?: ReactNode;
  /** Heading level of the title within the page outline. */
  headingLevel?: 2 | 3;
};

/** Shown when a list or page has nothing to display yet (§7.6). */
export function EmptyState({
  title,
  description,
  action,
  headingLevel = 2,
}: EmptyStateProps) {
  const Heading = headingLevel === 2 ? "h2" : "h3";

  return (
    <section className="flex flex-col items-center gap-3 rounded-xl border border-dashed bg-card px-4 py-10 text-center">
      <Heading className="font-heading text-lg font-semibold text-card-foreground">
        {title}
      </Heading>
      {description && (
        <p className="max-w-prose text-sm text-muted-foreground">
          {description}
        </p>
      )}
      {action && (
        <div className="mt-2 flex flex-wrap justify-center gap-2">{action}</div>
      )}
    </section>
  );
}
