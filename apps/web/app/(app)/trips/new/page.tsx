import type { Metadata } from "next";

import { TripWizard } from "@/components/trips/TripWizard";

export const metadata: Metadata = {
  title: "Plan a new trip · AI Travel Planner",
};

// Trip wizard (§7.5.4). Thin server component (§7.1); the wizard loads its data in the browser.
export default function NewTripPage() {
  return <TripWizard />;
}
