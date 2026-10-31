import { AuthApiError } from "@supabase/supabase-js";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { MESSAGES } from "@/components/auth/messages";
import { SignInForm } from "@/components/auth/SignInForm";
import { SignUpForm } from "@/components/auth/SignUpForm";

// The browser client is faked: no Supabase and no NEXT_PUBLIC_* values are needed.
const auth = vi.hoisted(() => ({
  signUp: vi.fn(),
  signInWithPassword: vi.fn(),
  getSession: vi.fn(),
}));
vi.mock("@/lib/auth/supabase", () => ({ getSupabase: () => ({ auth }) }));

const router = vi.hoisted(() => ({ replace: vi.fn() }));
vi.mock("next/navigation", () => ({ useRouter: () => router }));

const SESSION = { access_token: "t", user: { id: "u" } };

function apiError(message: string, status: number, code: string) {
  return new AuthApiError(message, status, code);
}

async function fill(email: string, password: string) {
  const user = userEvent.setup();
  if (email) await user.type(screen.getByLabelText("Email"), email);
  if (password) await user.type(screen.getByLabelText("Password"), password);
  return user;
}

beforeEach(() => {
  vi.clearAllMocks();
  auth.getSession.mockResolvedValue({ data: { session: null } });
});

describe("SignUpForm (FR-001, TC-051 to TC-053)", () => {
  it("shows an error under each empty field, tied to the input, and sends nothing", async () => {
    render(<SignUpForm next="/dashboard" />);
    await userEvent.click(
      screen.getByRole("button", { name: "Create account" }),
    );

    const email = screen.getByLabelText("Email");
    const password = screen.getByLabelText("Password");
    expect(email).toHaveAttribute("aria-invalid", "true");
    expect(email).toHaveAccessibleDescription("Enter your email address");
    expect(password).toHaveAccessibleDescription(
      "Enter a password At least 8 characters.",
    );
    expect(auth.signUp).not.toHaveBeenCalled();
  });

  it("rejects a weak password on its field", async () => {
    render(<SignUpForm next="/dashboard" />);
    const user = await fill("new@example.test", "short");
    await user.click(screen.getByRole("button", { name: "Create account" }));

    expect(screen.getByLabelText("Password")).toHaveAccessibleDescription(
      "Use at least 8 characters At least 8 characters.",
    );
    expect(auth.signUp).not.toHaveBeenCalled();
  });

  it("continues signed in when the project needs no confirmation", async () => {
    auth.signUp.mockResolvedValue({ data: { session: SESSION }, error: null });
    render(<SignUpForm next="/trips/abc" />);
    const user = await fill("new@example.test", "a-long-password");
    await user.click(screen.getByRole("button", { name: "Create account" }));

    expect(auth.signUp).toHaveBeenCalledWith({
      email: "new@example.test",
      password: "a-long-password",
      options: {
        emailRedirectTo:
          "http://localhost:3000/auth/callback?next=%2Ftrips%2Fabc",
      },
    });
    expect(router.replace).toHaveBeenCalledWith("/trips/abc");
  });

  it("shows the same neutral notice for a new address awaiting confirmation and an existing one", async () => {
    auth.signUp.mockResolvedValueOnce({
      data: { session: null, user: { id: "u" } },
      error: null,
    });
    const first = render(<SignUpForm next="/dashboard" />);
    let user = await fill("new@example.test", "a-long-password");
    await user.click(screen.getByRole("button", { name: "Create account" }));
    const newAddressNotice = (await screen.findByRole("status")).textContent;
    first.unmount();

    auth.signUp.mockResolvedValueOnce({
      data: { session: null, user: null },
      error: apiError("User already registered", 422, "user_already_exists"),
    });
    render(<SignUpForm next="/dashboard" />);
    user = await fill("taken@example.test", "a-long-password");
    await user.click(screen.getByRole("button", { name: "Create account" }));
    const existingNotice = (await screen.findByRole("status")).textContent;

    expect(newAddressNotice).toBe(MESSAGES.signUpNotice);
    expect(existingNotice).toBe(newAddressNotice);
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    expect(router.replace).not.toHaveBeenCalled();
  });

  it("says Try again later when Supabase rate-limits email sending", async () => {
    auth.signUp.mockResolvedValue({
      data: { session: null, user: null },
      error: apiError(
        "Email rate limit exceeded",
        429,
        "over_email_send_rate_limit",
      ),
    });
    render(<SignUpForm next="/dashboard" />);
    const user = await fill("new@example.test", "a-long-password");
    await user.click(screen.getByRole("button", { name: "Create account" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Try again later",
    );
  });

  it("has a keyboard-reachable show or hide password toggle", async () => {
    render(<SignUpForm next="/dashboard" />);
    const user = userEvent.setup();
    const password = screen.getByLabelText("Password");
    const toggle = screen.getByRole("button", { name: "Show password" });
    expect(password).toHaveAttribute("type", "password");

    toggle.focus();
    await user.keyboard("{Enter}");
    expect(password).toHaveAttribute("type", "text");
    expect(toggle).toHaveAttribute("aria-pressed", "true");
  });
});

describe("SignInForm (FR-002, TC-054)", () => {
  it("signs in and goes to next", async () => {
    auth.signInWithPassword.mockResolvedValue({
      data: { session: SESSION },
      error: null,
    });
    render(<SignInForm next="/dashboard" />);
    const user = await fill("traveller@example.test", "a-long-password");
    await user.click(screen.getByRole("button", { name: "Sign in" }));

    expect(router.replace).toHaveBeenCalledWith("/dashboard");
  });

  it("says only that the email or password is incorrect", async () => {
    auth.signInWithPassword.mockResolvedValue({
      data: { session: null },
      error: apiError("Invalid login credentials", 400, "invalid_credentials"),
    });
    render(<SignInForm next="/dashboard" />);
    const user = await fill("traveller@example.test", "wrong-password");
    await user.click(screen.getByRole("button", { name: "Sign in" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Email or password is incorrect.",
    );
    expect(screen.getByLabelText("Email")).not.toHaveAttribute("aria-invalid");
    expect(router.replace).not.toHaveBeenCalled();
  });

  it("says Try again later when sign-in is rate-limited", async () => {
    auth.signInWithPassword.mockResolvedValue({
      data: { session: null },
      error: apiError(
        "Request rate limit reached",
        429,
        "over_request_rate_limit",
      ),
    });
    render(<SignInForm next="/dashboard" />);
    const user = await fill("traveller@example.test", "a-long-password");
    await user.click(screen.getByRole("button", { name: "Sign in" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Try again later",
    );
  });

  it("sends a user who is already signed in to /dashboard (§7.2)", async () => {
    auth.getSession.mockResolvedValue({ data: { session: SESSION } });
    render(<SignInForm next="/trips/abc" />);

    await vi.waitFor(() =>
      expect(router.replace).toHaveBeenCalledWith("/dashboard"),
    );
  });

  it("explains a failed confirmation link", () => {
    render(<SignInForm next="/dashboard" confirmationFailed />);
    expect(screen.getByRole("alert")).toHaveTextContent(
      MESSAGES.confirmationFailed,
    );
  });
});
