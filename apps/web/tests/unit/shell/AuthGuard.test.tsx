import type { Session } from "@supabase/supabase-js";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { AuthGuard, useAuth } from "@/components/shell/AuthGuard";

// Supabase is never reached: the browser client is replaced by this fake (no NEXT_PUBLIC_* needed).
const fake = vi.hoisted(() => {
  type Listener = (event: string, session: unknown) => void;
  const state = {
    listener: undefined as Listener | undefined,
    getSession: vi.fn(),
    signOut: vi.fn(),
    unsubscribe: vi.fn(),
  };
  return state;
});

vi.mock("@/lib/auth/supabase", () => ({
  getSupabase: () => ({
    auth: {
      getSession: fake.getSession,
      signOut: fake.signOut,
      onAuthStateChange: (listener: (event: string, s: unknown) => void) => {
        fake.listener = listener;
        return { data: { subscription: { unsubscribe: fake.unsubscribe } } };
      },
    },
  }),
}));

const navigation = vi.hoisted(() => ({
  pathname: "/dashboard",
  replace: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  usePathname: () => navigation.pathname,
  useRouter: () => ({ replace: navigation.replace }),
}));

const SESSION = {
  access_token: "test-access-token",
  user: { id: "user-1", email: "traveller@example.test" },
} as unknown as Session;

function renderGuard(children: ReactNode, queryClient = new QueryClient()) {
  render(
    <QueryClientProvider client={queryClient}>
      <AuthGuard>{children}</AuthGuard>
    </QueryClientProvider>,
  );
  return queryClient;
}

function SignOutButton() {
  const auth = useAuth();
  return (
    <button type="button" onClick={() => void auth?.signOut()}>
      Sign out as {auth?.user.email}
    </button>
  );
}

describe("AuthGuard (§7.2, TC-054)", () => {
  beforeEach(() => {
    navigation.pathname = "/dashboard";
    navigation.replace.mockReset();
    fake.getSession.mockReset();
    fake.signOut.mockReset().mockImplementation(async () => {
      fake.listener?.("SIGNED_OUT", null);
      return { error: null };
    });
    fake.listener = undefined;
    window.history.replaceState(null, "", "/");
  });

  it("shows the loading skeleton and no page content while the session loads", () => {
    fake.getSession.mockReturnValue(new Promise(() => {}));
    renderGuard(<p>Private trip list</p>);

    expect(screen.getByRole("status")).toHaveTextContent(
      "Checking your session",
    );
    expect(screen.queryByText("Private trip list")).not.toBeInTheDocument();
    expect(navigation.replace).not.toHaveBeenCalled();
  });

  it("redirects a signed-out visitor of an (app) route to /sign-in with next", async () => {
    navigation.pathname = "/trips/abc/itinerary";
    window.history.replaceState(null, "", "/trips/abc/itinerary?day=2");
    fake.getSession.mockResolvedValue({ data: { session: null } });
    renderGuard(<p>Private trip list</p>);

    await waitFor(() =>
      expect(navigation.replace).toHaveBeenCalledWith(
        "/sign-in?next=%2Ftrips%2Fabc%2Fitinerary%3Fday%3D2",
      ),
    );
    expect(screen.queryByText("Private trip list")).not.toBeInTheDocument();
  });

  it("renders the page for a signed-in user", async () => {
    fake.getSession.mockResolvedValue({ data: { session: SESSION } });
    renderGuard(<p>Private trip list</p>);

    expect(await screen.findByText("Private trip list")).toBeInTheDocument();
    expect(navigation.replace).not.toHaveBeenCalled();
  });

  it("hides the page and redirects when the session ends in another tab", async () => {
    fake.getSession.mockResolvedValue({ data: { session: SESSION } });
    renderGuard(<p>Private trip list</p>);
    await screen.findByText("Private trip list");

    act(() => fake.listener?.("SIGNED_OUT", null));

    await waitFor(() =>
      expect(navigation.replace).toHaveBeenCalledWith(
        "/sign-in?next=%2Fdashboard",
      ),
    );
    expect(screen.queryByText("Private trip list")).not.toBeInTheDocument();
  });

  it("signs out, clears the query cache and replaces history with /sign-in (FR-002 AC3)", async () => {
    fake.getSession.mockResolvedValue({ data: { session: SESSION } });
    const queryClient = new QueryClient();
    queryClient.setQueryData(["trips"], [{ id: "trip-1", title: "Private" }]);
    renderGuard(<SignOutButton />, queryClient);

    await userEvent.click(
      await screen.findByRole("button", {
        name: "Sign out as traveller@example.test",
      }),
    );

    await waitFor(() =>
      expect(navigation.replace).toHaveBeenCalledWith("/sign-in"),
    );
    expect(fake.signOut).toHaveBeenCalledTimes(1);
    expect(queryClient.getQueryData(["trips"])).toBeUndefined();
    // Sign-out goes to /sign-in itself; the guard adds no `next` pointing back at the private page.
    expect(navigation.replace).toHaveBeenCalledTimes(1);
  });
});
