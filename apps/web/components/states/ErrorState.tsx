"use client";

import { OctagonX } from "lucide-react";

import { Button } from "@/components/ui/button";

/** The fields ErrorState reads; the ApiError of lib/api/errors.ts (IMP-214) satisfies it. */
export type ErrorStateError = {
  message: string;
  requestId?: string | null;
};

export type ErrorStateProps = {
  error: ErrorStateError;
  title?: string;
  onRetry?: () => void;
  retryLabel?: string;
};

/** Shown when a request failed (§7.6): the message, the request ID when the API sent one, and retry. */
export function ErrorState({
  error,
  title = "Something went wrong",
  onRetry,
  retryLabel = "Try again",
}: ErrorStateProps) {
  return (
    <section
      role="alert"
      className="flex flex-col items-center gap-3 rounded-xl border border-destructive/40 bg-card px-4 py-10 text-center"
    >
      <OctagonX aria-hidden="true" className="size-6 text-destructive" />
      <h2 className="font-heading text-lg font-semibold text-card-foreground">
        {title}
      </h2>
      <p className="max-w-prose text-sm text-card-foreground">
        {error.message}
      </p>
      {error.requestId && (
        <p className="text-xs text-muted-foreground">
          Request ID:{" "}
          <span className="font-mono break-all select-all">
            {error.requestId}
          </span>
        </p>
      )}
      {onRetry && (
        <Button className="mt-2" variant="outline" onClick={onRetry}>
          {retryLabel}
        </Button>
      )}
    </section>
  );
}
