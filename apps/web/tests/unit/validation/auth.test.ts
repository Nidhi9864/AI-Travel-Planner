import { describe, expect, it } from "vitest";

import { signInSchema, signUpSchema } from "@/lib/validation/auth";

type Result = {
  error?: { issues: { path: PropertyKey[]; message: string }[] };
};

/** The first message for each field, as react-hook-form shows it (criteriaMode "firstError"). */
function messages(result: Result) {
  const first: Record<string, string> = {};
  for (const issue of result.error?.issues ?? []) {
    first[String(issue.path[0])] ??= issue.message;
  }
  return first;
}

// §7.3 sign-up and sign-in schemas (FR-001 AC3, TC-053).
describe("signUpSchema", () => {
  it("accepts a valid email and an 8-character password, trimming the email", () => {
    const result = signUpSchema.safeParse({
      email: "  traveller@example.test ",
      password: "12345678",
    });
    expect(result.success).toBe(true);
    expect(result.data?.email).toBe("traveller@example.test");
  });

  it("rejects empty fields with a message per field", () => {
    const result = signUpSchema.safeParse({ email: "", password: "" });
    expect(result.success).toBe(false);
    expect(messages(result)).toEqual({
      email: "Enter your email address",
      password: "Enter a password",
    });
  });

  it("rejects a malformed email and a password under 8 characters", () => {
    const result = signUpSchema.safeParse({
      email: "not-an-email",
      password: "1234567",
    });
    expect(messages(result)).toEqual({
      email: "Enter a valid email address, like name@example.com",
      password: "Use at least 8 characters",
    });
  });
});

describe("signInSchema", () => {
  it("only requires a password, so it never hints at the password rules", () => {
    expect(
      signInSchema.safeParse({ email: "a@example.test", password: "x" })
        .success,
    ).toBe(true);
    expect(
      messages(
        signInSchema.safeParse({ email: "a@example.test", password: "" }),
      ),
    ).toEqual({ password: "Enter your password" });
  });

  it("checks the email format", () => {
    expect(
      messages(signInSchema.safeParse({ email: "a@", password: "secret" })),
    ).toEqual({ email: "Enter a valid email address, like name@example.com" });
  });
});
