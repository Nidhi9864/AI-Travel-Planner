import type { AuthError } from "@supabase/supabase-js";

/**
 * User-facing texts of the auth screens (§7.3, §7.5.2) and the mapping from Supabase Auth errors.
 * Nothing here reveals whether an email address has an account (FR-001 AC2).
 */
export const MESSAGES = {
  /** Shown after sign-up whenever no session starts: a new address and an existing one alike. */
  signUpNotice:
    "Check your email to finish creating your account. If you already have an account, try signing in instead.",
  signInFailed: "Email or password is incorrect.",
  rateLimited: "Too many attempts. Try again later.",
  offline:
    "Could not reach the sign-in service. Check your connection and try again.",
  unexpected: "Something went wrong. Try again later.",
  weakPassword:
    "Choose a stronger password: longer, and not one that is easy to guess.",
  confirmationFailed:
    "That confirmation link is invalid or has expired. Sign in, or create your account again to get a new link.",
} as const;

const RATE_LIMIT_CODES = new Set([
  "over_request_rate_limit",
  "over_email_send_rate_limit",
  "over_sms_send_rate_limit",
]);
const EXISTING_ACCOUNT_CODES = new Set(["user_already_exists", "email_exists"]);

export type AuthFailure =
  "rate_limited" | "offline" | "existing_account" | "weak_password" | "other";

/** Classify a Supabase Auth error; the screens decide what each class shows. */
export function classifyAuthError(error: AuthError): AuthFailure {
  if (
    error.status === 429 ||
    (error.code && RATE_LIMIT_CODES.has(error.code))
  ) {
    return "rate_limited";
  }
  // supabase-js reports a failed request (no response) as AuthRetryableFetchError with status 0.
  if (error.name === "AuthRetryableFetchError" || error.status === 0) {
    return "offline";
  }
  if (error.code && EXISTING_ACCOUNT_CODES.has(error.code)) {
    return "existing_account";
  }
  if (error.code === "weak_password") {
    return "weak_password";
  }
  return "other";
}
