import Link from "next/link";

import { AppShell } from "@/components/shell/AppShell";
import { Button } from "@/components/ui/button";

const POINTS = [
  {
    title: "Day-by-day and costed",
    text: "Each day lists its places with start times, travel gaps and an estimated cost.",
  },
  {
    title: "Checked by the app",
    text: "An AI model proposes the order from a shortlist of curated places; the app checks every place and recalculates every time and price itself.",
  },
  {
    title: "Yours to edit",
    text: "Move, add or remove places and the times and totals are worked out again.",
  },
];

// Landing page (§7.5.1). Public, no API call.
export default function LandingPage() {
  return (
    <AppShell variant="public">
      <section className="flex flex-col gap-6 py-6 md:py-12">
        <h1 className="max-w-3xl font-heading text-3xl font-semibold tracking-tight text-foreground md:text-4xl">
          Describe a trip and get a day-by-day plan you can edit
        </h1>
        <p className="max-w-2xl text-lg text-muted-foreground">
          Tell us where you are going, your dates, who is travelling, your
          budget and what you enjoy. You get an itinerary with times, travel
          between stops and costs for the whole group.
        </p>
        <div className="flex flex-col gap-3 sm:flex-row">
          <Button asChild size="lg">
            <Link href="/sign-up">Create an account</Link>
          </Button>
          <Button asChild size="lg" variant="outline">
            <Link href="/sign-in">Sign in</Link>
          </Button>
        </div>
        <p className="max-w-2xl rounded-lg border bg-muted px-4 py-3 text-sm text-foreground">
          Plans are drafts built from curated sample data. Prices, opening hours
          and travel times are estimates and are labelled as such; check them
          before you travel.
        </p>
      </section>

      <section aria-labelledby="how-it-works" className="py-6">
        <h2
          id="how-it-works"
          className="font-heading text-xl font-semibold text-foreground"
        >
          How it works
        </h2>
        <ul className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-3">
          {POINTS.map((point) => (
            <li key={point.title} className="rounded-xl border bg-card p-4">
              <h3 className="font-heading text-base font-semibold text-card-foreground">
                {point.title}
              </h3>
              <p className="mt-1 text-sm text-muted-foreground">{point.text}</p>
            </li>
          ))}
        </ul>
      </section>
    </AppShell>
  );
}
