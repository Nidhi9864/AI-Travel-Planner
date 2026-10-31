import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { LoadingSkeleton } from "@/components/states/LoadingSkeleton";

describe("LoadingSkeleton", () => {
  it("is a busy status with a readable label", () => {
    render(<LoadingSkeleton shape="cards" count={2} label="Loading trips" />);

    const status = screen.getByRole("status");
    expect(status).toHaveAttribute("aria-busy", "true");
    expect(status).toHaveTextContent("Loading trips");
  });
});
