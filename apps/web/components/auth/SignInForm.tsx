"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";

import { AuthCard, FieldError } from "@/components/auth/AuthCard";
import { classifyAuthError, MESSAGES } from "@/components/auth/messages";
import { PasswordInput } from "@/components/auth/PasswordInput";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { DEFAULT_AFTER_SIGN_IN } from "@/lib/auth/redirect";
import { getSupabase } from "@/lib/auth/supabase";
import { signInSchema, type SignInValues } from "@/lib/validation/auth";

/**
 * /sign-in (§7.5.2, FR-002). A failed sign-in never says which field was wrong. On success the
 * user goes to `next` (already reduced to a same-site path by the page) or /dashboard.
 */
export function SignInForm({
  next,
  confirmationFailed = false,
}: {
  next: string;
  confirmationFailed?: boolean;
}) {
  const router = useRouter();
  const [formError, setFormError] = useState<string | null>(
    confirmationFailed ? MESSAGES.confirmationFailed : null,
  );
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<SignInValues>({
    resolver: zodResolver(signInSchema),
    defaultValues: { email: "", password: "" },
  });

  // §7.2: a user who is already signed in and opens /sign-in goes to the dashboard. Checked once
  // on arrival, so it does not race the redirect to `next` after a successful sign-in.
  useEffect(() => {
    let active = true;
    getSupabase()
      .auth.getSession()
      .then(({ data }) => {
        if (active && data.session) router.replace(DEFAULT_AFTER_SIGN_IN);
      });
    return () => {
      active = false;
    };
  }, [router]);

  async function onSubmit(values: SignInValues) {
    setFormError(null);
    const { error } = await getSupabase().auth.signInWithPassword({
      email: values.email,
      password: values.password,
    });
    if (error) {
      const failure = classifyAuthError(error);
      setFormError(
        failure === "rate_limited"
          ? MESSAGES.rateLimited
          : failure === "offline"
            ? MESSAGES.offline
            : MESSAGES.signInFailed,
      );
      return;
    }
    router.replace(next);
  }

  return (
    <AuthCard
      title="Sign in"
      description="Welcome back. Sign in to see your trips."
      footer={
        <p>
          New here?{" "}
          <Link
            href="/sign-up"
            className="inline-flex min-h-touch items-center font-medium text-primary underline-offset-4 hover:underline"
          >
            Create an account
          </Link>
        </p>
      }
    >
      <form
        noValidate
        onSubmit={handleSubmit(onSubmit)}
        aria-label="Sign in"
        className="flex flex-col gap-5"
      >
        {formError && (
          <p
            role="alert"
            className="rounded-lg border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm font-medium text-destructive"
          >
            {formError}
          </p>
        )}
        <fieldset disabled={isSubmitting} className="flex flex-col gap-5">
          <div className="flex flex-col gap-2">
            <Label htmlFor="sign-in-email">Email</Label>
            <Input
              id="sign-in-email"
              type="email"
              autoComplete="email"
              inputMode="email"
              aria-invalid={errors.email ? true : undefined}
              aria-describedby={
                errors.email ? "sign-in-email-error" : undefined
              }
              {...register("email")}
            />
            <FieldError
              id="sign-in-email-error"
              message={errors.email?.message}
            />
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="sign-in-password">Password</Label>
            <PasswordInput
              id="sign-in-password"
              autoComplete="current-password"
              aria-invalid={errors.password ? true : undefined}
              aria-describedby={
                errors.password ? "sign-in-password-error" : undefined
              }
              {...register("password")}
            />
            <FieldError
              id="sign-in-password-error"
              message={errors.password?.message}
            />
          </div>
        </fieldset>
        <Button type="submit" size="lg" disabled={isSubmitting}>
          {isSubmitting && (
            <Loader2
              aria-hidden="true"
              className="size-5 motion-safe:animate-spin"
            />
          )}
          {isSubmitting ? "Signing in…" : "Sign in"}
        </Button>
      </form>
    </AuthCard>
  );
}
