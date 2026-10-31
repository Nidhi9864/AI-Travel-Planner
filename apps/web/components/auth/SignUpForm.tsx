"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { AuthCard, FieldError } from "@/components/auth/AuthCard";
import { classifyAuthError, MESSAGES } from "@/components/auth/messages";
import { PasswordInput } from "@/components/auth/PasswordInput";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { getSupabase } from "@/lib/auth/supabase";
import {
  PASSWORD_MIN_LENGTH,
  signUpSchema,
  type SignUpValues,
} from "@/lib/validation/auth";

/**
 * /sign-up (§7.5.2, FR-001). The browser calls Supabase Auth directly; the backend never sees a
 * password. When the project needs email confirmation, or the address already has an account,
 * the same neutral notice is shown, so the form does not reveal which addresses are registered.
 */
export function SignUpForm({ next }: { next: string }) {
  const router = useRouter();
  const [formError, setFormError] = useState<string | null>(null);
  const [notice, setNotice] = useState(false);
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<SignUpValues>({
    resolver: zodResolver(signUpSchema),
    defaultValues: { email: "", password: "" },
  });

  async function onSubmit(values: SignUpValues) {
    setFormError(null);
    const redirect = new URL("/auth/callback", window.location.origin);
    redirect.searchParams.set("next", next);

    const { data, error } = await getSupabase().auth.signUp({
      email: values.email,
      password: values.password,
      options: { emailRedirectTo: redirect.toString() },
    });

    if (error) {
      switch (classifyAuthError(error)) {
        case "existing_account":
          setNotice(true);
          return;
        case "weak_password":
          setError("password", { message: MESSAGES.weakPassword });
          return;
        case "rate_limited":
          setFormError(MESSAGES.rateLimited);
          return;
        case "offline":
          setFormError(MESSAGES.offline);
          return;
        default:
          setFormError(MESSAGES.unexpected);
          return;
      }
    }

    if (data.session) {
      // Email confirmation is off for this project: the new account is already signed in.
      router.replace(next);
      return;
    }
    setNotice(true);
  }

  const footer = (
    <p>
      Already have an account?{" "}
      <Link
        href="/sign-in"
        className="inline-flex min-h-touch items-center font-medium text-primary underline-offset-4 hover:underline"
      >
        Sign in
      </Link>
    </p>
  );

  if (notice) {
    return (
      <AuthCard
        title="Check your email"
        description="Your sign-up request has been received."
        footer={footer}
      >
        <p role="status" className="text-foreground">
          {MESSAGES.signUpNotice}
        </p>
      </AuthCard>
    );
  }

  return (
    <AuthCard
      title="Create an account"
      description="Plan trips and keep your itineraries in one place."
      footer={footer}
    >
      <form
        noValidate
        onSubmit={handleSubmit(onSubmit)}
        aria-label="Create an account"
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
            <Label htmlFor="sign-up-email">Email</Label>
            <Input
              id="sign-up-email"
              type="email"
              autoComplete="email"
              inputMode="email"
              aria-invalid={errors.email ? true : undefined}
              aria-describedby={
                errors.email ? "sign-up-email-error" : undefined
              }
              {...register("email")}
            />
            <FieldError
              id="sign-up-email-error"
              message={errors.email?.message}
            />
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="sign-up-password">Password</Label>
            <PasswordInput
              id="sign-up-password"
              autoComplete="new-password"
              aria-invalid={errors.password ? true : undefined}
              aria-describedby={
                errors.password
                  ? "sign-up-password-error sign-up-password-hint"
                  : "sign-up-password-hint"
              }
              {...register("password")}
            />
            <p
              id="sign-up-password-hint"
              className="text-sm text-muted-foreground"
            >
              At least {PASSWORD_MIN_LENGTH} characters.
            </p>
            <FieldError
              id="sign-up-password-error"
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
          {isSubmitting ? "Creating account…" : "Create account"}
        </Button>
      </form>
    </AuthCard>
  );
}
