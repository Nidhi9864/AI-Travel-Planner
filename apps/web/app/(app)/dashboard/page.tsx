import Link from "next/link";

import { EmptyState } from "@/components/states/EmptyState";
import { Button } from "@/components/ui/button";

// Placeholder: only the empty state of §7.5.3. The trip list and its actions arrive in IMP-212.
export default function DashboardPage() {
  return (
    <div className="flex flex-col gap-6">
      <h1 className="font-heading text-2xl font-semibold text-foreground">
        Your trips
      </h1>
      <EmptyState
        title="No trips yet"
        description="Start with a destination, your dates and a budget."
        action={
          <Button asChild>
            <Link href="/trips/new">Create a trip</Link>
          </Button>
        }
      />
    </div>
  );
}
