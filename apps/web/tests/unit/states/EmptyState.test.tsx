import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { EmptyState } from "@/components/states/EmptyState";

describe("EmptyState", () => {
  it("renders its title, description and action", () => {
    render(
      <EmptyState
        title="No trips yet"
        description="Start with a destination."
        action={<button type="button">Create a trip</button>}
      />,
    );

    expect(
      screen.getByRole("heading", { level: 2, name: "No trips yet" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Start with a destination.")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Create a trip" }),
    ).toBeInTheDocument();
  });
});
