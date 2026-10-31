import { z } from "zod";

/**
 * Sign-up and sign-in forms (§7.3). Supabase Auth stays the authority; these rules give field-level
 * messages before anything is sent (FR-001 AC3). The sign-in password rule is only "required", so
 * the form never hints at what a valid password looks like.
 */
export const PASSWORD_MIN_LENGTH = 8;

const email = z
  .string()
  .trim()
  .min(1, { error: "Enter your email address" })
  .pipe(
    z.email({ error: "Enter a valid email address, like name@example.com" }),
  );

export const signUpSchema = z.object({
  email,
  password: z
    .string()
    .min(1, { error: "Enter a password" })
    .min(PASSWORD_MIN_LENGTH, {
      error: `Use at least ${PASSWORD_MIN_LENGTH} characters`,
    }),
});

export const signInSchema = z.object({
  email,
  password: z.string().min(1, { error: "Enter your password" }),
});

export type SignUpValues = z.infer<typeof signUpSchema>;
export type SignInValues = z.infer<typeof signInSchema>;
