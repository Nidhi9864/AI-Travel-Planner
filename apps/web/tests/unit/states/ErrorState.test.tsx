import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ErrorState } from "@/components/states/ErrorState";

describe("ErrorState", () => {
  it("shows the message and request ID and retries", async () => {
    const onRetry = vi.fn();
    render(
      <ErrorState
        error={{
          message: "The service is unavailable.",
          requestId: "3f1c2a9e-0000-4000-8000-000000000001",
        }}
        onRetry={onRetry}
      />,
    );

    const alert = screen.getByRole("alert");
    expect(alert).toHaveTextContent("The service is unavailable.");
    expect(alert).toHaveTextContent(
      "Request ID: 3f1c2a9e-0000-4000-8000-000000000001",
    );

    await userEvent.click(screen.getByRole("button", { name: "Try again" }));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("leaves out the request ID and retry when they are not given", () => {
    render(<ErrorState error={{ message: "Network error." }} />);

    expect(screen.getByRole("alert")).not.toHaveTextContent("Request ID");
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });
});
